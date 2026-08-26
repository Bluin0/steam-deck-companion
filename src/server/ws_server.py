"""
WebSocket & Static HTTP Server Module for Steam Deck Companion.
"""

import asyncio
import http.server
import json
import socketserver
import threading
import sys
from pathlib import Path
import websockets

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BUNDLE_DIR = Path(sys._MEIPASS)
    ROOT_DIR = Path(sys.executable).parent
    CLIENT_DIR = BUNDLE_DIR / "src" / "client"
    PROFILES_DIR = BUNDLE_DIR / "profiles"
else:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"
    PROFILES_DIR = ROOT_DIR / "profiles"

NOTES_DIR = ROOT_DIR / "notes"

# Ensure notes and profiles directory exist
NOTES_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)

import urllib.parse
import urllib.request

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

            def end_headers(self):
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                super().end_headers()

            def do_GET(self):
                # Proxy to strip X-Frame-Options and CSP for web viewer
                if self.path.startswith('/proxy?url='):
                    target_url = urllib.parse.unquote(self.path[len('/proxy?url='):])
                    try:
                        req = urllib.request.Request(
                            target_url,
                            headers={"User-Agent": "Mozilla/5.0 (X11; SteamOS; Linux x86_64) AppleWebKit/537.36"}
                        )
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            content = resp.read()
                            content_type = resp.headers.get("Content-Type", "text/html; charset=utf-8")
                            
                            # Inject base tag for relative links
                            if "text/html" in content_type:
                                base_tag = f'<base href="{target_url}">'
                                if b'<head>' in content:
                                    content = content.replace(b'<head>', b'<head>' + base_tag.encode('utf-8'))
                                elif b'<HEAD>' in content:
                                    content = content.replace(b'<HEAD>', b'<HEAD>' + base_tag.encode('utf-8'))
                            
                            self.send_response(200)
                            self.send_header("Content-Type", content_type)
                            self.send_header("Access-Control-Allow-Origin", "*")
                            self.end_headers()
                            self.wfile.write(content)
                            return
                    except Exception as e:
                        self.send_response(502)
                        self.send_header("Content-Type", "text/html; charset=utf-8")
                        self.end_headers()
                        err_html = f"<html><body style='background:#0f141c;color:#f0f4f8;font-family:sans-serif;padding:2rem;text-align:center;'><h3>No se pudo cargar la vista embebida</h3><p>{e}</p></body></html>"
                        self.wfile.write(err_html.encode('utf-8'))
                        return
                elif self.path.startswith('/api/search_games?q='):
                    query = urllib.parse.unquote(self.path[len('/api/search_games?q='):])
                    try:
                        steam_url = f"https://store.steampowered.com/api/storesearch/?term={urllib.parse.quote(query)}&l=spanish&cc=ES"
                        req = urllib.request.Request(
                            steam_url,
                            headers={"User-Agent": "Mozilla/5.0"}
                        )
                        with urllib.request.urlopen(req, timeout=6) as resp:
                            data = json.loads(resp.read().decode('utf-8'))
                            items = [
                                {
                                    "appid": str(item["id"]),
                                    "name": item["name"],
                                    "img": item.get("tiny_image", "")
                                }
                                for item in data.get("items", [])
                            ]
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json; charset=utf-8")
                            self.send_header("Access-Control-Allow-Origin", "*")
                            self.end_headers()
                            self.wfile.write(json.dumps(items).encode('utf-8'))
                            return
                    except Exception:
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(b"[]")
                        return
                super().do_GET()

        class ReusableTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        def _serve():
            try:
                with ReusableTCPServer((self.host, self.http_port), QuietHandler) as httpd:
                    print(f"[HTTP] Serving Steam Deck Companion UI on http://{self.host}:{self.http_port}")
                    httpd.serve_forever()
            except Exception as e:
                print(f"[HTTP] Could not bind to port {self.http_port}: {e}")

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
                {"id": "map", "name": "Mapa", "icon": "🗺️", "type": "web", "url": "https://mapgenie.io/{game_slug}"},
                {"id": "wiki", "name": "Guías", "icon": "📖", "type": "web", "url": "https://steamcommunity.com/app/{appid}/guides/"},
                {"id": "hltb", "name": "HLTB", "icon": "⏱️", "type": "web", "url": "https://howlongtobeat.com/?q={game_name}"},
                {"id": "notes", "name": "Notas", "icon": "📝", "type": "notes"},
                {"id": "inputs", "name": "Mando", "icon": "🎮", "type": "inputs"},
                {"id": "browser", "name": "Google", "icon": "🌐", "type": "web", "url": "https://www.google.com"}
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
