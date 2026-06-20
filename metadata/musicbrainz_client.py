"""MusicBrainz client — online identification (stub for future implementation)."""


def search_recording(artist: str, title: str, album: str = None) -> list[dict] | None:
    """Search MusicBrainz for a recording. Returns list of matches or None."""
    return None


def search_release(artist: str, album: str) -> list[dict] | None:
    """Search MusicBrainz for a release. Returns list of matches or None."""
    return None


def lookup_cover_art(mbid: str) -> bytes | None:
    """Fetch cover art for a MusicBrainz release. Returns image bytes or None."""
    return None
