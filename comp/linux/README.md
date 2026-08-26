# 🐧 Compilador: Servidor PC Linux

### 📌 ¿Qué genera?
Genera el archivo binario **`dist/linux/SteamDeckCompanionServer`** (ejecutable ELF nativo de 64 bits para Linux).

### ⚙️ Requisitos para compilar:
- Sistema Operativo: **Cualquier distribución Linux (Ubuntu, Debian, Fedora, Arch, SteamOS, Manjaro, etc.)**.
- Python 3.10+ y `pip`.

### 🚀 Cómo compilar:
En tu terminal Linux, ejecuta:
```bash
./build_server.sh
```

---

### 🎮 Cómo lo usa el usuario final:
1. El usuario se descarga `SteamDeckCompanionServer` desde GitHub Releases.
2. Abre la terminal o le da permisos de ejecución y lo inicia:
   ```bash
   chmod +x SteamDeckCompanionServer
   ./SteamDeckCompanionServer
   ```
   *(No necesita tener Python instalado ni librerías adicionales)*.
