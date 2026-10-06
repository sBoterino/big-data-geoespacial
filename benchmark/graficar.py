"""
F8 — Gráficas del benchmark a partir de benchmark/resultados.csv (barras con media y desviación).

Requiere matplotlib (no está en las imágenes del proyecto). Uso:
  python benchmark/graficar.py docs/evidencias
"""
from pathlib import Path
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = Path(__file__).resolve().parent
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI
COLOR = {"dask": "#2a78d6", "spark": "#eb6834"}   # slots categóricos 1 y 2
TEXTO, TEXTO2, GRILLA = "#0b0b0b", "#52514e", "#e4e3df"

df = pd.read_csv(AQUI / "resultados.csv", encoding="utf-8-sig")
df = df[df["repeticion"] > 0]
g = df.groupby(["replicas", "motor", "config"]).agg(
    t=("segundos", "mean"), t_de=("segundos", "std"),
    m=("mem_pico_mib", "mean"), m_de=("mem_pico_mib", "std")).reset_index()


def figura(col, de, titulo, eje, archivo, fmt):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, ejes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=150)
    for ax, rep in zip(ejes, [1, 10]):
        sub = g[g.replicas == rep]
        filas = f"{1741828 * rep:,}".replace(",", ".")
        xs = [0, 1]
        ancho = 0.36
        for k, motor in enumerate(["dask", "spark"]):
            d = sub[sub.motor == motor].set_index("config").loc[["A", "B"]]
            pos = [x + (k - 0.5) * (ancho + 0.03) for x in xs]
            barras = ax.bar(pos, d[col], ancho, color=COLOR[motor], label=motor.capitalize(),
                            yerr=d[de], error_kw={"ecolor": TEXTO2, "elinewidth": 1, "capsize": 3},
                            zorder=3)
            for b, v, e in zip(barras, d[col], d[de].fillna(0)):
                ax.annotate(fmt(v), (b.get_x() + b.get_width() / 2, v + e), xytext=(0, 4),
                            textcoords="offset points", ha="center", va="bottom",
                            fontsize=9, color=TEXTO)
        ax.set_xticks(xs, ["A · 1 worker × 2 núcleos", "B · 2 workers × 2 núcleos"], color=TEXTO2)
        ax.set_title(f"Datos ×{rep} ({filas} filas)", fontsize=11, color=TEXTO, loc="left")
        ax.set_ylabel(eje, color=TEXTO2)
        ax.grid(axis="y", color=GRILLA, zorder=0)
        ax.set_facecolor("#fcfcfb")
        ax.set_ylim(0, (sub[col] + sub[de].fillna(0)).max() * 1.2)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRILLA)
        ax.tick_params(colors=TEXTO2)
    ejes[0].legend(frameon=False, loc="upper left")
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=13, color=TEXTO, fontweight="bold")
    fig.text(0.01, 0.005, "Media de 3 repeticiones (sin calentamiento); la barra de error es la desviación estándar.",
             fontsize=8, color=TEXTO2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(SALIDA / archivo, facecolor="#fcfcfb")
    print("guardado", SALIDA / archivo)


figura("t", "t_de", "Tiempo de cálculo de la agregación por grilla", "segundos",
       "bench_tiempo.png", lambda v: f"{v:.2f} s".replace(".", ","))
figura("m", "m_de", "Pico de memoria de los contenedores del motor", "MiB",
       "bench_memoria.png", lambda v: f"{v:,.0f}".replace(",", "."))
