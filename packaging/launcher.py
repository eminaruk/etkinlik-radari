"""Entry script for the frozen Windows build (PyInstaller needs a file, not a console-script entry point)."""
import sys

from etkinlik_radari.app import main

if __name__ == "__main__":
    sys.exit(main())
