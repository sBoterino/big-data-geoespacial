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

## Pendiente para cerrar el Gate 2

- Ejecutar `ingest/check_cluster.py` y comprobar dos workers de Dask.
- Ejecutar `spark/jobs/check_conexion.py` y comprobar lectura y escritura en MongoDB.
- Levantar Jenkins y configurar sus credenciales.
- Configurar el webhook, demostrar el despliegue correcto y el bloqueo con `FORZAR_FALLO`.

