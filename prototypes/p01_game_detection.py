"""
P0.1 — Steam Game Detection Prototype
======================================
VALIDATES: Can we detect which Steam game is running on a Windows PC?

Strategy:
  1. Read Steam install path from Windows registry
  2. Parse libraryfolders.vdf to find all Steam library paths
  3. Parse appmanifest_*.acf files to build installdir -> {appid, name} map
  4. Use psutil to check if any running process lives inside a Steam library
  5. Poll every 3 seconds

Prerequisites: pip install psutil
Platform: Windows only
"""

import sys
import os
import re
import time
import glob

try:
    import psutil
except ImportError:
    sys.exit("ERROR: pip install psutil")

# --- Minimal VDF/ACF parser (Valve KeyValue format) ---

def parse_vdf(text):
    """Parse Valve's KeyValue format into nested dicts. Good enough for manifests."""
    tokens = re.findall(r'"([^"]*)"|\{|\}', text)
    stack = [{}]
    key = None
    for tok in tokens:
        if tok == '{':
            new = {}
            stack[-1][key] = new
            stack.append(new)
            key = None
        elif tok == '}':
            stack.pop()
        elif key is None:
            key = tok.lower()  # normalize keys to lowercase
        else:
            stack[-1][key] = tok
            key = None
    return stack[0]


def get_steam_path():
    """Get Steam install path from Windows registry."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        val, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        return val.replace("/", "\\")
    except Exception as e:
        print(f"[WARN] Registry lookup failed: {e}")
        # Fallback: common default
        default = r"C:\Program Files (x86)\Steam"
        if os.path.isdir(default):
            return default
        return None


def get_library_paths(steam_path):
    """Parse libraryfolders.vdf to get all Steam library directories."""
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if not os.path.isfile(vdf_path):
        print(f"[WARN] Not found: {vdf_path}")
        return [steam_path]

    with open(vdf_path, "r", encoding="utf-8", errors="replace") as f:
        data = parse_vdf(f.read())

    paths = [steam_path]  # always include main install
    # libraryfolders -> "0", "1", ... -> "path"
    lf = data.get("libraryfolders", {})
    for _key, entry in lf.items():
        if isinstance(entry, dict) and "path" in entry:
            p = entry["path"].replace("\\\\", "\\")
            if p not in paths:
                paths.append(p)
    return paths


def build_game_map(library_paths):
    """Parse appmanifest_*.acf files. Returns {normalized_common_path: {appid, name}}."""
    game_map = {}
    for lib in library_paths:
        steamapps = os.path.join(lib, "steamapps")
        pattern = os.path.join(steamapps, "appmanifest_*.acf")
        for acf_path in glob.glob(pattern):
            try:
                with open(acf_path, "r", encoding="utf-8", errors="replace") as f:
                    data = parse_vdf(f.read())
                state = data.get("appstate", {})
                appid = state.get("appid", "?")
                name = state.get("name", "Unknown")
                installdir = state.get("installdir", "")
                if installdir:
                    game_dir = os.path.join(steamapps, "common", installdir)
                    game_map[os.path.normcase(os.path.normpath(game_dir))] = {
                        "appid": appid, "name": name
                    }
            except Exception as e:
                print(f"[WARN] Failed to parse {acf_path}: {e}")
    return game_map


def detect_running_games(game_map):
    """Check running processes against known Steam game directories."""
    found = []
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            exe = proc.info.get("exe")
            if not exe:
                continue
            exe_norm = os.path.normcase(os.path.normpath(exe))
            for game_dir, info in game_map.items():
                if exe_norm.startswith(game_dir):
                    found.append({**info, "exe": exe, "pid": proc.info["pid"]})
                    break
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return found


def main():
    print("=== P0.1: Steam Game Detection ===\n")

    steam_path = get_steam_path()
    if not steam_path:
        sys.exit("ERROR: Could not find Steam installation.")
    print(f"Steam path: {steam_path}")

    libraries = get_library_paths(steam_path)
    print(f"Library folders: {libraries}")

    game_map = build_game_map(libraries)
    print(f"Found {len(game_map)} installed games\n")

    print("Polling for running games every 3s... (Ctrl+C to stop)\n")
    try:
        while True:
            running = detect_running_games(game_map)
            if running:
                for g in running:
                    print(f"  🎮 {g['name']} (AppID: {g['appid']}, PID: {g['pid']})")
            else:
                print("  (no Steam games detected)")
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
