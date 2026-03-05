"""Generate a GeoTIFF that has AREA_OR_POINT metadata set to Point."""

from pathlib import Path

import numpy as np
from rasterio.transform import from_origin

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    data = np.arange(42, dtype=np.uint8).reshape(1, 42)
    data = np.repeat(data, 42, axis=0)
    transform = from_origin(-180, 24, 1, 1)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        crs="EPSG:4326",
        transform=transform,
        tags={"AREA_OR_POINT": "Point"},
    )
