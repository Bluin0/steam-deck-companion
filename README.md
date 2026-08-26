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

## 📦 Compiladores por Sistema (`comp/`)

Todos los scripts de compilación están organizados en la carpeta **`comp/`**:

```
comp/
├── windows/       ➔ Compilador para Servidor PC Windows (.exe)
├── linux/         ➔ Compilador para Servidor PC Linux (Binario ELF)
└── steam-deck/    ➔ Compilador para App Steam Deck (AppImage / Zip)
```

### 1. 🖥️ Compilar Servidor PC Windows
- Ve a la carpeta `comp/windows/` y haz doble clic en **`build_server.bat`**.
- Genera el ejecutable en: **`dist/windows/SteamDeckCompanionServer.exe`**.

### 2. 🐧 Compilar Servidor PC Linux
- Ve a la carpeta `comp/linux/` y ejecuta **`./build_server.sh`**.
- Genera el binario ELF en: **`dist/linux/SteamDeckCompanionServer`**.

### 3. 🎮 Compilar App para Steam Deck
- **Desde Linux/Deck**: Ve a `comp/steam-deck/` y ejecuta **`./build_deck_app.sh`**.
- **Desde Windows**: Ve a `comp/steam-deck/` y haz doble clic en **`build_deck_app.bat`**.
- Genera el archivo en: **`dist/steam-deck/`**.

---

### 📤 Subir a GitHub Releases
1. Ve a la pestaña **Releases** de tu GitHub ➔ **"Draft a new release"**.
2. Pon la etiqueta (ej: `v1.0.0`).
3. Arrastra los archivos generados desde la carpeta `dist/`.
4. Pulsa **"Publish release"**.

---

## ⚙️ Cambiar la IP del Servidor desde la Steam Deck

1. Dentro de la app, pulsa el botón **`⚙️ PC`** situado en la esquina superior derecha (o el aviso rojo que aparece si no detecta conexión).
2. Escribe la nueva IP local de tu PC de juegos (ej. `192.168.1.50`).
3. Elige tu tamaño de interfaz preferido (`100%`, `115%`, `125%` o `140%`).
4. Pulsa **"Guardar y Conectar"**. La app se reconecta al instante y guarda la configuración.
