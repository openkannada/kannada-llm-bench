# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

import json
import random
from collections import Counter
from pathlib import Path
from typing import ClassVar

import pytest

from kbench.suite import grammar, numbers, orthography, reading
from kbench.suite.items import LETTERS, Check, Item, balance, multiple_choice, problems, read
from kbench.suite.script import attach, without_final_vowel

ITEMS = Path(__file__).parent.parent / "suite" / "items"
EXPECTED_CHECKS = {
    "reading": {Check.HUMAN},
    "grammar": {Check.NEEDS_READER},
    "translit": {Check.COMPUTED},
    "numbers": {Check.COMPUTED, Check.NEEDS_READER},
    "orthography": {Check.COMPUTED},
}


def choice_item(kind: str, choices: tuple[str, ...], answer: str) -> Item:
    return Item(
        id=f"{kind}-{answer}-{choices[0]}",
        task="t",
        kind=kind,
        question="q",
        answers=(answer,),
        check=Check.COMPUTED,
        source="s",
        choices=choices,
    )


def test_multiple_choice_puts_the_correct_option_under_its_letter():
    choices, letter = multiple_choice("right", ["w1", "w2", "w3"], random.Random(1))
    assert choices[LETTERS.index(letter)] == "right"
    with pytest.raises(ValueError):
        multiple_choice("right", ["w1", "w1", "w3"], random.Random(1))


def test_balance_spreads_letters_evenly_in_a_shuffled_order():
    items = [choice_item("k", ("a", "b", "c", "d"), "C") for _ in range(40)]
    letters = [i.answers[0] for i in balance(items)]
    assert Counter(letters) == {"A": 10, "B": 10, "C": 10, "D": 10}
    assert letters != list("ABCD" * 10)
    assert all(i.choices[LETTERS.index(i.answers[0])] == "c" for i in balance(items))


def test_problems_finds_bad_items():
    good = choice_item("k", ("a", "b", "c", "d"), "A")
    assert problems([good]) == []
    assert problems([good, good]) == [f"{good.id}: duplicate id"]
    assert problems([choice_item("k", ("a", "a", "c", "d"), "A")])
    assert problems([choice_item("k", ("a", "b", "c", "d"), "E")])


def test_item_json_round_trip():
    item = choice_item("k", ("ಮರ", "b", "c", "d"), "B")
    assert Item.from_json(item.to_json()) == item


def test_attach_writes_the_ending_vowel_as_a_sign():
    assert without_final_vowel("ಮನೆ") == "ಮನ"
    assert without_final_vowel("ಮರ") == "ಮರ"
    assert attach("ಇಪ್ಪತ್ತ", "ಒಂದು") == "ಇಪ್ಪತ್ತೊಂದು"
    assert attach("ಇಪ್ಪತ್ತ", "ಮೂರು") == "ಇಪ್ಪತ್ತಮೂರು"
    assert attach("ಮರದ", "ಅಲ್ಲಿ") == "ಮರದಲ್ಲಿ"


@pytest.mark.parametrize(
    ("n", "words"),
    [
        (9, "ಒಂಬತ್ತು"),
        (11, "ಹನ್ನೊಂದು"),
        (19, "ಹತ್ತೊಂಬತ್ತು"),
        (21, "ಇಪ್ಪತ್ತೊಂದು"),
        (23, "ಇಪ್ಪತ್ತಮೂರು"),
        (25, "ಇಪ್ಪತ್ತೈದು"),
        (26, "ಇಪ್ಪತ್ತಾರು"),
        (27, "ಇಪ್ಪತ್ತೇಳು"),
        (99, "ತೊಂಬತ್ತೊಂಬತ್ತು"),
        (100, "ನೂರು"),
        (125, "ನೂರ ಇಪ್ಪತ್ತೈದು"),
        (999, "ಒಂಬೈನೂರ ತೊಂಬತ್ತೊಂಬತ್ತು"),
        (1000, "ಒಂದು ಸಾವಿರ"),
        (2500, "ಎರಡು ಸಾವಿರದ ಐನೂರು"),
        (12345, "ಹನ್ನೆರಡು ಸಾವಿರದ ಮುನ್ನೂರ ನಲವತ್ತೈದು"),
    ],
)
def test_number_words(n: int, words: str):
    assert numbers.number_words(n) == words


def test_kannada_digits():
    assert numbers.kannada_digits(1956) == "೧೯೫೬"


def test_joins_include_the_augmented_forms():
    assert "ಮರದಲ್ಲಿ" in grammar.joins("ಮರ", "ಅಲ್ಲಿ")
    assert "ಮನೆಯಲ್ಲಿ" in grammar.joins("ಮನೆ", "ಅಲ್ಲಿ")
    assert "ಊರಿನಲ್ಲಿ" in grammar.joins("ಊರು", "ಅಲ್ಲಿ")


class FakeKspell:
    """A paradigm for ಮರ in which 4 forms also carry the accusative, and a dictionary that knows its
    forms and 2 other words that look like joins of ಮರ."""

    READINGS: ClassVar[dict[str, set[str]]] = {
        "ಮರಕ್ಕೆ": {"dat"},
        "ಮರದ": {"gen", "acc"},
        "ಮರದಲ್ಲಿ": {"loc"},
        "ಮರದಿಂದ": {"ins"},
        "ಮರವನ್ನು": {"acc"},
        "ಮರಗಳು": {"pl", "acc"},
        "ಮರಗಳಿಗೆ": {"pl+dat", "acc"},
        "ಮರಗಳಲ್ಲಿ": {"pl+loc", "acc"},
    }
    OTHER_WORDS: ClassVar[set[str]] = {"ಮರನಲ್ಲಿ", "ಮರನಿಂದ"}

    def paradigm(self, lemma: str) -> list[tuple[str, str]]:
        pairs = [(f, f"{lemma}+n+{t}") for f, tags in self.READINGS.items() for t in sorted(tags)]
        return [*pairs, ("ಮರ", "ಮರ+adj")]

    def readings(self, words: list[str]) -> dict[str, set[str]]:
        known = {f: {f"ಮರ+n+{t}" for t in tags} for f, tags in self.READINGS.items()}
        known["ಮರದಿಂದ"] = {"ಮರ+n+ins", "ಮರದು+n+ins"}
        known |= {w: {f"{w}+n"} for w in self.OTHER_WORDS}
        return {w: known.get(w, set()) for w in words}

    def accepted(self, words: list[str]) -> set[str]:
        return {w for w, rs in self.readings(words).items() if rs}


def test_grammar_items_have_1_right_option():
    fake = FakeKspell()
    items = grammar.build(fake, [grammar.Lemma("ಮರ", "n", "tree")])  # type: ignore[arg-type]
    kinds = Counter(i.kind for i in items)
    assert kinds == {"case": 6, "case-recognition": 3, "sandhi": 2}
    assert all("ಮರದಿಂದ" not in i.choices for i in items), "a form of another word too"
    for item in items:
        right = item.choices[LETTERS.index(item.answers[0])]
        wrong = [c for c in item.choices if c != right]
        tag = item.meta["tag"]
        if item.kind == "case-recognition":
            assert right == grammar.CASE_NAMES[tag]
            assert fake.READINGS[item.meta["form"]] == {tag}
        else:
            assert tag in fake.READINGS[right]
            assert tag != "acc" or right == "ಮರವನ್ನು", "the answer should be the form with fewest readings"
            assert all(tag not in fake.READINGS.get(c, set()) for c in wrong)
        if item.kind == "sandhi":
            assert not fake.accepted(wrong)


class FakeOracle:
    def modernize(self, words: list[str]) -> list[str]:
        return [w.replace("ೞ", "ಳ").replace("ಱ", "ರ") for w in words]

    def has_old(self, words: list[str]) -> list[bool]:
        return [("ೞ" in w or "ಱ" in w) for w in words]


def test_orthography_items_have_the_modern_spelling_as_answer():
    old = Counter({"ಅಱಿದು": 5, "ಪೇೞ್ದು": 9, "ಬೞಿಯಂ": 4, "ಮೂಱು": 3, "ತೋಱಿ": 7, "ಉಱದೆ": 2})
    oracle = FakeOracle()
    modern = ["ಸಂಘಟನೆ", "ಮಂಞ", "ಋಷಿ", "ಢಕ್ಕೆ", "ಘಟನೆ", "ಮರ"]
    items = orthography.build(oracle, old, modern, per_kind=4)  # type: ignore[arg-type]
    for item in items:
        right = item.choices[LETTERS.index(item.answers[0])]
        if item.kind == "modernize":
            assert right == oracle.modernize([item.meta["old"]])[0]
        else:
            assert right == item.meta["old"] and sum(oracle.has_old(list(item.choices))) == 1
            assert oracle.modernize([right])[0] not in item.choices, "its own respelling would give it away"
            assert all(orthography.RARE_MODERN_LETTERS & set(c) for c in item.choices if c != right)
    assert "ಉಱದೆ" not in {i.meta["old"] for i in items}


def test_number_word_options_form_a_grid():
    for seed in range(50):
        rng = random.Random(seed)
        value = rng.randrange(11, 100_000)
        values = numbers.grid(value, rng)
        assert values[0] == value and len(set(values)) == 4
        assert all(len(str(v)) == len(str(value)) for v in values)
        differences = sorted(
            sum(a != b for a, b in zip(str(v), str(w), strict=True)) for v in values for w in values if v != w
        )
        assert differences == [1] * 8 + [2] * 4


@pytest.mark.parametrize("task", sorted(EXPECTED_CHECKS))
def test_committed_items_are_well_formed(task: str):
    items = read(ITEMS / f"{task}.jsonl")
    assert items and problems(items) == []
    assert {i.check for i in items} <= EXPECTED_CHECKS[task]
    assert all(i.task == task for i in items)


def test_reading_drops_questions_with_repeated_options(tmp_path: Path):
    def row(n: int, options: list[str]) -> str:
        fields = {f"mc_answer{i}": o for i, o in enumerate(options, start=1)}
        return json.dumps(
            {
                "link": "l",
                "question_number": n,
                "flores_passage": "p",
                "question": "q",
                "correct_answer_num": "2",
                **fields,
            }
        )

    path = tmp_path / "b.jsonl"
    path.write_text(row(1, ["a", "b", "c", "d"]) + "\n" + row(2, ["a", "a", "c", "d"]) + "\n")
    items = reading.build(path)
    assert [(i.id, i.answers) for i in items] == [("reading-0001", ("B",))]


def test_shortcuts_score_each_strategy():
    from kbench.suite import shortcuts

    items = [
        choice_item("k", ("long answer", "b", "c", "d"), "A"),
        choice_item("k", ("a", "b", "c", "long answer"), "B"),
    ]
    table = shortcuts.scores(items)["k"]
    assert table["longest"] == 0.5 and table["best single letter"] == 0.5


def test_committed_shortcuts_match_the_items_and_the_suite_doc(tmp_path: Path):
    from kbench.suite import shortcuts

    items = [i for task in EXPECTED_CHECKS for i in read(ITEMS / f"{task}.jsonl")]
    shortcuts.write(tmp_path / "s.csv", shortcuts.scores(items))
    committed = ITEMS.parent.parent / "results" / "suite-shortcuts.csv"
    assert (tmp_path / "s.csv").read_bytes() == committed.read_bytes()
    rows = {
        line.split(" | ")[0].lstrip("| "): line
        for line in (ITEMS.parent.parent / "docs" / "suite.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("| ")
    }
    labels = {
        "belebele": "Belebele",
        "case": "Case form",
        "verb": "Verb form",
        "case-recognition": "Case recognition",
        "sandhi": "Sandhi",
        "digits-to-words": "Digits to words",
        "modernize": "Modernize",
        "spot-old": "Spot the old letter",
    }
    for kind, result in shortcuts.scores(items).items():
        assert rows[labels[kind]].endswith(f"| {max(result.values()):.0%} |"), kind


def test_singular_nouns_get_no_plural_items():
    fake = FakeKspell()
    plural = grammar.build(fake, [grammar.Lemma("ಮರ", "n", "tree")])  # type: ignore[arg-type]
    singular = grammar.build(fake, [grammar.Lemma("ಮರ", "n", "tree", singular=True)])  # type: ignore[arg-type]
    assert any(i.meta["tag"] in grammar.PLURAL_CELLS for i in plural)
    assert singular and all(i.meta["tag"] not in grammar.PLURAL_CELLS for i in singular)


def test_no_elision_distractor_after_u():
    assert "ಕಾಡಲ್ಲಿ" not in grammar.joins("ಕಾಡು", "ಅಲ್ಲಿ")
    assert "ಮನಲ್ಲಿ" in grammar.joins("ಮನೆ", "ಅಲ್ಲಿ")


def test_digits_to_words_options_are_a_grid():
    items = [i for i in numbers.build(per_kind=20) if i.kind == "digits-to-words"]
    for item in items:
        values = [int(v) for v in item.meta["options"].split()]
        assert [numbers.number_words(v) for v in values] == list(item.choices)
        diffs = sorted(
            sum(a != b for a, b in zip(str(v), str(w), strict=True)) for v in values for w in values if v != w
        )
        assert diffs == [1] * 8 + [2] * 4


def test_variant_spellings_count_as_the_same_word():
    assert {"ಕಾರ್", "ಕಾರು"} <= grammar.spellings("ಕಾರು")
    assert "ಕಣ್" in grammar.spellings("ಕಣ್ಣು")
    assert "ಹೂ" in grammar.spellings("ಹೂವು")
    assert "ಹಸುವು" in grammar.spellings("ಹಸು")
    assert "ಕಾಲ" not in grammar.spellings("ಕಾಲು")


def test_spot_old_leaves_out_old_words_ending_in_anusvara():
    old = Counter({"ಅಱಿದು": 5, "ಪೇೞ್ದು": 9, "ಬೞಿಯಂ": 4, "ಮೂಱು": 3, "ತೋಱಿ": 7})
    items = orthography.build(FakeOracle(), old, ["ಸಂಘಟನೆ", "ಮಂಞ", "ಋಷಿ", "ಢಕ್ಕೆ"], per_kind=4)  # type: ignore[arg-type]
    assert all(not i.meta["old"].endswith("ಂ") for i in items if i.kind == "spot-old")


def test_grammar_build_refuses_an_unpinned_kannada_spell(tmp_path: Path):
    import subprocess

    from kbench.suite import build

    git = [
        "git",
        "-C",
        str(tmp_path),
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@example.com",
        "-c",
        "commit.gpgsign=false",
    ]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "x"], check=True)
    (tmp_path / "dict").mkdir()
    with pytest.raises(SystemExit):
        build.check_kannada_spell(tmp_path / "dict" / "kn_IN")
    build.check_kannada_spell(tmp_path / "dict" / "kn_IN", allow_other=True)


def test_paradigm_keeps_forms_also_read_under_a_variant_spelling():
    class Variant(FakeKspell):
        def readings(self, words: list[str]) -> dict[str, set[str]]:
            found = super().readings(words)
            found["ಮರಕ್ಕೆ"] = {"ಮರ+n+dat", "ಮರವು+n+dat"}
            return found

    p = grammar.paradigm(Variant(), grammar.Lemma("ಮರ", "n", "tree"))  # type: ignore[arg-type]
    assert "ಮರಕ್ಕೆ" in p.readings and "ಮರದಿಂದ" not in p.readings
