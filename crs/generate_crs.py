"""Generate the CRS conformance corpus: fixtures, manifest, and epsg.io cache.

Run with ``pixi run generate-crs`` (``--refresh-epsg`` refetches the cached
epsg.io responses). GDAL writes each fixture from the case's input, reads it
back, and the manifest records both sides. See ``crs/README.md``.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import numpy as np
import pyproj
import rasterio
import tifffile
from pyproj import CRS
from pyproj.exceptions import CRSError
from rasterio.transform import from_origin

from crs.cases import CASES, EPSG_CODES, Case
from crs.geokeys import decode_geokeys, encode_geokeys
from crs.normalize import core_of, point_for, project_point

SCHEMA_VERSION = 1
EPSG_IO_URL = "https://epsg.io/{code}.json"
_SIZE = 8


def write_case(case: Case, path: Path) -> None:
    """Write the fixture for ``case`` at ``path`` with no sidecar files."""
    data = np.zeros((_SIZE, _SIZE), dtype=np.uint8)
    if case.kind == "geokeys":
        assert isinstance(case.value, dict)
        tifffile.imwrite(path, data, extratags=encode_geokeys(case.value))
        return

    assert isinstance(case.value, str)
    crs = CRS.from_user_input(case.value)
    with (
        rasterio.Env(GDAL_PAM_ENABLED="NO"),
        rasterio.open(
            path,
            "w",
            driver="GTiff",
            width=_SIZE,
            height=_SIZE,
            count=1,
            dtype="uint8",
            crs=crs,
            transform=from_origin(0, 0, 10, 10),
        ) as dst,
    ):
        dst.write(data, 1)


def read_back(path: Path) -> CRS | None:
    """The CRS GDAL reads from the TIFF alone, or None when it reads none."""
    with rasterio.Env(GDAL_PAM_ENABLED="NO"), rasterio.open(path) as src:
        if not src.crs:
            return None
        return CRS.from_user_input(src.crs)


def _authority_code(value: str) -> int:
    """The numeric part of an ``AUTHORITY:code`` string."""
    return int(value.split(":", 1)[1])


def manifest_row(case: Case, path: Path, crs_dir: Path) -> dict:
    """One manifest row for a written fixture."""
    crs = read_back(path)
    gdal: dict = {"projjson": None, "proj4": None, "roundtrip": None}
    core = None
    point = None

    if crs is not None:
        gdal["projjson"] = crs.to_json_dict()
        try:
            gdal["proj4"] = crs.to_proj4()
        except CRSError:
            gdal["proj4"] = None
        if case.kind != "geokeys":
            assert isinstance(case.value, str)
            gdal["roundtrip"] = CRS.from_user_input(case.value).equals(crs)
        core = core_of(crs)
        if gdal["proj4"] is not None:
            lon, lat = point_for(core)
            x, y = project_point(crs, lon, lat)
            point = {"lon": lon, "lat": lat, "x": x, "y": y}

    epsg_json = None
    if case.kind == "epsg":
        assert isinstance(case.value, str)
        epsg_json = f"epsg/{_authority_code(case.value)}.json"

    return {
        "name": case.name,
        "file": path.relative_to(crs_dir).as_posix(),
        "input": {"kind": case.kind, "value": case.value},
        "note": case.note,
        "tags": list(case.tags),
        "geokeys": decode_geokeys(path),
        "gdal": gdal,
        "core": core,
        "point": point,
        "epsg_json": epsg_json,
    }


def fetch_epsg_json(code: int, epsg_dir: Path, *, refresh: bool = False) -> Path:
    """Cache ``https://epsg.io/<code>.json``; only hits the network when needed."""
    path = epsg_dir / f"{code}.json"
    if path.exists() and not refresh:
        return path
    epsg_dir.mkdir(parents=True, exist_ok=True)
    # epsg.io answers 403 to urllib's default User-Agent.
    request = urllib.request.Request(
        EPSG_IO_URL.format(code=code),
        headers={
            "User-Agent": "geotiff-test-data corpus generator (+https://github.com/developmentseed/geotiff-test-data)"
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        path.write_bytes(response.read())
    return path


def generate(crs_dir: Path, *, refresh_epsg: bool = False) -> dict:
    """Write every fixture, cache the EPSG JSON, and write the manifest."""
    fixtures_dir = crs_dir / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    epsg_dir = crs_dir / "epsg"

    rows = []
    for case in CASES:
        path = fixtures_dir / f"{case.name}.tif"
        write_case(case, path)
        rows.append(manifest_row(case, path, crs_dir))
        print(f"✓ Generated: {path.relative_to(crs_dir.parent)}")

    for code in EPSG_CODES:
        fetch_epsg_json(code, epsg_dir, refresh=refresh_epsg)
    for case in CASES:
        if (
            case.kind == "epsg"
            and isinstance(case.value, str)
            and not case.value.startswith("EPSG:")
        ):
            fetch_epsg_json(_authority_code(case.value), epsg_dir, refresh=refresh_epsg)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generator": {
            "gdal": rasterio.__gdal_version__,
            "proj": rasterio.__proj_version__,
            "rasterio": rasterio.__version__,
            "pyproj": pyproj.__version__,
        },
        "cases": sorted(rows, key=lambda row: row["name"]),
    }
    with (crs_dir / "manifest.json").open("w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"\nComplete! {len(rows)} cases in {crs_dir / 'manifest.json'}")
    return manifest


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-epsg", action="store_true", help="refetch cached epsg.io JSON"
    )
    args = parser.parse_args()
    generate(Path(__file__).parent, refresh_epsg=args.refresh_epsg)


if __name__ == "__main__":
    main()
