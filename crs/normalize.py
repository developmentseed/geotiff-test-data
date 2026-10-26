"""Name-free CRS summaries and the per-fixture test point.

The manifest stores GDAL's full PROJJSON, which is what a PROJ-backed reader
compares against. Readers without a PROJ database compare the ``core``
produced here instead: method, parameters in degrees and metres, ellipsoid
axes, prime meridian, unit sizes, axis directions, and TOWGS84.
"""

from __future__ import annotations

import math

from pyproj import CRS, Transformer

DEG_PER_RAD = 180.0 / math.pi

_LON_PARAMS = (
    "Longitude of natural origin",
    "Longitude of false origin",
    "Longitude of projection centre",
    "Longitude of origin",
)
_LAT_PARAMS = (
    "Latitude of natural origin",
    "Latitude of false origin",
    "Latitude of projection centre",
    "Latitude of standard parallel",
    "Latitude of 1st standard parallel",
)


def _inner(crs: CRS) -> CRS:
    """The CRS a BoundCRS wraps, or the CRS itself."""
    return crs.source_crs if crs.is_bound else crs


def _parameter_value(parameter: dict) -> float:
    """A PROJJSON parameter value in degrees, metres, or unity."""
    value = float(parameter["value"])
    unit = parameter["unit"]
    if isinstance(unit, str):
        return value
    factor = float(unit["conversion_factor"])
    if unit["type"] == "AngularUnit":
        return value * factor * DEG_PER_RAD
    return value * factor


def _parameter_epsg(parameter: dict) -> int | None:
    identifier = parameter.get("id")
    if identifier and identifier.get("authority") == "EPSG":
        return int(identifier["code"])
    return None


def core_of(crs: CRS) -> dict:
    """Summarize a CRS without names or ids, in degrees and metres."""
    inner = _inner(crs)
    projjson = inner.to_json_dict()
    if crs.is_bound:
        crs_type = "BoundCRS"
    elif inner.is_projected:
        crs_type = "ProjectedCRS"
    else:
        crs_type = "GeographicCRS"

    method = None
    parameters: list[dict] = []
    if "conversion" in projjson:
        conversion = projjson["conversion"]
        method = {
            "name": conversion["method"]["name"],
            "epsg": _parameter_epsg(conversion["method"]),
        }
        parameters = [
            {
                "epsg": _parameter_epsg(p),
                "name": p["name"],
                "value": _parameter_value(p),
            }
            for p in conversion.get("parameters", [])
        ]

    ellipsoid = inner.ellipsoid
    if ellipsoid.inverse_flattening:
        ellipsoid_core = {
            "a": ellipsoid.semi_major_metre,
            "rf": ellipsoid.inverse_flattening,
            "b": None,
        }
    else:
        ellipsoid_core = {
            "a": ellipsoid.semi_major_metre,
            "rf": None,
            "b": ellipsoid.semi_minor_metre,
        }

    prime_meridian = inner.prime_meridian
    geodetic = inner.geodetic_crs if inner.is_projected else inner
    return {
        "type": crs_type,
        "method": method,
        "parameters": parameters,
        "ellipsoid": ellipsoid_core,
        "prime_meridian_deg": prime_meridian.longitude
        * prime_meridian.unit_conversion_factor
        * DEG_PER_RAD,
        "angular_unit_deg": geodetic.axis_info[0].unit_conversion_factor * DEG_PER_RAD,
        "linear_unit_m": inner.axis_info[0].unit_conversion_factor
        if inner.is_projected
        else None,
        "axes": [axis.direction for axis in inner.axis_info],
        "towgs84": list(crs.coordinate_operation.towgs84) if crs.is_bound else None,
    }


def ellipsoid_longlat(crs: CRS) -> CRS:
    """A degree, Greenwich longlat CRS on the same ellipsoid as ``crs``."""
    ellipsoid = _inner(crs).ellipsoid
    if ellipsoid.inverse_flattening:
        return CRS.from_proj4(
            f"+proj=longlat +a={ellipsoid.semi_major_metre!r} +rf={ellipsoid.inverse_flattening!r}"
        )
    return CRS.from_proj4(f"+proj=longlat +R={ellipsoid.semi_major_metre!r}")


def point_for(core: dict) -> tuple[float, float]:
    """A lon/lat in degrees from Greenwich near the projection origin."""
    if core["method"] is None:
        return (10.0, 40.0)
    values = {p["name"]: p["value"] for p in core["parameters"]}
    lon0 = next((values[name] for name in _LON_PARAMS if name in values), 0.0)
    lat0 = next((values[name] for name in _LAT_PARAMS if name in values), 0.0)
    away_from_equator = 8.0 if lat0 >= 0 else -8.0
    lat = lat0 + away_from_equator if abs(lat0) < 80 else lat0 - away_from_equator
    return (lon0 + 3.0, lat)


def project_point(crs: CRS, lon: float, lat: float) -> tuple[float, float]:
    """Project a degree/Greenwich lon/lat into ``crs`` with no datum shift."""
    transformer = Transformer.from_crs(ellipsoid_longlat(crs), crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return (float(x), float(y))
