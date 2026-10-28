# PyInstaller spec for the Windows build: a windowed, one-folder app that Inno Setup then wraps in an installer.
# Run through packaging/build_windows.py, or directly: pyinstaller packaging/etkinlik-radari.spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent
ICON = ROOT / "etkinlik_radari" / "assets" / "icon.ico"

a = Analysis(
    [str(ROOT / "packaging" / "launcher.py")],
    pathex=[str(ROOT)],
    datas=collect_data_files("etkinlik_radari"),  # ui/ (html, css, js, flags) and assets/
    hiddenimports=collect_submodules("etkinlik_radari"),
    excludes=["tkinter", "pytest", "PyQt5", "PyQt6", "PySide2", "PySide6"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="EtkinlikRadari",
    icon=str(ICON),
    console=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="EtkinlikRadari", upx=False)
