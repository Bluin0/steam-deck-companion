#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   COMPILADOR: SERVIDOR PC LINUX (Script Universal .sh)"
echo "======================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

mkdir -p "$ROOT_DIR/dist/linux"
OUTPUT_SH="$ROOT_DIR/dist/linux/SteamDeckCompanionServer.sh"

echo "[1/2] Generando lanzador universal autónomo..."
cat << 'HEADER' > "$OUTPUT_SH"
#!/usr/bin/env bash
# =======================================================
#    STEAM DECK COMPANION SERVER — PORTABLE LINUX RUNNER
# =======================================================

set -e

APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/steam-deck-companion/server"
mkdir -p "$APP_DIR"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Se requiere Python 3 instalado en el sistema."
    exit 1
fi

SCRIPT_HASH=$(md5sum "$0" 2>/dev/null | cut -d' ' -f1 || cksum "$0" 2>/dev/null | cut -d' ' -f1 || echo "installed")
HASH_FILE="$APP_DIR/.version_hash"

if [ ! -f "$HASH_FILE" ] || [ "$SCRIPT_HASH" != "$(cat "$HASH_FILE" 2>/dev/null)" ]; then
    echo "[+] Preparando Steam Deck Companion Server en $APP_DIR..."
    PAYLOAD_LINE=$(awk '/^__PAYLOAD_BELOW__/ {print NR + 1; exit 0; }' "$0")
    tail -n +"$PAYLOAD_LINE" "$0" | tar -xz -C "$APP_DIR"
    echo "$SCRIPT_HASH" > "$HASH_FILE"
fi

cd "$APP_DIR"

# ── Setup Python dependencies if missing ──
VENV_DIR="$APP_DIR/.venv"
PYTHON_BIN="python3"

if ! "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then
    echo "[+] Verificando dependencias de Python (websockets, psutil)..."
    python3 -m pip install --user --quiet -r "$APP_DIR/requirements.txt" 2>/dev/null || \
    pip3 install --user --quiet -r "$APP_DIR/requirements.txt" 2>/dev/null || true

    if ! "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then
        if [ ! -d "$VENV_DIR" ]; then
            python3 -m venv "$VENV_DIR" 2>/dev/null || true
        fi
        if [ -f "$VENV_DIR/bin/pip" ]; then
            "$VENV_DIR/bin/pip" install --quiet -r "$APP_DIR/requirements.txt" 2>/dev/null || true
            PYTHON_BIN="$VENV_DIR/bin/python3"
        fi
    fi

    # Fallback portable installer (uv) if system lacks pip/venv
    if ! "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then
        echo "[+] Configurando entorno portable..."
        UV_DIR="$APP_DIR/.uv"
        mkdir -p "$UV_DIR"
        if [ ! -f "$UV_DIR/uv" ]; then
            ARCH=$(uname -m)
            curl -sSL "https://github.com/astral-sh/uv/releases/latest/download/uv-${ARCH}-unknown-linux-gnu.tar.gz" 2>/dev/null | tar -xz -C "$UV_DIR" --strip-components=1 2>/dev/null || true
        fi
        if [ -f "$UV_DIR/uv" ]; then
            "$UV_DIR/uv" venv "$APP_DIR/.venv" 2>/dev/null || true
            "$UV_DIR/uv" pip install --no-cache -r "$APP_DIR/requirements.txt" --python "$APP_DIR/.venv/bin/python3" 2>/dev/null || true
            if [ -f "$APP_DIR/.venv/bin/python3" ]; then
                PYTHON_BIN="$APP_DIR/.venv/bin/python3"
            fi
        fi
    fi
fi

# ── Launch Server ──
exec "$PYTHON_BIN" "$APP_DIR/src/server/main.py" "$@"

__PAYLOAD_BELOW__
HEADER

echo "[2/2] Empaquetando código, perfiles y cliente web en un solo archivo..."
tar -cz -C "$ROOT_DIR" src profiles requirements.txt >> "$OUTPUT_SH"
chmod +x "$OUTPUT_SH"

# Cleanup old build artifacts if any
rm -rf "$ROOT_DIR/dist/linux/"*.AppImage "$ROOT_DIR/dist/linux/SteamDeckCompanionServer" 2>/dev/null || true

echo ""
echo "======================================================="
echo "   ✅ SERVIDOR LINUX GENERADO CON ÉXITO!"
echo "   📂 Archivo listo para Releases en:"
echo "      dist/linux/SteamDeckCompanionServer.sh"
echo "======================================================="

