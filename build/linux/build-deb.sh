#!/usr/bin/env bash
# build/linux/build-deb.sh — empacota dist/fzbgptools em um .deb instalável.
# Uso:  bash build/linux/build-deb.sh [VERSION]
#
# Pré-requisitos:
#   - dist/fzbgptools deve existir (rode `make bin` antes)
#   - dpkg-deb instalado (`sudo apt install dpkg`)
set -euo pipefail

VERSION="${1:-0.2.0}"
ARCH="$(dpkg --print-architecture 2>/dev/null || echo amd64)"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PKG_NAME="fzbgptools"
PKG="${PKG_NAME}_${VERSION}_${ARCH}"
WORK="${ROOT}/build/work/${PKG}"

echo "▶ Empacotando ${PKG}.deb"

# ─── 1. Verificar binário ───
if [ ! -f "${ROOT}/dist/fzbgptools" ]; then
    echo "✗ dist/fzbgptools não encontrado. Rode 'make bin' primeiro."
    exit 1
fi

# ─── 2. Limpar e criar estrutura ───
rm -rf "${WORK}"
mkdir -p "${WORK}/DEBIAN"
mkdir -p "${WORK}/usr/bin"
mkdir -p "${WORK}/usr/lib/${PKG_NAME}"
mkdir -p "${WORK}/usr/share/applications"
mkdir -p "${WORK}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${WORK}/usr/share/doc/${PKG_NAME}"

# ─── 3. Copiar binário + recursos ───
cp "${ROOT}/dist/fzbgptools" "${WORK}/usr/lib/${PKG_NAME}/fzbgptools"
chmod 755 "${WORK}/usr/lib/${PKG_NAME}/fzbgptools"

# Wrapper em /usr/bin
cat > "${WORK}/usr/bin/fzbgptools" <<'EOF'
#!/bin/sh
exec /usr/lib/fzbgptools/fzbgptools "$@"
EOF
chmod 755 "${WORK}/usr/bin/fzbgptools"

# Ícone
cp "${ROOT}/src/resources/icon.png" "${WORK}/usr/share/icons/hicolor/256x256/apps/fzbgptools.png"

# .desktop
cp "${ROOT}/build/linux/fzbgptools.desktop" "${WORK}/usr/share/applications/fzbgptools.desktop"

# Documentação
cp "${ROOT}/README.md"    "${WORK}/usr/share/doc/${PKG_NAME}/README.md" 2>/dev/null || true
cp "${ROOT}/CHANGELOG.md" "${WORK}/usr/share/doc/${PKG_NAME}/changelog.md" 2>/dev/null || true
cp "${ROOT}/LICENSE"      "${WORK}/usr/share/doc/${PKG_NAME}/copyright" 2>/dev/null || true

# ─── 4. Control file ───
INSTALLED_SIZE="$(du -sk "${WORK}/usr" | cut -f1)"
cat > "${WORK}/DEBIAN/control" <<EOF
Package: ${PKG_NAME}
Version: ${VERSION}
Section: net
Priority: optional
Architecture: ${ARCH}
Depends: libc6, libqt5core5a, libqt5gui5, libqt5widgets5, iputils-ping, traceroute
Recommends: openssh-client, telnet
Installed-Size: ${INSTALLED_SIZE}
Maintainer: Roger Luft <rluft@example.com>
Homepage: https://github.com/rluft/fzBGPTools
Description: fzBGPTools — Network Peering Mapper
 Ferramenta desktop em PyQt5 para visualização de sessões BGP,
 descoberta automática de hosts em ranges CIDR, diagnóstico de
 rede (ping, traceroute) e acesso remoto SSH/Telnet.
 .
 Inclui cadastro de ASNs com múltiplos prefixos, gerenciamento
 de hosts e console de logs.
EOF

# ─── 5. postinst — update icon cache, menu ───
cat > "${WORK}/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
if [ -x /usr/bin/update-desktop-database ]; then
    update-desktop-database -q || true
fi
exit 0
EOF
chmod 755 "${WORK}/DEBIAN/postinst"

# ─── 6. postrm — limpar ───
cat > "${WORK}/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
if [ "$1" = "purge" ]; then
    rm -rf /usr/lib/fzbgptools 2>/dev/null || true
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "${WORK}/DEBIAN/postrm"

# ─── 7. Build .deb ───
mkdir -p "${ROOT}/dist"
OUT="${ROOT}/dist/${PKG}.deb"
dpkg-deb --build --root-owner-group "${WORK}" "${OUT}"

echo ""
echo "✓ Pacote gerado: ${OUT}"
echo ""
echo "  Instalar:    sudo apt install ${OUT}"
echo "  Desinstalar: sudo apt remove ${PKG_NAME}"
echo ""
