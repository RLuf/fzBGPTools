#!/usr/bin/env bash
# build_deb.sh — script ORIGINAL do Antigravity (Gemini)
# ────────────────────────────────────────────────────────
# Salvo como referência. Funcional, gera fzbgptools-1.0.deb mínimo.
#
# Para o build oficial v0.2.0+ use:   bash build/linux/build-deb.sh
# (esse aqui está aqui para preservar o trabalho do Antigravity)

set -e
PROJECT_DIR="/home/rluft/.gemini/antigravity/scratch/fzBGPTools"
BUILD_DIR="/tmp/fzbgptools-deb-build"
OUTPUT_DEB="/home/rluft/Downloads/fzbgptools-1.0.deb"

echo "=== Building .deb Package ==="

# 1. Clean previous build dir
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/pixmaps"

# 2. Check if binary exists
if [ ! -f "$PROJECT_DIR/dist/fzbgptools" ]; then
    echo "ERROR: Executable '$PROJECT_DIR/dist/fzbgptools' not found. Run PyInstaller first!"
    exit 1
fi

# 3. Copy binary and set execution permissions
echo "Copying executable..."
cp "$PROJECT_DIR/dist/fzbgptools" "$BUILD_DIR/usr/bin/fzbgptools"
chmod 755 "$BUILD_DIR/usr/bin/fzbgptools"

# 4. Copy resource files (extracting them if necessary, or using the sources)
echo "Setting up desktop entry and icons..."
if [ -f "/tmp/deb-extract/usr/share/applications/fzbgptools.desktop" ]; then
    cp "/tmp/deb-extract/usr/share/applications/fzbgptools.desktop" "$BUILD_DIR/usr/share/applications/fzbgptools.desktop"
else
    # Create desktop file inline
    cat << 'EOF' > "$BUILD_DIR/usr/share/applications/fzbgptools.desktop"
[Desktop Entry]
Name=fzBGPTools
Comment=BGP Network Peering Mapper
Exec=/usr/bin/fzbgptools
Icon=fzbgptools
Terminal=false
Type=Application
Categories=Network;System;
EOF
fi

if [ -f "/tmp/deb-extract/usr/share/pixmaps/fzbgptools.png" ]; then
    cp "/tmp/deb-extract/usr/share/pixmaps/fzbgptools.png" "$BUILD_DIR/usr/share/pixmaps/fzbgptools.png"
elif [ -f "$PROJECT_DIR/src/resources/icon.png" ]; then
    cp "$PROJECT_DIR/src/resources/icon.png" "$BUILD_DIR/usr/share/pixmaps/fzbgptools.png"
fi

# 5. Create control file
echo "Creating control file..."
cat << 'EOF' > "$BUILD_DIR/DEBIAN/control"
Package: fzbgptools
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Roger Luft <rluft@home.rogerluft.com.br>
Description: fzBGPTools BGP Peering Mapper and Network Diagnostics.
 An integrated desktop network suite including a real-time BGP topological peering visualizer, ping, traceroute, and built-in interactive SSH and Telnet terminal client interfaces.
EOF

# 6. Build package
echo "Packaging using dpkg-deb..."
dpkg-deb --build "$BUILD_DIR" "$OUTPUT_DEB"
echo "=== Done! .deb package generated at $OUTPUT_DEB ==="
