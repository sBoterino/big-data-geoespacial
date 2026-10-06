"""Configuración leída del entorno. Ningún valor sensible está escrito en el código."""
import os
from urllib.parse import quote_plus


def mongo_uri() -> str:
    """Construye la URI de MongoDB a partir de variables de entorno.

    Si existe MONGO_URI se usa tal cual. Si no, se arma con usuario y contraseña
    escapados, para que caracteres como @ o : en la contraseña no rompan la URI.
    """
    if os.getenv("MONGO_URI"):
        return os.environ["MONGO_URI"]
    user = quote_plus(os.getenv("MONGO_ROOT_USER", ""))
    password = quote_plus(os.getenv("MONGO_ROOT_PASSWORD", ""))
    host = os.getenv("MONGO_HOST", "mongodb")
    port = os.getenv("MONGO_PORT", "27017")
    cred = f"{user}:{password}@" if user else ""
    return f"mongodb://{cred}{host}:{port}/?authSource=admin"


MONGO_DB = os.getenv("MONGO_DB", "geo")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "eventos")
SPARK_COLLECTION_PREFIX = os.getenv("SPARK_COLLECTION_PREFIX", "spark_")
APP_VERSION = os.getenv("APP_VERSION", "dev")
