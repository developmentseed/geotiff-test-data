```
Driver: GTiff
File: tifffile_generated/fixtures/subifd_pyramid_classic.tif
COG: False
Compression: DEFLATE
ColorSpace: None

Profile
    Width:            256
    Height:           256
    Bands:            1
    Tiled:            True
    Dtype:            uint8
    NoData:           None
    Alpha Band:       False
    Internal Mask:    False
    Interleave:       BAND
    ColorMap:         False
    ColorInterp:      ('gray',)
    Scales:           (1.0,)
    Offsets:          (0.0,)

Geo
    Crs:              None
    Origin:           (0.0, 0.0)
    Resolution:       (1.0, 1.0)
    BoundingBox:      (0.0, 256.0, 256.0, 0.0)
    MinZoom:          17
    MaxZoom:          17

Image Metadata
    TIFFTAG_IMAGEDESCRIPTION: {"shape": [256, 256]}
    TIFFTAG_SOFTWARE: tifffile.py
    TIFFTAG_XRESOLUTION: 1
    TIFFTAG_YRESOLUTION: 1
    TIFFTAG_RESOLUTIONUNIT: 1 (unitless)

Image Structure
    COMPRESSION: DEFLATE
    INTERLEAVE: BAND

Band 1
    ColorInterp: gray

IFD
    Id      Size           BlockSize     Decimation
    0       256x256        64x64         0
    1       128x128        64x64         2
    2       64x64          64x64         4

COG Validation info
    - The offset of the first block of overview of index 0 should be after the one of the overview of index 1 (error)
    - The offset of the first block of the main resolution image should be after the one of the overview of index 1 (error)
```
