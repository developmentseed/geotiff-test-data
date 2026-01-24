"""Generate non-optimized HDF5 with 10 MB chunks."""

from pathlib import Path


import numpy as np

from netcdf4_generated.write_utils import write_netcdf4

DESCRIPTION = (
    "Non-optimized HDF5 with 10 MB chunks and metadata scattered throughout the file"
)


def generate(output_path: Path) -> None:
    """Generate fragmented (non-cloud-optimized) NetCDF4 file with 10 MB chunks."""
    # Dimensions: 100 x 512 x 1024 float32 = ~200 MB raw (same as cloud_optimized)
    nt, ny, nx = 100, 512, 1024

    # Coordinate data
    time_data = np.arange(nt, dtype=np.float64)
    x_data = np.linspace(0, nx - 1, nx, dtype=np.float64)
    y_data = np.linspace(0, ny - 1, ny, dtype=np.float64)

    # Main data variable - same seed = same data as cloud_optimized
    np.random.seed(42)
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
        "title": "Fragmented (non-cloud-optimized) test data with 10 MB chunks",
        "history": "Generated for VirtualiZarr testing",
    }

    # Chunks: (5, 512, 1024) = 5 * 512 * 1024 * 4 bytes = 10 MB
    write_netcdf4(
        output_path,
        variables,
        dimensions,
        global_attrs,
        cloud_optimized=False,
        chunk_sizes={"temperature": (5, 512, 1024)},
        compression="gzip",
        compression_opts=4,
    )
