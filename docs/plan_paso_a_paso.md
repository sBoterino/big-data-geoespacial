# Plan paso a paso — del 30 de septiembre al 9 de octubre

Este documento es para seguirlo en orden, sin tener que decidir nada. Cada día indica quién
hace qué, los comandos exactos, el criterio de "terminado" y la evidencia que hay que guardar.
Las especificaciones de las fases F4 a F8 están escritas para que se le puedan entregar
tal cual a Claude y genere el código.

---

## 0. Cómo leer este plan

**Roles.** El trabajo se divide en cuatro roles. Si el equipo es más pequeño, una persona toma
varios roles según esta tabla:

| Rol | Qué le toca | 4 personas | 3 personas | 2 personas |
|---|---|---|---|---|
| **INFRA** | Compose, Jenkins, webhook, pipeline, reproducibilidad | A | A | A |
| **DATOS** | Kaggle, ingesta y limpieza con Dask | B | B | B |
| **SPARK** | Agregaciones Spark y benchmark | C | C | B (desde el domingo) |
| **API** | MongoDB, consultas, Flask, pruebas | D | A (desde el sábado) | A (desde el sábado) |

Anotar los nombres en la sección 10 de `CONTEXT.md`.

**Símbolos.**
- ⏱️ tiempo estimado.
- ✅ criterio de terminado: no se sigue sin cumplirlo.
- 📸 evidencia que se guarda en `docs/evidencias/` para el informe.
- 🤖 paso en el que se le pide el código a Claude.

**Ritual diario** (5 minutos al final de cada día, lo hace una sola persona):
1. `git checkout main && git pull`.
2. Actualizar la sección 8 (estado) y la 14 (próxima acción) de `CONTEXT.md`.
3. Commit con el mensaje `docs: estado <fecha>` mediante un PR corto.

**Flujo de Git para cualquier cambio** (siempre igual; el docente revisa el historial):

```bash
git checkout main && git pull
git checkout -b feature/<nombre-corto>        # ej: feature/ingesta-dask
# ... trabajar ...
git add .
git commit -m "feat(ingesta): lectura particionada y reglas de limpieza"
git push -u origin feature/<nombre-corto>
```

Luego, en GitHub:
1. **Compare & pull request.**
2. Asignar como revisor a **otra persona**.
3. El revisor lee el código, pregunta lo que no entienda y aprueba.
4. **Merge.** Jenkins arranca solo.
5. Verificar que el build quedó en verde.

Si el build queda en rojo, **el autor del PR lo arregla antes de cualquier otra cosa**.

**Cómo pedirle código a Claude (🤖).** Abrir una conversación nueva, adjuntar `CONTEXT.md`,
este archivo y los archivos que indique el paso, y escribir:

> Estamos en la fase FX del plan. Genera los archivos de la especificación "FX" de
> `docs/plan_paso_a_paso.md`, respetando CONTEXT.md. [Adjunto también: …]

Después, **el dueño del rol lee y entiende cada archivo antes de hacer commit**. En la
sustentación cada integrante debe poder explicar cualquier parte.

---

## DÍA 1 — Miércoles 30 de septiembre · F0 + F1 · ⏱️ 1,5–2 h

**Objetivo:** dataset verificado y registrado; repositorio creado y funcionando para todos.

### Paso 1.1 — Verificar el dataset [DATOS] ⏱️ 30 min
1. Instalar las herramientas en el computador: `pip install kaggle pandas`.
2. En Kaggle, ir a **Settings → API → Create New Token**. Se descarga `kaggle.json`.
   Guardarlo en `~/.kaggle/kaggle.json` (en Windows, `C:\Users\<usuario>\.kaggle\kaggle.json`).
   **Nunca dentro del repositorio.**
3. Descomprimir el zip del proyecto en una carpeta y abrir una terminal dentro de ella.
4. Primero listar, que es rápido:
   `python scripts/verificar_dataset.py muzammilrizvi1/motor-vehicle-collisions-crashes --solo-listar`
5. Si lista archivos, correr la verificación completa (descarga y perfila):
   `python scripts/verificar_dataset.py muzammilrizvi1/motor-vehicle-collisions-crashes`
6. Revisar el resultado:
   - `registros_totales` debe ser ≥ 1.000.000.
   - Deben aparecer `col_lat`, `col_lon` y al menos una columna de fecha.
   - Anotar `coord_nulas`, `coord_no_numericas`, `coord_cero` y `fuera_de_rango`.
7. Si el slug no existe o no cumple, repetir con el respaldo `rtatman/188-million-us-wildfires`.

✅ Existe `docs/evidencias/verificacion_<slug>.json` y dice `"cumple_tamano": true`.
📸 Ese mismo JSON.

**Ejecutado el 1-oct-2026:** 1.972.121 registros, 29 columnas, 226.028 coordenadas nulas,
0 no numéricas, 4.115 en `(0,0)`, 106 fuera de rango y 1.741.872 válidas. Evidencia guardada.

### Paso 1.2 — Registrar el dataset [cualquiera] ⏱️ 5 min
1. Enviar al docente el correo que ya está redactado, con los nombres del equipo.
2. **No esperar la respuesta para seguir.** Si el docente rechaza el dataset, solo cambian
   la Fase 4 y las reglas de limpieza; todo lo demás sirve igual.

### Paso 1.3 — Crear el repositorio [INFRA] ⏱️ 20 min
1. En GitHub, crear el repositorio `big-data-geoespacial`. Público, o privado si tienen GitHub
   Pro (el Student Pack lo da gratis). **Sin** README ni .gitignore, porque ya vienen en el zip.
2. Configurar Git en el computador. En Windows, primero:
   `git config --global core.autocrlf false`
3. Subir el contenido del zip:

```bash
cd <carpeta-descomprimida>
git init -b main
git add .
git status              # REVISAR: no debe aparecer .env, kaggle.json ni ningún .csv
git commit -m "chore: base del proyecto (fases 1 y 2)"
git remote add origin https://github.com/<usuario>/big-data-geoespacial.git
git push -u origin main
```

4. En **Settings → Collaborators**, invitar a los demás integrantes.

✅ El repositorio está en GitHub con todos los archivos. `git status` en limpio no muestra secretos.

### Paso 1.4 — Todos clonan [TODOS] ⏱️ 15 min
Cada integrante, en su propio computador:

```bash
git clone https://github.com/<usuario>/big-data-geoespacial.git
cd big-data-geoespacial
cp .env.example .env          # en Windows (PowerShell): copy .env.example .env
```

Editar `.env`:
- Poner una contraseña en `MONGO_ROOT_PASSWORD`. **La del computador de Jenkins se anota**,
  porque después va en la credencial.
- Poner las credenciales de Kaggle.

✅ Todos tienen el repo clonado y un `.env` que **no** aparece en `git status`.

### Paso 1.5 — Repartir roles [TODOS] ⏱️ 10 min
1. Completar la sección 10 de `CONTEXT.md` con nombres y revisores.
2. Hacer el primer PR del proyecto, así ya practican el flujo:
   `git checkout -b docs/roles` → editar `CONTEXT.md` → commit → push → PR → aprobar → merge.

✅ **Gate 0 + Gate 1:** dataset verificado y enviado al docente; repo con los integrantes y
roles asignados.

---

## DÍA 2 — Jueves 1 de octubre · F2 parte 1 · ⏱️ 3–4 h

**Objetivo:** todo el sistema corriendo en local y el primer build de Jenkins en verde.

### Paso 2.1 — Levantar el sistema [INFRA, en el computador que tendrá Jenkins] ⏱️ 1–1,5 h
Seguir `docs/guia_fase2.md` **Paso 0 y Paso 1** al pie de la letra.

Si el computador tiene 8 GB de RAM o menos, antes de levantar poner en `.env`:
`SPARK_WORKER_CONTAINER_MEM=1536m`, `DASK_WORKER_CONTAINER_MEM=1536m` y `JENKINS_MEM=1536m`.

✅ Todo lo del Paso 1 de la guía está marcado.
📸 Captura de la UI de Spark con 1 worker, captura del dashboard de Dask con 2 workers y la
salida de los dos checks guardada en `docs/evidencias/checks_integracion.txt`.

### Paso 2.2 — Mientras tanto, los demás levantan también en sus computadores [DATOS, SPARK, API] ⏱️ 1 h

```bash
docker compose up -d --build
docker compose ps
docker compose run --rm dask-job python check_cluster.py
```

Así se detectan problemas de cada computador ahora, y no el día de la ingesta.
Si algo falla, anotar el error exacto y el sistema operativo.

✅ Cada integrante tiene al menos MongoDB y la API corriendo (`http://localhost:5000/health`).

### Paso 2.3 — Familiarizarse con los datos semilla [API, SPARK] ⏱️ 30 min
Conectarse a MongoDB. Con MongoDB Compass (gratis), la cadena es
`mongodb://admin:<password>@localhost:27017/?authSource=admin`. También sirve desde la terminal:

```bash
docker compose exec mongodb mongosh -u admin -p <password> --authenticationDatabase admin geo
```

Dentro de mongosh, probar a mano las tres consultas obligatorias. **Esto es práctica para la sustentación:**

```javascript
// $near: 120 esperados a menos de 1 km de Times Square
db.eventos_semilla.find({ location: { $near: { $geometry: { type: "Point", coordinates: [-73.9855, 40.7580] }, $maxDistance: 1000 } } }).toArray().length

// $geoWithin: 120 esperados dentro del polígono de Midtown
db.eventos_semilla.countDocuments({ location: { $geoWithin: { $geometry: { type: "Polygon", coordinates: [[[-73.996,40.75],[-73.975,40.75],[-73.975,40.766],[-73.996,40.766],[-73.996,40.75]]] } } } })

// $geoNear: distancia de cada punto y conteo por grupo
db.eventos_semilla.aggregate([
  { $geoNear: { near: { type: "Point", coordinates: [-73.9855, 40.7580] }, distanceField: "distancia_m", maxDistance: 1000, spherical: true } },
  { $group: { _id: "$grupo", n: { $sum: 1 }, distancia_media: { $avg: "$distancia_m" } } }
])

// Ver que el validador funciona: esto DEBE fallar (latitud 200 fuera de rango)
db.eventos_semilla.insertOne({ location: { type: "Point", coordinates: [-73.9, 200] } })
```

> `countDocuments` no admite `$near`. Por eso la primera consulta cuenta con `.toArray().length`.

✅ Los conteos coinciden con `mongo/init/semilla_esperados.json` y el insert inválido es rechazado.
📸 Captura del insert rechazado, que es evidencia de "GeoJSON válido".

### Paso 2.4 — Jenkins y primer build [INFRA] ⏱️ 1–1,5 h
Seguir `docs/guia_fase2.md` **Pasos 2, 3 y 4**.

✅ El primer build (lanzado a mano) termina en verde con las 8 etapas, y `/health` muestra el
número de build.
📸 Captura de la vista de etapas del primer build verde.

**Si algo falla:** buscar primero en la tabla de problemas de la guía. Si no está, abrir una
conversación con Claude y adjuntar:
- `CONTEXT.md`;
- el error exacto (el log de la etapa que falló, desde el inicio de esa etapa);
- la salida de `docker compose ps`;
- la salida de `docker compose logs --tail 50 <servicio-que-falla>`.

---

## DÍA 3 — Viernes 2 de octubre · F2 parte 2 + cierre de F3 · ⏱️ 3 h

**Objetivo:** Gate 2 aprobado, con el webhook funcionando y el bloqueo de deploy demostrado.

### Paso 3.1 — Webhook, flujo por PR y prueba completa [INFRA] ⏱️ 1,5 h
Seguir `docs/guia_fase2.md` **Pasos 5, 6, 7 y 8**.

✅ Checklist completo del **Gate 2** de la guía.
📸 Tres capturas:
- el build disparado por el webhook, que en la página del build dice "Started by GitHub push";
- el build en rojo con `FORZAR_FALLO` y la etapa de despliegue sin ejecutar;
- `/health` mostrando que siguió la versión anterior.

### Paso 3.2 — Cada integrante hace un PR que pase por Jenkins [DATOS, SPARK, API] ⏱️ 20 min c/u
Un cambio pequeño y real en su área. Por ejemplo, un comentario en su carpeta o su nombre en el
README. Flujo completo: rama → PR → revisión → merge → Jenkins verde.

✅ Cada integrante vio **su propio** merge disparar Jenkins. Es práctica directa para la sustentación.

### Paso 3.3 — Cierre de F3: modelo de documento definitivo [API + DATOS juntos] ⏱️ 45 min
Con el JSON de verificación del Día 1 en la mano, decidir y escribir en `docs/decisiones.md`
(como D13) el modelo de documento final de `eventos`.

Campos propuestos para NYC Collisions. **Confirmar los nombres reales de las columnas en el JSON:**

| Campo en Mongo | Origen | Tipo |
|---|---|---|
| `_id` | COLLISION_ID | int |
| `location` | LONGITUDE, LATITUDE | GeoJSON Point `[lon, lat]` |
| `fecha` | CRASH DATE + CRASH TIME | date |
| `hora`, `dia_semana`, `mes`, `anio` | derivados de `fecha` | int |
| `borough` | BOROUGH (nulo → "DESCONOCIDO") | string |
| `heridos`, `muertos` | NUMBER OF PERSONS INJURED / KILLED | int (nulo → 0) |
| `factor` | CONTRIBUTING FACTOR VEHICLE 1 | string |
| `vehiculo` | VEHICLE TYPE CODE 1 | string |

✅ D13 escrita y aprobada por PR. **Gate 3:** `eventos_semilla` con 2dsphere, validador y
consultas manuales correctas (Paso 2.3), más el modelo definido.

---

## DÍAS 4 y 5 — Sábado 3 y domingo 4 de octubre · F4, F5 y F6 en paralelo · ⏱️ 5–7 h por rol

Cada rol trabaja en su propia rama. **Nadie integra a `main` sin haber cumplido su ✅.**

---

### F4 — Ingesta con Dask [DATOS]

#### Especificación (para 🤖)

**Archivos a crear:**
- `ingest/descarga.py`
- `ingest/limpieza.py`
- `ingest/pipeline_ingesta.py`
- `ingest/tests/test_limpieza.py`
- La etapa "Ingesta (idempotente)" en el `Jenkinsfile`
- `scripts/reporte_limpieza.py` (opcional)

**1. `descarga.py`**
- Descarga `KAGGLE_DATASET` con la API de Kaggle a `/data/raw/<slug>/`, descomprimido.
- **Idempotente:** si existe `/data/raw/<slug>/.descarga_ok` (con nombre y tamaño de cada
  archivo), no vuelve a descargar.
- Los errores de credenciales se muestran con un mensaje claro y sin imprimir el token.

**2. `limpieza.py`**
Funciones puras sobre un `pandas.DataFrame`, para poder aplicarlas con `map_partitions` y
probarlas sin clúster. Las reglas se aplican **en orden** y cada una cuenta cuántos registros
elimina:

| # | Regla | Justificación para el informe |
|---|---|---|
| R1 | Coordenadas nulas o no numéricas | No se pueden representar como punto |
| R2 | Coordenadas exactamente (0, 0) | Valor centinela de "sin ubicación" que usa la fuente |
| R3 | Latitud fuera de [-90, 90] o longitud fuera de [-180, 180] | Inválidas en WGS84 y rechazadas por 2dsphere |
| R4 | Fuera del bounding box de NYC: lat [40.49, 40.92], lon [-74.27, -73.68] | Valores válidos en rango pero imposibles para el dataset (errores de digitación) |
| R5 | Fecha u hora no parseables | Sin ellas no hay agregación temporal |
| R6 | COLLISION_ID duplicado | Evita doble conteo |

También:
- `a_documento(fila)` construye el documento según el modelo D13, con `location` en `[lon, lat]`.
- `reporte` es un diccionario `{regla: eliminados}` más el total inicial y el total final.

**3. `pipeline_ingesta.py`** (se ejecuta con `docker compose run --rm dask-job python pipeline_ingesta.py`)
1. **Idempotencia.** Si la colección `ingesta_meta` tiene un registro del mismo dataset con
   estado `completa`, y `eventos` tiene ese número de documentos, y `FORCE_RELOAD` no es
   `true`: imprimir "Ingesta omitida" y salir con código 0.
2. Conectarse al scheduler de Dask y esperar 2 workers.
3. `dd.read_csv(..., blocksize="64MB", dtype=str, usecols=[...])` para una lectura
   **particionada**. Imprimir el número de particiones.
4. Si `INGEST_MAX_ROWS > 0`, limitar a esa muestra (mínimo 1.000.000).
5. Aplicar la limpieza con `map_partitions`, acumular el reporte y aplicar R6 con
   `drop_duplicates`.
6. Antes de cargar, eliminar el índice `location_2dsphere` de `eventos` si existe (la carga es
   más rápida sin él).
7. Cargar **por lotes** desde los workers: `map_partitions` con una función que hace
   `insert_many(lote, ordered=False)` en lotes de `INGEST_BATCH_SIZE`.
8. Recrear el índice 2dsphere y el de `fecha`.
9. Exportar Parquet a `/data/parquet/eventos/` con las columnas lat, lon, fecha, hora,
   dia_semana, mes y borough. Es la fuente común del benchmark (D5).
10. Guardar en `ingesta_meta` el dataset, la fecha, los totales, el reporte de limpieza y la
    duración. Escribir el reporte en `/data/reporte_limpieza.json` e imprimirlo.

**4. Tests** (`ingest/tests/test_limpieza.py`)
Un DataFrame pequeño con exactamente un caso de cada regla más filas válidas. Se verifica:
- el conteo por regla;
- que el documento tiene `[lon, lat]` en ese orden;
- que las fechas se parsean.

**5. Jenkinsfile**
- Agregar el parámetro `FORCE_RELOAD` (boolean, `false`).
- Agregar una etapa de build de la imagen de tests de ingesta y su pytest, junto al de la API.
- Agregar la etapa "Ingesta (idempotente)" después de "Levantar servicios":

```
withCredentials(kaggle-credentials) →
  . jenkins/ci-env.sh && FORCE_RELOAD=${FORCE_RELOAD} docker compose run --rm dask-job python pipeline_ingesta.py
```

#### Pasos [DATOS]
1. `git checkout -b feature/ingesta-dask`.
2. 🤖 Pedir el código con la especificación. Adjuntar `CONTEXT.md`, este plan, el JSON de
   verificación, `ingest/Dockerfile`, `ingest/requirements.txt`, `docker-compose.yml` y el `Jenkinsfile`.
3. Leer y entender cada archivo. Preguntarle a Claude todo lo que no quede claro.
4. Probar primero con una muestra, para que sea rápido:
   `INGEST_MAX_ROWS=50000` en `.env`, luego `docker compose run --rm dask-job python pipeline_ingesta.py`.
5. Mientras corre, abrir http://localhost:8787 y ver las tareas repartidas entre los 2 workers.
   📸 Captura del dashboard durante la carga.
6. Verificar en mongosh:
   `db.eventos.countDocuments()`, `db.eventos.getIndexes()` y
   `db.eventos.findOne()`, donde `coordinates[0]` debe estar cerca de -73.9.
7. Correr el mismo comando otra vez. Debe decir "Ingesta omitida" en segundos.
8. Carga completa: `INGEST_MAX_ROWS=0` y `FORCE_RELOAD=true` en `.env`, ejecutar, y después
   devolver `FORCE_RELOAD=false`.
9. PR, revisión por el rol API, merge y verificar Jenkins en verde. La etapa de ingesta debe
   decir "omitida" si ya se cargó en el computador de Jenkins. Si no, la primera vez carga.

✅ **Gate 4:**
- `eventos` tiene ≥ 1.000.000 documentos, con 2dsphere.
- El reporte de limpieza tiene conteos por regla.
- La segunda ejecución omite la carga.
- La descarga ocurre desde el pipeline con la credencial de Jenkins.
- Los tests de limpieza están en el pipeline.

📸 `reporte_limpieza.json`, el tiempo total de la carga, el log de Jenkins con "Ingesta omitida"
y el conteo final en mongosh.

---

### F5 — Consultas y API [API]

#### Especificación (para 🤖)

**Archivos a crear:**
- `api/app/validacion.py`
- `api/app/consultas.py`
- `api/app/rutas.py` (o ampliar `__init__.py`)
- `api/tests/test_validacion.py`
- `api/tests/test_consultas.py`
- Ampliación de `scripts/smoke_api.sh`

**Diseño clave:** las consultas se construyen con funciones puras que devuelven el filtro o el
pipeline de MongoDB como diccionario. Así se prueban sin base de datos (unitarias) y además se
prueban contra `eventos_semilla` en staging (smoke), con resultados exactos conocidos.

**Endpoints:**

| Método | Ruta | Parámetros | Operador | Respuesta |
|---|---|---|---|---|
| GET | `/near` | `lat`, `lon`, `radio` (metros), `limit` (defecto 100, máx 1000) | `$near` + `$maxDistance` | `{"total_devuelto", "parametros", "resultados": [...]}` |
| POST | `/within` | body: GeoJSON `Polygon` (o `{"geometry": ...}`); `?limit` | `$geoWithin` + `$geometry` | igual |
| GET | `/geonear` | `lat`, `lon`, `radio`, `limit`, `agrupar` (opcional: `borough`, `hora`, `factor`) | aggregate: `$geoNear` (primera etapa) + `$group` opcional + `$limit` | resultados con `distancia_m`, o grupos con `n` y `distancia_media_m` |
| GET | `/spark-results` | — | lista las colecciones `spark_*` | `{"colecciones": [...]}` |
| GET | `/spark-results/<nombre>` | `limit`, `orden` (campo), `desc` (bool) | find sobre `spark_<nombre>` (solo nombres permitidos) | documentos |
| GET | `/health` | — | ya existe | — |

**Validación** (`validacion.py`, devuelve 400 con `{"error": "<mensaje claro>"}`):
- `lat` en [-90, 90] y `lon` en [-180, 180], numéricos.
- `radio` > 0 y ≤ 50.000.
- `limit` entero entre 1 y 1000.
- Polígono: `type == "Polygon"`, al menos un anillo, ≥ 4 posiciones, primera posición igual a
  la última, cada posición `[lon, lat]` válida.
- `nombre` de spark-results en la lista blanca, para evitar leer colecciones arbitrarias.

**Otros requisitos:**
- Serializar `ObjectId` y `datetime` a JSON (fechas ISO).
- Colección configurable con `MONGO_COLLECTION`. En staging, el Jenkinsfile pasa
  `-e MONGO_COLLECTION=eventos_semilla`.
- Medir y devolver `tiempo_ms` en cada respuesta. Sirve para el criterio "tiempos de respuesta
  razonables".

**Smoke tests** (ampliar `smoke_api.sh`, con los valores de `semilla_esperados.json`):
- `/near` en Times Square con 1000 m y limit 1000 → exactamente 120.
- `/within` con el polígono de Midtown → exactamente 120.
- `/geonear` en Times Square con `agrupar` sobre el grupo → un solo grupo con n=120.
- `/near?lat=200&lon=0&radio=10` → 400.
- Polígono sin cerrar → 400.

**Jenkinsfile:** en la etapa de staging, agregar `-e MONGO_COLLECTION=eventos_semilla`.

#### Pasos [API]
1. `git checkout -b feature/api-consultas`.
2. 🤖 Pedir el código con la especificación. Adjuntar `CONTEXT.md`, este plan, todo `api/`,
   `scripts/smoke_api.sh`, `mongo/init/semilla_esperados.json` y el `Jenkinsfile`.
3. Leer y entender. **Esta parte la preguntan mucho**: la diferencia entre `$near` y `$geoNear`,
   por qué `$geoNear` va primero y por qué `[lon, lat]`.
4. Probar en local contra la semilla. Poner `MONGO_COLLECTION=eventos_semilla` en `.env`, luego
   `docker compose up -d --build api` y ejecutar:

```bash
curl "http://localhost:5000/near?lat=40.758&lon=-73.9855&radio=1000&limit=1000"
curl -X POST http://localhost:5000/within -H "Content-Type: application/json" \
  -d '{"type":"Polygon","coordinates":[[[-73.996,40.75],[-73.975,40.75],[-73.975,40.766],[-73.996,40.766],[-73.996,40.75]]]}'
curl "http://localhost:5000/geonear?lat=40.758&lon=-73.9855&radio=1000&agrupar=hora"
curl "http://localhost:5000/near?lat=200&lon=0&radio=10"       # debe dar 400
```

> En Windows (PowerShell) usar `curl.exe` en lugar de `curl`. El JSON del POST es más cómodo
> guardarlo en un archivo `poligono.json` y enviarlo con `-d @poligono.json`.

5. Correr los smoke tests en local: `bash scripts/smoke_api.sh http://localhost:5000`.
6. Cuando F4 haya cargado datos reales, poner `MONGO_COLLECTION=eventos` y repetir los curl.
   Anotar `tiempo_ms` de 5 ejecuciones de cada endpoint. Objetivo: menos de 500 ms con limit 100.
7. PR, revisión por el rol INFRA, merge y Jenkins en verde.

✅ **Gate 5:**
- Los 5 endpoints funcionan con parámetros variables.
- Los errores devuelven 400 con mensaje.
- Los unitarios y los smoke pasan en el pipeline.
- Los conteos de la semilla son exactos.

📸 Salida de cada curl con datos reales y una tabla de tiempos de respuesta.

---

### F6 — Procesamiento con Spark [SPARK]

#### Especificación (para 🤖)

**Archivos a crear:**
- `spark/jobs/agregacion_grilla.py`
- `spark/jobs/agregacion_temporal.py`
- `spark/jobs/verificar_resultados.py`
- La etapa "Procesamiento Spark" en el `Jenkinsfile`

**1. `agregacion_grilla.py`** (argumentos: `--coleccion` con defecto `eventos`, `--celda` en
grados con defecto `0.005` ≈ 500 m, `--top` con defecto `20`)
1. Leer con el MongoDB Spark Connector, proyectando solo los campos necesarios con la opción
   `aggregation.pipeline` (`$project` de coordenadas, fecha, heridos, muertos y borough). Esto
   reduce el I/O y se explica en el informe.
2. Extraer lon y lat de `location.coordinates`.
3. Calcular `celda_x = floor(lon / celda)` y `celda_y = floor(lat / celda)`.
4. Agrupar por celda: `n`, `heridos`, `muertos`, centroide (promedio de lat y lon), y el
   polígono GeoJSON de la celda (para mapas).
5. Escribir `spark_grilla` con todas las celdas y `spark_hotspots` con las `top` celdas por `n`
   y un campo `ranking`.
6. Registrar en `spark_meta` los parámetros, la fecha, la duración, el total leído y la suma de `n`.

**2. `agregacion_temporal.py`**
- Escribe `spark_por_hora` (0–23), `spark_por_dia_semana` (1–7), `spark_por_mes` (1–12) y
  `spark_hora_borough` (hora × borough).
- Cada una incluye `n`, `heridos` y `muertos`.

**3. `verificar_resultados.py`** (prueba de "resultados coherentes y verificables" de la rúbrica)
- La suma de `n` en `spark_grilla` debe ser igual a `countDocuments` de la colección de origen.
- La suma de `n` en `spark_por_hora` debe dar el mismo total.
- Tomar el hotspot número 1, construir su polígono y contar en Mongo con `$geoWithin`. Debe
  coincidir con el `n` de Spark con una tolerancia de ±0,5 % (los bordes geodésicos pueden
  diferir mínimamente).
- Con `--coleccion eventos_semilla`: la suma debe ser 300 y la celda más poblada debe estar en
  Times Square.
- Sale con código 1 si algo no cuadra.

**4. Jenkinsfile**
- Agregar el parámetro `EJECUTAR_SPARK` (boolean, `false`).
- Agregar la etapa "Procesamiento Spark" después de la ingesta. Se ejecuta si el parámetro es
  `true` **o** si `spark_meta` no existe. Corre los dos jobs y luego la verificación.
- En cada build normal, correr **solo** la verificación sobre `eventos_semilla`, que es rápida.

**Cómo ejecutar:** `docker compose exec spark-master /opt/spark/bin/spark-submit /opt/jobs/<job>.py [args]`.

#### Pasos [SPARK]
1. `git checkout -b feature/spark-agregaciones`.
2. 🤖 Pedir el código con la especificación. Adjuntar `CONTEXT.md`, este plan, todo `spark/`,
   el modelo D13 y el `Jenkinsfile`.
3. Leer y entender. Preguntas típicas:
   - qué es un DataFrame distribuido;
   - qué hace el master y qué hace el worker;
   - qué es un shuffle y por qué `groupBy` lo provoca;
   - qué ventaja tiene proyectar en Mongo antes de leer.
4. Probar primero con la semilla:
   `docker compose exec spark-master /opt/spark/bin/spark-submit /opt/jobs/agregacion_grilla.py --coleccion eventos_semilla`
   y luego `verificar_resultados.py --coleccion eventos_semilla`.
5. Mientras corre, abrir http://localhost:8081, entrar a la aplicación y ver las etapas y las
   tareas del worker. 📸 Captura.
6. Cuando F4 haya cargado datos reales, correr los dos jobs sobre `eventos` y la verificación.
7. Revisar que los hotspots tengan sentido. En NYC deberían salir zonas de Midtown y Brooklyn.
   Anotar los 5 primeros con sus coordenadas.
8. PR, revisión por el rol DATOS, merge y Jenkins en verde.

✅ **Gate 6:**
- Existen `spark_grilla`, `spark_hotspots` y las 4 colecciones temporales.
- `verificar_resultados.py` pasa sobre datos reales.
- El pipeline verifica la semilla en cada build.

📸 Salida de la verificación, top 5 de hotspots, gráfico de barras por hora (con cualquier
herramienta) y captura de la UI de Spark.

---

### Mientras tanto [INFRA] (sábado y domingo) ⏱️ 2–3 h
1. Revisar los PRs de los demás. Cada merge debe quedar en verde.
2. Medir el tiempo total del pipeline en un build normal, con la ingesta omitida. Objetivo:
   **menos de 5 minutos**. Si pasa de 8, pedirle a Claude que optimice (caché de capas, no
   reconstruir imágenes que no cambiaron).
3. Grabar un **video de respaldo** del flujo completo: cambio → push → PR → merge → Jenkins → `/health`.
   Si en la sustentación falla internet, se muestra el video y se explica.

---

## DÍA 6 — Lunes 5 de octubre · Integración + F7 · ⏱️ 3–4 h

**Objetivo:** todo integrado en `main`, con datos reales, y el pipeline completo en verde y rápido.

### Paso 6.1 — Integración sobre datos reales [TODOS, 1 h juntos, en llamada]
1. En el computador de Jenkins: `git pull` y lanzar el build con `EJECUTAR_SPARK=true`.
2. Comprobar en orden:
   - la ingesta se omite (o carga, si es la primera vez en ese computador);
   - Spark procesa y la verificación pasa;
   - staging pasa los smoke;
   - se despliega.
3. Probar los 5 endpoints contra producción con datos reales.
   `/spark-results/hotspots` debe devolver los hotspots.

✅ Build completo en verde con datos reales.

### Paso 6.2 — F7: completar las pruebas [API + INFRA] ⏱️ 2 h
Checklist de lo que debe existir. Pedirle a Claude lo que falte 🤖:
- [ ] pytest API: validación (casos límite de lat, lon, radio, limit y polígonos inválidos),
      constructores de consultas y serialización.
- [ ] pytest ingesta: cada regla de limpieza y el orden `[lon, lat]`.
- [ ] Smoke: los 5 endpoints con conteos exactos de la semilla, más 2 casos de error.
- [ ] Integración: checks de Dask y Spark, y la verificación de Spark sobre la semilla.
- [ ] `FORZAR_FALLO` sigue bloqueando el deploy. Repetir la prueba y la captura.
- [ ] Pipeline normal en menos de 5 minutos.

✅ **Gate 7/8:** todo lo anterior marcado.
📸 La vista de etapas final en verde y un resumen de pytest (`N passed`) de las dos suites.

---

## DÍA 7 — Martes 6 de octubre · F8 Benchmark Dask vs Spark · ⏱️ 4–5 h

### Especificación (para 🤖)

**Archivos a crear:**
- `benchmark/bench_dask.py`
- `benchmark/bench_spark.py`
- `benchmark/medir.sh`
- `benchmark/graficar.py`
- `benchmark/README.md`

**Operación pesada (idéntica en ambos motores):**
1. Leer `/data/parquet/eventos/`.
2. Calcular la celda de grilla de 0,005°.
3. Contar por celda y sumar los heridos.
4. Ordenar por conteo y tomar el top 20.
5. Forzar el cómputo completo (`.compute()` o `.collect()`).

La lógica es la misma que F6, pero sobre Parquet, para comparar motores y no el I/O de MongoDB (D5).

**Configuraciones (mismo total de recursos para ambos motores):**

| Config | Dask | Spark |
|---|---|---|
| **A** | 1 worker × 2 hilos (se detiene `dask-worker-2`) | 1 worker × 2 núcleos |
| **B** | 2 workers × 2 hilos | 2 workers × 2 núcleos (se levanta `spark-worker-2` del perfil `bench`) |

**Medición (`medir.sh <motor> <config> <repeticion>`):**
1. Lanza en segundo plano un muestreo de `docker stats --no-stream` cada 1 segundo para los
   contenedores del motor y lo guarda en un CSV.
2. Ejecuta el benchmark y mide el tiempo de reloj dentro del script con `time.perf_counter`,
   solo el cómputo, sin contar el arranque.
3. Detiene el muestreo y calcula el **pico de memoria** (suma de los workers y del
   scheduler/driver) y el promedio de CPU.
4. Agrega una fila a `benchmark/resultados.csv` con: motor, config, repetición, segundos,
   memoria pico en MB, CPU promedio y número de filas.

**Protocolo:**
- 1 corrida de calentamiento (no se registra) y **3 repeticiones** por combinación.
- Son 4 combinaciones, así que 12 corridas registradas.
- Entre corridas no hay otros procesos pesados.

**Salida de `graficar.py`:**
- `docs/evidencias/bench_tiempo.png` y `docs/evidencias/bench_memoria.png`: barras con la
  media y la desviación estándar.
- Una tabla resumen en markdown.

### Pasos [SPARK como responsable, con INFRA o DATOS de apoyo]
1. `git checkout -b feature/benchmark`.
2. 🤖 Pedir el código con la especificación.
3. Confirmar que existe `/data/parquet/eventos/` (lo genera F4):
   `docker compose exec spark-master ls /data/parquet/eventos | head`.
4. **Config A:**

```bash
docker compose stop dask-worker-2
bash benchmark/medir.sh dask A 0      # calentamiento
bash benchmark/medir.sh dask A 1; bash benchmark/medir.sh dask A 2; bash benchmark/medir.sh dask A 3
bash benchmark/medir.sh spark A 0
bash benchmark/medir.sh spark A 1; bash benchmark/medir.sh spark A 2; bash benchmark/medir.sh spark A 3
```

5. **Config B:**

```bash
docker compose start dask-worker-2
docker compose --profile bench up -d spark-worker-2
# verificar: 2 workers en http://localhost:8787 y 2 ALIVE en http://localhost:8081
bash benchmark/medir.sh dask B 0
bash benchmark/medir.sh dask B 1; bash benchmark/medir.sh dask B 2; bash benchmark/medir.sh dask B 3
bash benchmark/medir.sh spark B 0
bash benchmark/medir.sh spark B 1; bash benchmark/medir.sh spark B 2; bash benchmark/medir.sh spark B 3
docker compose --profile bench stop spark-worker-2
```

6. `python benchmark/graficar.py`.
7. Escribir el análisis (1 página) en `benchmark/README.md` respondiendo con **sus números**:
   - ¿Qué motor fue más rápido en A y en B?
   - ¿Cuánto mejoró cada uno al pasar de A a B? ¿Escala linealmente? ¿Por qué sí o por qué no?
   - ¿Cuál usó más memoria? Pista: la JVM de Spark tiene un costo fijo.
   - ¿Cuánto pesó el arranque? (Spark tiene más latencia de inicio.)
   - **Conclusión:** cuándo conviene cada uno. Por ejemplo, Dask para ecosistema Python y
     tamaños medianos; Spark para volúmenes mayores, tolerancia a fallos y clústeres grandes.
     **Debe salir de sus mediciones**, no de lo que dice internet.
8. PR, revisión y merge.

✅ **Gate 10:** `resultados.csv` con 12 filas, 2 gráficos y el análisis escrito.
📸 Los gráficos y la tabla resumen.

> Si el computador no aguanta la Config B, reducir la muestra del Parquet (por ejemplo, al
> primer millón de filas) para **todas** las corridas, y declararlo en el informe.

---

## DÍA 8 — Miércoles 7 de octubre · F9 Reproducibilidad + F10 Documentación · ⏱️ 5–6 h

### Paso 8.1 — Prueba de reproducibilidad en otro computador [INFRA + otro integrante] ⏱️ 1,5 h
**Es obligatoria**: el enunciado dice que si solo funciona en un computador no está terminado.

1. En un computador que **nunca** haya tenido el proyecto (o después de
   `docker compose down -v` y `docker system prune -a` en uno de los integrantes):
   seguir **solo** el README, sin ayuda verbal.
2. Anotar cada paso que no estuviera escrito o que fallara, y corregir el README en ese momento.
3. Tomar el tiempo desde el `git clone` hasta `/health` OK con datos cargados.

✅ Otra persona levanta todo solo con el README.
📸 Tiempo total y lista de correcciones al README.

### Paso 8.2 — Leaflet (opcional, solo si todo lo anterior está en verde) [API] ⏱️ 1,5 h
🤖 Pedir: "una página `api/app/static/mapa.html`, servida en `/mapa`, con Leaflet desde CDN, que
permita:
- hacer clic en el mapa para consultar `/near` con un radio elegido;
- dibujar un polígono para consultar `/within`;
- activar una capa con `spark_hotspots` coloreada por `n`."

Suma puntos en la presentación y facilita mucho la demo.

### Paso 8.3 — README final [INFRA] ⏱️ 45 min
Debe explicar **desde cero**:
- requisitos;
- clonar, configurar `.env`, levantar y cargar datos;
- configurar Jenkins (enlazando la guía de la Fase 2);
- los endpoints con un ejemplo de curl cada uno;
- cómo correr las pruebas y el benchmark;
- la estructura del repositorio;
- las referencias y el código de terceros citado.

### Paso 8.4 — Informe técnico ≤ 10 páginas [TODOS; cada uno escribe su sección] ⏱️ 3 h
Estructura con presupuesto de páginas. Todo el material ya está en `docs/decisiones.md` y
`docs/evidencias/`:

| # | Sección | Páginas | Responsable | Fuente |
|---|---|---|---|---|
| 1 | Introducción y dataset (origen, tamaño, campos, por qué se eligió) | 0,75 | DATOS | JSON de verificación |
| 2 | Arquitectura: diagrama y flujo de datos | 1,25 | INFRA | CONTEXT §4 (redibujar en draw.io o Excalidraw) |
| 3 | Decisiones técnicas (D1–D13, resumidas) | 1,5 | INFRA | `docs/decisiones.md` |
| 4 | Ingesta y limpieza: tabla de conteos por regla con justificación | 1 | DATOS | `reporte_limpieza.json` |
| 5 | Modelo geoespacial y consultas: documento, índices, las 3 consultas con ejemplo y tiempos | 1,5 | API | curl y tiempos de F5 |
| 6 | Procesamiento Spark: agregaciones, hotspots y verificación | 1 | SPARK | salidas de F6 |
| 7 | CI/CD: etapas, webhook, bloqueo de deploy (capturas) | 1 | INFRA | capturas F2 y F7 |
| 8 | Dask vs Spark: método, resultados y análisis | 1,5 | SPARK | benchmark |
| 9 | Conclusiones, limitaciones y referencias | 0,5 | TODOS | — |

Formato: Word o PDF con fuente de 11 pt. **Revisar al final que no pase de 10 páginas.**
Guardarlo en `docs/informe/`.

✅ **Gate 12:** README probado por otra persona e informe de 10 páginas o menos en el repo.

---

## DÍA 9 — Jueves 8 de octubre · F11 Simulacro de sustentación · ⏱️ 4 h

### Paso 9.1 — Congelamiento [INFRA] ⏱️ 15 min
1. Todo integrado en `main` y en verde.
2. Crear la etiqueta: `git tag v1.0 && git push origin v1.0`.
3. A partir de aquí, solo se hacen los cambios del simulacro.

### Paso 9.2 — Simulacro de cambios en vivo [TODOS] ⏱️ 2 h
Cada integrante hace **al menos dos** de estos cambios, con el cronómetro corriendo. Objetivo:
**15 minutos o menos** desde que "el docente" lo pide hasta que se ve desplegado. Otro
integrante hace de docente y elige el cambio **sin avisar antes**.

| # | Cambio probable del docente | Qué tocar |
|---|---|---|
| 1 | "Un endpoint que cuente los eventos dentro de un polígono" | `api/app/rutas.py` + validación existente + un test + un smoke |
| 2 | "Consulten este otro polígono (por ejemplo, Central Park)" | Solo el body del POST a `/within`; mostrar que **no** hace falta tocar código (parámetros) |
| 3 | "Filtren `/near` por rango de fechas" | Parámetros `desde` y `hasta` en validación y en el constructor de consulta, más un test |
| 4 | "Una agregación nueva en Spark: por día de la semana y borough" | Nuevo `groupBy` en `agregacion_temporal.py`, nueva colección y lista blanca de spark-results |
| 5 | "Cambien el tamaño de la celda de la grilla" | Argumento `--celda`; ejecutar y mostrar el resultado nuevo |
| 6 | "Un endpoint con los N hotspots más cercanos a un punto" | `$geoNear` sobre `spark_hotspots` (requiere índice 2dsphere sobre el centroide) |
| 7 | "Devuelvan solo algunos campos en `/near`" | Proyección en el constructor de consulta |

Para cada uno, el flujo completo:
1. Rama.
2. Cambio y su test.
3. Push.
4. PR.
5. Aprobación.
6. Merge.
7. **Mostrar a Jenkins construyendo.**
8. Mostrar `/health` con la nueva versión.
9. Mostrar el cambio funcionando con curl o en el mapa.

✅ Cada integrante completó 2 cambios en menos de 15 minutos cada uno.

### Paso 9.3 — Preguntas individuales [TODOS] ⏱️ 1,5 h
Cada integrante responde en voz alta **todas** las preguntas, no solo las de su rol. Otro
evalúa con la guía de respuesta.

| Pregunta | Idea clave de la respuesta |
|---|---|
| ¿Por qué Dask para la ingesta y Spark para el procesamiento? | Lo pide el enunciado. Dask es Python nativo, cómodo para limpieza tipo pandas; Spark es fuerte en agregaciones distribuidas y tiene conector nativo con MongoDB |
| ¿Qué es una partición en Dask? ¿Cuántas tenían? | Un trozo del CSV (unos 64 MB) procesado como un DataFrame de pandas; decir el número real |
| ¿Qué es la evaluación perezosa? | Dask y Spark construyen un grafo de tareas y solo ejecutan con `compute()` o `collect()`, o con una acción |
| ¿Por qué `[lon, lat]` y no `[lat, lon]`? | Así lo define el estándar GeoJSON (x, y) |
| ¿Qué hace el índice 2dsphere? ¿Qué pasa sin él? | Indexa geometrías sobre la esfera; `$near` y `$geoNear` lo exigen; sin él, error o recorrido completo |
| Diferencia entre `$near` y `$geoNear` | `$near` es un filtro de find que ordena por distancia; `$geoNear` es una etapa de agregación que debe ir primero, devuelve la distancia y permite `$group` después |
| ¿`$geoWithin` necesita índice? | No es obligatorio, pero lo usa si existe |
| ¿Cómo justifican cada regla de limpieza? | Con la tabla de conteos y su porqué, sobre todo el (0,0) y el bounding box |
| ¿Qué hacen el master y el worker de Spark? | El master asigna recursos; el worker ejecuta executors; el driver planifica las etapas |
| ¿Qué es un shuffle? | Redistribuir datos entre nodos por clave (groupBy); es la parte cara |
| ¿Cómo verificaron que Spark da resultados correctos? | Suma de conteos igual al total, y el hotspot contrastado con `$geoWithin` |
| ¿Qué pasa si falla un test? | El pipeline se detiene, no hay deploy y sigue la versión anterior (mostrar la captura) |
| ¿Dónde está el token de Kaggle? | En las credenciales de Jenkins y en el `.env` local ignorado por Git; nunca en el repo |
| ¿Por qué smee y no ngrok? | Para no exponer Jenkins, que controla Docker, a internet |
| ¿Cómo evitan recargar los datos en cada build? | La ingesta idempotente: `ingesta_meta` + conteo, y `FORCE_RELOAD` para forzar |
| ¿Qué es staging en su pipeline? | La nueva imagen se prueba en un contenedor temporal antes de reemplazar la API |
| ¿Qué concluyeron de Dask vs Spark? | Sus números: tiempos, memoria y escalado de A a B |
| ¿Qué harían distinto con 10 veces más datos? | Clúster real, particionar o shardear Mongo, Spark con más workers, Parquet como almacenamiento principal |

### Paso 9.4 — Checklist final del proyecto [INFRA lee en voz alta, todos confirman] ⏱️ 15 min
Recorrer la sección 12 de `CONTEXT.md` (criterio de proyecto terminado) casilla por casilla.

---

## DÍA 10 — Viernes 9 de octubre · Entrega y sustentación

### Antes de salir
- [ ] El computador de Jenkins está cargado, con el cargador y el adaptador de video si hay proyector.
- [ ] **1 hora antes:** abrir Docker Desktop y ejecutar `docker compose --profile ci up -d`.
- [ ] `docker compose ps`: todo healthy.
- [ ] `docker compose logs --tail 5 smee`: dice "Connected".
- [ ] Un push de prueba (por ejemplo, un espacio en el README con su PR) para confirmar que el webhook dispara.
- [ ] Pestañas abiertas:
  - GitHub (repo y PRs);
  - Jenkins (el job);
  - `/health`;
  - Spark UI;
  - Dask dashboard;
  - el mapa, si existe;
  - el informe.
- [ ] Una terminal con los curl de ejemplo preparados.
- [ ] El video de respaldo descargado localmente.
- [ ] Enlace del repositorio y del informe entregados por el canal del curso.

### Plan B si falla algo durante la sustentación
| Falla | Qué hacer |
|---|---|
| No hay internet o no llega el webhook | Hacer el push igual y lanzar el build con **Build Now**. Explicar que el trigger normal es el webhook y mostrar el video y la captura de "Started by GitHub push" |
| Se cae un contenedor | `docker compose up -d <servicio>`; tener a la mano `docker compose logs <servicio>` |
| El build tarda demasiado | Mientras corre, explicar las etapas; por eso importa que dure menos de 5 minutos |
| Un test falla con el cambio pedido | Es una oportunidad: mostrar que el deploy no se hizo, corregir y volver a hacer push |

---

## Resumen de fechas límite

| Fecha | Debe estar hecho |
|---|---|
| Mié 30 sep | Dataset verificado y registrado; repo creado; roles |
| Jue 1 oct | Sistema levantado; primer build en verde |
| Vie 2 oct | **Gate 2:** webhook y bloqueo de deploy; modelo D13 |
| Dom 4 oct | **Gates 4, 5 y 6:** ingesta, API y Spark en `main` |
| Lun 5 oct | Integración con datos reales; pruebas completas; pipeline en menos de 5 min |
| Mar 6 oct | Benchmark con análisis |
| Mié 7 oct | Reproducibilidad probada; README e informe |
| Jue 8 oct | Congelamiento v1.0; simulacro superado |
| Vie 9 oct | **Entrega y sustentación** |

**Si se atrasan:**
- 1 día de atraso: se recorta Leaflet.
- 2 días: el benchmark se hace con 2 repeticiones en lugar de 3.
- **Nunca** se recortan el pipeline, los tests, la reproducibilidad ni el simulacro.
