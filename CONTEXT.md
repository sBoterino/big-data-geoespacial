# CONTEXT.md — BIG DATA GEOESPACIAL
## Contexto maestro transferible entre IAs — v30 (4-oct-2026)

> **Propósito:** contexto, alcance, arquitectura, decisiones, estado y plan del proyecto, para que
> cualquier IA o integrante continúe exactamente desde donde se dejó, sin inventar decisiones.
>
> **Cambios en v30:** PR #1 fusionado y `bdgeo-main` #6 aprobado. Dask procesó 1.972.121 filas en
> 6 particiones, insertó 1.741.828 documentos en 57,435 s, pasó integraciones y desplegó API v6.
> MongoDB e índices fueron auditados; falta una segunda ejecución idempotente de la carga completa.
>
> **Cambios en v29:** auditoría directa de la muestra aprobada: 45.843 documentos, un `Point` real
> en orden longitud/latitud, fecha BSON y los índices `_id_`, `fecha_1` y `location_2dsphere`.
> La rama quedó integrada mediante PR #1; la carga completa fue aprobada en `bdgeo-main` #6.
>
> **Cambios en v28:** build #7 aprobado. La capa cacheable de Spark funcionó y la segunda ingesta
> detectó los 45.843 documentos existentes, imprimió `Ingesta omitida`, pasó Dask/Spark y no
> modificó producción. D3 quedó demostrada.
>
> **Cambios en v27:** los builds #4 y #6 no llegaron a la idempotencia por DNS de Docker
> Hub/Maven. Se sustituyeron los `ADD` remotos de Spark por una capa `RUN` cacheable y se añadieron
> tres intentos con espera a las construcciones Jenkins. Falta validar la mitigación.
>
> **Cambios en v26:** build de muestra #3 aprobado. Procesó 50.000 filas, descartó 3.888 por R1 y
> 269 por R2, insertó 45.843 documentos en 5,684 s, pasó Dask/Spark y omitió el despliegue por ser
> un job de rama. El próximo build debe demostrar idempotencia.
>
> **Cambios en v25:** el build #2 confirmó la distribución de `limpieza.py` y avanzó hasta el
> conteo final. Detectó una reducción inestable de escalares con una sola partición. Se reemplazó
> por suma explícita de longitudes y se añadieron dos pruebas; falta validarlo en el build #3.
>
> **Cambios en v24:** el build de muestra #1 validó Kaggle, imágenes, pruebas y dos workers. Falló
> de forma segura al deserializar el grafo porque el scheduler no encontraba `limpieza.py`.
> Se añadió `Client.upload_file`; falta confirmar la corrección en el build #2.
>
> **Cambios en v23:** F4 implementada en `feature/ingesta-dask`: descarga cacheada de Kaggle,
> limpieza R1–R6, GeoJSON, carga Dask por lotes, Parquet, metadatos idempotentes y etapa Jenkins.
> Las 3 pruebas sintéticas pasaron dentro de Docker; falta ejecutar la muestra de 50.000 filas.
>
> **Cambios en v22:** se creó `docs/guia_sustentacion.md`, que cruza la sección 6 del enunciado
> con las evidencias actuales, separa lo demostrable de lo pendiente y mantiene un banco vivo de
> respuestas, cambios probables y evidencias. Debe actualizarse junto con este contexto.
>
> **Cambios en v21:** Gate 2 aprobado. El push real inició automáticamente el build #2 y desplegó
> `version=2`. El build parametrizado #3 falló intencionalmente en pytest, omitió el despliegue y
> `/health` permaneció en versión 2. La auditoría no encontró credenciales rastreadas ni tokens.
>
> **Cambios en v20:** se creó el canal de smee, se levantó el reenviador y GitHub entregó el ping
> a Jenkins con HTTP 200. La publicación de esta actualización sirve como prueba del primer push
> real; falta confirmar que Jenkins inició automáticamente y ejecutar `FORZAR_FALLO`.
>
> **Cambios en v19:** se revocó el token de Kaggle expuesto y se creó `jenkins-bdgeo`; Jenkins
> guarda `mongo-root` y `kaggle-api-token`. Se creó el job `bdgeo-main` contra `*/main` y el build
> #1 terminó en SUCCESS: pytest, acceso real a Kaggle, Dask, Spark, staging y despliegue versión 1.
> Falta conectar smee/GitHub y ejecutar la prueba negativa `FORZAR_FALLO` para cerrar el Gate 2.
>
> **Cambios en v18:** se corrigió la autenticación de Kaggle al mecanismo actual: paquete 2.2.4,
> variable `KAGGLE_API_TOKEN` y credencial Jenkins `kaggle-api-token` de tipo *Secret text*. El token
> anterior debe revocarse porque apareció visible en una captura; el nuevo nunca se comparte.
>
> **Cambios en v17:** se completó el asistente inicial de Jenkins, se creó el usuario administrador
> y el panel quedó accesible en `http://localhost:8080/`. Faltan las credenciales internas, el job,
> el primer build, smee/webhook y la prueba de bloqueo del despliegue.
>
> **Cambios en v16:** Jenkins se construyó en 242,7 s después de reiniciar Docker para recuperar
> su DNS interno. El contenedor quedó iniciado en el puerto 8080 y Jenkins 2.541.3 respondió con
> redirección a la pantalla de acceso. Falta completar el asistente, credenciales, job y webhook.
>
> **Cambios en v15:** las pruebas internas pasaron. Dask confirmó dos workers, cálculo distribuido
> y 300 documentos semilla. Spark leyó los 300, agregó 120/80/100 y escribió tres documentos en
> `spark_check`, verificados directamente en MongoDB. La infraestructura distribuida está validada;
> falta Jenkins, webhook y la demostración de bloqueo del despliegue.
>
> **Cambios en v14:** el Compose base se construyó y levantó correctamente: 61/61 pasos, siete
> servicios iniciados y respuestas correctas de API, Dask y Spark desde el host. Evidencia parcial
> en `docs/evidencias/gate2_arranque_2026-10-04.md`; faltan las pruebas internas y Jenkins.
>
> **Cambios en v13:** Docker Desktop quedó instalado y verificado desde la PowerShell normal:
> Docker 29.8.1, Docker Compose 5.5.1 y `docker run --rm hello-world` exitoso. El siguiente paso
> es crear el `.env` local y levantar los servicios del Gate 2.
>
> **Cambios en v12:** WSL 3.0.1 quedó instalado después del reinicio. Se descargó el instalador
> oficial de Docker Desktop para Windows x86-64 y se verificó su firma válida de Docker Inc.; la
> instalación automática desde el entorno aislado terminó con código 1, por lo que debe ejecutarse
> manualmente desde Windows.
>
> **Cambios en v11:** Git 2.56.0 quedó operativo y se clonó una copia local normal del repositorio
> público. La verificación del equipo corrigió un dato anterior: Docker Desktop no está instalado
> ni disponible en el `PATH`, por lo que el Gate 2 queda bloqueado hasta instalarlo.
>
> **Cambios en v10:** se decidió no activar un ruleset de protección porque no es un requisito
> explícito de la rúbrica. El equipo mantiene el flujo obligatorio de ramas, PR y revisión.
>
> **Cambios en v9:** Git para Windows instalado y repositorio público poblado con los 45 archivos
> auditados. Datos, entorno virtual y credenciales quedaron excluidos.
>
> **Cambios en v8:** repositorio público creado en GitHub; permanece vacío porque Git todavía
> no está instalado o disponible en el `PATH` de la terminal normal de Windows.
>
> **Cambios en v7:** integrantes registrados y destino GitHub definido: repositorio público
> `sBoterino/big-data-geoespacial`. Los roles técnicos siguen pendientes de asignación.
>
> **Cambios en v6:** validación estática previa al Gate 2 completada: pruebas API normales y
> con fallo forzado, compilación Python y parseo YAML de Compose. Evidencia registrada.
>
> **Cambios en v5:** perfilador corregido y cubierto por pruebas sintéticas; repositorio Git
> local iniciado en `main`; borrador de registro al docente preparado; próxima acción actualizada.
>
> **Cambios en v4:** dataset principal verificado con la API de Kaggle y perfilado real guardado
> en `docs/evidencias/`: 1.972.121 registros, 29 columnas y defectos geográficos medidos.
>
> **Cambios en v3:** esqueleto de la Fase 2 escrito (compose, Jenkins, Jenkinsfile, API `/health`,
> checks de integración) y avance de la Fase 3 (validador GeoJSON, índices, datos semilla).
> Decisiones D8–D12. **Nada de esto se ha ejecutado aún en Docker: falta validar el Gate 2.**
>
> **Cambios en v2 respecto a v1:** MongoDB pasa a Docker (Atlas descartado). Jenkins pasa de la
> Fase 9 al inicio con un esqueleto de CI/CD. Hay un calendario de 9 días, un registro de
> riesgos técnicos, candidatos de dataset investigados, gates por componente en paralelo y
> Leaflet en lugar de QGIS.

---

# 1. IDENTIDAD DEL PROYECTO

**Proyecto:** Trabajo práctico de Big Data — procesamiento y consulta de datos geoespaciales con despliegue continuo.
**Docente:** Andrés Felipe Hernández Marulanda.
**Publicación:** 24-sep-2026. **Entrega y sustentación:** 9-oct-2026 (sin prórroga).
**Días disponibles desde v2:** 9 (30-sep → 8-oct), más la entrega.

Pipeline objetivo: **Kaggle → Dask → MongoDB → Spark → Flask → Jenkins**, todo en Docker Compose,
reproducible en otro equipo sin pasos manuales ocultos.

---

# 2. FUENTE ACADÉMICA PRINCIPAL

`Trabajo_Big_Data_Geoespacial-1.docx` es la fuente de requisitos. Si algo de este archivo lo
contradice, manda el documento.

## Requisitos (resumen fiel del enunciado)

**Dataset:** de Kaggle, con latitud/longitud o geometrías, de al menos 1 GB o 1 millón de
registros, único por equipo y registrado con el docente antes de empezar. La descarga se hace
con la API de Kaggle desde el pipeline. El token es una credencial de Jenkins y nunca está en
GitHub. Se permite una muestra de al menos 1 millón de registros si la descarga completa queda
automatizada.

**Servicios en Docker Compose (mínimo):**
- MongoDB con GeoJSON e índice 2dsphere.
- Spark con un master y al menos un worker, conectado mediante el MongoDB Spark Connector.
- Dask con un scheduler y al menos dos workers.
- Flask.
- Jenkins con Jenkinsfile versionado en el repositorio.

**GitHub:** trabajo en ramas, pull requests y webhook que dispara Jenkins al integrar en la rama
principal. **El historial de commits se revisa y debe reflejar el aporte real de cada integrante.**

**Ingesta y limpieza (Dask):** lectura particionada, descartar coordenadas nulas o fuera de
rango, transformar a punto GeoJSON y cargar a MongoDB por lotes. La limpieza se justifica en el
informe.

**Spark:** lee desde MongoDB y calcula agregaciones espaciales y temporales (grilla o geohash,
zonas de alta concentración, patrones por hora, día o mes). Los resultados van a colecciones
nuevas.

**Consultas:** `$near` (radio), `$geoWithin` (polígono) y una agregación con `$geoNear`, todas
con parámetros y sin valores fijos en el código.

**API Flask (mínimo 3 endpoints):**
1. Recibe latitud, longitud y radio, y devuelve los registros cercanos.
2. Recibe un polígono GeoJSON y devuelve lo que cae dentro.
3. Devuelve los resultados de Spark.

Leaflet es opcional, suma a la presentación y no se califica aparte.

**Jenkinsfile:** checkout, build de imágenes, pytest, levantar servicios, pruebas básicas contra
la API y deploy. **Si una prueba falla, no hay deploy.**

**Dask vs Spark:** una operación pesada, dos configuraciones de workers, medición de tiempos y
memoria, y conclusiones basadas en mediciones propias.

**Entregables:**
- Repositorio en GitHub con README (cómo levantar desde cero), `docker-compose.yml` y `Jenkinsfile`.
- Informe de máximo 10 páginas con diagrama de arquitectura, decisiones, consultas y comparación Dask vs Spark.

**Sustentación:** en vivo, con el sistema funcionando. El docente pide una modificación puntual
(por ejemplo, un endpoint nuevo o un polígono distinto). El equipo la programa, hace push,
muestra a Jenkins construyendo y la nueva versión desplegada. Hay preguntas individuales sobre
cualquier parte del sistema.

**Rúbrica:**

| Criterio | Peso |
|---|---|
| Infraestructura y orquestación (un comando, comunicación entre contenedores, secretos seguros) | 20 % |
| Ingesta y procesamiento (Kaggle automático, limpieza justificada, Spark coherente) | 25 % |
| Modelado y consultas (GeoJSON válido, 2dsphere, parámetros, tiempos razonables) | 20 % |
| API y CI/CD (endpoints, webhook, tests que bloquean el deploy) | 20 % |
| Análisis y sustentación (mediciones propias, cambio en vivo, dominio individual) | 15 % |

**Otras condiciones:** si solo funciona en un computador, no está terminado. Código de terceros
sin citar se considera copia. Las entregas tardías no se reciben.

---

# 3. DECISIONES TOMADAS

El detalle y la justificación están en `docs/decisiones.md`, que es la fuente para el informe.

| ID | Decisión | Estado |
|---|---|---|
| D1 | MongoDB en contenedor Docker, no Atlas | Aprobada |
| D2 | Esqueleto CI/CD primero (push→Jenkins→pytest→deploy de `/health`) | Aprobada |
| D3 | Ingesta idempotente: descarga cacheada en volumen, carga omitida si ya existe, `FORCE_RELOAD` | Aprobada |
| D4 | Imagen oficial `apache/spark` con versiones fijas y el conector incluido en la imagen | Aprobada |
| D5 | Benchmark sobre la misma fuente Parquet, límites de CPU y RAM en Compose, 3 repeticiones | Aprobada |
| D6 | Leaflet opcional al final; QGIS y BI fuera | Aprobada |
| D7 | Dataset: NYC Motor Vehicle Collisions (respaldo: US Wildfires) | **Verificado: falta registrarlo** |
| D8 | Webhook vía smee.io (Jenkins no se expone a internet) | Aprobada |
| D9 | Jenkins como root para usar el socket de Docker (riesgo aceptado y documentado) | Aprobada |
| D10 | Deploy = imagen `bdgeo-api:<BUILD>` → staging + smoke → promoción a `api` → verificación | Aprobada |
| D11 | Datos semilla deterministas (300 puntos, conteos conocidos) para las pruebas | Aprobada |
| D12 | Validador `$jsonSchema` de GeoJSON en MongoDB | Aprobada |

**Nota sobre D1:** si el docente pidiera expresamente usar Atlas, solo cambia la cadena de
conexión. Pero no se espera respuesta para avanzar.

---

# 4. ARQUITECTURA

```text
 Developer ──push/PR──▶ GITHUB (flujo por PR acordado, Jenkinsfile)
                            │ webhook → smee.io → servicio smee (sin exponer Jenkins, D8)
                            ▼
                     JENKINS (contenedor con Docker CLI + compose,
                              socket /var/run/docker.sock montado)
                            │ checkout → build → pytest → up → smoke tests → deploy
                            ▼
 ┌──────────────── Docker Compose (red interna) ────────────────────────┐
 │                                                                       │
 │  DASK scheduler + worker1 + worker2 ──(lotes)──▶ MONGODB              │
 │        ▲ lee de volumen "kaggle_data"             (GeoJSON, 2dsphere, │
 │        │                                           resultados Spark)  │
 │  kaggle download (cacheado)                          ▲      ▲         │
 │                                                      │      │         │
 │  SPARK master + worker ◀──MongoDB Spark Connector────┘      │         │
 │        └── escribe colecciones de agregados ────────────────┘         │
 │                                                             │         │
 │  FLASK API ──── $near / $geoWithin / $geoNear ──────────────┘         │
 │        ▲                                                              │
 └────────┼──────────────────────────────────────────────────────────────┘
          │ HTTP
     Cliente / (opcional) página Leaflet
```

**Separación de Jenkins:** Jenkins está en el mismo `docker-compose.yml`, pero con un perfil
(`profiles: [ci]`) o un proyecto de Compose separado. El paso de deploy solo levanta los
servicios de la aplicación. Si recreara Jenkins, se reiniciaría a sí mismo en mitad del build.

**Volúmenes:** se usan volúmenes con nombre (`mongo_data`, `kaggle_data`, `parquet_data`) y no
bind mounts. Con el socket de Docker, las rutas de un bind mount se resuelven en el host y no
dentro de Jenkins.

## Responsabilidades

| Componente | Responsabilidad |
|---|---|
| Kaggle API | Descarga automatizada (en pipeline, cacheada) |
| Dask | Lectura particionada, limpieza, GeoJSON, carga por lotes; también exporta Parquet para el benchmark |
| MongoDB | Almacenamiento GeoJSON, índice 2dsphere, colecciones de resultados |
| Spark | Agregaciones espaciales y temporales vía conector |
| Flask | API REST |
| Jenkins | CI/CD disparado por webhook |
| GitHub | Código, ramas, PRs, historial por integrante |
| Docker Compose | Orquestación con un solo comando |

## Modelo de documento (propuesta para la Fase 3; se ajusta al dataset)

```json
{
  "_id": "<id original del registro>",
  "location": { "type": "Point", "coordinates": [<longitud>, <latitud>] },
  "fecha": ISODate("..."),
  "hora": 14, "dia_semana": 3, "mes": 7, "anio": 2019,
  "...atributos relevantes del dataset...": "..."
}
```

**GeoJSON va en orden `[longitud, latitud]`.** Es el error más común del proyecto.

Índices previstos:
- `location` como `2dsphere`, creado después de la carga masiva.
- `fecha`, si hay filtros temporales.

---

# 5. FLUJOS

**Ingesta (idempotente):**
1. Si no hay caché en `kaggle_data`, se descarga desde Kaggle.
2. Si la colección ya tiene N documentos y `FORCE_RELOAD=false`, se omite la carga.
3. En otro caso, Dask lee de forma particionada y aplica la limpieza:
   - quita coordenadas nulas;
   - quita (0,0);
   - quita valores fuera de rango (|lat|>90, |lon|>180);
   - quita puntos fuera del bounding box de la región;
   - quita duplicados;
   - parsea fechas.
4. Se generan los puntos GeoJSON y se cargan con `insert_many(ordered=False)` por lotes.
5. Se crea el índice 2dsphere.
6. Se exporta Parquet para el benchmark.

**Procesamiento:** MongoDB → conector → Spark → agregados por celda o geohash y por
hora/día/mes → nuevas colecciones.

**Consulta:** cliente → Flask (valida parámetros) → `$near` / `$geoWithin` / `$geoNear` con
`limit` → JSON.

**CI/CD:** push o merge a main → webhook → checkout → build → pytest (unitarios con datos
semilla) → up → smoke tests contra la API → deploy (imagen etiquetada con el número de build,
healthcheck). Si falla cualquier etapa, el pipeline se detiene y no hay deploy.

**Definición de "deploy":** la imagen de la API se reconstruye y etiqueta con `BUILD_NUMBER`, se
recrea el contenedor de producción y se verifica que `/health` responda 200. Se deja evidencia
en el log de Jenkins.

---

# 6. RIESGOS TÉCNICOS Y MITIGACIONES

| # | Riesgo | Mitigación | Fase |
|---|---|---|---|
| R1 | GitHub no puede alcanzar Jenkins local para el webhook | smee.io + servicio `smee` en el compose (D8) | F2 |
| R2 | Jenkins no puede ejecutar Docker | Imagen propia de Jenkins con Docker CLI y compose plugin, socket montado | F2 |
| R3 | El deploy reinicia Jenkins | Perfil o proyecto separado; el deploy solo levanta servicios de la app | F2 |
| R4 | Bind mounts rotos por el socket | Volúmenes con nombre | F2 |
| R5 | Builds lentos por recargar datos | Ingesta idempotente (D3); objetivo de menos de 5 min por build | F4 |
| R6 | Tests lentos o frágiles por depender del dataset | Datos semilla pequeños (cientos de puntos) con resultados conocidos | F3/F7 |
| R7 | Imágenes Bitnami no disponibles | `apache/spark` oficial (D4) | F2 |
| R8 | Versiones incompatibles de Spark, Scala y el conector | Fijar versiones; probar lectura y escritura el primer día de la F6 | F6 |
| R9 | RAM insuficiente en el portátil | Límites por servicio; Docker Desktop con 10–12 GB; muestra de ~1–2 M registros | F2 |
| R10 | Scripts rotos por CRLF en Windows | `.gitattributes` con `eol=lf` (hecho) | F1 |
| R11 | Orden lat/lon invertido | Test automático que verifica un punto conocido | F3 |
| R12 | Falla la red o el túnel en la sustentación | Imágenes ya descargadas, datos precargados, túnel probado ese día | F11 |
| R13 | Historial de commits desigual | Ramas por dueño y PRs revisados por otro integrante | Todas |
| R14 | Acusación de copia | Citar fuentes en el README | Todas |

---

# 7. DATASET — CANDIDATOS INVESTIGADOS (30-sep-2026)

Los ejemplos del enunciado (US Accidents, Chicago Crime, taxis de NY) se descartan porque es
probable que otros equipos ya los hayan pedido.

| # | Dataset (slug de Kaggle) | Tamaño reportado | Geo | Tiempo | Valoración |
|---|---|---|---|---|---|
| 1 | NYC Motor Vehicle Collisions – Crashes (`muzammilrizvi1/motor-vehicle-collisions-crashes`) | **1.972.121 filas, 29 columnas, 420.704.526 bytes** (medido 1-oct-2026) | LATITUDE/LONGITUDE numéricas | CRASH DATE + CRASH TIME | **Verificado.** 226.028 coordenadas nulas, 4.115 puntos `(0,0)`, 106 fuera de rango y 1.741.872 válidas. Buen tamaño para portátiles. |
| 2 | 1.88 Million US Wildfires (`rtatman/188-million-us-wildfires`) | 1.880.465 filas, SQLite | LATITUDE/LONGITUDE | DISCOVERY_DATE (fecha juliana) | **Respaldo.** Tema poco común y cobertura nacional. Exige leer SQLite y convertir fechas julianas. |
| 3 | Uber Pickups NYC (`fivethirtyeight/uber-pickups-in-new-york-city`) | ~4,5 M (2014) | Lat/Lon | Date/Time | Datos muy limpios, así que hay poco que justificar en la limpieza. Además es muy parecido al ejemplo de taxis de NY. No recomendado. |
| 4 | Crime in Los Angeles (`cityofla/crime-in-los-angeles`) | 2010–2017, más de 1 M | Campo `Location` como texto "(lat, lon)" | Date Occurred | Posible, pero exige parsear texto. Es parecido a Chicago Crime. |

El dataset principal fue verificado con `python scripts/verificar_dataset.py <slug>`. La
evidencia quedó en `docs/evidencias/`. El siguiente paso es enviar el registro al docente.

---

# 8. ESTADO ACTUAL

## Completado
- WSL 3.0.1 y Docker Desktop están instalados. Verificación desde la PowerShell normal:
  Docker 29.8.1, Docker Compose 5.5.1 y `docker run --rm hello-world` exitoso. El entorno aislado
  de Codex no puede ejecutar el CLI ubicado en `AppData` por una política de Windows, así que los
  comandos reales de Docker deben ejecutarse en la terminal normal del usuario.
- Requisitos analizados; arquitectura v2 definida; decisiones D1–D6 y D8–D12 documentadas.
- Candidatos de dataset investigados (sección 7).
- **F0 técnico:** dataset principal descargado y perfilado; cumple el mínimo con 1.972.121
  registros. Evidencia JSON generada. El perfilador separa nulos de valores no numéricos,
  conserva el total cuando faltan columnas geográficas y cierra correctamente SQLite.
- **Pruebas del perfilador:** 5 pruebas sintéticas sobre detección de columnas, clasificación
  exclusiva de registros, ausencia de lat/lon, lectura CSV por bloques y selección/cierre de
  la tabla SQLite. Todas pasan con `python -m unittest discover -s tests`.
- **Validación estática de F2 (no sustituye el Gate 2):** los módulos Python compilan; la API
  obtiene `4 passed, 1 skipped`; con `FORZAR_FALLO=true` obtiene `1 failed, 4 passed`, que es el
  resultado esperado para bloquear el despliegue; `docker-compose.yml` es YAML válido y define
  11 servicios. Evidencia en `docs/evidencias/validacion_estatica_2026-10-01.md`.
- **F1 local:** base del repositorio (estructura, `.gitignore`, `.gitattributes`, `.env.example`,
  README, `docs/decisiones.md`, `scripts/verificar_dataset.py`). Git fue iniciado localmente en
  la rama `main`; `.venv/`, `data/` y `__pycache__/` aparecen ignorados. Falta el primer commit,
  crear el repositorio remoto. La auditoría previa encontró 44 archivos
  candidatos: incluye el JSON de evidencia y excluye datos, entorno virtual y token. El sandbox
  de Codex no permite escribir en `.git`, por lo que `git add` y el commit deben hacerse desde
  la terminal normal del usuario.
- **F1 remoto:** repositorio público creado en
  `https://github.com/sBoterino/big-data-geoespacial`. Git para Windows 2.53.0 fue instalado.
  Como el sandbox no pudo usar las credenciales HTTPS de Windows, la publicación se hizo con la
  conexión oficial de GitHub: `main` contiene los 45 archivos auditados en el commit
  `eaea454cca7a26ece822aad87ef6bcbdcb8dc113`. No se publicaron `data/`, `.venv/`, el token de
  Kaggle ni cachés. Falta invitar colaboradores. El ruleset `proteger-main` se preparó pero no
  se guardó: el equipo decidió no activarlo porque no es un requisito explícito; ramas, PR y
  revisión siguen siendo obligatorios como práctica de trabajo.
- **F1 local sincronizada:** copia normal clonada desde GitHub; `main` sigue a `origin/main` y
  quedó limpia. Git 2.56.0 funciona. La clonación requirió el backend TLS OpenSSL porque el
  almacén de credenciales de Windows no está disponible dentro del entorno aislado.
- **Registro académico:** borrador con cifras reales y los tres integrantes creado en
  `docs/registro_dataset_docente.md`. Falta enviarlo al docente.
- **F2, archivos base:**
  - `docker-compose.yml`: mongodb, spark-master, spark-worker, dask-scheduler, dask-worker-1,
    dask-worker-2, api; `dask-job` en el perfil `jobs`; `jenkins` y `smee` en el perfil `ci`.
  - Imágenes: `api/`, `mongo/`, `spark/` (apache/spark 3.5.3 con conector 10.4.0) e
    `ingest/` (Dask 2024.12.1).
  - `jenkins/Dockerfile` con Docker CLI y plugins; `jenkins/ci-env.sh`.
  - `Jenkinsfile`: checkout → build → pytest → Kaggle → levantar → integración → staging +
    smoke → deploy; parámetro `FORZAR_FALLO`.
  - API Flask con `/health` y 4 pruebas + prueba trampa (verificadas aquí con Flask).
  - `ingest/check_cluster.py` y `spark/jobs/check_conexion.py` (pruebas de integración).
  - `scripts/smoke_api.sh` (probado contra Flask local, en el caso exitoso y en el de falla).
  - `docs/guia_fase2.md`: guía paso a paso con checklist del Gate 2 y tabla de problemas.
  - `docs/plan_paso_a_paso.md`: plan día por día hasta el 9-oct, con especificaciones de F4–F8,
    simulacro y banco de preguntas.
  - Compose: Spark monta `kaggle_data` (benchmark sobre el mismo Parquet) y hay un
    `spark-worker-2` en el perfil `bench`.
- **F2, arranque base verificado:** `docker compose config --quiet` y
  `docker compose up -d --build` terminaron bien; BuildKit completó 61/61 pasos en 64,3 s.
  MongoDB, Spark master, Spark worker, Dask scheduler, dos workers de Dask y la API iniciaron.
  `/health` devolvió `mongo=ok` y `status=ok`; los paneles de Dask y Spark respondieron HTTP 200.
  Dask confirmó dos workers y 300 documentos semilla. Spark leyó los 300, produjo los conteos
  120/80/100 y escribió tres resultados en `spark_check`, verificados directamente en MongoDB.
  Jenkins 2.541.3 se construyó e inició en el puerto 8080; el asistente inicial y el usuario
  administrador quedaron completados.
- **F2, primer pipeline completo:** se revocó el token de Kaggle que había aparecido en una
  captura y se creó uno nuevo llamado `jenkins-bdgeo`. Jenkins guarda las credenciales globales
  `mongo-root` y `kaggle-api-token` sin revelar sus valores. El job `bdgeo-main` usa el repositorio
  público, rama `*/main`, `Jenkinsfile` y el trigger `GitHub hook trigger for GITScm polling`.
  El build #1 sobre el commit `a185f2bf1441184c25ec874c5d8639779619a9e3` terminó en SUCCESS
  en 1 min 52 s: 4 tests pasaron y 1 se omitió; Kaggle listó el CSV de 420.704.526 bytes; Dask
  confirmó 2 workers, media 0,5000 y 300 documentos; Spark leyó 300 con grupos 120/80/100;
  staging respondió `version=1-staging`; producción respondió `version=1`. Evidencia textual en
  `docs/evidencias/jenkins_build_1_2026-10-04.md`; la captura de Jenkins se conservó en la sesión.
- **F2, webhook conectado:** canal de smee creado y guardado solo en `.env`; el contenedor
  `bdgeo-smee-1` quedó conectado y reenvía a `http://jenkins:8080/github-webhook/`. GitHub creó
  el webhook activo para eventos `push` con `application/json`; el ping llegó a Jenkins con
  respuesta HTTP 200. Evidencia en `docs/evidencias/webhook_2026-10-04.md`.
- **F2, Gate 2 aprobado:** el push documental del commit `6153d80` generó automáticamente el
  build #2 y `/health` cambió a `version=2`. Después, el build parametrizado #3 ejecutó
  `FORZAR_FALLO=true`: pytest obtuvo 1 fallo intencional y 4 pruebas aprobadas; Kaggle, servicios,
  integración, staging y despliegue fueron omitidos. Jenkins terminó en `FAILURE` y producción
  continuó sana en `version=2`. No hay `.env`, `kaggle.json` ni `access_token` rastreados; tampoco
  se detectaron tokens `KGAT_...` reales en el historial. Evidencia en
  `docs/evidencias/gate2_cierre_2026-10-04.md`.
- **F3, avance:** `mongo/init/01-init.js` (validador GeoJSON e índices 2dsphere),
  `02-semilla.js` (300 puntos) y `semilla_esperados.json`.
- **F4, implementación en rama:** `ingest/descarga.py` descarga con la API de Kaggle y valida su
  caché; `limpieza.py` aplica R1–R6 en orden y construye GeoJSON; `pipeline_ingesta.py` coordina
  dos workers, deduplica globalmente, carga MongoDB por lotes, recrea índices, exporta Parquet y
  registra `ingesta_meta`. Jenkins construye y ejecuta la imagen de tests y añade la etapa
  `Ingesta (idempotente)`. Solo el job `bdgeo-main` puede desplegar; un job de rama usa etiquetas
  `validation-*`, procesa 50.000 filas y valida sin modificar producción; `bdgeo-main` conserva
  `INGEST_MAX_ROWS=0` para la carga completa. `docker compose config --quiet` pasó; la imagen de
  pruebas se construyó y obtuvo 3 pruebas aprobadas en 0,29 s. Falta muestra real, idempotencia y
  carga completa.
- **F4, muestra #1:** Kaggle confirmó el CSV de 420.704.526 bytes, API obtuvo 4 pruebas aprobadas,
  ingesta obtuvo 3 y Dask conectó 2 workers. La deserialización falló porque el scheduler no podía
  importar `limpieza.py`; el pipeline bloqueó las etapas posteriores. Se corrigió distribuyendo el
  módulo con `Client.upload_file`, corrección confirmada en el build #2.
- **F4, muestra #2:** `upload_file` funcionó y se reutilizó la caché. Falló antes de escribir en
  MongoDB porque `map_partitions(len).sum()` intentó reducir un entero como serie al existir una
  sola partición. Se creó `contar_filas`, que suma las longitudes materializadas, con pruebas para
  una y varias particiones. Corrección confirmada en el build #3.
- **F4, muestra #3 aprobada:** 5 pruebas de ingesta pasaron. De 50.000 filas, R1 descartó 3.888,
  R2 descartó 269 y R3–R6 no descartaron filas; MongoDB recibió 45.843 documentos en 5,684 s.
  Dask confirmó 2 workers y Spark conservó los controles 120/80/100. Staging y despliegue se
  omitieron por condición y el build terminó `SUCCESS` sin modificar producción.
- **F4, idempotencia aplazada por red:** builds #4 y #6 fallaron antes de las pruebas por DNS de
  Docker Hub y Maven. No modificaron datos. Spark ahora guarda sus JAR en una capa `RUN` cacheable
  y Jenkins reintenta cada construcción hasta tres veces con espera incremental.
- **F4, idempotencia aprobada:** build #7 terminó `SUCCESS`. Encontró 45.843 documentos para la
  muestra de 50.000 y omitió descarga, limpieza y reinserción. Las integraciones Dask/Spark pasaron,
  staging/despliegue se omitieron y producción quedó intacta.
- **F4, auditoría MongoDB aprobada:** conteo 45.843; documento `_id=4456314` con GeoJSON
  `Point [-73.8665, 40.667202]` y fecha BSON; índices `_id_`, `fecha_1` y `location_2dsphere`.
- **F4, carga completa aprobada:** PR #1 fusionado; `bdgeo-main` #6 procesó 1.972.121 filas en
  6 particiones, descartó 230.293 mediante R1–R4 e insertó 1.741.828 documentos en 57,435 s.
  Dask/Spark, staging y smoke tests pasaron; API v6 fue desplegada.
- **F4, auditoría completa aprobada:** MongoDB contiene 1.741.828 documentos; muestra real
  `_id=4486564`, `Point [-74.00231, 40.59662]`, fecha BSON e índices `_id_`, `fecha_1` y
  `location_2dsphere`. Reporte persistido en `docs/evidencias/`.

## Pendiente
- [ ] F0: enviar al docente el registro del dataset ya verificado.
- [ ] F1: invitar colaboradores y completar la asignación de roles de la sección 10.
- [x] Entorno: Docker Desktop, Docker Compose y `hello-world` verificados.
- [x] **F2: Gate 2 aprobado de punta a punta, incluido webhook y bloqueo del despliegue.**
- [x] **F4: muestra de 50.000 filas aprobada.**
- [x] **F4: idempotencia demostrada en el build #7.**
- [x] **F4: GeoJSON e índices verificados directamente en la muestra.**
- [x] **F4: PR #1 fusionado y carga completa aprobada.**
- [ ] **F4: confirmar idempotencia sobre los 1.741.828 documentos y cerrar Gate 4.**

**Estado oficial: F0 verificación completa, falta enviar el registro · F1 en curso · F2 aprobada · F4 carga completa aprobada, falta cierre idempotente.**

---

# 9. CALENDARIO Y FASES

Los gates se evalúan **por componente**. Las fases F3–F6 avanzan **en paralelo** en ramas
distintas; una rama solo se integra a `main` cuando pasa su gate, y el pipeline lo hace cumplir.

| Fecha | Fase | Gate (criterio verificable) |
|---|---|---|
| 30-sep | **F0 Definición** | Dataset verificado con el script y registrado con el docente; D1–D6 cerradas |
| 30-sep | **F1 Repositorio y entorno** | Repo en GitHub con la base, flujo de ramas y PR acordado, todos clonan y tienen `.env` local |
| 1–2 oct | **F2 Esqueleto de infraestructura y CI/CD** | `docker compose up` levanta Mongo, Spark (1+1), Dask (1+2), Flask y Jenkins; los servicios se ven entre sí; push → webhook → Jenkins → build → pytest → deploy de `/health`; **un test que falla a propósito bloquea el deploy** (con captura) |
| 2–3 oct | **F3 Modelo MongoDB y datos semilla** | Colección con GeoJSON válido, 2dsphere creado, datos semilla cargados y consulta `$near` manual correcta |
| 3–5 oct | **F4 Ingesta Dask** (paralela) | Descarga automática desde el pipeline; al menos 1 M de documentos limpios cargados; conteos antes y después de cada regla de limpieza registrados; segunda ejecución sin recarga |
| 3–5 oct | **F5 Consultas y API** (paralela, con datos semilla) | `/near`, `/within` y `/spark-results` más un endpoint con `$geoNear`; parámetros validados; errores 400 claros; tiempos medidos |
| 3–5 oct | **F6 Spark** (paralela) | Lee desde Mongo con el conector; agregados por grilla o geohash y por hora/día/mes guardados en colecciones nuevas; resultados coherentes con una verificación cruzada simple |
| 5–6 oct | **F7 Pruebas completas** | Tests unitarios y smoke tests de API en el pipeline; tiempo total del build menor a 5 min sin recarga |
| 6 oct | **F8 Benchmark Dask vs Spark** | Misma agregación sobre Parquet, 2 configuraciones × 2 motores × 3 repeticiones; tiempos y memoria en `docs/evidencias/` |
| 7 oct | **F9 Reproducibilidad (y Leaflet opcional)** | Clon limpio en **otro computador** levantado solo con el README |
| 7 oct | **F10 Documentación** | README completo; informe de 10 páginas o menos con arquitectura, decisiones, consultas y benchmark |
| 8 oct | **F11 Simulacro de sustentación** | Cada integrante hace un cambio en vivo (endpoint nuevo o polígono nuevo) con push → Jenkins → deploy, y responde preguntas de todo el sistema |
| 9 oct | **Entrega y sustentación** | — |

**Colchón:** si algo se atrasa, se recorta primero Leaflet, luego repeticiones del benchmark.
Nunca se recortan el pipeline ni los tests.

---

# 10. ORGANIZACIÓN DEL EQUIPO (completar)

**Integrantes:**

- Juan Guillermo Echeverri
- Sebastián Botero Velásquez
- Santiago Villamizar Mejía

**Cuenta propietaria prevista en GitHub:** `sBoterino`  
**Repositorio previsto:** público, `sBoterino/big-data-geoespacial`

| Componente | Dueño | Revisor de PR |
|---|---|---|
| Infraestructura (Compose) + Jenkins/CI | _por asignar_ | _por asignar_ |
| Ingesta Dask + limpieza | _por asignar_ | _por asignar_ |
| Spark + benchmark | _por asignar_ | _por asignar_ |
| MongoDB + consultas + API Flask + tests | _por asignar_ | _por asignar_ |

Reglas del equipo:
- Ramas `feature/<componente>` y PR hacia `main` con al menos una revisión.
- Cada integrante hace commits de su propia autoría, porque el historial se revisa.
- Todos revisan PRs de componentes ajenos, para poder explicar cualquier parte en la sustentación.

---

# 11. FUERA DE ALCANCE

Hadoop, Kafka, Kubernetes, Machine Learning, Power BI, QGIS y MongoDB Atlas.
Leaflet solo el 7-oct y solo si todo lo obligatorio pasó sus gates.

---

# 12. CRITERIO DE PROYECTO TERMINADO

- [x] Docker Compose levanta MongoDB, Spark, Dask, Flask, Jenkins y smee desde el mismo archivo.
- [x] El acceso a Kaggle es automático en el pipeline, con credencial de Jenkins y sin secretos en GitHub.
- [ ] Dask limpia y carga por lotes; la limpieza está justificada con conteos.
- [ ] MongoDB tiene GeoJSON válido `[lon, lat]` e índice 2dsphere.
- [ ] Spark agrega vía el conector y guarda los resultados en colecciones nuevas.
- [ ] `$near`, `$geoWithin` y `$geoNear` funcionan con parámetros.
- [ ] Flask expone los 3 endpoints mínimos.
- [x] Hay webhook de GitHub hacia Jenkins, y un test fallido bloquea el deploy (con evidencia).
- [ ] La comparación Dask vs Spark tiene mediciones propias.
- [x] Hay README, `docker-compose.yml` y `Jenkinsfile` en el repositorio.
- [ ] El informe tiene 10 páginas o menos.
- [ ] El historial de commits refleja a todos los integrantes.
- [ ] Todos pueden hacer un cambio en vivo y explicar el sistema completo.

---

# 13. INSTRUCCIONES PARA LA IA QUE CONTINÚE

1. Leer este archivo completo y `docs/decisiones.md` antes de actuar.
2. El `.docx` del enunciado manda sobre este archivo.
3. No reabrir decisiones aprobadas (D1–D6) salvo que el docente o el equipo lo pidan.
4. No asumir que el dataset está aprobado hasta que D7 figure como **Aprobada**.
5. Respetar los gates por componente; no integrar a `main` sin pasar el gate.
6. Priorizar lo evaluable sobre los extras; fijar versiones de todas las imágenes y librerías.
7. Mantener los secretos fuera de GitHub.
8. Guardar evidencia (logs, capturas, JSON de métricas) en `docs/evidencias/` para el informe.
9. Explicar cada paso antes de ejecutarlo cuando el usuario trabaja de forma interactiva.
10. Si una decisión cambia la arquitectura, detenerse, validarla y registrarla en `docs/decisiones.md`.
11. La meta es un sistema reproducible y demostrable en vivo, no que funcione en un solo portátil.
12. Actualizar `docs/guia_sustentacion.md` con cada función, decisión, evidencia o pregunta nueva
    que pueda aparecer en la sustentación.

---

# 14. PRÓXIMA ACCIÓN EXACTA

> **El plan operativo día por día está en `docs/plan_paso_a_paso.md`.** Seguirlo en orden; las especificaciones de F4–F8 de ese archivo son las que se entregan a la IA para generar el código.

1. Enviar al docente el texto ya completado en `docs/registro_dataset_docente.md`. No esperar
   respuesta para continuar; D7 sigue como verificada pero no aprobada hasta el registro.
2. Asignar los cuatro componentes de la sección 10 entre los tres integrantes y definir revisores.
   Cada integrante debe configurar su propio `user.name` y `user.email` antes de contribuir.
3. Invitar a los otros dos integrantes en GitHub. No activar el ruleset de `main`; exigir ramas,
   pull request y una revisión como norma del equipo y conservar la evidencia de los PR.
4. Arrancar **en paralelo** las siguientes fases, cada una en su rama y con PR:
   - F4: ingesta Dask. Requiere el JSON de la verificación del dataset.
   - F5: consultas y API sobre `eventos_semilla`.
   - F6: agregaciones Spark, partiendo de `check_conexion.py`.
5. Cada error: copiar el mensaje exacto y la salida de `docker compose ps` o `docker compose logs <servicio>`.

---

# 15. REGLA DE ACTUALIZACIÓN

Al cerrar cada fase o gate, actualizar:
- la sección 8 (estado);
- la sección 3 (y `docs/decisiones.md` si hay decisiones nuevas);
- la evidencia en `docs/evidencias/`;
- `docs/guia_sustentacion.md` cuando exista contenido demostrable o una pregunta nueva;
- la sección 14 (próxima acción);
- el número de versión y la fecha del encabezado.
