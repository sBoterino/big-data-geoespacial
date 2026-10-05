# Gate 4 — carga completa con Dask

Fecha de ejecución: 4-oct-2026 (UTC del reporte: 5-oct-2026)

Build: `bdgeo-main` #6
Commit: merge del PR #1
Resultado: `SUCCESS`

## Resultado de la ingesta

| Métrica | Resultado |
|---|---:|
| Filas de entrada | 1.972.121 |
| Particiones Dask | 6 |
| R1: coordenadas nulas/no numéricas | 226.028 |
| R2: coordenadas `(0,0)` | 4.115 |
| R3: coordenadas fuera de WGS84 | 106 |
| R4: coordenadas fuera de NYC | 44 |
| R5: fecha/hora inválida | 0 |
| R6: `COLLISION_ID` duplicado | 0 |
| Documentos insertados | 1.741.828 |
| Duración de la ingesta | 57,435 s |

Los descartes suman 230.293 y se contabilizaron de manera exclusiva siguiendo el orden R1–R6.
La identidad `1.972.121 - 230.293 = 1.741.828` coincide con MongoDB.

## Ejecución distribuida e integración

- Dos workers Dask conectados y seis particiones procesadas.
- Caché de Kaggle reutilizada; CSV verificado en 420.704.526 bytes.
- Cinco pruebas de ingesta aprobadas y cuatro pruebas de API aprobadas.
- Integración Dask aprobada.
- Integración Spark–MongoDB aprobada con los controles 120/80/100.
- Staging y smoke tests aprobados.
- API de producción desplegada como versión 6.

## Auditoría directa posterior

- `geo.eventos.countDocuments({})`: 1.741.828.
- Documento observado: `_id='4486564'`.
- GeoJSON: `Point [-74.00231, 40.59662]`, orden longitud/latitud.
- Fecha BSON: `ISODate('2021-12-14T00:59:00.000Z')`.
- Índices: `_id_`, `fecha_1`, `location_2dsphere`.

El reporte original generado por el pipeline se conserva en
`docs/evidencias/reporte_limpieza_completo_2026-10-04.json`.

## Gate

La carga completa, la limpieza justificada, el almacenamiento MongoDB, GeoJSON, los índices y las
integraciones están aprobados. La siguiente ejecución de `bdgeo-main` debe omitir la carga y dejar
evidencia de idempotencia sobre los 1.741.828 documentos antes de dar el Gate 4 por cerrado.
