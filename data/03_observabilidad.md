# Monitoreo y resolución de incidentes

## Apartado 1
Los indicadores principales del servicio son cantidad de solicitudes, latencia p95, porcentaje de HTTP 5xx y tasa de errores. Estos indicadores permiten observar tanto el volumen del tráfico como la estabilidad. Una alerta debe contener el nombre del servicio, el período afectado y el indicador que supera el umbral.

## Apartado 2
Cuando se produce una secuencia de HTTP 500, el equipo inspecciona los logs correlacionados por ID de solicitud. Después revisa si existe agotamiento del pool de PostgreSQL, tiempos de espera en servicios externos o saturación de recursos. Las alertas sin contexto suficiente no deberían convertirse automáticamente en un diagnóstico definitivo.

## Apartado 3
La criticidad alta se asigna a incidentes con impacto comprobado en operaciones de pago, pérdida de disponibilidad relevante o riesgo para integridad de los datos. La criticidad media se usa para degradaciones parciales o intermitentes con impacto acotado. La criticidad baja corresponde a observaciones sin evidencia de una afectación significativa.

## Apartado 4
Los logs deben tener marcas de tiempo consistentes y un identificador de correlación. Las métricas agregadas ayudan a detectar síntomas, mientras que las trazas permiten seguir la secuencia de llamadas entre servicios. Cuando se registra un error se recomienda documentar hipótesis, evidencias, decisión tomada y resultado de la intervención.

## Apartado 5
El plan de mitigación contempla reiniciar componentes solo después de evaluar el estado de las operaciones en curso. Antes de reintentar un cobro se revisan los mecanismos de idempotencia. Una recuperación rápida no elimina la necesidad de analizar la causa raíz y registrar las acciones preventivas.


## Procedimiento para investigar errores intermitentes

Ante una alerta de error rate se delimita primero el período temporal y se identifica qué servicio registró los cambios. Se comprueba si la tasa de errores aumentó por encima del comportamiento habitual y si coincidió con un despliegue o variación del tráfico. Después se consultan trazas y logs asociados con IDs de correlación. La investigación intenta diferenciar síntomas de causas raíz: un HTTP 500 es un síntoma, pero por sí mismo no identifica la causa.

Si la latencia p95 aumenta, el equipo observa el tiempo de respuesta de los servicios dependientes y la utilización del pool de conexiones. Una saturación de PostgreSQL puede reflejarse como mayor espera en la API, pero esa hipótesis necesita métricas de conexiones activas, consultas lentas y tiempos de espera. Si no existen esas mediciones no debe afirmarse que PostgreSQL es responsable. La documentación del incidente registra las hipótesis y los datos que las respaldan.

Al finalizar una intervención se verifica que las métricas vuelvan a valores compatibles con un funcionamiento estable y que no existan transacciones pendientes sin resolver. El cierre del incidente incluye una descripción del impacto real, la duración conocida y las medidas preventivas propuestas. Los niveles de criticidad son una herramienta para priorizar el trabajo; no reemplazan la investigación técnica ni la comprobación del impacto sobre usuarios u operaciones.
