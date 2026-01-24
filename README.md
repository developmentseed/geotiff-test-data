# netcdf4-test-data

Test data for NetCDF4/HDF5 parsers, designed for [VirtualiZarr](https://github.com/zarr-developers/VirtualiZarr) testing.

## Installation

```bash
pixi install
```

## Usage

```bash
pixi run generate              # Generate .nc files
pixi run info                  # Generate _info.md files (h5dump -H -p)
pixi run catalog               # Generate CATALOG.md
pixi run check                 # Verify all generated files are up-to-date
pixi run upload <bucket/prefix> # Upload .nc files to S3
```

## Test Files

See [CATALOG.md](CATALOG.md) for the auto-generated list of test files with their properties.

## Adding new test cases

1. Create `netcdf4_generated/generators/{name}.py` with a `generate(output_path: Path)` function
2. Run `pixi run generate && pixi run info && pixi run catalog`

## Acknowledgments

This project structure is derived from [geotiff-test-data](https://github.com/developmentseed/geotiff-test-data) by Development Seed, licensed under the MIT License.
