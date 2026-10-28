#!/usr/bin/env python3
"""Etkinlik Radarı installer — Windows, macOS and Linux. Uses only the standard library.

    python install.py              step-by-step installation
    python install.py --yes        accept every default (no questions)
    python install.py --uninstall  remove the app, its shortcuts and (optionally) user data

The app is installed into its own virtual environment, so the downloaded source folder can be
deleted afterwards. Settings are made in the app's own setup wizard on first launch.
"""
import argparse
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

APP_NAME = "Etkinlik Radarı"
APP_ID = "etkinlik-radari"
SOURCE_DIR = Path(__file__).resolve().parent
MIN_PY = (3, 10)
IS_WIN, IS_MAC = sys.platform == "win32", sys.platform == "darwin"
STEPS = 5

sys.path.insert(0, str(SOURCE_DIR))
from etkinlik_radari import __version__  # noqa: E402  (stdlib-only module)
from etkinlik_radari.paths import data_dir  # noqa: E402


# ---------- console helpers ----------
def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if IS_WIN:
        os.system("")  # enables ANSI escape handling in the Windows console
    return sys.stdout.isatty()


C = supports_color()
def paint(code, text): return f"\033[{code}m{text}\033[0m" if C else text
def bold(t): return paint("1", t)
def dim(t): return paint("2", t)
def ok(t): print(paint("32", "  ✓ ") + t)
def warn(t): print(paint("33", "  ! ") + t)
def fail(t): print(paint("31", "  ✗ ") + t)


def step(n, title):
    print()
    print(bold(paint("38;5;208", f"[{n}/{STEPS}] ") + title))


def ask_yes(question, default=True, assume=False) -> bool:
    if assume:
        return default
    hint = "E/h" if default else "e/H"
    while True:
        ans = input(f"  {question} [{hint}]: ").strip().lower()
        if not ans:
            return default
        if ans in ("e", "evet", "y", "yes"):
            return True
        if ans in ("h", "hayır", "hayir", "n", "no"):
            return False


def ask_path(question, default: Path, assume=False) -> Path:
    if assume:
        return default
    ans = input(f"  {question}\n  {dim(str(default))}\n  (Enter = varsayılan): ").strip().strip('"')
    return Path(ans).expanduser().resolve() if ans else default


# ---------- locations ----------
def default_install_dir() -> Path:
    if IS_WIN:
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "Programs" / "EtkinlikRadari"
    if IS_MAC:
        return Path.home() / "Library" / "Application Support" / "EtkinlikRadari" / "app"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / APP_ID / "app"


def venv_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if IS_WIN else "bin/python")


def launcher(root: Path) -> Path:
    """The gui-script pip generates from pyproject (no console window on Windows)."""
    return root / ("Scripts/etkinlik-radari.exe" if IS_WIN else "bin/etkinlik-radari")


def windows_folder(name: str) -> Path:
    """Real Desktop / Start Menu paths (handles OneDrive-redirected desktops)."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command", f"[Environment]::GetFolderPath('{name}')"],
                         capture_output=True, text=True)
    return Path(out.stdout.strip())


def xdg_dir(kind: str, fallback: Path) -> Path:
    try:
        out = subprocess.run(["xdg-user-dir", kind], capture_output=True, text=True, timeout=3)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return fallback


def shortcut_targets() -> dict:
    """name -> path of every launcher the installer may create on this OS."""
    if IS_WIN:
        return {"desktop": windows_folder("Desktop") / f"{APP_NAME}.lnk",
                "menu": windows_folder("Programs") / f"{APP_NAME}.lnk"}
    if IS_MAC:
        return {"menu": Path.home() / "Applications" / f"{APP_NAME}.app",
                "desktop": Path.home() / "Desktop" / f"{APP_NAME}.app"}
    apps = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "applications"
    return {"menu": apps / f"{APP_ID}.desktop",
            "desktop": xdg_dir("DESKTOP", Path.home() / "Desktop") / f"{APP_ID}.desktop"}


# ---------- shortcuts ----------
def make_windows_shortcut(path: Path, target: Path, icon: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    q = lambda p: str(p).replace("'", "''")  # PowerShell single-quote escaping
    ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{q(path)}');"
          f"$s.TargetPath='{q(target)}';$s.WorkingDirectory='{q(target.parent)}';"
          f"$s.IconLocation='{q(icon)},0';$s.Description='{APP_NAME}';$s.Save()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True, capture_output=True)


def make_mac_app(path: Path, target: Path, icon_png: Path):
    contents = path / "Contents"
    (contents / "MacOS").mkdir(parents=True, exist_ok=True)
    (contents / "Resources").mkdir(parents=True, exist_ok=True)
    exe = contents / "MacOS" / "EtkinlikRadari"
    exe.write_text(f'#!/bin/sh\nexec "{target}" "$@"\n', encoding="utf-8")
    exe.chmod(0o755)
    info = {"CFBundleName": APP_NAME, "CFBundleDisplayName": APP_NAME, "CFBundleIdentifier": "io.github.etkinlik-radari",
            "CFBundleExecutable": "EtkinlikRadari", "CFBundlePackageType": "APPL", "CFBundleShortVersionString": __version__,
            "LSMinimumSystemVersion": "11.0", "NSHighResolutionCapable": True}
    if shutil.which("sips") and shutil.which("iconutil"):  # build an .icns from the PNG
        with tempfile.TemporaryDirectory() as tmp:
            iconset = Path(tmp) / "icon.iconset"
            iconset.mkdir()
            for size in (16, 32, 128, 256, 512):
                for scale in (1, 2):
                    px = size * scale
                    name = f"icon_{size}x{size}{'@2x' if scale == 2 else ''}.png"
                    subprocess.run(["sips", "-z", str(px), str(px), str(icon_png), "--out", str(iconset / name)],
                                   check=True, capture_output=True)
            subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(contents / "Resources" / "icon.icns")],
                           check=True, capture_output=True)
        info["CFBundleIconFile"] = "icon"
    with open(contents / "Info.plist", "wb") as f:
        plistlib.dump(info, f)


def make_linux_desktop(path: Path, target: Path, icon_png: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([
        "[Desktop Entry]", "Type=Application", f"Name={APP_NAME}", "Comment=Girişim, yatırım ve teknoloji etkinlikleri",
        f'Exec="{target}"', f"Icon={icon_png}", "Terminal=false", "Categories=Office;Network;Calendar;",
        "StartupWMClass=etkinlik-radari", ""]), encoding="utf-8")
    path.chmod(0o755)
    if shutil.which("gio"):  # lets GNOME launch it from the desktop without the "untrusted" prompt
        subprocess.run(["gio", "set", str(path), "metadata::trusted", "true"], capture_output=True)


def create_shortcut(kind: str, path: Path, target: Path, assets: Path):
    if IS_WIN:
        make_windows_shortcut(path, target, assets / "icon.ico")
    elif IS_MAC:
        if kind == "desktop":  # a symlink to the bundle in ~/Applications
            if path.is_symlink() or path.exists():
                path.unlink()
            path.symlink_to(shortcut_targets()["menu"])
        else:
            make_mac_app(path, target, assets / "icon.png")
    else:
        make_linux_desktop(path, target, assets / "icon.png")


# ---------- install / uninstall ----------
def install(args):
    print(bold(f"\n  {APP_NAME} {__version__} — Kurulum"))
    print(dim("  Girişim · Yatırım · Teknoloji etkinlikleri tek yerde\n"))

    step(1, "Sistem kontrolü")
    if sys.version_info < MIN_PY:
        fail(f"Python {'.'.join(map(str, MIN_PY))} veya üstü gerekli (şu an {sys.version.split()[0]}).")
        sys.exit(1)
    ok(f"Python {sys.version.split()[0]} · {sys.platform}")
    if not (SOURCE_DIR / "pyproject.toml").is_file():
        fail("pyproject.toml bulunamadı; install.py proje klasöründen çalıştırılmalı.")
        sys.exit(1)
    if not IS_WIN and not IS_MAC:
        warn("Linux: pencere Qt WebEngine ile açılır. Hata alırsan README'deki 'Linux notları'na bak.")

    step(2, "Kurulum klasörü")
    target = args.dir.resolve() if args.dir else ask_path("Uygulama nereye kurulsun?", default_install_dir(), args.yes)
    if target.exists() and any(target.iterdir()):
        if not ask_yes(f"{target} zaten var. Üzerine yeniden kurulsun mu?", True, args.yes):
            sys.exit("  İptal edildi.")
        shutil.rmtree(target)
    ok(f"Klasör: {target}")

    step(3, "Uygulama ve bağımlılıklar yükleniyor (bu adım birkaç dakika sürebilir)")
    venv.EnvBuilder(with_pip=True, clear=True).create(target)
    ok("Sanal ortam oluşturuldu")
    py = venv_python(target)
    pip = [str(py), "-m", "pip", "--disable-pip-version-check"]
    subprocess.run(pip + ["install", "-q", "--upgrade", "pip"], check=False)
    leftovers = [p for p in (SOURCE_DIR / "build", SOURCE_DIR / "etkinlik_radari.egg-info") if not p.exists()]
    result = subprocess.run(pip + ["install", "-q", str(SOURCE_DIR)])
    for p in leftovers:  # setuptools builds in-tree; keep the source folder clean
        shutil.rmtree(p, ignore_errors=True)
    if result.returncode != 0:
        fail("Paketler yüklenemedi. İnternet bağlantını kontrol edip tekrar dene.")
        sys.exit(1)
    ok("Etkinlik Radarı ve bağımlılıkları yüklendi")
    legacy, data = SOURCE_DIR / "data" / "radar.db", data_dir()
    if legacy.is_file() and not (data / "radar.db").exists():  # data from running the app out of the source folder
        data.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy, data / "radar.db")
        ok(f"Önceki veriler taşındı: {data}")
    assets = Path(subprocess.run([str(py), "-c", "from etkinlik_radari import paths; print(paths.ASSETS_DIR)"],
                                 capture_output=True, text=True, check=True).stdout.strip())

    step(4, "Kısayollar")
    targets = shortcut_targets()
    labels = {"menu": "Başlat menüsü" if IS_WIN else "Uygulamalar klasörü" if IS_MAC else "Uygulama menüsü",
              "desktop": "Masaüstü"}
    made = []
    for kind in ("menu", "desktop"):
        if args.no_shortcuts or not ask_yes(f"{labels[kind]} kısayolu oluşturulsun mu?", True, args.yes):
            continue
        try:
            create_shortcut(kind, targets[kind], launcher(target), assets)
            made.append(targets[kind])
            ok(f"{labels[kind]}: {targets[kind]}")
        except (OSError, subprocess.CalledProcessError) as e:
            warn(f"{labels[kind]} kısayolu oluşturulamadı: {e}")
    if not made:
        ok("Kısayol oluşturulmadı")

    step(5, "Tamamlandı")
    ok(f"Başlatmak için: {launcher(target)}")
    ok(f"Verilerin: {data_dir()}")
    print(dim("  İlk açılışta kurulum sihirbazı ilgi alanlarını, kaynakları ve görünümü soracak."))
    print(dim(f"  Kaldırmak için: python install.py --uninstall"))
    if args.launch is not False and ask_yes("Etkinlik Radarı şimdi başlatılsın mı?", True, args.yes):
        subprocess.Popen([str(launcher(target))], start_new_session=not IS_WIN)


def uninstall(args):
    print(bold(f"\n  {APP_NAME} — Kaldırma\n"))
    target = args.dir.resolve() if args.dir else default_install_dir()
    for kind, path in shortcut_targets().items():
        if path.is_symlink() or path.is_file():
            path.unlink()
            ok(f"Kısayol silindi: {path}")
        elif path.is_dir() and path.suffix == ".app":
            shutil.rmtree(path)
            ok(f"Uygulama paketi silindi: {path}")
    if target.exists():
        shutil.rmtree(target)
        ok(f"Uygulama silindi: {target}")
    else:
        warn(f"Kurulum klasörü bulunamadı: {target}")
    data = data_dir()
    if data.exists() and ask_yes(f"Ayarlar ve kayıtlı etkinlikler de silinsin mi? ({data})", False, args.yes):
        shutil.rmtree(data)
        ok("Kullanıcı verileri silindi")
    print()


def main():
    p = argparse.ArgumentParser(description=f"{APP_NAME} kurulum aracı")
    p.add_argument("--yes", "-y", action="store_true", help="soru sormadan varsayılanları kabul et")
    p.add_argument("--dir", type=Path, help="kurulum klasörü")
    p.add_argument("--no-shortcuts", action="store_true", help="kısayol oluşturma")
    p.add_argument("--no-launch", dest="launch", action="store_false", default=None, help="kurulumdan sonra başlatma")
    p.add_argument("--uninstall", action="store_true", help="uygulamayı kaldır")
    args = p.parse_args()
    try:
        uninstall(args) if args.uninstall else install(args)
    except KeyboardInterrupt:
        sys.exit("\n  İptal edildi.")


if __name__ == "__main__":
    main()
