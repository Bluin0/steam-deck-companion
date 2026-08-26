#!/usr/bin/env bash

# Si se abre haciendo doble clic desde el explorador de archivos, abrir ventana de terminal visible
if [ ! -t 0 ]; then
    if command -v konsole >/dev/null 2>&1; then
        exec konsole -e "$0" "$@"
    elif command -v gnome-terminal >/dev/null 2>&1; then
        exec gnome-terminal -- "$0" "$@"
    elif command -v xfce4-terminal >/dev/null 2>&1; then
        exec xfce4-terminal -e "$0" "$@"
    elif command -v xterm >/dev/null 2>&1; then
        exec xterm -e "$0" "$@"
    fi
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

clear 2>/dev/null || true
echo "======================================================="
echo "      🎮 STEAM DECK COMPANION — SERVIDOR LINUX         "
echo "======================================================="
echo ""

# Detectar IP local
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ip -4 addr show scope global 2>/dev/null | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n 1)
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
fi

echo "📌 TU IP LOCAL PARA LA STEAM DECK ES:  $LOCAL_IP"
echo "-------------------------------------------------------"

# Determinar intérprete de Python con dependencias
PYTHON_EXE="python3"

# Comprobar si websockets y psutil están instalados
if ! python3 -c "import websockets, psutil" 2>/dev/null; then
    echo "[+] Instalando dependencias necesarias (websockets, psutil)..."
    
    python3 -m pip install --quiet -r requirements.txt 2>/dev/null || \
    pip install --quiet -r requirements.txt 2>/dev/null || \
    pip install --break-system-packages --quiet -r requirements.txt 2>/dev/null || true
    
    # Si sigue sin estar instalado (ej. entorno gestionado de Debian/Ubuntu/SteamOS), usar un venv local
    if ! python3 -c "import websockets, psutil" 2>/dev/null; then
        if [ ! -d ".venv" ]; then
            echo "[+] Configurando entorno virtual local (.venv)..."
            python3 -m venv .venv 2>/dev/null || true
        fi
        if [ -f ".venv/bin/pip" ]; then
            .venv/bin/pip install --quiet -r requirements.txt 2>/dev/null || true
            PYTHON_EXE=".venv/bin/python3"
        fi
    fi
fi

echo "[+] Arrancando servidor..."
echo ""

"$PYTHON_EXE" src/server/main.py

EXIT_CODE=$?
echo ""
echo "-------------------------------------------------------"
if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️ El servidor se cerró con código de error: $EXIT_CODE"
else
    echo "ℹ️ Servidor detenido correctamente."
fi
echo ""
echo "Presiona Enter para cerrar esta ventana..."
read -r
