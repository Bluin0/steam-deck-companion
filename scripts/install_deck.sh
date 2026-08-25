#!/usr/bin/env bash
# ==============================================================================
# Steam Deck Companion — 1-Click SteamOS Installer (Solución 2: Isolated Engine)
# ==============================================================================

set -e

echo "🎮 Instalando Steam Deck Companion (Motor Aislado) en SteamOS..."

APP_DIR="$HOME/.local/share/steam-deck-companion"
LAUNCHER="$APP_DIR/launch.sh"
DESKTOP_ENTRY="$HOME/.local/share/applications/steam-deck-companion.desktop"

mkdir -p "$APP_DIR/profile"

# Get IP from argument or tty or zenity
PC_IP="$1"

if [ -z "$PC_IP" ] && [ -t 0 ]; then
    read -p "Introduce la IP de tu PC de juegos (ej. 192.168.1.100): " PC_IP || true
elif [ -z "$PC_IP" ] && [ -e /dev/tty ]; then
    read -p "Introduce la IP de tu PC de juegos (ej. 192.168.1.100): " PC_IP < /dev/tty || true
fi

if [ -z "$PC_IP" ] && command -v zenity >/dev/null 2>&1; then
    PC_IP=$(zenity --entry --title="Steam Deck Companion" --text="Introduce la IP local de tu PC de juegos (ej. 192.168.1.100):" 2>/dev/null || echo "")
fi

if [ -z "$PC_IP" ]; then
    PC_IP="192.168.1.100"
    echo "⚠️ Usando IP por defecto: $PC_IP (puedes cambiarla en $APP_DIR/pc_ip.txt)"
else
    echo "✅ IP configurada: $PC_IP"
fi

# Save IP
echo "$PC_IP" > "$APP_DIR/pc_ip.txt"

# Write launch script with process isolation and full security bypass flags
cat << 'EOF' > "$LAUNCHER"
#!/usr/bin/env bash

# 1. Kill any existing Chrome/Chromium sessions so they don't block security flags
killall -9 chrome google-chrome chromium-browser zypak-sandbox 2>/dev/null || true
sleep 0.5

PC_IP_FILE="$HOME/.local/share/steam-deck-companion/pc_ip.txt"
if [ -f "$PC_IP_FILE" ]; then
    PC_IP=$(cat "$PC_IP_FILE" | tr -d '[:space:]')
else
    PC_IP="192.168.1.100"
fi

PROFILE_DIR="$HOME/.local/share/steam-deck-companion/profile"
mkdir -p "$PROFILE_DIR"

# Launch Flatpak Chrome with all frame and origin security checks disabled
flatpak run com.google.Chrome \
    --disable-web-security \
    --user-data-dir="$PROFILE_DIR" \
    --disable-site-isolation-trials \
    --disable-features=IsolateOrigins,site-per-process,BlockInsecurePrivateNetworkRequests \
    --allow-running-insecure-content \
    --ignore-certificate-errors \
    --autoplay-policy=no-user-gesture-required \
    --disable-pinch \
    --kiosk \
    --start-fullscreen \
    --app="http://${PC_IP}:8080"
EOF

chmod +x "$LAUNCHER"

# Create Desktop entry for Steam
cat << EOF > "$DESKTOP_ENTRY"
[Desktop Entry]
Name=Steam Deck Companion
Comment=Segunda pantalla contextual y companion para videojuegos de PC
Exec=$LAUNCHER
Icon=steamdeck-gaming-return
Terminal=false
Type=Application
Categories=Game;
EOF

chmod +x "$DESKTOP_ENTRY"

echo ""
echo "✅ ¡Instalación completada con éxito!"
echo "📌 Tu app se ha configurado para conectar a: http://${PC_IP}:8080"
echo ""
echo "Pasos para añadir a Steam:"
echo "1. Abre Steam en Modo Escritorio."
echo "2. Haz clic en 'Añadir un juego' (abajo a la izquierda) ➔ 'Añadir un producto que no es de Steam...'."
echo "3. Selecciona 'Steam Deck Companion' de la lista y pulsa 'Añadir seleccionados'."
echo "4. ¡Vuelve a Gaming Mode y dale a Jugar!"
