#!/usr/bin/env bash
# ==============================================================================
# Steam Deck Companion — Uninstaller for SteamOS
# ==============================================================================

set -e

echo "🧹 Desinstalando Steam Deck Companion de SteamOS..."

# 1. Kill any running instances
killall -9 chrome google-chrome chromium-browser zypak-sandbox 2>/dev/null || true

# 2. Remove application files & profiles
rm -rf "$HOME/.local/share/steam-deck-companion"
rm -rf "$HOME/.companion-browser-profile"
rm -rf "$HOME/.companion-chrome-profile"
rm -rf "$HOME/.companion-profile"
rm -rf "$HOME/.steamdeck-companion-profile"

# 3. Remove desktop shortcut
rm -f "$HOME/.local/share/applications/steam-deck-companion.desktop"

echo ""
echo "✅ ¡Todos los archivos y accesos directos de Steam Deck Companion han sido eliminados!"
echo ""
echo "📌 Si lo tenías añadido en tu biblioteca de Steam:"
echo "1. En Steam, haz clic derecho (o botón ☰) sobre 'Steam Deck Companion'."
echo "2. Selecciona 'Administrar' ➔ 'Eliminar juego que no es de Steam de la biblioteca'."
