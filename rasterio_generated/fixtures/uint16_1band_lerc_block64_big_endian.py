"""Generate a big endian (MM) uint16 GeoTIFF with LERC compression."""

import tempfile
from pathlib import Path

import numpy as np

from rasterio_generated.write_utils import rewrite_big_endian, write_cog

HERE = Path(__file__).parent


def generate_source(output_path: Path) -> None:
    """Generate the little endian COG this fixture is rewritten from."""
    data = (np.arange(128 * 128).reshape(128, 128) * 3 + 300).astype(np.uint16)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="LERC",
        nodata_type=None,
    )


def generate(output_path: Path) -> None:
    """Generate a 128x128 tiled uint16 big endian GeoTIFF with LERC compression.

    libtiff swaps samples into the file's byte order before passing them to any
    codec, so the LERC data in this file holds byte-swapped values. Readers must
    swap the samples LERC decodes, just as they do for raw codecs like DEFLATE.
    """
    with tempfile.TemporaryDirectory() as tmp:
        src_path = Path(tmp) / "source.tif"
        generate_source(src_path)
        rewrite_big_endian(src_path, output_path)
