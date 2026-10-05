"""Utilidades compartidas por los jobs de Spark: sesión, lectura y escritura en MongoDB."""
import json
import os
from urllib.parse import quote_plus

from pyspark.sql import Row, SparkSession


def mongo_uri():
    user = quote_plus(os.getenv("MONGO_ROOT_USER", ""))
    password = quote_plus(os.getenv("MONGO_ROOT_PASSWORD", ""))
    host = os.getenv("MONGO_HOST", "mongodb")
    port = os.getenv("MONGO_PORT", "27017")
    return f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"


def crear_sesion(nombre_app):
    uri = mongo_uri()
    return (
        SparkSession.builder.appName(nombre_app)
        .master(os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077"))
        .config("spark.mongodb.read.connection.uri", uri)
        .config("spark.mongodb.write.connection.uri", uri)
        .getOrCreate()
    )


DB = os.getenv("MONGO_DB", "geo")

# Proyección que se ejecuta DENTRO de MongoDB antes de enviar los datos a Spark.
# Solo viajan por la red los campos que usan las agregaciones (no calles, zip, fuente...),
# y los campos opcionales llegan con un valor por defecto. La semilla no tiene heridos,
# muertos ni borough, así que también sirve para ella.
PROYECCION_EVENTOS = {
    "$project": {
        "_id": 0,
        "lon": {"$arrayElemAt": ["$location.coordinates", 0]},
        "lat": {"$arrayElemAt": ["$location.coordinates", 1]},
        "hora": 1,
        "dia_semana": 1,
        "mes": 1,
        "heridos": {"$ifNull": ["$personas_heridas", 0]},
        "muertos": {"$ifNull": ["$personas_muertas", 0]},
        "borough": {"$ifNull": ["$borough", "DESCONOCIDO"]},
    }
}


def leer(spark, coleccion, pipeline=None):
    """Lee una colección con el MongoDB Spark Connector, opcionalmente filtrada en Mongo."""
    lector = (spark.read.format("mongodb")
              .option("database", DB).option("collection", coleccion))
    if pipeline:
        lector = lector.option("aggregation.pipeline", json.dumps(pipeline))
    return lector.load()


def leer_eventos(spark, coleccion):
    return leer(spark, coleccion, [PROYECCION_EVENTOS])


def escribir(df, coleccion):
    """Reemplaza la colección completa: cada ejecución deja resultados consistentes."""
    (df.write.format("mongodb").mode("overwrite")
     .option("database", DB).option("collection", coleccion).save())


def registrar_meta(spark, prefijo, documento):
    """Guarda (o reemplaza por _id) el registro de una ejecución en <prefijo>meta.

    Se usa replace+upsert en lugar de overwrite para que el job de grilla y el temporal
    conserven cada uno su propio registro en la misma colección.
    """
    (spark.createDataFrame([Row(**documento)]).write.format("mongodb").mode("append")
     .option("database", DB).option("collection", f"{prefijo}meta")
     .option("operationType", "replace").option("upsertDocument", "true").save())


def prefijo_por_defecto(coleccion):
    """eventos -> spark_ ; eventos_semilla -> spark_semilla_.

    Así la verificación sobre la semilla, que corre en cada build, nunca sobrescribe los
    resultados reales que consulta la API en /spark-results.
    """
    if coleccion == "eventos":
        return "spark_"
    return "spark_" + coleccion.replace("eventos_", "") + "_"
