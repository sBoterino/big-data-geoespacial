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

## Pendiente

- Ejecutar una muestra real de 50.000 filas mediante la credencial protegida de Jenkins.
- Verificar conteo, documento GeoJSON, índices y segunda ejecución omitida.
- Ejecutar la carga completa y conservar `reporte_limpieza.json`.
