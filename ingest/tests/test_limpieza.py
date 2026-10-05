from __future__ import annotations

import pandas as pd

from limpieza import a_documento, limpiar_dataframe


def fila(identificador: str, **cambios):
    base = {
        "CRASH DATE": "01/15/2024",
        "CRASH TIME": "14:30",
        "BOROUGH": "MANHATTAN",
        "ZIP CODE": "10036",
        "LATITUDE": "40.7580",
        "LONGITUDE": "-73.9855",
        "ON STREET NAME": "BROADWAY",
        "CROSS STREET NAME": "W 45 ST",
        "OFF STREET NAME": "",
        "NUMBER OF PERSONS INJURED": "1",
        "NUMBER OF PERSONS KILLED": "0",
        "COLLISION_ID": identificador,
    }
    base.update(cambios)
    return base


def test_reglas_en_orden_y_conteos_exclusivos():
    datos = pd.DataFrame(
        [
            fila("valido-1"),
            fila("valido-2", BOROUGH="QUEENS"),
            fila("r1", LATITUDE=None),
            fila("r2", LATITUDE="0", LONGITUDE="0"),
            fila("r3", LATITUDE="91"),
            fila("r4", LONGITUDE="-70"),
            fila("r5", **{"CRASH DATE": "fecha-invalida"}),
            fila("valido-1", BOROUGH="BROOKLYN"),
        ]
    )

    limpio, reporte = limpiar_dataframe(datos)

    assert reporte == {
        "total_inicial": 8,
        "R1_coord_nulas_no_numericas": 1,
        "R2_coord_cero": 1,
        "R3_fuera_rango": 1,
        "R4_fuera_nyc": 1,
        "R5_fecha_hora": 1,
        "R6_duplicado": 1,
        "total_final": 2,
    }
    assert limpio["collision_id"].tolist() == ["valido-1", "valido-2"]


def test_documento_geojson_y_fecha():
    limpio, _ = limpiar_dataframe(pd.DataFrame([fila("abc-123")]))
    documento = a_documento(limpio.iloc[0].to_dict())

    assert documento["_id"] == "abc-123"
    assert documento["location"] == {
        "type": "Point",
        "coordinates": [-73.9855, 40.758],
    }
    assert documento["fecha"].year == 2024
    assert documento["hora"] == 14
    assert documento["dia_semana"] == 0


def test_no_deduplica_entre_particiones_cuando_se_desactiva_r6():
    datos = pd.DataFrame([fila("duplicado"), fila("duplicado")])
    limpio, reporte = limpiar_dataframe(datos, deduplicar=False)

    assert len(limpio) == 2
    assert reporte["R6_duplicado"] == 0
