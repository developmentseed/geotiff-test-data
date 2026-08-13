"""Generate a classic TIFF whose reduced resolutions are in SubIFDs, typing tag 330 IFD.

Tag 330 has the type IFD in a classic TIFF and the type IFD8 in a BigTIFF. A reader must
convert the two types. This file is the classic variant. subifd_pyramid_bigtiff.py describes
the published files that the two files imitate.
"""

from pathlib import Path

from tifffile_generated.write_utils import checkerboard, write_subifd_pyramid


def generate(output_path: Path) -> None:
    write_subifd_pyramid(output_path, checkerboard(), bigtiff=False)
