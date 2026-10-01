"""Check that fixtures generated with a predictor carry it on every IFD.

write_cog once set the predictor on its in-memory dataset only, so the COGs it
wrote silently used no predictor.
"""

from pathlib import Path

import pytest
import tifffile

FIXTURES_DIR = Path(__file__).parent.parent / "rasterio_generated" / "fixtures"


@pytest.mark.parametrize(
    "name",
    [
        "uint16_1band_lzw_block128_predictor2",
        "uint16_1band_scale_offset",
        "uint8_1band_deflate_block128_unaligned_predictor2",
        "uint8_1band_lzw_block64_predictor2",
    ],
)
def test_predictor_2(name: str):
    with tifffile.TiffFile(FIXTURES_DIR / f"{name}.tif") as tif:
        assert [int(page.predictor) for page in tif.pages] == [2] * len(tif.pages)
