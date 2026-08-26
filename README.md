# 🎮 Steam Deck Companion

Segunda pantalla interactiva y mando virtual de baja latencia para tu Steam Deck conectada a tu PC de juegos (Windows / Linux) por red local.

---

## ✨ Características

- 🎯 **Detección Automática de Juegos**: Detecta el juego que estás jugando en tu PC (Steam o catálogo global) y adapta toda la interfaz al instante.
- ⚙️ **Configuración de IP en la App**: Cambia la IP de tu PC de juegos directamente desde la pantalla táctil de la Steam Deck con 1 toque (sin terminales ni archivos de texto).
- 🔍 **Escalado y Zoom para Steam Deck (7" 1280x800)**: Tipografías, botones e iconos agrandados para máxima legibilidad y confort táctil en modo portátil, con selector de escala (100% a 140%).
- 🗺️ **Mapas Interactivos Directos**: Carga automáticamente el mapa interactivo (MapGenie, etc.) del juego activo con búsqueda inteligente de respaldo (cero errores 404).
- 📖 **Guías Comunitarias y Wikis**: Guías de Steam o wikis en español (Vandal/Eliteguias) con un solo toque.
- ⏱️ **HowLongToBeat**: Información de duración y estadísticas del juego sincronizadas.
- 📝 **Bloc de Notas Persistente**: Toma apuntes, códigos y recetas que se guardan directamente en tu PC.
- 🎮 **Mando Virtual y Diagnóstico**: Streaming de inputs a 0ms hacia un mando Xbox 360 virtual en tu PC (`ViGEmBus` en Windows o `uinput` en Linux) con pestaña de test y calibración en tiempo real.
- 🛡️ **App Nativa con Bloqueador de Anuncios**: Carga ultra-rápida sin publicidad ni errores en consola.

---

## 📦 Compilación Local para subir a GitHub Releases

### 1. Compilar Servidor PC (`.exe` para Windows / Binario para Linux)
- **En Windows**: Haz doble clic en el archivo **`build_server.bat`**. Creará **`dist\SteamDeckCompanionServer.exe`**.
- **En Linux**: Ejecuta `./build_server.sh`. Creará **`dist/SteamDeckCompanionServer`**.

> **Para el usuario final**: Solo hace doble clic en `SteamDeckCompanionServer.exe` para jugar (no necesita consola ni instalar Python).

---

### 2. Compilar App de Steam Deck (`.AppImage` para SteamOS)
- Ejecuta el script:
  ```bash
  ./build_deck_app.sh
  ```
  O entra en `deck-app/` y corre `npm run build:linux`.
- El archivo ejecutable **`.AppImage`** se creará en **`deck-app/dist/`**.

---

### 3. Subir a Releases en GitHub
1. En tu repositorio de GitHub, ve a la pestaña **Releases** ➔ **"Draft a new release"**.
2. Ponle una etiqueta de versión (ej. `v1.0.0`).
3. Arrastra y suelta los archivos que has compilado:
   - `SteamDeckCompanionServer.exe` (Servidor para Windows)
   - `SteamDeckCompanion.AppImage` (Cliente para Steam Deck)
4. Pulsa **"Publish release"**. ¡Cualquiera puede descargarlos y usarlos con 1 clic!

---

## ⚙️ Cambiar la IP del Servidor desde la Steam Deck

1. Dentro de la app, pulsa el botón **`⚙️ PC`** situado en la esquina superior derecha (o el aviso rojo que aparece si no detecta conexión).
2. Escribe la nueva IP local de tu PC de juegos (ej. `192.168.1.50`).
3. Elige tu tamaño de interfaz preferido (`100%`, `115%`, `125%` o `140%`).
4. Pulsa **"Guardar y Conectar"**. La app se reconecta al instante y guarda la configuración.
