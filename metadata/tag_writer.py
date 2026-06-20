"""Tag writer — saves modified tags back to audio files using Mutagen."""
import os

from metadata.tag_model import TrackTags

try:
    import mutagen
    from mutagen.flac import FLAC, Picture
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TPE2, TRCK, TPOS, TDRC, TCON, TCOM, COMM, USLT, TBPM, TSRC, TXXX
    from mutagen.oggopus import OggOpus
    from mutagen.oggvorbis import OggVorbis
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.easyid3 import EasyID3
    from mutagen.aiff import AIFF
    from mutagen.wave import WAVE
    _mutagen_available = True
except ImportError:
    _mutagen_available = False


_MUTAGEN_KEY_MAP = {
    "title": "title",
    "artist": "artist",
    "album": "album",
    "albumartist": "albumartist",
    "tracknumber": "tracknumber",
    "discnumber": "discnumber",
    "date": "date",
    "genre": "genre",
    "composer": "composer",
    "comment": "comment",
    "lyrics": "lyrics",
    "bpm": "bpm",
    "isrc": "isrc",
    "musicbrainz_trackid": "musicbrainz_trackid",
    "musicbrainz_albumid": "musicbrainz_albumid",
}

_MP4_KEY_MAP = {
    "title": "\xa9nam",
    "artist": "\xa9ART",
    "album": "\xa9alb",
    "albumartist": "aART",
    "tracknumber": "trkn",
    "discnumber": "disk",
    "date": "\xa9day",
    "genre": "\xa9gen",
    "composer": "\xa9wrt",
    "comment": "\xa9cmt",
    "bpm": "tmpo",
}


def write_tags(tags: TrackTags) -> bool:
    """Write modified tags back to the audio file. Returns True on success."""
    if not os.path.isfile(tags.filepath):
        return False

    if not _mutagen_available:
        return False

    try:
        f = mutagen.File(tags.filepath)
        if f is None:
            return False

        ext = os.path.splitext(tags.filepath)[1].lower()
        kind = "mp3" if ext == ".mp3" else "flac" if ext == ".flac" else ext.lstrip(".")

        # Write tag fields
        for attr, mut_key in _MUTAGEN_KEY_MAP.items():
            val = getattr(tags, attr, "")
            if val:
                _set_tag(f, kind, mut_key, val)

        # Artwork — replace if modified
        if tags.has_artwork and tags.artwork_data:
            _set_artwork(f, kind, tags.artwork_data, tags.artwork_mime or "image/jpeg")

        f.save()
        tags.dirty = False
        tags.error = ""
        return True

    except Exception as e:
        tags.error = str(e)
        return False


def _set_tag(f, kind: str, key: str, value: str):
    """Set a single tag value on the mutagen file object."""
    if not value:
        return

    if kind in ("flac", "ogg", "opus"):
        if hasattr(f, 'tags'):
            f.tags[key] = value
    elif kind == "mp3":
        _set_mp3_tag(f, key, value)
    elif kind in ("mp4", "m4a"):
        mp4_key = _MP4_KEY_MAP.get(key)
        if mp4_key and hasattr(f, 'tags'):
            if mp4_key in ("trkn", "disk"):
                parts = value.split("/")
                nums = [(int(p) if p.isdigit() else 0) for p in parts[:2]]
                f.tags[mp4_key] = [tuple(nums)]
            else:
                f.tags[mp4_key] = [value]


def _set_mp3_tag(f, key: str, value: str):
    """Set ID3 tag on MP3 file."""
    if f.tags is None:
        f.add_tags()

    frame_map = {
        "title": TIT2,
        "artist": TPE1,
        "album": TALB,
        "albumartist": TPE2,
        "tracknumber": TRCK,
        "discnumber": TPOS,
        "date": TDRC,
        "genre": TCON,
        "composer": TCOM,
        "comment": COMM,
        "lyrics": USLT,
        "bpm": TBPM,
        "isrc": TSRC,
    }

    frame_cls = frame_map.get(key)
    if frame_cls:
        if frame_cls in (COMM,):
            f.tags.add(frame_cls(encoding=3, lang="spa", desc="", text=[value]))
        elif frame_cls in (USLT,):
            f.tags.add(frame_cls(encoding=3, lang="spa", desc="", text=value))
        else:
            f.tags.add(frame_cls(encoding=3, text=[value]))
    elif key in ("musicbrainz_trackid", "musicbrainz_albumid", "tracktotal", "disctotal"):
        f.tags.add(TXXX(encoding=3, desc=key, text=[value]))


def _set_artwork(f, kind: str, data: bytes, mime: str = "image/jpeg"):
    """Set embedded artwork on the file."""
    try:
        if kind == "mp3":
            if f.tags is None:
                f.add_tags()
            f.tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=data))
        elif kind == "flac":
            pic = Picture()
            pic.type = 3
            pic.mime = mime
            pic.desc = "Cover"
            pic.data = data
            if not hasattr(f, 'pictures'):
                f.add_picture(pic)
            else:
                f.clear_pictures()
                f.add_picture(pic)
        elif kind in ("mp4", "m4a"):
            fmt = MP4Cover.FORMAT_JPEG if "jpeg" in mime else MP4Cover.FORMAT_PNG
            f.tags["covr"] = [MP4Cover(data, imageformat=fmt)]
    except Exception:
        pass
