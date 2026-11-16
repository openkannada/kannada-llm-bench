"""Kannada words drawn from licensed text."""

import bz2
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

KANNADA_WORD = re.compile(r"[ಀ-೥ೱ-೿‌‍]+")
OLD_LETTERS = ("ೞ", "ಱ")


def kannada_words(texts: Iterable[str]) -> Counter[str]:
    """Runs of Kannada letters and signs, without Kannada digits."""
    counts: Counter[str] = Counter()
    for text in texts:
        counts.update(KANNADA_WORD.findall(text))
    return counts


def write_counts(path: Path, counts: Counter[str], header: str) -> None:
    rows = sorted(counts.items(), key=lambda wn: (-wn[1], wn[0]))
    path.write_text(header + "".join(f"{w}\t{n}\n" for w, n in rows), encoding="utf-8")


def read_counts(path: Path) -> Counter[str]:
    rows = (line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line[:1] != "#")
    return Counter({w: int(n) for w, n in rows})


def old_kannada_words(dump: Path) -> Counter[str]:
    """Words with ೞ or ಱ in a MediaWiki XML dump."""
    with bz2.open(dump, "rt", encoding="utf-8") as f:
        lines = (line for line in f if any(c in line for c in OLD_LETTERS))
        counts = kannada_words(lines)
    return Counter({w: n for w, n in counts.items() if any(c in w for c in OLD_LETTERS)})
