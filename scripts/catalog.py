#!/usr/bin/env python
"""Generate CATALOG.md from all NetCDF4 test files."""

import hashlib
import re
from pathlib import Path
from functools import reduce
from operator import mul

import h5py
import numpy as np


def get_generator_description(generators_dir: Path, filename: str) -> str:
    """Extract DESCRIPTION from the generator module."""
    stem = filename.replace(".nc", "")
    generator_path = generators_dir / f"{stem}.py"

    if not generator_path.exists():
        return ""

    content = generator_path.read_text()
    # Match both single-line and multi-line (with parens) DESCRIPTION
    match = re.search(
        r'^DESCRIPTION\s*=\s*\(?\s*["\'](.+?)["\']', content, re.MULTILINE | re.DOTALL
    )
    return match.group(1) if match else ""


def get_file_info(path: Path) -> dict:
    """Extract key metadata from an HDF5/NetCDF4 file."""
    info = {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "md5": hashlib.md5(path.read_bytes()).hexdigest(),
    }

    with h5py.File(path, "r") as f:
        datasets = []
        groups = []
        max_depth = 0

        def visit_item(name, obj):
            nonlocal max_depth
            depth = name.count("/") + 1  # depth 1 = direct child of root

            if isinstance(obj, h5py.Dataset):
                max_depth = max(max_depth, depth)
                datasets.append(
                    {
                        "name": name,
                        "dtype": str(obj.dtype),
                        "shape": obj.shape,
                        "chunks": obj.chunks,
                        "compression": obj.compression,
                        "compression_opts": obj.compression_opts,
                        "size": obj.size,
                    }
                )
            elif isinstance(obj, h5py.Group):
                max_depth = max(max_depth, depth)
                groups.append(name)

        f.visititems(visit_item)

        # Find largest dataset as the "main" variable
        main_ds = max(datasets, key=lambda d: d["size"]) if datasets else None

        if main_ds:
            info["dtype"] = main_ds["dtype"]
            info["shape"] = main_ds["shape"]
            info["chunks"] = main_ds["chunks"]
            info["compression"] = main_ds["compression"]
            info["compression_opts"] = main_ds["compression_opts"]

            # Calculate chunk size in bytes
            if main_ds["chunks"]:
                dtype_size = np.dtype(main_ds["dtype"]).itemsize
                chunk_elements = reduce(mul, main_ds["chunks"], 1)
                info["chunk_size_bytes"] = chunk_elements * dtype_size

        info["num_variables"] = len(datasets)
        info["num_groups"] = len(groups)
        info["max_depth"] = max_depth

    return info


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.0f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.0f} TB"


def generate_catalog(repo_dir: Path) -> str:
    """Generate catalog markdown content."""
    lines = [
        "# Test Data Catalog",
        "",
    ]

    # Find all .nc files
    data_dir = repo_dir / "netcdf4_generated" / "data"
    generators_dir = repo_dir / "netcdf4_generated" / "generators"
    nc_files = sorted(data_dir.glob("*.nc"))

    # Check for S3 bucket config
    s3_config = repo_dir / ".s3-bucket"
    s3_bucket = s3_config.read_text().strip() if s3_config.exists() else None

    if not nc_files:
        lines.append("*No test files found.*")
        return "\n".join(lines)

    # Build table
    lines.append(
        "| File | S3 URL | Description | Size | MD5 | Vars | Groups | Depth | Dtype | Shape | Chunks | Chunk Size | Compression |"
    )
    lines.append(
        "|------|--------|-------------|------|-----|------|--------|-------|-------|-------|--------|------------|-------------|"
    )

    for nc_path in nc_files:
        info = get_file_info(nc_path)
        description = get_generator_description(generators_dir, info["filename"])

        chunks_str = str(info.get("chunks")) if info.get("chunks") else "contiguous"
        chunk_size_str = (
            format_size(info["chunk_size_bytes"])
            if info.get("chunk_size_bytes")
            else "-"
        )
        comp = info.get("compression")
        comp_opts = info.get("compression_opts")
        comp_str = f"{comp}({comp_opts})" if comp else "none"

        if s3_bucket:
            s3_url = f"s3://{s3_bucket}/{info['filename']}"
        else:
            s3_url = "-"

        lines.append(
            f"| [`{info['filename']}`](netcdf4_generated/data/{info['filename']}) "
            f"| `{s3_url}` "
            f"| {description} "
            f"| {format_size(info['size_bytes'])} "
            f"| `{info['md5']}` "
            f"| {info.get('num_variables', 0)} "
            f"| {info.get('num_groups', 0)} "
            f"| {info.get('max_depth', 0)} "
            f"| {info.get('dtype', '')} "
            f"| {info.get('shape', '')} "
            f"| {chunks_str} "
            f"| {chunk_size_str} "
            f"| {comp_str} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    repo_dir = Path(__file__).parent.parent
    catalog_path = repo_dir / "CATALOG.md"

    content = generate_catalog(repo_dir)
    catalog_path.write_text(content)
    print(f"Generated: {catalog_path}")


if __name__ == "__main__":
    main()
