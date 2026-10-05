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

codigo=$(curl -s -o /tmp/near_invalido.json -w '%{http_code}' \
  "${BASE}/near?lat=200&lon=0&radio=10")
[ "$codigo" = "400" ] || { echo "[smoke] FALLO: /near inválido debía responder 400"; exit 1; }

if [ "${SMOKE_SEMILLA:-false}" = "true" ]; then
  curl -fsS "${BASE}/near?lat=40.758&lon=-73.9855&radio=1000&limit=1000" > /tmp/near.json
  grep -q '"total_devuelto":120' /tmp/near.json || { echo "[smoke] FALLO: /near != 120"; exit 1; }

  poligono='{"type":"Polygon","coordinates":[[[-73.996,40.75],[-73.975,40.75],[-73.975,40.766],[-73.996,40.766],[-73.996,40.75]]]}'
  curl -fsS -X POST "${BASE}/within?limit=1000" -H 'Content-Type: application/json' \
    --data "$poligono" > /tmp/within.json
  grep -q '"total_devuelto":120' /tmp/within.json || { echo "[smoke] FALLO: /within != 120"; exit 1; }

  curl -fsS "${BASE}/geonear?lat=40.758&lon=-73.9855&radio=1000&limit=1000&agrupar=grupo" \
    > /tmp/geonear.json
  grep -q '"total_devuelto":1' /tmp/geonear.json || { echo "[smoke] FALLO: /geonear grupos != 1"; exit 1; }
  grep -q '"n":120' /tmp/geonear.json || { echo "[smoke] FALLO: /geonear n != 120"; exit 1; }

  poligono_abierto='{"type":"Polygon","coordinates":[[[-74,40],[-73,40],[-73,41],[-74,41]]]}'
  codigo=$(curl -s -o /tmp/within_invalido.json -w '%{http_code}' -X POST "${BASE}/within" \
    -H 'Content-Type: application/json' --data "$poligono_abierto")
  [ "$codigo" = "400" ] || { echo "[smoke] FALLO: polígono abierto debía responder 400"; exit 1; }
  echo "[smoke] consultas geoespaciales sobre semilla: 120/120/120 OK"
fi

echo "[smoke] OK"
