# 🎮 Steam Deck Companion

Segunda pantalla interactiva y mando virtual de baja latencia para tu Steam Deck conectada a tu PC de juegos (Windows / Linux) por red local.

---

## ✨ Características

- 🎯 **Detección Automática de Juegos**: Detecta el juego que estás jugando en tu PC (Steam o catálogo global) y adapta toda la interfaz al instante.
- 🗺️ **Mapas Interactivos Directos**: Carga automáticamente el mapa interactivo (MapGenie, etc.) del juego activo con búsqueda inteligente de respaldo (cero errores 404).
- 📖 **Guías Comunitarias y Wikis**: Guías de Steam o wikis en español (Vandal/Eliteguias) con un solo toque.
- ⏱️ **HowLongToBeat**: Información de duración y estadísticas del juego sincronizadas.
- 📝 **Bloc de Notas Persistente**: Toma apuntes, códigos y recetas que se guardan directamente en tu PC.
- 🎮 **Mando Virtual y Visualizador**: Streaming de inputs a 0ms hacia un mando Xbox 360 virtual en tu PC (`ViGEmBus` en Windows o `uinput` en Linux) con pestaña de diagnóstico y calibración en tiempo real.
- 🛡️ **App Nativa con Bloqueador de Anuncios**: Carga ultra-rápida, resolución adaptada a 1280x800 y controles de zoom táctil.

---

## 🚀 Guía Rápida

### 1. En tu PC de Juegos (Servidor)
> Compatible con **Windows** y **Linux**

1. Clona el repositorio e instala las dependencias:
   ```bash
   git clone https://github.com/Bluin0/steam-deck-companion.git
   cd steam-deck-companion
   pip install -r requirements.txt
   ```
   *(En Windows, asegúrate de tener instalado el driver [ViGEmBus](https://github.com/nefarius/ViGEmBus/releases)).*

2. Inicia el servidor:
   ```bash
   python src/server/main.py
   ```
   *(Anota la IP local de tu PC, por ejemplo `192.168.1.100`)*.

---

### 2. En tu Steam Deck (Cliente Nativo)

Puedes instalar la aplicación en tu Steam Deck con **un solo comando**:

1. En tu Steam Deck, cambia a **Modo Escritorio** (*Desktop Mode*).
2. Abre la terminal **Konsole** y pega:
   ```bash
   curl -sSL https://raw.githubusercontent.com/Bluin0/steam-deck-companion/main/scripts/install_deck_app.sh | bash
   ```
3. Introduce la IP local de tu PC cuando te lo pida.

#### Para añadirlo a la biblioteca de Gaming Mode:
1. Abre Steam en Modo Escritorio.
2. Pulsa abajo a la izquierda en **"Añadir un juego"** ➔ **"Añadir un producto que no es de Steam..."**.
3. Selecciona **Steam Deck Companion** y pulsa *Añadir seleccionados*.
4. ¡Vuelve a **Gaming Mode** y lánzalo como cualquier juego de tu biblioteca!

---

## 🛠️ Desarrollo y Pruebas en PC

Para probar la app de Steam Deck directamente en tu ordenador:
```bash
npx electron deck-app --pc-ip=127.0.0.1
```
