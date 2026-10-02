"""
Prueba de integración Spark <-> MongoDB (Gate 2/3).

Lee eventos_semilla con el MongoDB Spark Connector, cuenta por grupo con los workers del
clúster y escribe el resultado en la colección spark_check. Si esto funciona, el conector,
las credenciales y la red entre contenedores están bien.

Ejecutar:
  docker compose exec spark-master spark-submit /opt/jobs/check_conexion.py
"""
import sys

from pyspark.sql import functions as F

from comun import DB, crear_sesion

spark = crear_sesion("check-conexion-mongo")
spark.sparkContext.setLogLevel("WARN")

df = (spark.read.format("mongodb")
      .option("database", DB).option("collection", "eventos_semilla").load())

total = df.count()
por_grupo = df.groupBy("grupo").agg(F.count("*").alias("n")).orderBy("grupo")
por_grupo.show(truncate=False)

(por_grupo.withColumn("calculado_en", F.current_timestamp())
 .write.format("mongodb").mode("overwrite")
 .option("database", DB).option("collection", "spark_check").save())

esperado = 300
print(f"[check] documentos leídos: {total} (esperado {esperado})")
spark.stop()
sys.exit(0 if total == esperado else 1)
