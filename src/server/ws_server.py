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

CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"

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
            def __init__(*args, **kwargs):
                super().__init__(*args, directory=str(CLIENT_DIR), **kwargs)
            def log_message(self, format, *args):
                pass # Silence HTTP log spam

        def _serve():
            with socketserver.TCPServer((self.host, self.http_port), QuietHandler) as httpd:
                print(f"[HTTP] Serving Steam Deck Companion UI on http://{self.host}:{self.http_port}")
                httpd.serve_forever()

        t = threading.Thread(target=_serve, daemon=True)
        t.start()

    async def _handle_ws_client(self, websocket):
        self.connected_clients.add(websocket)
        client_addr = websocket.remote_address
        print(f"[WS] Client connected: {client_addr}")

        # Send initial state
        await websocket.send(json.dumps({
            "type": "game_update",
            "game": self.current_game
        }))

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    if msg_type == "input" and self.virtual_controller:
                        self.virtual_controller.update_input(data.get("state", {}))
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            print(f"[WS] Client disconnected: {client_addr}")

    async def broadcast_game_state(self, game_info):
        """Broadcasts running game status change to all connected clients."""
        if self.current_game == game_info:
            return
        self.current_game = game_info
        print(f"[Server] Game state updated: {game_info['name'] if game_info else 'No game detected'}")

        if not self.connected_clients:
            return

        payload = json.dumps({
            "type": "game_update",
            "game": self.current_game
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
                await self.broadcast_game_state(detected)
            await asyncio.sleep(3)

    async def run(self):
        self.start_http_server()
        print(f"[WS] Starting WebSocket server on ws://{self.host}:{self.ws_port}")
        async with websockets.serve(self._handle_ws_client, self.host, self.ws_port):
            await self.poll_games_loop()
