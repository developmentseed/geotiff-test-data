"""Generate a GeoTIFF with non-epsg CRS."""

from pathlib import Path

import numpy as np
from rasterio.transform import from_origin

from rasterio_generated.write_utils import write_cog


def generate(output_path: Path) -> None:
    data = np.arange(42, dtype=np.uint8).reshape(1, 42)
    data = np.repeat(data, 42, axis=0)
    transform = from_origin(300000.00, 4200000.0, 1, 1)

    write_cog(
        output_path,
        data,
        blocksize=64,
        compress="DEFLATE",
        crs='PROJCS["unnamed",GEOGCS["Unknown datum based upon the WGS 84 ellipsoid",DATUM["Not_specified_based_on_WGS_84_spheroid",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",129],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]',
        transform=transform,
    )
