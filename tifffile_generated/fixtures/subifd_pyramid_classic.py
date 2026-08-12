"""Generate a classic TIFF whose reduced resolutions are in SubIFDs, typing tag 330 IFD."""

from pathlib import Path

from tifffile_generated.write_utils import checkerboard, write_subifd_pyramid


def generate(output_path: Path) -> None:
    write_subifd_pyramid(output_path, checkerboard(), bigtiff=False)
