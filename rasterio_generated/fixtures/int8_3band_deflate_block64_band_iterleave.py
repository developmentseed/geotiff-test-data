"""Generate a 3-band, tiled GeoTIFF.

Useful for testing band-interleave without zstd support.
"""

from pathlib import Path

import numpy as np

from rasterio_generated.write_utils import write_cog

HERE = Path(__file__).parent


def generate(output_path: Path) -> None:
    """Generate a 3x128x128 tiled int8 GeoTIFF compression."""
    # Create RGB gradient pattern
    r = np.linspace(-64, 64, 128, dtype=np.int8)
    g = np.full(shape=128, fill_value=64, dtype=np.int8)
    b = np.linspace(64, -64, 128, dtype=np.int8)

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
        interleave="band",
        nodata_type="mask",
    )
