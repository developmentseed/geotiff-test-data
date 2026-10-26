"""Check the shape of the CRS corpus case list."""

import re
from collections import Counter

from crs.cases import CASES, EPSG_CODES


def test_case_names_unique_and_well_formed():
    names = [c.name for c in CASES]
    assert len(names) == len(set(names))
    assert all(re.fullmatch(r"[a-z0-9_]+", n) for n in names)


def test_case_kinds():
    kinds = Counter(c.kind for c in CASES)
    assert set(kinds) == {"proj", "epsg", "wkt", "geokeys"}
    # The 46 EPSG codes plus ESRI:54009, which is also an authority code.
    assert len(EPSG_CODES) == 46
    assert kinds["epsg"] == 47
    assert kinds["geokeys"] == 1


def test_expected_cases_present():
    names = {c.name for c in CASES}
    for name in (
        "tmerc",
        "omerc_variant_a",
        "omerc_variant_b",
        "labrd",
        "somerc",
        "merc_1sp",
        "merc_2sp",
        "stere_polar_scaled_wkt",
        "stere_polar_k1_wkt",
        "tmso",
        "cea",
        "lcc_2sp_usft",
        "tmerc_ft",
        "lcc_1sp_grad_wkt",
        "geog_grad_wkt",
        "lcc_1sp_paris_grad",
        "aea_nad27",
        "tmerc_datum_wgs84",
        "sinu_sphere",
        "geog_sphere",
        "tmerc_towgs84",
        "lcc_1sp_paris_deg_wkt",
        "lcc_1sp_pm_user",
        "lcc_1sp_pm_epsg_tifffile",
        "longlat_grs80",
        "utm_bessel",
        "moll",
        "krovak",
        "esri_54009",
        "eqearth",
        "epsg_2953",
    ):
        assert name in names
    assert len(CASES) >= 95


def test_geokeys_case_has_epsg_prime_meridian():
    case = next(c for c in CASES if c.kind == "geokeys")
    assert isinstance(case.value, dict)
    assert case.value["GeogPrimeMeridian"] == 8903
    assert "GeogPrimeMeridianLong" not in case.value
