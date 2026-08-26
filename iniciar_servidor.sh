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

# 1. Detectar IP local con múltiples métodos fiables
LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ip -4 addr show scope global 2>/dev/null | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n 1)
fi
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
fi

echo "📌 TU IP LOCAL PARA LA STEAM DECK ES:  $LOCAL_IP"
echo "-------------------------------------------------------"

# 2. Configurar entorno de dependencias (websockets, psutil)
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="python3"

if "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then
    echo "[+] Dependencias verificadas correctamente."
else
    echo "[+] Instalando dependencias de Python (websockets, psutil)..."
    
    # Intentar crear entorno virtual si no existe
    if [ ! -f "$VENV_DIR/bin/python3" ]; then
        python3 -m venv "$VENV_DIR" 2>/dev/null || python3 -m ensurepip --user 2>/dev/null || true
    fi
    
    # Si tenemos entorno virtual, instalar en él
    if [ -f "$VENV_DIR/bin/python3" ]; then
        "$VENV_DIR/bin/python3" -m pip install --quiet --upgrade pip 2>/dev/null || true
        "$VENV_DIR/bin/python3" -m pip install -r "$ROOT_DIR/requirements.txt"
        PYTHON_BIN="$VENV_DIR/bin/python3"
    else
        # Intentar con pip directo del usuario
        python3 -m pip install --user -r "$ROOT_DIR/requirements.txt" 2>/dev/null || \
        pip3 install --user -r "$ROOT_DIR/requirements.txt" 2>/dev/null || \
        pip3 install --break-system-packages -r "$ROOT_DIR/requirements.txt" 2>/dev/null || \
        pip install -r "$ROOT_DIR/requirements.txt" 2>/dev/null || true
        
        # Comprobar si ahora funciona
        if ! python3 -c "import websockets" 2>/dev/null; then
            echo ""
            echo "⚠️ No se pudo instalar 'websockets' automáticamente."
            echo "Por favor ejecuta en tu terminal:"
            echo "  sudo apt install python3-pip python3-websockets python3-psutil"
            echo "  (o 'sudo pacman -S python-pip python-websockets' en Arch/SteamOS)"
            echo ""
            echo "Presiona Enter para continuar de todas formas..."
            read -r
        fi
    fi
fi

echo "[+] Arrancando servidor..."
echo ""

"$PYTHON_BIN" src/server/main.py

EXIT_CODE=$?
echo ""
echo "-------------------------------------------------------"
if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️ El servidor se cerró con código de error: $EXIT_CODE"
else
    echo "ℹ️ Servidor detenido."
fi
echo ""
echo "Presiona Enter para cerrar..."
read -r
