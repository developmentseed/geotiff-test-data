"""Generate a rotated EPSG:4326 GeoTIFF that crosses the antimeridian along a slanted seam."""

from pathlib import Path

import numpy as np
from rasterio.transform import Affine

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    data = np.arange(1, 43, dtype=np.uint8).reshape(1, 42)
    data = np.repeat(data, 42, axis=0)
    # Same footprint origin as antimeridian.py (-204, 24), rotated 20° so the
    # -180° meridian cuts the pixel grid diagonally.
    transform = Affine.translation(-204, 24) * Affine.rotation(20) * Affine.scale(1, -1)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        crs="EPSG:4326",
        transform=transform,
    )
