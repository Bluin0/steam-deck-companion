#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   COMPILADOR: SERVIDOR PC LINUX (.AppImage con GUI)"
echo "======================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$ROOT_DIR"

# ── 1. Setup Python environment ──
echo "[1/5] Verificando dependencias Python y PyInstaller..."

PYINSTALLER_BIN=""
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER_BIN="pyinstaller"
elif python3 -m PyInstaller --version &> /dev/null 2>&1; then
    PYINSTALLER_BIN="python3 -m PyInstaller"
else
    echo "[+] Configurando entorno virtual para compilar..."
    if [ ! -d ".build_venv" ]; then
        python3 -m venv .build_venv
    fi
    .build_venv/bin/pip install --quiet -r requirements.txt pyinstaller
    PYINSTALLER_BIN=".build_venv/bin/pyinstaller"
fi

# ── 2. Compile binary with PyInstaller ──
echo "[2/5] Compilando binario autónomo para Linux..."
mkdir -p "dist/linux"

$PYINSTALLER_BIN \
    --name "SteamDeckCompanionServer" \
    --onefile \
    --clean \
    --noconfirm \
    --add-data "$ROOT_DIR/profiles:profiles" \
    --add-data "$ROOT_DIR/src/client:src/client" \
    --distpath "dist/linux" \
    "src/server/main.py"

rm -f "SteamDeckCompanionServer.spec"
rm -rf "build"

if [ ! -f "dist/linux/SteamDeckCompanionServer" ]; then
    echo "ERROR: No se pudo generar el binario de Linux."
    exit 1
fi

chmod +x "dist/linux/SteamDeckCompanionServer"
echo "   Binario ELF generado correctamente."

# ── 3. Create AppImage structure ──
echo "[3/5] Preparando estructura del AppImage..."
APPDIR="dist/linux/SteamDeckCompanionServer.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp "dist/linux/SteamDeckCompanionServer" "$APPDIR/usr/bin/SteamDeckCompanionServer"

# Desktop entry
cat > "$APPDIR/SteamDeckCompanionServer.desktop" << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=Steam Deck Companion Server
Exec=SteamDeckCompanionServer
Icon=steamdeckcompanionserver
Categories=Game;Utility;
Terminal=false
DESKTOP

# AppRun script
cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/SteamDeckCompanionServer" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

# Generate a simple SVG icon
cat > "$APPDIR/steamdeckcompanionserver.svg" << 'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="40" fill="#0a0d14"/>
  <text x="128" y="160" text-anchor="middle" font-size="120" fill="#00d4aa">🎮</text>
</svg>
SVG
cp "$APPDIR/steamdeckcompanionserver.svg" "$APPDIR/usr/share/icons/hicolor/256x256/apps/steamdeckcompanionserver.svg"

# Symlinks required by AppImage spec
ln -sf "SteamDeckCompanionServer.desktop" "$APPDIR/default.desktop" 2>/dev/null || true
ln -sf "steamdeckcompanionserver.svg" "$APPDIR/.DirIcon" 2>/dev/null || true

# ── 4. Download appimagetool if needed ──
echo "[4/5] Obteniendo appimagetool..."
APPIMAGETOOL="$ROOT_DIR/dist/linux/appimagetool"

if [ ! -f "$APPIMAGETOOL" ]; then
    ARCH=$(uname -m)
    TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    echo "   Descargando appimagetool para $ARCH..."
    curl -sSL -o "$APPIMAGETOOL" "$TOOL_URL" || wget -q -O "$APPIMAGETOOL" "$TOOL_URL"
    chmod +x "$APPIMAGETOOL"
fi

# ── 5. Build AppImage ──
echo "[5/5] Generando archivo .AppImage..."
export ARCH=$(uname -m)
"$APPIMAGETOOL" --appimage-extract-and-run "$APPDIR" "dist/linux/SteamDeckCompanionServer-${ARCH}.AppImage" 2>/dev/null || \
"$APPIMAGETOOL" "$APPDIR" "dist/linux/SteamDeckCompanionServer-${ARCH}.AppImage"

# Cleanup
rm -rf "$APPDIR" ".build_venv" "$APPIMAGETOOL"

FINAL_FILE="dist/linux/SteamDeckCompanionServer-${ARCH}.AppImage"

if [ ! -f "$FINAL_FILE" ]; then
    echo ""
    echo "NOTA: appimagetool no pudo generar el AppImage."
    echo "El binario ejecutable sigue disponible en: dist/linux/SteamDeckCompanionServer"
    exit 0
fi

echo ""
echo "======================================================="
echo "   SERVIDOR LINUX COMPILADO CON EXITO!"
echo "   Archivo listo para Releases en:"
echo "      $FINAL_FILE"
echo "======================================================="
