\# F9 — reproducibilidad en el computador de Juan Guillermo



\- Fecha: 7 de octubre de 2026

\- Equipo: Windows, 16 GB de RAM

\- Git / Docker / Compose:

&#x20; - Git 2.53.0.windows.2

&#x20; - Docker 29.8.0, build 88096ef

&#x20; - Docker Compose v5.5.1

\- Commit probado: f67dce0 — Merge pull request #8 from sBoterino/docs/guia-fase9

\- Duración total: No medida desde el inicio de la prueba.



\## Resultados



\- Compose: Correcto. Las imágenes de Dask, API, Spark y MongoDB fueron construidas correctamente y los servicios iniciaron.

\- `/health`: Correcto. La API respondió con `mongo=ok`, `status=ok` y versión `latest`.

\- Dask: Correcto. Se detectaron 2 workers conectados, el cálculo distribuido fue correcto y MongoDB reportó 300 eventos semilla.

\- Spark Connector: Correcto. Spark pudo conectarse al clúster y leer los 300 documentos semilla desde MongoDB.

\- Ingesta y conteos: Correcto. Se procesaron 1.972.121 filas iniciales y se obtuvieron 1.741.828 documentos finales.

\- Controles de limpieza:

&#x20; - R1 — coordenadas nulas/no numéricas: 226.028

&#x20; - R2 — coordenadas `(0,0)`: 4.115

&#x20; - R3 — fuera de rango mundial: 106

&#x20; - R4 — fuera de NYC: 44

&#x20; - R5 — fecha/hora inválida: 0

&#x20; - R6 — ID duplicado: 0

\- Segunda ingesta: Correcta. El sistema indicó `Ingesta omitida` porque los 1.741.828 documentos ya correspondían al dataset con `max\_rows=0`.

\- Verificación Spark: Correcta. Las sumas de registros de `spark\_grilla`, `spark\_por\_hora`, `spark\_por\_dia\_semana` y `spark\_por\_mes` coincidieron con 1.741.828. La verificación final terminó con `RESULTADO: OK`.

\- Consultas API: Correctas. `/near` devolvió 10 resultados y `/spark-results/hotspots` devolvió 5 resultados.



\## Problemas encontrados y correcciones



1\. Problema — Docker estaba instalado y los comandos `docker` y `docker compose` eran reconocidos, pero `docker run --rm hello-world` inicialmente no podía conectarse al motor `dockerDesktopLinuxEngine`.

&#x20;  - Causa — El motor de Docker Desktop no estaba ejecutándose.

&#x20;  - Solución — Se abrió Docker Desktop, se esperó a que el motor estuviera disponible y posteriormente se continuó con las pruebas.



No se presentaron otros errores que impidieran completar la reproducción del sistema.



\## Conclusión



La reproducción del proyecto fue exitosa utilizando el repositorio clonado directamente desde GitHub y la configuración local correspondiente. El sistema pudo construir y levantar los servicios mediante Docker Compose, establecer comunicación entre Dask, Spark y MongoDB, ejecutar la ingesta completa, comprobar la idempotencia y verificar los resultados mediante Spark y la API.



La prueba permitió confirmar que el proyecto puede ser levantado y ejecutado en un equipo diferente utilizando la documentación disponible, sin copiar las carpetas, imágenes, volúmenes ni datos de otro integrante.

