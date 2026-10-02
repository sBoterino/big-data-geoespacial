"""Utilidades compartidas por los jobs de Spark: sesión y URI de MongoDB desde el entorno."""
import os
from urllib.parse import quote_plus

from pyspark.sql import SparkSession


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
