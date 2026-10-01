"""Check that write_cog applies every option it is given, or refuses it.

GDAL only warns when it ignores a creation option, and rasterio sends that
warning to a logger the generators never show, so an ignored option silently
produces a fixture without it.
"""

import logging
from pathlib import Path

import numpy as np
import pytest
import rasterio
import tifffile

from rasterio_generated.write_utils import write_cog

UINT8_RGB = np.zeros((3, 128, 128), dtype=np.uint8)
UINT16 = np.arange(128 * 128, dtype=np.uint16).reshape(128, 128)
FLOAT32 = np.linspace(0.0, 1.0, 128 * 128, dtype=np.float32).reshape(128, 128)


def read_predictors(path: Path) -> list[int]:
    """Read the predictor of every IFD."""
    with tifffile.TiffFile(path) as tif:
        return [int(page.predictor) for page in tif.pages]


@pytest.mark.parametrize("compress", [None, "DEFLATE", "LZW", "ZSTD"])
def test_predictor_2(compress: str | None, tmp_path: Path):
    path = tmp_path / "out.tif"
    write_cog(path, UINT16, blocksize=64, compress=compress, predictor=2)
    assert read_predictors(path) == [2, 2]


def test_predictor_3(tmp_path: Path):
    path = tmp_path / "out.tif"
    write_cog(path, FLOAT32, blocksize=64, predictor=3, nodata_type=None)
    assert read_predictors(path) == [3, 3]


# GDAL drops the predictor for these codecs: with LZMA it doesn't even warn.
@pytest.mark.parametrize("compress", ["JPEG", "LERC", "LZMA", "PACKBITS", "WEBP"])
def test_predictor_with_unsupported_codec_raises(compress: str, tmp_path: Path):
    with pytest.raises(ValueError, match="predictor"):
        write_cog(
            tmp_path / "out.tif",
            UINT8_RGB,
            blocksize=64,
            compress=compress,
            predictor=2,
        )


@pytest.mark.parametrize(("nodata", "expected"), [(None, 0), (255, 255)])
def test_nodata(nodata: int | None, expected: int, tmp_path: Path):
    path = tmp_path / "out.tif"
    write_cog(path, UINT16, blocksize=64, nodata=nodata)
    with rasterio.open(path) as src:
        assert src.nodata == expected


@pytest.mark.parametrize(
    ("scale", "offset", "expected"),
    [
        (0.01, None, (0.01, 0.0)),
        (None, 100.0, (1.0, 100.0)),
        (0.01, 100.0, (0.01, 100.0)),
    ],
)
def test_scale_and_offset(
    scale: float | None,
    offset: float | None,
    expected: tuple[float, float],
    tmp_path: Path,
):
    path = tmp_path / "out.tif"
    write_cog(path, UINT16, blocksize=64, scale=scale, offset=offset)
    with rasterio.open(path) as src:
        assert (src.scales[0], src.offsets[0]) == expected


def test_no_ignored_creation_options(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    # A block size under 128 makes GDAL warn even though it honors it, so use 128.
    caplog.set_level(logging.WARNING, logger="rasterio")
    write_cog(tmp_path / "out.tif", UINT16, blocksize=128)
    assert [record.getMessage() for record in caplog.records] == []
