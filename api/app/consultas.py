"""Constructores puros de consultas MongoDB geoespaciales."""

from __future__ import annotations

from typing import Any


AGRUPACIONES = {"borough", "hora", "grupo"}


def filtro_near(lat: float, lon: float, radio: float) -> dict[str, Any]:
    return {
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                "$maxDistance": radio,
            }
        }
    }


def filtro_within(geometria: dict[str, Any]) -> dict[str, Any]:
    return {"location": {"$geoWithin": {"$geometry": geometria}}}


def pipeline_geonear(
    lat: float,
    lon: float,
    radio: float,
    limit: int,
    agrupar: str | None = None,
) -> list[dict[str, Any]]:
    """Construye un pipeline cuya primera etapa siempre es ``$geoNear``."""

    pipeline: list[dict[str, Any]] = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lon, lat]},
                "distanceField": "distancia_m",
                "maxDistance": radio,
                "spherical": True,
            }
        }
    ]
    if agrupar:
        if agrupar not in AGRUPACIONES:
            permitidas = ", ".join(sorted(AGRUPACIONES))
            raise ValueError(f"'agrupar' debe ser una de: {permitidas}.")
        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": f"${agrupar}",
                        "n": {"$sum": 1},
                        "distancia_media_m": {"$avg": "$distancia_m"},
                    }
                },
                {"$sort": {"n": -1, "_id": 1}},
            ]
        )
    pipeline.append({"$limit": limit})
    return pipeline
