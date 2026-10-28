"""Per-user locations, following each OS's convention."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_DIR_NAME = "EtkinlikRadari"
PACKAGE_DIR = Path(__file__).resolve().parent
UI_DIR = PACKAGE_DIR / "ui"
ASSETS_DIR = PACKAGE_DIR / "assets"


def data_dir() -> Path:
    """Windows: %APPDATA%\\EtkinlikRadari · macOS: ~/Library/Application Support/EtkinlikRadari ·
    Linux: $XDG_DATA_HOME/etkinlik-radari (~/.local/share). ETKINLIK_RADARI_DATA overrides it."""
    override = os.environ.get("ETKINLIK_RADARI_DATA")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / APP_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "etkinlik-radari"


def downloads_dir() -> Path:
    d = Path.home() / "Downloads"
    if sys.platform.startswith("linux"):
        try:  # honours localised folders such as ~/İndirilenler
            out = subprocess.run(["xdg-user-dir", "DOWNLOAD"], capture_output=True, text=True, timeout=3)
            if out.returncode == 0 and out.stdout.strip():
                d = Path(out.stdout.strip())
        except (OSError, subprocess.SubprocessError):
            pass
    return d if d.is_dir() else Path.home()


def open_with_default_app(path: Path):
    try:
        if sys.platform == "win32":
            os.startfile(str(path))  # noqa: S606 - opening a file we just wrote
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except OSError:
        pass


def migrate_legacy_data(target: Path):
    """Early versions kept the database in <repo>/data/radar.db; move it to the per-user location once."""
    legacy = PACKAGE_DIR.parent / "data" / "radar.db"
    new = target / "radar.db"
    if legacy.is_file() and not new.exists():
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy, new)
