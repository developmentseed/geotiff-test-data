# geotiff-test-data

Test data for GeoTIFF parsers

## Installation

This project uses [pixi](https://pixi.sh) for dependency management.

```bash
pixi install
```

## Usage

### Generate all test files

```bash
pixi run generate
```

This command runs all generator scripts in [rasterio_generated/fixtures/](rasterio_generated/fixtures/) and [tifffile_generated/fixtures/](tifffile_generated/fixtures/). It saves each output GeoTIFF file next to its Python script, with the same name and a `.tif` extension.

## Adding new test cases

To add a new test case:

1. Create a new Python file in `rasterio_generated/fixtures/`. For a layout that rasterio cannot write, put the file in `tifffile_generated/fixtures/`
2. Implement a `generate(output_path: Path)` function that creates the GeoTIFF

Run `pixi run generate` and `pixi run info`.

## Image Sources

Images in the `real_data/` folder are sourced from various open data programs. See the individual README files in each subfolder for details.
