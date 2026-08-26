"""
Game Detector Module for Steam Deck Companion.

Enumerates running processes via psutil and matches them against installed Steam games.
Cross-platform support for Windows and Linux.
"""

import os
import re
import sys
import time
import psutil
from pathlib import Path

class GameDetector:
    def __init__(self):
        self.steam_path = self._get_steam_path()
        self.library_folders = self._get_library_folders() if self.steam_path else []
        self.games_map = self._build_games_map() if self.library_folders else {}

    def _get_steam_path(self):
        """Resolves Steam installation path on Windows and Linux."""
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                path, _ = winreg.QueryValueEx(key, "SteamPath")
                winreg.CloseKey(key)
                return Path(path)
            except Exception:
                default_win = Path(r"C:\Program Files (x86)\Steam")
                return default_win if default_win.exists() else None
        else:
            # Linux Steam standard and Flatpak paths
            home = Path.home()
            linux_paths = [
                home / ".local" / "share" / "Steam",
                home / ".steam" / "steam",
                home / ".steam" / "root",
                home / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam",
                home / ".var" / "app" / "com.valvesoftware.Steam" / ".steam" / "steam"
            ]
            for p in linux_paths:
                if p.exists():
                    return p
            return None

    def _parse_vdf_value(self, line):
        parts = re.findall(r'"([^"]*)"', line)
        if len(parts) >= 2:
            return parts[0], parts[1]
        return None, None

    def _get_library_folders(self):
        if not self.steam_path:
            return []

        vdf_path = self.steam_path / "steamapps" / "libraryfolders.vdf"
        folders = [self.steam_path / "steamapps"]

        if not vdf_path.exists():
            return folders

        try:
            with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    k, v = self._parse_vdf_value(line)
                    if k == "path" and v:
                        lib_path = Path(v) / "steamapps"
                        if lib_path.exists() and lib_path not in folders:
                            folders.append(lib_path)
        except Exception as e:
            print(f"[GameDetector] Error parsing libraryfolders.vdf: {e}")

        return folders

    def _build_games_map(self):
        """Builds a map of {installdir_name_lowercase: {'appid': appid, 'name': name}}"""
        games = {}
        for lib in self.library_folders:
            if not lib.exists():
                continue
            for acf_file in lib.glob("appmanifest_*.acf"):
                try:
                    appid = None
                    name = None
                    installdir = None
                    with open(acf_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            k, v = self._parse_vdf_value(line)
                            if k == "appid":
                                appid = v
                            elif k == "name":
                                name = v
                            elif k == "installdir":
                                installdir = v

                    if appid and name and installdir:
                        games[installdir.lower()] = {
                            "appid": appid,
                            "name": name,
                            "installdir": installdir,
                            "library": str(lib)
                        }
                except Exception:
                    continue
        return games

    def detect_running_game(self):
        """Scans running processes and returns dict with game info or None."""
        if not self.games_map:
            return None

        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    exe = proc.info.get('exe') or ''
                    cmdline = ' '.join(proc.info.get('cmdline') or [])
                    search_str = f"{exe} {cmdline}".lower()

                    for installdir, info in self.games_map.items():
                        if f"\\{installdir}\\" in search_str or f"/{installdir}/" in search_str or f"/{installdir} " in search_str:
                            return {
                                "appid": info["appid"],
                                "name": info["name"],
                                "pid": proc.info["pid"],
                                "exe": proc.info["name"]
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"[GameDetector] Polling error: {e}")

        return None
