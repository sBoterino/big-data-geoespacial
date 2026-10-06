# F8 — merge del benchmark y validación de Jenkins

Fecha local: 6-oct-2026.

## Integración

- PR fusionado: `#5`, Fase 8 — benchmark Dask vs Spark.
- Merge en `main`: `c2a2ec4`.
- Autor del evento GitHub: `gitsILLO69`.
- Job automático: `bdgeo-main` #10.

El benchmark no se repite dentro de Jenkins: sus 32 corridas, CSV, gráficas y análisis fueron
generados manualmente en el computador de Santiago y quedaron versionados en el PR. Jenkins #10
validó que integrar esos scripts y documentos no rompiera el sistema desplegable.

## Resultado del pipeline

- Pruebas API: 22 aprobadas y 1 trampa omitida.
- Pruebas de ingesta: 5 aprobadas.
- Ingesta idempotente: conservó los 1.741.828 documentos y omitió la recarga.
- Verificación Spark sobre semilla: todas las sumas dieron 300; hotspot #1, 57 frente a 57.
- `spark_meta` contenía los dos resultados reales requeridos, por lo que no se recalcularon las
  agregaciones de 1.741.828 documentos.
- Staging: versión `10-staging`, consultas 120/120/120 aprobadas.
- Producción: `/health` respondió con versión `10`.
- Resultado final: `Finished: SUCCESS`.
- Duración aproximada observada: 1 min 54 s (00:18:56–00:20:50), inferior al objetivo de 5 min
  de F7 para un build normal sin recarga.

## Conclusión

El PR #5 quedó integrado sin modificar la colección limpia ni recalcular innecesariamente las
agregaciones reales. La API versión 10 fue promovida después de aprobar pruebas, integración,
verificación Spark y staging. F8 queda fusionada; este build aporta además evidencia parcial para
el cierre de F7.
