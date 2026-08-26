"""
Main entry point for Steam Deck Companion PC Server.
Launches with GUI by default. Use --headless for terminal-only mode.
"""

import asyncio
import sys
from pathlib import Path

# Ensure src module resolution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main_headless():
    """Run server in headless/terminal mode (no GUI)."""
    from server.game_detector import GameDetector
    from server.virtual_controller import VirtualController
    from server.ws_server import CompanionServer

    print("==========================================")
    print("      STEAM DECK COMPANION SERVER         ")
    print("==========================================")

    detector = GameDetector()
    if detector.steam_path:
        print(f"[+] Steam Path: {detector.steam_path}")
        print(f"[+] Installed Games Found: {len(detector.games_map)}")
    else:
        print("[!] Steam Path not automatically found. Game detection will run in passive/manual mode.")

    controller = VirtualController()

    server = CompanionServer(
        host="0.0.0.0",
        http_port=8080,
        ws_port=8765,
        game_detector=detector,
        virtual_controller=controller
    )

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n[+] Server shut down gracefully.")


def main_gui():
    """Run server with desktop GUI."""
    from server.gui import launch_gui
    launch_gui()


def main():
    if "--headless" in sys.argv or "--no-gui" in sys.argv:
        main_headless()
    else:
        try:
            main_gui()
        except ImportError:
            print("[!] GUI no disponible (tkinter no instalado). Iniciando en modo terminal...")
            print("    Para instalar tkinter: sudo apt install python3-tk")
            main_headless()
        except Exception as e:
            print(f"[!] Error al abrir GUI ({e}). Iniciando en modo terminal...")
            main_headless()


if __name__ == "__main__":
    main()
