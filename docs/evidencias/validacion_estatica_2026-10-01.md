# Evidencia de validación estática — 1-oct-2026

Esta validación se ejecutó antes del Gate 2 para detectar errores sin depender de Docker. No
demuestra comunicación entre contenedores ni reemplaza las pruebas de integración del Gate 2.

## Perfilador del dataset

Comando:

```powershell
python -m unittest discover -s tests
```

Resultado: **5 pruebas aprobadas**. Incluye detección de columnas, clasificación exclusiva de
coordenadas, ausencia de lat/lon, CSV por bloques y lectura/cierre de SQLite.

## API Flask

Comando normal:

```powershell
cd api
python -m pytest -q
```

Resultado: **4 aprobadas y 1 omitida**. La omitida es la prueba trampa.

Comando de demostración del bloqueo:

```powershell
$env:FORZAR_FALLO='true'
python -m pytest -q
```

Resultado esperado y observado: **1 fallida y 4 aprobadas**, con código de salida 1. La prueba
falla con el mensaje `Fallo intencional: el despliegue NO debe ejecutarse`.

## Sintaxis y Compose

- `python -m compileall -q api ingest scripts spark tests`: sin errores.
- `docker-compose.yml`: parseado correctamente como YAML.
- Servicios definidos: **11** (`mongodb`, `spark-master`, `spark-worker`, `spark-worker-2`,
  `dask-scheduler`, `dask-worker-1`, `dask-worker-2`, `dask-job`, `api`, `jenkins`, `smee`).

## Pendiente

Ejecutar desde una terminal con Docker:

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Después deben ejecutarse las pruebas reales de comunicación Dask → MongoDB, Spark ↔ MongoDB y
los smoke tests contra la API de staging y producción.
