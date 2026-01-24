"""Utilities for writing HDF5/NetCDF4 test files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py
import numpy as np


def write_netcdf4(
    path: Path,
    variables: dict[str, tuple[np.ndarray, dict[str, Any]]],
    dimensions: dict[str, int],
    global_attrs: dict[str, Any] | None = None,
    *,
    cloud_optimized: bool = False,
    chunk_sizes: dict[str, tuple[int, ...]] | None = None,
    compression: str | None = "gzip",
    compression_opts: int = 4,
) -> None:
    """
    Write a NetCDF4/HDF5 file with control over layout optimization.

    Parameters
    ----------
    path : Path
        Output file path.
    variables : dict
        Mapping of variable name to (data, attrs) tuples.
        Variables with names matching dimension names are treated as coordinates.
    dimensions : dict
        Mapping of dimension name to size.
    global_attrs : dict, optional
        Global file attributes.
    cloud_optimized : bool
        If True, use settings that consolidate metadata:
        - libver='latest' for SWMR compatibility
        - Large meta_block_size to consolidate metadata blocks
    chunk_sizes : dict, optional
        Mapping of variable name to chunk shape.
    compression : str, optional
        Compression filter name (default: "gzip").
    compression_opts : int, optional
        Compression level (default: 4).
    """
    if cloud_optimized:
        _write_cloud_optimized(
            path,
            variables,
            dimensions,
            global_attrs,
            chunk_sizes,
            compression,
            compression_opts,
        )
    else:
        _write_fragmented(
            path,
            variables,
            dimensions,
            global_attrs,
            chunk_sizes,
            compression,
            compression_opts,
        )


def _setup_dimension_scales(
    f: h5py.File,
    variables: dict[str, tuple[np.ndarray, dict[str, Any]]],
    dimensions: dict[str, int],
) -> dict[str, h5py.Dataset]:
    """Create dimension scale datasets and return them."""
    dim_datasets = {}
    dim_order = list(dimensions.keys())

    # First, identify coordinate variables (1D variables matching dimension names)
    for dim_name in dim_order:
        if dim_name in variables:
            data, _ = variables[dim_name]
            if data.ndim == 1 and len(data) == dimensions[dim_name]:
                dim_datasets[dim_name] = f[dim_name]

    # Make each coordinate a dimension scale
    for dim_name, dset in dim_datasets.items():
        dset.make_scale(dim_name)

    return dim_datasets


def _attach_dimension_scales(
    dset: h5py.Dataset,
    dim_datasets: dict[str, h5py.Dataset],
    dimensions: dict[str, int],
    shape: tuple[int, ...],
) -> None:
    """Attach dimension scales to a dataset based on its shape."""
    dim_order = list(dimensions.keys())

    # Match dimensions by size
    for i, size in enumerate(shape):
        for dim_name in dim_order:
            if dimensions[dim_name] == size and dim_name in dim_datasets:
                dset.dims[i].attach_scale(dim_datasets[dim_name])
                dset.dims[i].label = dim_name
                break


def _write_cloud_optimized(
    path: Path,
    variables: dict[str, tuple[np.ndarray, dict[str, Any]]],
    dimensions: dict[str, int],
    global_attrs: dict[str, Any] | None,
    chunk_sizes: dict[str, tuple[int, ...]] | None,
    compression: str | None,
    compression_opts: int,
) -> None:
    """Write with settings that consolidate metadata."""
    with h5py.File(
        path,
        "w",
        libver="latest",
        meta_block_size=1048576,  # 1MB metadata blocks
    ) as f:
        # Write all datasets first
        for name, (data, _) in variables.items():
            chunks = chunk_sizes.get(name) if chunk_sizes else None
            if chunks:
                f.create_dataset(
                    name,
                    data=data,
                    chunks=chunks,
                    compression=compression,
                    compression_opts=compression_opts,
                )
            else:
                f.create_dataset(name, data=data)

        # Set up dimension scales
        dim_datasets = _setup_dimension_scales(f, variables, dimensions)

        # Attach dimension scales to non-coordinate variables
        for name, (data, _) in variables.items():
            if name not in dim_datasets and data.ndim > 0:
                _attach_dimension_scales(f[name], dim_datasets, dimensions, data.shape)

        # Write all attributes after datasets
        if global_attrs:
            for key, value in global_attrs.items():
                f.attrs[key] = value

        for name, (_, attrs) in variables.items():
            for key, value in attrs.items():
                f[name].attrs[key] = value


def _write_fragmented(
    path: Path,
    variables: dict[str, tuple[np.ndarray, dict[str, Any]]],
    dimensions: dict[str, int],
    global_attrs: dict[str, Any] | None,
    chunk_sizes: dict[str, tuple[int, ...]] | None,
    compression: str | None,
    compression_opts: int,
) -> None:
    """Write with interleaved metadata to fragment it."""
    with h5py.File(path, "w") as f:
        # Interleave dataset creation with attribute writes
        # to fragment metadata throughout the file
        if global_attrs:
            for key, value in global_attrs.items():
                f.attrs[key] = value

        for name, (data, attrs) in variables.items():
            chunks = chunk_sizes.get(name) if chunk_sizes else None
            if chunks:
                dset = f.create_dataset(
                    name,
                    data=data,
                    chunks=chunks,
                    compression=compression,
                    compression_opts=compression_opts,
                )
            else:
                dset = f.create_dataset(name, data=data)

            # Write attributes immediately after each dataset
            for key, value in attrs.items():
                dset.attrs[key] = value

        # Set up dimension scales
        dim_datasets = _setup_dimension_scales(f, variables, dimensions)

        # Attach dimension scales to non-coordinate variables
        for name, (data, _) in variables.items():
            if name not in dim_datasets and data.ndim > 0:
                _attach_dimension_scales(f[name], dim_datasets, dimensions, data.shape)
