"""Etkinlik Radarı — desktop entry point (`etkinlik-radari` or `python -m etkinlik_radari`)."""
import argparse
import sys
from pathlib import Path

import webview

from . import __version__, paths
from .backend.api import Api


def main():
    parser = argparse.ArgumentParser(prog="etkinlik-radari", description="Etkinlik Radarı masaüstü uygulaması")
    parser.add_argument("--debug", action="store_true", help="geliştirici araçlarını aç")
    parser.add_argument("--data-dir", help="veritabanı klasörü (varsayılan: kullanıcı veri klasörü)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else paths.data_dir()
    paths.migrate_legacy_data(data_dir)
    api = Api(data_dir)
    webview.create_window(
        "Etkinlik Radarı", str(paths.UI_DIR / "index.html"), js_api=api,
        width=1440, height=920, min_size=(1040, 680), background_color="#100F0F",
    )
    # WinForms (Windows) needs an .ico; GTK/Qt take the PNG; macOS uses the .app bundle's icon
    icon = paths.ASSETS_DIR / ("icon.ico" if sys.platform == "win32" else "icon.png")
    webview.start(http_server=True, debug=args.debug, icon=str(icon) if icon.exists() else None)


if __name__ == "__main__":
    sys.exit(main())
