"""
Verificación de un dataset de Kaggle antes de registrarlo con el docente (Gate 0).

Comprueba, con mediciones reales y no con lo que dice la página de Kaggle:
  1. Que el dataset se puede listar y descargar con la API de Kaggle.
  2. Cuántos registros tiene (debe ser >= 1.000.000 o >= 1 GB).
  3. Qué columnas de latitud / longitud / fecha tiene.
  4. Cuántos registros tienen coordenadas nulas, no numéricas, (0,0) o fuera de rango.
     Estos números sirven después para justificar la limpieza en el informe.

Requisitos:  pip install kaggle pandas
Credenciales: variable KAGGLE_API_TOKEN (o ~/.kaggle/access_token).
              Nunca escribirlas en este archivo.

Uso:
  python scripts/verificar_dataset.py muzammilrizvi1/motor-vehicle-collisions-crashes
  python scripts/verificar_dataset.py <owner/slug> --solo-listar
  python scripts/verificar_dataset.py <owner/slug> --dir data/raw
"""
import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pandas as pd

NOMBRES_LAT = {"lat", "latitude", "latitud", "start_lat", "pickup_latitude"}
NOMBRES_LON = {"lon", "long", "lng", "longitude", "longitud", "start_lng", "pickup_longitude"}
PISTAS_FECHA = ("date", "time", "fecha", "hora", "timestamp")
MINIMO_REGISTROS = 1_000_000
MINIMO_BYTES = 1_000_000_000


def kaggle(*args):
    """Ejecuta el CLI de Kaggle y devuelve su salida; aborta si falla."""
    try:
        res = subprocess.run(["kaggle", *args], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit("No se encontró el comando 'kaggle'. Instalar con: pip install kaggle")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Kaggle devolvió un error:\n{e.stderr or e.stdout}")
    return res.stdout


def detectar_columnas(columnas):
    normal = {c.strip().lower(): c for c in columnas}
    lat = next((normal[n] for n in normal if n in NOMBRES_LAT), None)
    lon = next((normal[n] for n in normal if n in NOMBRES_LON), None)
    fechas = [c for c in columnas if any(p in c.lower() for p in PISTAS_FECHA)]
    return lat, lon, fechas


def perfilar(df_iter):
    """Recorre el dataset por bloques y cuenta problemas de coordenadas."""
    stats = {
        "registros": 0,
        "coord_nulas": 0,
        "coord_no_numericas": 0,
        "coord_cero": 0,
        "fuera_de_rango": 0,
        "validos": 0,
    }
    lat_col = lon_col = None
    for bloque in df_iter:
        if lat_col is None:
            lat_col, lon_col, fechas = detectar_columnas(bloque.columns)
            stats["col_lat"], stats["col_lon"], stats["cols_fecha"] = lat_col, lon_col, fechas
            if not (lat_col and lon_col):
                stats["registros"] += len(bloque)
                stats["registros"] += sum(len(restante) for restante in df_iter)
                stats["error"] = f"No se detectaron columnas lat/lon. Columnas: {list(bloque.columns)}"
                return stats
        lat_original = bloque[lat_col]
        lon_original = bloque[lon_col]
        lat = pd.to_numeric(lat_original, errors="coerce")
        lon = pd.to_numeric(lon_original, errors="coerce")
        nulas = lat_original.isna() | lon_original.isna()
        no_numericas = ~nulas & (lat.isna() | lon.isna())
        coordenadas_invalidas = nulas | no_numericas
        cero = ~coordenadas_invalidas & (lat == 0) & (lon == 0)
        rango = ~coordenadas_invalidas & ~cero & ((lat.abs() > 90) | (lon.abs() > 180))
        stats["registros"] += len(bloque)
        stats["coord_nulas"] += int(nulas.sum())
        stats["coord_no_numericas"] += int(no_numericas.sum())
        stats["coord_cero"] += int(cero.sum())
        stats["fuera_de_rango"] += int(rango.sum())
        stats["validos"] += int((~coordenadas_invalidas & ~cero & ~rango).sum())
    return stats


def bloques_de(archivo, tam=500_000):
    if archivo.suffix.lower() == ".csv":
        return pd.read_csv(archivo, chunksize=tam, low_memory=False)
    if archivo.suffix.lower() in {".sqlite", ".db", ".sqlite3"}:
        def leer_sqlite():
            con = sqlite3.connect(archivo)
            try:
                tablas = [
                    t
                    for (t,) in con.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                ]
                # La tabla principal suele ser la más grande.
                tabla = max(
                    tablas,
                    key=lambda t: con.execute(
                        f'SELECT COUNT(*) FROM "{t}"'
                    ).fetchone()[0],
                )
                print(f"  Tabla SQLite analizada: {tabla}")
                yield from pd.read_sql_query(
                    f'SELECT * FROM "{tabla}"', con, chunksize=tam
                )
            finally:
                con.close()

        return leer_sqlite()
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dataset", help="owner/slug de Kaggle")
    p.add_argument("--dir", default="data/verificacion", help="carpeta de descarga")
    p.add_argument("--solo-listar", action="store_true", help="no descargar, solo listar archivos")
    a = p.parse_args()

    print(f"== Archivos de {a.dataset} ==")
    print(kaggle("datasets", "files", a.dataset))
    if a.solo_listar:
        return

    destino = Path(a.dir) / a.dataset.replace("/", "__")
    destino.mkdir(parents=True, exist_ok=True)
    print(f"== Descargando en {destino} (puede tardar) ==")
    kaggle("datasets", "download", a.dataset, "-p", str(destino), "--unzip")

    archivos = [f for f in destino.rglob("*") if f.is_file()]
    total_bytes = sum(f.stat().st_size for f in archivos)
    reporte = {"dataset": a.dataset, "bytes_totales": total_bytes, "archivos": {}}

    for f in sorted(archivos, key=lambda x: x.stat().st_size, reverse=True):
        it = bloques_de(f)
        if it is None:
            continue
        print(f"== Perfilando {f.name} ({f.stat().st_size / 1e6:.0f} MB) ==")
        reporte["archivos"][f.name] = perfilar(it)

    total_reg = sum(s.get("registros", 0) for s in reporte["archivos"].values())
    cumple = total_reg >= MINIMO_REGISTROS or total_bytes >= MINIMO_BYTES
    reporte["registros_totales"] = total_reg
    reporte["cumple_tamano"] = cumple

    print(json.dumps(reporte, indent=2, ensure_ascii=False))
    salida = Path("docs/evidencias") / f"verificacion_{a.dataset.replace('/', '__')}.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nReporte guardado en {salida} (evidencia para el informe).")
    print("CUMPLE el mínimo de tamaño." if cumple else "NO CUMPLE el mínimo de tamaño.")


if __name__ == "__main__":
    main()
