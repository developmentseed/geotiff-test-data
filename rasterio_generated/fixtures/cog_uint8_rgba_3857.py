"""Generate an 1band + alpha dataset GeoTIFF with DEFLATE compression."""

from pathlib import Path

import numpy as np
from rasterio.enums import ColorInterp
from rasterio.transform import from_origin

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    """Generate a 256x256 RGBA GeoTIFF in EPSG:3857 with a rainbow gradient.

    Red increases left→right, green increases top→bottom, blue is zero.
    This makes it easy to verify correct orientation: top-left is black,
    top-right is red, bottom-left is green, bottom-right is yellow.
    """
    xs = np.linspace(0, 255, 256, dtype=np.uint8)
    ys = np.linspace(0, 255, 256, dtype=np.uint8)
    red = np.tile(xs, (256, 1))        # increases left→right
    green = np.tile(ys[:, None], (1, 256))  # increases top→bottom
    blue = np.zeros((256, 256), dtype=np.uint8)
    alpha = np.full((256, 256), 255, dtype=np.uint8)
    data = np.stack([red, green, blue, alpha])

    transform = from_origin(663007.755215658, 5751231.407046753, 100, 100)

    write_cog(
        output_path,
        data,
        blocksize=64,
        crs="EPSG:3857",
        transform=transform,
        compress="DEFLATE",
        nodata_type=None,
        colorinterp=[
            ColorInterp.red,
            ColorInterp.green,
            ColorInterp.blue,
            ColorInterp.alpha,
        ],
    )
