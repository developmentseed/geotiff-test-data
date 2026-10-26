"""The CRS conformance corpus case list.

Each case is one GeoTIFF fixture. GDAL writes it from the input; the manifest
records the GeoKeys GDAL wrote and the CRS GDAL/PROJ reads back. See
``crs/README.md`` for the case kinds and the design spec in async-geotiff
(``dev-docs/specs/2026-10-26-geokey-crs-conformance-design.md``) for why each
case exists.

Keep PROJ-string cases away from parameters that exactly match an EPSG CRS:
GDAL then writes the EPSG code instead of user-defined keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

CaseKind = Literal["proj", "epsg", "wkt", "geokeys"]
GeoKeys = dict[str, int | float | str | list[float]]


@dataclass(frozen=True)
class Case:
    """One corpus fixture.

    ``value`` is a PROJ string, ``EPSG:<code>``, a WKT1 string, or for the
    ``geokeys`` kind a raw GeoKey dict written with tifffile.
    """

    name: str
    kind: CaseKind
    value: str | GeoKeys
    note: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)


# WKT fragments for cases a PROJ string cannot express.
_GEOG_WGS84_DEG = (
    'GEOGCS["unknown",DATUM["unknown",SPHEROID["WGS 84",6378137,298.257223563]],'
    'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
)
_GEOG_CLRK80IGN_GRAD = (
    'GEOGCS["unknown",DATUM["unknown",SPHEROID["Clarke 1880 (IGN)",6378249.2,293.466021293627]],'
    'PRIMEM["Greenwich",0],UNIT["grad",0.01570796326794897]]'
)
_GEOG_CLRK80IGN_PARIS_DEG = (
    'GEOGCS["unknown",DATUM["unknown",SPHEROID["Clarke 1880 (IGN)",6378249.2,293.466021293627]],'
    'PRIMEM["Paris",2.33722917],UNIT["degree",0.0174532925199433]]'
)


def _lcc_1sp(geogcs: str, lat: float) -> str:
    return (
        f'PROJCS["unknown",{geogcs},PROJECTION["Lambert_Conformal_Conic_1SP"],'
        f'PARAMETER["latitude_of_origin",{lat}],PARAMETER["central_meridian",0],'
        'PARAMETER["scale_factor",0.99987742],PARAMETER["false_easting",600000],'
        'PARAMETER["false_northing",2200000],UNIT["metre",1]]'
    )


def _polar_stereographic(lat: float, k: float) -> str:
    return (
        f'PROJCS["unknown",{_GEOG_WGS84_DEG},PROJECTION["Polar_Stereographic"],'
        f'PARAMETER["latitude_of_origin",{lat}],PARAMETER["central_meridian",-45],'
        f'PARAMETER["scale_factor",{k}],PARAMETER["false_easting",0],'
        'PARAMETER["false_northing",0],UNIT["metre",1]]'
    )


_TMERC = "+proj=tmerc +lat_0=0 +lon_0=-3.5 +k=0.9996 +x_0=500000 +y_0=0"
_LCC_1SP = "+proj=lcc +lat_1=46.8 +lat_0=46.8 +k_0=0.99987742 +x_0=600000 +y_0=2200000 +ellps=clrk80ign"
_OMERC = (
    "+proj=omerc +lat_0=4 +lonc=102.25 +alpha=323.0257964666666 +gamma=323.1301023611111 "
    "+k=0.99984 +x_0=804671 +y_0=0"
)

# The GeoKeys GDAL writes for `lcc_1sp` (lon_0 = 0), with the prime meridian
# given as the EPSG code for Paris instead of a longitude. GDAL never writes
# GeogPrimeMeridian codes itself, so this fixture is written with tifffile.
_LCC_1SP_PM_EPSG_GEOKEYS: GeoKeys = {
    "GTModelType": 1,
    "GTRasterType": 1,
    "GTCitation": "unknown",
    "GeographicType": 32767,
    "GeogCitation": (
        "GCS Name = unknown|Datum = Unknown based on Clarke 1880 (IGN) ellipsoid|"
        "Ellipsoid = Clarke 1880 (IGN)|Primem = Paris|"
    ),
    "GeogGeodeticDatum": 32767,
    "GeogPrimeMeridian": 8903,
    "GeogAngularUnits": 9102,
    "GeogEllipsoid": 32767,
    "GeogSemiMajorAxis": 6378249.2,
    "GeogInvFlattening": 293.466021293627,
    "ProjectedCSType": 32767,
    "Projection": 32767,
    "ProjCoordTrans": 9,
    "ProjLinearUnits": 9001,
    "ProjNatOriginLong": 0.0,
    "ProjNatOriginLat": 46.8,
    "ProjFalseEasting": 600000.0,
    "ProjFalseNorthing": 2200000.0,
    "ProjScaleAtNatOrigin": 0.99987742,
}

EPSG_CODES: list[int] = [
    2039, 2046, 2056, 2057, 2065, 2100, 2154, 21781, 2193, 2263,
    26917, 27572, 27700, 28992, 2953, 3031, 3035, 3067, 3088, 31370,
    32633, 32661, 32761, 3301, 3310, 3338, 3347, 3375, 3395, 3408,
    3410, 3413, 3857, 3975, 3978, 3993, 4087, 4326, 4267, 5070,
    5514, 5880, 6318, 6933, 7845, 9377,
]  # fmt: skip
"""EPSG codes written as coded GeoKeys; each also gets a cached epsg.io JSON."""

CASES: list[Case] = [
    # One case per CT code GDAL can write.
    Case("tmerc", "proj", f"{_TMERC} +ellps=WGS84", tags=("ct:1",)),
    Case("omerc_variant_a", "proj", f"{_OMERC} +no_uoff +ellps=WGS84", tags=("ct:3",)),
    Case(
        "labrd",
        "proj",
        "+proj=labrd +lat_0=-18.9 +lon_0=46.43722917 +azi=18.9 +k=0.9995 +x_0=400000 +y_0=800000 +ellps=intl",
        tags=("ct:4",),
    ),
    Case("merc_1sp", "proj", "+proj=merc +lon_0=10 +k=0.98 +ellps=WGS84", tags=("ct:7",)),
    Case("merc_2sp", "proj", "+proj=merc +lat_ts=30 +lon_0=10 +ellps=WGS84", tags=("ct:7",)),
    Case(
        "lcc_2sp",
        "proj",
        "+proj=lcc +lat_1=33 +lat_2=45 +lat_0=23 +lon_0=-96 +ellps=WGS84",
        tags=("ct:8",),
    ),
    Case("lcc_1sp", "proj", f"{_LCC_1SP} +lon_0=2.3", tags=("ct:9",)),
    Case(
        "laea",
        "proj",
        "+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80",
        tags=("ct:10",),
    ),
    Case(
        "aea",
        "proj",
        "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +ellps=WGS84",
        tags=("ct:11",),
    ),
    Case("aeqd", "proj", "+proj=aeqd +lat_0=40 +lon_0=-100 +ellps=WGS84", tags=("ct:12",)),
    Case(
        "eqdc",
        "proj",
        "+proj=eqdc +lat_1=33 +lat_2=45 +lat_0=23 +lon_0=-96 +ellps=WGS84",
        tags=("ct:13",),
    ),
    Case(
        "stere_oblique",
        "proj",
        "+proj=stere +lat_0=46.5 +lon_0=-66.5 +k=0.999912 +ellps=WGS84",
        tags=("ct:14",),
    ),
    Case("stere_polar_a", "proj", "+proj=stere +lat_0=90 +k=0.994 +lon_0=0 +ellps=WGS84", tags=("ct:15",)),
    Case("stere_polar_b", "proj", "+proj=stere +lat_0=90 +lat_ts=71 +lon_0=-45 +ellps=WGS84", tags=("ct:15",)),
    Case("stere_south_a", "proj", "+proj=stere +lat_0=-90 +k=0.994 +lon_0=0 +ellps=WGS84", tags=("ct:15",)),
    Case("stere_south_b", "proj", "+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +ellps=WGS84", tags=("ct:15",)),
    Case(
        "stere_polar_scaled_wkt",
        "wkt",
        _polar_stereographic(71, 0.9),
        note=(
            "Polar_Stereographic off the pole with scale != 1: PROJ keeps a non-EPSG "
            "WKT1 method and cannot export it, so gdal.proj4 is null"
        ),
        tags=("ct:15",),
    ),
    Case(
        "stere_polar_k1_wkt",
        "wkt",
        _polar_stereographic(90, 1),
        note="Scale 1 at the pole: PROJ picks variant B with lat_ts = 90",
        tags=("ct:15",),
    ),
    Case(
        "sterea",
        "proj",
        "+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel",
        tags=("ct:16",),
    ),
    Case("eqc", "proj", "+proj=eqc +lat_ts=30 +lon_0=10 +ellps=WGS84", tags=("ct:17",)),
    Case("cass", "proj", "+proj=cass +lat_0=10 +lon_0=-61 +ellps=WGS84", tags=("ct:18",)),
    Case("gnom", "proj", "+proj=gnom +lat_0=40 +lon_0=-100 +ellps=WGS84", tags=("ct:19",)),
    Case("mill", "proj", "+proj=mill +lon_0=0 +ellps=WGS84", tags=("ct:20",)),
    Case("ortho", "proj", "+proj=ortho +lat_0=40 +lon_0=-100 +ellps=WGS84", tags=("ct:21",)),
    Case("poly", "proj", "+proj=poly +lat_0=0 +lon_0=-54 +ellps=WGS84", tags=("ct:22",)),
    Case("robin", "proj", "+proj=robin +lon_0=0 +ellps=WGS84", tags=("ct:23",)),
    Case("sinu_sphere", "proj", "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181", tags=("ct:24", "sphere")),
    Case("vandg", "proj", "+proj=vandg +lon_0=0 +ellps=WGS84", tags=("ct:25",)),
    Case(
        "nzmg",
        "proj",
        "+proj=nzmg +lat_0=-41 +lon_0=173 +x_0=2510000 +y_0=6023150 +ellps=intl",
        tags=("ct:26",),
    ),
    Case(
        "tmso",
        "proj",
        "+proj=tmerc +lat_0=0 +lon_0=19 +k=1 +x_0=0 +y_0=0 +axis=wsu +ellps=WGS84",
        tags=("ct:27",),
    ),
    Case("cea", "proj", "+proj=cea +lat_ts=31 +lon_0=0 +ellps=WGS84", tags=("ct:28",)),
    Case("omerc_variant_b", "proj", f"{_OMERC} +ellps=WGS84", tags=("ct:9815",)),
    Case(
        "somerc",
        "proj",
        "+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel",
        note="GDAL writes CT 9815 with azimuth 90 and reads it back as +proj=somerc",
        tags=("ct:9815",),
    ),
    # Units: linear parameters in the projected unit, angular in GeogAngularUnits.
    Case(
        "lcc_2sp_usft",
        "proj",
        "+proj=lcc +lat_1=41.03333 +lat_2=40.66667 +lat_0=40.16667 +lon_0=-74 +x_0=300000 +y_0=0 +ellps=GRS80 +units=us-ft",
        tags=("ct:8", "linear:9003"),
    ),
    Case("tmerc_ft", "proj", f"{_TMERC} +ellps=WGS84 +units=ft", tags=("ct:1", "linear:9002")),
    Case("lcc_1sp_grad_wkt", "wkt", _lcc_1sp(_GEOG_CLRK80IGN_GRAD, 52), tags=("ct:9", "angular:9105")),
    Case("geog_grad_wkt", "wkt", _GEOG_CLRK80IGN_GRAD, tags=("geographic", "angular:9105")),
    Case(
        "lcc_1sp_paris_grad",
        "proj",
        f"{_LCC_1SP} +lon_0=0 +pm=paris",
        note=(
            "GDAL writes grads for +pm=paris and its prime meridian write/read "
            "disagree with each other (spec Q3); a known failure in async-geotiff"
        ),
        tags=("ct:9", "angular:9105", "pm:paris"),
    ),
    # Datum, ellipsoid, and prime meridian variants.
    Case(
        "aea_nad27",
        "proj",
        "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +datum=NAD27",
        tags=("ct:11", "datum:epsg"),
    ),
    Case("tmerc_datum_wgs84", "proj", f"{_TMERC} +datum=WGS84", tags=("ct:1", "datum:epsg")),
    Case("geog_sphere", "proj", "+proj=longlat +R=6371007.181", tags=("geographic", "sphere")),
    Case(
        "tmerc_towgs84",
        "proj",
        "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=bessel +towgs84=598.1,73.7,418.2,0.202,0.045,-2.455,6.7",
        note="GeogTOWGS84GeoKey; needs an async-tiff release with key 2062 (async-tiff#368)",
        tags=("ct:1", "towgs84"),
    ),
    Case(
        "lcc_1sp_paris_deg_wkt",
        "wkt",
        _lcc_1sp(_GEOG_CLRK80IGN_PARIS_DEG, 46.8),
        tags=("ct:9", "pm:paris"),
    ),
    Case("lcc_1sp_pm_user", "proj", f"{_LCC_1SP} +lon_0=0 +pm=2.5", tags=("ct:9", "pm:user")),
    Case(
        "lcc_1sp_pm_epsg_tifffile",
        "geokeys",
        _LCC_1SP_PM_EPSG_GEOKEYS,
        note="Written with tifffile: GDAL never writes GeogPrimeMeridian codes",
        tags=("ct:9", "pm:epsg"),
    ),
    Case("longlat_grs80", "proj", "+proj=longlat +ellps=GRS80", tags=("geographic",)),
    Case(
        "utm_bessel",
        "proj",
        "+proj=utm +zone=33 +ellps=bessel",
        note="GDAL writes Projection = 16033 and no CT key",
        tags=("projection:16033",),
    ),
    # Coded and citation forms.
    *[Case(f"epsg_{code}", "epsg", f"EPSG:{code}", tags=("epsg",)) for code in EPSG_CODES],
    Case("moll", "proj", "+proj=moll +lon_0=0 +ellps=WGS84", note="ESRI PE String citation", tags=("pe-string",)),
    Case(
        "krovak",
        "proj",
        "+proj=krovak +lat_0=49.5 +lon_0=24.83333333333333 +alpha=30.28813972222222 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel",
        note="ESRI PE String citation",
        tags=("pe-string",),
    ),
    Case("esri_54009", "epsg", "ESRI:54009", note="ESRI PE String citation with GeogGeodeticDatum = 6326", tags=("pe-string",)),
    Case(
        "eqearth",
        "proj",
        "+proj=eqearth +lon_0=0 +ellps=WGS84",
        note="GDAL writes no GeoKeys for Equal Earth; the sidecar is disabled, so gdal.projjson is null",
        tags=("no-keys",),
    ),
]
