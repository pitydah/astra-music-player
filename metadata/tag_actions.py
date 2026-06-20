"""Batch tag actions — apply operations across multiple TrackTags."""
from metadata.tag_model import TrackTags


def apply_field_to_all(items: list[TrackTags], field: str, value: str):
    """Set a field value on all items."""
    for t in items:
        setattr(t, field, value)
        t.mark_dirty()


def auto_number_tracks(items: list[TrackTags], start: int = 1):
    """Number tracks sequentially."""
    for i, t in enumerate(items):
        t.tracknumber = str(start + i)
        t.mark_dirty()


def normalize_spaces(items: list[TrackTags]):
    """Collapse multiple spaces and trim field values."""
    text_fields = ["title", "artist", "album", "albumartist", "genre", "composer", "comment"]
    for t in items:
        for f in text_fields:
            val = getattr(t, f, "").strip()
            if "  " in val:
                val = " ".join(val.split())
                setattr(t, f, val)
                t.mark_dirty()


def title_case(items: list[TrackTags]):
    """Capitalize first letter of each word in title/artist/album."""
    text_fields = ["title", "artist", "album", "albumartist", "composer"]
    for t in items:
        for f in text_fields:
            val = getattr(t, f, "")
            if val and val != val.title():
                setattr(t, f, val.title())
                t.mark_dirty()


def search_replace(items: list[TrackTags], field: str, old: str, new: str):
    """Replace substring in a field across all items."""
    for t in items:
        val = getattr(t, field, "")
        if old in val:
            setattr(t, field, val.replace(old, new))
            t.mark_dirty()


def clear_field(items: list[TrackTags], field: str):
    """Clear a field on all items."""
    for t in items:
        setattr(t, field, "")
        t.mark_dirty()


def copy_field(items: list[TrackTags], source_field: str, target_field: str):
    """Copy one tag field to another across all items."""
    for t in items:
        setattr(t, target_field, getattr(t, source_field, ""))
        t.mark_dirty()
