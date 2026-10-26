"""Check the committed corpus: fixtures, manifest, and case list agree."""

import json
from pathlib import Path

import pytest

from crs.cases import CASES
from crs.geokeys import decode_geokeys

CRS_DIR = Path(__file__).parent.parent / "crs"
MANIFEST = json.loads((CRS_DIR / "manifest.json").read_text())
ROWS = {c["name"]: c for c in MANIFEST["cases"]}


def test_manifest_matches_case_list():
    assert sorted(ROWS) == sorted(c.name for c in CASES)
    assert [c["name"] for c in MANIFEST["cases"]] == sorted(ROWS)


@pytest.mark.parametrize("name", sorted(ROWS))
def test_fixture_geokeys_match_manifest(name: str):
    row = ROWS[name]
    path = CRS_DIR / row["file"]
    assert path.exists()
    assert not path.with_name(path.name + ".aux.xml").exists()
    assert decode_geokeys(path) == row["geokeys"]


def test_proj_cases_are_user_defined():
    for row in MANIFEST["cases"]:
        if row["input"]["kind"] != "proj" or row["gdal"]["projjson"] is None:
            continue
        keys = row["geokeys"]
        assert keys.get("ProjectedCSType", 32767) == 32767, row["name"]
        assert keys.get("GeographicType", 32767) == 32767, row["name"]


def test_flagged_rows():
    flagged = {
        r["name"]
        for r in MANIFEST["cases"]
        if r["gdal"]["projjson"] is None or r["gdal"]["proj4"] is None
    }
    assert flagged == {"eqearth", "stere_polar_scaled_wkt"}
    assert all(ROWS[n]["note"] for n in flagged)


def test_epsg_rows_have_cached_json():
    for row in MANIFEST["cases"]:
        if row["input"]["kind"] == "epsg":
            assert (CRS_DIR / row["epsg_json"]).exists(), row["name"]


def test_point_rows():
    for row in MANIFEST["cases"]:
        if row["gdal"]["proj4"] is not None:
            assert set(row["point"]) == {"lon", "lat", "x", "y"}, row["name"]
        else:
            assert row["point"] is None, row["name"]
