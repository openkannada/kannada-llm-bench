"""Kannada script operations the item builders need: joining a stem and a vowel-initial ending."""

VOWEL_SIGNS = {
    "ಅ": "",
    "ಆ": "ಾ",
    "ಇ": "ಿ",
    "ಈ": "ೀ",
    "ಉ": "ು",
    "ಊ": "ೂ",
    "ಋ": "ೃ",
    "ಎ": "ೆ",
    "ಏ": "ೇ",
    "ಐ": "ೈ",
    "ಒ": "ೊ",
    "ಓ": "ೋ",
    "ಔ": "ೌ",
}
SIGNS = set(VOWEL_SIGNS.values()) - {""}


def without_final_vowel(word: str) -> str:
    """The word with its last vowel sign removed, leaving the consonant with its inherent a."""
    return word[:-1] if word and word[-1] in SIGNS else word


def attach(base: str, ending: str) -> str:
    """Join a base ending in a consonant to an ending that starts with an independent vowel,
    writing that vowel as a sign: ಇಪ್ಪತ್ತ + ಒಂದು = ಇಪ್ಪತ್ತೊಂದು."""
    if not ending or ending[0] not in VOWEL_SIGNS:
        return base + ending
    return base + VOWEL_SIGNS[ending[0]] + ending[1:]
