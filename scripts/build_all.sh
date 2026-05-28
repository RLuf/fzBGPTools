#!/bin/bash
# Unified build script for fzBGPTools

set -e

PROJECT_DIR="/home/rluft/.gemini/antigravity/scratch/fzBGPTools"
cd "$PROJECT_DIR"

echo "=== Cleaning previous builds ==="
sudo rm -rf build dist

echo "=== Compiling native Linux binary ==="
python3 -m PyInstaller --clean -y fzbgptools.spec

echo "=== Packaging as .deb ==="
./build_deb.sh

echo "=== Build completed successfully ==="
