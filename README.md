# Big Data Geoespacial — Procesamiento y consulta con despliegue continuo

Sistema distribuido y dockerizado:
**Kaggle → Dask (ingesta y limpieza) → MongoDB (GeoJSON + 2dsphere) → Spark (agregaciones) → Flask (API) → Jenkins (CI/CD)**

Equipo: Juan Guillermo Echeverri, Sebastián Botero Velásquez y Santiago Villamizar Mejía.

Repositorio: https://github.com/sBoterino/big-data-geoespacial

> Estado: **implementacion, pruebas, benchmark y reproducibilidad en un segundo computador completados**. El informe tecnico final esta disponible en [PDF](docs/informe_tecnico_big_data_geoespacial.pdf) y en [Word](docs/informe_tecnico_big_data_geoespacial.docx).
> Guía de la Fase 2 en [`docs/guia_fase2.md`](docs/guia_fase2.md) · reproducibilidad F9 en [`docs/guia_fase9_reproducibilidad.md`](docs/guia_fase9_reproducibilidad.md) · plan completo en [`docs/plan_paso_a_paso.md`](docs/plan_paso_a_paso.md) · preparación viva en [`docs/guia_sustentacion.md`](docs/guia_sustentacion.md).

## Dataset

**NYC Motor Vehicle Collisions – Crashes**
(`muzammilrizvi1/motor-vehicle-collisions-crashes`), perfilado y utilizado por el proyecto.

Verificación real del 1-oct-2026: 1.972.121 registros, 29 columnas y 420.704.526 bytes.
El perfilado encontró 226.028 coordenadas nulas, 4.115 puntos `(0,0)`, 106 coordenadas fuera
de rango y 1.741.872 registros geográficamente válidos. La evidencia está en
`docs/evidencias/verificacion_muzammilrizvi1__motor-vehicle-collisions-crashes.json`.

## Requisitos previos

- Docker Desktop con al menos 8 GB de RAM asignados (recomendado 10–12 GB).
- Git.
- Una cuenta de Kaggle con token de API.

## Levantar el sistema desde cero

```powershell
git clone https://github.com/sBoterino/big-data-geoespacial.git
Set-Location .\big-data-geoespacial
Copy-Item .env.example .env
notepad .env                       # cambiar contraseña Mongo y añadir el token de Kaggle
docker compose config --quiet
docker compose up -d --build       # MongoDB, Spark, Dask y API
docker compose ps
```

En Windows, los comandos completos desde un equipo limpio, la carga de datos, las pruebas y el
formato de evidencia están en la [guía F9](docs/guia_fase9_reproducibilidad.md).

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

Probar las reglas de limpieza dentro de la imagen de ingesta:

```bash
docker build --target test -t bdgeo-ingest-test:dev ingest
docker run --rm bdgeo-ingest-test:dev
```

Probar la API y las transformaciones puras de Spark:

```bash
docker build --target test -t bdgeo-api-test:dev api
docker run --rm bdgeo-api-test:dev
docker compose build spark-master
docker run --rm -e SPARK_LOCAL_IP=127.0.0.1 \
  --entrypoint /opt/spark/bin/spark-submit bdgeo-spark:latest \
  --master 'local[2]' /opt/tests/test_agregaciones.py
```

La etapa de staging de Jenkins usa los datos y resultados Spark de semilla, con conteos
conocidos, tanto en ramas como en `main`. Solo `bdgeo-main` puede desplegar en producción.

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

## Entregables

- Informe tecnico final: [`docs/informe_tecnico_big_data_geoespacial.pdf`](docs/informe_tecnico_big_data_geoespacial.pdf) (9 paginas).
- Version editable: [`docs/informe_tecnico_big_data_geoespacial.docx`](docs/informe_tecnico_big_data_geoespacial.docx).
- Diagrama de arquitectura: [`docs/informe_assets/arquitectura.png`](docs/informe_assets/arquitectura.png).
- Orquestacion: [`docker-compose.yml`](docker-compose.yml).
- Pipeline CI/CD: [`Jenkinsfile`](Jenkinsfile).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/near?lat=&lon=&radio=&limit=` | Registros dentro de un radio (`$near`) |
| POST | `/within?limit=` | Registros dentro de un polígono GeoJSON (`$geoWithin`) |
| GET | `/geonear?lat=&lon=&radio=&limit=&agrupar=` | Agregación geoespacial (`$geoNear`) |
| GET | `/spark-results` | Colecciones permitidas generadas por Spark |
| GET | `/spark-results/<nombre>` | Resultados calculados por Spark |

Todas las consultas aceptan parámetros, rechazan entradas inválidas con HTTP 400 y reportan
`tiempo_ms`. `/spark-results/<nombre>` acepta `grilla`, `hotspots`, `por_hora`,
`por_dia_semana`, `por_mes`, `hora_borough` y `meta`.

## Agregaciones con Spark (F6)

Tres jobs en `spark/jobs/`, que leen desde MongoDB con el MongoDB Spark Connector y una
proyección `$project` hecha en MongoDB (D14):

| Job | Resultado |
|---|---|
| `agregacion_grilla.py` | `spark_grilla` (celdas de 0,005° ≈ 500 m con n, heridos, muertos y polígono GeoJSON) y `spark_hotspots` (top 20) |
| `agregacion_temporal.py` | `spark_por_hora`, `spark_por_dia_semana`, `spark_por_mes`, `spark_hora_borough` |
| `verificar_resultados.py` | Sumas de control contra el total de documentos y cruce del hotspot #1 con `$geoWithin` (±0,5 %) |

```bash
docker compose exec spark-master spark-submit /opt/jobs/agregacion_grilla.py            # datos reales
docker compose exec spark-master spark-submit /opt/jobs/verificar_resultados.py
docker compose exec spark-master spark-submit /opt/jobs/agregacion_grilla.py --coleccion eventos_semilla
```

Jenkins corre los jobs y la verificación sobre la semilla en cada build (salida
`spark_semilla_*`, sin tocar lo que sirve la API) y, en `bdgeo-main`, recalcula sobre los datos
reales con `EJECUTAR_SPARK=true` o si aún no existen resultados. Gate 6 cerró con `bdgeo-main` #9.

## Benchmark Dask vs Spark (F8)

Misma operación en los dos motores (Parquet de la ingesta, celda de 0,005°, conteo y top 20),
con 1 y 2 workers y con 1× y 10× (Parquet físico) de volumen. Protocolo y scripts en
[`benchmark/README.md`](benchmark/README.md); resultados y análisis en
[`docs/evidencias/fase8_benchmark_2026-10-05.md`](docs/evidencias/fase8_benchmark_2026-10-05.md).

| Datos | Dask (1 / 2 workers) | Spark (1 / 2 workers) |
|---|---:|---:|
| ×1 (1.741.828 filas) | 0,30 / 0,20 s | 3,80 / 4,65 s |
| ×10 (17.418.280 filas) | 2,36 / 1,39 s | 4,51 / 5,12 s |

Dask fue más rápido en todas las combinaciones, pero su ventaja bajó de ×12,7 a ×1,9 al pasar a
10 veces más filas. Limitaciones: un solo computador, memoria medida como pico observado con
`docker stats` (~2 s por muestra) y filas repetidas en la prueba ×10.

## Flujo de trabajo en Git

- Por acuerdo del equipo, `main` solo se modifica mediante pull request con al menos una revisión.
  No hay un ruleset activo porque no es un requisito explícito de la rúbrica.
- Ramas por componente: `feature/ingesta-dask`, `feature/spark-agg`, `feature/api-flask`, etc.
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
