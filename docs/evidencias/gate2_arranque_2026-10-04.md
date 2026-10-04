# Evidencia parcial del Gate 2 — arranque de infraestructura

Fecha: 4 de octubre de 2026

## Entorno

- Docker: 29.8.1, build 4a63305.
- Docker Compose: v5.5.1.
- `docker run --rm hello-world`: exitoso.
- `docker compose config --quiet`: exitoso.

## Construcción y arranque

- `docker compose up -d --build`: exitoso.
- BuildKit completó 61 de 61 pasos en 64,3 segundos.
- Se construyeron `bdgeo-dask`, `bdgeo-api`, `bdgeo-spark` y `bdgeo-mongo`.
- Se crearon la red `bdgeo-net` y los volúmenes `bdgeo_kaggle_data` y `bdgeo_mongo_data`.
- MongoDB, Spark master y Dask scheduler reportaron estado saludable durante el arranque.
- Spark worker, dos workers de Dask y la API quedaron iniciados.

## Comprobaciones desde el host

- `http://localhost:5000/health`: `{"mongo":"ok","status":"ok","version":"latest"}`.
- `http://localhost:8787/status`: HTTP 200.
- `http://localhost:8081`: HTTP 200.

## Integración Dask y MongoDB

`docker compose run --rm dask-job python check_cluster.py` terminó correctamente:

- dos workers conectados;
- cálculo distribuido con media 0,5001 (esperada aproximadamente 0,5);
- conexión a MongoDB correcta;
- 300 documentos en `eventos_semilla`;
- resultado final `OK`.

## Integración Spark y MongoDB

`spark-submit /opt/jobs/check_conexion.py` se conectó al clúster Spark 3.5.3, recibió un executor
de dos núcleos y leyó los 300 documentos esperados. La agregación produjo:

| Grupo | Conteo |
|---|---:|
| `A_times_square` | 120 |
| `B_brooklyn_bridge` | 80 |
| `C_queens` | 100 |

Después de la ejecución se verificó directamente en MongoDB que `spark_check` contiene los tres
documentos con esos mismos grupos y conteos. Esto confirma lectura y escritura mediante el
MongoDB Spark Connector.

## Pendiente para cerrar el Gate 2

- Jenkins se construyó correctamente en 242,7 segundos y el contenedor quedó iniciado en el
  puerto 8080. La interfaz respondió como Jenkins 2.541.3 y redirigió a la autenticación.
- Completar el asistente inicial de Jenkins y configurar sus credenciales.
- Configurar el webhook, demostrar el despliegue correcto y el bloqueo con `FORZAR_FALLO`.
