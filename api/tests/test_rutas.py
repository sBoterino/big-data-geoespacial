from datetime import datetime, timezone

from app import create_app


class CursorFalso:
    def __init__(self, documentos):
        self.documentos = list(documentos)

    def limit(self, cantidad):
        self.documentos = self.documentos[:cantidad]
        return self

    def sort(self, campo, direccion):
        self.documentos.sort(key=lambda doc: doc.get(campo, 0), reverse=direccion < 0)
        return self

    def __iter__(self):
        return iter(self.documentos)


class ColeccionFalsa:
    def __init__(self, documentos=None):
        self.documentos = documentos or []
        self.ultima_consulta = None
        self.ultimo_pipeline = None

    def find(self, consulta):
        self.ultima_consulta = consulta
        return CursorFalso(self.documentos)

    def aggregate(self, pipeline):
        self.ultimo_pipeline = pipeline
        return iter(self.documentos)


class DBFalsaRutas:
    def __init__(self):
        self.colecciones = {
            "eventos": ColeccionFalsa(
                [{"_id": "uno", "fecha": datetime(2020, 1, 1, tzinfo=timezone.utc)}]
            ),
            "spark_hotspots": ColeccionFalsa([{"_id": "h1", "n": 12}]),
        }

    def __getitem__(self, nombre):
        return self.colecciones.setdefault(nombre, ColeccionFalsa())

    def command(self, _nombre):
        return {"ok": 1}

    def list_collection_names(self):
        return list(self.colecciones)


def cliente_rutas():
    db = DBFalsaRutas()
    return create_app(db=db).test_client(), db


def test_near_responde_parametros_y_serializa_fecha():
    cliente, db = cliente_rutas()
    respuesta = cliente.get("/near?lat=40.758&lon=-73.9855&radio=1000")
    cuerpo = respuesta.get_json()
    assert respuesta.status_code == 200
    assert cuerpo["total_devuelto"] == 1
    assert cuerpo["resultados"][0]["fecha"] == "2020-01-01T00:00:00+00:00"
    coordenadas = db["eventos"].ultima_consulta["location"]["$near"]["$geometry"]["coordinates"]
    assert coordenadas == [-73.9855, 40.758]


def test_near_invalido_devuelve_400_json():
    cliente, _db = cliente_rutas()
    respuesta = cliente.get("/near?lat=200&lon=0&radio=10")
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


def test_within_rechaza_poligono_abierto():
    cliente, _db = cliente_rutas()
    respuesta = cliente.post(
        "/within",
        json={
            "type": "Polygon",
            "coordinates": [[[-74, 40], [-73, 40], [-73, 41], [-74, 41]]],
        },
    )
    assert respuesta.status_code == 400


def test_geonear_usa_pipeline_con_operador_primero():
    cliente, db = cliente_rutas()
    respuesta = cliente.get(
        "/geonear?lat=40.758&lon=-73.9855&radio=1000&agrupar=grupo"
    )
    assert respuesta.status_code == 200
    assert list(db["eventos"].ultimo_pipeline[0]) == ["$geoNear"]


def test_spark_results_solo_expone_colecciones_permitidas():
    cliente, _db = cliente_rutas()
    listado = cliente.get("/spark-results")
    assert listado.get_json()["colecciones"] == ["hotspots"]
    assert cliente.get("/spark-results/usuarios").status_code == 400
    resultado = cliente.get("/spark-results/hotspots?limit=5&orden=n&desc=true")
    assert resultado.status_code == 200
    assert resultado.get_json()["resultados"][0]["n"] == 12
