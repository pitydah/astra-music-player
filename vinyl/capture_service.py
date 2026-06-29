"""Capture service — records audio from system input via GStreamer.

Uses GStreamer's autoaudiosrc or a user-selected ALSA/PulseAudio source
to capture PCM audio and write it to a temporary WAV file.
"""

from __future__ import annotations

import logging
import os
import tempfile

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("michi.vinyl.capture")


class VinylCaptureService(QObject):
    recording_started = Signal(str)  # filepath
    recording_progress = Signal(float)  # seconds recorded
    recording_finished = Signal(str)  # filepath
    recording_error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pipeline: Gst.Element | None = None
        self._filepath: str = ""
        self._is_recording = False
        self._sample_rate = 96000
        self._bit_depth = 24
        self._channels = 2

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def set_format(self, sample_rate: int = 96000,
                   bit_depth: int = 24, channels: int = 2):
        self._sample_rate = sample_rate
        self._bit_depth = bit_depth
        self._channels = channels

    def start_recording(self, filepath: str | None = None) -> bool:
        if self._is_recording:
            return False

        if not filepath:
            fd, filepath = tempfile.mkstemp(suffix=".wav", prefix="vinyl_")
            os.close(fd)

        pipeline_str = (
            f"autoaudiosrc ! "
            f"audioconvert ! audioresample ! "
            f"capsfilter caps=audio/x-raw,rate={self._sample_rate},"
            f"channels={self._channels},"
            f"format=S{self._bit_depth}LE ! "
            f"wavenc ! "
            f"filesink location={filepath}"
        )

        try:
            self._pipeline = Gst.parse_launch(pipeline_str)
            self._pipeline.set_state(Gst.State.PLAYING)
            self._filepath = filepath
            self._is_recording = True
            self.recording_started.emit(filepath)
            logger.info("Vinyl recording started: %s", filepath)
            return True
        except Exception as e:
            logger.exception("Failed to start vinyl capture")
            self.recording_error.emit(str(e))
            return False

    def stop_recording(self) -> str:
        if not self._is_recording or not self._pipeline:
            return self._filepath

        try:
            self._pipeline.send_event(Gst.Event.new_eos())
            self._pipeline.get_state(Gst.CLOCK_TIME_NONE)
            self._pipeline.set_state(Gst.State.NULL)
        except Exception as e:
            logger.warning("Error stopping capture: %s", e)

        self._is_recording = False
        self.recording_finished.emit(self._filepath)
        logger.info("Vinyl recording finished: %s", self._filepath)
        return self._filepath

    def list_devices(self) -> list[dict]:
        """List available audio input sources."""
        from audio.output_device_manager import list_devices
        try:
            return [d.to_dict() if hasattr(d, 'to_dict') else {"name": str(d)}
                    for d in list_devices(capture=True)]
        except Exception:
            return [{"name": "Default (autoaudiosrc)"}]

    def cleanup(self):
        if self._pipeline:
            try:
                self._pipeline.set_state(Gst.State.NULL)
            except Exception:
                pass
            self._pipeline = None
        self._is_recording = False
