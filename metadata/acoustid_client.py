"""AcoustID client — audio fingerprinting (stub for future implementation)."""


def fingerprint_file(filepath: str) -> str | None:
    """Generate an AcoustID fingerprint for an audio file. Returns fingerprint string or None."""
    return None


def lookup_fingerprint(fingerprint: str, duration: float) -> list[dict] | None:
    """Look up a fingerprint against the AcoustID database. Returns list of matches or None."""
    return None
