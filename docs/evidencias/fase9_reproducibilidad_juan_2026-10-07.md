\# F9 â€” reproducibilidad en el computador de Juan Guillermo



\- Fecha: 7 de octubre de 2026

\- Equipo: Windows, 16 GB de RAM

\- Git / Docker / Compose:

&#x20; - Git 2.53.0.windows.2

&#x20; - Docker 29.8.0, build 88096ef

&#x20; - Docker Compose v5.5.1

\- Commit probado: f67dce0 â€” Merge pull request #8 from sBoterino/docs/guia-fase9

\- DuraciÃ³n total: No medida desde el inicio de la prueba.



\## Resultados



\- Compose: Correcto. Las imÃ¡genes de Dask, API, Spark y MongoDB fueron construidas correctamente y los servicios iniciaron.

\- `/health`: Correcto. La API respondiÃ³ con `mongo=ok`, `status=ok` y versiÃ³n `latest`.

\- Dask: Correcto. Se detectaron 2 workers conectados, el cÃ¡lculo distribuido fue correcto y MongoDB reportÃ³ 300 eventos semilla.

\- Spark Connector: Correcto. Spark pudo conectarse al clÃºster y leer los 300 documentos semilla desde MongoDB.

\- Ingesta y conteos: Correcto. Se procesaron 1.972.121 filas iniciales y se obtuvieron 1.741.828 documentos finales.

\- Controles de limpieza:

&#x20; - R1 â€” coordenadas nulas/no numÃ©ricas: 226.028

&#x20; - R2 â€” coordenadas `(0,0)`: 4.115

&#x20; - R3 â€” fuera de rango mundial: 106

&#x20; - R4 â€” fuera de NYC: 44

&#x20; - R5 â€” fecha/hora invÃ¡lida: 0

&#x20; - R6 â€” ID duplicado: 0

\- Segunda ingesta: Correcta. El sistema indicÃ³ `Ingesta omitida` porque los 1.741.828 documentos ya correspondÃ­an al dataset con `max\_rows=0`.

\- VerificaciÃ³n Spark: Correcta. Las sumas de registros de `spark\_grilla`, `spark\_por\_hora`, `spark\_por\_dia\_semana` y `spark\_por\_mes` coincidieron con 1.741.828. La verificaciÃ³n final terminÃ³ con `RESULTADO: OK`.

\- Consultas API: Correctas. `/near` devolviÃ³ 10 resultados y `/spark-results/hotspots` devolviÃ³ 5 resultados.



\## Problemas encontrados y correcciones



1\. Problema â€” Docker estaba instalado y los comandos `docker` y `docker compose` eran reconocidos, pero `docker run --rm hello-world` inicialmente no podÃ­a conectarse al motor `dockerDesktopLinuxEngine`.

&#x20;  - Causa â€” El motor de Docker Desktop no estaba ejecutÃ¡ndose.

&#x20;  - SoluciÃ³n â€” Se abriÃ³ Docker Desktop, se esperÃ³ a que el motor estuviera disponible y posteriormente se continuÃ³ con las pruebas.



No se presentaron otros errores que impidieran completar la reproducciÃ³n del sistema.



\## ConclusiÃ³n



La reproducciÃ³n del proyecto fue exitosa utilizando el repositorio clonado directamente desde GitHub y la configuraciÃ³n local correspondiente. El sistema pudo construir y levantar los servicios mediante Docker Compose, establecer comunicaciÃ³n entre Dask, Spark y MongoDB, ejecutar la ingesta completa, comprobar la idempotencia y verificar los resultados mediante Spark y la API.



La prueba permitiÃ³ confirmar que el proyecto puede ser levantado y ejecutado en un equipo diferente utilizando la documentaciÃ³n disponible, sin copiar las carpetas, imÃ¡genes, volÃºmenes ni datos de otro integrante.

---

## Actualizacion de validacion - 9 de octubre de 2026

Se realizo una nueva validacion sobre el estado actual del proyecto, commit 77521c7.

### Resultados

- Docker Compose: servicios principales activos correctamente.
- API: healthy.
- MongoDB: healthy.
- Dask Scheduler: healthy.
- Dask Workers: 2 workers activos.
- Spark Master: healthy.
- Spark Worker: activo.
- Dask-MongoDB: validado correctamente con 300 eventos semilla.
- Spark-MongoDB: validado correctamente con 300 documentos semilla.
- Dataset: 1,741,828 documentos.
- Agregacion espacial: 1,741,828 registros procesados, 3,246 celdas y suma_n=1,741,828.
- Agregacion temporal: hora, dia de semana, mes y hora-borough conservaron suma_n=1,741,828.
- Verificacion Spark: RESULTADO: OK.
- Hotspot principal: Spark n=5336 y MongoDB n=5337, dentro del margen permitido.
- API /health: mongo=ok, status=ok, version 8.
- API /near: 10 resultados.
- API /spark-results/hotspots: 5 resultados.

### Incidencia

Inicialmente se intento ejecutar entanas_temporales.py, pero dicho archivo no existe en el proyecto. Se verificaron los archivos disponibles y se ejecuto correctamente gregacion_temporal.py.

### Conclusion

La validacion realizada el 9 de octubre de 2026 fue satisfactoria. Dask, Spark, MongoDB y la API funcionaron correctamente y la verificacion final termino con RESULTADO: OK.

