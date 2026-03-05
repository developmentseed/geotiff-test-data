"""Generate a tiled, LZW-compressed GeoTIFF."""

from pathlib import Path

import numpy as np

from rasterio_generated.write_utils import write_cog

HERE = Path(__file__).parent


def generate(output_path: Path) -> None:
    """Generate a 512x512 tiled uint16 GeoTIFF with DEFLATE compression and scale and offset."""
    data = np.arange(128 * 128, dtype=np.uint16).reshape(128, 128)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        predictor=2,
        scale=0.01,
        offset=100,
    )
