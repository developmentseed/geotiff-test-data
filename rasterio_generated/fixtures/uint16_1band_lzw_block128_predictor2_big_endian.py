"""Generate a big endian (MM) copy of uint16_1band_lzw_block128_predictor2."""

import tempfile
from pathlib import Path

from rasterio_generated.fixtures.uint16_1band_lzw_block128_predictor2 import (
    generate as generate_source,
)
from rasterio_generated.write_utils import rewrite_big_endian

HERE = Path(__file__).parent


def generate(output_path: Path) -> None:
    """Generate a 128x128 tiled uint16 big endian GeoTIFF with LZW and predictor 2.

    Readers must swap samples to native order before undoing horizontal
    differencing, which adds neighbouring samples as integers.
    """
    with tempfile.TemporaryDirectory() as tmp:
        src_path = Path(tmp) / "source.tif"
        generate_source(src_path)
        rewrite_big_endian(src_path, output_path)
