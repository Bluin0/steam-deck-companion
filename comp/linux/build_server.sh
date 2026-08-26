#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   🐧 COMPILADOR: SERVIDOR PC LINUX (Binario ELF)"
echo "======================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$ROOT_DIR"

echo "[1/3] Verificando dependencias Python y PyInstaller..."
python3 -m pip install --quiet -r requirements.txt pyinstaller 2>/dev/null || pip install -r requirements.txt pyinstaller || true

echo "[2/3] Compilando binario autónomo para Linux..."
mkdir -p "dist/linux"

pyinstaller \
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
    echo "❌ ERROR: No se pudo generar el binario de Linux."
    exit 1
fi

echo ""
echo "======================================================="
echo "   ✅ ¡SERVIDOR LINUX COMPILADO CON ÉXITO!"
echo "   📂 Archivo listo para Releases en:"
echo "      dist/linux/SteamDeckCompanionServer"
echo "======================================================="
