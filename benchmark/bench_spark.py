"""
F8 — Benchmark: agregación por grilla con Spark.

Operación (idéntica en bench_dask.py):
  1. Leer latitude y longitude de /data/parquet/eventos (Parquet generado por la ingesta).
  2. Asignar cada punto a su celda: floor(lon / celda), floor(lat / celda).
  3. Contar puntos por celda.
  4. Obtener el top 20 de celdas y el total de filas procesadas.

Solo se cronometra el cálculo. La creación de la SparkSession y la espera de los executors
se miden aparte como "arranque" (la JVM de Spark tiene un costo de inicio fijo).

Salida: una línea  RESULTADO_BENCH {json}  que lee benchmark/medir.ps1.

Ejecutar (lo hace medir.ps1, que primero copia este archivo al contenedor):
  docker compose exec spark-master spark-submit /tmp/bench_spark.py --workers 2
"""
import argparse
import json
import os
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def executors_activos(spark):
    # getExecutorMemoryStatus incluye al driver, por eso se resta 1.
    return spark.sparkContext._jsc.sc().getExecutorMemoryStatus().size() - 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ruta", default="/data/parquet/eventos")
    p.add_argument("--celda", type=float, default=0.005)
    p.add_argument("--top", type=int, default=20)
    p.add_argument("--workers", type=int, required=True, help="workers esperados (1 o 2)")
    p.add_argument("--shuffle", type=int, default=0,
                   help="particiones del shuffle; 0 = una por núcleo del clúster (ver D17)")
    args = p.parse_args()

    t0 = time.perf_counter()
    spark = (SparkSession.builder.appName(f"f8-bench-spark-{args.workers}w")
             .master(os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077"))
             # La ingesta escribe la fecha con precisión de nanosegundos; Spark 3.5 no la
             # interpreta por defecto aunque no se use esa columna.
             .config("spark.sql.legacy.parquet.nanosAsLong", "true")
             .getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    limite = time.time() + 60
    while executors_activos(spark) < args.workers and time.time() < limite:
        time.sleep(1)
    workers = executors_activos(spark)
    if workers != args.workers:
        raise SystemExit(f"Se esperaban {args.workers} executors de Spark y hay {workers}")
    nucleos = spark.sparkContext.defaultParallelism
    # Spark usa 200 particiones de shuffle por defecto, pensado para clústeres grandes; con
    # 2-4 núcleos eso son cientos de tareas diminutas. Se iguala al número de núcleos (D17).
    spark.conf.set("spark.sql.shuffle.partitions", args.shuffle or nucleos)
    arranque = time.perf_counter() - t0

    inicio = time.perf_counter()
    df = spark.read.parquet(args.ruta).select("latitude", "longitude")
    conteo = (df.groupBy(F.floor(F.col("longitude") / args.celda).alias("cx"),
                         F.floor(F.col("latitude") / args.celda).alias("cy"))
              .count()
              .cache())  # el top y el total comparten la misma lectura del Parquet
    filas = conteo.agg(F.sum("count")).first()[0]
    top = conteo.orderBy(F.col("count").desc()).limit(args.top).collect()
    segundos = time.perf_counter() - inicio

    resultado = {
        "motor": "spark",
        "workers": workers,
        "nucleos": nucleos,
        "particiones": df.rdd.getNumPartitions(),
        "shuffle": int(spark.conf.get("spark.sql.shuffle.partitions")),
        "segundos": round(segundos, 3),
        "arranque_s": round(arranque, 3),
        "filas": int(filas),
        "top1": f"{top[0]['cx']}_{top[0]['cy']}",
        "top1_n": int(top[0]["count"]),
    }
    print("RESULTADO_BENCH " + json.dumps(resultado))
    spark.stop()


if __name__ == "__main__":
    main()
