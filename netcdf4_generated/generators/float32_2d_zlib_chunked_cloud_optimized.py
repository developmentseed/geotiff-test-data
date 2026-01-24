"""Generate cloud-optimized HDF5 with contiguous metadata."""

from pathlib import Path

import numpy as np

from netcdf4_generated.write_utils import write_netcdf4

DESCRIPTION = "Cloud-optimized HDF5 with metadata consolidated in a single block for efficient remote access"


def generate(output_path: Path) -> None:
    """Generate cloud-optimized NetCDF4 file with metadata in a single block."""
    # Dimensions: 100 x 512 x 1024 float32 = ~200 MB raw
    nt, ny, nx = 100, 512, 1024

    # Coordinate data
    time_data = np.arange(nt, dtype=np.float64)
    x_data = np.linspace(0, nx - 1, nx, dtype=np.float64)
    y_data = np.linspace(0, ny - 1, ny, dtype=np.float64)

    # Main data variable - 3D temperature-like data
    np.random.seed(42)  # Reproducible
    data = np.random.randn(nt, ny, nx).astype(np.float32) * 10 + 273.15

    variables = {
        "time": (
            time_data,
            {"units": "days since 2000-01-01", "calendar": "standard"},
        ),
        "x": (x_data, {"units": "km", "long_name": "x coordinate"}),
        "y": (y_data, {"units": "km", "long_name": "y coordinate"}),
        "temperature": (
            data,
            {
                "units": "K",
                "long_name": "Temperature",
                "coordinates": "time y x",
            },
        ),
    }

    dimensions = {"time": nt, "y": ny, "x": nx}

    global_attrs = {
        "Conventions": "CF-1.8",
        "title": "Cloud-optimized test data",
        "history": "Generated for VirtualiZarr testing",
    }

    write_netcdf4(
        output_path,
        variables,
        dimensions,
        global_attrs,
        cloud_optimized=True,
        chunk_sizes={"temperature": (1, 128, 256)},
        compression="gzip",
        compression_opts=4,
    )
