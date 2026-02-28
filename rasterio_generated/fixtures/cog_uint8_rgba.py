"""Generate an 1band + alpha dataset GeoTIFF with DEFLATE compression."""

from pathlib import Path

import numpy as np
from rasterio.enums import ColorInterp

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    """Generate a 256x256 1band + alpha GeoTIFF with DEFLATE compression."""
    data = np.zeros((4, 256, 256), dtype=np.uint8) + 1
    data[3, :, :] = 255
    data[:, 0:128, 0:128] = 0

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        nodata_type=None,
        colorinterp=[
            ColorInterp.red,
            ColorInterp.green,
            ColorInterp.blue,
            ColorInterp.alpha,
        ],
    )
