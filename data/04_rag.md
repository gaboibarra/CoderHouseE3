# Recuperación semántica y base vectorial

## Apartado 1
La arquitectura RAG comienza por leer archivos .md y .txt, dividirlos en fragmentos y generar embeddings. ChromaDB almacena los vectores y los metadatos de procedencia. La aplicación crea una colección persistente en la carpeta local vectorstore, para reutilizarla en ejecuciones posteriores sin volver a pagar la indexación.

## Apartado 2
El modelo de embeddings debe ser exactamente el mismo al indexar documentos y al transformar la pregunta del usuario. En este ejercicio se usa text-embedding-3-small de OpenAI para ambas operaciones, aunque el modelo de generación puede ser de OpenAI o de Anthropic. Cambiar el modelo de embeddings exige reconstruir la colección.

## Apartado 3
Para fragmentar el texto se utiliza RecursiveCharacterTextSplitter con conteo de tokens y tamaño objetivo máximo de 600 tokens y overlap de 50 tokens. El último segmento de un archivo puede ser más pequeño. El solapamiento intenta conservar información cercana a los límites entre fragmentos y reduce la pérdida de continuidad.

## Apartado 4
El retriever convierte la pregunta en un embedding, calcula similitud respecto de los documentos almacenados y recupera hasta cuatro fragmentos relevantes por defecto. No se envían todos los documentos al modelo generativo: se limita el contexto para controlar costo y ruido. Los metadatos incluyen el nombre del archivo y el índice del fragmento.

## Apartado 5
La respuesta final se genera exclusivamente a partir del contexto recuperado. Cuando el contexto no permite responder, el asistente debe decir No lo sé, sin inventar hechos. Un PydanticOutputParser valida que el objeto incluya respuesta y referencias. La aplicación comprueba que las referencias pertenezcan a los archivos realmente recuperados.


## Buenas prácticas para recuperar información confiable

Una búsqueda vectorial compara representaciones numéricas de la pregunta y los fragmentos. La cercanía en el espacio vectorial indica similitud semántica aproximada, no prueba lógica de que el fragmento responda. Por esta razón se instruye al modelo generativo a abstenerse cuando el contexto recuperado no contiene la información requerida. Preguntas sobre salarios, acuerdos comerciales o personas no mencionadas en estos documentos deben recibir No lo sé.

El componente de generación recibe la pregunta y solo los fragmentos seleccionados por el recuperador. El prompt diferencia claramente instrucciones del sistema y texto documental. El texto documental no debe tratarse como instrucciones operativas, porque un documento podría contener frases maliciosas o irrelevantes. Las respuestas se validan con Pydantic, y las referencias deben corresponder a nombres de archivos realmente recuperados en esa consulta.

El índice persistente permite evitar recalcular vectores cuando los archivos y la configuración siguen iguales. Para ello se genera una firma sobre nombres y contenidos de los archivos, modelo de embeddings y parámetros de fragmentación. Si cambia la firma, se reconstruye la colección completa. La carpeta del índice se excluye de Git, mientras que el dataset original se mantiene versionado para que otra persona pueda reconstruir el sistema con su propia clave de API.
