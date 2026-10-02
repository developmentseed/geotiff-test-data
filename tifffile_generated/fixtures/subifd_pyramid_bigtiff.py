"""Generate a BigTIFF whose reduced resolutions are in SubIFDs, typing tag 330 IFD8.

This file imitates published OME-TIFF files that are too large for test data and are not
redistributable here. It is the smallest file with the same directory shape. Two unrelated
writers put the pyramid in SubIFDs. The writer, the size, and the levels come from range
requests to the objects themselves:

- morphology.ome.tif from the Xenium human lung cancer dataset
  (https://www.10xgenomics.com/datasets/preview-data-ffpe-human-lung-cancer-with-xenium-multimodal-cell-segmentation-1-standard):
  written with tifffile.py, 4.76 GB, 7 levels for each plane, 11 planes.
  https://s3-us-west-2.amazonaws.com/10x.files/samples/xenium/2.0.0/Xenium_V1_humanLung_Cancer_FFPE/Xenium_V1_humanLung_Cancer_FFPE_morphology.ome.tif
- he_image.ome.tif from the same dataset: written with OME Bio-Formats 6.12.0, 1.19 GB, 5 levels.
  https://s3-us-west-2.amazonaws.com/10x.files/samples/xenium/2.0.0/Xenium_V1_humanLung_Cancer_FFPE/Xenium_V1_humanLung_Cancer_FFPE_he_image.ome.tif

The 17.73 GB Bio-Formats file in trailing_directory.py also has a SubIFD pyramid, with 9 levels.
"""

from pathlib import Path

from tifffile_generated.write_utils import checkerboard, write_subifd_pyramid


def generate(output_path: Path) -> None:
    write_subifd_pyramid(output_path, checkerboard(), bigtiff=True)
