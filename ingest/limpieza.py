"""Reglas puras de limpieza y transformación del dataset de colisiones."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

import pandas as pd


COLUMNAS_ORIGEN = [
    "CRASH DATE",
    "CRASH TIME",
    "BOROUGH",
    "ZIP CODE",
    "LATITUDE",
    "LONGITUDE",
    "ON STREET NAME",
    "CROSS STREET NAME",
    "OFF STREET NAME",
    "NUMBER OF PERSONS INJURED",
    "NUMBER OF PERSONS KILLED",
    "COLLISION_ID",
]

COLUMNAS_LIMPIAS = [
    "collision_id",
    "latitude",
    "longitude",
    "fecha",
    "hora",
    "dia_semana",
    "mes",
    "anio",
    "borough",
    "zip_code",
    "on_street_name",
    "cross_street_name",
    "off_street_name",
    "personas_heridas",
    "personas_muertas",
]

REGLAS = ("R1_coord_nulas_no_numericas", "R2_coord_cero", "R3_fuera_rango", "R4_fuera_nyc", "R5_fecha_hora", "R6_duplicado")
NYC_LAT = (40.49, 40.92)
NYC_LON = (-74.27, -73.68)


def meta_limpio() -> pd.DataFrame:
    """Metadatos estables para ``dask.dataframe.from_delayed``."""

    return pd.DataFrame(
        {
            "collision_id": pd.Series(dtype="string"),
            "latitude": pd.Series(dtype="float64"),
            "longitude": pd.Series(dtype="float64"),
            "fecha": pd.Series(dtype="datetime64[ns]"),
            "hora": pd.Series(dtype="int64"),
            "dia_semana": pd.Series(dtype="int64"),
            "mes": pd.Series(dtype="int64"),
            "anio": pd.Series(dtype="int64"),
            "borough": pd.Series(dtype="string"),
            "zip_code": pd.Series(dtype="string"),
            "on_street_name": pd.Series(dtype="string"),
            "cross_street_name": pd.Series(dtype="string"),
            "off_street_name": pd.Series(dtype="string"),
            "personas_heridas": pd.Series(dtype="int64"),
            "personas_muertas": pd.Series(dtype="int64"),
        }
    )


def _texto(serie: pd.Series) -> pd.Series:
    return serie.astype("string").str.strip()


def limpiar_dataframe(
    dataframe: pd.DataFrame, *, deduplicar: bool = True
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Aplica R1–R6 en orden y devuelve datos normalizados más su reporte."""

    faltantes = sorted(set(COLUMNAS_ORIGEN) - set(dataframe.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {', '.join(faltantes)}")

    trabajo = dataframe[COLUMNAS_ORIGEN].copy()
    reporte = {"total_inicial": int(len(trabajo)), **{regla: 0 for regla in REGLAS}}
    trabajo["_lat"] = pd.to_numeric(trabajo["LATITUDE"], errors="coerce")
    trabajo["_lon"] = pd.to_numeric(trabajo["LONGITUDE"], errors="coerce")

    def eliminar(mascara: pd.Series, regla: str) -> None:
        nonlocal trabajo
        mascara = mascara.fillna(True)
        reporte[regla] += int(mascara.sum())
        trabajo = trabajo.loc[~mascara].copy()

    eliminar(trabajo["_lat"].isna() | trabajo["_lon"].isna(), "R1_coord_nulas_no_numericas")
    eliminar((trabajo["_lat"] == 0) & (trabajo["_lon"] == 0), "R2_coord_cero")
    eliminar(
        ~trabajo["_lat"].between(-90, 90) | ~trabajo["_lon"].between(-180, 180),
        "R3_fuera_rango",
    )
    eliminar(
        ~trabajo["_lat"].between(*NYC_LAT) | ~trabajo["_lon"].between(*NYC_LON),
        "R4_fuera_nyc",
    )

    fecha_hora = _texto(trabajo["CRASH DATE"]) + " " + _texto(trabajo["CRASH TIME"])
    trabajo["_fecha"] = pd.to_datetime(
        fecha_hora, format="%m/%d/%Y %H:%M", errors="coerce"
    )
    eliminar(trabajo["_fecha"].isna(), "R5_fecha_hora")

    trabajo["_collision_id"] = _texto(trabajo["COLLISION_ID"])
    if deduplicar:
        eliminar(trabajo["_collision_id"].duplicated(keep="first"), "R6_duplicado")

    fecha = trabajo["_fecha"]
    limpio = pd.DataFrame(
        {
            "collision_id": trabajo["_collision_id"],
            "latitude": trabajo["_lat"].astype("float64"),
            "longitude": trabajo["_lon"].astype("float64"),
            "fecha": fecha,
            "hora": fecha.dt.hour.astype("int64"),
            "dia_semana": fecha.dt.dayofweek.astype("int64"),
            "mes": fecha.dt.month.astype("int64"),
            "anio": fecha.dt.year.astype("int64"),
            "borough": _texto(trabajo["BOROUGH"]),
            "zip_code": _texto(trabajo["ZIP CODE"]),
            "on_street_name": _texto(trabajo["ON STREET NAME"]),
            "cross_street_name": _texto(trabajo["CROSS STREET NAME"]),
            "off_street_name": _texto(trabajo["OFF STREET NAME"]),
            "personas_heridas": pd.to_numeric(
                trabajo["NUMBER OF PERSONS INJURED"], errors="coerce"
            ).fillna(0).astype("int64"),
            "personas_muertas": pd.to_numeric(
                trabajo["NUMBER OF PERSONS KILLED"], errors="coerce"
            ).fillna(0).astype("int64"),
        },
        index=trabajo.index,
    )
    reporte["total_final"] = int(len(limpio))
    return limpio[COLUMNAS_LIMPIAS], reporte


def _valor_texto(valor: Any) -> str | None:
    if valor is None or pd.isna(valor):
        return None
    texto = str(valor).strip()
    return texto or None


def a_documento(fila: Mapping[str, Any]) -> dict[str, Any]:
    """Convierte una fila limpia al modelo MongoDB/GeoJSON del proyecto."""

    fecha = fila["fecha"]
    if isinstance(fecha, pd.Timestamp):
        fecha = fecha.to_pydatetime()
    if not isinstance(fecha, datetime):
        raise ValueError("La fila limpia debe contener una fecha válida.")

    documento: dict[str, Any] = {
        "_id": str(fila["collision_id"]),
        "location": {
            "type": "Point",
            "coordinates": [float(fila["longitude"]), float(fila["latitude"])],
        },
        "fecha": fecha,
        "hora": int(fila["hora"]),
        "dia_semana": int(fila["dia_semana"]),
        "mes": int(fila["mes"]),
        "anio": int(fila["anio"]),
        "personas_heridas": int(fila["personas_heridas"]),
        "personas_muertas": int(fila["personas_muertas"]),
        "fuente": "NYC Motor Vehicle Collisions – Crashes",
    }
    for campo in ("borough", "zip_code", "on_street_name", "cross_street_name", "off_street_name"):
        valor = _valor_texto(fila.get(campo))
        if valor is not None:
            documento[campo] = valor
    return documento
