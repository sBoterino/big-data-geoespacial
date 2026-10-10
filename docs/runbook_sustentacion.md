# Runbook de sustentacion

Fecha de preparacion: 10 de octubre de 2026  
Equipo: Juan Guillermo Echeverri, Sebastian Botero Velasquez y Santiago Villamizar Mejia.

Este documento indica que abrir, que ejecutar y que explicar. No reemplaza el informe tecnico ni
la guia detallada de sustentacion.

## 1. Objetivo de la demostracion

Demostrar que el proyecto:

1. se levanta con Docker Compose;
2. descarga y limpia el dataset con Dask;
3. guarda GeoJSON valido e indexado en MongoDB;
4. calcula agregaciones verificables con Spark;
5. publica consultas mediante una API Flask;
6. prueba y despliega cambios con GitHub y Jenkins;
7. bloquea el despliegue cuando una prueba falla.

## 2. Reparto sugerido

| Integrante | Parte principal | Tambien debe poder explicar |
|---|---|---|
| Juan Guillermo | Arranque reproducible, Docker y MongoDB | Dask, Spark, API y Jenkins |
| Sebastian | API, prueba, PR y CI/CD | Datos, MongoDB, Dask y Spark |
| Santiago | Spark y benchmark Dask-Spark | Docker, MongoDB, API y Jenkins |

El reparto solo organiza la exposicion. El docente puede preguntar cualquier componente a
cualquier integrante.

## 3. Preparacion, 15 minutos antes

En el computador de Juan, abrir Docker Desktop y esperar a que el motor este listo. Luego abrir
PowerShell en el repositorio:

```powershell
cd "RUTA_DEL_REPOSITORIO"
$docker = "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe"

git switch main
git pull --ff-only origin main
git status
git log -1 --oneline
Test-Path .env
& $docker compose config --quiet
& $docker compose --profile ci up -d
& $docker compose ps
& $docker compose logs --tail 10 smee
Invoke-RestMethod http://localhost:5000/health
```

No continuar hasta comprobar:

- `main` actualizado y sin cambios locales;
- `.env` presente, pero nunca proyectado ni abierto durante la sustentacion;
- MongoDB, API, Dask Scheduler y Spark Master en `healthy`;
- dos workers Dask y un worker Spark en `Up`;
- Jenkins y smee en `Up`;
- smee en estado `Connected`;
- `/health` con `status=ok`, `mongo=ok`, `coleccion=eventos` y una version de build.

Abrir previamente estas paginas:

- API: <http://localhost:5000/health>
- Jenkins: <http://localhost:8080>
- Dask: <http://localhost:8787>
- Spark: <http://localhost:8081>
- repositorio de GitHub: <https://github.com/sBoterino/big-data-geoespacial>

## 4. Guion principal, 12 a 15 minutos

### 4.1 Problema y resultado, 1 minuto

Decir:

> Procesamos NYC Motor Vehicle Collisions, con 1.972.121 filas. Dask aplico seis reglas de
> limpieza y MongoDB recibio 1.741.828 documentos validos. Spark produjo agregaciones espaciales
> y temporales. Flask expone las consultas y Jenkins automatiza pruebas y despliegue.

Mostrar el README y el informe tecnico de nueve paginas.

### 4.2 Arquitectura, 2 minutos

Mostrar `docs/informe_assets/arquitectura.png` y explicar el flujo:

```text
Kaggle -> Dask -> MongoDB -> Spark -> MongoDB -> Flask
                       GitHub -> smee -> Jenkins -> Docker
```

Ideas clave:

- Docker Compose crea la red `bdgeo-net` y los contenedores se encuentran por nombre.
- Kaggle y MongoDB usan credenciales externas al repositorio.
- Dask realiza la ingesta particionada; Spark genera agregaciones.
- Jenkins prueba una imagen en staging antes de promoverla.

### 4.3 Ingesta y limpieza, 2 minutos

Mostrar `docs/evidencias/gate4_carga_completa_2026-10-04.md` y explicar:

| Regla | Motivo | Descartados |
|---|---|---:|
| R1 | Coordenadas nulas o no numericas | 226.028 |
| R2 | Punto centinela `(0,0)` | 4.115 |
| R3 | Fuera de rangos mundiales | 106 |
| R4 | Fuera del area de NYC | 44 |
| R5 | Fecha u hora invalida | 0 |
| R6 | ID duplicado | 0 |

Control aritmetico:

```text
1.972.121 - 230.293 = 1.741.828
```

Explicar que `ingesta_meta` hace la carga idempotente: si metadatos y conteo coinciden, una segunda
ejecucion informa `Ingesta omitida`. `FORCE_RELOAD=true` permite una recarga deliberada.

### 4.4 MongoDB y consultas geoespaciales, 2 minutos

Mostrar una consulta de la API:

```powershell
$near = Invoke-RestMethod "http://localhost:5000/near?lat=40.758&lon=-73.9855&radio=1000&limit=5"
$near | Select-Object total_devuelto, tiempo_ms
$near.parametros
```

Mostrar un poligono diferente sin cambiar codigo:

```powershell
$poligono = @{
    type = "Polygon"
    coordinates = @(,@(
        @(-73.990, 40.750),
        @(-73.980, 40.750),
        @(-73.980, 40.760),
        @(-73.990, 40.760),
        @(-73.990, 40.750)
    ))
} | ConvertTo-Json -Depth 6

$within = Invoke-RestMethod `
    "http://localhost:5000/within?limit=5" `
    -Method Post -ContentType "application/json" -Body $poligono

$within | Select-Object total_devuelto, tiempo_ms
```

Explicar:

- `location` es un `Point` GeoJSON en orden `[longitud, latitud]`;
- MongoDB valida la geometria;
- `location_2dsphere` acelera las operaciones sobre la superficie terrestre;
- `/near`, `/within` y `/geonear` reciben parametros variables y validan entradas.

### 4.5 Spark y comprobacion de resultados, 2 minutos

```powershell
$hotspots = Invoke-RestMethod `
    "http://localhost:5000/spark-results/hotspots?limit=5&orden=ranking&desc=false"
$hotspots.resultados | Format-Table ranking, n, heridos, muertos

$horas = Invoke-RestMethod `
    "http://localhost:5000/spark-results/por_hora?limit=24&orden=hora&desc=false"
$horas.resultados | Format-Table hora, n
```

Explicar que Spark genera grilla, hotspots, hora, dia de semana, mes y hora por borough. Las sumas
de las agregaciones principales deben coincidir con 1.741.828. El hotspot se contrasta con una
consulta MongoDB independiente, por lo que no se valida un resultado usando el mismo calculo.

### 4.6 Benchmark, 1 minuto

Mostrar `benchmark/resumen.md` y resumir sin afirmar mas de lo medido:

- se registraron 24 corridas validas mas calentamientos y corridas descartadas documentadas;
- con datos x1 y dos workers, Dask: 0,20 s; Spark: 4,65 s;
- con datos x10 fisicos y dos workers, Dask: 1,39 s; Spark: 5,12 s;
- ambos produjeron el mismo top 1 y conteos;
- Spark no mejoro con dos workers porque ambos compartian el mismo computador;
- en un cluster con varias maquinas el resultado podria cambiar, pero no se presenta como medido.

### 4.7 CI/CD y cambio en vivo, 3 a 5 minutos

Antes del cambio, guardar la version productiva:

```powershell
$antes = Invoke-RestMethod http://localhost:5000/health
$antes
```

Flujo que debe seguir cualquier solicitud del docente:

```powershell
git switch main
git pull --ff-only origin main
git switch -c simulacro/nombre-del-cambio
```

1. Implementar el cambio solicitado.
2. Agregar o modificar una prueba automatizada.
3. Probar localmente:

```powershell
git diff --check
& $docker build --target test -t bdgeo-api-test:simulacro api
& $docker run --rm bdgeo-api-test:simulacro
```

4. Confirmar que produccion aun conserva `$antes.version`.
5. Versionar y publicar:

```powershell
git add RUTA_DEL_CODIGO RUTA_DE_LA_PRUEBA
git diff --cached --check
git commit -m "feat: describir el cambio"
git push -u origin simulacro/nombre-del-cambio
```

6. Crear PR hacia `main` y explicar el cambio y las pruebas.
7. Otro integrante revisa y aprueba el PR.
8. Hacer merge. GitHub envia el push a smee y smee lo reenvia a Jenkins.
9. Abrir el build de `bdgeo-main` y narrar las etapas:

```text
Checkout -> Construir imagenes -> Pruebas -> Kaggle -> Servicios
-> Ingesta idempotente -> Integracion -> Spark -> Staging -> Despliegue
```

10. Tras `SUCCESS`, verificar:

```powershell
$despues = Invoke-RestMethod http://localhost:5000/health
$despues
$antes.version
$despues.version
```

La version debe cambiar y la respuesta debe contener el comportamiento solicitado. El simulacro
realizado agrego `coleccion=eventos` a `/health`, con 30 pruebas aprobadas y una omitida antes del
PR.

## 5. Demostracion de bloqueo por error

Solo realizarla en vivo si el docente la pide o si hay tiempo. En Jenkins, abrir `bdgeo-main`,
seleccionar **Build with Parameters**, activar `FORZAR_FALLO=true` y conservar los demas parametros
seguros.

Resultado esperado:

- pytest produce el fallo intencional;
- las etapas posteriores quedan omitidas;
- Jenkins termina en `FAILURE`;
- `/health` conserva la version que estaba desplegada.

Frase de cierre:

> El fallo no es un despliegue roto; es la evidencia de que el pipeline impidio que una imagen
> defectuosa llegara a produccion.

## 6. Respuestas cortas para preguntas frecuentes

**¿Por que Dask para limpiar?** Trabaja naturalmente con el flujo tipo pandas, particiona el CSV y
fue mas rapido en las mediciones locales.

**¿Por que Spark si fue mas lento?** Cumple un papel distinto: agregaciones reproducibles con su
motor distribuido y el conector de MongoDB. El benchmark tambien muestra el costo de arranque JVM.

**¿Por que MongoDB?** Almacena documentos GeoJSON, valida su estructura y ofrece consultas e
indices geoespaciales nativos.

**¿Por que `[longitud, latitud]`?** GeoJSON usa orden `[x,y]`; para coordenadas geograficas eso es
longitud y luego latitud.

**¿Como se protegen los secretos?** `.env` esta ignorado. Jenkins guarda MongoDB como credencial de
usuario/contrasena y Kaggle como texto secreto. Los valores no estan en Git.

**¿Como verifican Spark?** Las sumas de grilla y periodos coinciden con el total; el hotspot se
recuenta mediante MongoDB y la semilla ofrece resultados deterministas.

**¿Que pasa si Jenkins falla?** El pipeline detiene las etapas siguientes y no recrea la API de
produccion.

**¿Como saben que la version nueva llego?** Jenkins inyecta el numero de build como `APP_VERSION` y
`/health` lo devuelve.

## 7. Contingencias

| Problema | Comprobacion | Accion segura |
|---|---|---|
| Docker no responde | `& $docker version` | Abrir Docker Desktop y esperar al motor |
| Servicio caido | `& $docker compose ps` | `& $docker compose --profile ci up -d` |
| Webhook no llega | logs de smee | `& $docker compose logs --tail 50 smee` |
| Jenkins no inicia build | job, webhook y rama | Confirmar `bdgeo-main`, trigger GitHub y push a `main` |
| API conserva version vieja | consola de Jenkins | No reiniciar manualmente: localizar la etapa que fallo |
| Kaggle 401/403 | etapa Kaggle | Renovar el token en Jenkins; nunca pegarlo en Git o pantalla |
| Puerto ocupado | `docker compose ps` | Cerrar el proceso ajeno o usar la instalacion preparada |
| Sin internet | sistema local | Mostrar evidencias guardadas; no borrar volumenes ni imagenes |

Nunca ejecutar `docker compose down -v`, porque elimina los volumenes con la carga y las evidencias
operativas.

## 8. Cierre de la exposicion

Decir:

> El proyecto no solo procesa el dataset. Tambien demuestra reproducibilidad, calidad de datos,
> consistencia entre motores, consultas geoespaciales parametrizables y una ruta controlada desde
> un cambio en GitHub hasta produccion.

Confirmar visualmente:

- Jenkins en `SUCCESS`;
- `/health` con la version nueva;
- consulta solicitada funcionando;
- repositorio en `main` y sin secretos.

## 9. Apagado seguro despues de la sustentacion

```powershell
& $docker compose --profile ci stop
```

Esto detiene los contenedores y conserva los volumenes. Si se necesita liberar memoria, cerrar
Docker Desktop y despues ejecutar `wsl --shutdown`. No usar `down -v`.

