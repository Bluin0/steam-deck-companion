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

chmod +x "dist/linux/SteamDeckCompanionServer"

# Create double-clickable launcher scripts with visible terminal window
cat << 'EOF' > "dist/linux/iniciar_servidor.sh"
#!/usr/bin/env bash
cd "$(dirname "$0")"

# Open terminal if running from GUI file manager
if [ ! -t 0 ]; then
    if command -v konsole >/dev/null 2>&1; then
        exec konsole -e "$0" "$@"
    elif command -v gnome-terminal >/dev/null 2>&1; then
        exec gnome-terminal -- "$0" "$@"
    elif command -v xterm >/dev/null 2>&1; then
        exec xterm -e "$0" "$@"
    fi
fi

echo "=========================================="
echo "      STEAM DECK COMPANION SERVER         "
echo "=========================================="
./SteamDeckCompanionServer
echo ""
echo "Presiona Enter para cerrar..."
read
EOF

chmod +x "dist/linux/iniciar_servidor.sh"

cat << EOF > "dist/linux/Iniciar_Servidor.desktop"
[Desktop Entry]
Type=Application
Name=Iniciar Servidor Steam Deck Companion
Exec=bash -c "cd '\$(dirname \"\$(readlink -f \"\$0\")\")' && ./iniciar_servidor.sh"
Icon=utilities-terminal
Terminal=true
Categories=Utility;Game;
EOF

chmod +x "dist/linux/Iniciar_Servidor.desktop"

echo ""
echo "======================================================="
echo "   ✅ ¡SERVIDOR LINUX COMPILADO CON ÉXITO!"
echo "   📂 Archivos listos en dist/linux/:"
echo "      - SteamDeckCompanionServer (Binario ejecutable)"
echo "      - iniciar_servidor.sh (Doble clic para abrir ventana)"
echo "======================================================="
