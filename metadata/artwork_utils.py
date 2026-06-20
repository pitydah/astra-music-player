"""Artwork utilities — extract, set, remove embedded artwork."""
import os


def extract_artwork(filepath: str, dest_path: str) -> bool:
    """Extract embedded artwork to a file. Returns True on success."""
    try:
        from metadata.tag_reader import read_tags
        tags = read_tags(filepath)
        if tags.artwork_data:
            mime = tags.artwork_mime or "image/jpeg"
            ext = ".jpg" if "jpeg" in mime else ".png"
            out = dest_path if dest_path.endswith(ext) else dest_path + ext
            with open(out, "wb") as f:
                f.write(tags.artwork_data)
            return True
    except Exception:
        pass
    return False


def set_artwork(filepath: str, image_path: str) -> bool:
    """Embed an image file into the audio file. Returns True on success."""
    if not os.path.isfile(image_path):
        return False
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        ext = os.path.splitext(image_path)[1].lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"

        from metadata.tag_reader import read_tags
        from metadata.tag_writer import write_tags
        tags = read_tags(filepath)
        if tags.error:
            return False
        tags.has_artwork = True
        tags.artwork_mime = mime
        tags.artwork_data = data
        tags.mark_dirty()
        return write_tags(tags)
    except Exception:
        return False


def remove_artwork(filepath: str) -> bool:
    """Remove embedded artwork. Returns True on success."""
    try:
        from metadata.tag_reader import read_tags
        from metadata.tag_writer import write_tags
        tags = read_tags(filepath)
        if tags.error:
            return False
        tags.has_artwork = False
        tags.artwork_mime = ""
        tags.artwork_data = None
        tags.mark_dirty()
        return write_tags(tags)
    except Exception:
        return False


def load_image_as_bytes(image_path: str) -> bytes | None:
    """Load an image file as bytes."""
    if not os.path.isfile(image_path):
        return None
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except Exception:
        return None
