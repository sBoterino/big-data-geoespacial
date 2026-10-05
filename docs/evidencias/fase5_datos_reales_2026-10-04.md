# Fase 5 — consultas geoespaciales sobre datos reales

Fecha: 4-oct-2026

Rama: `feature/api-consultas`

Colección: `eventos` (1.741.828 documentos)

Punto de prueba: Times Square (`lat=40.758`, `lon=-73.9855`), radio 1.000 m.

## Cinco ejecuciones

| Ejecución | `$near` (100 docs) | `$geoWithin` (100 docs) | `$geoNear` agrupado (5 grupos) |
|---:|---:|---:|---:|
| 1 | 322,602 ms | 748,619 ms | 3.246,483 ms |
| 2 | 15,374 ms | 106,729 ms | 1.870,785 ms |
| 3 | 13,095 ms | 98,096 ms | 1.770,044 ms |
| 4 | 11,401 ms | 101,634 ms | 1.780,945 ms |
| 5 | 14,103 ms | 91,663 ms | 1.722,931 ms |

Promedio caliente (ejecuciones 2–5): `$near` 13,493 ms, `$geoWithin` 99,531 ms y `$geoNear`
agrupado 1.786,176 ms.

## `$geoNear` sin agrupación

| Ejecución | Documentos | Tiempo |
|---:|---:|---:|
| 1 | 100 | 495,027 ms |
| 2 | 100 | 192,703 ms |
| 3 | 100 | 181,121 ms |
| 4 | 100 | 173,593 ms |
| 5 | 100 | 181,701 ms |

Promedio caliente (ejecuciones 2–5): 182,280 ms. Todas las ejecuciones del uso normal quedaron
por debajo del objetivo de 500 ms.

La diferencia es esperable: sin agrupación MongoDB puede detenerse al obtener los 100 vecinos;
con `agrupar=borough` debe calcular las distancias de todos los documentos dentro del radio antes
de agruparlos. Se conservan ambas mediciones para explicar el costo de la agregación en el informe
y la sustentación.
