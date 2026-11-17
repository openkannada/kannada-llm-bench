# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""How well strategies that ignore Kannada score on the multiple-choice items: a floor that a
model's score should be read against, alongside chance."""

import csv
from collections import Counter, defaultdict
from collections.abc import Callable, Sequence
from difflib import SequenceMatcher
from pathlib import Path

from kbench.suite.items import LETTERS, Item

Strategy = Callable[[Sequence[str]], int]


def _similarity(options: Sequence[str], i: int) -> float:
    return sum(SequenceMatcher(None, options[i], other).ratio() for j, other in enumerate(options) if j != i)


STRATEGIES: dict[str, Strategy] = {
    "longest": lambda o: max(range(len(o)), key=lambda i: (len(o[i]), -i)),
    "shortest": lambda o: min(range(len(o)), key=lambda i: (len(o[i]), i)),
    "most similar to the rest": lambda o: max(range(len(o)), key=lambda i: (_similarity(o, i), -i)),
    "least similar to the rest": lambda o: min(range(len(o)), key=lambda i: (_similarity(o, i), i)),
}


def scores(items: Sequence[Item]) -> dict[str, dict[str, float]]:
    """For each kind, the share of items each strategy gets right, including the best single letter."""
    by_kind: dict[str, list[Item]] = defaultdict(list)
    for item in items:
        if item.is_choice:
            by_kind[item.kind].append(item)
    out = {}
    for kind, group in by_kind.items():
        result = {"best single letter": max(Counter(i.answers[0] for i in group).values()) / len(group)}
        for name, pick in STRATEGIES.items():
            result[name] = sum(LETTERS[pick(i.choices)] == i.answers[0] for i in group) / len(group)
        out[kind] = result
    return out


def write(path: Path, table: dict[str, dict[str, float]]) -> None:
    names = ["best single letter", *STRATEGIES]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["kind", *names, "best"])
        for kind, result in table.items():
            writer.writerow([kind, *(f"{result[n]:.3f}" for n in names), f"{max(result.values()):.3f}"])
