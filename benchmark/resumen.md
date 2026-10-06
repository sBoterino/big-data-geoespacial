# Resultados del benchmark Dask vs Spark

Corridas registradas (sin calentamiento): 24

| Datos | Motor | Config | Workers × núcleos | Cálculo (s) | Arranque (s) | Pico de memoria (MiB) | CPU prom. (%) | Filas |
|---|---|---|---|---:|---:|---:|---:|---:|
| ×1 | dask | A | 1 × 2 | 0.30 ± 0.01 | 0.03 | 425 ± 54 | 32 | 1.741.828 |
| ×1 | dask | B | 2 × 2 | 0.20 ± 0.02 | 0.03 | 612 ± 59 | 26 | 1.741.828 |
| ×1 | spark | A | 1 × 2 | 3.80 ± 0.17 | 3.38 | 1077 ± 77 | 187 | 1.741.828 |
| ×1 | spark | B | 2 × 2 | 4.65 ± 0.04 | 3.47 | 1657 ± 106 | 350 | 1.741.828 |
| ×10 | dask | A | 1 × 2 | 2.36 ± 0.05 | 0.03 | 491 ± 19 | 68 | 17.418.280 |
| ×10 | dask | B | 2 × 2 | 1.39 ± 0.05 | 0.03 | 698 ± 2 | 46 | 17.418.280 |
| ×10 | spark | A | 1 × 2 | 4.51 ± 0.20 | 3.38 | 1121 ± 54 | 199 | 17.418.280 |
| ×10 | spark | B | 2 × 2 | 5.12 ± 0.21 | 3.45 | 1816 ± 114 | 290 | 17.418.280 |

## Escalamiento de A (1 worker) a B (2 workers)

- datos ×1, dask: 0.30 s → 0.20 s, aceleración ×1.50 (×2,00 sería escalamiento lineal)
- datos ×1, spark: 3.80 s → 4.65 s, aceleración ×0.82 (×2,00 sería escalamiento lineal)
- datos ×10, dask: 2.36 s → 1.39 s, aceleración ×1.69 (×2,00 sería escalamiento lineal)
- datos ×10, spark: 4.51 s → 5.12 s, aceleración ×0.88 (×2,00 sería escalamiento lineal)

## Dask frente a Spark

- datos ×1, config A: Spark tarda ×12.7 lo que tarda Dask
- datos ×1, config B: Spark tarda ×23.3 lo que tarda Dask
- datos ×10, config A: Spark tarda ×1.9 lo que tarda Dask
- datos ×10, config B: Spark tarda ×3.7 lo que tarda Dask

## Consistencia de resultados

- datos ×1, dask: top 1 = -14799_8151 con n = 5336
- datos ×1, spark: top 1 = -14799_8151 con n = 5336
- datos ×10, dask: top 1 = -14799_8151 con n = 53360
- datos ×10, spark: top 1 = -14799_8151 con n = 53360
