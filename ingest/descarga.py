"""Descarga idempotente de datasets de Kaggle."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


DATA_ROOT = Path("/data/raw")


def _directorio_dataset(slug: str, root: Path = DATA_ROOT) -> Path:
    return root / slug.replace("/", "__")


def _inventario(directorio: Path) -> list[dict[str, object]]:
    return [
        {"nombre": str(path.relative_to(directorio)), "bytes": path.stat().st_size}
        for path in sorted(directorio.rglob("*"))
        if path.is_file() and path.name != ".descarga_ok"
    ]


def _cache_valida(directorio: Path) -> bool:
    marcador = directorio / ".descarga_ok"
    if not marcador.exists():
        return False
    try:
        esperado = json.loads(marcador.read_text(encoding="utf-8"))["archivos"]
    except (OSError, KeyError, json.JSONDecodeError):
        return False
    return esperado == _inventario(directorio) and bool(esperado)


def descargar_dataset(slug: str, root: Path = DATA_ROOT) -> Path:
    """Descarga y descomprime ``slug``; devuelve el CSV principal.

    El valor de ``KAGGLE_API_TOKEN`` nunca se incluye en mensajes de error.
    """

    directorio = _directorio_dataset(slug, root)
    directorio.mkdir(parents=True, exist_ok=True)

    if _cache_valida(directorio):
        print(f"[descarga] caché válida: {directorio}")
    else:
        token = os.getenv("KAGGLE_API_TOKEN", "")
        if not token:
            raise RuntimeError(
                "Falta KAGGLE_API_TOKEN. Configurar la credencial 'kaggle-api-token' en Jenkins."
            )

        print(f"[descarga] descargando {slug} desde Kaggle...")
        resultado = subprocess.run(
            ["kaggle", "datasets", "download", "-d", slug, "-p", str(directorio), "--unzip"],
            capture_output=True,
            text=True,
            check=False,
        )
        if resultado.returncode != 0:
            detalle = (resultado.stderr or resultado.stdout or "error desconocido").replace(token, "***")
            ultima_linea = detalle.strip().splitlines()[-1] if detalle.strip() else "error desconocido"
            raise RuntimeError(f"Kaggle no pudo descargar '{slug}': {ultima_linea}")

        archivos = _inventario(directorio)
        if not archivos:
            raise RuntimeError(f"Kaggle no produjo archivos para '{slug}'.")
        (directorio / ".descarga_ok").write_text(
            json.dumps({"dataset": slug, "archivos": archivos}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    csvs = sorted(directorio.rglob("*.csv"), key=lambda path: path.stat().st_size, reverse=True)
    if not csvs:
        raise RuntimeError(f"No se encontró ningún CSV en {directorio}.")
    print(f"[descarga] CSV: {csvs[0].name} ({csvs[0].stat().st_size:,} bytes)")
    return csvs[0]
