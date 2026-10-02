"""Generate an EPSG:3832 (PDC Mercator) GeoTIFF that crosses the antimeridian in the Pacific."""

from pathlib import Path

import numpy as np
from rasterio.transform import from_origin

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    data = np.arange(1, 43, dtype=np.uint8).reshape(1, 42)
    data = np.repeat(data, 42, axis=0)
    # 42 x 42 pixels at 111,320 m (~1° of longitude), spanning 156.5°E to 161.5°W, ~24°N to ~17.3°S.
    # The origin is (156.5°E, 24°N) converted to EPSG:3832, so the seam falls mid-pixel (column 23.5).
    transform = from_origin(723_577, 2_736_035, 111_320, 111_320)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        crs="EPSG:3832",
        transform=transform,
    )