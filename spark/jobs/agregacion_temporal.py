"""
F6 — Agregaciones temporales con Spark.

Usa los campos hora (0–23), dia_semana (1 = lunes … 7 = domingo) y mes (1–12) que la ingesta
calculó a partir de la fecha original, de modo que Spark no reinterpreta zonas horarias.

Salidas (con prefijo "spark_" para la colección real):
  <prefijo>por_hora        n, heridos y muertos por hora del día
  <prefijo>por_dia_semana  n, heridos y muertos por día de la semana
  <prefijo>por_mes         n, heridos y muertos por mes
  <prefijo>hora_borough    n, heridos y muertos por hora y borough
  <prefijo>meta            registro de la ejecución (_id = "temporal")

Ejecutar:
  docker compose exec spark-master spark-submit /opt/jobs/agregacion_temporal.py
  docker compose exec spark-master spark-submit /opt/jobs/agregacion_temporal.py --coleccion eventos_semilla
"""
import argparse
import time
from datetime import datetime, timezone

from pyspark.sql import functions as F

from comun import crear_sesion, escribir, leer_eventos, prefijo_por_defecto, registrar_meta

# nombre de la salida -> columnas de agrupación
AGRUPACIONES = {
    "por_hora": ["hora"],
    "por_dia_semana": ["dia_semana"],
    "por_mes": ["mes"],
    "hora_borough": ["hora", "borough"],
}


def argumentos():
    p = argparse.ArgumentParser(description="Agregaciones por hora, día de la semana y mes")
    p.add_argument("--coleccion", default="eventos", help="colección de origen en MongoDB")
    p.add_argument("--prefijo", default=None, help="prefijo de las colecciones de salida")
    return p.parse_args()


def agregar(df, columnas):
    """Cuenta eventos y suma heridos/muertos por las columnas dadas (sin E/S)."""
    return (df.groupBy(*columnas)
            .agg(F.count("*").alias("n"),
                 F.sum("heridos").cast("long").alias("heridos"),
                 F.sum("muertos").cast("long").alias("muertos"))
            # _id legible y estable, p. ej. "17" o "17_BROOKLYN"
            .withColumn("_id", F.concat_ws("_", *[F.col(c).cast("string") for c in columnas]))
            .orderBy(*columnas))


def main():
    args = argumentos()
    prefijo = args.prefijo or prefijo_por_defecto(args.coleccion)
    spark = crear_sesion(f"f6-temporal-{args.coleccion}")
    spark.sparkContext.setLogLevel("WARN")
    inicio = time.perf_counter()

    # cache(): las cuatro agregaciones reutilizan la misma lectura en lugar de ir 4 veces a Mongo.
    eventos = leer_eventos(spark, args.coleccion).cache()
    total = eventos.count()

    sumas = {}
    for nombre, columnas in AGRUPACIONES.items():
        resultado = agregar(eventos, columnas).cache()
        escribir(resultado, f"{prefijo}{nombre}")
        sumas[nombre] = int(resultado.agg(F.sum("n")).first()[0] or 0)
        print(f"[temporal] {prefijo}{nombre}: {resultado.count()} filas, suma_n={sumas[nombre]}")

    duracion = round(time.perf_counter() - inicio, 3)
    registrar_meta(spark, prefijo, {
        "_id": "temporal",
        "coleccion_origen": args.coleccion,
        "total_leido": total,
        "suma_n": sumas["por_hora"],
        "duracion_s": duracion,
        "calculado_en": datetime.now(timezone.utc).isoformat(),
    })

    print(f"[temporal] origen={args.coleccion} leídos={total} duración={duracion}s")
    print("[temporal] eventos por hora:")
    agregar(eventos, ["hora"]).select("hora", "n", "heridos", "muertos").show(24, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
