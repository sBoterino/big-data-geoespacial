"""Pipeline distribuido e idempotente de Kaggle a MongoDB."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import dask
import dask.dataframe as dd
import pandas as pd
from dask import delayed
from distributed import Client, wait
from pymongo import ASCENDING, GEOSPHERE, MongoClient

from descarga import descargar_dataset
from limpieza import COLUMNAS_LIMPIAS, COLUMNAS_ORIGEN, REGLAS, a_documento, limpiar_dataframe, meta_limpio


PARQUET_COLUMNAS = ["latitude", "longitude", "fecha", "hora", "dia_semana", "mes", "anio", "borough"]


def _verdadero(nombre: str) -> bool:
    return os.getenv(nombre, "false").lower() in {"1", "true", "yes", "si", "sí"}


def _mongo_uri() -> str:
    usuario = quote_plus(os.getenv("MONGO_ROOT_USER", "admin"))
    clave = quote_plus(os.environ["MONGO_ROOT_PASSWORD"])
    host = os.getenv("MONGO_HOST", "mongodb")
    puerto = os.getenv("MONGO_PORT", "27017")
    return f"mongodb://{usuario}:{clave}@{host}:{puerto}/?authSource=admin"


def limitar_filas(dataframe: dd.DataFrame, limite: int) -> dd.DataFrame:
    """Conserva las primeras ``limite`` filas sin reunir todo el CSV en memoria."""

    if limite <= 0:
        return dataframe
    tamanos = dataframe.map_partitions(len).compute().tolist()
    partes: list[dd.DataFrame] = []
    restantes = limite
    for indice, tamano in enumerate(tamanos):
        if restantes <= 0:
            break
        particion = dataframe.partitions[indice]
        if tamano <= restantes:
            partes.append(particion)
            restantes -= tamano
        else:
            partes.append(
                particion.map_partitions(
                    lambda pdf, n: pdf.head(n), restantes, meta=dataframe._meta
                )
            )
            restantes = 0
    return dd.concat(partes, interleave_partitions=True) if partes else dataframe.head(0, compute=False)


def _insertar_particion(
    particion: pd.DataFrame, uri: str, base: str, coleccion: str, tamano_lote: int
) -> pd.DataFrame:
    if particion.empty:
        return pd.DataFrame({"insertados": pd.Series([0], dtype="int64")})
    cliente = MongoClient(uri)
    destino = cliente[base][coleccion]
    insertados = 0
    try:
        for inicio in range(0, len(particion), tamano_lote):
            registros = particion.iloc[inicio : inicio + tamano_lote].to_dict("records")
            documentos = [a_documento(registro) for registro in registros]
            if documentos:
                resultado = destino.insert_many(documentos, ordered=False)
                insertados += len(resultado.inserted_ids)
    finally:
        cliente.close()
    return pd.DataFrame({"insertados": pd.Series([insertados], dtype="int64")})


def _sumar_reportes(reportes: tuple[dict[str, int], ...]) -> dict[str, int]:
    total = {"total_inicial": 0, **{regla: 0 for regla in REGLAS}, "total_final": 0}
    for reporte in reportes:
        for clave in total:
            total[clave] += int(reporte.get(clave, 0))
    return total


def ejecutar() -> None:
    inicio = time.perf_counter()
    dataset = os.getenv("KAGGLE_DATASET", "muzammilrizvi1/motor-vehicle-collisions-crashes")
    max_filas = int(os.getenv("INGEST_MAX_ROWS", "0"))
    tamano_lote = int(os.getenv("INGEST_BATCH_SIZE", "5000"))
    forzar = _verdadero("FORCE_RELOAD")
    base = os.getenv("MONGO_DB", "geo")
    coleccion = os.getenv("MONGO_COLLECTION", "eventos")
    clave_meta = f"{dataset}|max_rows={max_filas}"
    uri = _mongo_uri()

    mongo = MongoClient(uri)
    db = mongo[base]
    meta = db["ingesta_meta"].find_one({"_id": clave_meta, "estado": "completa"})
    if meta and not forzar and db[coleccion].count_documents({}) == meta.get("total_final"):
        print(
            f"[ingesta] Ingesta omitida: {meta['total_final']:,} documentos ya corresponden a {clave_meta}."
        )
        mongo.close()
        return

    db["ingesta_meta"].update_one(
        {"_id": clave_meta},
        {"$set": {"dataset": dataset, "max_rows": max_filas, "estado": "en_progreso", "inicio": datetime.now(timezone.utc)}},
        upsert=True,
    )

    cliente_dask: Client | None = None
    try:
        csv = descargar_dataset(dataset)
        cliente_dask = Client(os.getenv("DASK_SCHEDULER", "tcp://dask-scheduler:8786"))
        cliente_dask.wait_for_workers(2, timeout=120)
        print(f"[ingesta] workers conectados: {len(cliente_dask.scheduler_info()['workers'])}")

        raw = dd.read_csv(
            csv,
            blocksize="64MB",
            dtype=str,
            usecols=COLUMNAS_ORIGEN,
            on_bad_lines="skip",
        )
        raw = limitar_filas(raw, max_filas)
        print(f"[ingesta] particiones Dask: {raw.npartitions}")

        resultados = [delayed(limpiar_dataframe)(parte, deduplicar=False) for parte in raw.to_delayed()]
        limpio = dd.from_delayed([resultado[0] for resultado in resultados], meta=meta_limpio())
        persistidos = dask.persist(limpio, *[resultado[1] for resultado in resultados])
        limpio = persistidos[0]
        reportes = dask.compute(*persistidos[1:])
        reporte = _sumar_reportes(reportes)

        antes_duplicados = reporte["total_final"]
        limpio = limpio.drop_duplicates(subset=["collision_id"], keep="first")
        limpio = cliente_dask.persist(limpio)
        wait(limpio)
        total_final = int(limpio.map_partitions(len).sum().compute())
        reporte["R6_duplicado"] = antes_duplicados - total_final
        reporte["total_final"] = total_final

        destino = db[coleccion]
        if "location_2dsphere" in destino.index_information():
            destino.drop_index("location_2dsphere")
        destino.delete_many({})

        insertados = int(
            limpio.map_partitions(
                _insertar_particion,
                uri,
                base,
                coleccion,
                tamano_lote,
                meta={"insertados": "int64"},
            )["insertados"].sum().compute()
        )
        if insertados != total_final or destino.count_documents({}) != total_final:
            raise RuntimeError(
                f"Conteo inconsistente: esperados={total_final}, insertados={insertados}, Mongo={destino.count_documents({})}"
            )

        destino.create_index([("location", GEOSPHERE)], name="location_2dsphere")
        destino.create_index([("fecha", ASCENDING)], name="fecha_1")

        parquet = Path("/data/parquet/eventos")
        limpio[PARQUET_COLUMNAS].to_parquet(
            parquet, engine="pyarrow", write_index=False, overwrite=True
        )

        duracion = round(time.perf_counter() - inicio, 3)
        evidencia = {
            "dataset": dataset,
            "archivo": str(csv),
            "max_rows": max_filas,
            "particiones": raw.npartitions,
            "reporte": reporte,
            "insertados": insertados,
            "duracion_segundos": duracion,
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
        }
        Path("/data/reporte_limpieza.json").write_text(
            json.dumps(evidencia, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        db["ingesta_meta"].update_one(
            {"_id": clave_meta},
            {"$set": {**evidencia, "estado": "completa", "total_final": total_final, "fin": datetime.now(timezone.utc)}},
            upsert=True,
        )
        print(json.dumps(evidencia, indent=2, ensure_ascii=False))
        print(f"[ingesta] COMPLETA: {insertados:,} documentos en {duracion:.1f} s")
    except Exception as exc:
        db["ingesta_meta"].update_one(
            {"_id": clave_meta},
            {"$set": {"estado": "error", "error": str(exc)[:500], "fin": datetime.now(timezone.utc)}},
            upsert=True,
        )
        try:
            db[coleccion].create_index([("location", GEOSPHERE)], name="location_2dsphere")
        except Exception:
            pass
        raise
    finally:
        if cliente_dask is not None:
            cliente_dask.close()
        mongo.close()


if __name__ == "__main__":
    ejecutar()
