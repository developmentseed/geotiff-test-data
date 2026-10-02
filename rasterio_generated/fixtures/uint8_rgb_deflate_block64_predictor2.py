"""Generate a pixel-interleaved RGB GeoTIFF with DEFLATE compression and predictor 2."""

from pathlib import Path

import numpy as np
from rasterio.enums import ColorInterp

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    """Generate a 128x128 RGB GeoTIFF with DEFLATE compression and predictor 2.

    Each band changes differently along the rows, so undoing the horizontal
    differencing must add each sample to the same band of the previous pixel,
    not to the previous sample.
    """
    x = np.arange(128, dtype=np.uint8)
    y = np.arange(128, dtype=np.uint8)

    data = np.stack(
        [
            np.tile(x * 2, (128, 1)),
            np.tile(255 - x * 2, (128, 1)),
            np.tile((y * 2).reshape(-1, 1), (1, 128)),
        ]
    )

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        predictor=2,
        nodata_type=None,
        colorinterp=[ColorInterp.red, ColorInterp.green, ColorInterp.blue],
    )
