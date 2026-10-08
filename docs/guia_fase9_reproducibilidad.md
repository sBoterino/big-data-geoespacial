# Guía F9 — reproducibilidad en el computador de Juan Guillermo

Fecha de preparación: 7-oct-2026.

Objetivo: demostrar que una persona diferente puede clonar el repositorio, configurar sus
propios secretos y levantar el sistema completo sin copiar carpetas, imágenes, volúmenes ni datos
de otro integrante.

## Reglas de la prueba

1. Usar un computador diferente al de Sebastián.
2. Clonar desde GitHub; no copiar la carpeta del proyecto por USB, Drive o red local.
3. No copiar volúmenes de Docker, `.env`, token de Kaggle ni datos descargados.
4. Seguir primero el README. Esta guía sirve como checklist y formato de evidencia.
5. Anotar cualquier paso ausente, ambiguo o incorrecto y corregir el README en la rama de Juan.
6. No publicar secretos, `.env`, `kaggle.json`, `access_token`, CSV, Parquet ni volúmenes.

## Resultado mínimo para aprobar

- El clon parte de `main` limpio.
- `docker compose up -d --build` levanta MongoDB, Spark, Dask y Flask.
- `/health` responde `status=ok` y `mongo=ok`.
- Dask detecta dos workers y accede a MongoDB.
- Spark accede a MongoDB mediante el conector.
- La ingesta completa se ejecuta o se reproduce con los conteos esperados.
- Spark calcula y verifica resultados sobre MongoDB.
- Juan registra tiempo, equipo, problemas y correcciones en un commit propio.

## 0. Información que Juan debe devolver

Al terminar, enviar al equipo:

- versión de Windows, RAM y procesador;
- versiones de Git, Docker y Compose;
- hora inicial, hora final y duración;
- salida de `docker compose ps`;
- respuesta de `/health`;
- salida de los checks Dask y Spark;
- reporte de limpieza y resultado de la verificación Spark;
- lista de problemas y cómo se resolvieron;
- enlace al PR creado por Juan.

No incluir contraseñas ni el token de Kaggle.

## 1. Instalar y comprobar requisitos

Instalar:

- Git para Windows: <https://git-scm.com/install/windows>
- Docker Desktop: <https://www.docker.com/products/docker-desktop/>

Durante la instalación de Docker, usar WSL 2. Reiniciar Windows si lo solicita. Abrir Docker
Desktop y esperar a que indique que el motor está funcionando.

En una ventana nueva de PowerShell:

```powershell
git --version
docker --version
docker compose version
docker run --rm hello-world
```

Los cuatro comandos deben terminar correctamente. Si PowerShell no encuentra Git o Docker,
cerrar la terminal, abrir otra y repetir.

## 2. Clonar desde GitHub y medir el tiempo

Elegir una carpeta nueva. No usar una copia previa del proyecto.

```powershell
$inicioF9 = Get-Date

Set-Location "$env:USERPROFILE\Documents"
git clone https://github.com/sBoterino/big-data-geoespacial.git
Set-Location .\big-data-geoespacial

git status
git log -1 --oneline
```

`git status` debe indicar que el árbol está limpio y la rama debe ser `main`.

## 3. Crear la configuración local

```powershell
Copy-Item .env.example .env
notepad .env
```

En `.env`:

1. Cambiar `MONGO_ROOT_PASSWORD=cambiar_esto` por una contraseña local nueva.
2. Crear un token en Kaggle: foto de perfil → **Settings** → **API** → **Generate New Token**.
3. Copiar el token `KGAT_...` en `KAGGLE_API_TOKEN=`.
4. Conservar `INGEST_MAX_ROWS=0` para la carga completa.
5. Dejar `SMEE_URL=` vacío: Jenkins y el webhook no son necesarios para esta prueba.

Si el computador tiene 8 GB de RAM o menos, usar:

```dotenv
SPARK_WORKER_CONTAINER_MEM=1536m
DASK_WORKER_CONTAINER_MEM=1536m
JENKINS_MEM=1536m
```

Guardar y cerrar el Bloc de notas. Nunca mostrar ni copiar el contenido completo de `.env` en
una captura o en el chat.

Comprobar que Compose entiende el archivo:

```powershell
docker compose config --quiet
```

No debe producir errores.

## 4. Construir y levantar el sistema base

```powershell
docker compose up -d --build
docker compose ps
```

La primera construcción puede tardar y descargar varios GB. Deben aparecer:

- `mongodb`: `healthy`;
- `spark-master`: `healthy`;
- `spark-worker`: `Up`;
- `dask-scheduler`: `healthy`;
- `dask-worker-1` y `dask-worker-2`: `Up`;
- `api`: `healthy`.

No hace falta iniciar Jenkins para F9.

Abrir:

- API: <http://localhost:5000/health>
- Spark: <http://localhost:8081>
- Dask: <http://localhost:8787>

En PowerShell:

```powershell
Invoke-RestMethod http://localhost:5000/health
```

Debe responder con `status=ok` y `mongo=ok`.

## 5. Verificar la comunicación distribuida

```powershell
docker compose run --rm dask-job python check_cluster.py
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/check_conexion.py
```

El primer comando debe reconocer dos workers Dask. El segundo debe confirmar la lectura y
escritura entre Spark y MongoDB usando los 300 documentos semilla.

## 6. Ejecutar la ingesta completa

Confirmar antes que `.env` conserva `INGEST_MAX_ROWS=0`.

```powershell
docker compose run --rm dask-job python pipeline_ingesta.py
```

No cerrar Docker ni suspender el computador. La descarga puede tardar varios minutos según la
red. Al finalizar, consultar el reporte guardado en el volumen:

```powershell
docker compose run --rm --no-deps -T dask-job cat /data/reporte_limpieza.json
```

Para la versión verificada del dataset, los controles esperados son:

| Control | Valor esperado |
|---|---:|
| Filas iniciales | 1.972.121 |
| R1: coordenadas nulas/no numéricas | 226.028 |
| R2: `(0,0)` | 4.115 |
| R3: fuera de rango mundial | 106 |
| R4: fuera de NYC | 44 |
| R5: fecha/hora inválida | 0 |
| R6: ID duplicado | 0 |
| Documentos finales | 1.741.828 |

Si Kaggle actualizó el archivo y cambian los conteos, no modificar el código para forzarlos:
guardar el nuevo reporte y avisar al equipo.

## 7. Comprobar idempotencia

Ejecutar exactamente el mismo comando otra vez:

```powershell
docker compose run --rm dask-job python pipeline_ingesta.py
```

Debe indicar `Ingesta omitida` y conservar 1.741.828 documentos, sin descargar ni insertar de
nuevo.

## 8. Ejecutar y verificar Spark sobre los datos reales

```powershell
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/agregacion_grilla.py
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/agregacion_temporal.py
docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/verificar_resultados.py
```

El último comando debe finalizar con `RESULTADO: OK`. Las sumas de grilla, hora, día y mes deben
coincidir con el total de documentos.

## 9. Probar la API con los datos cargados

```powershell
$health = Invoke-RestMethod http://localhost:5000/health
$near = Invoke-RestMethod "http://localhost:5000/near?lat=40.758&lon=-73.9855&radio=1000&limit=10"
$spark = Invoke-RestMethod "http://localhost:5000/spark-results/hotspots?limit=5&orden=ranking&desc=false"

$health
$near.total_devuelto
$spark.total_devuelto
```

`$health` debe seguir correcto y las dos consultas deben devolver resultados.

## 10. Registrar tiempo y preparar la evidencia

```powershell
$finF9 = Get-Date
$duracionF9 = $finF9 - $inicioF9

[PSCustomObject]@{
    inicio = $inicioF9
    fin = $finF9
    minutos = [math]::Round($duracionF9.TotalMinutes, 2)
}
```

Crear `docs/evidencias/fase9_reproducibilidad_juan_2026-10-07.md` con:

```markdown
# F9 — reproducibilidad en el computador de Juan Guillermo

- Fecha:
- Equipo: Windows, RAM, procesador
- Git / Docker / Compose:
- Commit probado:
- Duración total:

## Resultados

- Compose:
- `/health`:
- Dask:
- Spark Connector:
- Ingesta y conteos:
- Segunda ingesta:
- Verificación Spark:
- Consultas API:

## Problemas encontrados y correcciones

1. Problema — causa — solución.

## Conclusión

Indicar si pudo levantarse usando solo la documentación del repositorio.
```

Guardar capturas sin secretos. Como mínimo:

1. `docker compose ps`.
2. `/health`.
3. dashboard de Dask con dos workers.
4. UI de Spark con un worker.
5. reporte de ingesta y `RESULTADO: OK` de Spark.

## 11. Commit y PR de Juan Guillermo

Configurar su identidad real de GitHub:

```powershell
git config user.name "Juan Guillermo Echeverri"
git config user.email "CORREO_DE_GITHUB_DE_JUAN"
git switch -c docs/reproducibilidad-juan
```

Antes del commit:

```powershell
git status
git diff -- . ':!.env'
```

Solo deben aparecer la evidencia y las correcciones legítimas al README. Nunca agregar `.env` ni
datos. Después:

```powershell
git add README.md docs/evidencias/fase9_reproducibilidad_juan_2026-10-07.md
git commit -m "docs: validar reproducibilidad en equipo de Juan"
git push -u origin docs/reproducibilidad-juan
```

Juan crea el pull request hacia `main` y otro integrante lo revisa. Este commit es importante
porque el docente revisará que el historial refleje el aporte real de los tres integrantes.

## 12. Apagar sin borrar la evidencia local

```powershell
docker compose down
```

No usar `docker compose down -v` ni `docker system prune`, porque eliminarían datos y volúmenes
necesarios si hay que repetir una comprobación.

## Problemas frecuentes

| Síntoma | Acción |
|---|---|
| Docker no responde | Abrir Docker Desktop y esperar a que el motor esté listo |
| Error WSL | Reiniciar Windows; luego `wsl --update` y `wsl --shutdown` |
| DNS de Docker Hub | Reintentar `docker compose build`; comprobar internet y reiniciar Docker Desktop |
| Kaggle 401/403 | Generar un token nuevo y reemplazar solo `KAGGLE_API_TOKEN` en `.env` |
| Puerto ocupado | Cerrar la aplicación que usa 5000, 8081, 8787 o 27017; alternativamente cambiar `API_PORT` |
| Contenedor `unhealthy` | `docker compose ps` y `docker compose logs --tail 100 NOMBRE_SERVICIO` |
| Falta de memoria | Cerrar aplicaciones y bajar los límites de worker a `1536m` |
| Construcción interrumpida | Repetir `docker compose up -d --build`; Docker reutiliza las capas completas |

