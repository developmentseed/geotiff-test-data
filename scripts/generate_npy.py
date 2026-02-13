"""Generate .npy tile files alongside each TIFF in the repository.

This is intended to be used for downstream libraries to have "known" valid data to test
against, without needing to read TIFF files directly. I.e. in Python we can easily test
against rasterio at runtime, but in something like JavaScript, there's no canonical
known-good TIFF reader. So having .npy files (which are pretty easy to parse in any
language) allows us to test against a known reference implementation.

For each TIFF file, this script reads every internal tile (block) at each IFD
level (full resolution + overviews) and saves them as NumPy .npy files.

Output structure:
    <tif_stem>/<z>-<x>-<y>.npy

where z=0 is full resolution, z=1 is the first overview, etc.
x is the column index and y is the row index of the tile.

The .npy array has shape (bands, height, width).
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import rasterio
import rasterio.windows


def generate_npy_tiles(tif_path: Path) -> None:
    """Generate .npy files for every internal tile of a TIFF."""
    output_dir = tif_path.parent / tif_path.stem
    output_dir.mkdir(exist_ok=True)

    with rasterio.open(tif_path) as src:
        _write_tiles_for_ifd(src, output_dir, z=0)

        for ix, _ in enumerate(src.overviews(1)):
            with rasterio.open(tif_path, OVERVIEW_LEVEL=ix) as ovr:
                _write_tiles_for_ifd(ovr, output_dir, z=ix + 1)


def _write_tiles_for_ifd(
    dataset: rasterio.DatasetReader,
    output_dir: Path,
    z: int,
) -> None:
    """Write .npy tiles for a single IFD (full res or overview)."""
    block_shapes = dataset.block_shapes
    # All bands should have the same block shape in a COG
    block_height, block_width = block_shapes[0]

    n_tiles_x = math.ceil(dataset.width / block_width)
    n_tiles_y = math.ceil(dataset.height / block_height)

    for tile_y in range(n_tiles_y):
        for tile_x in range(n_tiles_x):
            window = rasterio.windows.Window(
                col_off=tile_x * block_width,
                row_off=tile_y * block_height,
                width=block_width,
                height=block_height,
            )

            data = dataset.read(window=window, boundless=True)

            npy_path = output_dir / f"{z}-{tile_x}-{tile_y}.npy"
            np.save(npy_path, data)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    tif_paths = sorted(repo_root.rglob("*.tif"))

    if not tif_paths:
        print("No .tif files found!")
        return

    print(f"Found {len(tif_paths)} TIFF file(s)\n")

    for tif_path in tif_paths:
        rel = tif_path.relative_to(repo_root)
        print(f"Processing {rel}...")
        generate_npy_tiles(tif_path)
        output_dir = tif_path.parent / tif_path.stem
        npy_count = len(list(output_dir.glob("*.npy")))
        print(f"  → {npy_count} tile(s) in {output_dir.relative_to(repo_root)}/")

    print("\nDone!")


if __name__ == "__main__":
    main()
