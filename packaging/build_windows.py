"""Build the Windows installer: PyInstaller (one-folder app) -> Inno Setup (setup wizard).

    python -m pip install . pyinstaller
    python packaging/build_windows.py            # -> dist/EtkinlikRadari-<version>-Setup.exe

Needs Inno Setup 6 (https://jrsoftware.org/isdl.php, or `winget install JRSoftware.InnoSetup`).
Pass --iscc PATH if ISCC.exe is not in a standard location, --no-installer to stop after PyInstaller.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGING = ROOT / "packaging"


def version() -> str:
    text = (ROOT / "etkinlik_radari" / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__\s*=\s*"([^"]+)"', text).group(1)


def find_iscc(given: str | None) -> Path | None:
    if given:
        return Path(given)
    found = shutil.which("ISCC")
    if found:
        return Path(found)
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
        for sub in ("Inno Setup 6", r"Programs\Inno Setup 6"):
            p = Path(base or "") / sub / "ISCC.exe"
            if base and p.is_file():
                return p
    return None


def main():
    if sys.platform != "win32":
        sys.exit("The installer is Windows-only; on macOS/Linux use install.py.")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--iscc", help="path to ISCC.exe")
    ap.add_argument("--no-installer", action="store_true", help="only build dist/EtkinlikRadari with PyInstaller")
    args = ap.parse_args()
    ver = version()

    print(f"[1/2] PyInstaller - Etkinlik Radari {ver}")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", str(ROOT / "dist"), "--workpath", str(ROOT / "build" / "pyinstaller"),
                    str(PACKAGING / "etkinlik-radari.spec")], check=True, cwd=ROOT)
    if args.no_installer:
        print(f"Done: {ROOT / 'dist' / 'EtkinlikRadari'}")
        return

    iscc = find_iscc(args.iscc)
    if not iscc:
        sys.exit("ISCC.exe not found. Install Inno Setup 6 or pass --iscc.")
    print(f"[2/2] Inno Setup - {iscc}")
    subprocess.run([str(iscc), f"/DAppVersion={ver}", str(PACKAGING / "installer.iss")], check=True, cwd=PACKAGING)
    print(f"Done: {ROOT / 'dist' / f'EtkinlikRadari-{ver}-Setup.exe'}")


if __name__ == "__main__":
    main()
