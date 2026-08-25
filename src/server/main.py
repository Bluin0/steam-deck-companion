"""
Main entry point for Steam Deck Companion PC Server.
"""

import asyncio
import sys
from pathlib import Path

# Ensure src module resolution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.game_detector import GameDetector
from server.virtual_controller import VirtualController
from server.ws_server import CompanionServer

def main():
    print("==========================================")
    print("      STEAM DECK COMPANION SERVER         ")
    print("==========================================")

    detector = GameDetector()
    if detector.steam_path:
        print(f"[+] Steam Path: {detector.steam_path}")
        print(f"[+] Installed Games Found: {len(detector.games_map)}")
    else:
        print("[!] Steam Path not found (or non-Windows OS). Game detection will run in passive mode.")

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

if __name__ == "__main__":
    main()
