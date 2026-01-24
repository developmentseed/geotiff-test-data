#!/bin/bash
# Upload generated NetCDF4 files to S3

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <bucket>[/prefix]"
    echo "Example: $0 my-bucket/netcdf4-test-data"
    exit 1
fi

BUCKET="$1"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$REPO_DIR/netcdf4_generated/data"
CONFIG_FILE="$REPO_DIR/.s3-bucket"

echo "Uploading to s3://$BUCKET/"
echo

for nc in "$DATA_DIR"/*.nc; do
    filename=$(basename "$nc")
    echo "Uploading: $filename"
    aws s3 cp "$nc" "s3://$BUCKET/$filename"
done

# Save bucket config for catalog generation
echo "$BUCKET" > "$CONFIG_FILE"
echo
echo "Saved bucket config to $CONFIG_FILE"
echo "Run 'pixi run catalog' to update CATALOG.md with S3 URLs"
