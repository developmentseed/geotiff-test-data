"""Generate an 1band + alpha dataset GeoTIFF with DEFLATE compression."""

from pathlib import Path

import numpy as np
from rasterio.enums import ColorInterp

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    """Generate a 256x256 1band + alpha GeoTIFF with DEFLATE compression."""
    # Create RGB gradient pattern
    data = np.zeros((3, 256, 256), dtype=np.uint8) + 1
    data[:, 0:128, 0:128] = 0

    mask = np.zeros((1, 256, 256), dtype=np.uint8) + 1
    mask[:, 0:128, 0:128] = 0

    write_cog(
        output_path,
        data,
        mask=mask,
        blocksize=64,
        nodata_type="mask",
        compress="DEFLATE",
        colorinterp=[
            ColorInterp.red,
            ColorInterp.green,
            ColorInterp.blue,
        ],
        rasterio_env={"GDAL_TIFF_INTERNAL_MASK": "YES"},
    )
