from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy as np
import rasterio
from rasterio.transform import from_origin

if TYPE_CHECKING:
    from affine import Affine


def write_tiff(
    path: Path,
    data: np.ndarray,
    *,
    driver: Literal["GTiff", "COG"] = "GTiff",
    blocksize: int | None = 256,
    compress: Literal[
        "LZW",
        "JPEG",
        "DEFLATE",
        "ZSTD",
        "WEBP",
        "LERC",
        "LERC_DEFLATE",
        "LERC_ZSTD",
        "LZMA",
    ]
    | None = None,
    crs: str = "EPSG:4326",
    transform: Affine = from_origin(0, 0, 0.01, 0.01),
    predictor: Literal[2, 3] | None = None,
    nodata: int | float | None = None,
):
    """
    data:
      - shape (H, W)           -> 1 band
      - shape (B, H, W)        -> multi-band (e.g. RGB)
    """
    if data.ndim == 2:
        count = 1
        height, width = data.shape
    elif data.ndim == 3:
        count, height, width = data.shape
    else:
        raise ValueError("data must be 2D or 3D (bands, height, width)")

    profile = {
        "driver": driver,
        "width": width,
        "height": height,
        "count": count,
        "dtype": data.dtype,
        "crs": crs,
        "transform": transform,
        "tiled": blocksize is not None,
        "interleave": "pixel",  # explicit chunky
    }

    if blocksize is not None:
        profile["blocksize"] = blocksize

    if compress is not None:
        profile["compress"] = compress

    if predictor is not None:
        profile["predictor"] = predictor

    if nodata is not None:
        profile["nodata"] = nodata

    with rasterio.open(path, "w", **profile) as dst:
        if count == 1:
            dst.write(data, 1)
        else:
            dst.write(data)
