"""Rutas REST para consultas geoespaciales y resultados de Spark."""

from __future__ import annotations

from datetime import date, datetime
from time import perf_counter
from typing import Any

from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request

from . import config
from .consultas import AGRUPACIONES, filtro_near, filtro_within, pipeline_geonear
from .validacion import (
    ErrorValidacion,
    booleano,
    campo_orden,
    entero,
    poligono,
    punto,
)


bp = Blueprint("consultas", __name__)

COLECCIONES_SPARK = {
    "grilla",
    "hotspots",
    "por_hora",
    "por_dia_semana",
    "por_mes",
    "hora_borough",
    "meta",
}


def serializar(valor: Any) -> Any:
    if isinstance(valor, ObjectId):
        return str(valor)
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    if isinstance(valor, dict):
        return {clave: serializar(item) for clave, item in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [serializar(item) for item in valor]
    return valor


def _coleccion_eventos():
    return current_app.config["DB"][config.MONGO_COLLECTION]


def _coleccion_spark(nombre: str) -> str:
    """Nombre físico de una salida Spark; staging usa el prefijo de la semilla."""
    return f"{current_app.config['SPARK_COLLECTION_PREFIX']}{nombre}"


def _respuesta(resultados: list[dict[str, Any]], parametros: dict[str, Any], inicio: float):
    return jsonify(
        total_devuelto=len(resultados),
        parametros=parametros,
        tiempo_ms=round((perf_counter() - inicio) * 1000, 3),
        resultados=serializar(resultados),
    )


@bp.get("/near")
def near():
    inicio = perf_counter()
    lat, lon, radio, limit = punto(request.args)
    resultados = list(_coleccion_eventos().find(filtro_near(lat, lon, radio)).limit(limit))
    return _respuesta(resultados, {"lat": lat, "lon": lon, "radio": radio, "limit": limit}, inicio)


@bp.post("/within")
def within():
    inicio = perf_counter()
    geometria = poligono(request.get_json(silent=True))
    limit = entero(request.args.get("limit", 100), "limit", minimo=1, maximo=1000)
    resultados = list(_coleccion_eventos().find(filtro_within(geometria)).limit(limit))
    return _respuesta(resultados, {"geometry": geometria, "limit": limit}, inicio)


@bp.get("/geonear")
def geonear():
    inicio = perf_counter()
    lat, lon, radio, limit = punto(request.args)
    agrupar = request.args.get("agrupar") or None
    if agrupar and agrupar not in AGRUPACIONES:
        raise ErrorValidacion(f"'agrupar' debe ser una de: {', '.join(sorted(AGRUPACIONES))}.")
    pipeline = pipeline_geonear(lat, lon, radio, limit, agrupar)
    resultados = list(_coleccion_eventos().aggregate(pipeline))
    return _respuesta(
        resultados,
        {"lat": lat, "lon": lon, "radio": radio, "limit": limit, "agrupar": agrupar},
        inicio,
    )


@bp.get("/spark-results")
def spark_colecciones():
    inicio = perf_counter()
    existentes = set(current_app.config["DB"].list_collection_names())
    colecciones = sorted(
        nombre for nombre in COLECCIONES_SPARK if _coleccion_spark(nombre) in existentes
    )
    return jsonify(colecciones=colecciones, tiempo_ms=round((perf_counter() - inicio) * 1000, 3))


@bp.get("/spark-results/<nombre>")
def spark_resultados(nombre: str):
    inicio = perf_counter()
    if nombre not in COLECCIONES_SPARK:
        raise ErrorValidacion("Colección Spark no permitida.")
    limit = entero(request.args.get("limit", 100), "limit", minimo=1, maximo=1000)
    orden = campo_orden(request.args.get("orden", "n"))
    desc = booleano(request.args.get("desc", "true"), "desc")
    cursor = current_app.config["DB"][_coleccion_spark(nombre)].find({}).sort(
        orden, -1 if desc else 1
    ).limit(limit)
    resultados = list(cursor)
    return _respuesta(
        resultados,
        {"nombre": nombre, "limit": limit, "orden": orden, "desc": desc},
        inicio,
    )
