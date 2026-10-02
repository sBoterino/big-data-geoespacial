#!/usr/bin/env bash
# Pruebas básicas contra la API en ejecución (etapa "Pruebas contra la API" del pipeline).
# Uso: scripts/smoke_api.sh http://api:5000
# Sale con código distinto de 0 si algo falla, lo que detiene el pipeline y evita el deploy.
set -euo pipefail
BASE="${1:?Uso: smoke_api.sh <url_base>}"
INTENTOS="${SMOKE_INTENTOS:-20}"

echo "[smoke] esperando a ${BASE}/health ..."
for i in $(seq 1 "$INTENTOS"); do
  if curl -fsS "${BASE}/health" > /tmp/health.json 2>/dev/null; then break; fi
  if [ "$i" -eq "$INTENTOS" ]; then echo "[smoke] FALLO: la API no respondió"; exit 1; fi
  sleep 3
done
echo "[smoke] /health -> $(cat /tmp/health.json)"
grep -q '"status":"ok"' /tmp/health.json || { echo "[smoke] FALLO: status != ok"; exit 1; }
grep -q '"mongo":"ok"' /tmp/health.json || { echo "[smoke] FALLO: MongoDB no conectado"; exit 1; }

codigo=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/ruta-que-no-existe")
[ "$codigo" = "404" ] || { echo "[smoke] FALLO: se esperaba 404 y llegó ${codigo}"; exit 1; }

# Aquí se agregan las pruebas de /near, /within y /spark-results en la Fase 5.
echo "[smoke] OK"
