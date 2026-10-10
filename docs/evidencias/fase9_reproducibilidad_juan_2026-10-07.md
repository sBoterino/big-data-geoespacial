# F9 - reproducibilidad en el computador de Juan Guillermo

- Fecha inicial: 7 de octubre de 2026.
- Equipo: Windows, 16 GB de RAM.
- Git: 2.53.0.windows.2.
- Docker: 29.8.0, build 88096ef.
- Docker Compose: v5.5.1.
- Commit inicial probado: `f67dce0`, merge del PR #8.
- Duracion total: no se midio desde el inicio; no se presenta una estimacion como medicion.

## Resultados iniciales

- **Compose:** las imagenes de Dask, API, Spark y MongoDB se construyeron y los servicios iniciaron correctamente.
- **`/health`:** la API respondio con `mongo=ok`, `status=ok` y version `latest`.
- **Dask:** se detectaron dos workers, el calculo distribuido fue correcto y MongoDB reporto 300 eventos semilla.
- **Spark Connector:** Spark se conecto al cluster y leyo los 300 documentos semilla desde MongoDB.
- **Ingesta:** se procesaron 1.972.121 filas y se obtuvieron 1.741.828 documentos finales.
- **Segunda ingesta:** el sistema indico `Ingesta omitida` porque los 1.741.828 documentos ya correspondian al dataset con `max_rows=0`.
- **Verificacion Spark:** las sumas de `spark_grilla`, `spark_por_hora`, `spark_por_dia_semana` y `spark_por_mes` coincidieron con 1.741.828; el proceso termino con `RESULTADO: OK`.
- **API:** `/near` devolvio 10 resultados y `/spark-results/hotspots` devolvio 5.

### Controles de limpieza

| Regla | Descartados |
|---|---:|
| R1 - coordenadas nulas o no numericas | 226.028 |
| R2 - coordenadas `(0,0)` | 4.115 |
| R3 - fuera de rango mundial | 106 |
| R4 - fuera de NYC | 44 |
| R5 - fecha u hora invalida | 0 |
| R6 - ID duplicado | 0 |

## Problema encontrado y correccion

Docker estaba instalado y `docker` y `docker compose` eran reconocidos, pero `docker run --rm hello-world` inicialmente no podia conectarse al motor `dockerDesktopLinuxEngine`. La causa era que Docker Desktop no estaba ejecutandose. Se abrio la aplicacion, se espero a que el motor estuviera disponible y se continuaron las pruebas.

## Actualizacion de validacion del 9 de octubre de 2026

Se realizo una nueva validacion sobre el commit `77521c7`:

- Servicios principales activos; API, MongoDB, Dask Scheduler y Spark Master saludables.
- Dos workers Dask y un worker Spark activos.
- Dask-MongoDB y Spark-MongoDB validados con 300 documentos semilla.
- Dataset completo con 1.741.828 documentos.
- Agregacion espacial sobre 1.741.828 registros, 3.246 celdas y `suma_n=1.741.828`.
- Agregaciones por hora, dia de semana, mes y hora por borough con `suma_n=1.741.828`.
- Verificacion Spark terminada con `RESULTADO: OK`.
- Hotspot principal: Spark `n=5.336` y MongoDB `n=5.337`, dentro del margen permitido.
- `/health`: `mongo=ok`, `status=ok`, version 8.
- `/near`: 10 resultados.
- `/spark-results/hotspots`: 5 resultados.

Durante esta validacion se intento ejecutar `ventanas_temporales.py`, pero ese archivo no pertenece al proyecto. Se revisaron los jobs disponibles y se ejecuto correctamente `agregacion_temporal.py`.

## Conclusion

La reproduccion fue exitosa desde un clon de GitHub y con secretos propios. El sistema construyo y levanto los servicios mediante Docker Compose, conecto Dask y Spark con MongoDB, ejecuto la ingesta completa, comprobo la idempotencia y verifico los resultados mediante Spark y la API. No fue necesario copiar carpetas, imagenes, volumenes ni datos de otro integrante.
