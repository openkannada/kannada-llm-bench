"""Transliteration between Kannada script and ISO 15919, with kannadi as the answer key."""

import random
from collections.abc import Sequence

from kbench.suite.items import Check, Item
from kbench.suite.tools import Oracle

SOURCE = "Words from the Kannada side of WMT24++ (Apache 2.0); answers computed with kannadi"
TO_LATIN = (
    "Write this Kannada word in ISO 15919 transliteration, with diacritics. "
    "For example, ಕನ್ನಡ is kannaḍa and ಬೆಂಗಳೂರು is beṁgaḷūru.\n\nWord: {word}"
)
TO_KANNADA = (
    "Write this ISO 15919 transliteration in Kannada script. "
    "For example, kannaḍa is ಕನ್ನಡ and beṁgaḷūru is ಬೆಂಗಳೂರು.\n\nTransliteration: {word}"
)


def build(oracle: Oracle, words: Sequence[str], per_kind: int = 100) -> list[Item]:
    """Words that round-trip exactly, so both directions have 1 right answer."""
    pool = sorted({w for w in words if len(w) >= 4 and "‌" not in w and "‍" not in w})
    latin = oracle.translit(pool, "kannada", "iso15919")
    back = oracle.translit(latin, "iso15919", "kannada")
    pairs = [(k, lat) for k, lat, b in zip(pool, latin, back, strict=True) if b == k]
    rng = random.Random("translit")
    chosen = rng.sample(pairs, 2 * per_kind)
    items = []
    for n, (kannada, iso) in enumerate(chosen[:per_kind], start=1):
        items.append(
            Item(
                id=f"translit-to-latin-{n:04d}",
                task="translit",
                kind="to-latin",
                question=TO_LATIN.format(word=kannada),
                answers=(iso,),
                check=Check.COMPUTED,
                source=SOURCE,
                meta={"kannada": kannada},
            )
        )
    for n, (kannada, iso) in enumerate(chosen[per_kind:], start=1):
        items.append(
            Item(
                id=f"translit-to-kannada-{n:04d}",
                task="translit",
                kind="to-kannada",
                question=TO_KANNADA.format(word=iso),
                answers=(kannada,),
                check=Check.COMPUTED,
                source=SOURCE,
                meta={"iso": iso},
            )
        )
    return items
