# Pre-entrega 3 — RAG local con ChromaDB, LangChain y Pydantic

Sistema **Python 3.12** para consultar cuatro documentos técnicos de ejemplo. Indexa sus fragmentos como vectores en una **colección persistente local** y responde utilizando **exclusivamente el contexto recuperado**. Si el contexto no alcanza, debe devolver **«No lo sé»**.

## Componentes y arquitectura

```text
data/*.md → ingest.py → RecursiveCharacterTextSplitter (600 tokens, 50 overlap)
                        ↓ embeddings: text-embedding-3-small (OpenAI)
                 ./vectorstore/ (ChromaDB persistente)
                        ↑ pregunta convertida con el MISMO modelo de embeddings
query → recuperador asíncrono (top_k=4) → contexto [FUENTE: archivo]
      → ChatPromptTemplate | ChatOpenAI/ChatAnthropic | PydanticOutputParser
      → RAGResponse(respuesta, referencias)
      → chequeo de referencias contra documentos recuperados
```

**Aclaración del chunking:** `chunk_size=600` representa el **máximo de tokens por fragmento**, no un mínimo rígido. Los fragmentos finales pueden ser menores de 500 tokens, algo normal en un corpus pequeño. El overlap configurado es de **50 tokens**. Se cuenta con `tiktoken`, no con caracteres.

**Modelos de generación vs. embeddings:** el proveedor de **generación** puede ser OpenAI o Anthropic. Los **embeddings** usan siempre OpenAI (`text-embedding-3-small`) para indexar y consultar, evitando el error de modelos incompatibles. Si cambiás `EMBEDDING_MODEL`, debés volver a indexar.

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
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python --version
Copy-Item .env.example .env
```

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

Probar Anthropic (sigue usando OpenAI para embeddings):

```powershell
python main.py --provider anthropic
```

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
