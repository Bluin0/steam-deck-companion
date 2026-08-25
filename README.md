# Steam Deck Companion

Use a Steam Deck as a second screen & gamepad controller for PC gaming over LAN.

## Highlights
- **Second Screen Companion**: Automatically detects the running Steam game on your PC and displays context-aware info/companion tools on the Deck screen.
- **Gamepad Forwarding**: Streams physical Steam Deck controls over WebSocket to a virtual Xbox 360 controller (ViGEmBus) on the PC.
- **No SteamOS modification required**: Client runs inside the Deck browser; PC host runs a lightweight Python server.

## Quickstart

### Prerequisites (PC Host - Windows)
1. Python 3.10+
2. [ViGEmBus Driver](https://github.com/nefarius/ViGEmBus/releases) installed on Windows.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server (PC)
```bash
python src/server/main.py
```

### Connecting from Steam Deck
1. Switch Steam Deck to Desktop Mode (or open browser).
2. Open Chrome/Firefox and navigate to:
   ```
   http://<PC-IP-ADDRESS>:8080
   ```

---

## Architecture & Prototypes

See [ARCHITECTURE.md](ARCHITECTURE.md) for technical design details, decisions, and roadmap.
Validation prototypes are available under [`prototypes/`](prototypes/).
