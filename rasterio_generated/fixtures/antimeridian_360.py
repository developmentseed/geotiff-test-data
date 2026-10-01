"""Generate an EPSG:4326 GeoTIFF spanning the full 360° of longitude, from 10°S to 10°N."""

from pathlib import Path

import numpy as np
from rasterio.transform import from_origin

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    data = np.arange(1, 73, dtype=np.uint8).reshape(1, 72)
    data = np.repeat(data, 4, axis=0)
    # 72 x 4 pixels at 5°, spanning -180°..180° longitude, -10°..10° latitude
    transform = from_origin(-180, 10, 5, 5)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        crs="EPSG:4326",
        transform=transform,
    )
