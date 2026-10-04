from __future__ import annotations

import dask.dataframe as dd
import pandas as pd

from pipeline_ingesta import contar_filas


def test_contar_filas_con_una_particion():
    dataframe = dd.from_pandas(pd.DataFrame({"valor": [1, 2, 3]}), npartitions=1)

    assert contar_filas(dataframe) == 3


def test_contar_filas_con_varias_particiones():
    dataframe = dd.from_pandas(pd.DataFrame({"valor": range(7)}), npartitions=3)

    assert contar_filas(dataframe) == 7
