#!/bin/bash
# Generate h5dump info markdown files for all NetCDF4 files in the data directory

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$REPO_DIR/netcdf4_generated/data"

for nc in $(find "$DATA_DIR" -name "*.nc" -type f); do
	md="${nc%.nc}_info.md"
	echo '```' >"$md"
	h5dump -H -p "$nc" >>"$md"
	echo '```' >>"$md"
	echo "Generated: $(basename "$md")"
done
