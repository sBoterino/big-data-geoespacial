# Evidencia — Fase 4, validación previa a datos reales

Fecha: 4-oct-2026
Rama: `feature/ingesta-dask`

## Implementado

- Descarga Kaggle con marcador e inventario de caché.
- Limpieza ordenada R1–R6 y reporte exclusivo por regla.
- Transformación a GeoJSON `[longitud, latitud]`.
- Lectura Dask particionada y espera de dos workers.
- Deduplicación global, carga MongoDB por lotes e índices.
- Exportación Parquet para el benchmark.
- Metadatos de idempotencia y `FORCE_RELOAD`.
- Pruebas de limpieza integradas en Jenkins.
- Aislamiento de jobs de validación: solo `bdgeo-main` puede ejecutar staging y despliegue;
  los demás jobs usan etiquetas `validation-*`, procesan una muestra de 50.000 filas y no
  modifican producción. `bdgeo-main` mantiene `INGEST_MAX_ROWS=0` para la carga completa.

## Validaciones

- `docker compose config --quiet`: correcto, sin salida.
- Construcción `bdgeo-ingest-test:dev`: 14/14 pasos completados.
- Primera ejecución: detectó que pytest no importaba el módulo desde el ejecutable directo.
- Corrección: ejecutar `python -m pytest` dentro de la imagen.
- Segunda ejecución: `3 passed in 0.29s`.

## Primera muestra real — build `bdgeo-ingesta-test` #1

- La credencial protegida funcionó y Kaggle confirmó el CSV de 420.704.526 bytes.
- API: 4 pruebas aprobadas y 1 prueba intencional omitida.
- Ingesta: 3 pruebas aprobadas en 0,77 s.
- Dask confirmó dos workers y descargó el CSV en el volumen persistente.
- El grafo falló antes de modificar la colección: el scheduler no podía importar `limpieza.py`.
- Jenkins omitió integración, staging y despliegue; producción quedó intacta.
- Corrección aplicada: `Client.upload_file` distribuye `limpieza.py` al scheduler y los workers
  antes de enviar el grafo.

## Segunda muestra real — build `bdgeo-ingesta-test` #2

- El webhook inició automáticamente el build al publicarse la corrección.
- La caché evitó descargar nuevamente los 420.704.526 bytes.
- La distribución de `limpieza.py` funcionó y el grafo avanzó hasta el conteo final.
- Falló la reducción `map_partitions(len).sum()` con una sola partición: Dask recibió un entero
  donde esperaba una serie. Ocurrió antes de vaciar o insertar en la colección.
- Corrección aplicada: materializar únicamente las longitudes de las particiones y sumarlas en el
  cliente. Se añadieron pruebas para una y varias particiones.

## Tercera muestra real — build `bdgeo-ingesta-test` #3

- Resultado: `SUCCESS`, iniciado automáticamente por el webhook.
- API: 4 pruebas aprobadas y 1 intencionalmente omitida.
- Ingesta: 5 pruebas aprobadas, incluidas una y varias particiones.
- Kaggle: CSV de 420.704.526 bytes reconocido desde la caché.
- Dask: 2 workers conectados; muestra procesada en 1 partición.
- Entrada: 50.000 filas.
- R1, coordenadas nulas/no numéricas: 3.888 descartadas.
- R2, coordenadas `(0,0)`: 269 descartadas.
- R3–R6: 0 descartadas en esta muestra.
- Salida e inserción MongoDB: 45.843 documentos.
- Duración de la ingesta: 5,684 segundos.
- Integración Dask: 2 workers, cálculo distribuido y MongoDB, resultado `OK`.
- Integración Spark: 300 documentos y grupos de control 120/80/100, resultado correcto.
- Staging y despliegue: omitidos por la condición del job de rama.
- Mensaje final: producción no fue modificada.

## Pendiente

- Ejecutar la carga completa y conservar `reporte_limpieza.json`.

## Incidencia de red antes de la prueba idempotente

- Los builds #4 y #6 no alcanzaron las pruebas ni la ingesta por fallos DNS de Docker Desktop.
- #4 no resolvió `registry-1.docker.io`; #6 no resolvió `repo1.maven.org`.
- No son fallos del pipeline de datos y no modificaron MongoDB ni producción.
- Hallazgo estructural: los `ADD` remotos del Dockerfile de Spark consultaban Maven en cada build.
- Mitigación: descarga de JAR en una capa `RUN` cacheable y hasta tres intentos con espera para los
  comandos de construcción. La primera construcción de esa capa todavía requiere internet.

## Idempotencia — build `bdgeo-ingesta-test` #7

- Resultado: `SUCCESS`, iniciado automáticamente por el webhook.
- La nueva capa cacheable de Spark se construyó y la mitigación de red quedó validada.
- API: 4 pruebas aprobadas y 1 intencionalmente omitida; ingesta: 5 aprobadas.
- Mensaje: `Ingesta omitida: 45,843 documentos ya corresponden a ...|max_rows=50000`.
- No se descargó, limpió, vació ni reinsertó la colección.
- Integraciones Dask y Spark aprobadas.
- Staging y despliegue omitidos por condición; producción no fue modificada.
- La segunda ejecución demuestra la decisión D3 de ingesta idempotente.

## Auditoría directa de MongoDB

Consulta ejecutada con `mongosh` contra `geo.eventos` después del build #7:

- Conteo: 45.843 documentos, igual al reporte y a `ingesta_meta`.
- Documento observado: `_id='4456314'`.
- GeoJSON: `type='Point'`, coordenadas `[-73.8665, 40.667202]` en orden longitud/latitud.
- Fecha: `ISODate('2021-09-11T09:35:00.000Z')`.
- Índices presentes: `_id_`, `fecha_1` y `location_2dsphere`.

Esto confirma que la muestra no solo fue contada: quedó almacenada con el modelo e índices que
usarán las consultas geoespaciales y temporales.
