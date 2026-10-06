# F8 — Benchmark Dask vs Spark

Fecha: 5-oct-2026
Responsable: Santiago Villamizar
Equipo: PC de Santiago (Windows 11, AMD Ryzen, 16 GB de RAM, Docker Desktop 4.93 con WSL 2)
Rama: `feature/benchmark`

## Qué se midió

La misma operación en los dos motores (decisiones D5 y D16): leer `latitude` y `longitude` del
Parquet que escribe la ingesta, asignar cada punto a su celda de 0,005° (grilla de F6, D13),
contar por celda y obtener el top 20 y el total de filas.

- Config A: 1 worker × 2 núcleos. Config B: 2 workers × 2 núcleos.
- Volumen ×1: las 1.741.828 filas limpias. Volumen ×10: el mismo Parquet leído 10 veces,
  17.418.280 filas (D18).
- Por combinación: 1 corrida de calentamiento (no se reporta) y 3 repeticiones; 32 corridas en
  total. Mientras se medía un motor, el otro estaba detenido.
- Spark con particiones de shuffle iguales a los núcleos del clúster (D17).
- Memoria: pico de la suma de los contenedores del motor (scheduler/master, workers y
  cliente/driver), muestreado con `docker stats`.

Datos crudos: `benchmark/resultados.csv`. Tabla: `benchmark/resumen.md`.

## Resultados

| Datos | Motor | Config | Cálculo (s) | Arranque (s) | Pico de memoria (MiB) |
|---|---|---|---:|---:|---:|
| ×1 | Dask | A | 0,30 ± 0,01 | 0,03 | 425 ± 54 |
| ×1 | Dask | B | 0,20 ± 0,02 | 0,03 | 612 ± 59 |
| ×1 | Spark | A | 3,80 ± 0,17 | 3,38 | 1.077 ± 77 |
| ×1 | Spark | B | 4,65 ± 0,04 | 3,47 | 1.657 ± 106 |
| ×10 | Dask | A | 1,95 ± 0,15 | 0,03 | 479 ± 16 |
| ×10 | Dask | B | 1,27 ± 0,12 | 0,03 | 692 ± 5 |
| ×10 | Spark | A | 6,47 ± 0,07 | 3,47 | 1.416 ± 137 |
| ×10 | Spark | B | 8,02 ± 0,58 | 3,51 | 2.092 ± 79 |

![Tiempo de cálculo](bench_tiempo.png)

![Pico de memoria](bench_memoria.png)

**Consistencia.** En las 32 corridas los dos motores dieron el mismo top 1: la celda
`-14799_8151` (lon −73,995 a −73,990, lat 40,755 a 40,760; oeste de Midtown, junto a la
terminal Port Authority), con n = 5.336 en ×1 y exactamente 53.360 en ×10.

## Análisis

**¿Qué motor fue más rápido?** Dask, en todas las combinaciones: 12,6 veces más rápido en A y
23 veces en B con ×1; 3,3 y 6,3 veces con ×10. Además, Spark necesita unos 3,4 s solo para
crear la sesión y obtener sus executors, frente a 0,03 s de Dask para conectarse a su
scheduler.

**¿La diferencia se mantiene al crecer los datos?** No: se reduce. Con 10 veces más filas, el
tiempo de Dask creció 6,5 veces (0,30 → 1,95 s), mientras que el de Spark creció solo 1,7 veces
(3,80 → 6,47 s). Spark tiene un costo fijo alto (planificación en la JVM, tareas, shuffle) que
se reparte mejor cuanto más trabajo hay. Si la tendencia se mantuviera, Spark alcanzaría a Dask
con volúmenes de uno o dos órdenes de magnitud más que los de este proyecto; no lo medimos.

**¿Escala al pasar de 1 a 2 workers?** Dask sí, aunque no linealmente: ×1,50 con ×1 y ×1,53
con ×10 (×2 sería lineal). Parte del trabajo no se paraleliza: la lectura de 6 archivos
Parquet, la combinación final de los conteos y la coordinación con el scheduler. Spark, en
cambio, fue más lento con 2 workers (×0,82 y ×0,81). Los dos workers son contenedores en el
mismo computador: no suman CPU física nueva, y al repartir el `groupBy` los datos viajan
serializados por la red entre JVM distintas. En un clúster de varias máquinas, con más datos,
el segundo worker aportaría capacidad real.

**¿Cuál usó más memoria?** Spark: entre 2,5 y 3 veces lo de Dask, y creció unos 600 MiB con
el segundo worker. Cada executor es una JVM con un costo fijo de memoria, además del driver.
Dask creció poco al pasar de ×1 a ×10 (425 → 479 MiB en A) porque procesa el Parquet por
particiones en lugar de cargarlo completo.

**Conclusión con nuestros datos.**
- Para el volumen de este proyecto (≈ 1,7 M de registros, unos cientos de MB) y un solo
  computador, **Dask es la mejor opción**: más rápido, con menos memoria, sin costo de arranque
  y en el mismo ecosistema de pandas que usa la ingesta.
- **Spark se justifica cuando crece el volumen** —su ventaja relativa mejoró de ×13 a ×3 al
  multiplicar los datos por 10— y cuando hay varias máquinas reales, donde aporta tolerancia a
  fallos, un optimizador de consultas y el conector maduro con MongoDB que usamos en F6.
- Por eso el proyecto usa Dask para la ingesta y la limpieza, y Spark para las agregaciones
  sobre MongoDB: cada motor en el papel que estas mediciones respaldan.

## Limitaciones

- Todo corre en un solo computador: los workers comparten CPU, memoria y disco.
- `docker stats` toma una muestra cada ~2 s. Las corridas de Dask duran menos que eso, así que
  su CPU promedio no es confiable (no se reporta) y el pico de memoria puede subestimarse.
- La prueba ×10 repite los mismos datos: mide volumen, no diversidad (D18).
- Las 8 corridas iniciales de Dask ×1 se descartaron porque sus workers conservaban la memoria
  de la ingesta y su pico salió mayor que el de ×10. Se repitieron con los workers reiniciados,
  como en las demás pruebas. Los tiempos fueron iguales; solo cambió la memoria
  (`benchmark/resultados_descartados.csv`).
