# Steam Deck Companion — Prototypes

Throwaway prototypes that validate core technical hypotheses for the Steam Deck Companion project.

## Prerequisites

```bash
pip install psutil websockets vgamepad
```

**ViGEmBus driver** (required for P0.3):  
https://github.com/nefarius/ViGEmBus/releases  
Download and install the latest `ViGEmBus_Setup_x64.msi`.

---

## P0.1 — Game Detection (`p01_game_detection.py`)

**Question:** Can we detect which Steam game is currently running on a Windows PC?

**How it works:**
1. Reads Steam install path from Windows registry
2. Parses `libraryfolders.vdf` + `appmanifest_*.acf` to build a game map
3. Cross-references running processes (via `psutil`) against Steam library directories
4. Polls every 3 seconds

**Run:**
```bash
python p01_game_detection.py
```

**Expected output:**
```
Steam path: C:\Program Files (x86)\Steam
Library folders: ['C:\\Program Files (x86)\\Steam', 'D:\\SteamLibrary']
Found 47 installed games

Polling for running games every 3s... (Ctrl+C to stop)

  🎮 Half-Life 2 (AppID: 220, PID: 12345)
```

If no game is running, it prints `(no Steam games detected)`.

---

## P0.2 — WebSocket + Gamepad API (`p02_websocket_gamepad/`)

**Question:** Can a browser on the Steam Deck capture gamepad input via the Gamepad API and stream it to the PC over WebSocket?

**Components:**
- `server.py` — HTTP server (port 8080) + WebSocket server (port 8765)
- `index.html` — Gamepad API client with visual button/axis display

**Run:**
```bash
cd p02_websocket_gamepad
python server.py
```

Then open `http://<your-pc-ip>:8080` in any browser (or on the Steam Deck).

**Expected output (server console):**
```
[HTTP] Serving on http://0.0.0.0:8080
[WS] WebSocket server on ws://0.0.0.0:8765
[WS] Client connected: ('192.168.1.50', 54321)
  Buttons: [0, 2]  |  Axes: A0:+0.50 A1:-0.30 A2:+0.00 A3:+0.00
```

**Expected output (browser):**
- Dark themed page showing button grid and axis bars
- Buttons light up blue when pressed
- Axis bars move in real time

---

## P0.3 — Virtual Controller (`p03_virtual_controller.py`)

**Question:** Can we programmatically create a virtual Xbox 360 controller on Windows?

**Run:**
```bash
python p03_virtual_controller.py
```

Open https://gamepad-tester.com in a browser **before** running to watch the virtual controller appear and cycle through inputs.

**Expected output:**
```
[+] Virtual Xbox 360 controller created.

  [ 1/16] Press A button
  [ 2/16] Release A button
  [ 3/16] Press B button
  ...

[+] Done. Virtual controller cleaned up.
```

The gamepad tester site should show buttons lighting up and sticks moving.

---

## P0.4 — Steam Deck Integration Test (Manual)

**Question:** Does the full pipeline work? (Deck gamepad → browser → WebSocket → PC)

**This is a manual test. No script needed.**

### Steps:
1. On the **PC**: Run `python p02_websocket_gamepad/server.py`
2. On the **Steam Deck**: Switch to **Desktop Mode**
3. Open a browser (Firefox/Chrome) and navigate to `http://<pc-ip>:8080`
4. Press buttons / move sticks on the Deck
5. Verify that:
   - The HTML page shows button presses and axis movement
   - The PC server console prints the received input
   - Latency feels acceptable (< 50ms subjectively)

### Notes:
- Both devices must be on the same network
- If the Steam Deck is in **Gaming Mode**, the built-in browser may not expose the Gamepad API — Desktop Mode is the safe bet for this test
- Firewall on the PC may need ports 8080 and 8765 opened

---

## What's Next

If all four prototypes succeed, we've validated:
- ✅ Game detection on the PC
- ✅ Gamepad capture in the browser
- ✅ Real-time WebSocket transport
- ✅ Virtual controller injection on the PC
- ✅ End-to-end: Deck → browser → WebSocket → PC

The next step is to wire them together: Deck gamepad input → WebSocket → virtual controller on PC, matched to the detected running game.
