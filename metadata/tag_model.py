"""Track tags data model — in-memory representation for the metadata editor."""
from dataclasses import dataclass, field


@dataclass
class TrackTags:
    filepath: str
    title: str = ""
    artist: str = ""
    album: str = ""
    albumartist: str = ""
    tracknumber: str = ""
    tracktotal: str = ""
    discnumber: str = ""
    disctotal: str = ""
    date: str = ""
    genre: str = ""
    composer: str = ""
    comment: str = ""
    lyrics: str = ""
    bpm: str = ""
    isrc: str = ""
    musicbrainz_trackid: str = ""
    musicbrainz_albumid: str = ""

    # Technical info (read-only)
    kind: str = ""
    bitrate: int = 0
    sample_rate: int = 0
    channels: int = 0
    duration: float = 0.0
    filesize: int = 0
    file_mtime: float = 0.0

    has_artwork: bool = False
    artwork_mime: str = ""
    artwork_data: bytes | None = None

    # State
    dirty: bool = False
    error: str = ""
    original: "TrackTags | None" = None

    # For batch edit storage, shallow copy per-field
    FIELD_NAMES = [
        "title", "artist", "album", "albumartist",
        "tracknumber", "tracktotal", "discnumber", "disctotal",
        "date", "genre", "composer", "comment", "lyrics",
        "bpm", "isrc", "musicbrainz_trackid", "musicbrainz_albumid",
        "has_artwork",
    ]

    def mark_dirty(self):
        self.dirty = True

    def revert(self):
        if self.original:
            for f in self.FIELD_NAMES:
                setattr(self, f, getattr(self.original, f))
            self.dirty = False

    def clone(self) -> "TrackTags":
        return TrackTags(
            filepath=self.filepath,
            title=self.title, artist=self.artist, album=self.album,
            albumartist=self.albumartist, tracknumber=self.tracknumber,
            tracktotal=self.tracktotal, discnumber=self.discnumber,
            disctotal=self.disctotal, date=self.date, genre=self.genre,
            composer=self.composer, comment=self.comment, lyrics=self.lyrics,
            bpm=self.bpm, isrc=self.isrc,
            musicbrainz_trackid=self.musicbrainz_trackid,
            musicbrainz_albumid=self.musicbrainz_albumid,
            kind=self.kind, bitrate=self.bitrate, sample_rate=self.sample_rate,
            channels=self.channels, duration=self.duration, filesize=self.filesize,
            file_mtime=self.file_mtime,
            has_artwork=self.has_artwork, artwork_mime=self.artwork_mime,
            artwork_data=self.artwork_data,
            dirty=False, error=self.error, original=self,
        )
