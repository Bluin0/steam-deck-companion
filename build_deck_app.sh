#!/usr/bin/env bash
set -e

echo "=========================================="
echo " 🎮 COMPILANDO APPIMAGE PARA STEAM DECK"
echo "=========================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR/deck-app"

echo "[1/2] Verificando dependencias npm..."
npm install

echo "[2/2] Compilando archivo .AppImage..."
npm run build:linux

echo ""
echo "=========================================="
echo " ✅ ¡COMPILACIÓN COMPLETADA!"
echo " 📂 Archivo listo para subir a GitHub Releases en:"
echo "    $(ls "$ROOT_DIR/deck-app/dist/"*.AppImage 2>/dev/null || echo "$ROOT_DIR/deck-app/dist/")"
echo "=========================================="
