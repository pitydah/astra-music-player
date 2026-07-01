"""Tests for MPD profiles in output_profiles.py."""


class TestMpdProfiles:
    def test_michi_hifi_mpd_exists(self):
        from audio.output_profiles import get_profile
        prof = get_profile("michi_hifi_mpd")
        assert prof.preferred_backend == "mpd"
        assert prof.bitperfect is True

    def test_michi_bitperfect_mpd_exists(self):
        from audio.output_profiles import get_profile
        prof = get_profile("michi_bitperfect_mpd")
        assert prof.preferred_backend == "mpd"
        assert prof.allows_eq is False
        assert prof.allows_replaygain is False

    def test_michi_dsd_mpd_exists(self):
        from audio.output_profiles import get_profile
        prof = get_profile("michi_dsd_mpd")
        assert prof.preferred_backend == "mpd"
        assert prof.dsd_mode == "native"

    def test_michi_server_renderer_mpd_exists(self):
        from audio.output_profiles import get_profile
        prof = get_profile("michi_server_renderer_mpd")
        assert prof.preferred_backend == "mpd"

    def test_mpd_profiles_have_no_dsp(self):
        from audio.output_profiles import PROFILES
        mpd_keys = [k for k in PROFILES if k.endswith("_mpd")]
        for key in mpd_keys:
            prof = PROFILES[key]
            assert prof.allows_eq is False, f"{key} allows_eq"
            assert prof.allows_replaygain is False, f"{key} allows_replaygain"
            assert prof.allows_spectrum is False, f"{key} allows_spectrum"
            assert prof.allows_resample is False, f"{key} allows_resample"

    def test_standard_profile_unchanged(self):
        from audio.output_profiles import get_profile
        prof = get_profile("standard")
        assert prof.preferred_backend == "auto"
        assert prof.bitperfect is False

    def test_all_profiles_have_preferred_backend(self):
        from audio.output_profiles import PROFILES
        for key, prof in PROFILES.items():
            assert hasattr(prof, 'preferred_backend'), f"{key} missing preferred_backend"
