"""
F8 — Crea una copia física N veces más grande del Parquet de la ingesta (decisión D18).

Copia cada archivo de datos de /data/parquet/eventos N veces a /data/parquet/eventos_xN con
nombres distintos. Así los dos motores leen de verdad N veces más filas desde disco.

Por qué no basta con concatenar lecturas dentro de cada motor: Dask reconoce que
dd.concat([base] * N) son N copias de la misma lectura y lee el Parquet una sola vez, mientras
que Spark con unionAll lo lee N veces. Esa versión del benchmark quedó sesgada y se descartó.

Ejecutar (una sola vez, en el contenedor de Dask, que monta el volumen /data):
  docker compose run --rm -v "${PWD}/benchmark:/opt/bench" dask-job python /opt/bench/preparar_volumen.py --veces 10
"""
import argparse
import shutil
from pathlib import Path

import pyarrow.parquet as pq


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--origen", default="/data/parquet/eventos")
    p.add_argument("--veces", type=int, default=10)
    args = p.parse_args()

    origen = Path(args.origen)
    destino = origen.parent / f"{origen.name}_x{args.veces}"
    # Solo archivos de datos: _metadata / _common_metadata listarían los archivos originales.
    archivos = sorted(f for f in origen.glob("*.parquet") if not f.name.startswith(("_", ".")))
    if not archivos:
        raise SystemExit(f"No hay archivos Parquet en {origen}. ¿Corrió la ingesta?")

    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    for i in range(args.veces):
        for f in archivos:
            shutil.copyfile(f, destino / f"copia{i:02d}_{f.name}")

    filas_origen = sum(pq.ParquetFile(f).metadata.num_rows for f in archivos)
    filas_destino = sum(pq.ParquetFile(f).metadata.num_rows for f in destino.glob("*.parquet"))
    mb = sum(f.stat().st_size for f in destino.glob("*.parquet")) / 1024 ** 2
    print(f"[volumen] {len(archivos)} archivos × {args.veces} = "
          f"{len(list(destino.glob('*.parquet')))} archivos en {destino} ({mb:.0f} MB)")
    print(f"[volumen] filas: origen {filas_origen:,} -> destino {filas_destino:,}")
    if filas_destino != filas_origen * args.veces:
        raise SystemExit("[volumen] FALLO: el número de filas no es exactamente N veces el original")
    print("[volumen] OK")


if __name__ == "__main__":
    main()
