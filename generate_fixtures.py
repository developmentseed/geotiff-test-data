"""The CLI that generates all test files."""

import importlib.util
import sys
from pathlib import Path

MODULES = ["rasterio_generated", "tifffile_generated"]


def generate_module(module: str) -> None:
    """Generate the test files for one generator module."""
    fixtures_dir = Path(__file__).parent / module / "fixtures"
    output_dir = fixtures_dir
    output_dir.mkdir(exist_ok=True)

    # Find all fixture Python files
    fixture_files = sorted(fixtures_dir.glob("*.py"))
    fixture_files = [f for f in fixture_files if f.name != "__init__.py"]

    if not fixture_files:
        print("No fixture files found!", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(fixture_files)} fixture(s)")
    print(f"Output directory: {output_dir.absolute()}\n")

    for fixture_path in fixture_files:
        # Import the module
        module_name = f"{module}.fixtures.{fixture_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, fixture_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load {fixture_path}")

        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)

        # Call generate function with output path matching the script name
        if hasattr(mod, "generate"):
            output_path = output_dir / f"{fixture_path.stem}.tif"
            mod.generate(output_path)
            print(f"✓ Generated: {output_path}")
        else:
            raise ValueError(
                f"Module {module_name} does not have a generate() function"
            )

    print(f"\nComplete! Generated files in {output_dir}/")


def main() -> None:
    """Generate the test files for all generator modules."""
    for module in MODULES:
        generate_module(module)


if __name__ == "__main__":
    main()
