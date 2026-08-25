"""
P0.2 — WebSocket + Gamepad API Server
======================================
VALIDATES: Can a browser on the Steam Deck capture gamepad input and send it
           to a PC over WebSocket in real time?

Runs two things:
  - HTTP server on port 8080 serving index.html
  - WebSocket server on port 8765 receiving gamepad input JSON

Prerequisites: pip install websockets
Usage: python server.py   (then open http://<your-ip>:8080 on the Deck)
"""

import asyncio
import os
import http.server
import threading
import json

try:
    import websockets
except ImportError:
    import sys; sys.exit("ERROR: pip install websockets")

HTML_DIR = os.path.dirname(os.path.abspath(__file__))
HTTP_PORT = 8080
WS_PORT = 8765


# --- Simple HTTP server for index.html (runs in a thread) ---

def start_http_server():
    os.chdir(HTML_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("0.0.0.0", HTTP_PORT), handler)
    print(f"[HTTP] Serving on http://0.0.0.0:{HTTP_PORT}")
    httpd.serve_forever()


# --- WebSocket handler ---

PREV_STATE = {}  # track per-client to reduce spam

async def handle_client(websocket):
    addr = websocket.remote_address
    print(f"[WS] Client connected: {addr}")
    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("type") == "input":
                buttons = msg.get("buttons", [])
                axes = msg.get("axes", [])
                pressed = [i for i, b in enumerate(buttons) if b]
                axis_str = " ".join(f"A{i}:{v:+.2f}" for i, v in enumerate(axes))
                if pressed:
                    print(f"  Buttons: {pressed}  |  Axes: {axis_str}")
                else:
                    print(f"  Buttons: (none)   |  Axes: {axis_str}")
    except websockets.ConnectionClosed:
        pass
    print(f"[WS] Client disconnected: {addr}")


async def start_ws_server():
    print(f"[WS] WebSocket server on ws://0.0.0.0:{WS_PORT}")
    async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
        await asyncio.Future()  # run forever


def main():
    print("=== P0.2: WebSocket + Gamepad Server ===\n")

    # HTTP in a daemon thread
    t = threading.Thread(target=start_http_server, daemon=True)
    t.start()

    # WebSocket in asyncio
    try:
        asyncio.run(start_ws_server())
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
