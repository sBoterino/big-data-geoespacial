# Guía viva de sustentación

Última actualización: 4-oct-2026

Fuente principal: sección 6 del enunciado del docente.

Uso: actualizar este archivo cada vez que aparezca una decisión, prueba, resultado o cambio que
pueda ser explicado o demostrado durante la sustentación.

## 1. Qué exigirá el docente

La sustentación será en vivo y con el sistema funcionando. El docente podrá:

1. Pedir una modificación puntual, por ejemplo un endpoint nuevo.
2. Pedir una consulta sobre un polígono diferente.
3. Exigir que el cambio se suba a GitHub.
4. Observar a Jenkins construir, probar y desplegar la nueva versión.
5. Hacer preguntas individuales sobre cualquier componente, sin limitarse al rol de cada persona.

Por tanto, no basta con mostrar código terminado: los tres integrantes deben poder cambiarlo,
seguir el despliegue y explicar por qué está construido así.

## 2. Qué de lo ya realizado sirve directamente

| Apartado sustentable | Estado | Evidencia actual | Qué se puede demostrar o explicar |
|---|---|---|---|
| Sistema contenedorizado funcionando | **Listo** | `docker-compose.yml`, Gate 2 | MongoDB, Spark, Dask, Flask, Jenkins y smee se comunican en la red `bdgeo-net` |
| Push de GitHub dispara Jenkins | **Listo** | Build #2, `docs/evidencias/webhook_2026-10-04.md` | GitHub envía el evento a smee; smee lo reenvía a Jenkins sin exponer Jenkins a internet |
| Jenkins construye y despliega | **Listo** | Builds #1 y #2 | Checkout, imágenes, pytest, Kaggle, servicios, integración, staging y despliegue |
| La versión nueva llegó a producción | **Listo** | `/health` mostró `version=2` | `APP_VERSION` usa el número de build para probar qué ejecución está desplegada |
| Un test fallido bloquea el despliegue | **Listo** | Build #3 y `gate2_cierre_2026-10-04.md` | Con `FORZAR_FALLO=true`, pytest falla, las etapas posteriores se omiten y producción queda en versión 2 |
| Credenciales seguras | **Listo** | Jenkins y auditoría del historial | Mongo usa `mongo-root`; Kaggle usa `kaggle-api-token`; `.env` está ignorado y no hay tokens reales en Git |
| Dask distribuido | **Validado con carga completa** | `bdgeo-main` #6 | Dos workers procesaron 1.972.121 filas en 6 particiones |
| Reglas de limpieza R1–R6 | **Validadas con carga completa** | `gate4_carga_completa_2026-10-04.md` | R1=226.028, R2=4.115, R3=106, R4=44, R5=0, R6=0; quedaron 1.741.828 documentos |
| Ingesta idempotente | **Validada con carga completa** | `bdgeo-main` #7 | Encontró 1.741.828 documentos y omitió descarga, limpieza y reinserción; `FORCE_RELOAD` permite recargar |
| Validación de ramas sin afectar producción | **Demostrada** | `bdgeo-ingesta-test` #3 | Staging y despliegue se omitieron por condición; el job terminó correctamente sin modificar producción |
| Aislamiento de datos en ramas | **Reforzado en F5** | Condición de la etapa `Ingesta (idempotente)` | Solo `bdgeo-main` puede ejecutar la ingesta; los jobs de rama no escriben en `eventos` |
| Fallo distribuido bloqueado antes de desplegar | **Demostrado** | `bdgeo-ingesta-test` #1 | Un módulo no importable en el scheduler detuvo el pipeline; integración y despliegue quedaron omitidos |
| Compatibilidad entre particiones y reducciones | **Corregida y validada** | `bdgeo-ingesta-test` #3 | Cinco pruebas y la muestra real confirmaron el conteo explícito de longitudes por partición |
| Tolerancia a fallos transitorios de descarga | **Mitigada y validada** | Builds #4/#6/#7, `Jenkinsfile`, `spark/Dockerfile` | Tres intentos con espera; el build #7 creó la capa cacheable de JAR y terminó correctamente |
| Spark conectado a MongoDB | **Listo** | `spark/jobs/check_conexion.py` | Master, worker, conector MongoDB, lectura de 300 documentos y conteos 120/80/100 |
| Agregaciones Spark (grilla, hotspots, hora, día, mes, hora×borough) | **Gate 6 cerrado** | PR #4, `bdgeo-main` #9, `fase6_logica_local_2026-10-04.md` | Siete colecciones `spark_*`; con la semilla, hotspot #1 n=57 en Spark y 57 con `$geoWithin` |
| Resultados de Spark verificables | **Automatizado** | `verificar_resultados.py`, etapa "Procesamiento Spark" | Sumas de control y cruce con MongoDB en cada build; si no cuadra, el pipeline se detiene |
| Benchmark Dask vs Spark | **Cerrado (F8)** | PR #5, `fase8_benchmark_2026-10-05.md` | 32 corridas propias, ×1 y ×10 físico, mismo top 1 en ambos motores, gráficas y limitaciones |
| Corrección metodológica del benchmark | **Documentada** | D18, `resultados_descartados.csv` | El ×10 lógico estaba sesgado (Dask leía una vez y Spark diez); se repitió con un Parquet físico |
| GeoJSON e índice 2dsphere | **Validado con carga completa** | Auditoría posterior a `bdgeo-main` #6 | Documento real `Point [-74.00231, 40.59662]`; índices `_id_`, `fecha_1` y `location_2dsphere` |
| Modificación puntual en vivo | **Preparación lista; práctica pendiente** | Pipeline operativo | Endpoints y Spark ya existen; falta ensayar el cambio con rama, PR, merge y Jenkins (simulacro del 8-oct) |
| Consulta con otro polígono | **Validada con semilla y datos reales** | `fase5_semilla_2026-10-04.md`, `fase5_datos_reales_2026-10-04.md` | `/within` recibe cualquier `Polygon` GeoJSON válido; cambiar el polígono no exige cambiar código |
| Pruebas de consultas API | **Unitarias e integración real aprobadas** | Evidencias F5 en `docs/evidencias/` | 22 pruebas, conteos semilla 120/120/120 y consultas sobre 1.741.828 documentos; falta Jenkins |
| Rendimiento de consultas | **Medido** | `fase5_datos_reales_2026-10-04.md` | Promedios calientes: `$near` 13,493 ms, `$geoWithin` 99,531 ms y `$geoNear` simple 182,280 ms; agrupado 1.786,176 ms |
| Dominio integral de los tres miembros | **Pendiente de ensayo** | — | Cada integrante debe practicar preguntas y hacer cambios fuera de su componente principal |

## 3. Demostración que ya podemos hacer

### Flujo exitoso

1. Se integra un cambio a `main`.
2. GitHub envía un evento `push` al canal de smee.
3. smee reenvía el evento a `http://jenkins:8080/github-webhook/`.
4. Jenkins obtiene el `Jenkinsfile` versionado y ejecuta el pipeline.
5. La imagen nueva se prueba primero en un contenedor temporal de staging.
6. Solo si todo pasa, Jenkins recrea la API de producción.
7. `/health` muestra el número del build desplegado.

### Flujo con error

1. El build #3 se ejecutó con `FORZAR_FALLO=true`.
2. Pytest produjo 1 fallo intencional y 4 pruebas aprobadas.
3. Jenkins omitió Kaggle, integración, staging y despliegue.
4. El build terminó en `FAILURE`.
5. `/health` continuó mostrando `version=2`.

Esta es evidencia directa del criterio: **si una prueba falla, no se despliega**.

## 4. Preguntas individuales que ya pueden responderse

### ¿Cómo se comunican los servicios?

Docker Compose crea la red `bdgeo-net`. Los contenedores usan nombres de servicio, por ejemplo
`mongodb`, `spark-master` y `jenkins`, en lugar de `localhost`. Los puertos publicados se usan
desde el computador anfitrión; entre contenedores se usan los puertos internos.

### ¿Por qué hay un master y un worker de Spark?

El master administra los recursos del clúster y asigna trabajo. El driver construye el plan de
ejecución y el worker aloja los executors que procesan las particiones. La prueba actual confirmó
que el worker se registra y que Spark lee y escribe en MongoDB mediante el conector.

### ¿Por qué Dask tiene un scheduler y dos workers?

El scheduler organiza el grafo de tareas y reparte las particiones. Los dos workers realizan el
cálculo. `check_cluster.py` comprueba que ambos están conectados y ejecuta una media distribuida.

### ¿Cómo se justifican técnicamente las reglas de limpieza?

R1 elimina coordenadas nulas o no numéricas porque no forman un punto. R2 elimina `(0,0)` porque
es un valor centinela fuera de NYC. R3 aplica los rangos mundiales WGS84. R4 usa el bounding box
de NYC para detectar coordenadas globalmente válidas pero incompatibles con la fuente. R5 exige
fecha y hora para los agregados temporales. R6 elimina IDs repetidos para evitar doble conteo.
En la carga completa, R1 descartó 226.028 registros; R2, 4.115; R3, 106; R4, 44; R5 y R6, cero.
Quedaron 1.741.828 documentos. La suma de descartes más la salida coincide con las 1.972.121 filas.

### ¿Cómo evita el pipeline recargar casi dos millones de filas en cada build?

`ingesta_meta` guarda dataset, tamaño de muestra, estado y total final. Si el registro está
completo y el conteo de `eventos` coincide, la ejecución imprime `Ingesta omitida`. Solo se
recarga cuando cambia la configuración o `FORCE_RELOAD=true`. El build #7 lo demostró al conservar
45.843 documentos sin repetir la descarga ni la transformación.

### ¿Por qué se usa `Client.upload_file` si todos usan la misma imagen?

Tener la misma imagen garantiza versiones iguales, pero un proceso iniciado mediante el comando
`dask scheduler` puede no incluir `/opt/ingest` en su ruta de importación. El primer build real lo
detectó al deserializar el grafo. `upload_file` instala el módulo en la ruta temporal importable del
scheduler y de los workers antes de enviar tareas.

### ¿Por qué GeoJSON usa `[longitud, latitud]`?

GeoJSON expresa coordenadas como `[x, y]`, es decir `[longitud, latitud]`. Invertirlas ubicaría
los puntos en lugares incorrectos y dañaría las consultas espaciales.

### ¿Qué hace el índice `2dsphere`?

Indexa geometrías sobre una esfera y permite consultas geoespaciales eficientes. `$near` y
`$geoNear` lo requieren. `$geoWithin` puede funcionar sin él, pero se beneficia del índice.

### ¿Dónde están las credenciales?

El token de Kaggle está en Jenkins como `Secret text` con ID `kaggle-api-token`. MongoDB usa la
credencial `mongo-root`. Para desarrollo local se usa `.env`, que está ignorado por Git. Los
valores nunca se guardan en el repositorio.

### ¿Por qué smee y no exponer Jenkins directamente?

Jenkins controla el socket Docker del equipo y no debe quedar publicado en internet. GitHub envía
el webhook al canal de smee y un cliente local establece una conexión saliente para reenviarlo.

### ¿Qué es staging en este pipeline?

La imagen candidata se levanta como un contenedor temporal separado. Los smoke tests consultan
su `/health`; solo después se promueve la misma imagen a producción. Al terminar, el contenedor
temporal se elimina.

### ¿Qué ocurre si falla una prueba?

Jenkins detiene el pipeline declarativo y marca las etapas posteriores como omitidas. El build #3
lo demostró: no se ejecutó `Despliegue` y la API siguió en la versión 2.

## 5. Preguntas que deben completarse en fases posteriores

| Pregunta probable | Qué falta obtener |
|---|---|
| ¿Por qué Dask para ingesta y Spark para agregaciones? | **Respondida:** Dask fue más rápido y sin arranque para la limpieza en pandas; Spark aporta el conector de MongoDB, el optimizador y el clúster para las agregaciones, y su desventaja bajó de ×12,7 a ×1,9 con 10 veces más datos (F8) |
| ¿Cuántas particiones Dask usaron? | 6 particiones para 1.972.121 filas; dos workers conectados |
| ¿Cuántos registros eliminó cada regla de limpieza? | R1=226.028, R2=4.115, R3=106, R4=44, R5=0, R6=0 |
| Diferencia práctica entre `$near`, `$geoWithin` y `$geoNear` | Implementar y medir F5 |
| ¿Cómo verificaron los resultados de Spark? | **Respondida:** grilla, hora, día y mes suman el total de documentos; el hotspot #1 se recuenta con `$geoWithin` (semilla: 57 = 57) |
| ¿Cuándo conviene Dask o Spark? | **Respondida:** con ~1,7 M de filas en un PC, Dask (0,30 s vs 3,80 s); Spark crece más despacio con el volumen (×1,2 frente a ×7,9 al multiplicar por 10). Que lo supere con más datos es hipótesis no medida |
| ¿Qué harían con diez veces más datos? | **Medido parcialmente:** con un Parquet físico ×10, Dask 2,36 s y Spark 4,51 s (1 worker); Spark no ganó con un 2.º worker en el mismo PC. En un clúster real se probaría Spark con varias máquinas |
| ¿Por qué Spark fue más lento con 2 workers? | Ambos workers comparten el mismo computador (sin CPU física extra) y el shuffle del `groupBy` serializa datos entre JVM |
| ¿Por qué descartaron mediciones? | Workers con memoria residual de la ingesta y un ×10 lógico sesgado; todo queda en `resultados_descartados.csv` con el motivo (D18) |

## 6. Cambios en vivo que deben ensayarse

Objetivo: completar cada ejercicio en 15 minutos o menos, usando rama, prueba, push, PR, revisión,
merge, Jenkins y comprobación final.

1. Añadir un endpoint que cuente eventos dentro de un polígono.
2. Consultar otro polígono sin modificar el código, cambiando solo el cuerpo de `/within`.
3. Añadir filtros `desde` y `hasta` a `/near`.
4. Devolver una proyección reducida de campos en `/near`.
5. Añadir una agregación Spark por día de la semana y borough.
6. Cambiar mediante parámetro el tamaño de la celda espacial.

## 7. Evidencias que se deben conservar

- URL del repositorio y PR usados en el simulacro.
- Captura de Jenkins iniciado por un push de GitHub.
- Captura del Stage View del build exitoso.
- Captura del build fallido con `Despliegue` omitido.
- Respuesta de `/health` antes y después de cada cambio.
- Petición y respuesta del endpoint o consulta solicitada.
- Conteos de limpieza, tiempos, memoria y resultados de verificación.

## 8. Regla de actualización de este documento

Al terminar una fase o incorporar una función demostrable, añadir:

1. **Qué hace.**
2. **Por qué se diseñó así.**
3. **Cómo se verifica.**
4. **Qué evidencia existe.**
5. **Qué podría pedir el docente que cambie en vivo.**
6. **Qué preguntas individuales nuevas deben practicar los tres integrantes.**

Este archivo se actualiza junto con `CONTEXT.md`; no reemplaza el enunciado ni el informe final.
