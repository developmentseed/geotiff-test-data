from __future__ import annotations

import tempfile
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
    photometric: Literal["RGB", "MINISBLACK"] | None = None,
):
    """
    data:
      - shape (H, W)           -> 1 band
      - shape (B, H, W)        -> multi-band (e.g. RGB)

    Note: The GDAL COG driver does not support the PHOTOMETRIC creation option.
    When driver="COG" and photometric is set, a two-step process is used:
    first write a GTiff with photometric, then convert to COG via gdal.Translate.
    """
    if data.ndim == 2:
        count = 1
        height, width = data.shape
    elif data.ndim == 3:
        count, height, width = data.shape
    else:
        raise ValueError("data must be 2D or 3D (bands, height, width)")

    # The COG driver ignores PHOTOMETRIC. Work around this by writing a
    # temporary GTiff first, then converting to COG with gdal.Translate.
    if driver == "COG" and photometric is not None:
        _write_cog_with_photometric(
            path,
            data,
            count=count,
            blocksize=blocksize,
            compress=compress,
            crs=crs,
            transform=transform,
            predictor=predictor,
            nodata=nodata,
            photometric=photometric,
        )
        return

    profile = {
        "driver": driver,
        "width": width,
        "height": height,
        "count": count,
        "dtype": data.dtype,
        "crs": crs,
        "transform": transform,
        "tiled": blocksize is not None,
        "interleave": "pixel",
    }

    if blocksize is not None:
        profile["blocksize"] = blocksize

    if compress is not None:
        profile["compress"] = compress

    if predictor is not None:
        profile["predictor"] = predictor

    if nodata is not None:
        profile["nodata"] = nodata

    if photometric is not None:
        profile["photometric"] = photometric

    with rasterio.open(path, "w", **profile) as dst:
        if count == 1:
            dst.write(data, 1)
        else:
            dst.write(data)


def _write_cog_with_photometric(
    path: Path,
    data: np.ndarray,
    *,
    count: int,
    blocksize: int | None,
    compress: str | None,
    crs: str,
    transform: Affine,
    predictor: int | None,
    nodata: int | float | None,
    photometric: str,
):
    """Write a COG via a temporary GTiff to preserve photometric interpretation."""
    from osgeo import gdal

    height = data.shape[-2]
    width = data.shape[-1]

    with tempfile.NamedTemporaryFile(suffix=".tif", delete=True) as tmp:
        # Step 1: Write GTiff with photometric
        gtiff_profile = {
            "driver": "GTiff",
            "width": width,
            "height": height,
            "count": count,
            "dtype": data.dtype,
            "crs": crs,
            "transform": transform,
            "tiled": True,
            "blockxsize": blocksize or 256,
            "blockysize": blocksize or 256,
            "interleave": "pixel",
            "photometric": photometric,
        }

        if compress is not None:
            gtiff_profile["compress"] = compress

        if predictor is not None:
            gtiff_profile["predictor"] = predictor

        if nodata is not None:
            gtiff_profile["nodata"] = nodata

        with rasterio.open(tmp.name, "w", **gtiff_profile) as dst:
            if count == 1:
                dst.write(data, 1)
            else:
                dst.write(data)

        # Step 2: Convert to COG via gdal.Translate
        gdal.UseExceptions()
        creation_options = []
        if compress is not None:
            creation_options.append(f"COMPRESS={compress}")
        if blocksize is not None:
            creation_options.append(f"BLOCKSIZE={blocksize}")
        if predictor is not None:
            creation_options.append(f"PREDICTOR={predictor}")

        ds = gdal.Open(tmp.name)
        gdal.Translate(str(path), ds, format="COG", creationOptions=creation_options)
        ds = None
