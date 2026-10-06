# Benchmark Dask vs Spark (F8)

Compara los dos motores ejecutando **la misma operación pesada** sobre **la misma fuente** y
con **los mismos recursos** (decisión D5).

## Operación

1. Leer `latitude` y `longitude` de `/data/parquet/eventos` (Parquet que escribe la ingesta,
   1.741.828 filas limpias).
2. Asignar cada punto a su celda de 0,005° (la grilla de F6, decisión D13).
3. Contar puntos por celda.
4. Obtener el top 20 de celdas y el total de filas.

Solo se cronometra el cálculo. El arranque (conexión al clúster de Dask o creación de la
SparkSession y espera de executors) se mide aparte en `arranque_s`.

## Configuraciones

| Config | Dask | Spark |
|---|---|---|
| A | 1 worker × 2 hilos (`dask-worker-2` detenido) | 1 worker × 2 núcleos |
| B | 2 workers × 2 hilos | 2 workers × 2 núcleos (`spark-worker-2`, perfil `bench`) |

Cada combinación: 1 corrida de calentamiento (repetición 0, no entra en el resumen) y
3 repeticiones. Mientras se mide un motor, el otro se detiene para no competir por RAM y CPU.

## Archivos

| Archivo | Qué hace |
|---|---|
| `bench_dask.py` | Operación con Dask; imprime `RESULTADO_BENCH {json}` |
| `bench_spark.py` | Operación con Spark; imprime `RESULTADO_BENCH {json}` |
| `medir.ps1` | Una corrida: muestrea `docker stats`, ejecuta el benchmark y agrega una fila a `resultados.csv` |
| `preparar_volumen.py` | Copia física ×N del Parquet para la prueba de volumen (D18) |
| `resumen.py` | Media y desviación por motor y configuración → `resumen.md` |
| `graficar.py` | Gráficas de tiempo y memoria (requiere matplotlib) |
| `resultados.csv` | Mediciones crudas (32 corridas) |
| `resultados_descartados.csv` | Corridas descartadas, con el motivo |
| `resumen.md` | Tabla resumen generada por `resumen.py` |

## Protocolo (PowerShell, desde la raíz del repositorio)

Requisito: la ingesta completa ya corrió en este computador (existe `/data/parquet/eventos`).

```powershell
docker compose up -d

# ---------- Dask, config A ----------
docker compose stop spark-worker spark-master dask-worker-2
.\benchmark\medir.ps1 -Motor dask -Config A -Repeticion 0
1..3 | ForEach-Object { .\benchmark\medir.ps1 -Motor dask -Config A -Repeticion $_ }

# ---------- Dask, config B ----------
docker compose start dask-worker-2
.\benchmark\medir.ps1 -Motor dask -Config B -Repeticion 0
1..3 | ForEach-Object { .\benchmark\medir.ps1 -Motor dask -Config B -Repeticion $_ }

# ---------- Spark, config A ----------
docker compose stop dask-worker-1 dask-worker-2
docker compose start spark-master spark-worker
.\benchmark\medir.ps1 -Motor spark -Config A -Repeticion 0
1..3 | ForEach-Object { .\benchmark\medir.ps1 -Motor spark -Config A -Repeticion $_ }

# ---------- Spark, config B ----------
docker compose --profile bench up -d spark-worker-2
.\benchmark\medir.ps1 -Motor spark -Config B -Repeticion 0
1..3 | ForEach-Object { .\benchmark\medir.ps1 -Motor spark -Config B -Repeticion $_ }

# ---------- Restaurar y resumir ----------
docker compose --profile bench stop spark-worker-2
docker compose up -d
docker compose run --rm -v "${PWD}/benchmark:/opt/bench" dask-job python /opt/bench/resumen.py
```

Si PowerShell bloquea el script por la política de ejecución, habilitarlo solo para la
sesión actual: `Set-ExecutionPolicy -Scope Process Bypass`.

## Prueba de volumen (×10, decisión D18)

Primero se crea una copia física ×10 del Parquet (60 archivos, 17.418.280 filas):

```powershell
docker compose run --rm -v "${PWD}/benchmark:/opt/bench" dask-job python /opt/bench/preparar_volumen.py --veces 10
```

Después se repite el protocolo agregando `-Replicas 10` a cada `medir.ps1`, que entonces lee
`/data/parquet/eventos_x10`. Por ejemplo:

```powershell
.\benchmark\medir.ps1 -Motor dask -Config A -Repeticion 0 -Replicas 10
1..3 | ForEach-Object { .\benchmark\medir.ps1 -Motor dask -Config A -Repeticion $_ -Replicas 10 }
```

El top 1 de esta prueba debe ser exactamente 10 veces el de la prueba ×1.

## Análisis

Resultados, gráficas y análisis: `docs/evidencias/fase8_benchmark_2026-10-05.md`.

En resumen: con el volumen del proyecto Dask fue más rápido en todas las combinaciones, pero su
ventaja bajó de ×12,7 a ×1,9 (config A) al pasar a 10 veces más filas; Spark no ganó con el
segundo worker porque ambos comparten el mismo computador. La memoria es el pico observado
con `docker stats` y la posible convergencia de Spark con más datos es una hipótesis no medida.

Preguntas que responde:
qué motor fue más rápido en A y en B; cuánto mejoró cada uno de A a B y por qué no escala
linealmente; cuál usó más memoria (la JVM de Spark tiene un costo fijo); cuánto pesa el
arranque; y, con estos datos, cuándo conviene cada motor.
