"""Genre normalizer — clean, deduplicate, and canonicalize genre tags."""
import re

# Delimiter patterns for multi-genre strings
_DELIM_RE = re.compile(r"\s*[,;/|&+]\s*")

# Common aliases mapped to canonical names
_ALIASES = {
    "synthpop": "Synth pop",
    "synth pop": "Synth pop",
    "synth-pop": "Synth pop",
    "electropop": "Electropop",
    "electro pop": "Electropop",
    "postpunk": "Post-punk",
    "post punk": "Post-punk",
    "punk rock": "Punk rock",
    "hiphop": "Hip-Hop",
    "hip hop": "Hip-Hop",
    "rnb": "R&B",
    "r&b": "R&B",
    "randb": "R&B",
    "alt rock": "Alternative rock",
    "alternative": "Alternative rock",
    "indie rock": "Indie rock",
    "indie pop": "Indie pop",
    "dream pop": "Dream pop",
    "shoegaze": "Shoegaze",
    "shoegazing": "Shoegaze",
    "prog rock": "Progressive rock",
    "progressive": "Progressive rock",
    "prog": "Progressive rock",
    "folk rock": "Folk rock",
    "hard rock": "Hard rock",
    "classic rock": "Classic rock",
    "blues rock": "Blues rock",
    "death metal": "Death metal",
    "black metal": "Black metal",
    "heavy metal": "Heavy metal",
    "thrash metal": "Thrash metal",
    "doom metal": "Doom metal",
    "speed metal": "Speed metal",
    "power metal": "Power metal",
    "dark wave": "Darkwave",
    "new wave": "New wave",
    "post rock": "Post-rock",
    "trip hop": "Trip-hop",
    "drum n bass": "Drum & Bass",
    "drum and bass": "Drum & Bass",
    "d&b": "Drum & Bass",
    "dnb": "Drum & Bass",
    "art rock": "Art rock",
    "noise": "Noise",
    "ambient": "Ambient",
    "industrial": "Industrial",
    "ebm": "EBM",
    "techno": "Techno",
    "house": "House",
    "deep house": "Deep house",
    "tech house": "Tech house",
    "minimal": "Minimal",
    "idm": "IDM",
    "breaks": "Breakbeat",
    "breakbeat": "Breakbeat",
    "jungle": "Jungle",
    "uk garage": "UK Garage",
    "garage": "UK Garage",
    "dubstep": "Dubstep",
    "grime": "Grime",
    "vaporwave": "Vaporwave",
    "chiptune": "Chiptune",
    "lo fi": "Lo-fi",
    "lofi": "Lo-fi",
    "neoclassical": "Neoclassical",
    "contemporary classical": "Contemporary classical",
    "baroque": "Baroque",
    "orchestral": "Orchestral",
    "chamber": "Chamber music",
    "opera": "Opera",
    "smooth jazz": "Smooth jazz",
    "fusion": "Jazz fusion",
    "acid jazz": "Acid jazz",
    "bossa nova": "Bossa nova",
    "mpb": "MPB",
    "samba": "Samba",
    "reggaeton": "Reggaeton",
    "salsa": "Salsa",
    "bachata": "Bachata",
    "cumbia": "Cumbia",
    "ranchera": "Ranchera",
    "norteño": "Norteño",
    "corrido": "Corrido",
    "flamenco": "Flamenco",
    "world": "World",
    "afrobeat": "Afrobeat",
    "funk": "Funk",
    "soul": "Soul",
    "gospel": "Gospel",
    "blues": "Blues",
    "disco": "Disco",
    "country": "Country",
    "bluegrass": "Bluegrass",
    "americana": "Americana",
    "soundtrack": "Soundtrack",
    "score": "Score",
    "experimental": "Experimental",
    "avant garde": "Avant-garde",
    "avant-garde": "Avant-garde",
    "new age": "New Age",
    "downtempo": "Downtempo",
    "chill": "Chillout",
    "chillout": "Chillout",
    "lounge": "Lounge",
    "easy listening": "Easy listening",
    "christmas": "Christmas",
    "xmas": "Christmas",
    "holiday": "Holiday",
    "spoken word": "Spoken word",
    "audiobook": "Audiobook",
    "podcast": "Podcast",
    "radio": "Radio",
    "live": "Live",
    "remix": "Remix",
    "instrumental": "Instrumental",
    "acoustic": "Acoustic",
}


def normalize_genre_name(raw: str) -> str:
    """Normalize a single genre name: strip, clean, canonicalize aliases."""
    name = raw.strip()
    if not name:
        return ""
    # Title case but preserve special words
    key = name.lower()
    if key in _ALIASES:
        return _ALIASES[key]

    # Clean up common patterns
    name = re.sub(r"\s+", " ", name)
    name = name.replace("_", " ")
    # Capitalize words (keep hyphenated parts)
    parts = []
    for part in name.split("-"):
        parts.append(part.strip().title())
    name = "-".join(parts)
    # Fix common capitalization issues
    name = name.replace("And", "and").replace("Of", "of").replace("In", "in")
    name = name.replace("Or", "or").replace("The", "the")
    # Fix start of string
    if name.startswith("And "):
        name = "and" + name[3:]
    if name.startswith("Of "):
        name = "of" + name[2:]
    return name


def split_genres(raw: str) -> list[str]:
    """Split a multi-genre string into individual genre names."""
    if not raw or not raw.strip():
        return []
    parts = _DELIM_RE.split(raw)
    result = []
    for p in parts:
        if p.strip():
            result.append(normalize_genre_name(p))
    return result


def canonicalize_genre(raw: str) -> str:
    """Return the canonical single genre name from a raw tag."""
    return normalize_genre_name(raw)


def genre_key(name: str) -> str:
    """Create a stable key from a genre name."""
    return name.lower().replace(" ", "_").replace("-", "_").replace("/", "_").replace("&", "and")


def detect_dirty_genres(items) -> list[str]:
    """Find genre strings that have multiple values or non-standard formatting."""
    dirty = set()
    for item in items:
        genre = getattr(item, 'genre', '') or ''
        if not genre:
            continue
        if any(d in genre for d in (',', ';', '/', '|', '&')):
            dirty.add(genre)
        if genre != normalize_genre_name(genre):
            dirty.add(genre)
    return sorted(dirty)
