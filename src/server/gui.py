"""
Steam Deck Companion Server — Desktop GUI.
Cross-platform tkinter interface for controlling the server with visual feedback.
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import asyncio
import socket
import sys
import os


class ServerGUI:
    """Dark-themed GUI for the Steam Deck Companion Server."""

    BG = "#0a0d14"
    BG_CARD = "#141923"
    BG_INPUT = "#1a2233"
    FG = "#e0e6f0"
    FG_DIM = "#6b7a90"
    ACCENT = "#00d4aa"
    ACCENT_RED = "#ff4d6a"
    ACCENT_YELLOW = "#ffc107"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Steam Deck Companion — Server")
        self.root.configure(bg=self.BG)
        self.root.minsize(620, 480)
        self.root.geometry("680x520")

        # Try to set icon if available
        try:
            if sys.platform == "win32":
                self.root.iconbitmap(default="")
        except Exception:
            pass

        self.server = None
        self.server_thread = None
        self.server_running = False
        self.detector = None
        self.controller = None

        self._build_ui()
        self._log("Servidor listo. Pulsa 'Iniciar Servidor' para empezar.")

    # ──────── UI Construction ────────

    def _build_ui(self):
        # ── Title Bar ──
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(title_frame, text="🎮 Steam Deck Companion", font=("Segoe UI", 18, "bold"),
                 bg=self.BG, fg=self.FG).pack(side="left")

        self.status_label = tk.Label(title_frame, text="● Detenido", font=("Segoe UI", 11),
                                     bg=self.BG, fg=self.ACCENT_RED)
        self.status_label.pack(side="right")

        # ── IP Display Card ──
        ip_card = tk.Frame(self.root, bg=self.BG_CARD, highlightbackground="#1e2a3a",
                           highlightthickness=1)
        ip_card.pack(fill="x", padx=20, pady=(14, 0), ipady=10)

        tk.Label(ip_card, text="📌 IP LOCAL PARA LA STEAM DECK:", font=("Segoe UI", 9),
                 bg=self.BG_CARD, fg=self.FG_DIM).pack(pady=(8, 0))

        self.ip_display = tk.Label(ip_card, text=self._get_local_ip(), font=("Consolas", 26, "bold"),
                                   bg=self.BG_CARD, fg=self.ACCENT)
        self.ip_display.pack(pady=(2, 4))

        ports_text = "HTTP :8080  •  WebSocket :8765"
        tk.Label(ip_card, text=ports_text, font=("Segoe UI", 9),
                 bg=self.BG_CARD, fg=self.FG_DIM).pack(pady=(0, 8))

        # ── Info Row ──
        info_frame = tk.Frame(self.root, bg=self.BG)
        info_frame.pack(fill="x", padx=20, pady=(12, 0))

        # Games detected
        games_card = tk.Frame(info_frame, bg=self.BG_CARD, highlightbackground="#1e2a3a",
                              highlightthickness=1)
        games_card.pack(side="left", fill="both", expand=True, padx=(0, 6), ipady=6)

        tk.Label(games_card, text="🕹️ Juegos detectados", font=("Segoe UI", 9),
                 bg=self.BG_CARD, fg=self.FG_DIM).pack(pady=(6, 0))
        self.games_count = tk.Label(games_card, text="—", font=("Segoe UI", 16, "bold"),
                                    bg=self.BG_CARD, fg=self.FG)
        self.games_count.pack(pady=(0, 6))

        # Clients connected
        clients_card = tk.Frame(info_frame, bg=self.BG_CARD, highlightbackground="#1e2a3a",
                                highlightthickness=1)
        clients_card.pack(side="left", fill="both", expand=True, padx=(6, 6), ipady=6)

        tk.Label(clients_card, text="📱 Clientes conectados", font=("Segoe UI", 9),
                 bg=self.BG_CARD, fg=self.FG_DIM).pack(pady=(6, 0))
        self.clients_count = tk.Label(clients_card, text="0", font=("Segoe UI", 16, "bold"),
                                      bg=self.BG_CARD, fg=self.FG)
        self.clients_count.pack(pady=(0, 6))

        # Current game
        game_card = tk.Frame(info_frame, bg=self.BG_CARD, highlightbackground="#1e2a3a",
                             highlightthickness=1)
        game_card.pack(side="left", fill="both", expand=True, padx=(6, 0), ipady=6)

        tk.Label(game_card, text="🎯 Juego activo", font=("Segoe UI", 9),
                 bg=self.BG_CARD, fg=self.FG_DIM).pack(pady=(6, 0))
        self.game_name = tk.Label(game_card, text="Ninguno", font=("Segoe UI", 10, "bold"),
                                  bg=self.BG_CARD, fg=self.FG, wraplength=180)
        self.game_name.pack(pady=(0, 6))

        # ── Start / Stop Button ──
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(fill="x", padx=20, pady=(14, 0))

        self.start_btn = tk.Button(btn_frame, text="▶  Iniciar Servidor", font=("Segoe UI", 13, "bold"),
                                   bg="#00b894", fg="white", activebackground="#00a885",
                                   activeforeground="white", relief="flat", cursor="hand2",
                                   command=self._toggle_server, height=2)
        self.start_btn.pack(fill="x")

        # ── Log Area ──
        log_frame = tk.Frame(self.root, bg=self.BG)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(12, 16))

        tk.Label(log_frame, text="📋 Registro del servidor:", font=("Segoe UI", 9),
                 bg=self.BG, fg=self.FG_DIM).pack(anchor="w")

        self.log_area = scrolledtext.ScrolledText(log_frame, font=("Consolas", 9), height=8,
                                                   bg=self.BG_INPUT, fg=self.FG_DIM,
                                                   insertbackground=self.FG, relief="flat",
                                                   state="disabled", wrap="word",
                                                   selectbackground="#2a3a50")
        self.log_area.pack(fill="both", expand=True, pady=(4, 0))

    # ──────── Helpers ────────

    def _get_local_ip(self):
        """Get the LAN IP address of this machine."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return "127.0.0.1"

    def _log(self, message):
        """Append a message to the log area (thread-safe)."""
        def _append():
            self.log_area.config(state="normal")
            self.log_area.insert("end", message + "\n")
            self.log_area.see("end")
            self.log_area.config(state="disabled")
        self.root.after(0, _append)

    def _set_status(self, running):
        """Update GUI status indicators."""
        def _update():
            if running:
                self.status_label.config(text="● Funcionando", fg=self.ACCENT)
                self.start_btn.config(text="■  Detener Servidor", bg=self.ACCENT_RED,
                                      activebackground="#e0435a")
            else:
                self.status_label.config(text="● Detenido", fg=self.ACCENT_RED)
                self.start_btn.config(text="▶  Iniciar Servidor", bg="#00b894",
                                      activebackground="#00a885")
        self.root.after(0, _update)

    def _update_info(self, games=None, clients=None, game_name=None):
        """Update info cards (thread-safe)."""
        def _update():
            if games is not None:
                self.games_count.config(text=str(games))
            if clients is not None:
                self.clients_count.config(text=str(clients))
            if game_name is not None:
                self.game_name.config(text=game_name if game_name else "Ninguno")
        self.root.after(0, _update)

    # ──────── Server Control ────────

    def _toggle_server(self):
        if self.server_running:
            self._stop_server()
        else:
            self._start_server()

    def _start_server(self):
        if self.server_running:
            return

        from pathlib import Path
        CURRENT_DIR = Path(__file__).resolve().parent
        sys.path.insert(0, str(CURRENT_DIR))
        sys.path.insert(0, str(CURRENT_DIR.parent))

        try:
            from server.game_detector import GameDetector
            from server.virtual_controller import VirtualController
            from server.ws_server import CompanionServer
        except ImportError:
            from game_detector import GameDetector
            from virtual_controller import VirtualController
            from ws_server import CompanionServer

        self._log("[+] Iniciando servidor...")
        self.detector = GameDetector()
        if self.detector.steam_path:
            self._log(f"[+] Steam Path: {self.detector.steam_path}")
            self._log(f"[+] Juegos instalados: {len(self.detector.games_map)}")
            self._update_info(games=len(self.detector.games_map))
        else:
            self._log("[!] Steam no detectado. Detección en modo pasivo/manual.")
            self._update_info(games=0)

        self.controller = VirtualController()
        if self.controller.available:
            self._log(f"[+] Mando Virtual activo ({self.controller.backend})")
        else:
            err = f" ({self.controller.error_msg})" if getattr(self.controller, 'error_msg', '') else ""
            self._log(f"[!] Mando virtual NO inicializado{err}")
            if sys.platform == "win32":
                self._show_driver_install_banner()

        self.server = CompanionServer(
            host="0.0.0.0",
            http_port=8080,
            ws_port=8765,
            game_detector=self.detector,
            virtual_controller=self.controller
        )

        # Inject GUI callbacks into the server
        self.server._gui_log = self._log
        self.server._gui_update = self._update_info

        self.server_running = True
        self._set_status(True)
        self._log(f"[+] Servidor iniciado en {self._get_local_ip()}")
        self._log(f"    HTTP → http://0.0.0.0:8080")
        self._log(f"    WebSocket → ws://0.0.0.0:8765")

        self.server_thread = threading.Thread(target=self._run_server_loop, daemon=True)
        self.server_thread.start()

    def _run_server_loop(self):
        """Runs the async server in a background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.server.run())
        except Exception as e:
            self._log(f"[!] Error del servidor: {e}")
        finally:
            self.server_running = False
            self._set_status(False)
            self._log("[+] Servidor detenido.")

    def _stop_server(self):
        self._log("[+] Deteniendo servidor...")
        self.server_running = False
        self._set_status(False)
        # Server thread is daemon, will die with the app
        self._log("[+] Servidor detenido. Puedes cerrar la ventana.")

    # ──────── Driver Auto-Install (Windows ViGEmBus) ────────

    def _get_driver_installer_path(self):
        from pathlib import Path
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            p = Path(sys._MEIPASS) / "drivers" / "ViGEmBusSetup.exe"
        else:
            p = Path(__file__).resolve().parent.parent.parent / "drivers" / "ViGEmBusSetup.exe"
        return p if p.exists() else None

    def _show_driver_install_banner(self):
        if hasattr(self, 'driver_banner') and self.driver_banner:
            self.driver_banner.pack(fill="x", padx=20, pady=(10, 0), before=self.start_btn.master)
            return

        self.driver_banner = tk.Frame(self.root, bg="#2a161c", highlightbackground="#ff4d6a", highlightthickness=1)
        self.driver_banner.pack(fill="x", padx=20, pady=(10, 0), before=self.start_btn.master)

        content = tk.Frame(self.driver_banner, bg="#2a161c")
        content.pack(fill="x", padx=12, pady=10)

        left = tk.Frame(content, bg="#2a161c")
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="⚠️ Driver de Mando Xbox (ViGEmBus) no detectado",
                 font=("Segoe UI", 10, "bold"), bg="#2a161c", fg="#ff6b81").pack(anchor="w")
        tk.Label(left, text="Necesario para que Windows reconozca los controles de la Steam Deck en tus juegos.",
                 font=("Segoe UI", 8), bg="#2a161c", fg=self.FG_DIM).pack(anchor="w")

        btn = tk.Button(content, text="📥 Instalar Driver de Mando", font=("Segoe UI", 10, "bold"),
                        bg="#ff4d6a", fg="white", activebackground="#e84118", activeforeground="white",
                        relief="flat", cursor="hand2", command=self._install_driver, padx=12, pady=4)
        btn.pack(side="right")

    def _install_driver(self):
        installer = self._get_driver_installer_path()
        if not installer:
            self._log("[!] No se encontró el instalador local ViGEmBusSetup.exe.")
            self._log("    Descárgalo manualmente de: https://github.com/nefarius/ViGEmBus/releases")
            import webbrowser
            webbrowser.open("https://github.com/nefarius/ViGEmBus/releases/latest")
            return

        self._log("[+] Lanzando instalador oficial de ViGEmBus...")
        try:
            import subprocess
            subprocess.Popen([str(installer)])
            self._log("[+] Sigue los pasos del instalador de Windows (acepta permisos de Administrador).")
            self._log("[+] El servidor activará el mando automáticamente en cuanto termine la instalación.")
            self._poll_driver_installation()
        except Exception as e:
            self._log(f"[!] Error ejecutando instalador: {e}")

    def _poll_driver_installation(self, attempts=45):
        if not self.server_running or not self.controller:
            return
        if self.controller.reinit():
            if hasattr(self, 'driver_banner') and self.driver_banner:
                self.driver_banner.pack_forget()
            self._log("[+] ¡Driver ViGEmBus detectado con éxito! Mando Virtual Xbox 360 ACTIVO.")
            return
        if attempts > 0:
            self.root.after(2000, lambda: self._poll_driver_installation(attempts - 1))

    # ──────── Main Loop ────────

    def run(self):
        """Start the tkinter main loop."""
        # Auto-start server on launch
        self.root.after(500, self._start_server)

        # Periodic UI refresh for connected clients
        def _refresh_clients():
            if self.server and self.server_running:
                count = len(self.server.connected_clients) if hasattr(self.server, 'connected_clients') else 0
                game = self.server.current_game.get("name", "Ninguno") if self.server.current_game else "Ninguno"
                self._update_info(clients=count, game_name=game)
            self.root.after(2000, _refresh_clients)

        self.root.after(2000, _refresh_clients)
        self.root.mainloop()


def launch_gui():
    """Entry point for GUI mode."""
    gui = ServerGUI()
    gui.run()
