"""Check the raw GeoKeys of real_data fixtures.

Some fixtures exist to exercise a specific GeoKey layout, which regenerating
them with GDAL can silently change: GDAL may identify a user-defined CRS as an
EPSG code and write only that code. Reading the raw keys with async-tiff
catches that.
"""

import asyncio
from pathlib import Path
from typing import Any

from async_tiff import TIFF
from async_tiff.store import LocalStore

REPO_ROOT = Path(__file__).parent.parent


def read_geo_keys(path: str) -> dict[str, Any]:
    """Read the GeoKeys of the first IFD of a TIFF, relative to the repo root."""

    async def _read() -> dict[str, Any]:
        tiff = await TIFF.open(path, store=LocalStore(REPO_ROOT))
        gkd = tiff.ifds[0].geo_key_directory
        return {key: gkd[key] for key in gkd.keys()}

    return asyncio.run(_read())


def test_dataforcanada_user_defined_oblique_stereographic():
    """Assert that CRS is stored in custom geo keys, not simply as `EPSG:2953`.

    See real_data/source-coop-dataforcanada/README.md.
    """
    geo_keys = read_geo_keys(
        "real_data/source-coop-dataforcanada/O2308000_7586000_cog.tif"
    )
    assert geo_keys == {
        "model_type": 1,
        "raster_type": 1,
        "citation": "NAD83(CSRS) / New Brunswick Stereographic",
        "geographic_type": 32767,
        "geog_citation": "GCS Name = NAD83(CSRS)|Primem = Greenwich|",
        "geog_geodetic_datum": 6140,
        "geog_angular_units": 9102,
        "geog_semi_major_axis": 6378137.0,
        "geog_inv_flattening": 298.257222101,
        "geog_prime_meridian_long": 0.0,
        "projected_type": 32767,
        "projection": 32767,
        "proj_coord_trans": 16,
        "proj_linear_units": 9001,
        "proj_nat_origin_long": -66.5,
        "proj_nat_origin_lat": 46.5,
        "proj_false_easting": 2500000.0,
        "proj_false_northing": 7500000.0,
        "proj_scale_at_nat_origin": 0.999912,
    }
