"""
F8 — Benchmark: agregación por grilla con Dask.

Operación (idéntica en bench_spark.py):
  1. Leer latitude y longitude del Parquet: /data/parquet/eventos (ingesta, ×1) o
     /data/parquet/eventos_x10 (copia física ×10 creada con preparar_volumen.py, D18).
  2. Asignar cada punto a su celda: floor(lon / celda), floor(lat / celda).
  3. Contar puntos por celda.
  4. Obtener el top 20 de celdas y el total de filas procesadas.

Solo se cronometra el cálculo (desde la lectura hasta tener el resultado en el cliente).
La conexión al clúster se mide aparte como "arranque".

Salida: una línea  RESULTADO_BENCH {json}  que lee benchmark/medir.ps1.

Ejecutar (lo hace medir.ps1):
  docker compose run --rm -v "${PWD}/benchmark:/opt/bench" dask-job python /opt/bench/bench_dask.py --workers 2
"""
import argparse
import json
import os
import time

import dask
import dask.dataframe as dd
import numpy as np
from dask.distributed import Client


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ruta", default="/data/parquet/eventos")
    p.add_argument("--celda", type=float, default=0.005)
    p.add_argument("--top", type=int, default=20)
    p.add_argument("--workers", type=int, required=True, help="workers esperados (1 o 2)")
    args = p.parse_args()

    t0 = time.perf_counter()
    client = Client(os.getenv("DASK_SCHEDULER", "tcp://dask-scheduler:8786"), timeout=30)
    client.wait_for_workers(args.workers, timeout=60)
    workers = len(client.scheduler_info()["workers"])
    if workers != args.workers:
        raise SystemExit(f"Se esperaban {args.workers} workers de Dask y hay {workers}")
    hilos = sum(w["nthreads"] for w in client.scheduler_info()["workers"].values())
    arranque = time.perf_counter() - t0

    inicio = time.perf_counter()
    df = dd.read_parquet(args.ruta, columns=["latitude", "longitude"])
    df = df.assign(
        cx=np.floor(df["longitude"] / args.celda).astype("int64"),
        cy=np.floor(df["latitude"] / args.celda).astype("int64"),
    )
    conteo = df.groupby(["cx", "cy"]).size()
    # Un solo compute: el top y el total comparten la misma lectura del Parquet.
    top, filas = dask.compute(conteo.nlargest(args.top), conteo.sum())
    segundos = time.perf_counter() - inicio

    (cx, cy), n1 = next(iter(top.items()))
    resultado = {
        "motor": "dask",
        "workers": workers,
        "nucleos": hilos,
        "particiones": df.npartitions,
        "segundos": round(segundos, 3),
        "arranque_s": round(arranque, 3),
        "filas": int(filas),
        "top1": f"{cx}_{cy}",
        "top1_n": int(n1),
    }
    print("RESULTADO_BENCH " + json.dumps(resultado))
    client.close()


if __name__ == "__main__":
    main()
