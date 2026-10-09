Claro. Te lo paso **completo otra vez**, pero esta vez te recomiendo copiarlo directamente desde aquí al Bloc de notas.

````markdown
# Evidencia de reproducibilidad — Fase 9

**Estudiante:** Juan Guillermo Echeverri Ramirez  
**Fecha de ejecución:** 2026-10-09  
**Commit evaluado:** `77521c7`  
**Proyecto:** big-data-geoespacial  

---

## 1. Objetivo

Validar la reproducibilidad de la solución Big Data geoespacial desde el entorno local, comprobando el funcionamiento de Docker Compose, MongoDB, Dask, Spark y la API, así como la correcta ejecución de los procesos de ingestión, agregación y verificación de resultados.

---

## 2. Entorno de ejecución

El proyecto fue ejecutado localmente utilizando Docker Compose sobre Windows con WSL2.

### Componentes principales

- MongoDB
- Flask API
- Dask Scheduler
- Dask Worker 1
- Dask Worker 2
- Spark Master
- Spark Worker

El commit utilizado durante la validación fue:

```text
77521c7
````

---

## 3. Estado de los servicios

Se ejecutó:

```powershell
docker compose ps
```

Los servicios principales quedaron activos correctamente:

| Servicio       | Estado       |
| -------------- | ------------ |
| API            | Up / healthy |
| MongoDB        | Up / healthy |
| Dask Scheduler | Up / healthy |
| Dask Worker 1  | Up           |
| Dask Worker 2  | Up           |
| Spark Master   | Up / healthy |
| Spark Worker   | Up           |

La API quedó publicada en el puerto `5000`, el Dashboard de Dask en el puerto `8787` y la interfaz de Spark en el puerto `8081`.

---

## 4. Validación de Dask

Se ejecutó:

```powershell
docker compose run --rm dask-job python check_cluster.py
```

La prueba confirmó:

* 2 workers de Dask conectados.
* Ejecución distribuida correcta.
* Conexión correcta con MongoDB.
* Existencia de 300 documentos de prueba en MongoDB.
* Resultado final: `RESULTADO: OK`.

---

## 5. Validación del conector Spark - MongoDB

Se ejecutó:

```powershell
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/check_conexion.py
```

La prueba confirmó:

* Lectura correcta desde MongoDB mediante Spark.
* 300 documentos de prueba leídos.
* Categorías de prueba encontradas:

  * `A_times_square`: 120
  * `B_brooklyn_bridge`: 80
  * `C_queens`: 100

La conexión Spark-MongoDB funcionó correctamente.

---

## 6. Ingesta y dataset

La configuración utilizada fue:

```text
INGEST_MAX_ROWS=0
```

Al ejecutar:

```powershell
docker compose run --rm dask-job python pipeline_ingesta.py
```

el sistema indicó que la ingesta fue omitida debido a que ya existían:

```text
1,741,828 documentos
```

correspondientes al dataset configurado.

La condición de idempotencia de la ingesta fue respetada.

---

## 7. Agregación espacial con Spark

Se ejecutó:

```powershell
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/agregacion_grilla.py
```

Resultado principal:

```text
[grilla] origen=eventos leídos=1741828 celdas=3246 suma_n=1741828
```

Esto demuestra que Spark procesó los `1,741,828` documentos y que la suma de los registros agrupados por celda coincide con el total de documentos procesados.

La duración registrada fue aproximadamente:

```text
31.079 segundos
```

---

## 8. Agregación temporal con Spark

Se ejecutó:

```powershell
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/agregacion_temporal.py
```

Resultados:

```text
[temporal] spark_por_hora: 24 filas, suma_n=1741828
[temporal] spark_por_dia_semana: 7 filas, suma_n=1741828
[temporal] spark_por_mes: 12 filas, suma_n=1741828
[temporal] spark_hora_borough: 144 filas, suma_n=1741828
```

El proceso leyó:

```text
1,741,828 documentos
```

y tuvo una duración aproximada de:

```text
27.183 segundos
```

---

## 9. Verificación de resultados Spark

Se ejecutó:

```powershell
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/verificar_resultados.py
```

Resultado:

```text
[verificar] documentos en eventos: 1741828
[verificar] OK    suma de n en spark_grilla = 1741828 (esperado 1741828)
[verificar] OK    suma de n en spark_por_hora = 1741828 (esperado 1741828)
[verificar] OK    suma de n en spark_por_dia_semana = 1741828 (esperado 1741828)
[verificar] OK    suma de n en spark_por_mes = 1741828 (esperado 1741828)
[verificar] OK    hotspot #1 (-14799_8151): Spark n=5336, MongoDB $geoWithin=5337 (margen ±27)
[verificar] RESULTADO: OK
```

La verificación confirma que las agregaciones generadas por Spark son consistentes con el total de documentos y que el hotspot principal fue validado contra MongoDB dentro del margen establecido.

---

## 10. Validación de la API

Se realizaron las siguientes consultas desde PowerShell:

```powershell
$health = Invoke-RestMethod http://localhost:5000/health
$near = Invoke-RestMethod "http://localhost:5000/near?lat=40.758&lon=-73.9855&radio=1000&limit=10"
$spark = Invoke-RestMethod "http://localhost:5000/spark-results/hotspots?limit=5&orden=ranking&desc=false"

$health
$near.total_devuelto
$spark.total_devuelto
```

Resultado:

```text
mongo status version
----- ------ -------
ok    ok     8

10
5
```

Se verificó que:

* MongoDB responde correctamente.
* La API responde con estado `ok`.
* La versión desplegada corresponde a `8`.
* La consulta `/near` devolvió 10 resultados.
* La consulta de hotspots de Spark devolvió 5 resultados.

---

## 11. Incidencias encontradas y soluciones

Durante la validación se presentó una incidencia al intentar ejecutar inicialmente:

```powershell
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/ventanas_temporales.py
```

El sistema respondió:

```text
python3: can't open file '/opt/jobs/ventanas_temporales.py': [Errno 2] No such file or directory
```

Se verificaron los archivos Python disponibles en el proyecto y se identificó que el nombre correcto del trabajo era:

```text
spark/jobs/agregacion_temporal.py
```

Se ejecutó nuevamente utilizando:

```powershell
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/agregacion_temporal.py
```

La ejecución terminó correctamente.

También se observaron algunos mensajes `WARN` de Spark relacionados con la librería nativa de Hadoop y opciones duplicadas del conector de MongoDB. Estos mensajes no impidieron la ejecución y las pruebas terminaron correctamente.

---

## 12. Conclusión

La validación de reproducibilidad de la Fase 9 fue completada satisfactoriamente.

El entorno ejecutó correctamente los componentes de MongoDB, Dask, Spark y la API. Dask reconoció dos workers y pudo comunicarse con MongoDB. Spark pudo leer y procesar los datos almacenados en MongoDB.

Se procesaron y verificaron `1,741,828` documentos. Las agregaciones espaciales y temporales conservaron la correspondencia con el total de documentos y la verificación final terminó con:

```text
RESULTADO: OK
```

Finalmente, la API respondió correctamente mediante los endpoints de salud, consulta geoespacial y resultados de Spark.

Por lo anterior, la solución cumplió las pruebas técnicas de reproducibilidad establecidas para la Fase 9.
