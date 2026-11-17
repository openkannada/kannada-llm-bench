# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Old and new orthography: the letters ೞ and ಱ, which modern Kannada writes ಳ and ರ."""

import random
from collections import Counter
from collections.abc import Sequence

from kbench.suite.items import Check, Item, multiple_choice
from kbench.suite.tools import Oracle

SOURCE = "Old Kannada words from Kannada Wikisource (CC BY-SA 4.0); answers computed with kannadi"
SPOT_SOURCE = f"{SOURCE}; modern words from WMT24++ (Apache 2.0)"
WRONG_LETTERS = ({"ೞ": "ಲ", "ಱ": "ಳ"}, {"ೞ": "ಡ", "ಱ": "ಡ"}, {"ೞ": "ರ", "ಱ": "ಲ"})
MODERNIZE = (
    "This word is written in Old Kannada letters. Which option writes the same word with the letters "
    "modern Kannada uses, changing only the letters that are no longer used?\n\nWord: {word}"
)
SPOT = "Which of these words contains a letter that modern Kannada no longer uses?"
MIN_ATTESTATIONS = 3


def _respell(word: str, letters: dict[str, str]) -> str:
    return "".join(letters.get(c, c) for c in word)


RARE_MODERN_LETTERS = set("ಙಞಋಃಔಘಝಢಠಛಫಥಐಈಊಓಷ")


def build(
    oracle: Oracle, old_words: Counter[str], modern_words: Sequence[str], per_kind: int = 80
) -> list[Item]:
    """Old words attested at least 3 times. In the spotting items the other options are modern
    words of about the same length that each have an uncommon letter still in use, so the old
    word is not simply the odd one out."""
    old = sorted(w for w, n in old_words.items() if n >= MIN_ATTESTATIONS and len(w) >= 3)
    modern = oracle.modernize(old)
    rng = random.Random("orthography")
    items = []
    usable = [(w, m) for w, m in zip(old, modern, strict=True) if m != w]
    for n, (word, answer) in enumerate(rng.sample(usable, per_kind), start=1):
        wrong = list(dict.fromkeys(_respell(word, letters) for letters in WRONG_LETTERS))
        choices, letter = multiple_choice(answer, wrong, rng)
        items.append(
            Item(
                id=f"orthography-modernize-{n:04d}",
                task="orthography",
                kind="modernize",
                question=MODERNIZE.format(word=word),
                choices=choices,
                answers=(letter,),
                check=Check.COMPUTED,
                source=SOURCE,
                meta={"old": word},
            )
        )
    pool = sorted({w for w in modern_words if RARE_MODERN_LETTERS & set(w) and "\u200c" not in w})
    clean = [w for w, has in zip(pool, oracle.has_old(pool), strict=True) if not has]
    # Modern words rarely end in ಂ, so an old word ending in it would stand out.
    spot = [(w, m) for w, m in usable if not w.endswith("ಂ")]
    for n, (word, _) in enumerate(rng.sample(spot, per_kind), start=1):
        similar = sorted((abs(len(m) - len(word)), m) for m in clean)
        others = rng.sample([m for _, m in similar[:30]], 3)
        choices, letter = multiple_choice(word, others, rng)
        items.append(
            Item(
                id=f"orthography-spot-old-{n:04d}",
                task="orthography",
                kind="spot-old",
                question=SPOT,
                choices=choices,
                answers=(letter,),
                check=Check.COMPUTED,
                source=SPOT_SOURCE,
                meta={"old": word},
            )
        )
    return items
