#!/bin/bash
# Generate rio cogeo info markdown files for all TIFFs in the repo

REPO_DIR="$(dirname "$0")/.."

for tif in $(find "$REPO_DIR" -name "*.tif" -type f); do
	md="${tif%.tif}_info.md"
	echo '```' >"$md"
	rio cogeo info "$tif" >>"$md"
	echo '```' >>"$md"
	echo "✓ Generated: $(basename "$md")"
done
