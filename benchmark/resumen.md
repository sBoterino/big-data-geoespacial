# Resultados del benchmark Dask vs Spark

Corridas registradas (sin calentamiento): 24

| Datos | Motor | Config | Workers × núcleos | Cálculo (s) | Arranque (s) | Pico de memoria (MiB) | CPU prom. (%) | Filas |
|---|---|---|---|---:|---:|---:|---:|---:|
| ×1 | dask | A | 1 × 2 | 0.30 ± 0.01 | 0.03 | 425 ± 54 | 32 | 1.741.828 |
| ×1 | dask | B | 2 × 2 | 0.20 ± 0.02 | 0.03 | 612 ± 59 | 26 | 1.741.828 |
| ×1 | spark | A | 1 × 2 | 3.80 ± 0.17 | 3.38 | 1077 ± 77 | 187 | 1.741.828 |
| ×1 | spark | B | 2 × 2 | 4.65 ± 0.04 | 3.47 | 1657 ± 106 | 350 | 1.741.828 |
| ×10 | dask | A | 1 × 2 | 1.95 ± 0.15 | 0.03 | 479 ± 16 | 85 | 17.418.280 |
| ×10 | dask | B | 2 × 2 | 1.27 ± 0.12 | 0.03 | 692 ± 5 | 32 | 17.418.280 |
| ×10 | spark | A | 1 × 2 | 6.47 ± 0.07 | 3.47 | 1416 ± 137 | 224 | 17.418.280 |
| ×10 | spark | B | 2 × 2 | 8.02 ± 0.58 | 3.51 | 2092 ± 79 | 368 | 17.418.280 |

## Escalamiento de A (1 worker) a B (2 workers)

- datos ×1, dask: 0.30 s → 0.20 s, aceleración ×1.50 (×2,00 sería escalamiento lineal)
- datos ×1, spark: 3.80 s → 4.65 s, aceleración ×0.82 (×2,00 sería escalamiento lineal)
- datos ×10, dask: 1.95 s → 1.27 s, aceleración ×1.53 (×2,00 sería escalamiento lineal)
- datos ×10, spark: 6.47 s → 8.02 s, aceleración ×0.81 (×2,00 sería escalamiento lineal)

## Dask frente a Spark

- datos ×1, config A: Spark tarda ×12.7 lo que tarda Dask
- datos ×1, config B: Spark tarda ×23.3 lo que tarda Dask
- datos ×10, config A: Spark tarda ×3.3 lo que tarda Dask
- datos ×10, config B: Spark tarda ×6.3 lo que tarda Dask

## Consistencia de resultados

- datos ×1, dask: top 1 = -14799_8151 con n = 5336
- datos ×1, spark: top 1 = -14799_8151 con n = 5336
- datos ×10, dask: top 1 = -14799_8151 con n = 53360
- datos ×10, spark: top 1 = -14799_8151 con n = 53360
