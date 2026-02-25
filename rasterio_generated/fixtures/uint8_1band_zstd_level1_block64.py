"""Generate a 1-band, tiled, ZSTD-compressed GeoTIFF with compression level 1."""

from pathlib import Path

import numpy as np

from rasterio_generated.write_utils import write_cog

HERE = Path(__file__).parent


def generate(output_path: Path) -> None:
    """Generate a 128x128 tiled uint8 GeoTIFF with ZSTD compression at level 1."""
    # Create a gradient pattern
    data = np.tile(
        np.linspace(0, 255, 128, dtype=np.uint8),
        (128, 1),
    )

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="ZSTD",
        level=1,
    )
