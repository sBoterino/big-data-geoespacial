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
| Dask distribuido básico | **Listo como infraestructura** | `ingest/check_cluster.py` | Scheduler, dos workers, cálculo distribuido y lectura de 300 documentos semilla |
| Reglas de limpieza R1–R6 | **Implementadas; datos reales pendientes** | `ingest/limpieza.py`, 3 tests Docker | Cada descarte se aplica en orden y queda contado de forma exclusiva; falta el reporte completo |
| Ingesta idempotente | **Implementada; ejecución pendiente** | `ingest/pipeline_ingesta.py` | `ingesta_meta` y el conteo de Mongo deciden si se omite; `FORCE_RELOAD` permite recargar |
| Validación de ramas sin afectar producción | **Implementada; ejecución pendiente** | Condiciones por `JOB_NAME` en `Jenkinsfile` | Solo `bdgeo-main` puede pasar por staging y despliegue; los jobs temporales usan etiquetas `validation-*` |
| Spark conectado a MongoDB | **Listo como infraestructura** | `spark/jobs/check_conexion.py` | Master, worker, conector MongoDB, lectura de 300 documentos y conteos 120/80/100 |
| GeoJSON e índice 2dsphere | **Listo con datos semilla** | `mongo/init/01-init.js`, `02-semilla.js` | Validador, orden `[longitud, latitud]`, índices y resultados conocidos |
| Modificación puntual en vivo | **Preparación lista; práctica pendiente** | Pipeline operativo | Todavía falta implementar los endpoints reales y ensayar un cambio de aplicación con rama, PR y merge |
| Consulta con otro polígono | **Pendiente de F5** | — | `/within` debe aceptar el polígono como parámetro; cambiar el polígono no debe exigir cambiar código |
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
Los conteos reales se añadirán después de la carga completa.

### ¿Cómo evita el pipeline recargar casi dos millones de filas en cada build?

`ingesta_meta` guarda dataset, tamaño de muestra, estado y total final. Si el registro está
completo y el conteo de `eventos` coincide, la ejecución imprime `Ingesta omitida`. Solo se
recarga cuando cambia la configuración o `FORCE_RELOAD=true`.

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
| ¿Por qué Dask para ingesta y Spark para agregaciones? | Añadir experiencia y mediciones reales de F4, F6 y F8 |
| ¿Cuántas particiones Dask usaron? | Registrar el número real durante la ingesta completa |
| ¿Cuántos registros eliminó cada regla de limpieza? | Añadir el reporte real de la carga completa |
| Diferencia práctica entre `$near`, `$geoWithin` y `$geoNear` | Implementar y medir F5 |
| ¿Cómo verificaron los resultados de Spark? | Sumas de control y cruce de hotspots con MongoDB en F6 |
| ¿Cuándo conviene Dask o Spark? | Tiempos y memoria propios del benchmark F8 |
| ¿Qué harían con diez veces más datos? | Respuesta final basada en los cuellos de botella observados |

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
