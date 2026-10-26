"""Raw GeoKey directory decoding and encoding.

The corpus manifest records exactly which GeoKeys GDAL wrote, keyed by the
GeoTIFF spec name without the ``GeoKey`` suffix. Reading the raw tags with
tifffile, rather than through a GeoTIFF reader, keeps the record independent of
any implementation under test and includes keys such as ``GeogTOWGS84`` that
some readers do not expose yet.

Key ids come from OGC 19-008r4 (GeoTIFF 1.1) and libgeotiff ``geokeys.inc``.
"""

from __future__ import annotations

from pathlib import Path

import tifffile

GEOKEY_DIRECTORY_TAG = 34735
GEOKEY_DOUBLE_PARAMS_TAG = 34736
GEOKEY_ASCII_PARAMS_TAG = 34737

GEOKEY_IDS: dict[str, int] = {
    # GeoTIFF configuration keys
    "GTModelType": 1024,
    "GTRasterType": 1025,
    "GTCitation": 1026,
    # Geodetic CRS parameter keys
    "GeographicType": 2048,
    "GeogCitation": 2049,
    "GeogGeodeticDatum": 2050,
    "GeogPrimeMeridian": 2051,
    "GeogLinearUnits": 2052,
    "GeogLinearUnitSize": 2053,
    "GeogAngularUnits": 2054,
    "GeogAngularUnitSize": 2055,
    "GeogEllipsoid": 2056,
    "GeogSemiMajorAxis": 2057,
    "GeogSemiMinorAxis": 2058,
    "GeogInvFlattening": 2059,
    "GeogAzimuthUnits": 2060,
    "GeogPrimeMeridianLong": 2061,
    "GeogTOWGS84": 2062,
    # Projected CRS parameter keys
    "ProjectedCSType": 3072,
    "PCSCitation": 3073,
    "Projection": 3074,
    "ProjCoordTrans": 3075,
    "ProjLinearUnits": 3076,
    "ProjLinearUnitSize": 3077,
    "ProjStdParallel1": 3078,
    "ProjStdParallel2": 3079,
    "ProjNatOriginLong": 3080,
    "ProjNatOriginLat": 3081,
    "ProjFalseEasting": 3082,
    "ProjFalseNorthing": 3083,
    "ProjFalseOriginLong": 3084,
    "ProjFalseOriginLat": 3085,
    "ProjFalseOriginEasting": 3086,
    "ProjFalseOriginNorthing": 3087,
    "ProjCenterLong": 3088,
    "ProjCenterLat": 3089,
    "ProjCenterEasting": 3090,
    "ProjCenterNorthing": 3091,
    "ProjScaleAtNatOrigin": 3092,
    "ProjScaleAtCenter": 3093,
    "ProjAzimuthAngle": 3094,
    "ProjStraightVertPoleLong": 3095,
    "ProjRectifiedGridAngle": 3096,
    # Vertical CRS parameter keys
    "VerticalCSType": 4096,
    "VerticalCitation": 4097,
    "VerticalDatum": 4098,
    "VerticalUnits": 4099,
    # GeoTIFF 1.1
    "CoordinateEpoch": 5120,
}
"""GeoTIFF spec key names (without the ``GeoKey`` suffix) to key ids."""

GEOKEY_NAMES: dict[int, str] = {key_id: name for name, key_id in GEOKEY_IDS.items()}
"""Key ids to GeoTIFF spec key names."""

GeoKeyValue = int | float | str | list[float]

# TIFF data type codes used in tifffile extratags.
_TIFF_SHORT = 3
_TIFF_DOUBLE = 12
_TIFF_ASCII = 2

_ASCII_TERMINATOR = "|"


def decode_geokeys(path: Path) -> dict[str, GeoKeyValue]:
    """Read the GeoKey directory of the first IFD of a TIFF, keyed by key name.

    SHORT values come back as ``int``, a single DOUBLE as ``float``, several
    DOUBLEs as ``list[float]``, and ASCII values as ``str`` with the one
    trailing ``|`` terminator removed. Ids outside :data:`GEOKEY_IDS` are
    keyed ``unknown_<id>``.
    """
    with tifffile.TiffFile(path) as tif:
        tags = tif.pages[0].tags
        directory = list(tags[GEOKEY_DIRECTORY_TAG].value)
        doubles = (
            list(tags[GEOKEY_DOUBLE_PARAMS_TAG].value)
            if GEOKEY_DOUBLE_PARAMS_TAG in tags
            else []
        )
        ascii_params = (
            tags[GEOKEY_ASCII_PARAMS_TAG].value
            if GEOKEY_ASCII_PARAMS_TAG in tags
            else ""
        )

    number_of_keys = directory[3]
    keys: dict[str, GeoKeyValue] = {}
    for i in range(number_of_keys):
        key_id, location, count, offset = directory[4 + 4 * i : 8 + 4 * i]
        name = GEOKEY_NAMES.get(key_id, f"unknown_{key_id}")
        if location == 0:
            keys[name] = int(offset)
        elif location == GEOKEY_DOUBLE_PARAMS_TAG:
            values = [float(v) for v in doubles[offset : offset + count]]
            keys[name] = values[0] if count == 1 else values
        elif location == GEOKEY_ASCII_PARAMS_TAG:
            text = ascii_params[offset : offset + count]
            keys[name] = text.removesuffix(_ASCII_TERMINATOR)
        else:
            raise ValueError(f"GeoKey {key_id} stored in unexpected tag {location}")
    return keys


def encode_geokeys(keys: dict[str, GeoKeyValue]) -> list[tuple]:
    """Build tifffile ``extratags`` for a GeoKey directory.

    Returns the directory (SHORT), double params (DOUBLE) and ASCII params
    (ASCII) tags, in that order, with directory entries sorted by key id as the
    GeoTIFF spec requires.
    """
    entries: list[tuple[int, int, int, int]] = []
    doubles: list[float] = []
    ascii_params = ""

    for name, value in sorted(keys.items(), key=lambda item: GEOKEY_IDS[item[0]]):
        key_id = GEOKEY_IDS[name]
        if isinstance(value, bool):
            raise TypeError(f"GeoKey {name} cannot be a bool")
        if isinstance(value, int):
            entries.append((key_id, 0, 1, value))
        elif isinstance(value, float):
            entries.append((key_id, GEOKEY_DOUBLE_PARAMS_TAG, 1, len(doubles)))
            doubles.append(value)
        elif isinstance(value, list):
            entries.append((key_id, GEOKEY_DOUBLE_PARAMS_TAG, len(value), len(doubles)))
            doubles.extend(float(v) for v in value)
        elif isinstance(value, str):
            text = value + _ASCII_TERMINATOR
            entries.append((key_id, GEOKEY_ASCII_PARAMS_TAG, len(text), len(ascii_params)))
            ascii_params += text
        else:
            raise TypeError(f"Unsupported GeoKey value for {name}: {value!r}")

    directory = [1, 1, 0, len(entries)]
    for entry in entries:
        directory.extend(entry)

    extratags = [(GEOKEY_DIRECTORY_TAG, _TIFF_SHORT, len(directory), directory, True)]
    if doubles:
        extratags.append((GEOKEY_DOUBLE_PARAMS_TAG, _TIFF_DOUBLE, len(doubles), doubles, True))
    if ascii_params:
        extratags.append(
            (GEOKEY_ASCII_PARAMS_TAG, _TIFF_ASCII, len(ascii_params), ascii_params, True)
        )
    return extratags
