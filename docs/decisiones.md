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
