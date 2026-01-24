"""Test that all generated NetCDF4 files can be loaded with xarray."""

from pathlib import Path

import pytest
import xarray as xr

DATA_DIR = Path(__file__).parent.parent / "netcdf4_generated" / "data"


def get_nc_files():
    """Get all .nc files in the data directory."""
    return sorted(DATA_DIR.glob("*.nc"))


@pytest.fixture(params=get_nc_files(), ids=lambda p: p.name)
def nc_file(request):
    """Fixture that yields each .nc file path."""
    return request.param


def test_xarray_open_dataset(nc_file):
    """Test that each file can be opened with xarray."""
    ds = xr.open_dataset(nc_file)
    assert ds is not None
    ds.close()


def test_xarray_has_dimensions(nc_file):
    """Test that each file has expected dimensions."""
    ds = xr.open_dataset(nc_file)
    assert "time" in ds.dims
    assert "x" in ds.dims
    assert "y" in ds.dims
    ds.close()


def test_xarray_has_coordinates(nc_file):
    """Test that each file has coordinate variables."""
    ds = xr.open_dataset(nc_file)
    assert "time" in ds.coords
    assert "x" in ds.coords
    assert "y" in ds.coords
    ds.close()


def test_xarray_has_temperature(nc_file):
    """Test that each file has the temperature variable."""
    ds = xr.open_dataset(nc_file)
    assert "temperature" in ds.data_vars
    assert ds["temperature"].dims == ("time", "y", "x")
    ds.close()


def test_xarray_data_readable(nc_file):
    """Test that data can be read from the file."""
    ds = xr.open_dataset(nc_file)
    # Read a small slice to verify data is accessible
    data = ds["temperature"].isel(time=0, x=slice(0, 10), y=slice(0, 10)).values
    assert data.shape == (10, 10)
    ds.close()
