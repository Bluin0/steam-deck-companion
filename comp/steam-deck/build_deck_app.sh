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

echo "[1/3] Instalando dependencias de Node.js..."
npm install

echo "[2/3] Compilando .AppImage para SteamOS..."
npm run build:appimage || npm run build

mkdir -p "$ROOT_DIR/dist/steam-deck"
cp -f "$DECK_DIR/dist/"*.AppImage "$ROOT_DIR/dist/steam-deck/" 2>/dev/null || cp -f "$DECK_DIR/dist/"* "$ROOT_DIR/dist/steam-deck/" 2>/dev/null || true

echo ""
echo "======================================================="
echo "   ✅ ¡APP DE STEAM DECK COMPILADA CON ÉXITO!"
echo "   📂 Archivo listo para Releases en:"
echo "      dist/steam-deck/"
echo "======================================================="
