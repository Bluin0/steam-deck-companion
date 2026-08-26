"""
Build script to compile Steam Deck Companion PC Server into a single-file executable using PyInstaller.
Compatible with Windows (.exe) and Linux standalone binary.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build():
    root = Path(__file__).resolve().parent.parent
    dist_dir = root / "dist"
    build_dir = root / "build_temp"
    
    print("==========================================")
    print(" 🛠️  COMPILANDO SERVIDOR COMPANION ")
    print("==========================================")
    print(f"Sistema Operativo: {sys.platform}")
    print(f"Directorio raíz: {root}")
    
    # 1. Ensure PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("[!] Intentando instalar PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        except Exception:
            try:
                subprocess.check_call(["pip", "install", "pyinstaller"])
            except Exception:
                try:
                    subprocess.check_call(["pip3", "install", "pyinstaller"])
                except Exception as e:
                    print(f"⚠️ No se pudo instalar PyInstaller automáticamente. Por favor ejecuta 'pip install pyinstaller'. Error: {e}")

    # 2. Prepare PyInstaller command
    sep = ";" if sys.platform == "win32" else ":"
    profiles_data = f"{root / 'profiles'}{sep}profiles"
    client_data = f"{root / 'src' / 'client'}{sep}src/client"
    
    output_name = "SteamDeckCompanionServer"
    if sys.platform == "win32":
        output_name += ".exe"

    pyinstaller_bin = [sys.executable, "-m", "PyInstaller"]
    
    cmd = pyinstaller_bin + [
        "--name", "SteamDeckCompanionServer",
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

    print("\n[+] Ejecutando compilación...")
    print(" ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except Exception:
        # Fallback to direct pyinstaller command
        fallback_cmd = ["pyinstaller"] + cmd[3:]
        print("\n[!] Reintentando con comando directo 'pyinstaller'...")
        subprocess.check_call(fallback_cmd)

    # 3. Clean temporary build directory
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)

    print("\n==========================================")
    print(" ✅ ¡COMPILACIÓN EXITOSA!")
    print(f" 📂 Archivo generado en: {dist_dir / output_name}")
    print("==========================================")

if __name__ == "__main__":
    build()
