"""
Generate a 3-band, tiled, ZSTD compressed GeoTIFF with uint16 dtype, predictor 2, and
band interleave.
"""

from pathlib import Path

import numpy as np
from rasterio.enums import ColorInterp

from rasterio_generated.write_utils import write_cog

HERE = Path(__file__).parent


def generate(output_path: Path) -> None:
    """
    Generate a 3x16x16 tiled uint16 GeoTIFF with ZSTD compression, predictor=2 and
    band interleave format.
    """
    # Create RGB gradient pattern
    r = np.linspace(0, 256, 128, dtype=np.uint16)
    g = np.full(shape=128, fill_value=128, dtype=np.uint16)
    b = np.linspace(256, 0, 128, dtype=np.uint16)

    data = np.stack(
        [
            np.tile(r, (128, 1)),
            np.tile(g.reshape(-1, 1), (1, 128)),
            np.tile(b, (128, 1)),
        ]
    )

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="ZSTD",
        interleave="band",  # planar configuration
        colorinterp=[
            ColorInterp.red,
            ColorInterp.green,
            ColorInterp.blue,
        ],
        predictor=2,
    )
