"""CLI for generating test NetCDF4/HDF5 files."""

import importlib.util
import sys
from pathlib import Path


def main() -> None:
    """Generate all test NetCDF4 files."""
    package_dir = Path(__file__).parent
    generators_dir = package_dir / "generators"
    output_dir = package_dir / "data"
    output_dir.mkdir(exist_ok=True)

    # Find all generator Python files
    generator_files = sorted(generators_dir.glob("*.py"))
    generator_files = [f for f in generator_files if f.name != "__init__.py"]

    if not generator_files:
        print("No generator files found!", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(generator_files)} generator(s)")
    print(f"Output directory: {output_dir.absolute()}\n")

    for generator_path in generator_files:
        # Import the module
        module_name = f"netcdf4_generated.generators.{generator_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, generator_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load {generator_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Call generate function with output path matching the script name
        if hasattr(module, "generate"):
            output_path = output_dir / f"{generator_path.stem}.nc"
            module.generate(output_path)
            print(f"Generated: {output_path}")
        else:
            raise ValueError(
                f"Module {module_name} does not have a generate() function"
            )

    print(f"\nComplete! Generated files in {output_dir}/")


if __name__ == "__main__":
    main()
