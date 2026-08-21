from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import tifffile


def checkerboard(size: int = 256, seed: int = 0) -> np.ndarray:
    """A pattern that compresses but is not uniform, so a wrong tile is visible."""
    rng = np.random.default_rng(seed)
    base = np.indices((size, size)).sum(axis=0) % 2 * 200
    return (base + rng.integers(0, 40, size=(size, size))).astype(np.uint8)


def write_subifd_pyramid(
    path: Path,
    data: np.ndarray,
    *,
    bigtiff: bool,
    levels: int = 2,
    blocksize: int = 64,
    compression: str = "zlib",
) -> None:
    """Write `data` with `levels` reduced resolutions in SubIFDs rather than in the IFD chain.

    `rasterio.build_overviews` writes the reduced resolutions as more IFDs in the top-level
    chain. It sets `NewSubfileType=1` on each reduced level and does not write tag 330. In a
    SubIFD pyramid, tag 330 has the type IFD in a classic TIFF and the type IFD8 in a BigTIFF.
    """
    reduced = [data[:: 2**power, :: 2**power] for power in range(1, levels + 1)]
    with tifffile.TiffWriter(path, bigtiff=bigtiff) as writer:
        writer.write(
            data,
            subifds=len(reduced),
            tile=(blocksize, blocksize),
            compression=compression,
        )
        for level in reduced:
            writer.write(
                level,
                subfiletype=1,  # NewSubfileType bit 0 marks a reduced resolution of another image
                tile=(blocksize, blocksize),
                compression=compression,
            )


def relocate_first_ifd_to_end(path: Path) -> None:
    """Move the first IFD of a TIFF to the end of the file and point the header to it.

    `tifffile` reserves the directory immediately after the header, as rasterio does, because both
    are told the image size up front. A writer that streams image data cannot reserve it, so the
    directory comes after the data. This function makes that layout from a file that is already
    complete. It operates on a classic TIFF or a BigTIFF.

    Only the directory record of the first IFD moves. A tag value too large for its slot is stored
    elsewhere and referenced absolutely, as are the tile offsets, so nothing else needs rewriting.
    """
    with tifffile.TiffFile(path) as tif:
        fmt, start = tif.tiff, tif.pages[0].offset

    raw = bytearray(path.read_bytes())
    entries = struct.unpack(fmt.tagnoformat, raw[start : start + fmt.tagnosize])[0]
    length = fmt.tagnosize + entries * fmt.tagsize + fmt.offsetsize

    if len(raw) % 2:
        raw += b"\x00"  # An IFD must start on a word boundary
    moved = len(raw)
    raw += raw[start : start + length]
    struct.pack_into(fmt.offsetformat, raw, fmt.offsetsize, moved)
    struct.pack_into(fmt.tagnoformat, raw, start, 0)
    path.write_bytes(bytes(raw))
