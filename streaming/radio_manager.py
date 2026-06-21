"""Radio Manager — manages the list of radio stations."""

import os
import json
from dataclasses import dataclass, asdict

try:
    from gi.repository import Gst
except ImportError:
    Gst = None

CONFIG_DIR = os.path.expanduser("~/.local/share/astra-music-player")
RADIO_FILE = os.path.join(CONFIG_DIR, "radio_stations.json")


@dataclass
class RadioStation:
    name: str
    url: str
    id: int = 0
    image_path: str = ""


class RadioManager:
    def __init__(self):
        self._stations: list[RadioStation] = []
        self._next_id = 1
        self._load()

    def _load(self):
        if not os.path.exists(RADIO_FILE):
            return
        try:
            with open(RADIO_FILE, "r") as f:
                data = json.load(f)
                self._stations = [RadioStation(**s) for s in data]
                self._next_id = max([s.id for s in self._stations] + [0]) + 1
        except Exception:
            import logging
            logging.getLogger("astra").debug("Failed to load radio stations config")
            self._stations = []
            self._next_id = 1

    def _save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(RADIO_FILE, "w") as f:
            json.dump([asdict(s) for s in self._stations], f, indent=2)

    def get_all(self) -> list[RadioStation]:
        return self._stations.copy()

    def add(self, name: str, url: str, image_path: str = "") -> RadioStation:
        station = RadioStation(name=name, url=url, id=self._next_id,
                              image_path=image_path)
        self._stations.append(station)
        self._next_id += 1
        self._save()
        return station

    def remove(self, station_id: int) -> bool:
        for i, s in enumerate(self._stations):
            if s.id == station_id:
                del self._stations[i]
                self._save()
                return True
        return False

    def update(self, station_id: int, name: str, url: str, image_path: str = "") -> bool:
        for s in self._stations:
            if s.id == station_id:
                s.name = name
                s.url = url
                s.image_path = image_path
                self._save()
                return True
        return False

    def start_recording(self, url: str, output_path: str) -> bool:
        """Record a radio stream to file using GStreamer."""
        import gi
        gi.require_version("Gst", "1.0")
        from gi.repository import Gst
        Gst.init(None)

        # Sanitize URL for GStreamer properties (escape single quotes in f-strings)
        safe_url = url.replace("'", "\\'")

        pipeline = Gst.Pipeline.new("radio-record")
        src = Gst.ElementFactory.make("uridecodebin", None)
        conv = Gst.ElementFactory.make("audioconvert", None)

        # Try lamemp3enc, fallback to opusenc
        enc_name = "lamemp3enc"
        enc = Gst.ElementFactory.make(enc_name, None)
        if not enc:
            enc_name = "opusenc"
            enc = Gst.ElementFactory.make(enc_name, None)
        if enc and enc_name == "lamemp3enc":
            enc.set_property("target", "bitrate")
            enc.set_property("bitrate", 192)

        sink = Gst.ElementFactory.make("filesink", None)
        if not all([src, conv, enc, sink]):
            import logging
            logging.getLogger("astra.radio").warning(
                "Missing GStreamer elements for recording: uridecodebin=%s, audioconvert=%s, enc=%s/opusenc=%s, filesink=%s",
                src is not None, conv is not None, enc is not None, enc_name, sink is not None)
            return False

        src.set_property("uri", safe_url)
        sink.set_property("location", output_path)

        for e in [src, conv, enc, sink]:
            pipeline.add(e)
        src.link(conv)
        conv.link(enc)
        enc.link(sink)

        self._record_pipeline = pipeline
        ret = pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            import logging
            logging.getLogger("astra.radio").warning("Failed to start recording pipeline")
            self._record_pipeline = None
            return False
        return True

    def stop_recording(self):
        if hasattr(self, '_record_pipeline') and self._record_pipeline:
            self._record_pipeline.set_state(Gst.State.NULL)
            self._record_pipeline.get_state(Gst.CLOCK_TIME_NONE)
            self._record_pipeline = None
