#!/usr/bin/env bash
set -e

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
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || ip -4 addr show scope global | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n 1 || echo "127.0.0.1")

echo "📌 TU IP LOCAL PARA LA STEAM DECK ES:  $LOCAL_IP"
echo "-------------------------------------------------------"

echo "[1/2] Verificando dependencias..."
python3 -m pip install --quiet -r requirements.txt 2>/dev/null || pip install --quiet -r requirements.txt 2>/dev/null || true

echo "[2/2] Iniciando servidor en segundo plano..."
echo ""

python3 src/server/main.py

echo ""
echo "Servidor detenido. Presiona Enter para cerrar..."
read
