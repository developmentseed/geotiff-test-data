"""Generate a float32 GeoTIFF with DEFLATE compression and predictor 3."""

from pathlib import Path

import numpy as np

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    """Generate a 128x128 tiled float32 GeoTIFF with DEFLATE and predictor 3.

    Predictor 3 splits each row into byte planes, most significant byte first,
    and then differences the bytes.
    """
    data = np.linspace(0.0, 1.0, 128 * 128, dtype=np.float32).reshape(128, 128)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        predictor=3,
        nodata_type=None,
    )
