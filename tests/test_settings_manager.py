"""Tests for core/settings_manager — QSettings fully mocked."""
import pytest
from unittest.mock import patch


import core.settings_manager as _real_sm


class TestSettingsManager:
    """Test every public function in core.settings_manager with QSettings mocked."""

    # ── get(key) ──

    def test_get_returns_default_for_unset_key(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            val = _real_sm.get("playback/default_volume")

            assert val == 70

    def test_get_returns_stored_value(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: "custom"

            val = _real_sm.get("audio/device")

            assert val == "custom"

    def test_get_returns_none_for_unknown_key(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            val = _real_sm.get("nonexistent/key")

            assert val is None

    def test_get_returns_false_bool_default(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            val = _real_sm.get("general/confirm_exit")

            assert val is False

    # ── set_(key, value) ──

    def test_set_stores_value(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_("playback/default_volume", 50)

            mock_set.setValue.assert_called_with("playback/default_volume", 50)

    def test_set_overwrites_previous(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_("audio/device", "hw:1,0")

            mock_set.setValue.assert_called_once_with("audio/device", "hw:1,0")

    def test_set_roundtrip(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            storage = {}
            def value_side(key, default=None):
                return storage.get(key, default)
            def setValue_side(key, val):
                storage[key] = val
            mock_set.value.side_effect = value_side
            mock_set.setValue.side_effect = setValue_side

            _real_sm.set_("playback/crossfade", 3)
            result = _real_sm.get("playback/crossfade")

            assert result == 3

    # ── get_bool(key) ──

    def test_get_bool_returns_false_for_unset_bool_key(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            assert _real_sm.get_bool("general/confirm_exit") is False

    def test_get_bool_from_bool(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: True
            assert _real_sm.get_bool("x") is True

            mock_set.value.side_effect = lambda key, default=None: False
            assert _real_sm.get_bool("x") is False

    def test_get_bool_from_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            for val, expected in [("true", True), ("True", True), ("1", True),
                                    ("yes", True), ("YES", True),
                                    ("false", False), ("False", False),
                                    ("0", False), ("no", False),
                                    ("anything", False)]:
                mock_set.value.side_effect = lambda k, d=None, _v=val: _v
                got = _real_sm.get_bool("x")
                assert got is expected, f"FAIL: val={val!r} expected={expected} got={got}"

    def test_get_bool_from_int(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: 1
            assert _real_sm.get_bool("x") is True

            mock_set.value.side_effect = lambda key, default=None: 0
            assert _real_sm.get_bool("x") is False

    def test_get_bool_from_none(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: None

            assert _real_sm.get_bool("x") is False

    # ── get_int(key) ──

    def test_get_int_returns_default(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            assert _real_sm.get_int("playback/crossfade") == 0

    def test_get_int_from_int(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: 42

            assert _real_sm.get_int("playback/crossfade") == 42

    def test_get_int_from_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: "99"

            assert _real_sm.get_int("playback/crossfade") == 99

    def test_get_int_from_invalid_string_returns_zero(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: "not-a-number"

            assert _real_sm.get_int("playback/crossfade") == 0

    def test_get_int_from_none(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: None

            assert _real_sm.get_int("x") == 0

    def test_get_int_from_empty_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: ""

            assert _real_sm.get_int("x") == 0

    # ── get_float(key) ──

    def test_get_float_default(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            assert _real_sm.get_float("eq/preamp") == 0.0

    def test_get_float_from_float(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: -3.5

            assert _real_sm.get_float("eq/preamp") == -3.5

    def test_get_float_from_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: "2.75"

            assert _real_sm.get_float("eq/preamp") == 2.75

    def test_get_float_from_invalid_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: "bad"

            assert _real_sm.get_float("eq/preamp") == 0.0

    def test_get_float_from_none(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: None

            assert _real_sm.get_float("x") == 0.0

    # ── get_str(key) ──

    def test_get_str_returns_default(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            assert _real_sm.get_str("audio/device") == "default"

    def test_get_str_returns_stored_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: "hw:1,0"

            assert _real_sm.get_str("audio/device") == "hw:1,0"

    def test_get_str_converts_non_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: 42

            assert _real_sm.get_str("x") == "42"

    def test_get_str_returns_empty_for_none(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: None

            assert _real_sm.get_str("nonexistent") == ""

    # ── get_list(key) ──

    def test_get_list_default(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default

            assert _real_sm.get_list("any/key") == []

    def test_get_list_from_list(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: ["a", "b", "c"]

            assert _real_sm.get_list("x") == ["a", "b", "c"]

    def test_get_list_from_json_string(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: '["x","y"]'

            assert _real_sm.get_list("x") == ["x", "y"]

    def test_get_list_from_bad_json(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: "not-json"

            assert _real_sm.get_list("x") == []

    # ── set_bool / set_str / set_int / set_float ──

    def test_set_bool(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_bool("general/confirm_exit", True)

            mock_set.setValue.assert_called_with("general/confirm_exit", True)

    def test_set_bool_converts(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_bool("general/confirm_exit", 1)

            args = mock_set.setValue.call_args[0]
            assert args[1] is True

    def test_set_str(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_str("audio/device", "hw:2,0")

            mock_set.setValue.assert_called_with("audio/device", "hw:2,0")

    def test_set_str_converts(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_str("audio/device", 123)

            args = mock_set.setValue.call_args[0]
            assert args[1] == "123"

    def test_set_int(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_int("playback/crossfade", 5)

            mock_set.setValue.assert_called_with("playback/crossfade", 5)

    def test_set_int_converts(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_int("playback/crossfade", "3")

            args = mock_set.setValue.call_args[0]
            assert args[1] == 3

    def test_set_float(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_float("eq/preamp", -2.5)

            mock_set.setValue.assert_called_with("eq/preamp", -2.5)

    def test_set_float_converts(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_float("eq/preamp", "-1.5")

            args = mock_set.setValue.call_args[0]
            assert args[1] == -1.5

    # ── DEFAULTS ──

    def test_defaults_contains_expected_keys(self):
        expected_categories = [
            "general/", "interface/", "library/", "playback/",
            "audio/", "eq/", "transmit/", "sync/", "radio/",
            "shortcuts/", "advanced/", "home_audio/",
            "artist_enrichment/", "identifier/", "ai_assistant/",
            "knowledge_broker/", "recommendation/", "audio_analysis/",
        ]
        for cat in expected_categories:
            assert any(k.startswith(cat) for k in _real_sm.DEFAULTS), f"Missing category: {cat}"

    def test_defaults_values_are_typed_correctly(self):
        for key, val in _real_sm.DEFAULTS.items():
            assert isinstance(val, (bool, int, float, str)), (
                f"Key {key!r} has unexpected type {type(val).__name__}"
            )

    def test_defaults_bool_keys_have_bool_values(self):
        bool_keys = [k for k, v in _real_sm.DEFAULTS.items()
                     if isinstance(v, bool)]
        for k in bool_keys:
            assert isinstance(_real_sm.DEFAULTS[k], bool), (
                f"Key {k!r} should be bool, got {type(_real_sm.DEFAULTS[k]).__name__}"
            )

    def test_defaults_int_keys_have_int_values(self):
        int_keys = [k for k, v in _real_sm.DEFAULTS.items()
                    if isinstance(v, int)]
        for k in int_keys:
            assert isinstance(_real_sm.DEFAULTS[k], int), (
                f"Key {k!r} should be int, got {type(_real_sm.DEFAULTS[k]).__name__}"
            )

    # ── restore_defaults ──

    def test_restore_defaults_sets_all_keys(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.restore_defaults()

            assert mock_set.setValue.call_count == len(_real_sm.DEFAULTS)
            mock_set.setValue.assert_any_call("general/confirm_exit", False)
            mock_set.setValue.assert_any_call("playback/default_volume", 70)

    def test_restore_defaults_overwrites_existing(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.set_("playback/default_volume", 0)
            mock_set.setValue.reset_mock()

            _real_sm.restore_defaults()

            mock_set.setValue.assert_any_call("playback/default_volume", 70)

    def test_restore_defaults_called_twice(self):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            _real_sm.restore_defaults()
            count1 = mock_set.setValue.call_count

            _real_sm.restore_defaults()
            count2 = mock_set.setValue.call_count

            assert count2 == count1 * 2

    # ── export_to_file / import_from_file ──

    def test_export_to_file_writes_json(self, tmp_path):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            mock_set.value.side_effect = lambda key, default=None: default
            path = tmp_path / "settings.json"

            _real_sm.export_to_file(str(path))

            import json
            data = json.loads(path.read_text())
            assert data["playback/default_volume"] == 70
            assert data["audio/device"] == "default"
            assert len(data) == len(_real_sm.DEFAULTS)

    def test_import_from_file_restores_values(self, tmp_path):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            path = tmp_path / "settings.json"
            import json
            path.write_text(json.dumps({"playback/default_volume": 42}))

            _real_sm.import_from_file(str(path))

            mock_set.setValue.assert_called_with("playback/default_volume", 42)

    def test_import_from_file_skips_unknown_keys(self, tmp_path):
        with patch.object(_real_sm, "SETTINGS") as mock_set:
            path = tmp_path / "settings.json"
            import json
            path.write_text(json.dumps({
                "unknown/key": "value",
                "playback/default_volume": 80,
            }))

            _real_sm.import_from_file(str(path))

            calls = mock_set.setValue.call_args_list
            keys = [c[0][0] for c in calls]
            assert "unknown/key" not in keys
            assert "playback/default_volume" in keys

    def test_import_from_file_missing_file(self):
        with pytest.raises(FileNotFoundError):
            _real_sm.import_from_file("/nonexistent/settings.json")
