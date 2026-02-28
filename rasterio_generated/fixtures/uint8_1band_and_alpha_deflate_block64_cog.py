"""Generate an 1band + alpha dataset GeoTIFF with DEFLATE compression."""

from pathlib import Path

import numpy as np
from rasterio.enums import ColorInterp

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    """Generate a 256x256 1band + alpha GeoTIFF with DEFLATE compression."""
    # Create RGB gradient pattern
    r = np.linspace(0, 127, 256, dtype=np.uint8)
    a = np.full(256, 255, dtype=np.uint8)

    data = np.stack(
        [
            np.tile(r, (256, 1)),
            np.tile(a.reshape(-1, 1), (1, 256)),
        ]
    )

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        colorinterp=[
            ColorInterp.red,
            ColorInterp.alpha,
        ],
    )
