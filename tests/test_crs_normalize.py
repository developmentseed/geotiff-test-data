"""Check the name-free CRS core, test point, and ellipsoid base helpers."""

import pytest
from pyproj import CRS

from crs.normalize import core_of, ellipsoid_longlat, point_for, project_point

GRAD_WKT = (
    'PROJCS["unknown",GEOGCS["unknown",DATUM["unknown",SPHEROID["Clarke 1880 (IGN)",6378249.2,293.466021293627]],'
    'PRIMEM["Greenwich",0],UNIT["grad",0.01570796326794897]],PROJECTION["Lambert_Conformal_Conic_1SP"],'
    'PARAMETER["latitude_of_origin",52],PARAMETER["central_meridian",0],PARAMETER["scale_factor",0.99987742],'
    'PARAMETER["false_easting",600000],PARAMETER["false_northing",2200000],UNIT["metre",1]]'
)


def test_core_of_utm():
    core = core_of(CRS.from_epsg(32633))
    assert core["type"] == "ProjectedCRS"
    assert core["method"] == {"name": "Transverse Mercator", "epsg": 9807}
    assert core["parameters"] == [
        {"epsg": 8801, "name": "Latitude of natural origin", "value": 0.0},
        {"epsg": 8802, "name": "Longitude of natural origin", "value": 15.0},
        {"epsg": 8805, "name": "Scale factor at natural origin", "value": 0.9996},
        {"epsg": 8806, "name": "False easting", "value": 500000.0},
        {"epsg": 8807, "name": "False northing", "value": 0.0},
    ]
    assert core["ellipsoid"] == {"a": 6378137.0, "rf": 298.257223563, "b": None}
    assert core["prime_meridian_deg"] == 0.0
    assert core["angular_unit_deg"] == pytest.approx(1.0)
    assert core["linear_unit_m"] == 1.0
    assert core["axes"] == ["east", "north"]
    assert core["towgs84"] is None


def test_core_of_grads():
    core = core_of(CRS.from_wkt(GRAD_WKT))
    assert core["parameters"][0]["value"] == pytest.approx(46.8)
    assert core["angular_unit_deg"] == pytest.approx(0.9)


def test_core_of_feet():
    core = core_of(
        CRS.from_proj4(
            "+proj=lcc +lat_1=41.03333 +lat_2=40.66667 +lat_0=40.16667 +lon_0=-74 +x_0=300000 +y_0=0 +ellps=GRS80 +units=us-ft"
        )
    )
    easting = next(p for p in core["parameters"] if p["epsg"] == 8826)
    assert easting["value"] == pytest.approx(300000.0)
    assert core["linear_unit_m"] == pytest.approx(0.3048006096012192)


def test_core_of_bound_crs():
    core = core_of(
        CRS.from_proj4(
            "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=bessel +towgs84=598.1,73.7,418.2,0.202,0.045,-2.455,6.7"
        )
    )
    assert core["type"] == "BoundCRS"
    assert core["method"]["epsg"] == 9807
    assert core["towgs84"] == [598.1, 73.7, 418.2, 0.202, 0.045, -2.455, 6.7]


def test_core_of_sphere_and_geographic():
    core = core_of(CRS.from_proj4("+proj=longlat +R=6371007.181"))
    assert core["type"] == "GeographicCRS"
    assert core["method"] is None
    assert core["ellipsoid"] == {"a": 6371007.181, "rf": None, "b": 6371007.181}
    assert core["linear_unit_m"] is None


def test_core_of_south_orientated_axes():
    core = core_of(
        CRS.from_proj4(
            "+proj=tmerc +lat_0=0 +lon_0=19 +k=1 +x_0=0 +y_0=0 +axis=wsu +ellps=WGS84"
        )
    )
    assert core["axes"] == ["west", "south"]


def test_point_for():
    assert point_for(core_of(CRS.from_epsg(32633))) == (18.0, 8.0)
    assert point_for(
        core_of(CRS.from_proj4("+proj=stere +lat_0=90 +k=0.994 +lon_0=0 +ellps=WGS84"))
    ) == (3.0, 82.0)
    assert point_for(core_of(CRS.from_epsg(4326))) == (10.0, 40.0)


def test_project_point():
    assert project_point(CRS.from_epsg(32633), 15.0, 0.0) == pytest.approx(
        (500000.0, 0.0)
    )
    # A grads geographic CRS: degrees in, grads out.
    assert project_point(
        CRS.from_wkt(GRAD_WKT).geodetic_crs, 3.0, 54.8
    ) == pytest.approx((3.3333333333, 60.8888888889))


def test_ellipsoid_longlat_sphere():
    assert (
        ellipsoid_longlat(CRS.from_proj4("+proj=sinu +R=6371007.181"))
        .to_proj4()
        .startswith("+proj=longlat +R=6371007.181")
    )
