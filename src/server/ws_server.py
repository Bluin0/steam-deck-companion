"""
WebSocket & Static HTTP Server Module for Steam Deck Companion.
"""

import asyncio
import http.server
import json
import socketserver
import threading
from pathlib import Path
import websockets

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"
PROFILES_DIR = ROOT_DIR / "profiles"
NOTES_DIR = ROOT_DIR / "notes"

# Ensure notes and profiles directory exist
NOTES_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)

class CompanionServer:
    def __init__(self, host="0.0.0.0", http_port=8080, ws_port=8765, game_detector=None, virtual_controller=None):
        self.host = host
        self.http_port = http_port
        self.ws_port = ws_port
        self.game_detector = game_detector
        self.virtual_controller = virtual_controller

        self.connected_clients = set()
        self.current_game = None

    def start_http_server(self):
        """Runs built-in HTTP server serving client UI in a background thread."""
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, request, client_address, server):
                super().__init__(request, client_address, server, directory=str(CLIENT_DIR))
            def log_message(self, format, *args):
                pass # Silence HTTP log spam

        def _serve():
            with socketserver.TCPServer((self.host, self.http_port), QuietHandler) as httpd:
                print(f"[HTTP] Serving Steam Deck Companion UI on http://{self.host}:{self.http_port}")
                httpd.serve_forever()

        t = threading.Thread(target=_serve, daemon=True)
        t.start()

    def _get_installed_games(self):
        """Returns a sorted list of installed Steam games."""
        if not self.game_detector or not self.game_detector.games_map:
            return []
        
        seen_appids = set()
        games = []
        for info in self.game_detector.games_map.values():
            appid = info.get("appid")
            name = info.get("name")
            if appid and name and appid not in seen_appids:
                seen_appids.add(appid)
                games.append({"appid": appid, "name": name})
        
        return sorted(games, key=lambda x: x["name"].lower())

    def _load_profile(self, appid):
        """Loads game profile JSON or falls back to default.json."""
        if appid:
            profile_file = PROFILES_DIR / f"{appid}.json"
            if profile_file.exists():
                try:
                    with open(profile_file, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    print(f"[Profile] Error loading profile for {appid}: {e}")

        default_file = PROFILES_DIR / "default.json"
        if default_file.exists():
            try:
                with open(default_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "appid": "default",
            "name": "General Profile",
            "tabs": [
                {"id": "overview", "name": "Resumen", "icon": "📋", "type": "overview"},
                {"id": "hltb", "name": "HLTB", "icon": "⏱️", "type": "web", "url": "https://howlongtobeat.com"},
                {"id": "notes", "name": "Notas", "icon": "📝", "type": "notes"},
                {"id": "browser", "name": "Navegador", "icon": "🌐", "type": "web", "url": "https://www.google.com"}
            ]
        }

    def _get_notes(self, appid):
        """Retrieves saved scratchpad notes for a game."""
        notes_file = NOTES_DIR / f"{appid}.txt"
        if notes_file.exists():
            try:
                with open(notes_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return ""
        return ""

    def _save_notes(self, appid, content):
        """Saves scratchpad notes for a game."""
        notes_file = NOTES_DIR / f"{appid}.txt"
        try:
            with open(notes_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[Notes] Error saving notes for {appid}: {e}")
            return False

    async def _handle_ws_client(self, websocket):
        self.connected_clients.add(websocket)
        client_addr = websocket.remote_address
        print(f"[WS] Client connected: {client_addr}")

        appid = self.current_game.get("appid") if self.current_game else "default"

        # Send initial full state
        await websocket.send(json.dumps({
            "type": "init",
            "game": self.current_game,
            "profile": self._load_profile(appid),
            "notes": self._get_notes(appid),
            "installed_games": self._get_installed_games()
        }))

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "input" and self.virtual_controller:
                        self.virtual_controller.update_input(data.get("state", {}))
                    
                    elif msg_type == "save_notes":
                        target_appid = data.get("appid", "default")
                        content = data.get("content", "")
                        success = self._save_notes(target_appid, content)
                        await websocket.send(json.dumps({
                            "type": "notes_saved",
                            "appid": target_appid,
                            "success": success
                        }))

                    elif msg_type == "set_game_manual":
                        manual_appid = data.get("appid")
                        manual_name = data.get("name", "Manual Selection")
                        game_data = {
                            "appid": str(manual_appid),
                            "name": manual_name,
                            "pid": "manual",
                            "exe": "manual"
                        }
                        await self.broadcast_game_state(game_data)

                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            print(f"[WS] Client disconnected: {client_addr}")

    async def broadcast_game_state(self, game_info):
        """Broadcasts running game status & corresponding profile to all clients."""
        if self.current_game == game_info:
            return
        self.current_game = game_info
        print(f"[Server] Game state updated: {game_info['name'] if game_info else 'No game detected'}")

        if not self.connected_clients:
            return

        appid = self.current_game.get("appid") if self.current_game else "default"
        payload = json.dumps({
            "type": "game_update",
            "game": self.current_game,
            "profile": self._load_profile(appid),
            "notes": self._get_notes(appid)
        })

        await asyncio.gather(
            *[client.send(payload) for client in self.connected_clients],
            return_exceptions=True
        )

    async def poll_games_loop(self):
        """Background loop polling game detector every 3s."""
        while True:
            if self.game_detector:
                detected = self.game_detector.detect_running_game()
                if detected:
                    await self.broadcast_game_state(detected)
            await asyncio.sleep(3)

    async def run(self):
        self.start_http_server()
        print(f"[WS] Starting WebSocket server on ws://{self.host}:{self.ws_port}")
        async with websockets.serve(self._handle_ws_client, self.host, self.ws_port):
            await self.poll_games_loop()
