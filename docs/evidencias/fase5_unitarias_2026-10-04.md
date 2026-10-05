# Fase 5 — pruebas unitarias de la API geoespacial

Fecha: 4-oct-2026

Rama: `feature/api-consultas`

Imagen: `bdgeo-api-test:f5`

## Ejecución

```text
.............s.........                                                  [100%]
SKIPPED [1] tests/test_trampa.py:12: Solo se activa con FORZAR_FALLO=true
22 passed, 1 skipped in 0.05s
```

La prueba omitida es la prueba trampa del pipeline y solo se activa con
`FORZAR_FALLO=true`. Las 22 pruebas normales cubren salud de la API, validación de parámetros y
polígonos, constructores `$near`, `$geoWithin` y `$geoNear`, rutas, serialización y lista blanca
de colecciones Spark.

Esta evidencia aprueba la parte unitaria de F5. Todavía faltan los smoke tests contra
`eventos_semilla`, las consultas sobre los datos reales y la validación del pipeline Jenkins.
