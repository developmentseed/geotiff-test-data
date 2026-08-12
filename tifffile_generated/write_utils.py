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

    Tag 330 is typed IFD in a classic TIFF and IFD8 in a BigTIFF.
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
                subfiletype=1,
                tile=(blocksize, blocksize),
                compression=compression,
            )


def relocate_directory_to_end(path: Path) -> None:
    """Move a BigTIFF's first IFD to the end of the file and repoint the header at it.

    `tifffile` reserves the directory immediately after the header, as rasterio does, because both
    are told the image size up front. A writer that streams image data cannot, so its directory
    follows the data; this produces that layout from a file already written.

    Only the directory record moves. A tag value too large for its slot is stored elsewhere and
    referenced absolutely, as are the tile offsets, so nothing else needs rewriting.
    """
    raw = bytearray(path.read_bytes())
    endian = "<" if raw[:2] == b"II" else ">"
    start = struct.unpack(endian + "Q", raw[8:16])[0]
    entries = struct.unpack(endian + "Q", raw[start : start + 8])[0]
    length = 8 + entries * 20 + 8

    moved = len(raw)
    raw += bytes(raw[start : start + length])
    struct.pack_into(endian + "Q", raw, 8, moved)
    struct.pack_into(endian + "Q", raw, start, 0)
    path.write_bytes(bytes(raw))
