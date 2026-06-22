"""Genre taxonomy — map genres to families for grouping and visualization."""

# Family → genre keywords (lowercase matching)
FAMILY_MAP = {
    "Rock": [
        "rock", "rock n roll", "alternative rock", "indie rock", "hard rock",
        "classic rock", "blues rock", "garage rock", "psych rock", "stoner rock",
        "surf rock", "desert rock", "krautrock", "math rock", "post-rock",
    ],
    "Pop": [
        "pop", "synth pop", "electropop", "dream pop", "indie pop",
        "art pop", "chamber pop", "baroque pop", "power pop", "j-pop", "k-pop",
        "britpop", "bubblegum", "dance pop", "teen pop",
    ],
    "Electronic": [
        "electronic", "electronica", "techno", "house", "trance", "dubstep",
        "idm", "ambient", "downtempo", "breaks", "jungle", "drum", "ebm",
        "industrial", "electro", "synth", "vaporwave", "chiptune",
        "garage", "grime", "minimal", "deep house", "tech house",
        "trip-hop", "chillout", "lounge", "new age", "darkwave",
        "lo-fi", "breakbeat", "dnb",
    ],
    "Jazz": [
        "jazz", "swing", "bebop", "cool jazz", "fusion", "smooth jazz",
        "acid jazz", "free jazz", "hard bop", "modal", "latin jazz",
        "bossa nova", "bossa", "ragtime", "dixieland", "big band",
    ],
    "Classical": [
        "classical", "orchestral", "symphony", "opera", "baroque",
        "chamber", "sonata", "concerto", "neoclassical", "contemporary classical",
        "romantic", "modern classical", "minimalism", "choral", "renaissance",
        "medieval", "gregorian", "avant-garde",
    ],
    "Hip-Hop / Rap": [
        "hip-hop", "hip hop", "rap", "trap", "grime", "gangsta",
        "east coast", "west coast", "southern", "boom bap", "drill",
        "conscious", "crunk", "instrumental hip",
    ],
    "Metal": [
        "metal", "heavy metal", "death metal", "black metal", "thrash",
        "doom", "progressive metal", "power metal", "speed metal",
        "sludge", "grindcore", "metalcore", "nu metal", "djent",
        "groove metal", "folk metal", "symphonic metal", "gothic metal",
    ],
    "Punk": [
        "punk", "hardcore punk", "post-punk", "punk rock", "pop punk",
        "skate punk", "anarcho", "crust", "oi", "emo", "screamo",
        "post-hardcore", "new wave", "no wave",
    ],
    "Folk / Americana": [
        "folk", "americana", "bluegrass", "country", "singer-songwriter",
        "traditional folk", "celtic", "roots", "old-time", "gospel",
        "spiritual", "protest", "neofolk", "freak folk",
    ],
    "R&B / Soul": [
        "r&b", "soul", "funk", "disco", "motown", "neo soul", "funk",
        "philly soul", "quiet storm", "gospel", "blues",
    ],
    "Latin": [
        "latin", "salsa", "bachata", "merengue", "reggaeton", "cumbia",
        "bossa nova", "samba", "mpb", "tango", "ranchera", "norteño",
        "corrido", "flamenco", "bolero", "mambo", "cha cha", "dembow",
    ],
    "Reggae / Dub": [
        "reggae", "dub", "ska", "rocksteady", "dancehall", "ragga",
        "lover's rock", "roots reggae", "reggaeton",
    ],
    "Soundtrack / Score": [
        "soundtrack", "score", "film music", "cinematic", "anime",
        "video game", "musical", "theme",
    ],
    "Experimental / Avant-garde": [
        "experimental", "avant-garde", "noise", "drone", "musique concrete",
        "electroacoustic", "sound art", "field recording", "plunderphonics",
    ],
    "World": [
        "world", "afrobeat", "highlife", "rai", "qawwali", "bhangra",
        "klezmer", "fado", "rebetiko", "gamelan", "taiko", "kabuki",
    ],
}


def get_family(genre_name: str) -> str:
    """Return the taxonomic family for a genre name."""
    key = genre_name.lower()
    for family, keywords in FAMILY_MAP.items():
        for kw in keywords:
            if kw in key or key in kw:
                return family
    return "Other"


def get_family_display(family: str) -> str:
    """Return a display-safe family name."""
    return family


# Mood / energy hints for common genres
GENRE_CHIPS = {
    "synth pop": {"energy": "medium", "electronic": 0.8, "organic": 0.2,
                  "mood": ["melódico", "nocturno", "retro"]},
    "post-punk": {"energy": "medium-high", "electronic": 0.3, "organic": 0.7,
                  "mood": ["oscuro", "angular", "urbano"]},
    "ambient": {"energy": "low", "electronic": 0.9, "organic": 0.1,
                "mood": ["etéreo", "calmo", "espacial"]},
    "techno": {"energy": "high", "electronic": 1.0, "organic": 0.0,
               "mood": ["repetitivo", "industrial", "nocturno"]},
    "rock": {"energy": "medium-high", "electronic": 0.2, "organic": 0.8,
             "mood": ["enérgico", "clásico"]},
    "jazz": {"energy": "low-medium", "electronic": 0.1, "organic": 0.9,
             "mood": ["sofisticado", "cálido", "improvisado"]},
    "classical": {"energy": "variable", "electronic": 0.0, "organic": 1.0,
                  "mood": ["refinado", "histórico"]},
    "hip-hop": {"energy": "medium-high", "electronic": 0.5, "organic": 0.5,
                "mood": ["rítmico", "urbano"]},
    "metal": {"energy": "very-high", "electronic": 0.3, "organic": 0.7,
              "mood": ["intenso", "agresivo", "oscuro"]},
    "folk": {"energy": "low-medium", "electronic": 0.0, "organic": 1.0,
             "mood": ["acústico", "narrativo"]},
}


def get_mood_hints(genre_name: str) -> dict:
    key = genre_name.lower()
    if key in GENRE_CHIPS:
        return GENRE_CHIPS[key]
    return {"energy": "unknown", "electronic": 0.5, "organic": 0.5, "mood": []}
