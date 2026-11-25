# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

import json
from pathlib import Path

from kbench.harness import prompts, replies, report, sample, score
from kbench.suite.items import Check, Item


def item(
    kind: str = "k",
    choices: tuple[str, ...] = ("a", "b", "c", "d"),
    answers: tuple[str, ...] = ("C",),
    n: int = 0,
) -> Item:
    return Item(
        id=f"{kind}-{n}",
        task="t",
        kind=kind,
        question="Q?",
        answers=answers,
        check=Check.COMPUTED,
        source="s",
        choices=choices,
    )


def test_choice_prompt_lists_lettered_options_and_the_rule():
    text = prompts.user_message(item())
    assert "A. a\nB. b\nC. c\nD. d" in text and prompts.CHOICE_RULE in text


def test_open_prompt_has_the_open_rule_and_the_passage_first():
    text = prompts.user_message(
        Item(
            id="x",
            task="t",
            kind="k",
            question="Q?",
            answers=("x",),
            check=Check.COMPUTED,
            source="s",
            passage="P",
        )
    )
    assert text.startswith("Passage:\nP") and prompts.OPEN_RULE in text


def test_parse_reads_the_first_option_letter():
    mc = item()
    assert score.parse(mc, "C") == "C"
    assert score.parse(mc, "Answer: B.") == "B"
    assert score.parse(mc, "(D) because") == "D"
    assert score.parse(mc, "<think>maybe A</think>\nC") == "C"
    assert score.parse(mc, "I think it is a good one") == ""


def test_parse_and_score_open_answers():
    open_item = item(choices=(), answers=("ಕನ್ನಡ",))
    assert score.parse(open_item, "Answer: ಕನ್ನಡ.\nmore") == "ಕನ್ನಡ"
    assert score.is_correct(open_item, "ಕನ್ನ‌ಡ")
    latin = item(choices=(), answers=("kannaḍa",))
    assert score.is_correct(latin, "Kannaḍa")
    assert not score.is_correct(latin, "kannada")


def test_sample_takes_the_same_items_per_kind_every_time():
    items = [item(kind, n=n) for kind in ("x", "y") for n in range(10)]
    first = sample.per_kind(items, 3)
    assert first == sample.per_kind(items, 3)
    assert [i.kind for i in first].count("x") == 3


def test_report_rescores_replies_with_chance_and_the_shortcut_on_the_same_items():
    items = [item(n=n) for n in range(4)]
    replies = {"k-0": "C", "k-1": "C.", "k-2": "A", "k-3": "no idea"}
    (row,) = report.rows("m", replies, items)
    assert (row.items, row.correct, row.no_answer, row.chance) == (4, 2, 1, 0.25)
    assert row.shortcut == 1.0


def test_read_replies_skips_a_cut_off_last_line(tmp_path: Path):
    path = tmp_path / "m.jsonl"
    path.write_text(json.dumps({"id": "a", "reply": "B"}) + "\n" + '{"id": "b", "rep')
    assert replies.read_replies(path) == {"a": "B"}


def test_parse_takes_the_result_of_an_equation_and_drops_replacement_characters():
    exact = item(choices=(), answers=("೮೦೫೩೫೦",))
    assert score.is_correct(exact, score.parse(exact, "೮೮೫ × ೯೧೦ = ೮೦೫೩೫೦"))
    assert score.is_correct(exact, score.parse(exact, "\ufffd೮೦೫೩೫೦"))


def test_committed_summary_rescores_from_the_committed_replies(tmp_path: Path):
    from kbench.cli import SUITE_TASKS, load_items
    from kbench.harness.models import MODELS

    root = Path(__file__).parent.parent
    items = load_items(list(SUITE_TASKS))
    rows = [
        r
        for m in MODELS
        for r in report.rows(
            m.key, replies.read_replies(root / "results" / "suite" / f"{m.key}.jsonl"), items
        )
    ]
    report.write(tmp_path / "s.csv", rows)
    assert (tmp_path / "s.csv").read_bytes() == (root / "results" / "suite" / "summary.csv").read_bytes()


def test_baselines_doc_matches_the_committed_summary():
    import csv

    root = Path(__file__).parent.parent
    with (root / "results" / "suite" / "summary.csv").open(encoding="utf-8") as f:
        summary = list(csv.DictReader(f))
    readme = (root / "docs" / "baselines.md").read_text(encoding="utf-8").splitlines()
    from kbench.harness.models import MODELS

    models = [m.key for m in MODELS]
    by = {(r["model"], r["kind"]): r for r in summary}
    for kind in {r["kind"] for r in summary}:
        first = by[(models[0], kind)]
        cells = " | ".join(
            f"{int(by[(m, kind)]['correct']) / int(by[(m, kind)]['items']):.0%}" for m in models
        )
        floors = f"{float(first['chance']):.0%} | {float(first['best_shortcut']):.0%}"
        assert any(line.endswith(f"| {cells} | {floors} |") for line in readme), kind
