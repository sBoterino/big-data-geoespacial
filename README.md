# Big Data Geoespacial — Procesamiento y consulta con despliegue continuo

Sistema distribuido y dockerizado:
**Kaggle → Dask (ingesta y limpieza) → MongoDB (GeoJSON + 2dsphere) → Spark (agregaciones) → Flask (API) → Jenkins (CI/CD)**

Equipo: Juan Guillermo Echeverri, Sebastián Botero Velásquez y Santiago Villamizar Mejía.

Repositorio: https://github.com/sBoterino/big-data-geoespacial

> Estado: **Fase 2 — esqueleto de infraestructura y CI/CD** (pendiente de validar el Gate 2).
> Guía de la Fase 2 en [`docs/guia_fase2.md`](docs/guia_fase2.md) · plan completo en [`docs/plan_paso_a_paso.md`](docs/plan_paso_a_paso.md).

## Dataset

**NYC Motor Vehicle Collisions – Crashes**
(`muzammilrizvi1/motor-vehicle-collisions-crashes`), pendiente de registro con el docente.

Verificación real del 1-oct-2026: 1.972.121 registros, 29 columnas y 420.704.526 bytes.
El perfilado encontró 226.028 coordenadas nulas, 4.115 puntos `(0,0)`, 106 coordenadas fuera
de rango y 1.741.872 registros geográficamente válidos. La evidencia está en
`docs/evidencias/verificacion_muzammilrizvi1__motor-vehicle-collisions-crashes.json`.

## Requisitos previos

- Docker Desktop con al menos 8 GB de RAM asignados (recomendado 10–12 GB).
- Git.
- Una cuenta de Kaggle con token de API.

## Levantar el sistema desde cero

```bash
git clone <url-del-repo>
cd <repo>
cp .env.example .env              # completar MONGO_ROOT_PASSWORD y las credenciales de Kaggle
docker compose up -d --build      # MongoDB, Spark (master + worker), Dask (scheduler + 2 workers), API
```

| Servicio | URL |
|---|---|
| API | http://localhost:5000/health |
| Spark master UI | http://localhost:8081 |
| Dashboard Dask | http://localhost:8787 |
| MongoDB | `mongodb://admin:<password>@localhost:27017/?authSource=admin` |
| Jenkins (perfil `ci`) | http://localhost:8080 |

Verificar la comunicación entre contenedores:

```bash
docker compose run --rm dask-job python check_cluster.py
docker compose exec spark-master /opt/spark/bin/spark-submit /opt/jobs/check_conexion.py
```

Probar el perfilador con datos sintéticos (requiere `pandas`, pero no Kaggle ni credenciales):

```bash
python -m unittest discover -s tests -v
```

CI/CD (solo en el computador que corre Jenkins):

```bash
docker compose --profile ci up -d --build     # Jenkins + reenviador de webhook (smee)
```

## Estructura

```text
api/          API Flask y sus pruebas (api/tests)
ingest/       Descarga desde Kaggle, limpieza y carga con Dask
spark/        Jobs de Spark e imagen con MongoDB Spark Connector
mongo/        Imagen de MongoDB, validador GeoJSON, índices 2dsphere y datos semilla
jenkins/      Imagen de Jenkins con Docker CLI
benchmark/    Comparación Dask vs Spark
scripts/      Verificación del dataset, generador de semilla, smoke tests de la API
docs/         Decisiones, evidencias e informe
```

## Endpoints *(solo `/health` implementado; el resto en la Fase 5)*

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/near?lat=&lon=&radio=` | Registros dentro de un radio (`$near`) |
| POST | `/within` | Registros dentro de un polígono GeoJSON (`$geoWithin`) |
| GET | `/spark-results/<coleccion>` | Resultados calculados por Spark |

## Flujo de trabajo en Git

- `main` está protegida: solo se modifica mediante pull request con al menos una revisión.
- Ramas por componente: `feature/ingest-dask`, `feature/spark-agg`, `feature/api-flask`, etc.
- Cada merge a `main` dispara el webhook → Jenkins → build, pruebas y despliegue.
- Si una prueba falla, no hay despliegue.

## Seguridad de credenciales

- El token de Kaggle vive como credencial en Jenkins y en un `.env` local ignorado por Git.
- `.env`, `kaggle.json` y los datos descargados están en `.gitignore`.
- Nunca se hace commit de valores reales. Si ocurre, se rota el token de inmediato.

## Referencias y código de terceros

Todo fragmento tomado de documentación, tutoriales o repositorios públicos se cita aquí con su
enlace, según las condiciones del curso.

- Instalación de Docker CLI en Debian: https://docs.docker.com/engine/install/debian/
- MongoDB Spark Connector: https://www.mongodb.com/docs/spark-connector/current/
- smee-client: https://github.com/probot/smee-client
- *(agregar a medida que se usen)*
