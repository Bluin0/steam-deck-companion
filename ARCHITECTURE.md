# Steam Deck Companion — Architecture

> Living document. Updated as decisions are made.
> Last updated: 2026-08-25

## Objective

Use a Steam Deck as a companion device for PC gaming:
1. **Second screen** — contextual info for the running game
2. **Controller** — forward gamepad input to the PC

The game runs on the PC. The Deck does NOT stream the game.

## Scope

### MVP (v0.1)
- Deck connects to PC over LAN
- PC detects which Steam game is running
- Deck displays game name/info
- Deck forwards gamepad input → PC virtual controller
- Basic mode switching (UI mode vs game mode)

### Not in MVP
- Non-Steam games
- Modules (wiki, maps, guides, YouTube, etc.)
- Trackpad/gyro as game input
- Vibration/haptics
- Multi-client
- Mobile/tablet support
- Security beyond basic pairing

## Architecture

```
STEAM DECK (Client)                    PC (Server)
┌────────────────────────┐      ┌─────────────────────────────┐
│ Browser (non-Steam)    │      │ Python Server               │
│ ┌────────────────────┐ │      │ ┌─────────────────────────┐ │
│ │ Web App (HTML/JS)  │◄├─WS──►│ │ WebSocket Server        │ │
│ │ - UI               │ │      │ │ - Game Detector         │ │
│ │ - Gamepad Capture  │ │      │ │ - Virtual Input (ViGEm) │ │
│ │ - Mode Switcher    │ │      │ │ - HTTP Static Server    │ │
│ └────────────────────┘ │      │ └─────────────────────────┘ │
└────────────────────────┘      └─────────────────────────────┘
```

### Why This Architecture
- **Browser as client**: No compilation for SteamOS. Gamepad API covers buttons/sticks. Served by PC server.
- **Python server**: Fast to prototype. Libraries available for everything needed.
- **Single WebSocket**: Handles game state, input, and companion content. No REST API needed.
- **No database**: Game profiles are JSON files on disk.
- **No build step**: Plain HTML/CSS/JS. No React, no bundler.

## Components

### Game Detection (PC)
- **Strategy**: Enumerate running processes (psutil) → match against Steam appmanifest files → resolve AppID + name
- **Fallback**: Manual selection on Deck
- **Polling interval**: ~3 seconds

> ⚠️ Steam's `RunningAppID` registry key is deprecated/unreliable. Do NOT depend on it.

### Communication
- **Protocol**: WebSocket (JSON messages)
- **Discovery**: mDNS (python-zeroconf) or manual IP entry
- **Latency**: ~1-4ms over Wi-Fi LAN (acceptable for gamepad input)
- **Reconnection**: Basic auto-reconnect on disconnect

### Virtual Input (PC, Windows)
- **Library**: vgamepad (wraps ViGEmBus)
- **Prerequisite**: ViGEmBus driver installed on Windows
- **Device**: Virtual Xbox 360 controller

### Input Mode Switching (Deck)
- **Problem**: Same physical controls must navigate UI OR control game
- **Solution**: TBD — requires prototype validation
- **Candidate**: Dedicated button combo (e.g., back grip) toggles mode

## Technologies

| Component | Technology | Justification |
|---|---|---|
| PC Server | Python 3.10+ | Fast prototyping, cross-platform, good library ecosystem |
| WebSocket | `websockets` (Python) | Simple, async, well-maintained |
| Game Detection | `psutil` + VDF file parsing | No external API needed, works offline |
| Virtual Controller | `vgamepad` (ViGEmBus) | Standard for virtual Xbox controllers on Windows |
| Device Discovery | `python-zeroconf` | Pure Python mDNS, no external deps |
| Deck Client | Browser (Chrome/Firefox) | No compilation, Gamepad API, served from PC |
| Deck UI | HTML/CSS/JS (vanilla) | No build step, minimal resource usage |

## Decisions

| Decision | Rationale | Date |
|---|---|---|
| Browser as Deck client (not native app) | Avoids compilation for SteamOS, Gamepad API sufficient for MVP | 2026-08-25 |
| Python server (not Node/Rust/C#) | Fastest to prototype, good library coverage | 2026-08-25 |
| Process enum for game detection (not registry) | RunningAppID is deprecated in current Steam | 2026-08-25 |
| Separate companion/input phases | Validates concept before tackling hardest problem | 2026-08-25 |
| Desktop Mode for initial prototyping | Easier to test, Gaming Mode later | 2026-08-25 |
| ViGEmBus for virtual controller | Industry standard, used by DS4Windows/Sunshine | 2026-08-25 |

## Decisions Descartadas

| Decision | Why Rejected |
|---|---|
| Decky Loader plugin | UI limited to QAM side panel, fragile against Steam updates |
| Native app on Deck | Unnecessary complexity for MVP, browser is sufficient |
| Steam Web API for game detection | Requires internet + API key for a local feature |
| React/Vue for Deck UI | Unnecessary build complexity, vanilla JS sufficient |

## Known Issues

- ViGEmBus original project archived (Nov 2023). Final build v1.21.442 still works. Monitor community forks.
- Trackpad/gyro not accessible via browser Gamepad API (only via Steam Input mouse mapping)
- SteamOS immutable root filesystem — all persistence must be in `/home`

## Current State

**Phase 0: Validation Prototypes** — In progress

## Roadmap

1. ✅ Phase 0: Validation prototypes (game detection, WebSocket, virtual controller, Deck test)
2. ⬜ Phase 1: First vertical slice (connect → detect game → show on Deck)
3. ⬜ Phase 2: Input forwarding (Deck → PC → virtual controller → game)
4. ⬜ Phase 3: Basic companion UI (game profiles, manual selection)
5. ⬜ Phase 4+: Modules, polish (deferred)
