"""Pruebas unitarias F7 para las transformaciones puras de Spark, sin MongoDB."""

import sys
import unittest

sys.path.insert(0, "/opt/jobs")

from pyspark.sql import SparkSession

from agregacion_grilla import agregar_por_celda, seleccionar_hotspots
from agregacion_temporal import agregar
from verificar_resultados import distancia_m


class PruebasAgregacionesSpark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = (
            SparkSession.builder.master("local[2]")
            .appName("f7-pruebas-agregaciones")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )
        cls.spark.sparkContext.setLogLevel("ERROR")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_grilla_cuenta_suma_y_construye_geojson_lon_lat(self):
        eventos = self.spark.createDataFrame(
            [
                (-73.984, 40.758, 1, 0),
                (-73.983, 40.759, 2, 1),
                (-73.974, 40.768, 4, 0),
            ],
            ["lon", "lat", "heridos", "muertos"],
        )
        filas = {fila["_id"]: fila.asDict(recursive=True)
                 for fila in agregar_por_celda(eventos, 0.005).collect()}

        self.assertEqual(len(filas), 2)
        principal = next(fila for fila in filas.values() if fila["n"] == 2)
        self.assertEqual(principal["heridos"], 3)
        self.assertEqual(principal["muertos"], 1)
        self.assertEqual(principal["celda"]["type"], "Polygon")
        anillo = principal["celda"]["coordinates"][0]
        self.assertEqual(len(anillo), 5)
        self.assertEqual(anillo[0], anillo[-1])
        self.assertLess(anillo[0][0], 0)  # primera coordenada = longitud
        self.assertGreater(anillo[0][1], 0)  # segunda coordenada = latitud

    def test_hotspots_desempatan_por_id_y_respetan_top(self):
        grilla = self.spark.createDataFrame(
            [("b", 10), ("a", 10), ("c", 5)], ["_id", "n"]
        )
        filas = seleccionar_hotspots(grilla, 2).orderBy("ranking").collect()
        self.assertEqual([(f["_id"], f["ranking"]) for f in filas], [("a", 1), ("b", 2)])

    def test_agregacion_temporal_cuenta_y_suma(self):
        eventos = self.spark.createDataFrame(
            [(8, "A", 1, 0), (8, "A", 2, 1), (9, "B", 4, 0)],
            ["hora", "borough", "heridos", "muertos"],
        )
        filas = agregar(eventos, ["hora"]).orderBy("hora").collect()
        self.assertEqual(
            [(f["hora"], f["n"], f["heridos"], f["muertos"]) for f in filas],
            [(8, 2, 3, 1), (9, 1, 4, 0)],
        )

    def test_haversine_cero_y_distancia_times_square(self):
        times_square = (40.7580, -73.9855)
        self.assertEqual(distancia_m(times_square, times_square), 0)
        self.assertLess(distancia_m(times_square, (40.7577, -73.9873)), 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
