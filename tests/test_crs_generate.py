"""Check the corpus generator: writing, reading back, manifest rows, EPSG cache."""

from pathlib import Path

import pytest

from crs.cases import Case
from crs.generate_crs import fetch_epsg_json, manifest_row, read_back, write_case

TMERC = Case(
    "tmerc",
    "proj",
    "+proj=tmerc +lat_0=0 +lon_0=-3.5 +k=0.9996 +x_0=500000 +y_0=0 +ellps=WGS84",
)


def test_write_and_read_back_proj_case(tmp_path: Path):
    path = tmp_path / "tmerc.tif"
    write_case(TMERC, path)
    assert not (tmp_path / "tmerc.tif.aux.xml").exists()
    crs = read_back(path)
    assert crs is not None
    assert crs.coordinate_operation.method_code == "9807"


def test_manifest_row_proj_case(tmp_path: Path):
    path = tmp_path / "fixtures" / "tmerc.tif"
    path.parent.mkdir()
    write_case(TMERC, path)
    row = manifest_row(TMERC, path, tmp_path)
    assert row["file"] == "fixtures/tmerc.tif"
    assert row["input"] == {"kind": "proj", "value": TMERC.value}
    assert row["geokeys"]["ProjCoordTrans"] == 1
    assert row["geokeys"]["ProjectedCSType"] == 32767
    assert row["gdal"]["roundtrip"] is True
    assert row["gdal"]["proj4"].startswith("+proj=tmerc +lat_0=0 +lon_0=-3.5")
    assert row["gdal"]["projjson"]["type"] == "ProjectedCRS"
    assert row["core"]["method"]["epsg"] == 9807
    assert row["point"]["lon"] == -0.5 and row["point"]["lat"] == 8.0
    assert row["epsg_json"] is None


def test_manifest_row_keyless_case(tmp_path: Path):
    case = Case(
        "eqearth", "proj", "+proj=eqearth +lon_0=0 +ellps=WGS84", note="no keys"
    )
    path = tmp_path / "eqearth.tif"
    write_case(case, path)
    row = manifest_row(case, path, tmp_path)
    assert row["gdal"] == {"projjson": None, "proj4": None, "roundtrip": None}
    assert row["core"] is None and row["point"] is None
    assert row["note"] == "no keys"


def test_manifest_row_geokeys_case(tmp_path: Path):
    case = Case(
        "pm_epsg",
        "geokeys",
        {
            "GTModelType": 2,
            "GTRasterType": 1,
            "GeographicType": 32767,
            "GeogGeodeticDatum": 32767,
            "GeogEllipsoid": 7030,
            "GeogPrimeMeridian": 8903,
            "GeogAngularUnits": 9102,
        },
    )
    path = tmp_path / "pm_epsg.tif"
    write_case(case, path)
    row = manifest_row(case, path, tmp_path)
    assert row["geokeys"] == case.value
    assert row["gdal"]["roundtrip"] is None
    assert row["core"]["prime_meridian_deg"] == pytest.approx(2.33722917)


def test_manifest_row_epsg_case(tmp_path: Path):
    case = Case("epsg_32633", "epsg", "EPSG:32633")
    path = tmp_path / "epsg_32633.tif"
    write_case(case, path)
    row = manifest_row(case, path, tmp_path)
    assert row["geokeys"]["ProjectedCSType"] == 32633
    assert row["epsg_json"] == "epsg/32633.json"


def _no_network(*args, **kwargs):
    raise AssertionError("network used")


def test_fetch_epsg_json_skips_existing(tmp_path: Path, monkeypatch):
    existing = tmp_path / "32633.json"
    existing.write_text("{}")
    monkeypatch.setattr("urllib.request.urlopen", _no_network)
    assert fetch_epsg_json(32633, tmp_path) == existing


class _Response:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self) -> bytes:
        return self.body


def test_fetch_epsg_json_identifies_itself(tmp_path: Path, monkeypatch):
    """epsg.io answers 403 to urllib's default User-Agent."""
    seen = {}

    def fake_urlopen(request, timeout=None):
        seen["url"] = request.full_url
        seen["user_agent"] = request.get_header("User-agent")
        return _Response(b'{"code": "4267"}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    path = fetch_epsg_json(4267, tmp_path)
    assert seen["url"] == "https://epsg.io/4267.json"
    assert seen["user_agent"] and "geotiff-test-data" in seen["user_agent"]
    assert path.read_bytes() == b'{"code": "4267"}'
