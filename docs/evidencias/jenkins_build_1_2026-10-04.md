# Evidencia — Jenkins build #1 exitoso

Fecha: 4-oct-2026  
Job: `bdgeo-main`  
Repositorio: `https://github.com/sBoterino/big-data-geoespacial.git`  
Rama: `*/main`  
Commit: `a185f2bf1441184c25ec874c5d8639779619a9e3`  
Resultado: `SUCCESS`  
Duración: 1 min 52 s

## Resultados verificados

- Credenciales Jenkins presentes: `mongo-root` y `kaggle-api-token`; los secretos aparecen
  enmascarados en la consola.
- Pruebas unitarias: 4 pasaron y 1 fue omitida porque `FORZAR_FALLO` estaba desactivado.
- Kaggle autenticó correctamente y listó
  `Motor_Vehicle_Collisions_-_Crashes.csv` con 420.704.526 bytes.
- Dask: 2 workers conectados, media distribuida 0,5000 y 300 documentos semilla en MongoDB.
- Spark: 300 documentos leídos; grupos 120, 80 y 100.
- API de staging: `mongo=ok`, `status=ok`, `version=1-staging`.
- API desplegada: `mongo=ok`, `status=ok`, `version=1`.
- Mensaje final de Jenkins: `Finished: SUCCESS`.

## Pendiente para cerrar el Gate 2

- Conectar el webhook de GitHub mediante smee.io y demostrar ejecución automática.
- Ejecutar con `FORZAR_FALLO=true` y demostrar que la versión desplegada no cambia.

