# Seguridad de credenciales y accesos

## Apartado 1
Las credenciales de OpenAI y Anthropic se almacenan en variables de entorno que el proceso lee al iniciarse. En desarrollo local puede utilizarse un archivo .env, que debe estar excluido de Git mediante .gitignore. El repositorio solo contiene .env.example con valores de ejemplo sin secretos. Nunca se deben escribir las claves directamente en main.py, rag.py ni en un README.

## Apartado 2
Si una clave aparece accidentalmente en un repositorio público, se debe revocar y emitir una nueva desde la consola del proveedor. Borrar únicamente el archivo de la versión actual no elimina el secreto del historial de Git. También se deben revisar logs, capturas y archivos de prueba antes de compartir evidencias.

## Apartado 3
Los permisos para acceder a bases de datos y APIs deben limitarse al mínimo requerido. Cada servicio utiliza su propio conjunto de credenciales y no comparte cuentas privilegiadas con otros componentes. Las credenciales se rotan de acuerdo con el procedimiento operativo aprobado.

## Apartado 4
En los logs técnicos no se deben imprimir tokens de autenticación ni encabezados sensibles. Se pueden conservar IDs de correlación, duraciones y códigos de estado para el diagnóstico. Los mensajes de error destinados al usuario no deben exponer credenciales, cadenas de conexión ni trazas internas.

## Apartado 5
Las comunicaciones externas deben realizarse mediante TLS, y las claves privadas deben quedar fuera del control de versiones. Los repositorios se revisan antes de cada push. Si se cambia el proveedor de generación, las claves y los modelos se seleccionan desde configuración en vez de editar las funciones de negocio.


## Manejo práctico de secretos durante el desarrollo

Cada persona que trabaja en el repositorio crea su propia copia de .env.example y la guarda como .env. Ese segundo archivo es privado y contiene las claves reales, mientras que el primero contiene nombres de variables y valores ilustrativos. En la documentación pública deben aparecer únicamente nombres como OPENAI_API_KEY y ANTHROPIC_API_KEY, nunca valores completos. El comando git status ayuda a verificar la lista de archivos preparados antes de publicar un commit.

Si un desarrollador sospecha que una credencial quedó expuesta, debe verificar la consola del proveedor, revocar la clave afectada y crear otra. También conviene examinar si el secreto apareció en un historial de Git, una captura de pantalla o un archivo de prueba. La revocación tiene prioridad sobre la limpieza visual del repositorio, porque una clave publicada puede haberse copiado antes de ser borrada. El equipo documenta el incidente sin registrar de nuevo el valor secreto.

El principio de menor privilegio implica conceder solo los permisos necesarios a cada componente. Las API keys utilizadas para desarrollo no deberían reutilizarse indiscriminadamente en producción. La observabilidad necesita métricas y estados, no secretos de autenticación. Si un programa falla al leer variables de entorno, debe informar qué nombre de variable falta y terminar con un error controlado; nunca debe imprimir la clave cargada para demostrar que la leyó.
