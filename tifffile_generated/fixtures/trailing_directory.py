"""Generate a BigTIFF whose first IFD is at the end of the file, after the image data."""

from pathlib import Path

import tifffile

from tifffile_generated.write_utils import checkerboard, relocate_directory_to_end


def generate(output_path: Path) -> None:
    with tifffile.TiffWriter(output_path, bigtiff=True) as writer:
        writer.write(checkerboard(seed=1), tile=(64, 64), compression="zlib")

    relocate_directory_to_end(output_path)
