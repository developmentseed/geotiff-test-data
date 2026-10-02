"""Generate a BigTIFF whose first IFD is at the end of the file, after the image data.

rasterio and tifffile do not write this layout. Both know the image size before they write, so
both reserve the directory at the front, at byte 8 or byte 16. This script moves the directory
to the end after tifffile writes the file. A writer that streams image data makes the same
layout.

This file imitates a published OME-TIFF file that is too large for test data and is not
redistributable here. It is the smallest file with the same directory shape. The imitated file
is he_image.ome.tif from the Atera WTA human cervical cancer dataset
(https://www.10xgenomics.com/datasets/atera-wta-ffpe-human-cervical-cancer): written with
OME Bio-Formats, 17.73 GB, first IFD at byte 17,731,963,126. These values come from range
requests to the object itself:

https://s3-us-west-2.amazonaws.com/10x.files/samples/atera/dev/WTA_Preview_FFPE_Cervical_Cancer/WTA_Preview_FFPE_Cervical_Cancer_he_image.ome.tif

The position of the first IFD is not consistent, even for one writer. Bio-Formats put the first
IFD at byte 16 in a 1.19 GB file (see subifd_pyramid_bigtiff.py). In this 17.73 GB file, it put
the first IFD at the end. Thus it is better for a reader to handle the layout than to detect it.
"""

from pathlib import Path

import tifffile

from tifffile_generated.write_utils import checkerboard, relocate_first_ifd_to_end


def generate(output_path: Path) -> None:
    with tifffile.TiffWriter(output_path, bigtiff=True) as writer:
        writer.write(checkerboard(seed=1), tile=(64, 64), compression="zlib")

    relocate_first_ifd_to_end(output_path)
