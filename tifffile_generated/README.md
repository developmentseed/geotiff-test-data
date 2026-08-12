# Test data generated from tifffile

Run `pixi run generate-tifffile` to create the test data files.

Each file is generated from a corresponding Python script with the same name, as in
[`rasterio_generated`](../rasterio_generated). These use `tifffile` because of what they contain:

- SubIFD pyramids. `rasterio.build_overviews` writes reduced resolutions as further IFDs in the
  top-level chain - three pages, `NewSubfileType=1` on the reduced two, no tag 330 anywhere. A
  pyramid in SubIFDs types tag 330 `IFD` in a classic TIFF and `IFD8` in a BigTIFF.
- A directory after the image data. Neither rasterio nor tifffile writes this: both are told the
  image size up front and reserve the directory at the front, at bytes 8 and 16. `trailing_directory`
  relocates it afterwards, which is what a writer that streams image data produces.

## The files these imitate

Both layouts come from microscopy. These three published OME-TIFFs are what the fixtures were
derived from - too large to be test data at 1.19 to 17.7 GB, and none of them redistributable here,
so what is committed is the smallest thing that has the same directory shape.

| published file | writer | size | first IFD | SubIFDs |
|---|---|---|---|---|
| [Xenium human lung cancer](https://www.10xgenomics.com/datasets/preview-data-ffpe-human-lung-cancer-with-xenium-multimodal-cell-segmentation-1-standard), `morphology.ome.tif` | `tifffile.py` | 4.76 GB | byte 16 | 7 levels per plane, 11 planes |
| the same dataset, `he_image.ome.tif` | `OME Bio-Formats 6.12.0` | 1.19 GB | byte 16 | 5 levels |
| [Atera WTA human cervical cancer](https://www.10xgenomics.com/datasets/atera-wta-ffpe-human-cervical-cancer), `he_image.ome.tif` | `OME Bio-Formats` | 17.73 GB | byte 17,731,963,126 | 9 levels |

All three carry a SubIFD pyramid, from two unrelated writers. The trailing directory is
Bio-Formats and not consistently so - the same writer put it at byte 16 for the 1.19 GB file and at
the end for the 17.73 GB one - which is why a reader is better off handling the layout than
detecting it.

The `Software` tag, the sizes and the IFD offsets above were read from the objects themselves, each
with a couple of range requests:

```
https://s3-us-west-2.amazonaws.com/10x.files/samples/xenium/2.0.0/Xenium_V1_humanLung_Cancer_FFPE/Xenium_V1_humanLung_Cancer_FFPE_morphology.ome.tif
https://s3-us-west-2.amazonaws.com/10x.files/samples/xenium/2.0.0/Xenium_V1_humanLung_Cancer_FFPE/Xenium_V1_humanLung_Cancer_FFPE_he_image.ome.tif
https://s3-us-west-2.amazonaws.com/10x.files/samples/atera/dev/WTA_Preview_FFPE_Cervical_Cancer/WTA_Preview_FFPE_Cervical_Cancer_he_image.ome.tif
```

`pixi run info` covers these like any other file here, and they report `COG: False`.
