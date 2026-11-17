# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Build every item file from its sources and answer-key programs."""

import subprocess
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from kbench.sources import BELEBELE, WIKISOURCE
from kbench.suite import grammar, numbers, orthography, reading, translit
from kbench.suite.items import Item, balance, problems, write
from kbench.suite.tools import Kspell, Oracle
from kbench.suite.words import kannada_words, old_kannada_words, read_counts, write_counts
from kbench.tokentax import wmt

ITEMS = Path("suite/items")
LEMMAS = Path("suite/lemmas.tsv")
OLD_WORDS = Path("suite/old-kannada-words.tsv")
OLD_WORDS_HEADER = (
    "# Words with the Old Kannada letters ೞ or ಱ in Kannada Wikisource, dump of 1 November 2026\n"
    "# (CC BY-SA 4.0), seen at least 3 times, with their counts. Written by kbench suite-old-words.\n"
)


def extract_old_words(out: Path = OLD_WORDS) -> int:
    counts = old_kannada_words(WIKISOURCE.fetch())
    kept = Counter({w: n for w, n in counts.items() if n >= orthography.MIN_ATTESTATIONS})
    write_counts(out, kept, OLD_WORDS_HEADER)
    return len(kept)


@dataclass(frozen=True)
class Tools:
    oracle: Oracle
    kspell: Kspell | None


def build_all(tools: Tools, tasks: set[str]) -> dict[str, list[Item]]:
    """The items of each requested task. Grammar needs kspell; the other tasks need only the oracle.
    Reading items keep Belebele's option order; the generated ones are balanced."""
    builders = {
        "reading": lambda: reading.build(BELEBELE.fetch()),
        "translit": lambda: translit.build(tools.oracle, _wmt_words()),
        "numbers": numbers.build,
        "orthography": lambda: orthography.build(tools.oracle, read_counts(OLD_WORDS), _wmt_words()),
        "grammar": lambda: grammar.build(_need(tools.kspell), grammar.read_lemmas(LEMMAS)),
    }
    built = {task: builders[task]() for task in builders if task in tasks}
    return {task: items if task == "reading" else balance(items) for task, items in built.items()}


@cache
def _wmt_words() -> list[str]:
    return sorted(kannada_words(s.kannada for s in wmt.load()))


def check_kannada_spell(dictionary: Path, allow_other: bool = False) -> None:
    """Stop unless the dictionary comes from the kannada-spell commit the grammar items name."""
    head = subprocess.run(
        ["git", "-C", str(dictionary.parent), "rev-parse", "--short=7", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if head != grammar.KANNADA_SPELL and not allow_other:
        raise SystemExit(
            f"kannada-spell is at {head or 'an unknown commit'}, the grammar items pin "
            f"{grammar.KANNADA_SPELL}; check it out, or pass --any-kannada-spell and update the pin"
        )


def _need(kspell: Kspell | None) -> Kspell:
    if kspell is None:
        raise SystemExit("grammar items need --kspell and --dictionary from a kannada-spell checkout")
    return kspell


def write_all(built: dict[str, list[Item]], out: Path = ITEMS) -> None:
    for task, items in built.items():
        found = problems(items)
        if found:
            raise ValueError("\n".join(found[:20]))
        print(f"{task}: {write(out / f'{task}.jsonl', items)} items")
