"""
Genera datos semilla deterministas para pruebas (colección eventos_semilla).

Son 300 puntos en tres grupos separados, de modo que las consultas tengan resultados
conocidos de antemano:
  A: 120 puntos a menos de 400 m de Times Square
  B:  80 puntos a menos de 300 m del extremo de Brooklyn del Brooklyn Bridge
  C: 100 puntos dispersos en el este de Queens (lejos de A y B)

Salidas:
  mongo/init/02-semilla.js        -> se carga al inicializar MongoDB
  mongo/init/semilla_esperados.json -> resultados esperados que usan las pruebas

Uso:  python scripts/generar_semilla.py
"""
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA_JS = RAIZ / "mongo" / "init" / "02-semilla.js"
SALIDA_ESPERADOS = RAIZ / "mongo" / "init" / "semilla_esperados.json"

TIMES_SQUARE = (40.7580, -73.9855)      # (lat, lon)
BROOKLYN_BRIDGE = (40.7003, -73.9900)
R_TIERRA = 6_371_000


def distancia_m(a, b):
    """Haversine en metros entre (lat, lon)."""
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_TIERRA * math.asin(math.sqrt(h))


def punto_en_disco(rng, centro, radio_m):
    """Punto uniforme dentro de un círculo de radio_m alrededor del centro."""
    d = radio_m * math.sqrt(rng.random())
    ang = rng.random() * 2 * math.pi
    lat = centro[0] + (d * math.cos(ang)) / 111_320
    lon = centro[1] + (d * math.sin(ang)) / (111_320 * math.cos(math.radians(centro[0])))
    return round(lat, 6), round(lon, 6)


def main():
    rng = random.Random(42)
    inicio = datetime(2020, 1, 1)
    docs = []

    def agregar(grupo, lat, lon, hora):
        fecha = inicio + timedelta(days=rng.randrange(365), hours=hora, minutes=rng.randrange(60))
        docs.append({
            "_id": f"semilla-{len(docs):04d}",
            "grupo": grupo,
            # GeoJSON: [LONGITUD, LATITUD]
            "location": {"type": "Point", "coordinates": [lon, lat]},
            "fecha": fecha.isoformat(),
            "hora": fecha.hour, "dia_semana": fecha.isoweekday(), "mes": fecha.month, "anio": fecha.year,
        })

    for _ in range(120):
        agregar("A_times_square", *punto_en_disco(rng, TIMES_SQUARE, 380), hora=rng.choice([8, 9, 17, 18]))
    for _ in range(80):
        agregar("B_brooklyn_bridge", *punto_en_disco(rng, BROOKLYN_BRIDGE, 280), hora=rng.choice([12, 13]))
    for _ in range(100):
        lat, lon = round(rng.uniform(40.70, 40.78), 6), round(rng.uniform(-73.85, -73.75), 6)
        agregar("C_queens", lat, lon, hora=rng.randrange(24))

    # Polígono que encierra Midtown (contiene todo el grupo A y nada más)
    poligono_midtown = {"type": "Polygon", "coordinates": [[
        [-73.9960, 40.7500], [-73.9750, 40.7500], [-73.9750, 40.7660],
        [-73.9960, 40.7660], [-73.9960, 40.7500],
    ]]}

    def contar_cerca(centro, radio):
        return sum(distancia_m(centro, (d["location"]["coordinates"][1], d["location"]["coordinates"][0])) <= radio
                   for d in docs)

    def dentro_caja(d):
        lon, lat = d["location"]["coordinates"]
        return -73.9960 <= lon <= -73.9750 and 40.7500 <= lat <= 40.7660

    esperados = {
        "total": len(docs),
        "near": [
            {"lat": TIMES_SQUARE[0], "lon": TIMES_SQUARE[1], "radio_m": 1000, "esperado": contar_cerca(TIMES_SQUARE, 1000)},
            {"lat": BROOKLYN_BRIDGE[0], "lon": BROOKLYN_BRIDGE[1], "radio_m": 500, "esperado": contar_cerca(BROOKLYN_BRIDGE, 500)},
        ],
        "within": [{"poligono": poligono_midtown, "esperado": sum(dentro_caja(d) for d in docs)}],
        "orientacion": {"_id": docs[0]["_id"], "coordinates": docs[0]["location"]["coordinates"],
                        "nota": "coordinates[0] es longitud (~-73.98) y coordinates[1] latitud (~40.76)"},
    }

    # Comprobaciones: si el generador cambia, que no rompa lo que las pruebas esperan
    assert esperados["near"][0]["esperado"] == 120, esperados["near"][0]
    assert esperados["near"][1]["esperado"] == 80, esperados["near"][1]
    assert esperados["within"][0]["esperado"] == 120, esperados["within"][0]
    assert all(d["location"]["coordinates"][0] < -73 for d in docs), "orden lon/lat invertido"

    lineas = []
    for d in docs:
        d_js = dict(d)
        fecha = d_js.pop("fecha")
        cuerpo = json.dumps(d_js, ensure_ascii=False)[:-1]
        lineas.append(f'  {cuerpo}, "fecha": new Date("{fecha}Z")}}')
    js = (
        "// GENERADO por scripts/generar_semilla.py. No editar a mano.\n"
        "// 300 puntos con resultados conocidos (ver semilla_esperados.json).\n"
        'const geoSemilla = db.getSiblingDB(process.env.MONGO_DB || "geo");\n'
        "if (geoSemilla.eventos_semilla.countDocuments() === 0) {\n"
        "  geoSemilla.eventos_semilla.insertMany([\n" + ",\n".join(lineas) + "\n  ]);\n"
        "}\n"
        'print(`[init] eventos_semilla: ${geoSemilla.eventos_semilla.countDocuments()} documentos.`);\n'
    )
    SALIDA_JS.write_text(js, encoding="utf-8")
    SALIDA_ESPERADOS.write_text(json.dumps(esperados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {len(docs)} documentos -> {SALIDA_JS.name}; esperados -> {SALIDA_ESPERADOS.name}")


if __name__ == "__main__":
    main()
