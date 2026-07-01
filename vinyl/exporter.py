"""Vinyl Lab exporter — splits recordings into tracks and encodes to FLAC/WAV.

Takes a recorded WAV side, split points, and metadata, then:
1. Splits the WAV into individual track files.
2. Encodes to FLAC (or keeps as WAV).
3. Writes metadata tags via mutagen.
4. Copies to the library import directory.
"""

from __future__ import annotations

import logging
import os
import subprocess
import wave

logger = logging.getLogger("michi.vinyl.exporter")


def split_wav(input_path: str, output_dir: str,
              split_points: list[float],
              tracks: list[dict]) -> list[str]:
    """Split a WAV file into tracks at given split points.

    Args:
        input_path: Path to the recorded WAV.
        output_dir: Directory for split WAV files.
        split_points: Sorted list of split times in seconds.
            The i-th track runs from split_points[i] to split_points[i+1].
        tracks: Metadata for each track (title, artist, track_number).

    Returns:
        List of output filepaths created.
    """
    os.makedirs(output_dir, exist_ok=True)
    created = []

    try:
        with wave.open(input_path, "rb") as wf:
            sr = wf.getframerate()
            sampwidth = wf.getsampwidth()
            n_channels = wf.getnchannels()
            total_frames = wf.getnframes()
            raw = wf.readframes(total_frames)

        for i in range(len(split_points) - 1):
            start_frame = int(split_points[i] * sr)
            end_frame = int(split_points[i + 1] * sr)
            if start_frame >= end_frame or start_frame >= total_frames:
                continue

            track_info = tracks[i] if i < len(tracks) else {}
            track_num = track_info.get("track_number", i + 1)
            title = track_info.get("title", f"Track {track_num}")
            safe_title = "".join(
                c for c in title if c.isalnum() or c in " _-."
            ).strip() or f"Track_{track_num}"

            out_path = os.path.join(output_dir, f"{track_num:02d} - {safe_title}.wav")
            frames_to_write = min(end_frame - start_frame,
                                  total_frames - start_frame)

            chunk = raw[start_frame * sampwidth * n_channels:
                        (start_frame + frames_to_write) * sampwidth * n_channels]

            with wave.open(out_path, "wb") as out_wf:
                out_wf.setnchannels(n_channels)
                out_wf.setsampwidth(sampwidth)
                out_wf.setframerate(sr)
                out_wf.writeframes(chunk)

            created.append(out_path)

    except Exception:
        logger.exception("Failed to split WAV: %s", input_path)

    return created


def encode_to_flac(wav_path: str, output_dir: str,
                   tags: dict | None = None) -> str | None:
    """Encode a WAV file to FLAC using flac CLI or ffmpeg.

    Args:
        wav_path: Input WAV filepath.
        output_dir: Output directory for FLAC file.
        tags: Optional metadata tags.

    Returns:
        Path to FLAC file, or None on failure.
    """
    base = os.path.splitext(os.path.basename(wav_path))[0]
    flac_path = os.path.join(output_dir, f"{base}.flac")

    try:
        # Prefer flac CLI
        if not tags:
            result = subprocess.run(
                ["flac", "--best", "-o", flac_path, wav_path],
                capture_output=True, text=True, timeout=120,
            )
        else:
            tag_args = []
            for k, v in tags.items():
                if v:
                    tag_args.extend(["-T", f"{k}={v}"])
            result = subprocess.run(
                ["flac", "--best"] + tag_args + ["-o", flac_path, wav_path],
                capture_output=True, text=True, timeout=120,
            )

        if result.returncode == 0 and os.path.exists(flac_path):
            return flac_path

        # Fallback to ffmpeg
        ff_path = os.path.join(output_dir, f"{base}.flac")
        ff_result = subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-c:a", "flac",
             "-compression_level", "12", ff_path],
            capture_output=True, text=True, timeout=120,
        )
        if ff_result.returncode == 0 and os.path.exists(ff_path):
            return ff_path

        logger.warning("FLAC encoding failed for %s: %s",
                       wav_path, result.stderr[:200])
        return None

    except Exception:
        logger.exception("FLAC encoding failed: %s", wav_path)
        return None


def export_side(input_path: str, export_dir: str, split_points: list,
                tracks: list, fmt: str = "flac") -> dict:
    """Run full export pipeline: split + encode + cleanup.
    Returns dict with keys: exported (list[str]), errors (list[str]).
    """
    result: dict = {"exported": [], "errors": []}
    try:
        split_files = split_wav(input_path, export_dir, split_points, tracks)
    except Exception as e:
        result["errors"].append(f"split failed: {e}")
        return result
    for wav_path in split_files:
        try:
            out = encode_wav(wav_path, export_dir, fmt)
            if out:
                result["exported"].append(out)
            if os.path.exists(wav_path) and fmt != "wav":
                import contextlib
                with contextlib.suppress(Exception):
                    os.remove(wav_path)
        except Exception as e:
            result["errors"].append(f"{wav_path}: {e}")
    return result


def encode_wav(wav_path: str, output_dir: str, output_format: str = "flac",
               tags: dict | None = None) -> str | None:
    """Encode a WAV file to the specified format."""
    if output_format == "flac":
        return encode_to_flac(wav_path, output_dir, tags)
    if output_format == "wav":
        import shutil
        dst = os.path.join(output_dir, os.path.basename(wav_path))
        shutil.copy2(wav_path, dst)
        return dst
    logger.warning("Unsupported output format: %s", output_format)
    return None
