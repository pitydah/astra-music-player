#!/bin/bash
# Astra Music Player — Arch Linux / CachyOS installation
set -e

echo "=== Astra Music Player — Arch Linux Install ==="

echo "→ Installing system dependencies..."
sudo pacman -S --needed \
  python \
  python-pyside6 \
  python-mutagen \
  python-numpy \
  python-gobject \
  python-cairo \
  python-dbus \
  gstreamer \
  gst-plugins-base \
  gst-plugins-good \
  gst-plugins-bad \
  gst-plugins-ugly \
  gst-libav

echo "→ Installing Astra Music Player..."
pip install --user .

echo "→ Installing .desktop file..."
mkdir -p ~/.local/share/applications
cp data/astra-music-player.desktop ~/.local/share/applications/

echo "→ Installing app icon..."
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp icons/app_icon.png ~/.local/share/icons/hicolor/256x256/apps/astra-music-player.png

echo "✅ Astra Music Player installed!"
echo "   Run: astra-music-player"
echo "   Or find 'Astra Music Player' in your app menu."
