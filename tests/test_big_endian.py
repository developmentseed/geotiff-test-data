"""Check the big endian fixtures.

GDAL's COG driver can't write big endian files, so these fixtures are rewritten
from a little endian COG through the GTiff driver. Check that they really are
big endian, carry the predictor they are named for on every IFD, and hold the
same pixels as their little endian source at every level.
"""

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest
import rasterio
import tifffile

from rasterio_generated.fixtures import (
    float32_1band_deflate_block64_predictor3_big_endian as float32_predictor3,
)
from rasterio_generated.fixtures import (
    uint16_1band_lzw_block128_predictor2 as uint16_predictor2,
)

FIXTURES_DIR = Path(__file__).parent.parent / "rasterio_generated" / "fixtures"

CASES = [
    (
        "uint16_1band_lzw_block128_predictor2_big_endian",
        2,
        uint16_predictor2.generate,
    ),
    (
        "float32_1band_deflate_block64_predictor3_big_endian",
        3,
        float32_predictor3.generate_source,
    ),
]


def read_levels(path: Path) -> list[np.ndarray]:
    """Read the full resolution image and every overview."""
    with rasterio.open(path) as src:
        levels = [src.read()]
        overview_count = len(src.overviews(1))
    for level in range(overview_count):
        with rasterio.open(path, overview_level=level) as src:
            levels.append(src.read())
    return levels


@pytest.mark.parametrize(("name", "predictor", "generate_source"), CASES)
def test_big_endian_fixture(
    name: str,
    predictor: int,
    generate_source: Callable[[Path], None],
    tmp_path: Path,
):
    path = FIXTURES_DIR / f"{name}.tif"
    assert path.read_bytes()[:2] == b"MM"

    with tifffile.TiffFile(path) as tif:
        assert len(tif.pages) > 1
        assert [int(page.predictor) for page in tif.pages] == [predictor] * len(
            tif.pages
        )

    source_path = tmp_path / "source.tif"
    generate_source(source_path)
    assert source_path.read_bytes()[:2] == b"II"

    actual = read_levels(path)
    expected = read_levels(source_path)
    assert len(actual) == len(expected)
    for actual_level, expected_level in zip(actual, expected):
        np.testing.assert_array_equal(actual_level, expected_level)
