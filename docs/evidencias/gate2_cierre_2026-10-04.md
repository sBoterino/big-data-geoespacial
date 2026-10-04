# Evidencia — cierre del Gate 2

Fecha: 4-oct-2026

## Despliegue automático

- Un push real a `main` atravesó GitHub → smee → Jenkins con respuesta HTTP 200.
- Jenkins creó automáticamente el build #2.
- El pipeline terminó correctamente y la API respondió:
  `mongo=ok`, `status=ok`, `version=2`.

## Bloqueo del despliegue

- Se inició manualmente el build #3 con `FORZAR_FALLO=true`.
- Pytest terminó con 1 fallo intencional y 4 pruebas aprobadas.
- Jenkins omitió las etapas de Kaggle, servicios, integración, staging y despliegue.
- La consola indicó: `NO se desplegó la versión 3. La versión anterior sigue activa`.
- Resultado final del build: `FAILURE`.
- Después del fallo, `/health` continuó respondiendo:
  `mongo=ok`, `status=ok`, `version=2`.

Esto demuestra que una prueba fallida detiene el pipeline antes del despliegue.

## Auditoría de secretos

- No hay `.env`, `kaggle.json` ni `access_token` rastreados por Git.
- No se encontraron tokens Kaggle reales con patrón `KGAT_...` en el historial.
- Las coincidencias de MongoDB encontradas son ejemplos con `<password>` o construcción de URI
  mediante variables en el código; no contienen contraseñas reales.
