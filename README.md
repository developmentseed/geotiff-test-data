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

This will execute all generator scripts in [geotiff_test_data/generators/](geotiff_test_data/generators/) and save the output GeoTIFF files next to each Python file, with the same name but a `.tif` extension.

## Adding new test cases

To add a new test case:

1. Create a new Python file in `geotiff_test_data/fixtures/`
2. Implement a `generate(output_path: Path)` function that creates the GeoTIFF

Run `pixi run generate`.

## Image Sources

### Vantor (formerly Maxar)

Some test images are copyright [Vantor](https://vantor.com/), provided under a [Creative Commons Attribution Non Commercial](https://spdx.org/licenses/CC-BY-NC-4.0.html) license via the [Maxar Open Data Program](https://registry.opendata.aws/maxar-open-data/).
