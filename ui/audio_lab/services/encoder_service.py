"""Encoder service — audio format conversion. STUB."""

from __future__ import annotations


class EncoderService:
    def check_available_encoders(self) -> dict[str, bool]:
        from ui.audio_lab.services.external_tools import tool_available
        return {
            "flac": tool_available("flac"),
            "lame": tool_available("lame"),
            "opus": tool_available("opusenc"),
            "ffmpeg": tool_available("ffmpeg"),
        }

    def encode_to_flac(self, input_path: str, output_path: str):
        pass

    def encode_to_mp3(self, input_path: str, output_path: str, bitrate: int = 320):
        pass

    def encode_to_opus(self, input_path: str, output_path: str, bitrate: int = 192):
        pass

    def encode_to_alac(self, input_path: str, output_path: str):
        pass

    def encode_multiple_outputs(self, input_path: str, outputs: list[str]):
        pass
