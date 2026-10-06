# Registro de decisiones técnicas

Cada decisión queda con su contexto, alternativas y justificación. Este archivo alimenta
directamente la sección "Decisiones tomadas" del informe técnico.

Estados: **Aprobada** (vigente), **Propuesta** (pendiente de validar), **Reemplazada**.

---

## D1 — MongoDB en contenedor Docker, no MongoDB Atlas
**Estado:** Aprobada (30-sep-2026)

**Contexto.** El enunciado dice que la solución "se orquesta con Docker Compose y debe incluir,
como mínimo… MongoDB", que el sistema debe levantarse "con un solo comando" y "en otro equipo
sin pasos manuales ocultos".

**Alternativas.** MongoDB Atlas (nube) o MongoDB oficial (`mongo`) como servicio de Compose.

**Justificación.**
- Cumple literalmente el requisito de que MongoDB esté dentro de Docker Compose.
- El tier gratuito de Atlas (M0) tiene un límite de 512 MB. Un millón o más de documentos GeoJSON
  con índice 2dsphere, más las colecciones de resultados de Spark, puede superarlo.
- La latencia de red a Atlas contaminaría el benchmark de Spark leyendo desde MongoDB.
- La sustentación en vivo no dependería de la red del salón para acceder a los datos.

---

## D2 — Esqueleto funcional de CI/CD primero
**Estado:** Aprobada (30-sep-2026)

**Contexto.** El docente advierte que Jenkins es la parte que más problemas da y recomienda no
dejarlo para el final. Quedan 9 días.

**Decisión.** Antes de implementar la lógica de datos, se construye un pipeline completo pero
mínimo: push → webhook → Jenkins → build → pytest → deploy de un Flask con `/health`. Luego
cada componente se incorpora sobre ese pipeline que ya funciona.

---

## D3 — Ingesta idempotente con caché de descarga
**Estado:** Aprobada (30-sep-2026)

**Contexto.** Si cada build descargara el dataset y recargara MongoDB, un cambio pequeño
tardaría decenas de minutos, también durante la sustentación.

**Decisión.** La descarga desde Kaggle sigue automatizada en el pipeline, pero se guarda en un
volumen Docker con nombre. La carga se omite si la colección ya contiene los datos esperados.
El parámetro `FORCE_RELOAD` del pipeline permite forzarla.

---

## D4 — Imágenes oficiales de Apache Spark con el conector incluido
**Estado:** Aprobada (30-sep-2026)

**Contexto.** Muchos tutoriales usan imágenes de Bitnami, que dejaron de estar disponibles
gratuitamente en 2025.

**Decisión.** Se usa la imagen oficial `apache/spark` con versiones fijas. El jar del MongoDB
Spark Connector se incluye en la imagen durante el build, en vez de descargarse con
`--packages` en cada ejecución.

---

## D5 — Benchmark Dask vs Spark sobre una fuente común
**Estado:** Aprobada (30-sep-2026)

**Decisión.** Ambos motores ejecutan la misma agregación por grilla leyendo el mismo archivo
Parquet desde un volumen compartido. Así se comparan los motores y no dos formas distintas de
I/O. Las dos configuraciones de workers se definen con límites de CPU y memoria en Compose.
Cada corrida se repite 3 veces. La memoria se mide igual para ambos, muestreando `docker stats`.

---

## D6 — Leaflet como visualización opcional; QGIS descartado
**Estado:** Aprobada (30-sep-2026)

**Justificación.** El enunciado menciona Leaflet como opcional y dice que "suma a la
presentación". Una página estática que consuma la API toma pocas horas. QGIS no aparece en el
enunciado y conectarlo a MongoDB cuesta más. Solo se hace si sobra tiempo el 7-oct.

---

## D7 — Dataset
**Estado:** Verificada técnicamente (pendiente de registro con el docente)

**Primera opción:** NYC Motor Vehicle Collisions – Crashes
(`muzammilrizvi1/motor-vehicle-collisions-crashes`). La API de Kaggle y el perfilador propio
confirmaron 1.972.121 registros, 29 columnas y 420.704.526 bytes el 1-oct-2026. De ellos,
226.028 tienen coordenadas nulas, 4.115 corresponden a `(0,0)`, 106 están fuera de rango y
1.741.872 tienen coordenadas válidas. Estos defectos reales justifican las reglas de limpieza.
**Respaldo:** 1.88 Million US Wildfires (`rtatman/188-million-us-wildfires`).

Ver la sección 7 de CONTEXT.md para la comparación y
`docs/evidencias/verificacion_muzammilrizvi1__motor-vehicle-collisions-crashes.json` para la
medición. Pasa a **Aprobada** cuando el equipo envíe el registro al docente y este no informe
que el dataset ya fue tomado por otro equipo.

---

## D8 — Webhook vía smee.io en lugar de ngrok
**Estado:** Aprobada (30-sep-2026)

**Contexto.** GitHub necesita una URL pública para el webhook y Jenkins corre en un portátil.

**Justificación.** Con ngrok, Jenkins quedaría accesible desde internet. Como Jenkins controla
el Docker del host a través del socket, una cuenta débil equivaldría a entregar el computador.
Con smee.io, un cliente local (servicio `smee` del perfil `ci`) recibe los eventos y los reenvía
a `http://jenkins:8080/github-webhook/` por la red interna, sin abrir ningún puerto.

---

## D9 — Jenkins corre como root dentro de su contenedor
**Estado:** Aprobada (30-sep-2026)

**Contexto.** Jenkins necesita usar el Docker del host (docker-outside-of-docker). En Docker
Desktop el socket pertenece a root.

**Justificación y riesgo.** Es la forma más confiable en Windows y macOS. El riesgo se acepta
por ser un entorno local académico y queda mitigado con D8 (Jenkins no se expone a internet) y
un usuario administrador con contraseña fuerte. En un entorno real se usarían agentes dedicados
o un grupo con el GID del socket.

---

## D10 — Definición de "despliegue": staging, smoke tests y promoción
**Estado:** Aprobada (30-sep-2026)

**Decisión.** Cada build genera la imagen `bdgeo-api:<BUILD_NUMBER>`. La etapa de staging la
ejecuta como un contenedor temporal en la misma red y corre `scripts/smoke_api.sh` contra ella.
Solo si pasa, la etapa de despliegue recrea el servicio `api` con esa imagen y vuelve a
verificarlo. Si algo falla antes, la versión anterior sigue sirviendo.

**Justificación.** Así "levantar servicios", "pruebas contra la API" y "despliegue" son etapas
distintas y verificables, como pide el enunciado. `/health` muestra la versión desplegada, lo
que en la sustentación prueba que el cambio llegó a producción. Se conservan las últimas 5
imágenes para poder volver atrás.

---

## D11 — Datos semilla deterministas para las pruebas
**Estado:** Aprobada (30-sep-2026)

**Decisión.** La colección `eventos_semilla` tiene 300 puntos generados con semilla fija
(`scripts/generar_semilla.py`), en tres grupos de NYC con conteos conocidos:
120 puntos a menos de 1 km de Times Square, 80 a menos de 500 m del Brooklyn Bridge y 120
dentro del polígono de Midtown. Las pruebas de consultas y de Spark comparan contra
`mongo/init/semilla_esperados.json`.

**Justificación.** Las pruebas son rápidas, deterministas e independientes del dataset
completo (riesgo R6). Además verifican el orden `[lon, lat]` (riesgo R11).

---

## D12 — Validador `$jsonSchema` en las colecciones geoespaciales
**Estado:** Aprobada (30-sep-2026)

**Decisión.** MongoDB rechaza documentos cuyo `location` no sea un `Point` GeoJSON con
`[longitud, latitud]` numéricos y dentro de rango. Es una segunda línea de defensa después de
la limpieza en Dask, y aporta al criterio "GeoJSON válido" de la rúbrica.

---

## D13 — Grilla de 0,005° como unidad espacial de agregación en Spark
**Estado:** Aprobada (Gate 6, `bdgeo-main` #9, 5-oct-2026)

**Contexto.** El enunciado pide agregaciones espaciales "por celda de una grilla o por geohash"
e identificar zonas de alta concentración.

**Alternativas.** Geohash de precisión 6 (≈ 1,2 km × 0,6 km) o grilla regular en grados.

**Decisión.** Grilla regular: `celda_x = floor(lon / 0.005)` y `celda_y = floor(lat / 0.005)`.
En la latitud de NYC cada celda mide ≈ 555 m (norte-sur) × 420 m (este-oeste). El tamaño es
parámetro (`--celda`), así que puede cambiarse en la sustentación sin tocar el código.

**Justificación.**
- Se calcula con dos operaciones aritméticas, sin librerías externas en la imagen de Spark.
- Cada celda se guarda también como polígono GeoJSON, lo que permite contrastarla con
  `$geoWithin` en MongoDB (D15) y dibujarla en un mapa.
- ~500 m es una escala útil para hablar de "intersecciones o tramos peligrosos"; el geohash 6
  mezcla zonas demasiado distintas en Manhattan.
- Es la misma operación que se usará en el benchmark Dask vs Spark (D5).

---

## D14 — Proyección en MongoDB antes de leer con Spark
**Estado:** Aprobada (Gate 6, `bdgeo-main` #9, 5-oct-2026)

**Decisión.** Los jobs leen con la opción `aggregation.pipeline` del MongoDB Spark Connector y
un `$project` que deja solo lon, lat, hora, día, mes, heridos, muertos y borough.

**Justificación.** MongoDB filtra los campos antes de enviarlos por la red, de modo que Spark
no transfiere calles, códigos postales ni el texto de la fuente. Además resuelve en origen los
valores ausentes (`$ifNull`), lo que permite usar el mismo código sobre la semilla.

---

## D15 — Verificación de los resultados de Spark en cada build
**Estado:** Aprobada (Gate 6, `bdgeo-main` #9, 5-oct-2026)

**Decisión.** `verificar_resultados.py` comprueba sumas de control (grilla, hora, día y mes
deben sumar el total de documentos) y cruza el hotspot #1 con un `$geoWithin` en MongoDB
(tolerancia ±0,5 %). Cada build de Jenkins corre los jobs y la verificación sobre la semilla,
con salidas `spark_semilla_*`, para no sobrescribir los resultados reales que sirve la API.
Los datos reales se recalculan solo en `bdgeo-main`, con `EJECUTAR_SPARK` o si aún no
existen resultados.

**Justificación.** Cumple el criterio "resultados espaciales coherentes y verificables" con una
prueba automática que detiene el pipeline, y mantiene el build normal en pocos minutos.

---

## D16 — Operación del benchmark: conteo por celda sin sumar heridos
**Estado:** Aprobada (revisión del PR #5, 6-oct-2026)

**Contexto.** El plan proponía "contar por celda y sumar los heridos". El Parquet que escribe
la ingesta (`PARQUET_COLUMNAS` en `ingest/pipeline_ingesta.py`) no incluye `personas_heridas`.

**Alternativas.** Agregar la columna al Parquet, lo que obliga a modificar la ingesta y a
recargar con `FORCE_RELOAD`, o medir solo el conteo.

**Decisión.** El benchmark cuenta puntos por celda y obtiene el top 20 y el total de filas.

**Justificación.** La parte costosa es la lectura, el cálculo de celdas y el shuffle del
`groupBy`; una suma adicional no cambia la comparación. Se evita tocar la ingesta, que ya está
aprobada (Gate 4), a cuatro días de la entrega.

---

## D17 — Particiones de shuffle de Spark iguales al número de núcleos
**Estado:** Aprobada (revisión del PR #5, 6-oct-2026)

**Contexto.** Spark usa por defecto `spark.sql.shuffle.partitions = 200`, un valor pensado para
clústeres grandes. En una prueba local con 200.000 filas y 2 núcleos, el `groupBy` generó 200
tareas diminutas y tardó 9,5 s; con 2 particiones tardó 3,7 s.

**Decisión.** `bench_spark.py` fija las particiones de shuffle en el número de núcleos del
clúster (2 en la config A, 4 en la B). El valor queda registrado en la salida y puede
cambiarse con `--shuffle`.

**Justificación.** Dask no tiene ese sobrecosto por defecto: su `groupby` produce una sola
partición de salida. Sin el ajuste se compararía la configuración por defecto y no los motores.
El ajuste se declara en el informe como parte del análisis.

---

## D18 — Prueba de volumen del benchmark con un Parquet físico ×10
**Estado:** Aprobada (revisión del PR #5, 6-oct-2026; corregida tras la revisión)

**Contexto.** Con las 1.741.828 filas reales, Dask calculó en 0,20–0,30 s y Spark en
3,8–4,7 s. Con tan poco trabajo domina el sobrecosto de coordinación, y no se puede ver cómo
cambia la comparación con más datos.

**Primer intento (descartado).** Concatenar N lecturas del mismo Parquet dentro de cada motor
(`dd.concat([base] * N)` en Dask, `unionAll` en Spark). La revisión del PR #5 lo cuestionó y la
comprobación mostró el sesgo: Dask reconoce las N lecturas como la misma tarea y lee el Parquet
una sola vez, mientras que Spark lo lee N veces.

**Decisión.** `benchmark/preparar_volumen.py` copia cada archivo del Parquet N veces a
`/data/parquet/eventos_xN` (con N = 10: 60 archivos, 295 MB, 17.418.280 filas) y verifica que
el total de filas sea exactamente N veces el original. Ambos motores leen esa carpeta como
cualquier otro Parquet. Se corre el mismo protocolo (A y B, 1 calentamiento y 3 repeticiones).

**Justificación.** Misma operación, misma fuente física y mismos recursos para los dos motores
(D5); solo cambia el volumen. Es verificable: el top 1 debe ser exactamente N veces el de ×1.
**Limitación declarada:** son filas repetidas; miden lectura y agrupación de más filas, no
datos más diversos.
