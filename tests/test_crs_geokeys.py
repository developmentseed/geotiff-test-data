"""Check the raw GeoKey decoder and encoder used by the CRS corpus."""

from pathlib import Path

import numpy as np
import tifffile

from crs.geokeys import GEOKEY_IDS, decode_geokeys, encode_geokeys

REPO_ROOT = Path(__file__).parent.parent


def test_geokey_ids_cover_spec():
    assert GEOKEY_IDS["GTModelType"] == 1024
    assert GEOKEY_IDS["GeogTOWGS84"] == 2062
    assert GEOKEY_IDS["ProjRectifiedGridAngle"] == 3096
    assert GEOKEY_IDS["CoordinateEpoch"] == 5120
    assert len(GEOKEY_IDS) == 48


def test_decode_existing_fixture():
    keys = decode_geokeys(
        REPO_ROOT / "real_data/source-coop-dataforcanada/O2308000_7586000_cog.tif"
    )
    assert keys == {
        "GTModelType": 1,
        "GTRasterType": 1,
        "GTCitation": "NAD83(CSRS) / New Brunswick Stereographic",
        "GeographicType": 32767,
        "GeogCitation": "GCS Name = NAD83(CSRS)|Primem = Greenwich|",
        "GeogGeodeticDatum": 6140,
        "GeogAngularUnits": 9102,
        "GeogSemiMajorAxis": 6378137.0,
        "GeogInvFlattening": 298.257222101,
        "GeogPrimeMeridianLong": 0.0,
        "ProjectedCSType": 32767,
        "Projection": 32767,
        "ProjCoordTrans": 16,
        "ProjLinearUnits": 9001,
        "ProjNatOriginLong": -66.5,
        "ProjNatOriginLat": 46.5,
        "ProjFalseEasting": 2500000.0,
        "ProjFalseNorthing": 7500000.0,
        "ProjScaleAtNatOrigin": 0.999912,
    }


def test_encode_decode_roundtrip(tmp_path: Path):
    keys = {
        "GTModelType": 1,
        "GTRasterType": 1,
        "GeographicType": 32767,
        "GeogCitation": "GCS Name = unknown|Primem = Paris|",
        "GeogPrimeMeridian": 8903,
        "GeogSemiMajorAxis": 6378249.2,
        "GeogTOWGS84": [598.1, 73.7, 418.2, 0.202, 0.045, -2.455, 6.7],
        "ProjCoordTrans": 9,
        "ProjRectifiedGridAngle": 90.0,
    }
    path = tmp_path / "keys.tif"
    tifffile.imwrite(path, np.zeros((8, 8), np.uint8), extratags=encode_geokeys(keys))
    assert decode_geokeys(path) == keys


def test_decode_three_value_towgs84(tmp_path: Path):
    keys = {"GTModelType": 2, "GeogTOWGS84": [0.0, 0.0, 0.0]}
    path = tmp_path / "keys.tif"
    tifffile.imwrite(path, np.zeros((8, 8), np.uint8), extratags=encode_geokeys(keys))
    assert decode_geokeys(path)["GeogTOWGS84"] == [0.0, 0.0, 0.0]
