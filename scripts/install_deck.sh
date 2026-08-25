#!/usr/bin/env bash
# ==============================================================================
# Steam Deck Companion — 1-Click SteamOS Installer
# ==============================================================================

set -e

echo "🎮 Instalando Steam Deck Companion en SteamOS..."

APP_DIR="$HOME/.local/share/steam-deck-companion"
LAUNCHER="$APP_DIR/launch.sh"
DESKTOP_ENTRY="$HOME/.local/share/applications/steam-deck-companion.desktop"

mkdir -p "$APP_DIR/profile"

# Ask for PC IP or use default
read -p "Introduce la IP de tu PC de juegos (ej. 192.168.1.100): " PC_IP
if [ -z "$PC_IP" ]; then
    echo "⚠️ No se introdujo IP, usando localhost:8080 por defecto."
    PC_IP="127.0.0.1"
fi

# Create launch script
cat << 'EOF' > "$LAUNCHER"
#!/usr/bin/env bash
PC_IP_FILE="$HOME/.local/share/steam-deck-companion/pc_ip.txt"
if [ -f "$PC_IP_FILE" ]; then
    PC_IP=$(cat "$PC_IP_FILE")
else
    PC_IP="192.168.1.100"
fi

# Launch Flatpak Chrome with web security disabled so all websites render in iframes
flatpak run com.google.Chrome \
    --disable-web-security \
    --user-data-dir="$HOME/.local/share/steam-deck-companion/profile" \
    --kiosk \
    --start-fullscreen \
    --autoplay-policy=no-user-gesture-required \
    --disable-pinch \
    --app="http://${PC_IP}:8080"
EOF

chmod +x "$LAUNCHER"
echo "$PC_IP" > "$APP_DIR/pc_ip.txt"

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

echo "✅ ¡Instalación completada con éxito!"
echo ""
echo "📌 Para añadirlo a tu biblioteca de Steam en Gaming Mode:"
echo "1. Abre Steam en Modo Escritorio."
echo "2. Haz clic en 'Añadir un juego' (abajo a la izquierda) ➔ 'Añadir un producto que no es de Steam...'."
echo "3. Selecciona 'Steam Deck Companion' de la lista y pulsa 'Añadir seleccionados'."
echo "4. ¡Vuelve a Gaming Mode y dale a Jugar!"
