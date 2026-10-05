import pytest

from app.validacion import ErrorValidacion, booleano, poligono, punto


def test_punto_valido_aplica_limit_por_defecto():
    assert punto({"lat": "40.758", "lon": "-73.9855", "radio": "1000"}) == (
        40.758,
        -73.9855,
        1000.0,
        100,
    )


@pytest.mark.parametrize(
    "parametros",
    [
        {"lat": "91", "lon": "0", "radio": "10"},
        {"lat": "0", "lon": "181", "radio": "10"},
        {"lat": "0", "lon": "0", "radio": "0"},
        {"lat": "0", "lon": "0", "radio": "50001"},
        {"lat": "0", "lon": "0", "radio": "10", "limit": "1.5"},
    ],
)
def test_punto_rechaza_limites_invalidos(parametros):
    with pytest.raises(ErrorValidacion):
        punto(parametros)


def test_poligono_acepta_geometry_envuelta():
    geometria = {
        "type": "Polygon",
        "coordinates": [[[-74, 40], [-73, 40], [-73, 41], [-74, 40]]],
    }
    assert poligono({"geometry": geometria}) == geometria


def test_poligono_rechaza_anillo_sin_cerrar():
    with pytest.raises(ErrorValidacion, match="cerrado"):
        poligono(
            {
                "type": "Polygon",
                "coordinates": [[[-74, 40], [-73, 40], [-73, 41], [-74, 41]]],
            }
        )


def test_booleano_exige_valor_reconocible():
    assert booleano("true", "desc") is True
    assert booleano("no", "desc") is False
    with pytest.raises(ErrorValidacion):
        booleano("quizás", "desc")
