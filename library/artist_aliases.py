"""Artist aliases — detection, normalization, and persistent alias resolution."""
import json
import os
import re
import unicodedata
from difflib import SequenceMatcher

from library.artist_grouping import ArtistGroup

_ARTICLES_RE = re.compile(r"^(the|a|an|el|la|los|las|le|les|der|die|das)\s+", re.IGNORECASE)
_FEAT_RE = re.compile(
    r"\s+(feat\.?|ft\.?|featuring|with|vs\.?|versus)\s+", re.IGNORECASE)
_COLLAB_RE = re.compile(
    r"\s*[&/,;]\s*|\s+y\s+|\s+e\s+|\s+und\s+|\s+et\s+", re.IGNORECASE)
_PAREN_RE = re.compile(r"\(.*?\)")
_BRACKET_RE = re.compile(r"\[.*?\]")
_SEP_RE = re.compile(r"\s*/\s*")
_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_MULTI_SPACE_RE = re.compile(r"\s+")


def normalize_accents(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_punctuation(name: str) -> str:
    return _PUNCTUATION_RE.sub("", name)


def strip_articles(name: str) -> str:
    return _ARTICLES_RE.sub("", name).strip()


def normalize_artist_alias(name: str) -> str:
    name = str(name or "").strip()
    name = name.lower()
    name = normalize_accents(name)
    name = strip_articles(name)
    name = normalize_punctuation(name)
    name = _MULTI_SPACE_RE.sub(" ", name)
    return name.strip()


def split_artist_names(raw: str) -> list[str]:
    raw = str(raw or "").strip()
    if not raw:
        return []
    raw = _PAREN_RE.sub("", raw)
    raw = _BRACKET_RE.sub("", raw)

    parts = _FEAT_RE.split(raw)
    result = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        sub = _COLLAB_RE.split(p)
        for s in sub:
            s = s.strip()
            if s and s.lower() not in ("", "various", "unknown", "desconocido"):
                result.append(s)
    return result


def detect_featured_artists(raw: str) -> list[str]:
    raw = str(raw or "").strip()
    parts = _FEAT_RE.split(raw)
    if len(parts) <= 1:
        return []
    featured = []
    # parts[0] is the main artist, parts[1:] alternate between separator and featured artist
    for i in range(1, len(parts)):
        p = parts[i].strip()
        if not p or p.lower() in ("feat", "feat.", "ft", "ft.", "featuring", "with", "vs", "vs.", "versus", "", "various", "unknown", "desconocido"):
            continue
        sub = _COLLAB_RE.split(p)
        featured.extend(s.strip() for s in sub if s.strip())
    return featured


def _is_compilation(name: str) -> bool:
    lower = name.lower().strip()
    comp_names = {
        "various artists", "varios artistas", "va", "various", "varios",
        "compilation", "compilacion", "compilación", "soundtrack",
        "banda sonora", "bso", "ost", "unknown artist", "artista desconocido",
    }
    return lower in comp_names


def find_artist_alias_candidates(groups: list[ArtistGroup]) -> list[tuple[str, str, float]]:
    candidates = []
    normalized = {}

    for g in groups:
        norm = normalize_artist_alias(g.display_name)
        if norm in normalized:
            prev = normalized[norm]
            if prev != g.key:
                candidates.append((prev, g.key, 1.0))
        else:
            normalized[norm] = g.key

    norm_names = list(normalized.keys())
    for i in range(len(norm_names)):
        for j in range(i + 1, len(norm_names)):
            a, b = norm_names[i], norm_names[j]
            ratio = SequenceMatcher(None, a, b).ratio()
            if 0.75 <= ratio <= 0.99 and abs(len(a) - len(b)) <= 3:
                candidates.append((normalized[a], normalized[b], round(ratio, 3)))

    seen_pairs = set()
    unique = []
    for k1, k2, score in candidates:
        pair = tuple(sorted([k1, k2]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique.append((k1, k2, score))

    unique.sort(key=lambda x: -x[2])
    return unique


_ALIAS_FILE = ""


def set_alias_path(path: str):
    global _ALIAS_FILE
    _ALIAS_FILE = path


def _get_alias_path() -> str:
    if _ALIAS_FILE:
        return _ALIAS_FILE
    from core.paths import config_dir
    return os.path.join(config_dir(), "artist_aliases.json")


def load_aliases() -> dict[str, str]:
    path = _get_alias_path()
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("aliases", {})
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_aliases(aliases: dict[str, str]):
    path = _get_alias_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"aliases": aliases}, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def resolve_alias(display_name: str, key: str) -> str:
    aliases = load_aliases()
    if key in aliases:
        return aliases[key]
    norm = normalize_artist_alias(display_name)
    if norm in aliases:
        return aliases[norm]
    return key


def add_alias(source_key: str, target_key: str):
    aliases = load_aliases()
    aliases[source_key] = target_key
    save_aliases(aliases)


def remove_alias(source_key: str):
    aliases = load_aliases()
    aliases.pop(source_key, None)
    save_aliases(aliases)
