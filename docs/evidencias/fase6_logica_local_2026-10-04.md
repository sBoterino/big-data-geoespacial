# F6 — Validación de la lógica de Spark en local

Fecha: 4-oct-2026
Responsable: Santiago Villamizar
Rama: `feature/spark-agregaciones`

## Qué se probó

Las funciones puras `agregar_por_celda`, `seleccionar_hotspots` (grilla) y `agregar` (temporal)
se ejecutaron con PySpark 3.5.3 en modo local (`local[2]`) sobre los 300 puntos de
`mongo/init/02-semilla.js`. Esta prueba no usa MongoDB: valida la lógica de agregación antes
de correrla en el clúster Docker.

## Resultados

| Comprobación | Resultado |
|---|---:|
| Puntos leídos | 300 |
| Suma de `n` en la grilla (celda 0,005°) | 300 |
| Celdas con al menos un punto | 92 |
| Hotspot #1 | celda `-14798_8151`, n = 57 |
| Centroide del hotspot #1 | `[-73.987295, 40.757704]` (≈ 200 m de Times Square) |
| Hotspot #2 | celda `-14797_8151`, n = 42 (también Times Square) |
| Hotspot #3 | celda `-14798_8139`, n = 26 (Brooklyn Bridge) |
| Suma de `n` por hora / día / mes / hora×borough | 300 / 300 / 300 / 300 |

El polígono del hotspot #1 quedó en GeoJSON válido, orden `[lon, lat]` y anillo cerrado:
`[[-73.99, 40.755], [-73.985, 40.755], [-73.985, 40.76], [-73.99, 40.76], [-73.99, 40.755]]`.

## Validación en el clúster Docker (5-oct-2026, PC de Santiago)

Los tres jobs se ejecutaron con `spark-submit` en `spark-master` (1 worker, 2 núcleos, 1 GiB por
executor), leyendo y escribiendo con el MongoDB Spark Connector:

- `agregacion_grilla.py --coleccion eventos_semilla`: leídos=300, celdas=92, suma_n=300,
  duración 10,858 s. Top 5: n = 57, 42 (Times Square), 26, 24, 19 (Brooklyn Bridge).
- `agregacion_temporal.py --coleccion eventos_semilla`: cuatro colecciones `spark_semilla_*`.
- `verificar_resultados.py --coleccion eventos_semilla`: **RESULTADO: OK**.

```
[verificar] documentos en eventos_semilla: 300
[verificar] OK    suma de n en spark_semilla_grilla = 300 (esperado 300)
[verificar] OK    suma de n en spark_semilla_por_hora = 300 (esperado 300)
[verificar] OK    suma de n en spark_semilla_por_dia_semana = 300 (esperado 300)
[verificar] OK    suma de n en spark_semilla_por_mes = 300 (esperado 300)
[verificar] OK    hotspot #1 (-14798_8151): Spark n=57, MongoDB $geoWithin=57 (margen ±1)
[verificar] OK    la semilla tiene 300 documentos
[verificar] OK    hotspot #1 a 155 m de Times Square (< 1000 m)
[verificar] RESULTADO: OK
```

El conteo de Spark para el hotspot #1 coincide exactamente con el de MongoDB usando el índice
2dsphere, lo que valida la asignación de celdas y el orden `[lon, lat]`.

## Pendiente

- Correrlos sobre los 1.741.828 documentos de `eventos` y registrar el top 5 de hotspots,
  los tiempos y una captura de la UI de Spark.
