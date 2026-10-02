import pytest

from app import create_app


class DBFalsa:
    """Doble de prueba mínimo de una base de datos de pymongo."""

    def __init__(self, disponible=True):
        self.disponible = disponible

    def command(self, nombre):
        if not self.disponible:
            raise ConnectionError("MongoDB no disponible")
        return {"ok": 1}


@pytest.fixture
def client():
    return create_app(db=DBFalsa()).test_client()


@pytest.fixture
def client_sin_mongo():
    return create_app(db=DBFalsa(disponible=False)).test_client()
