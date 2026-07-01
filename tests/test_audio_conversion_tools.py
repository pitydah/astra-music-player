"""Tests for audio conversion tools — read-only recommendations, no side effects."""

from __future__ import annotations

from unittest.mock import MagicMock

from integrations.ai_assistant.tools.audio_conversion_tools import (
    explain_audio_format,
    recommend_conversion_profile,
    suggest_mobile_audio_profile,
    suggest_micro_server_streaming_profile,
    suggest_hifi_audio_profile,
)


def _mock_item():
    item = MagicMock()
    item.codec = "FLAC"
    item.container = "flac"
    item.sample_rate = 96000
    item.bit_depth = 24
    item.bitrate = 2800000
    item.channels = 2
    return item


def _mock_db():
    db = MagicMock()
    db.get_media_item_by_id.return_value = _mock_item()
    return db


class TestExplainAudioFormat:
    def test_lossless(self):
        result = explain_audio_format(_mock_db(), track_ids=[1])
        assert result.success
        data = result.data or {}
        info = data.get("format_info") or {}
        assert info.get("codec") == "FLAC"
        assert info.get("sample_rate") == 96000

    def test_hires(self):
        db = _mock_db()
        result = explain_audio_format(db, track_ids=[1])
        assert result.success

    def test_no_db(self):
        result = explain_audio_format(None, track_ids=[1])
        assert result.success


class TestRecommendMobileProfile:
    def test_suggest_mobile_balanced(self):
        result = suggest_mobile_audio_profile(_mock_db(), track_ids=[1], phone_storage_profile="balanced")
        assert result.success
        data = result.data or {}
        rec = data.get("recommendation") or {}
        assert rec.get("codec") == "opus"
        assert rec.get("bitrate") == "160k"

    def test_suggest_mobile_space_saver(self):
        result = suggest_mobile_audio_profile(_mock_db(), track_ids=[1], phone_storage_profile="space_saver")
        assert result.success
        data = result.data or {}
        rec = data.get("recommendation") or {}
        assert rec.get("bitrate") == "128k"

    def test_no_db(self):
        result = suggest_mobile_audio_profile(None, track_ids=None)
        assert result.success
        data = result.data or {}
        assert "warnings" in data


class TestRecommendMicroServerProfile:
    def test_remote(self):
        result = suggest_micro_server_streaming_profile(_mock_db(), track_ids=[1], network_profile="remote")
        assert result.success
        data = result.data or {}
        rec = data.get("recommendation") or {}
        assert rec.get("codec") == "opus"

    def test_lan(self):
        result = suggest_micro_server_streaming_profile(_mock_db(), track_ids=[1], network_profile="lan")
        assert result.success
        data = result.data or {}
        rec = data.get("recommendation") or {}
        assert rec.get("codec") == "flac"


class TestRecommendHifiProfile:
    def test_hifi(self):
        result = suggest_hifi_audio_profile(_mock_db(), track_ids=[1])
        assert result.success
        data = result.data or {}
        rec = data.get("recommendation") or {}
        assert rec.get("codec") == "flac"


class TestNoConversionSideEffects:
    def test_no_conversion_executed(self):
        db = _mock_db()
        result = recommend_conversion_profile(db, track_ids=[1], target="mobile")
        assert result.success
        data = result.data or {}
        assert "warnings" in data
        assert any("no sera modificado" in w for w in data.get("warnings", []))
