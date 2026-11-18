# Pre-entrega 3 — RAG local con ChromaDB, LangChain y Pydantic

Sistema **Python 3.12** para consultar cuatro documentos técnicos de ejemplo. Indexa sus fragmentos como vectores en una **colección persistente local** y responde utilizando **exclusivamente el contexto recuperado**. Si el contexto no alcanza, debe devolver **«No lo sé»**.

## Componentes y arquitectura

El flujo del sistema RAG se compone de las siguientes etapas:

1. **Ingesta de documentos**
   - Se leen los archivos `data/*.md`.
   - Se fragmentan con `RecursiveCharacterTextSplitter`.
   - Configuración de fragmentación: **600 tokens** con **50 tokens de overlap**.

2. **Generación de embeddings**
   - Cada fragmento se transforma en embedding usando **`text-embedding-3-small` (OpenAI)**.

3. **Persistencia vectorial**
   - Los embeddings y metadatos se almacenan en **ChromaDB** dentro de `./vectorstore`.

4. **Recuperación semántica**
   - La consulta del usuario se convierte en embedding usando el **mismo modelo**.
   - Se realiza una búsqueda de similitud en ChromaDB.
   - Se recuperan los **4 fragmentos más relevantes** (`top_k=4`).

5. **Construcción del contexto**
   - Los fragmentos recuperados se formatean junto con su fuente (`FUENTE: archivo`).

6. **Generación de respuesta**
   - El contexto y la pregunta se envían a una cadena LCEL compuesta por:
     - `ChatPromptTemplate`
     - `ChatOpenAI` o `ChatAnthropic`
     - `PydanticOutputParser`

7. **Validación final**
   - La salida se valida contra el modelo `RAGResponse`.
   - Se verifica que las referencias citadas pertenezcan a los documentos recuperados.

## Estructura del repositorio

```text
pre-entrega-3-rag/
├── data/                 # 4 documentos .md de ejemplo
├── tests/                # tests sin llamadas a las APIs
├── config.py             # rutas, proveedor de embeddings y Chroma
├── schemas.py            # RAGResponse de Pydantic
├── ingest.py             # carga, chunking, firma de contenido, persistencia
├── rag.py                # retriever asíncrono + cadena LCEL + validaciones
├── main.py               # dos preguntas demo o consulta personalizada
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

El directorio **`vectorstore/`** y el manifiesto `.vectorstore_manifest.json` se generan al ejecutar la ingesta y **no** se suben a GitHub. Se reconstruyen desde `data/`.

## Instalación — Windows PowerShell

```powershell
py -3.12 -m venv .venv
```
<img width="886" height="31" alt="image" src="https://github.com/user-attachments/assets/674719e4-2d90-486e-9750-1b43acaed7f5" />


```powershell
.\.venv\Scripts\Activate.ps1
```
<img width="886" height="31" alt="image" src="https://github.com/user-attachments/assets/571b7a2f-594c-4b19-a80b-0c3f7fc0ddeb" />


```powershell
python -m pip install -r requirements.txt
```
<img width="886" height="70" alt="image" src="https://github.com/user-attachments/assets/4616d836-5d47-4f90-8c71-919f4d2ffcf0" />


```powershell
python --version
```
<img width="886" height="37" alt="image" src="https://github.com/user-attachments/assets/1ff0465f-46b1-4447-978a-cbeae13882ef" />


```powershell
Copy-Item .env.example .env
```
<img width="886" height="29" alt="image" src="https://github.com/user-attachments/assets/19baec95-c670-47fb-8182-624a90bd79a2" />


Completá `.env` con tus propias claves privadas:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=TU_CLAVE_DE_OPENAI
ANTHROPIC_API_KEY=TU_CLAVE_DE_ANTHROPIC
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-haiku-4-5
EMBEDDING_MODEL=text-embedding-3-small
TOP_K=4
```

**Nunca subas `.env` a GitHub.** Aunque generes con Anthropic, necesitás `OPENAI_API_KEY` porque la base vectorial usa embeddings de OpenAI. Las solicitudes a APIs pueden tener costo.

## 1. Ingesta y persistencia

```powershell
python ingest.py
```
<img width="886" height="45" alt="image" src="https://github.com/user-attachments/assets/d2dc4d78-fdb8-4747-afd4-14708b526ec9" />


El script lee `data/*.md` y `data/*.txt`, obtiene los fragmentos, genera embeddings y guarda la colección en `./vectorstore/`. Genera una firma SHA-256 sobre los contenidos, el modelo y el chunking. Si corrés `python ingest.py` de nuevo sin cambios, **reutiliza la colección** en lugar de recalcular embeddings.

Para reconstruirla explícitamente:

```powershell
python ingest.py --force
```

Si cambiás cualquier documento o el modelo de embeddings, `ingest.py` reconstruye el índice completo. **No hace falta llamar manualmente a `.persist()`** con la integración Chroma actual cuando se configura `persist_directory`.

## 2. Consultas RAG asíncronas

Ejecutar dos preguntas con OpenAI:

```powershell
python main.py --provider openai
```
<img width="886" height="291" alt="image" src="https://github.com/user-attachments/assets/12be1436-1f57-48a6-8413-940dcb96df45" />



Probar Anthropic (sigue usando OpenAI para embeddings):

```powershell
python main.py --provider anthropic
```
<img width="886" height="296" alt="image" src="https://github.com/user-attachments/assets/200a010b-cd7c-4208-8290-8ff85dae7e55" />


Consultar libremente:

```powershell
python main.py --provider openai --question "¿Dónde se guardan las API keys?"
```

La función reutilizable es:

```python
import asyncio
from rag import get_rag_response

async def main():
    resultado = await get_rag_response("¿Qué métricas se monitorean?", provider="openai")
    print(resultado.model_dump_json(indent=2))

asyncio.run(main())
```

El retriever utiliza `store.asimilarity_search(...)` para no bloquear el event loop durante la búsqueda. La generación utiliza `chain.ainvoke(...)`.

## 3. Ejemplos de resultados esperados

**Pregunta respondible:** «¿Qué mecanismos se usan para proteger las credenciales de las APIs?»

```json
{
  "respuesta": "Las credenciales se guardan en variables de entorno. En desarrollo se permite .env, excluido por .gitignore; el repositorio comparte solo .env.example sin secretos.",
  "referencias": ["02_seguridad.md"]
}
```

**Pregunta trampa:** «¿Cuál es el sueldo del director general de esta empresa?»

```json
{
  "respuesta": "No lo sé",
  "referencias": []
}
```

**Son resultados ilustrativos, no una ejecución verificada.** La redacción puede variar entre consultas. Para la trampa, el resultado deseado es exactamente «No lo sé» porque la información no está en el corpus.

### Limitaciones importantes

- RAG reduce alucinaciones, **no las elimina**. La búsqueda por similitud siempre puede recuperar fragmentos relacionados de forma débil; el prompt debe imponer la abstención.
- Pydantic valida tipos y estructura; **no demuestra por sí solo que cada afirmación esté respaldada** por el documento. Se comprueba que los nombres de referencias pertenezcan a los archivos recuperados, pero no hay verificación automática oración por oración.
- Una referencia indica el **archivo fuente**; el contexto también incluye un índice de fragmento para depurar.
- Los documentos de ejemplo son ficticios y solo sirven para practicar el pipeline.

## 4. Pruebas automáticas

```powershell
python -m pytest -v
```

Las pruebas incluidas se enfocan en Pydantic, referencias y armado del contexto **sin llamar a las APIs**. También hay dos pruebas manuales con la API real desde `main.py`, cuya salida deberás verificar en tu equipo. No declares las pruebas reales como aprobadas hasta ejecutarlas.

## Cómo se relaciona con las entregas anteriores

- **E1:** clientes asíncronos y selección de proveedor.
- **E2:** pipeline LCEL y validación Pydantic.
- **E3:** ingesta local persistente + recuperación semántica + generación fundada + referencias.

La arquitectura se reutiliza, pero este repositorio es independiente y utiliza adaptadores LangChain.

## Referencias técnicas

- [LangChain — Chroma](https://reference.langchain.com/python/langchain-chroma/vectorstores/Chroma)
- [LangChain — PydanticOutputParser](https://reference.langchain.com/python/langchain-core/output_parsers/pydantic/PydanticOutputParser)
- [LangChain — TextSplitter](https://reference.langchain.com/python/langchain-text-splitters/base/TextSplitter)
- [Documentación de ChromaDB](https://docs.trychroma.com/)
