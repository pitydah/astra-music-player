#!/bin/bash
# Astra Music Player — Ubuntu / Debian installation
set -e

echo "=== Astra Music Player — Ubuntu Install ==="

echo "→ Installing system dependencies..."
sudo apt install -y \
  python3 \
  python3-pip \
  python3-gi \
  gir1.2-gstreamer-1.0 \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav \
  python3-numpy

echo "→ Installing Python dependencies..."
pip install --user -r requirements.txt

echo "→ Installing .desktop file..."
mkdir -p ~/.local/share/applications
cp data/astra-music-player.desktop ~/.local/share/applications/

echo "→ Installing app icon..."
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp icons/app_icon.png ~/.local/share/icons/hicolor/256x256/apps/astra-music-player.png

echo "✅ Astra Music Player installed!"
echo "   Run: python3 main.py"
echo "   Or find 'Astra Music Player' in your app menu."
