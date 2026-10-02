# syntax=docker/dockerfile:1
# Imagen OFICIAL de Apache Spark (no Bitnami: sus imágenes gratuitas se retiraron en 2025).
# Versiones fijadas: Spark 3.5 usa Scala 2.12, así que el conector debe ser _2.12.
ARG SPARK_IMAGE=apache/spark:3.5.3-scala2.12-java17-python3-ubuntu
FROM ${SPARK_IMAGE}

# MongoDB Spark Connector y sus dependencias del driver Java, descargados UNA vez en el build
# (no con --packages en cada ejecución, que requiere internet y hace lento cada job).
# Si cambian la versión del conector, revisar en Maven Central qué versión del driver pide.
ARG CONNECTOR_VERSION=10.4.0
ARG DRIVER_VERSION=5.1.4
ARG MAVEN=https://repo1.maven.org/maven2
ADD --chmod=644 ${MAVEN}/org/mongodb/spark/mongo-spark-connector_2.12/${CONNECTOR_VERSION}/mongo-spark-connector_2.12-${CONNECTOR_VERSION}.jar /opt/spark/jars/
ADD --chmod=644 ${MAVEN}/org/mongodb/mongodb-driver-sync/${DRIVER_VERSION}/mongodb-driver-sync-${DRIVER_VERSION}.jar /opt/spark/jars/
ADD --chmod=644 ${MAVEN}/org/mongodb/mongodb-driver-core/${DRIVER_VERSION}/mongodb-driver-core-${DRIVER_VERSION}.jar /opt/spark/jars/
ADD --chmod=644 ${MAVEN}/org/mongodb/bson/${DRIVER_VERSION}/bson-${DRIVER_VERSION}.jar /opt/spark/jars/
ADD --chmod=644 ${MAVEN}/org/mongodb/bson-record-codec/${DRIVER_VERSION}/bson-record-codec-${DRIVER_VERSION}.jar /opt/spark/jars/

COPY --chmod=755 jobs /opt/jobs
ENV PATH="/opt/spark/bin:${PATH}"
WORKDIR /opt/jobs
