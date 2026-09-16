"""Same as uint8_1band_sparse_nodata.py, but with no GDAL_NODATA tag."""

from pathlib import Path

import numpy as np
from rasterio import open as rio_open
from rasterio.transform import from_origin
from rasterio.windows import Window


def generate(output_path: Path) -> None:
    transform = from_origin(-10, 10, 0.01953125, 0.01953125)
    with rio_open(
        output_path,
        "w",
        driver="GTiff",
        height=512,
        width=512,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=transform,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        sparse_ok=True,
    ) as ds:
        # Only write tile (0, 0); the other three stay sparse.
        data = (np.arange(256 * 256).reshape(256, 256) % 256).astype(np.uint8)
        ds.write(data, 1, window=Window(0, 0, 256, 256))
