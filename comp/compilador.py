"""
Steam Deck Companion — Compilador Visual (GUI)
Aplicación gráfica para compilar los 3 ejecutables con un clic.
Ejecutar desde Windows: python comp/compilador.py
"""

import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import os
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


class CompiladorGUI:
    BG = "#0a0d14"
    BG_CARD = "#141923"
    BG_INPUT = "#1a2233"
    FG = "#e0e6f0"
    FG_DIM = "#6b7a90"
    GREEN = "#00d4aa"
    RED = "#ff4d6a"
    YELLOW = "#ffc107"
    BLUE = "#4da6ff"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Steam Deck Companion — Compilador")
        self.root.configure(bg=self.BG)
        self.root.minsize(720, 600)
        self.root.geometry("760x650")
        self.building = False
        self._build_ui()

    def _build_ui(self):
        # ── Title ──
        tk.Label(self.root, text="🛠️ Compilador de Steam Deck Companion",
                 font=("Segoe UI", 18, "bold"), bg=self.BG, fg=self.FG
                 ).pack(fill="x", padx=24, pady=(20, 4))

        tk.Label(self.root, text="Compila los ejecutables para subir a GitHub Releases",
                 font=("Segoe UI", 10), bg=self.BG, fg=self.FG_DIM
                 ).pack(fill="x", padx=24, pady=(0, 12))

        # ── Build Cards ──
        cards_frame = tk.Frame(self.root, bg=self.BG)
        cards_frame.pack(fill="x", padx=24, pady=(0, 8))

        # Card 1: Windows Server
        self._make_card(cards_frame, 0,
                        icon="🖥️", title="Servidor Windows",
                        desc=".exe con GUI (PyInstaller)",
                        output="dist/windows/SteamDeckCompanionServer.exe",
                        btn_text="Compilar .exe",
                        btn_cmd=self._build_windows_server,
                        status_id="win")

        # Card 2: Steam Deck App
        self._make_card(cards_frame, 1,
                        icon="🎮", title="App Steam Deck",
                        desc=".AppImage (Electron Builder)",
                        output="dist/steam-deck/*.AppImage",
                        btn_text="Compilar .AppImage",
                        btn_cmd=self._build_deck_app,
                        status_id="deck")

        # Card 3: Linux Server
        self._make_card(cards_frame, 2,
                        icon="🐧", title="Servidor Linux",
                        desc="Script Universal (.sh)",
                        output="dist/linux/SteamDeckCompanionServer.sh",
                        btn_text="Generar .sh",
                        btn_cmd=self._build_linux_server,
                        status_id="linux")

        # ── Build All Button ──
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(fill="x", padx=24, pady=(8, 0))

        self.build_all_btn = tk.Button(
            btn_frame, text="🚀  COMPILAR TODO", font=("Segoe UI", 14, "bold"),
            bg="#4da6ff", fg="white", activebackground="#3d96ef",
            activeforeground="white", relief="flat", cursor="hand2",
            command=self._build_all, height=2)
        self.build_all_btn.pack(fill="x")

        # ── Log ──
        log_frame = tk.Frame(self.root, bg=self.BG)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(12, 16))

        tk.Label(log_frame, text="📋 Registro de compilación:",
                 font=("Segoe UI", 9), bg=self.BG, fg=self.FG_DIM).pack(anchor="w")

        self.log_area = scrolledtext.ScrolledText(
            log_frame, font=("Consolas", 9), height=10,
            bg=self.BG_INPUT, fg=self.FG_DIM, insertbackground=self.FG,
            relief="flat", state="disabled", wrap="word",
            selectbackground="#2a3a50")
        self.log_area.pack(fill="both", expand=True, pady=(4, 0))

    def _make_card(self, parent, col, icon, title, desc, output, btn_text, btn_cmd, status_id):
        """Create a build target card."""
        card = tk.Frame(parent, bg=self.BG_CARD, highlightbackground="#1e2a3a",
                        highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0 if col == 2 else 6), pady=4)
        parent.columnconfigure(col, weight=1)

        tk.Label(card, text=icon, font=("Segoe UI", 28), bg=self.BG_CARD, fg=self.FG
                 ).pack(pady=(12, 2))

        tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), bg=self.BG_CARD, fg=self.FG
                 ).pack()

        tk.Label(card, text=desc, font=("Segoe UI", 8), bg=self.BG_CARD, fg=self.FG_DIM
                 ).pack(pady=(0, 2))

        tk.Label(card, text=output, font=("Consolas", 7), bg=self.BG_CARD, fg=self.FG_DIM
                 ).pack(pady=(0, 6))

        # Status indicator
        status = tk.Label(card, text="⏳ Pendiente", font=("Segoe UI", 9),
                          bg=self.BG_CARD, fg=self.FG_DIM)
        status.pack(pady=(0, 4))
        setattr(self, f"status_{status_id}", status)

        btn = tk.Button(card, text=btn_text, font=("Segoe UI", 10, "bold"),
                        bg="#00b894", fg="white", activebackground="#00a885",
                        activeforeground="white", relief="flat", cursor="hand2",
                        command=btn_cmd)
        btn.pack(fill="x", padx=12, pady=(0, 12))
        setattr(self, f"btn_{status_id}", btn)

    # ──────── Logging ────────

    def _log(self, msg):
        def _do():
            self.log_area.config(state="normal")
            self.log_area.insert("end", msg + "\n")
            self.log_area.see("end")
            self.log_area.config(state="disabled")
        self.root.after(0, _do)

    def _set_card_status(self, status_id, text, color):
        def _do():
            label = getattr(self, f"status_{status_id}", None)
            if label:
                label.config(text=text, fg=color)
        self.root.after(0, _do)

    def _set_buttons_state(self, enabled):
        def _do():
            state = "normal" if enabled else "disabled"
            for sid in ["win", "deck", "linux"]:
                btn = getattr(self, f"btn_{sid}", None)
                if btn:
                    btn.config(state=state)
            self.build_all_btn.config(state=state)
        self.root.after(0, _do)

    # ──────── Build Tasks ────────

    def _run_cmd(self, cmd, cwd=None, shell=False):
        """Run a command and stream output to log. Returns True on success."""
        self._log(f"$ {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
        try:
            proc = subprocess.Popen(
                cmd, cwd=cwd or str(ROOT_DIR), shell=shell,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace")
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    self._log(line)
            proc.wait()
            return proc.returncode == 0
        except Exception as e:
            self._log(f"[ERROR] {e}")
            return False

    def _build_windows_server(self):
        if self.building:
            return
        self.building = True
        self._set_buttons_state(False)

        def _task():
            self._set_card_status("win", "🔄 Compilando...", self.YELLOW)
            self._log("\n══════ COMPILANDO SERVIDOR WINDOWS (.exe) ══════")

            os.makedirs(ROOT_DIR / "dist" / "windows", exist_ok=True)

            ok = self._run_cmd([
                sys.executable, "-m", "PyInstaller",
                "--name", "SteamDeckCompanionServer",
                "--onefile", "--windowed", "--clean", "--noconfirm",
                "--collect-all", "vgamepad",
                "--add-data", f"{ROOT_DIR / 'profiles'};profiles",
                "--add-data", f"{ROOT_DIR / 'src' / 'client'};src/client",
                "--add-data", f"{ROOT_DIR / 'drivers'};drivers",
                "--distpath", str(ROOT_DIR / "dist" / "windows"),
                str(ROOT_DIR / "src" / "server" / "main.py")
            ])

            # Clean temp files
            for f in ["SteamDeckCompanionServer.spec"]:
                p = ROOT_DIR / f
                if p.exists():
                    p.unlink()
            build_dir = ROOT_DIR / "build"
            if build_dir.exists():
                shutil.rmtree(build_dir, ignore_errors=True)

            if ok and (ROOT_DIR / "dist" / "windows" / "SteamDeckCompanionServer.exe").exists():
                self._set_card_status("win", "✅ Compilado", self.GREEN)
                self._log("[OK] dist/windows/SteamDeckCompanionServer.exe")
            else:
                self._set_card_status("win", "❌ Error", self.RED)

            self.building = False
            self._set_buttons_state(True)

        threading.Thread(target=_task, daemon=True).start()

    def _build_deck_app(self):
        if self.building:
            return
        self.building = True
        self._set_buttons_state(False)

        def _task():
            self._set_card_status("deck", "🔄 Compilando...", self.YELLOW)
            self._log("\n══════ COMPILANDO APP STEAM DECK ══════")

            deck_dir = ROOT_DIR / "deck-app"

            # Check if npm is missing on Linux / SteamOS and download portable Node.js
            if not shutil.which("npm") and sys.platform != "win32":
                self._log("[+] Node.js / npm no detectado. Descargando versión portable...")
                node_dir = ROOT_DIR / ".node_portable"
                if not (node_dir / "bin" / "node").exists():
                    os.makedirs(node_dir, exist_ok=True)
                    self._run_cmd('curl -sSL https://nodejs.org/dist/v20.11.1/node-v20.11.1-linux-x64.tar.xz | tar -xJ -C "' + str(node_dir) + '" --strip-components=1', shell=True)
                os.environ["PATH"] = f"{node_dir / 'bin'}:{os.environ.get('PATH', '')}"

            self._log("[1/2] Instalando dependencias npm...")
            self._run_cmd("npm install", cwd=str(deck_dir), shell=True)

            self._log("[2/2] Empaquetando aplicación para SteamOS...")
            # Run electron-builder for zip and AppImage
            self._run_cmd("npx electron-builder --linux zip AppImage",
                          cwd=str(deck_dir), shell=True)

            # Check if WSL is available to produce native AppImage if Windows mksquashfs failed
            if sys.platform == "win32" and shutil.which("wsl"):
                try:
                    self._log("[+] WSL detectado. Intentando generar .AppImage nativo...")
                    self._run_cmd('wsl bash -c "cd $(wslpath -u \'' + str(deck_dir).replace('\\', '/') + '\') && npx electron-builder --linux AppImage"', shell=True)
                except Exception:
                    pass

            os.makedirs(ROOT_DIR / "dist" / "steam-deck", exist_ok=True)

            # Copy generated artifacts
            dist_deck = deck_dir / "dist"
            found_appimage = False
            found_zip = False
            if dist_deck.exists():
                for f in dist_deck.iterdir():
                    if f.suffix == ".AppImage":
                        shutil.copy2(f, ROOT_DIR / "dist" / "steam-deck" / f.name)
                        found_appimage = True
                        self._log(f"[OK] dist/steam-deck/{f.name}")
                    elif f.suffix == ".zip":
                        shutil.copy2(f, ROOT_DIR / "dist" / "steam-deck" / f.name)
                        found_zip = True
                        self._log(f"[OK] dist/steam-deck/{f.name}")

            if found_appimage:
                self._set_card_status("deck", "✅ Compilado (.AppImage)", self.GREEN)
            elif found_zip:
                self._set_card_status("deck", "✅ Compilado (.zip)", self.GREEN)
                self._log("ℹ️  Se ha generado el paquete portable .zip para Steam Deck.")
            else:
                self._set_card_status("deck", "❌ Error", self.RED)

            self.building = False
            self._set_buttons_state(True)

        threading.Thread(target=_task, daemon=True).start()

    def _generate_linux_sh(self):
        """Generates a standalone, self-extracting single .sh server runner for Linux."""
        import tarfile
        os.makedirs(ROOT_DIR / "dist" / "linux", exist_ok=True)
        sh_path = ROOT_DIR / "dist" / "linux" / "SteamDeckCompanionServer.sh"

        header = (
            "#!/usr/bin/env bash\n"
            "# =======================================================\n"
            "#    STEAM DECK COMPANION SERVER — PORTABLE LINUX RUNNER\n"
            "# =======================================================\n\n"
            "set -e\n\n"
            'APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/steam-deck-companion/server"\n'
            'mkdir -p "$APP_DIR"\n\n'
            'if ! command -v python3 &> /dev/null; then\n'
            '    echo "ERROR: Se requiere Python 3 instalado en el sistema."\n'
            '    exit 1\n'
            'fi\n\n'
            'SCRIPT_HASH=$(md5sum "$0" 2>/dev/null | cut -d\' \' -f1 || cksum "$0" 2>/dev/null | cut -d\' \' -f1 || echo "installed")\n'
            'HASH_FILE="$APP_DIR/.version_hash"\n\n'
            'if [ ! -f "$HASH_FILE" ] || [ "$SCRIPT_HASH" != "$(cat "$HASH_FILE" 2>/dev/null)" ]; then\n'
            '    echo "[+] Preparando Steam Deck Companion Server en $APP_DIR..."\n'
            '    PAYLOAD_LINE=$(awk \'/^__PAYLOAD_BELOW__/ {print NR + 1; exit 0; }\' "$0")\n'
            '    tail -n +"$PAYLOAD_LINE" "$0" | tar -xz -C "$APP_DIR"\n'
            '    echo "$SCRIPT_HASH" > "$HASH_FILE"\n'
            'fi\n\n'
            'cd "$APP_DIR"\n\n'
            '# ── Setup Python dependencies if missing ──\n'
            'VENV_DIR="$APP_DIR/.venv"\n'
            'PYTHON_BIN="python3"\n\n'
            'if ! "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then\n'
            '    echo "[+] Verificando dependencias de Python (websockets, psutil)..."\n'
            '    python3 -m pip install --user --quiet -r "$APP_DIR/requirements.txt" 2>/dev/null || \\\n'
            '    pip3 install --user --quiet -r "$APP_DIR/requirements.txt" 2>/dev/null || true\n\n'
            '    if ! "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then\n'
            '        if [ ! -d "$VENV_DIR" ]; then\n'
            '            python3 -m venv "$VENV_DIR" 2>/dev/null || true\n'
            '        fi\n'
            '        if [ -f "$VENV_DIR/bin/pip" ]; then\n'
            '            "$VENV_DIR/bin/pip" install --quiet -r "$APP_DIR/requirements.txt" 2>/dev/null || true\n'
            '            PYTHON_BIN="$VENV_DIR/bin/python3"\n'
            '        fi\n'
            '    fi\n\n'
            '    if ! "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then\n'
            '        echo "[+] Configurando entorno Python portable automático..."\n'
            '        UV_DIR="$APP_DIR/.uv"\n'
            '        mkdir -p "$UV_DIR"\n'
            '        if [ ! -f "$UV_DIR/uv" ]; then\n'
            '            ARCH=$(uname -m)\n'
            '            curl -sSL "https://github.com/astral-sh/uv/releases/latest/download/uv-${ARCH}-unknown-linux-gnu.tar.gz" 2>/dev/null | tar -xz -C "$UV_DIR" --strip-components=1 2>/dev/null || true\n'
            '        fi\n'
            '        if [ -f "$UV_DIR/uv" ]; then\n'
            '            export UV_LINK_MODE=copy\n'
            '            "$UV_DIR/uv" python install 3.12 2>/dev/null || true\n'
            '            "$UV_DIR/uv" venv "$VENV_DIR" --python 3.12 2>/dev/null || "$UV_DIR/uv" venv "$VENV_DIR" 2>/dev/null || true\n'
            '            "$UV_DIR/uv" pip install --no-cache -r "$APP_DIR/requirements.txt" --python "$VENV_DIR/bin/python3" 2>/dev/null || true\n'
            '            if [ -f "$VENV_DIR/bin/python3" ]; then\n'
            '                PYTHON_BIN="$VENV_DIR/bin/python3"\n'
            '            fi\n'
            '        fi\n'
            '    fi\n'
            'fi\n\n'
            '# ── Launch Server ──\n'
            'exec "$PYTHON_BIN" "$APP_DIR/src/server/main.py" "$@"\n\n'
            '__PAYLOAD_BELOW__\n'
        )

        with open(sh_path, "wb") as out_f:
            out_f.write(header.encode("utf-8"))
            with tarfile.open(fileobj=out_f, mode="w:gz") as tar:
                tar.add(ROOT_DIR / "src", arcname="src",
                        filter=lambda ti: None if "__pycache__" in ti.name or ti.name.endswith(".pyc") else ti)
                tar.add(ROOT_DIR / "profiles", arcname="profiles")
                tar.add(ROOT_DIR / "requirements.txt", arcname="requirements.txt")

        try:
            sh_path.chmod(0o755)
        except Exception:
            pass

        return sh_path

    def _build_linux_server(self):
        if self.building:
            return
        self.building = True
        self._set_buttons_state(False)

        def _task():
            self._set_card_status("linux", "🔄 Generando...", self.YELLOW)
            self._log("\n══════ GENERANDO SERVIDOR LINUX (.sh) ══════")

            try:
                sh_path = self._generate_linux_sh()
                self._set_card_status("linux", "✅ Generado", self.GREEN)
                self._log(f"[OK] {sh_path.relative_to(ROOT_DIR)}")
                self._log("Script autónomo universal listo para todas las distros Linux.")

            except Exception as e:
                self._set_card_status("linux", "❌ Error", self.RED)
                self._log(f"[ERROR] {e}")

            self.building = False
            self._set_buttons_state(True)

        threading.Thread(target=_task, daemon=True).start()

    def _build_all(self):
        if self.building:
            return
        self.building = True
        self._set_buttons_state(False)

        def _task():
            self._log("\n🚀 ══════ COMPILANDO TODO ══════\n")

            # 1. Windows Server
            self._set_card_status("win", "🔄 Compilando...", self.YELLOW)
            self._log("══════ [1/3] SERVIDOR WINDOWS (.exe) ══════")
            os.makedirs(ROOT_DIR / "dist" / "windows", exist_ok=True)
            ok_win = self._run_cmd([
                sys.executable, "-m", "PyInstaller",
                "--name", "SteamDeckCompanionServer",
                "--onefile", "--windowed", "--clean", "--noconfirm",
                "--collect-all", "vgamepad",
                "--add-data", f"{ROOT_DIR / 'profiles'};profiles",
                "--add-data", f"{ROOT_DIR / 'src' / 'client'};src/client",
                "--add-data", f"{ROOT_DIR / 'drivers'};drivers",
                "--distpath", str(ROOT_DIR / "dist" / "windows"),
                str(ROOT_DIR / "src" / "server" / "main.py")
            ])
            for f in [ROOT_DIR / "SteamDeckCompanionServer.spec"]:
                if f.exists(): f.unlink()
            if (ROOT_DIR / "build").exists():
                shutil.rmtree(ROOT_DIR / "build", ignore_errors=True)

            if ok_win and (ROOT_DIR / "dist" / "windows" / "SteamDeckCompanionServer.exe").exists():
                self._set_card_status("win", "✅ Compilado", self.GREEN)
            else:
                self._set_card_status("win", "❌ Error", self.RED)

            # 2. Steam Deck App
            self._set_card_status("deck", "🔄 Compilando...", self.YELLOW)
            self._log("\n══════ [2/3] APP STEAM DECK ══════")
            deck_dir = ROOT_DIR / "deck-app"
            self._run_cmd("npm install", cwd=str(deck_dir), shell=True)
            self._run_cmd("npx electron-builder --linux zip AppImage",
                          cwd=str(deck_dir), shell=True)

            if sys.platform == "win32" and shutil.which("wsl"):
                try:
                    self._run_cmd('wsl bash -c "cd $(wslpath -u \'' + str(deck_dir).replace('\\', '/') + '\') && npx electron-builder --linux AppImage"', shell=True)
                except Exception:
                    pass

            os.makedirs(ROOT_DIR / "dist" / "steam-deck", exist_ok=True)
            found_appimage = False
            found_zip = False
            dist_deck = deck_dir / "dist"
            if dist_deck.exists():
                for f in dist_deck.iterdir():
                    if f.suffix == ".AppImage":
                        shutil.copy2(f, ROOT_DIR / "dist" / "steam-deck" / f.name)
                        found_appimage = True
                    elif f.suffix == ".zip":
                        shutil.copy2(f, ROOT_DIR / "dist" / "steam-deck" / f.name)
                        found_zip = True

            if found_appimage or found_zip:
                self._set_card_status("deck", "✅ Compilado", self.GREEN)
            else:
                self._set_card_status("deck", "❌ Error", self.RED)

            # 3. Linux Server Portable (.sh)
            self._set_card_status("linux", "🔄 Generando...", self.YELLOW)
            self._log("\n══════ [3/3] SERVIDOR LINUX (.sh) ══════")
            try:
                sh_path = self._generate_linux_sh()
                self._set_card_status("linux", "✅ Generado", self.GREEN)
                self._log(f"[OK] {sh_path.relative_to(ROOT_DIR)}")
            except Exception as e:
                self._set_card_status("linux", "❌ Error", self.RED)
                self._log(f"[ERROR] {e}")

            self._log("\n══════ RESUMEN ══════")
            self._log("Archivos listos en la carpeta dist/:")
            self._log("  1. dist/windows/SteamDeckCompanionServer.exe")
            self._log("  2. dist/steam-deck/*.AppImage")
            self._log("  3. dist/linux/SteamDeckCompanionServer.sh")
            self._log("\nSube estos archivos a GitHub Releases.")

            self.building = False
            self._set_buttons_state(True)

        threading.Thread(target=_task, daemon=True).start()

    # ──────── Main ────────

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CompiladorGUI()
    app.run()
