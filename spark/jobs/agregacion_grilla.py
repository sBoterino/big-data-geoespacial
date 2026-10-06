"""
F6 — Agregación espacial por grilla con Spark.

Divide el mapa en celdas cuadradas de `--celda` grados (0.005° ≈ 555 m de norte a sur y
≈ 420 m de este a oeste en la latitud de NYC) y, por cada celda, cuenta los eventos y suma
heridos y muertos.

Salidas (con prefijo "spark_" para la colección real):
  <prefijo>grilla    todas las celdas con n, heridos, muertos, centroide y polígono GeoJSON
  <prefijo>hotspots  las `--top` celdas con más eventos, con su ranking
  <prefijo>meta      registro de la ejecución (_id = "grilla")

Ejecutar:
  docker compose exec spark-master spark-submit /opt/jobs/agregacion_grilla.py
  docker compose exec spark-master spark-submit /opt/jobs/agregacion_grilla.py --coleccion eventos_semilla
"""
import argparse
import time
from datetime import datetime, timezone

from pyspark.sql import Window
from pyspark.sql import functions as F

from comun import crear_sesion, escribir, leer_eventos, prefijo_por_defecto, registrar_meta


def argumentos():
    p = argparse.ArgumentParser(description="Agregación por grilla y hotspots")
    p.add_argument("--coleccion", default="eventos", help="colección de origen en MongoDB")
    p.add_argument("--celda", type=float, default=0.005, help="tamaño de la celda en grados")
    p.add_argument("--top", type=int, default=20, help="número de hotspots a guardar")
    p.add_argument("--prefijo", default=None, help="prefijo de las colecciones de salida")
    return p.parse_args()


def agregar_por_celda(df, celda):
    """Asigna cada punto a su celda y agrega. Función pura sobre DataFrames (sin E/S)."""
    con_celda = (df
                 .withColumn("celda_x", F.floor(F.col("lon") / celda).cast("long"))
                 .withColumn("celda_y", F.floor(F.col("lat") / celda).cast("long")))

    # groupBy provoca un shuffle: los registros de una misma celda viajan al mismo executor.
    agregado = con_celda.groupBy("celda_x", "celda_y").agg(
        F.count("*").alias("n"),
        F.sum("heridos").cast("long").alias("heridos"),
        F.sum("muertos").cast("long").alias("muertos"),
        F.avg("lon").alias("centroide_lon"),
        F.avg("lat").alias("centroide_lat"),
    )

    # Esquinas de la celda, redondeadas para que el polígono sea exactamente reproducible.
    x0 = F.round(F.col("celda_x") * celda, 6)
    y0 = F.round(F.col("celda_y") * celda, 6)
    x1 = F.round((F.col("celda_x") + 1) * celda, 6)
    y1 = F.round((F.col("celda_y") + 1) * celda, 6)
    anillo = F.array(F.array(x0, y0), F.array(x1, y0), F.array(x1, y1),
                     F.array(x0, y1), F.array(x0, y0))

    return (agregado
            .withColumn("_id", F.concat_ws("_", "celda_x", "celda_y"))
            .withColumn("celda", F.struct(F.lit("Polygon").alias("type"),
                                          F.array(anillo).alias("coordinates")))
            .withColumn("centroide", F.struct(
                F.lit("Point").alias("type"),
                F.array(F.round("centroide_lon", 6), F.round("centroide_lat", 6)).alias("coordinates")))
            .drop("centroide_lon", "centroide_lat"))


def seleccionar_hotspots(grilla, top):
    # Desempate determinista por _id para que el ranking no cambie entre ejecuciones.
    orden = Window.orderBy(F.col("n").desc(), F.col("_id"))
    return grilla.withColumn("ranking", F.row_number().over(orden)).filter(F.col("ranking") <= top)


def main():
    args = argumentos()
    prefijo = args.prefijo or prefijo_por_defecto(args.coleccion)
    spark = crear_sesion(f"f6-grilla-{args.coleccion}")
    spark.sparkContext.setLogLevel("WARN")
    inicio = time.perf_counter()

    eventos = leer_eventos(spark, args.coleccion).cache()
    total = eventos.count()

    grilla = agregar_por_celda(eventos, args.celda).cache()
    hotspots = seleccionar_hotspots(grilla, args.top)

    escribir(grilla, f"{prefijo}grilla")
    escribir(hotspots, f"{prefijo}hotspots")

    suma_n = grilla.agg(F.sum("n")).first()[0] or 0
    celdas = grilla.count()
    duracion = round(time.perf_counter() - inicio, 3)

    registrar_meta(spark, prefijo, {
        "_id": "grilla",
        "coleccion_origen": args.coleccion,
        "celda_grados": args.celda,
        "top": args.top,
        "total_leido": total,
        "suma_n": int(suma_n),
        "celdas": celdas,
        "duracion_s": duracion,
        "calculado_en": datetime.now(timezone.utc).isoformat(),
    })

    print(f"[grilla] origen={args.coleccion} leídos={total} celdas={celdas} "
          f"suma_n={suma_n} duración={duracion}s")
    print(f"[grilla] top 5 de {prefijo}hotspots:")
    (hotspots.orderBy("ranking")
     .select("ranking", "n", "heridos", "muertos", F.col("centroide.coordinates").alias("lon_lat"))
     .show(5, truncate=False))
    spark.stop()


if __name__ == "__main__":
    main()
