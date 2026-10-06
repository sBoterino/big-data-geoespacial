"""
F6 — Verificación de los resultados de Spark ("resultados coherentes y verificables").

Comprobaciones:
  1. La suma de n en <prefijo>grilla es igual al número de documentos de la colección origen.
  2. La suma de n en <prefijo>por_hora, por_dia_semana y por_mes da ese mismo total.
  3. Validación cruzada con MongoDB: el polígono del hotspot #1 se consulta con $geoWithin
     (índice 2dsphere) y el conteo debe coincidir con el n calculado por Spark, con una
     tolerancia de ±0,5 % por la diferencia entre bordes geodésicos y planos (mínimo 1).
  4. Solo con la semilla: el total es 300 y el hotspot #1 está a menos de 1 km de
     Times Square (grupo A de scripts/generar_semilla.py).

Sale con código 1 si algo no cuadra, para que Jenkins detenga el pipeline.

Ejecutar:
  docker compose exec spark-master spark-submit /opt/jobs/verificar_resultados.py
  docker compose exec spark-master spark-submit /opt/jobs/verificar_resultados.py --coleccion eventos_semilla
"""
import argparse
import math
import sys

from pyspark.sql import functions as F

from comun import crear_sesion, leer, prefijo_por_defecto

TIMES_SQUARE = (40.7580, -73.9855)  # (lat, lon), igual que en generar_semilla.py
TOTAL_SEMILLA = 300


def distancia_m(a, b):
    """Haversine en metros entre dos tuplas (lat, lon)."""
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def suma_n(spark, coleccion, pipeline=None):
    """Suma la columna n. Con un pipeline $count, el conector lo ejecuta una vez por
    partición de lectura, así que se suman los conteos parciales."""
    df = leer(spark, coleccion, pipeline)
    if "n" not in df.columns:  # resultado vacío: el conector no puede inferir la columna
        return 0
    return int(df.agg(F.sum("n")).first()[0] or 0)


def main():
    p = argparse.ArgumentParser(description="Verifica los resultados de F6")
    p.add_argument("--coleccion", default="eventos")
    p.add_argument("--prefijo", default=None)
    p.add_argument("--tolerancia", type=float, default=0.005, help="0.005 = ±0,5 %%")
    args = p.parse_args()
    prefijo = args.prefijo or prefijo_por_defecto(args.coleccion)

    spark = crear_sesion(f"f6-verificar-{args.coleccion}")
    spark.sparkContext.setLogLevel("WARN")
    fallas = []

    def comprobar(condicion, mensaje):
        print(f"[verificar] {'OK   ' if condicion else 'FALLA'} {mensaje}")
        if not condicion:
            fallas.append(mensaje)

    # El conteo de origen se hace en MongoDB y solo vuelve un número.
    total = suma_n(spark, args.coleccion, [{"$count": "n"}])
    print(f"[verificar] documentos en {args.coleccion}: {total}")

    # 1 y 2: sumas de control
    for salida in ("grilla", "por_hora", "por_dia_semana", "por_mes"):
        s = suma_n(spark, f"{prefijo}{salida}")
        comprobar(s == total, f"suma de n en {prefijo}{salida} = {s} (esperado {total})")

    # 3: validación cruzada del hotspot #1 contra MongoDB
    top = leer(spark, f"{prefijo}hotspots", [{"$match": {"ranking": 1}}]).first()
    if top is None:
        comprobar(False, f"{prefijo}hotspots tiene el ranking 1")
    else:
        poligono = {"type": "Polygon",
                    "coordinates": [[list(map(float, v)) for v in top["celda"]["coordinates"][0]]]}
        conteo_geo = suma_n(spark, args.coleccion, [
            {"$match": {"location": {"$geoWithin": {"$geometry": poligono}}}},
            {"$count": "n"},
        ])
        margen = max(1, math.ceil(top["n"] * args.tolerancia))
        comprobar(abs(conteo_geo - top["n"]) <= margen,
                  f"hotspot #1 ({top['_id']}): Spark n={top['n']}, "
                  f"MongoDB $geoWithin={conteo_geo} (margen ±{margen})")

        # 4: expectativas conocidas de la semilla
        if args.coleccion == "eventos_semilla":
            comprobar(total == TOTAL_SEMILLA, f"la semilla tiene {TOTAL_SEMILLA} documentos")
            lon, lat = top["centroide"]["coordinates"]
            d = distancia_m((lat, lon), TIMES_SQUARE)
            comprobar(d < 1000, f"hotspot #1 a {d:.0f} m de Times Square (< 1000 m)")

    spark.stop()
    if fallas:
        print(f"[verificar] RESULTADO: {len(fallas)} comprobación(es) fallaron")
        sys.exit(1)
    print("[verificar] RESULTADO: OK")


if __name__ == "__main__":
    main()
