from app import config


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"
    assert r.get_json()["mongo"] == "ok"
    assert r.get_json()["coleccion"] == "eventos"


def test_health_sin_mongo_devuelve_503(client_sin_mongo):
    r = client_sin_mongo.get("/health")
    assert r.status_code == 503
    assert r.get_json()["status"] == "error"


def test_ruta_inexistente_devuelve_json_404(client):
    r = client.get("/no-existe")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_uri_escapa_caracteres_especiales(monkeypatch):
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.setenv("MONGO_ROOT_USER", "admin")
    monkeypatch.setenv("MONGO_ROOT_PASSWORD", "p@ss:word")
    uri = config.mongo_uri()
    assert "p%40ss%3Aword" in uri
    assert uri.endswith("authSource=admin")
