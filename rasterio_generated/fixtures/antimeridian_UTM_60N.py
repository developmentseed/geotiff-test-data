"""Generate a GeoTIFF in UTM zone 60N that crosses the antimeridian near the Aleutian Islands."""

from pathlib import Path

import numpy as np
from rasterio.transform import from_origin

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    data = np.arange(1, 43, dtype=np.uint8).reshape(1, 42)
    data = np.repeat(data, 42, axis=0)
    # 42 x 42 pixels at 20 km = 840 km square, spanning ~174°E to ~173°W, ~48°N to ~56°N
    transform = from_origin(300_000, 6_200_000, 20_000, 20_000)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        crs="EPSG:32660",
        transform=transform,
    )
