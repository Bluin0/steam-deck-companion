"""
Unified Master Builder to compile all 3 artifacts from Windows:
1. SteamDeckCompanionServer-Windows.exe (Windows PC Server)
2. SteamDeckCompanionServer-Linux (Linux PC Server via WSL / Docker)
3. SteamDeckCompanion-SteamDeck.AppImage (Steam Deck Client via electron-builder)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    print("\n" + "="*65)
    print(f"  🚀 {title}")
    print("="*65)

def build_windows_server(root):
    print_header("1/3 COMPILANDO SERVIDOR WINDOWS (.exe)")
    dist_dir = root / "dist"
    build_dir = root / "build_temp_win"
    dist_dir.mkdir(exist_ok=True)
    
    profiles_data = f"{root / 'profiles'};profiles"
    client_data = f"{root / 'src' / 'client'};src/client"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "SteamDeckCompanionServer-Windows",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--add-data", profiles_data,
        "--add-data", client_data,
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(build_dir),
        str(root / "src" / "server" / "main.py")
    ]
    
    print("[+] Ejecutando PyInstaller para Windows...")
    subprocess.check_call(cmd)
    
    # Also create standard named alias
    shutil.copyfile(dist_dir / "SteamDeckCompanionServer-Windows.exe", dist_dir / "SteamDeckCompanionServer.exe")
    shutil.rmtree(build_dir, ignore_errors=True)
    print("✅ Servidor Windows compilado en: dist/SteamDeckCompanionServer-Windows.exe")

def build_deck_app(root):
    print_header("2/3 COMPILANDO APP STEAM DECK (.AppImage)")
    deck_dir = root / "deck-app"
    
    print("[+] Instalando dependencias de Node.js en deck-app...")
    subprocess.check_call(["npm", "install"], cwd=str(deck_dir), shell=True)
    
    print("[+] Generando .AppImage para SteamOS con electron-builder...")
    subprocess.check_call(["npm", "run", "build:linux"], cwd=str(deck_dir), shell=True)
    print("✅ App de Steam Deck compilada en: deck-app/dist/")

def build_linux_server(root):
    print_header("3/3 COMPILANDO SERVIDOR LINUX (Binario ELF)")
    dist_dir = root / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # Check 1: WSL
    if shutil.which("wsl"):
        print("[+] Detectado WSL (Windows Subsystem for Linux). Compilando binario Linux...")
        try:
            # Get WSL path for root
            wsl_cmd = "python3 -m pip install --quiet -r requirements.txt pyinstaller 2>/dev/null; python3 scripts/build_server.py"
            subprocess.check_call(["wsl", "bash", "-c", wsl_cmd])
            
            if (dist_dir / "SteamDeckCompanionServer").exists():
                shutil.copyfile(dist_dir / "SteamDeckCompanionServer", dist_dir / "SteamDeckCompanionServer-Linux")
                print("✅ Servidor Linux compilado con éxito mediante WSL: dist/SteamDeckCompanionServer-Linux")
                return
        except Exception as e:
            print(f"[!] WSL build attempt error: {e}")

    # Check 2: Docker
    if shutil.which("docker"):
        print("[+] Detectado Docker. Compilando binario Linux en contenedor x86_64...")
        try:
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{root}:/app",
                "-w", "/app",
                "python:3.11-slim",
                "bash", "-c",
                "pip install --quiet -r requirements.txt pyinstaller && python scripts/build_server.py"
            ]
            subprocess.check_call(docker_cmd)
            if (dist_dir / "SteamDeckCompanionServer").exists():
                shutil.copyfile(dist_dir / "SteamDeckCompanionServer", dist_dir / "SteamDeckCompanionServer-Linux")
                print("✅ Servidor Linux compilado con éxito mediante Docker: dist/SteamDeckCompanionServer-Linux")
                return
        except Exception as e:
            print(f"[!] Docker build attempt error: {e}")

    print("\nℹ️  NOTA SOBRE EL SERVIDOR LINUX:")
    print("PyInstaller requiere el kernel de Linux para compilar binarios ELF nativos.")
    print("Para compilarlo desde Windows, simplemente necesitas:")
    print("  Opción A: Tener WSL instalado en Windows (escribe 'wsl --install' en PowerShell).")
    print("  Opción B: Tener Docker Desktop abierto.")
    print("  Opción C: Ejecutar './build_server.sh' en cualquier máquina o terminal Linux.")

def main():
    root = Path(__file__).resolve().parent.parent
    
    # 1. Build Windows Server
    try:
        build_windows_server(root)
    except Exception as e:
        print(f"❌ Error al compilar Servidor Windows: {e}")
        
    # 2. Build Steam Deck App (.AppImage)
    try:
        build_deck_app(root)
    except Exception as e:
        print(f"❌ Error al compilar App de Steam Deck: {e}")

    # 3. Build Linux Server
    try:
        build_linux_server(root)
    except Exception as e:
        print(f"❌ Error al compilar Servidor Linux: {e}")

    print_header("RESUMEN DE ARCHIVOS LISTOS PARA GITHUB RELEASES")
    print("1. 📄 dist/SteamDeckCompanionServer-Windows.exe (o SteamDeckCompanionServer.exe)")
    print("2. 📄 deck-app/dist/*.AppImage (App de Steam Deck)")
    print("3. 📄 dist/SteamDeckCompanionServer-Linux (si tienes WSL/Docker activado)")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
