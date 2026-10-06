# F7 — pruebas completas y validación en Jenkins

Fecha: 6-oct-2026.

Rama: `feature/fase7-pruebas`.

## Cobertura incorporada

- API: parámetros límite, polígonos mal formados y fuera de rango, construcción de `$near`,
  `$geoWithin` y `$geoNear`, prefijo aislado de colecciones Spark y serialización de BSON,
  fechas y estructuras anidadas.
- Ingesta: reglas exclusivas R1–R6, GeoJSON `[longitud, latitud]`, fecha, hora y conteo por
  partición.
- Spark: funciones puras de grilla, sumas, polígono GeoJSON, ranking determinista de hotspots,
  agregación temporal y distancia Haversine.
- Smoke de staging: `/health`, dos respuestas de error, conteos geoespaciales 120/120/120 y
  resultados Spark conocidos: 7 colecciones, hotspot `n=57` y 23 horas.

El staging de Jenkins ahora también se ejecuta en jobs de rama. Usa `eventos_semilla` y el
prefijo `spark_semilla_`, por lo que comprueba la imagen candidata sin leer ni modificar las
colecciones de producción. El despliegue continúa restringido a `bdgeo-main`.

## Resultados locales

| Suite | Resultado |
|---|---:|
| API normal | 30 aprobadas, 1 trampa omitida |
| API con `FORZAR_FALLO=true` | 30 aprobadas, 1 fallo intencional; código de salida 1 |
| Ingesta Dask | 5 aprobadas |
| Sintaxis de `scripts/smoke_api.sh` | válida (`bash -n`) |
| Parseo de `docker-compose.yml` | válido |
| Sintaxis de la nueva suite Spark | válida |

## Jenkins de la rama

Job: `bdgeo-fase7-test`. Revisión probada: `640eb16`.

### Build #1 — flujo normal

- Resultado: `SUCCESS`.
- Duración aproximada: 2 min 19 s (00:40:40–00:42:59), inferior a la meta de 5 minutos.
- API: 30 aprobadas y 1 trampa omitida.
- Ingesta: 5 aprobadas.
- Spark puro: 4 aprobadas en 6,251 s.
- Integraciones Dask y Spark: aprobadas.
- Verificación Spark sobre semilla: sumas 300, hotspot `57 = 57` y ubicación a 155 m de
  Times Square.
- Staging: `/health` correcto; consultas 120/120/120 y resultados Spark 7/57/23.
- `Despliegue` se omitió por ser un job de rama; producción no fue modificada.

Docker Hub falló transitoriamente por DNS en los primeros intentos de construcción. El mecanismo
de tres reintentos permitió completar el build; no fue un fallo del código ni de las pruebas.

### Build #2 — fallo intencional

- Parámetro: `FORZAR_FALLO=true`.
- Resultado esperado y obtenido: `FAILURE`.
- Pytest: 30 aprobadas y 1 fallo intencional en 0,10 s.
- Se omitieron acceso a Kaggle, servicios, ingesta, integración, procesamiento Spark, staging y
  despliegue debido al fallo anterior.
- Mensaje final: la versión anterior continúa activa.

Esto demuestra con el pipeline final que una prueba rota detiene la promoción de la imagen.

### Build de producción #11 — cierre después del merge

- PR #6 revisado y fusionado; merge `71fd7fb` en `main`.
- Inicio automático por push de GitHub de `gitsILLO69`.
- Resultado: `SUCCESS` en aproximadamente 1 min 52 s (00:52:09–00:54:01).
- API: 30 aprobadas y 1 trampa omitida; ingesta: 5 aprobadas; Spark puro: 4 aprobadas.
- La ingesta idempotente conservó 1.741.828 documentos.
- Integraciones Dask/Spark y verificación Spark sobre semilla aprobadas.
- Staging versión 11: 120/120/120 y resultados Spark 7/57/23.
- Producción recreada desde la misma imagen candidata; `/health` respondió `version=11`.
- Mensaje final: `OK: build 11 desplegado`.

## Evidencia previa útil

`bdgeo-main` #10 terminó en aproximadamente 1 min 54 s, por debajo de la meta de 5 minutos,
con 22 pruebas API, 5 de ingesta, integraciones Dask/Spark, verificación Spark sobre semilla,
staging y despliegue. Esa medición es parcial: el cierre de F7 requiere repetirla con las nuevas
pruebas de esta rama.

## Criterio de Gate 7

1. [x] Job de la rama en `SUCCESS`, incluida la nueva suite Spark y staging 120/120/120 + 7/57/23.
2. [x] Mismo job con `FORZAR_FALLO=true` en `FAILURE`, sin ejecutar staging ni despliegue.
3. [x] Build normal inferior a 5 minutos.
4. [x] Merge mediante PR revisado y `bdgeo-main` #11 en `SUCCESS`.

**Gate 7 cerrado.**
