"""Generate a big endian (MM) float32 GeoTIFF with LERC compression."""

import tempfile
from pathlib import Path

import numpy as np
import rasterio

from rasterio_generated.write_utils import rewrite_big_endian, write_cog

HERE = Path(__file__).parent


def generate_source(output_path: Path) -> None:
    """Generate the little endian COG this fixture is rewritten from."""
    data = np.arange(128 * 128, dtype=np.float32).reshape(128, 128) / 16 - 512

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="LERC",
        nodata_type=None,
    )


def check_no_nan_after_byte_swap(path: Path) -> None:
    """Raise if any value, at any level, has a NaN bit pattern once byte-swapped."""
    with rasterio.open(path) as src:
        levels = [src.read()]
        overview_count = len(src.overviews(1))
    for level in range(overview_count):
        with rasterio.open(path, overview_level=level) as src:
            levels.append(src.read())

    for level, data in enumerate(levels):
        count = int(np.isnan(data.byteswap()).sum())
        if count:
            raise ValueError(
                f"{count} values at level {level} are NaN once byte-swapped, "
                "and GDAL loses those in a big endian LERC file"
            )


def generate(output_path: Path) -> None:
    """Generate a 128x128 tiled float32 big endian GeoTIFF with LERC compression.

    libtiff swaps samples into the file's byte order before passing them to any
    codec, so the LERC data in this file holds byte-swapped values. Readers must
    swap the samples LERC decodes, just as they do for raw codecs like DEFLATE.

    GDAL loses any value whose byte-swapped bits are a NaN: LERC stores NaN as an
    invalid pixel, so GDAL reads it back as a byte-swapped NaN (6.9e-41). The
    values here are multiples of 1/16 between -512 and 512, so the low byte of
    every mantissa is zero and no value swaps to a NaN.
    """
    with tempfile.TemporaryDirectory() as tmp:
        src_path = Path(tmp) / "source.tif"
        generate_source(src_path)
        check_no_nan_after_byte_swap(src_path)
        rewrite_big_endian(src_path, output_path)
