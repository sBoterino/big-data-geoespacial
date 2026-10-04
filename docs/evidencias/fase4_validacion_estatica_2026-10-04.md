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
  cliente. Se añadieron pruebas para una y varias particiones. Pendiente de validar en el build #3.

## Pendiente

- Ejecutar una muestra real de 50.000 filas mediante la credencial protegida de Jenkins.
- Verificar conteo, documento GeoJSON, índices y segunda ejecución omitida.
- Ejecutar la carga completa y conservar `reporte_limpieza.json`.
