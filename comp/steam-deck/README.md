# 🎮 Compilador: App para Steam Deck (SteamOS)

### 📌 ¿Qué genera?
Genera el paquete ejecutable para SteamOS en **`dist/steam-deck/`**:
- En Linux: Genera **`SteamDeckCompanion-linux-x86_64.AppImage`**.
- En Windows: Genera **`SteamDeckCompanion-linux-x64.zip`** (y `.tar.gz`).

### ⚙️ Requisitos para compilar:
- Node.js (v18 o v20) y npm instalado.

### 🚀 Cómo compilar:
- **Desde Linux (o la propia Steam Deck)**:
  ```bash
  ./build_deck_app.sh
  ```
- **Desde Windows**:
  Haz doble clic en **`build_deck_app.bat`**.

---

### 🎮 Cómo lo usa el usuario en la Steam Deck:
1. Se descarga el archivo `.AppImage` (o descomprime el `.zip`) en su Steam Deck.
2. En Steam (Modo Escritorio), pulsa **"Añadir un juego" ➔ "Añadir un producto que no es de Steam..."** ➔ Selecciona la aplicación.
3. ¡Vuelve a **Gaming Mode** y le da a Jugar!
