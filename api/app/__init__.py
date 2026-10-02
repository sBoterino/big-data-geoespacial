"""API Flask del proyecto Big Data Geoespacial.

Se usa el patrón application factory: create_app() recibe opcionalmente una base de
datos ya construida. Así las pruebas inyectan un doble de prueba sin MongoDB real,
y en producción se conecta con la URI del entorno.
"""
from flask import Flask, jsonify

from . import config


def create_app(db=None):
    app = Flask(__name__)

    if db is None:
        from pymongo import MongoClient  # import diferido: las pruebas no necesitan pymongo

        client = MongoClient(config.mongo_uri(), serverSelectionTimeoutMS=3000)
        db = client[config.MONGO_DB]

    app.config["DB"] = db

    @app.get("/health")
    def health():
        """Estado del servicio y de su conexión a MongoDB.

        Devuelve 503 si MongoDB no responde, para que el healthcheck de Docker y los
        smoke tests de Jenkins detecten un despliegue roto.
        """
        try:
            app.config["DB"].command("ping")
            mongo_estado = "ok"
        except Exception as exc:  # noqa: BLE001 - cualquier fallo de conexión cuenta
            return jsonify(status="error", mongo=f"sin conexión: {type(exc).__name__}",
                           version=config.APP_VERSION), 503
        return jsonify(status="ok", mongo=mongo_estado, version=config.APP_VERSION)

    @app.errorhandler(404)
    def no_encontrado(_):
        return jsonify(error="Ruta no encontrada"), 404

    return app
