"""Tag reader — reads audio metadata using Mutagen."""
import os

from metadata.tag_model import TrackTags

_mutagen_available = False
try:
    import mutagen
    from mutagen.flac import FLAC, Picture
    from mutagen.id3 import ID3, APIC
    from mutagen.oggopus import OggOpus
    from mutagen.oggvorbis import OggVorbis
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.easyid3 import EasyID3
    from mutagen.aiff import AIFF
    from mutagen.wave import WAVE
    from mutagen.monkeysaudio import MonkeysAudio
    _mutagen_available = True
except ImportError:
    pass

AUDIO_EXTS = {
    ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".mp4",
    ".wav", ".aiff", ".aif", ".ape", ".wma", ".dsf",
}


def _read_artwork(f, kind: str) -> tuple[bool, str, bytes | None]:
    """Extract artwork data from the file if available."""
    try:
        if kind == "mp3" and hasattr(f, "tags"):
            for k in f.tags or {}:
                if k.startswith("APIC:"):
                    return True, f.tags[k].mime, f.tags[k].data
        elif kind == "flac" and hasattr(f, "pictures"):
            pics = f.pictures or []
            if pics:
                return True, pics[0].mime, pics[0].data
        elif kind in ("mp4", "m4a"):
            covr = f.tags.get("covr", []) if hasattr(f, "tags") else []
            if covr:
                fmt = "image/jpeg" if covr[0].imageformat == MP4Cover.FORMAT_JPEG else "image/png"
                return True, fmt, bytes(covr[0])
    except Exception:
        pass
    return False, "", None


def read_tags(filepath: str) -> TrackTags:
    """Read all tags from an audio file. Returns TrackTags (with error field on failure)."""
    if not os.path.isfile(filepath):
        return TrackTags(filepath=filepath, error="Archivo no encontrado")

    if not _mutagen_available:
        return TrackTags(filepath=filepath, error="Instala mutagen: pip install mutagen")

    try:
        f = mutagen.File(filepath)
    except Exception as e:
        return TrackTags(filepath=filepath, error=f"Error al abrir: {e}")

    if f is None:
        return TrackTags(filepath=filepath, error="Formato no soportado")

    ext = os.path.splitext(filepath)[1].lower()
    kind = "mp3" if ext == ".mp3" else "flac" if ext == ".flac" else ext.lstrip(".")

    # Base from mutagen info
    desc = TrackTags(filepath=filepath, filesize=os.path.getsize(filepath),
                     file_mtime=os.path.getmtime(filepath))

    if hasattr(f, 'info') and f.info:
        desc.duration = getattr(f.info, 'length', 0.0)
        desc.bitrate = getattr(f.info, 'bitrate', 0) or 0
        desc.sample_rate = getattr(f.info, 'sample_rate', 0) or 0
        desc.channels = getattr(f.info, 'channels', 0) or 0

    desc.kind = kind.upper()

    # Read standard tags
    if hasattr(f, 'tags') and f.tags:
        _set_if(desc, f.tags, 'artist', 'title', 'album', 'albumartist',
                'tracknumber', 'discnumber', 'date', 'genre', 'composer',
                'comment', 'lyrics', 'bpm', 'isrc',
                'musicbrainz_trackid', 'musicbrainz_albumid')

    # MP3 specific
    if kind == "mp3" and hasattr(f, 'tags') and f.tags:
        tags = f.tags
        _set_if_txxx(desc, tags, 'tracktotal', 'tracktotal')
        _set_if_txxx(desc, tags, 'disctotal', 'disctotal')

    # FLAC / Vorbis comments
    if kind in ("flac", "ogg", "opus"):
        pass  # handled by the generic tags above

    # Artwork
    has_art, art_mime, art_data = _read_artwork(f, kind)
    desc.has_artwork = has_art
    desc.artwork_mime = art_mime
    desc.artwork_data = art_data

    # Store original snapshot
    desc.original = desc.clone()
    desc.dirty = False

    return desc


def _set_if(target, tags, *keys):
    """Copy tag values from mutagen dict-like tags into target."""
    for key in keys:
        try:
            val = tags.get(key)
        except Exception:
            continue
        if val:
            v = val[0] if isinstance(val, list) else str(val)
            setattr(target, key, str(v))


def _set_if_txxx(target, tags, tag_key, attr):
    """Read TXXX frame from ID3."""
    try:
        for k in tags:
            if k.startswith("TXXX:") and k.lower().endswith(tag_key.lower()):
                val = str(tags[k])
                setattr(target, attr, val)
                return
    except Exception:
        pass
