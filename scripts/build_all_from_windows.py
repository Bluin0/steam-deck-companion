"""
Unified Master Builder to compile all 3 artifacts from Windows:
1. SteamDeckCompanionServer-Windows.exe (Windows PC Server)
2. SteamDeckCompanion-linux-x64.zip / .AppImage (Steam Deck Client)
3. SteamDeckCompanionServer-Linux (Linux PC Server via WSL/Docker or Portable bundle)
"""

import os
import sys
import subprocess
import shutil
import zipfile
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
    
    # Standard alias
    shutil.copyfile(dist_dir / "SteamDeckCompanionServer-Windows.exe", dist_dir / "SteamDeckCompanionServer.exe")
    shutil.rmtree(build_dir, ignore_errors=True)
    print("✅ Servidor Windows compilado en: dist/SteamDeckCompanionServer-Windows.exe")

def build_deck_app(root):
    print_header("2/3 COMPILANDO APP STEAM DECK (Linux x64)")
    deck_dir = root / "deck-app"
    
    print("[+] Instalando dependencias de Node.js en deck-app...")
    subprocess.check_call(["npm", "install"], cwd=str(deck_dir), shell=True)
    
    print("[+] Empaquetando aplicación portable para SteamOS (zip / tar.gz)...")
    subprocess.check_call(["npm", "run", "build:linux"], cwd=str(deck_dir), shell=True)

    # Try AppImage if Windows Developer Mode / symlinks are enabled
    try:
        print("[+] Intentando generar también .AppImage...")
        subprocess.check_call(["npm", "run", "build:appimage"], cwd=str(deck_dir), shell=True)
    except Exception:
        print("ℹ️  Nota: .AppImage requiere permisos de administrador en Windows. El paquete portable .zip/.tar.gz se ha generado perfectamente.")
        
    print("✅ App de Steam Deck generada en: deck-app/dist/")

def is_wsl_functional():
    if not shutil.which("wsl"):
        return False
    try:
        # Check without interactive prompt
        out = subprocess.run(["wsl", "-l", "-q"], capture_output=True, text=True, timeout=5)
        return out.returncode == 0 and len(out.stdout.strip()) > 0
    except Exception:
        return False

def is_docker_functional():
    if not shutil.which("docker"):
        return False
    try:
        out = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        return out.returncode == 0
    except Exception:
        return False

def build_linux_server(root):
    print_header("3/3 PREPARANDO SERVIDOR PARA LINUX")
    dist_dir = root / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 1. Check WSL
    if is_wsl_functional():
        print("[+] Detectado WSL activo. Compilando binario ELF nativo de Linux...")
        try:
            wsl_cmd = "python3 -m pip install --quiet -r requirements.txt pyinstaller 2>/dev/null; python3 scripts/build_server.py"
            subprocess.check_call(["wsl", "bash", "-c", wsl_cmd])
            if (dist_dir / "SteamDeckCompanionServer").exists():
                shutil.copyfile(dist_dir / "SteamDeckCompanionServer", dist_dir / "SteamDeckCompanionServer-Linux")
                print("✅ Servidor Linux binario compilado en: dist/SteamDeckCompanionServer-Linux")
                return
        except Exception as e:
            print(f"[!] Error con WSL: {e}")

    # 2. Check Docker
    if is_docker_functional():
        print("[+] Detectado Docker Desktop activo. Compilando binario ELF en contenedor Linux...")
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
                print("✅ Servidor Linux binario compilado en: dist/SteamDeckCompanionServer-Linux")
                return
        except Exception as e:
            print(f"[!] Error con Docker: {e}")

    # 3. Fallback: Portable Linux Server Package (Zero-configuration 1-Click for Linux)
    print("[+] Creando Paquete Portable Autónomo del Servidor Linux (1-Click)...")
    portable_zip_path = dist_dir / "SteamDeckCompanionServer-Linux-Portable.zip"
    
    with zipfile.ZipFile(portable_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Include start script
        start_sh_content = (
            "#!/usr/bin/env bash\n"
            "cd \"$(dirname \"$0\")\"\n"
            "echo \"==========================================\"\n"
            "echo \"    STEAM DECK COMPANION SERVER (LINUX)   \"\n"
            "echo \"==========================================\"\n"
            "python3 -m pip install --quiet -r requirements.txt 2>/dev/null || true\n"
            "python3 src/server/main.py\n"
        )
        zf.writestr("start_server.sh", start_sh_content)
        
        # Include requirements.txt
        zf.write(root / "requirements.txt", "requirements.txt")
        
        # Include src/
        for root_folder, _, files in os.walk(root / "src"):
            for f in files:
                full_p = Path(root_folder) / f
                rel_p = full_p.relative_to(root)
                zf.write(full_p, str(rel_p))
                
        # Include profiles/
        for root_folder, _, files in os.walk(root / "profiles"):
            for f in files:
                full_p = Path(root_folder) / f
                rel_p = full_p.relative_to(root)
                zf.write(full_p, str(rel_p))

    print(f"✅ Paquete de Servidor Linux 1-Click generado en: dist/{portable_zip_path.name}")

def main():
    root = Path(__file__).resolve().parent.parent
    
    # 1. Build Windows Server
    try:
        build_windows_server(root)
    except Exception as e:
        print(f"❌ Error al compilar Servidor Windows: {e}")
        
    # 2. Build Steam Deck App
    try:
        build_deck_app(root)
    except Exception as e:
        print(f"❌ Error al compilar App de Steam Deck: {e}")

    # 3. Build Linux Server
    try:
        build_linux_server(root)
    except Exception as e:
        print(f"❌ Error al compilar Servidor Linux: {e}")

    print_header("RESUMEN DE ARCHIVOS GENERADOS PARA GITHUB RELEASES")
    print("1. 🖥️  dist/SteamDeckCompanionServer-Windows.exe (Servidor PC Windows)")
    print("2. 🎮 deck-app/dist/*.zip o *.AppImage (App para Steam Deck)")
    print("3. 🐧 dist/SteamDeckCompanionServer-Linux* (Servidor para Linux)")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
