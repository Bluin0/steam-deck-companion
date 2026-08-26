#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# ── Setup Python environment ──
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="python3"

if ! "$PYTHON_BIN" -c "import websockets, psutil" 2>/dev/null; then
    if [ ! -f "$VENV_DIR/bin/python3" ]; then
        python3 -m venv "$VENV_DIR" 2>/dev/null || true
    fi
    if [ -f "$VENV_DIR/bin/python3" ]; then
        "$VENV_DIR/bin/python3" -m pip install --quiet --upgrade pip 2>/dev/null || true
        "$VENV_DIR/bin/python3" -m pip install --quiet -r "$ROOT_DIR/requirements.txt" 2>/dev/null || true
        PYTHON_BIN="$VENV_DIR/bin/python3"
    else
        python3 -m pip install --user --quiet -r "$ROOT_DIR/requirements.txt" 2>/dev/null || \
        pip3 install --user --quiet -r "$ROOT_DIR/requirements.txt" 2>/dev/null || true
    fi
fi

# ── Launch server (GUI or headless) ──
"$PYTHON_BIN" src/server/main.py "$@"
