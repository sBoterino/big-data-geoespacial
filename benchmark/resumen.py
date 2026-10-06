"""
F8 — Resume benchmark/resultados.csv en una tabla markdown (benchmark/resumen.md).

Descarta las corridas de calentamiento (repeticion = 0) y calcula media y desviación estándar
del tiempo de cálculo, del arranque, del pico de memoria y del CPU por motor y configuración.
También compara A contra B (aceleración) y comprueba que ambos motores dieron el mismo top 1.

Ejecutar (usa la imagen de Dask, que ya trae pandas):
  docker compose run --rm -v "${PWD}/benchmark:/opt/bench" dask-job python /opt/bench/resumen.py
"""
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent


def main():
    df = pd.read_csv(AQUI / "resultados.csv", encoding="utf-8-sig")
    medidas = df[df["repeticion"] > 0]

    tabla = (medidas.groupby(["motor", "config"])
             .agg(corridas=("segundos", "size"),
                  workers=("workers", "first"),
                  nucleos=("nucleos", "first"),
                  calculo_s=("segundos", "mean"),
                  calculo_de=("segundos", "std"),
                  arranque_s=("arranque_s", "mean"),
                  mem_pico_mib=("mem_pico_mib", "mean"),
                  mem_de=("mem_pico_mib", "std"),
                  cpu_pct=("cpu_prom_pct", "mean"),
                  filas=("filas", "first"))
             .reset_index())

    lineas = [
        "# Resultados del benchmark Dask vs Spark",
        "",
        "Corridas registradas (sin calentamiento): " + str(len(medidas)),
        "",
        "| Motor | Config | Workers × núcleos | Cálculo (s) | Arranque (s) | Pico de memoria (MiB) | CPU prom. (%) | Filas |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, f in tabla.iterrows():
        lineas.append(
            f"| {f.motor} | {f.config} | {f.workers} × {int(f.nucleos) // max(int(f.workers), 1)} "
            f"| {f.calculo_s:.2f} ± {0 if pd.isna(f.calculo_de) else f.calculo_de:.2f} "
            f"| {f.arranque_s:.2f} "
            f"| {f.mem_pico_mib:.0f} ± {0 if pd.isna(f.mem_de) else f.mem_de:.0f} "
            f"| {f.cpu_pct:.0f} | {int(f.filas):,} |".replace(",", ".")
        )

    lineas += ["", "## Escalamiento de A (1 worker) a B (2 workers)", ""]
    for motor, g in tabla.groupby("motor"):
        t = dict(zip(g["config"], g["calculo_s"]))
        if "A" in t and "B" in t:
            lineas.append(f"- {motor}: {t['A']:.2f} s → {t['B']:.2f} s, aceleración ×{t['A'] / t['B']:.2f}"
                          " (×2,00 sería escalamiento lineal)")

    lineas += ["", "## Consistencia de resultados", ""]
    tops = medidas.groupby("motor")[["top1", "top1_n"]].agg(lambda s: sorted(set(s.astype(str))))
    for motor, f in tops.iterrows():
        lineas.append(f"- {motor}: top 1 = {', '.join(f.top1)} con n = {', '.join(f.top1_n)}")

    (AQUI / "resumen.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
