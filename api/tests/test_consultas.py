from app.consultas import filtro_near, filtro_within, pipeline_geonear


def test_near_usa_longitud_latitud_y_distancia():
    consulta = filtro_near(40.758, -73.9855, 1000)
    near = consulta["location"]["$near"]
    assert near["$geometry"]["coordinates"] == [-73.9855, 40.758]
    assert near["$maxDistance"] == 1000


def test_within_conserva_el_poligono_parametrico():
    geometria = {"type": "Polygon", "coordinates": [[[-74, 40], [-73, 40], [-74, 40]]]}
    assert filtro_within(geometria) == {
        "location": {"$geoWithin": {"$geometry": geometria}}
    }


def test_geonear_siempre_es_primera_etapa():
    pipeline = pipeline_geonear(40.758, -73.9855, 1000, 25)
    assert list(pipeline[0]) == ["$geoNear"]
    assert pipeline[0]["$geoNear"]["near"]["coordinates"] == [-73.9855, 40.758]
    assert pipeline[-1] == {"$limit": 25}


def test_geonear_agrupa_y_calcula_distancia_media():
    pipeline = pipeline_geonear(40.758, -73.9855, 1000, 10, "hora")
    assert pipeline[1]["$group"]["_id"] == "$hora"
    assert pipeline[1]["$group"]["n"] == {"$sum": 1}
    assert "distancia_media_m" in pipeline[1]["$group"]
