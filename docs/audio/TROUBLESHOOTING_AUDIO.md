# Troubleshooting Audio — Michi Music Player

## No audio output

1. Check that GStreamer plugins are installed:
   ```bash
   gst-inspect-1.0 alsasink
   gst-inspect-1.0 pipewiresink
   ```
2. Check available devices in Audio Lab → Output Profiles
3. Verify PipeWire/PulseAudio is running:
   ```bash
   pactl info
   ```

## Bit-perfect not working

1. Open Audio Lab → Bit-Perfect Monitor
2. Check the status field — if it shows "broken", read the reasons
3. Common issues:
   - Using `plughw` instead of `hw`
   - EQ or ReplayGain active
   - PipeWire/PulseAudio mixing
   - Sample rate mismatch (source ≠ DAC)
4. Verify ALSA device:
   ```bash
   cat /proc/asound/cards
   cat /proc/asound/card0/pcm0p/sub0/hw_params  # while playing
   ```

## MPD connection issues

1. Verify MPD is installed:
   ```bash
   which mpd
   ```
2. Check if MPD is running:
   ```bash
   ps aux | grep mpd
   ```
3. Test connection:
   ```bash
   nc -zv 127.0.0.1 6600
   ```
4. Check MPD log:
   ```
   ~/.local/share/michi-music-player/mpd/mpd.log
   ```
5. Try switching profile to a non-MPD profile (e.g., "Estándar")

## MPD local instance won't start

1. Check the generated config:
   ```
   ~/.local/share/michi-music-player/mpd/mpd.conf
   ```
2. Ensure music directory exists and is readable
3. Try starting MPD manually:
   ```bash
   mpd ~/.local/share/michi-music-player/mpd/mpd.conf --no-daemon --verbose
   ```
4. Common issues:
   - Music directory doesn't exist
   - Database file directory not writable
   - Port 6600 already in use

## Audio profile not applying

1. Open Audio Lab → Output Profiles
2. Select the desired profile and click "Aplicar"
3. Check the status panel shows the correct profile
4. Verify `audio/profile` setting:
   ```bash
   grep profile ~/.config/Michi/MusicPlayer.conf
   ```

## MPD Remote

1. Set `audio/mpd/mode` to `remote`
2. Set `audio/mpd/host` to the server address
3. Set `audio/mpd/port` (default 6600)
4. Test connection in Audio Lab → Bit-Perfect Monitor
