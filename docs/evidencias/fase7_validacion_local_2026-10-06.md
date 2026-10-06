# F7 — validación local previa a Jenkins

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

La ejecución real de las 4 pruebas Spark y de los smoke tests necesita la imagen Docker del
proyecto. Se validará en Jenkins antes de fusionar esta rama.

## Evidencia previa útil

`bdgeo-main` #10 terminó en aproximadamente 1 min 54 s, por debajo de la meta de 5 minutos,
con 22 pruebas API, 5 de ingesta, integraciones Dask/Spark, verificación Spark sobre semilla,
staging y despliegue. Esa medición es parcial: el cierre de F7 requiere repetirla con las nuevas
pruebas de esta rama.

## Criterio para cerrar Gate 7

1. Job de la rama en `SUCCESS`, incluida la nueva suite Spark y staging 120/120/120 + 7/57/23.
2. Mismo job con `FORZAR_FALLO=true` en `FAILURE`, sin ejecutar staging ni despliegue.
3. Build normal inferior a 5 minutos.
4. Merge mediante PR revisado y `bdgeo-main` en `SUCCESS`.
