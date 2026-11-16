"""Scores per model and kind, re-scored from the saved replies, with chance and the best shortcut
on the same items."""

import csv
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from kbench.harness import score
from kbench.suite import shortcuts
from kbench.suite.items import Item

FIELDS = (
    "model",
    "task",
    "kind",
    "check",
    "items",
    "correct",
    "accuracy",
    "chance",
    "best_shortcut",
    "no_answer",
)


@dataclass(frozen=True)
class Row:
    model: str
    task: str
    kind: str
    check: str
    items: int
    correct: int
    no_answer: int
    chance: float
    shortcut: float
    """The best score of a strategy that ignores Kannada on these items; chance for exact answers."""

    @property
    def accuracy(self) -> float:
        return self.correct / self.items if self.items else 0.0


def chance(item: Item) -> float:
    return 1 / len(item.choices) if item.is_choice else 0.0


def rows(model: str, replies: dict[str, str], items: Sequence[Item]) -> list[Row]:
    by_kind: dict[tuple[str, str, str], list[Item]] = defaultdict(list)
    for item in items:
        if item.id in replies:
            by_kind[(item.task, item.kind, item.check.value)].append(item)
    out = []
    for (task, kind, check), group in sorted(by_kind.items()):
        answers = [score.parse(i, replies[i.id]) for i in group]
        floor = max(shortcuts.scores(group)[kind].values()) if group[0].is_choice else 0.0
        out.append(
            Row(
                model,
                task,
                kind,
                check,
                len(group),
                sum(score.is_correct(i, a) for i, a in zip(group, answers, strict=True)),
                sum(not a for a in answers),
                chance(group[0]),
                floor,
            )
        )
    return out


def write(path: Path, all_rows: Sequence[Row]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(FIELDS)
        for r in all_rows:
            writer.writerow(
                (
                    r.model,
                    r.task,
                    r.kind,
                    r.check,
                    r.items,
                    r.correct,
                    f"{r.accuracy:.3f}",
                    f"{r.chance:.2f}",
                    f"{r.shortcut:.3f}",
                    r.no_answer,
                )
            )
