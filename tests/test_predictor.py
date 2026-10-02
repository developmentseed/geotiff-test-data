"""Check that a fixture carries a predictor exactly when its name says so.

write_cog once set the predictor on its in-memory dataset only, so the COGs it
wrote silently used no predictor. Fixing that gave a predictor to a fixture
whose name didn't mention one.
"""

import re
from pathlib import Path

import pytest
import tifffile

REPO_ROOT = Path(__file__).parent.parent
FIXTURES = sorted(REPO_ROOT.glob("*_generated/fixtures/*.tif"))


@pytest.mark.parametrize("path", FIXTURES, ids=lambda path: path.stem)
def test_predictor_matches_name(path: Path):
    match = re.search(r"predictor(\d)", path.stem)
    expected = int(match.group(1)) if match else 1

    with tifffile.TiffFile(path) as tif:
        # GDAL writes the mask IFDs of a COG without a predictor
        pages = [
            page for page in tif.pages if not page.subfiletype & tifffile.FILETYPE.MASK
        ]
        assert [int(page.predictor) for page in pages] == [expected] * len(pages)
