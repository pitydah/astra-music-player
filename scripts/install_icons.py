#!/usr/bin/env python3
"""Install Michi Music Player icons to the FreeDesktop hicolor theme.

Generates PNGs at standard sizes (16, 22, 24, 32, 48, 64, 128, 256)
from the base SVG or PNG and installs them to ~/.local/share/icons/hicolor/.

Usage:
  python3 scripts/install_icons.py              # from repo root inside venv
  python3 scripts/install_icons.py --uninstall   # remove installed icons
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ICON_SIZES = [16, 22, 24, 32, 48, 64, 128, 256]
APP_ID = "michi-music-player"


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_icon_dir() -> Path:
    return Path.home() / ".local" / "share" / "icons" / "hicolor"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_png_qt(source_path: Path, size: int, dest_path: Path) -> bool:
    """Generate a PNG at the given size using PySide6 (already in venv)."""
    try:
        from PySide6.QtCore import QSize, Qt
        from PySide6.QtGui import QImage, QPainter
    except ImportError:
        return False

    try:
        from PySide6.QtSvg import QSvgRenderer  # type: ignore[import-untyped]
        _has_svg = True
    except ImportError:
        _has_svg = False

    if source_path.suffix.lower() == ".svg" and _has_svg:
        renderer = QSvgRenderer(str(source_path))
        if not renderer.isValid():
            print(f"  ⚠  Invalid SVG: {source_path}")
            return False
        image = QImage(QSize(size, size), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
    else:
        image = QImage(str(source_path))
        if image.isNull():
            print(f"  ⚠  Cannot load image: {source_path}")
            return False
        image = image.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        # Re-center on a square canvas
        final = QImage(QSize(size, size), QImage.Format_ARGB32_Premultiplied)
        final.fill(Qt.GlobalColor.transparent)
        painter = QPainter(final)
        x = (size - image.width()) // 2
        y = (size - image.height()) // 2
        painter.drawImage(x, y, image)
        painter.end()
        image = final

    ensure_dir(dest_path.parent)
    image.save(str(dest_path), "PNG")
    return True


def generate_png_convert(source_path: Path, size: int, dest_path: Path) -> bool:
    """Generate a PNG at the given size using ImageMagick or rsvg-convert."""
    ensure_dir(dest_path.parent)

    if source_path.suffix.lower() == ".svg":
        cmd = ["rsvg-convert", "-w", str(size), "-h", str(size),
               "-o", str(dest_path), str(source_path)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

    # Fallback: ImageMagick
    for magick_cmd in (["magick"], ["convert"]):
        cmd = [*magick_cmd, str(source_path), "-resize", f"{size}x{size}",
               "-background", "none", "-gravity", "center",
               "-extent", f"{size}x{size}", str(dest_path)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

    return False


def find_source_icon() -> Path | None:
    root = get_repo_root()
    svg = root / "icons" / "app_icon.svg"
    if svg.exists():
        return svg
    png = root / "icons" / "app_icon.png"
    if png.exists():
        return png
    return None


def install_icons() -> bool:
    source = find_source_icon()
    if source is None:
        print("❌ No se encontró app_icon.svg ni app_icon.png en icons/")
        return False

    print(f"→ Generando iconos desde {source.name}...")
    icon_dir = get_icon_dir()
    installed = 0

    for size in ICON_SIZES:
        dest = icon_dir / f"{size}x{size}" / "apps" / f"{APP_ID}.png"
        ok = generate_png_qt(source, size, dest)
        if not ok:
            ok = generate_png_convert(source, size, dest)
        if ok:
            print(f"  ✓ {size}x{size}")
            installed += 1
        else:
            print(f"  ✗ {size}x{size} — falló la conversión")
            return False

    # Also install scalable SVG
    if source.suffix.lower() == ".svg":
        scalable_dir = icon_dir / "scalable" / "apps"
        ensure_dir(scalable_dir)
        shutil.copy2(source, scalable_dir / f"{APP_ID}.svg")
        print("  ✓ scalable (SVG)")

    print(f"  {installed} iconos instalados en {icon_dir}")
    return True


def uninstall_icons() -> None:
    icon_dir = get_icon_dir()
    count = 0
    for size in ICON_SIZES:
        path = icon_dir / f"{size}x{size}" / "apps" / f"{APP_ID}.png"
        if path.exists():
            path.unlink()
            count += 1

    scalable = icon_dir / "scalable" / "apps" / f"{APP_ID}.svg"
    if scalable.exists():
        scalable.unlink()
        count += 1

    print(f"  {count} iconos eliminados de {icon_dir}")


def update_cache() -> None:
    """Update icon and desktop caches so DEs pick up the new icons."""
    icon_dir = get_icon_dir()

    if shutil.which("gtk-update-icon-cache"):
        subprocess.run(
            ["gtk-update-icon-cache", "-f", "-t", str(icon_dir)],
            capture_output=True,
        )
        print("  ✓ gtk-update-icon-cache")

    desktop_dir = Path.home() / ".local" / "share" / "applications"
    if shutil.which("update-desktop-database"):
        subprocess.run(
            ["update-desktop-database", str(desktop_dir)],
            capture_output=True,
        )
        print("  ✓ update-desktop-database")

    # KDE Plasma: rebuild sycoca so the app appears in menus immediately
    for kbuild in ("kbuildsycoca6", "kbuildsycoca5"):
        if shutil.which(kbuild):
            subprocess.run([kbuild], capture_output=True)
            print(f"  ✓ {kbuild} (KDE menu cache)")
            break


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install Michi Music Player icons to FreeDesktop hicolor theme"
    )
    parser.add_argument(
        "--uninstall", action="store_true",
        help="Remove installed icons"
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Skip cache updates (gtk-update-icon-cache, update-desktop-database)"
    )
    args = parser.parse_args()

    if args.uninstall:
        uninstall_icons()
    else:
        if not install_icons():
            sys.exit(1)

    if not args.no_cache:
        update_cache()

    print("✅ Iconos listos")


if __name__ == "__main__":
    main()
