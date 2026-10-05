# Fase 5 — consultas geoespaciales contra datos semilla

Fecha: 4-oct-2026

Rama: `feature/api-consultas`

Contenedor temporal: `bdgeo-api-f5-test`, colección `eventos_semilla`

## Resultados

| Consulta | Resultado esperado | Resultado observado | Tiempo |
|---|---:|---:|---:|
| `$near`, Times Square, radio 1.000 m | 120 | 120 | 12,408 ms |
| `$geoWithin`, polígono Midtown | 120 | 120 | 3,093 ms |
| `$geoNear`, radio 1.000 m, agrupado por `grupo` | 1 grupo / n=120 | 1 grupo / n=120 | 11,397 ms |

Los tres conteos coinciden exactamente con `mongo/init/semilla_esperados.json`. La API utilizó
parámetros recibidos en cada petición y el contenedor temporal evitó modificar la API de
producción. Los tiempos observados están ampliamente por debajo del objetivo de 500 ms.

Esta prueba aprueba la integración de F5 con MongoDB y el índice `2dsphere` sobre la semilla.
Todavía faltan las mediciones sobre `eventos`, la ejecución de los smoke tests en Jenkins y el
merge a `main`.
