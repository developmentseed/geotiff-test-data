"""Generate a big endian (MM) float32 GeoTIFF with the floating point predictor."""

import tempfile
from pathlib import Path

import numpy as np

from rasterio_generated.write_utils import rewrite_big_endian, write_cog

HERE = Path(__file__).parent


def generate_source(output_path: Path) -> None:
    """Generate the little endian COG this fixture is rewritten from."""
    data = np.linspace(0.0, 1.0, 128 * 128, dtype=np.float32).reshape(128, 128)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        predictor=3,
        nodata_type=None,
    )


def generate(output_path: Path) -> None:
    """Generate a 128x128 tiled float32 big endian GeoTIFF with DEFLATE and predictor 3.

    Predictor 3 splits each row into byte planes, most significant byte first,
    whatever the file's byte order, so readers must not swap these samples.
    """
    with tempfile.TemporaryDirectory() as tmp:
        src_path = Path(tmp) / "source.tif"
        generate_source(src_path)
        rewrite_big_endian(src_path, output_path)
