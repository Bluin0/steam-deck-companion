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

PYINSTALLER_BIN=""
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER_BIN="pyinstaller"
elif python3 -m PyInstaller --version &> /dev/null 2>&1; then
    PYINSTALLER_BIN="python3 -m PyInstaller"
else
    echo "[+] Configurando entorno temporal para compilar..."
    if ! python3 -m pip install -r requirements.txt pyinstaller 2>/dev/null; then
        python3 -m venv .build_venv 2>/dev/null || true
        if [ -f ".build_venv/bin/pip" ]; then
            .build_venv/bin/pip install -r requirements.txt pyinstaller
            PYINSTALLER_BIN=".build_venv/bin/pyinstaller"
        else
            echo "⚠️ Se requiere PyInstaller. Por favor instala pyinstaller con: sudo apt install python3-pip && pip install pyinstaller"
            exit 1
        fi
    else
        PYINSTALLER_BIN="python3 -m PyInstaller"
    fi
fi

echo "[2/3] Compilando binario autónomo para Linux..."
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
rm -rf "build" ".build_venv"

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
