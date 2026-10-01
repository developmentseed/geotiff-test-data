"""Generate a tiled uint16 GeoTIFF with LZW compression and predictor 2."""

from pathlib import Path

import numpy as np

from rasterio_generated.write_utils import write_cog

HERE = Path(__file__).parent


def generate(output_path: Path) -> None:
    """Generate a 256x256 uint16 GeoTIFF with 128x128 tiles, LZW and predictor 2.

    Each row is a triangle wave that falls and rises by 1000 per pixel, so
    undoing the horizontal differencing must carry from the low byte into the
    high byte, and must wrap around for the falling steps.
    """
    x = np.abs(np.arange(256) % 128 - 64) * 1000
    y = np.arange(256)
    data = (x[np.newaxis, :] + y[:, np.newaxis]).astype(np.uint16)

    write_cog(
        output_path,
        data,
        blocksize=128,
        compress="LZW",
        predictor=2,
    )
