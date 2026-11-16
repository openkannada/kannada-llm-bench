"""Reading comprehension: Belebele's Kannada questions on FLORES passages (CC BY-SA 4.0)."""

import json
from pathlib import Path

from kbench.suite.items import LETTERS, Check, Item

QUESTION = "Read the passage and answer the question.\n\nQuestion: {question}"
SOURCE = "Belebele kan_Knda (Bandarkar et al. 2023), CC BY-SA 4.0"


def build(path: Path) -> list[Item]:
    """Every question whose 4 options differ; 3 of Belebele's 900 Kannada questions repeat an option."""
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return [
        Item(
            id=f"reading-{i:04d}",
            task="reading",
            kind="belebele",
            passage=row["flores_passage"],
            question=QUESTION.format(question=row["question"]),
            choices=tuple(row[f"mc_answer{n}"] for n in range(1, 5)),
            answers=(LETTERS[int(row["correct_answer_num"]) - 1],),
            check=Check.HUMAN,
            source=SOURCE,
            meta={"link": row["link"], "question_number": str(row["question_number"])},
        )
        for i, row in enumerate(rows, start=1)
        if len({row[f"mc_answer{n}"] for n in range(1, 5)}) == 4
    ]
