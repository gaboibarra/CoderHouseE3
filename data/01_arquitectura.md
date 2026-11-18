# Arquitectura de la plataforma de pagos

## Apartado 1
La plataforma demostrativa procesa solicitudes de pago con una API FastAPI. La API recibe un identificador de solicitud, valida campos obligatorios y delega el procesamiento a un servicio de operaciones. PostgreSQL almacena los registros transaccionales y Redis sirve como caché de consultas frecuentes. Este documento describe un sistema ficticio para practicar recuperación documental y no representa una plataforma real.

## Apartado 2
La separación de responsabilidades evita que las reglas de negocio queden mezcladas con la capa de persistencia. El adaptador de PostgreSQL implementa operaciones de lectura y escritura; el adaptador Redis mantiene datos temporales con vencimiento. Los identificadores de operaciones permiten correlacionar logs entre componentes. Las solicitudes deben registrar un ID de correlación desde la entrada hasta su finalización.

## Apartado 3
Los servicios intercambian respuestas mediante HTTP. Si un componente externo no responde, se aplica un timeout configurado, se registra un error y no se asume que la operación fue exitosa. El acceso a la base relacional utiliza un pool de conexiones con límites establecidos para evitar agotamiento de recursos. Un servicio no debe mantener conexiones abiertas más tiempo del necesario.

## Apartado 4
Para una operación crítica, el sistema debe asegurar que el mismo identificador de transacción no produzca cargos duplicados. Se utiliza una clave de idempotencia y se revisa el estado anterior de la operación antes de repetirla. Las claves de idempotencia deben asociarse con la operación de negocio y conservarse durante el plazo operativo definido.

## Apartado 5
La plataforma registra métricas de latencia de API y porcentaje de errores HTTP 5xx. Los tableros comparan tendencias y permiten detectar aumentos de tiempo de respuesta. Cuando se observan fallas continuadas se activa una investigación y se revisan trazas y logs del intervalo afectado.


## Reglas adicionales de disponibilidad y recuperación

El sistema considera una solicitud aceptada solo cuando se han validado sus datos de entrada y se ha generado un identificador que permita seguimiento. Si se utiliza Redis como caché, la caída de Redis no debe provocar pérdida de registros persistentes de PostgreSQL. Los datos de carácter transaccional deben permanecer en el repositorio duradero. Los valores de caché pueden regenerarse a partir de información válida. Este principio permite separar claramente una pérdida temporal de rendimiento de una pérdida real de datos.

La API aplica un mecanismo de control de errores que diferencia fallos de validación, indisponibilidad del servicio dependiente y errores internos. Las respuestas HTTP 400 se utilizan para solicitudes de entrada no válidas; los errores HTTP 500 señalan una falla del lado del servidor, sin revelar información sensible. Los registros internos conservan el ID de correlación y la marca de tiempo. Los clientes no reciben detalles de conexión a PostgreSQL ni contenido de excepciones internas.

Las pruebas funcionales incluyen una operación válida, una solicitud con un campo faltante, una llamada duplicada con la misma clave de idempotencia y un escenario en que Redis no responde. Durante la revisión de incidentes, el equipo compara el estado externo reportado con los registros almacenados. No se debe concluir que un pago fue rechazado o aprobado a partir de un mensaje de timeout aislado; es necesario verificar el estado transaccional persistido antes de reintentar.
