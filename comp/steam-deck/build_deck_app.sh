#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   🎮 COMPILADOR: APP STEAM DECK (AppImage para SteamOS)"
echo "======================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DECK_DIR="$ROOT_DIR/deck-app"

cd "$DECK_DIR"

# ── 1. Verificar o descargar Node.js / npm portable para SteamOS ──
if ! command -v npm &> /dev/null || ! command -v node &> /dev/null; then
    echo "[+] Node.js / npm no detectado en el sistema."
    echo "[+] Descargando Node.js portable para SteamOS (sin necesidad de sudo)..."
    
    NODE_VERSION="v20.11.1"
    NODE_TAR="node-${NODE_VERSION}-linux-x64.tar.xz"
    NODE_URL="https://nodejs.org/dist/${NODE_VERSION}/${NODE_TAR}"
    NODE_DIR="$ROOT_DIR/.node_portable"
    
    if [ ! -f "$NODE_DIR/bin/node" ]; then
        mkdir -p "$NODE_DIR"
        echo "   Descargando e instalando Node.js $NODE_VERSION..."
        curl -sSL "$NODE_URL" | tar -xJ -C "$NODE_DIR" --strip-components=1
    fi
    
    export PATH="$NODE_DIR/bin:$PATH"
    echo "   ✅ Node.js listo: $(node -v) / npm: $(npm -v)"
    echo ""
fi

# ── 2. Instalar dependencias de la app ──
echo "[1/2] Instalando dependencias de Node.js..."
npm install --silent

# ── 3. Compilar AppImage ──
echo "[2/2] Compilando .AppImage para SteamOS..."
# Limpiar compilaciones anteriores para evitar errores de cache/rename en electron-builder
rm -rf "$DECK_DIR/dist"
npx electron-builder --linux AppImage

mkdir -p "$ROOT_DIR/dist/steam-deck"
cp -f "$DECK_DIR/dist/"*.AppImage "$ROOT_DIR/dist/steam-deck/" 2>/dev/null || true
chmod +x "$ROOT_DIR/dist/steam-deck/"*.AppImage 2>/dev/null || true


echo ""
echo "======================================================="
echo "   ✅ ¡APP DE STEAM DECK COMPILADA CON ÉXITO!"
echo "   📂 Archivo listo para Releases en:"
echo "      $(ls -1 "$ROOT_DIR/dist/steam-deck/"*.AppImage 2>/dev/null || echo "$ROOT_DIR/dist/steam-deck/")"
echo "======================================================="
