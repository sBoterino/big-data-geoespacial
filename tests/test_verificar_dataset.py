import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd


RUTA_SCRIPT = Path(__file__).parents[1] / "scripts" / "verificar_dataset.py"
SPEC = importlib.util.spec_from_file_location("verificar_dataset", RUTA_SCRIPT)
verificador = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verificador)


class PruebasVerificadorDataset(unittest.TestCase):
    def test_detectar_columnas_normaliza_mayusculas_y_espacios(self):
        columnas = [" pickup_LATITUDE ", "Start_Lng", "CRASH DATE", "CRASH TIME"]

        lat, lon, fechas = verificador.detectar_columnas(columnas)

        self.assertEqual(lat, " pickup_LATITUDE ")
        self.assertEqual(lon, "Start_Lng")
        self.assertEqual(fechas, ["CRASH DATE", "CRASH TIME"])

    def test_perfilar_clasifica_cada_registro_una_sola_vez(self):
        bloques = [
            pd.DataFrame(
                {
                    "LATITUDE": [40.75, None, 0, 91, "40.71"],
                    "LONGITUDE": [-73.99, -73.9, 0, -73, "-74.01"],
                    "CRASH DATE": ["01/01/2024"] * 5,
                    "CRASH TIME": ["12:00"] * 5,
                }
            ),
            pd.DataFrame(
                {
                    "LATITUDE": [-90, 45, "texto", 0],
                    "LONGITUDE": [180, 181, -70, -73],
                    "CRASH DATE": ["01/02/2024"] * 4,
                    "CRASH TIME": ["13:00"] * 4,
                }
            ),
        ]

        resultado = verificador.perfilar(iter(bloques))

        self.assertEqual(
            resultado,
            {
                "registros": 9,
                "coord_nulas": 1,
                "coord_no_numericas": 1,
                "coord_cero": 1,
                "fuera_de_rango": 2,
                "validos": 4,
                "col_lat": "LATITUDE",
                "col_lon": "LONGITUDE",
                "cols_fecha": ["CRASH DATE", "CRASH TIME"],
            },
        )
        self.assertEqual(
            resultado["registros"],
            sum(
                resultado[categoria]
                for categoria in (
                    "coord_nulas",
                    "coord_no_numericas",
                    "coord_cero",
                    "fuera_de_rango",
                    "validos",
                )
            ),
        )

    def test_perfilar_sin_columnas_geo_conserva_el_total_de_filas(self):
        bloques = [
            pd.DataFrame({"fecha": ["2024-01-01", "2024-01-02"], "x": [1, 2]}),
            pd.DataFrame({"fecha": ["2024-01-03"], "x": [3]}),
        ]

        resultado = verificador.perfilar(iter(bloques))

        self.assertEqual(resultado["registros"], 3)
        self.assertIn("No se detectaron columnas lat/lon", resultado["error"])

    def test_bloques_de_lee_csv_por_bloques(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "eventos.csv"
            pd.DataFrame(
                {"latitude": [1, 2, 3], "longitude": [4, 5, 6]}
            ).to_csv(ruta, index=False)

            bloques = list(verificador.bloques_de(ruta, tam=2))

        self.assertEqual([len(bloque) for bloque in bloques], [2, 1])
        self.assertEqual(verificador.perfilar(iter(bloques))["validos"], 3)

    def test_bloques_de_elige_la_tabla_sqlite_mas_grande(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "eventos.sqlite"
            conexion = sqlite3.connect(ruta)
            try:
                pd.DataFrame({"latitude": [1], "longitude": [2]}).to_sql(
                    "pequena", conexion, index=False
                )
                pd.DataFrame(
                    {"latitude": [1, 2, 3], "longitude": [4, 5, 6]}
                ).to_sql("principal", conexion, index=False)
            finally:
                conexion.close()

            bloques = list(verificador.bloques_de(ruta, tam=2))

        self.assertEqual([len(bloque) for bloque in bloques], [2, 1])
        self.assertEqual(verificador.perfilar(iter(bloques))["registros"], 3)


if __name__ == "__main__":
    unittest.main()
