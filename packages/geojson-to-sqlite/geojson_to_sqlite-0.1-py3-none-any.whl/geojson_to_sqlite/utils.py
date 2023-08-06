from shapely.geometry import shape
import sqlite_utils
import os

SPATIALITE_PATHS = (
    "/usr/lib/x86_64-linux-gnu/mod_spatialite.so",
    "/usr/local/lib/mod_spatialite.dylib",
)


class SpatiaLiteError(Exception):
    pass


def import_features(
    db_path,
    table,
    features,
    pk=None,
    alter=False,
    spatialite=False,
    spatialite_mod=None,
):
    db = sqlite_utils.Database(db_path)
    conversions = {}
    if spatialite_mod:
        spatialite = True
    if spatialite:
        lib = spatialite_mod or find_spatialite()
        if not lib:
            raise SpatiaLiteError("Could not find SpatiaLite module")
        init_spatialite(db, lib)
        ensure_table_has_geometry(db, table)
        conversions = {"geometry": "GeomFromText(?, 4326)"}

    def yield_records():
        for feature in features:
            record = feature.get("properties") or {}
            if spatialite:
                record["geometry"] = shape(feature["geometry"]).wkt
            else:
                record["geometry"] = feature["geometry"]
            yield record

    if pk:
        db[table].upsert_all(
            yield_records(), conversions=conversions, pk=pk, alter=alter
        )
    else:
        db[table].insert_all(yield_records(), conversions=conversions)
    return db[table]


def find_spatialite():
    for path in SPATIALITE_PATHS:
        if os.path.exists(path):
            return path
    return None


def init_spatialite(db, lib):
    db.conn.enable_load_extension(True)
    db.conn.load_extension(lib)
    # Initialize SpatiaLite if not yet initialized
    if "spatial_ref_sys_all" in db.table_names():
        return
    db.conn.execute("select InitSpatialMetadata(1)")


def ensure_table_has_geometry(db, table):
    if "geometry" not in db[table].columns_dict:
        db.conn.execute(
            "SELECT AddGeometryColumn(?, 'geometry', 4326, 'MULTIPOLYGON', 2);", [table]
        )
