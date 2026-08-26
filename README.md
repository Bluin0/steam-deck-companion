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

## 📦 Compilación y Ejecutables Autónomos (Sin Comandos)

### 1. Servidor PC (`.exe` para Windows / Binario para Linux)
Puedes compilar el servidor en un solo archivo ejecutable:
- **En Windows**: Haz doble clic en el archivo **`build_server.bat`**. Se creará automáticamente **`dist\SteamDeckCompanionServer.exe`**.
- **En Linux**: Ejecuta `./build_server.sh`.
- *(También puedes descargarlo ya compilado desde la pestaña **Releases** de GitHub).*

> **Para iniciarlo**: Simplemente haz doble clic en `SteamDeckCompanionServer.exe` en tu PC. ¡No requiere abrir terminales!

---

### 2. Cliente Steam Deck (`.AppImage` ejecutable para SteamOS)
- **Compilar en Linux/Deck**:
  ```bash
  cd deck-app
  npm install
  npm run build:linux
  ```
  Se creará el archivo **`deck-app/dist/Steam Deck Companion-linux-x64.AppImage`**.

- **Para añadirlo a Steam**:
  1. Copia el archivo `.AppImage` a tu Steam Deck (ej: a tu carpeta personal o `~/Applications`).
  2. En Steam (Modo Escritorio), pulsa **"Añadir un juego"** ➔ **"Añadir un producto que no es de Steam..."** ➔ Selecciona el `.AppImage`.
  3. ¡Vuelve a **Gaming Mode** y lánzalo como cualquier juego!

---

## ⚙️ Cambiar la IP del Servidor desde la Steam Deck

1. Dentro de la app, pulsa el botón **`⚙️ PC`** situado en la esquina superior derecha (o el aviso rojo que aparece si no detecta conexión).
2. Escribe la nueva IP local de tu PC de juegos (ej. `192.168.1.50`).
3. Elige tu tamaño de interfaz preferido (`100%`, `115%`, `125%` o `140%`).
4. Pulsa **"Guardar y Conectar"**. La app se reconecta al instante y guarda la configuración.
