#!/bin/bash
# CI script to verify generated artifacts are up to date

set -e

echo "Running generate..."
pixi run generate

echo "Running info..."
pixi run info

echo "Running catalog..."
pixi run catalog

echo "Checking for uncommitted changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Generated files are out of date. Please run 'pixi run generate', 'pixi run info', and 'pixi run catalog' and commit the changes."
    git status
    git diff
    exit 1
fi

echo "All generated files are up to date."
