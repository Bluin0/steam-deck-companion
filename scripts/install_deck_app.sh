#!/usr/bin/env bash
# ==============================================================================
# Steam Deck Companion — Native App Installer for SteamOS (Electron WebView)
# ==============================================================================

set -e

echo "🎮 Instalando Steam Deck Companion (App Nativa con WebView) en SteamOS..."

APP_BASE="$HOME/.local/share/steam-deck-companion"
APP_DIR="$APP_BASE/app"
LAUNCHER="$APP_BASE/launch.sh"
DESKTOP_ENTRY="$HOME/.local/share/applications/steam-deck-companion.desktop"

mkdir -p "$APP_DIR"

# 1. Get PC IP
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
    echo "⚠️ Usando IP por defecto: $PC_IP"
else
    echo "✅ IP configurada: $PC_IP"
fi

echo "$PC_IP" > "$APP_BASE/pc_ip.txt"

# 2. Download latest deck-app files from GitHub
echo "📦 Descargando archivos de la aplicación nativa..."
curl -sSL -o "$APP_DIR/package.json" https://raw.githubusercontent.com/Bluin0/steam-deck-companion/main/deck-app/package.json
curl -sSL -o "$APP_DIR/main.js" https://raw.githubusercontent.com/Bluin0/steam-deck-companion/main/deck-app/main.js
curl -sSL -o "$APP_DIR/preload.js" https://raw.githubusercontent.com/Bluin0/steam-deck-companion/main/deck-app/preload.js
curl -sSL -o "$APP_DIR/index.html" https://raw.githubusercontent.com/Bluin0/steam-deck-companion/main/deck-app/index.html
curl -sSL -o "$APP_DIR/style.css" https://raw.githubusercontent.com/Bluin0/steam-deck-companion/main/deck-app/style.css
curl -sSL -o "$APP_DIR/app.js" https://raw.githubusercontent.com/Bluin0/steam-deck-companion/main/deck-app/app.js

# 3. Setup Electron runtime
ELECTRON_BIN=""

if command -v electron >/dev/null 2>&1; then
    ELECTRON_BIN=$(command -v electron)
elif command -v npx >/dev/null 2>&1; then
    echo "⚡ Instalando dependencias de Electron..."
    (cd "$APP_DIR" && npm install --silent electron)
    ELECTRON_BIN="$APP_DIR/node_modules/.bin/electron"
else
    echo "⬇️ Descargando binario oficial de Electron para SteamOS..."
    ELECTRON_ZIP="$APP_BASE/electron.zip"
    curl -sSL -o "$ELECTRON_ZIP" "https://github.com/electron/electron/releases/download/v28.2.0/electron-v28.2.0-linux-x64.zip"
    mkdir -p "$APP_BASE/electron-bin"
    unzip -q -o "$ELECTRON_ZIP" -d "$APP_BASE/electron-bin"
    rm -f "$ELECTRON_ZIP"
    ELECTRON_BIN="$APP_BASE/electron-bin/electron"
fi

# 4. Create Launcher script
cat << EOF > "$LAUNCHER"
#!/usr/bin/env bash
PC_IP_FILE="\$HOME/.local/share/steam-deck-companion/pc_ip.txt"
if [ -f "\$PC_IP_FILE" ]; then
    TARGET_IP=\$(cat "\$PC_IP_FILE" | tr -d '[:space:]')
else
    TARGET_IP="192.168.1.100"
fi

"$ELECTRON_BIN" "$APP_DIR" --pc-ip="\$TARGET_IP" --no-sandbox
EOF

chmod +x "$LAUNCHER"

# 5. Create Desktop Entry
cat << EOF > "$DESKTOP_ENTRY"
[Desktop Entry]
Name=Steam Deck Companion
Comment=Segunda pantalla contextual y companion para videojuegos de PC (Nativo)
Exec=$LAUNCHER
Icon=steamdeck-gaming-return
Terminal=false
Type=Application
Categories=Game;
EOF

chmod +x "$DESKTOP_ENTRY"

echo ""
echo "✅ ¡Instalación de la App Nativa completada con éxito!"
echo "📌 Configurado para conectar a tu PC en: http://${PC_IP}:8080"
echo ""
echo "Pasos para añadir a Steam:"
echo "1. Abre Steam en Modo Escritorio."
echo "2. Haz clic en 'Añadir un juego' (abajo a la izquierda) ➔ 'Añadir un producto que no es de Steam...'."
echo "3. Selecciona 'Steam Deck Companion' de la lista y pulsa 'Añadir seleccionados'."
echo "4. ¡Vuelve a Gaming Mode y dale a Jugar!"
