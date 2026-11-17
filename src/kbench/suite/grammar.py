# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Grammar items built from kannada-spell's paradigms: noun cases, verb forms, case
recognition, and joining a stem to a case ending."""

import random
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from kbench.suite.items import Check, Item, multiple_choice
from kbench.suite.script import attach, without_final_vowel
from kbench.suite.tools import Kspell

KANNADA_SPELL = "a01fe20"
SOURCE = (
    f"Paradigms of kannada-spell {KANNADA_SPELL} (kspell paradigm); lemmas and glosses written for this suite"
)

CASES = {
    "acc": "accusative form (the object)",
    "dat": "dative form ('to' or 'for')",
    "gen": "genitive form ('of')",
    "loc": "locative form ('in' or 'at')",
    "ins": "instrumental form ('by' or 'from')",
    "pl": "plural form",
    "pl+dat": "plural dative form ('to the ___s')",
    "pl+loc": "plural locative form ('in the ___s')",
}
CASE_NAMES = {
    "acc": "Accusative",
    "dat": "Dative",
    "gen": "Genitive",
    "loc": "Locative",
    "ins": "Instrumental",
}
# Imperatives are left out: the paradigms give ಬರಿ for ಬನ್ನಿ.
VERB_FORMS = {
    "past.3sm": "past tense form for 'he' ('he ___ed')",
    "past.3sf": "past tense form for 'she' ('she ___ed')",
    "past.3sn": "past tense form for 'it' ('it ___ed')",
    "past.3p": "past tense form for 'they', of people ('they ___ed')",
    "npst.1s": "present or future form for 'I' ('I ___')",
    "npst.3sm": "present or future form for 'he' ('he ___s')",
    "npst.3p": "present or future form for 'they', of people ('they ___')",
    "npst.neg": "negative present form ('does not ___')",
    "past.neg": "negative past form ('did not ___')",
    "inf": "infinitive ('to ___')",
    "cp": "conjunctive participle ('having ___ed')",
    "cond": "conditional form ('if ___')",
    "deb": "form for obligation ('must ___')",
}
ENDINGS = {"loc": "ಅಲ್ಲಿ", "ins": "ಇಂದ", "acc": "ಅನ್ನು"}
PLURAL_CELLS = {"pl", "pl+dat", "pl+loc"}


@dataclass(frozen=True)
class Lemma:
    lemma: str
    pos: str
    gloss: str
    singular: bool = False

    def cells(self, cells: dict[str, str]) -> dict[str, str]:
        """The cells to ask about: no plural cells for a singular-only noun."""
        return {t: d for t, d in cells.items() if not (self.singular and t in PLURAL_CELLS)}


@dataclass(frozen=True)
class Paradigm:
    lemma: Lemma
    readings: dict[str, frozenset[str]]
    """Each form and the tags it can carry, for this lemma and part of speech only."""

    def forms_with(self, tag: str) -> list[str]:
        return sorted(form for form, tags in self.readings.items() if tag in tags)

    def answer_for(self, tag: str) -> str | None:
        """The least ambiguous form with this tag, the longest on a tie."""
        forms = self.forms_with(tag)
        return min(forms, key=lambda f: (len(self.readings[f]), -len(f), f)) if forms else None


def read_lemmas(path: Path) -> list[Lemma]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = [line.split("\t") for line in lines if line and line[0] != "#"]
    return [Lemma(r[0], r[1], r[2], singular=r[3:] == ["singular"]) for r in rows]


def spellings(lemma: str) -> set[str]:
    """The lemma and the variant spellings of the same word the dictionary lists as lemmas: ಕಾರ್
    for ಕಾರು, ಕಣ್ for ಕಣ್ಣು, ಹೂ for ಹೂವು, ಹಸುವು for ಹಸು. ಕಾಲ is not one for ಕಾಲು."""
    found = {lemma, lemma + "ವು"}
    if lemma.endswith("ವು"):
        found.add(lemma[:-2])
    if lemma.endswith("ು"):
        found.add(lemma[:-1] + "್")
        if len(lemma) >= 4 and lemma[-3] == "್" and lemma[-4] == lemma[-2]:
            found.add(lemma[:-3] + "್")
    return found


def paradigm(kspell: Kspell, lemma: Lemma) -> Paradigm:
    """The forms of a lemma, without any form the dictionary also reads as another word, such as
    ಕಾಲಕ್ಕೆ, which is a form of ಕಾಲು 'leg' and of ಕಾಲ 'time'."""
    prefix = f"{lemma.lemma}+{lemma.pos}"
    readings: dict[str, set[str]] = defaultdict(set)
    for form, reading in kspell.paradigm(lemma.lemma):
        if reading == prefix or reading.startswith(prefix + "+"):
            readings[form].add(reading[len(prefix) + 1 :])
    everything = kspell.readings(sorted(readings))
    same = spellings(lemma.lemma)
    own = {f for f, rs in everything.items() if all(r.split("+", 1)[0] in same for r in rs)}
    return Paradigm(lemma, {form: frozenset(tags) for form, tags in readings.items() if form in own})


def _form_item(p: Paradigm, tag: str, cells: dict[str, str], kind: str, rng: random.Random) -> Item | None:
    answer = p.answer_for(tag)
    others = sorted({f for t in cells if t != tag for f in p.forms_with(t)} - set(p.forms_with(tag)))
    if answer is None or len(others) < 3:
        return None
    choices, letter = multiple_choice(answer, rng.sample(others, 3), rng)
    noun = kind == "case"
    question = (
        f"Which word is the {cells[tag]} of the Kannada {'noun' if noun else 'verb'} "
        f"{p.lemma.lemma} ('{p.lemma.gloss}')?"
    )
    return Item(
        id="",
        task="grammar",
        kind=kind,
        question=question,
        choices=choices,
        answers=(letter,),
        check=Check.NEEDS_READER,
        source=SOURCE,
        meta={"lemma": p.lemma.lemma, "tag": tag, "form": answer},
    )


def _recognition_item(p: Paradigm, form: str, rng: random.Random) -> Item | None:
    cases = [t for t in p.readings[form] if t in CASE_NAMES]
    if len(cases) != 1 or len(p.readings[form]) != 1:
        return None
    wrong = rng.sample(sorted(n for t, n in CASE_NAMES.items() if t != cases[0]), 3)
    choices, letter = multiple_choice(CASE_NAMES[cases[0]], wrong, rng)
    return Item(
        id="",
        task="grammar",
        kind="case-recognition",
        question=(
            f"In the Kannada word {form}, which case is the noun {p.lemma.lemma} ('{p.lemma.gloss}') in?"
        ),
        choices=choices,
        answers=(letter,),
        check=Check.NEEDS_READER,
        source=SOURCE,
        meta={"lemma": p.lemma.lemma, "tag": cases[0], "form": form},
    )


def joins(stem: str, ending: str) -> list[str]:
    """Ways a learner might join a stem and a vowel-initial ending: elision, a glide, or an
    augment. Usually 1 of them is right. Elision is left out after ು, where the short form
    (ಕಾಡಲ್ಲಿ for ಕಾಡಿನಲ್ಲಿ) is common in writing and so not wrong."""
    base = without_final_vowel(stem)
    candidates = [] if stem.endswith("ು") else [attach(base, ending)]
    candidates += [attach(stem + c, ending) for c in ("ಯ", "ವ", "ದ", "ನ")]
    if base != stem:
        candidates.append(attach(base + "ಿನ", ending))
    return list(dict.fromkeys(c for c in candidates if c != stem))


def _sandhi_item(p: Paradigm, tag: str, rejected: set[str], rng: random.Random) -> Item | None:
    answer = p.answer_for(tag)
    if answer is None:
        return None
    wrong = [c for c in joins(p.lemma.lemma, ENDINGS[tag]) if c != answer and c in rejected]
    if len(wrong) < 3:
        return None
    choices, letter = multiple_choice(answer, rng.sample(wrong, 3), rng)
    return Item(
        id="",
        task="grammar",
        kind="sandhi",
        question=(
            f"Kannada joins case endings to nouns. Which is the correct way to write "
            f"{p.lemma.lemma} + {ENDINGS[tag]} as a single word? This is the {CASES[tag]} of {p.lemma.lemma} "
            f"('{p.lemma.gloss}')."
        ),
        choices=choices,
        answers=(letter,),
        check=Check.NEEDS_READER,
        source=SOURCE,
        meta={"lemma": p.lemma.lemma, "tag": tag, "form": answer},
    )


def build(kspell: Kspell, lemmas: Sequence[Lemma], per_kind: int = 120) -> list[Item]:
    paradigms = [paradigm(kspell, lemma) for lemma in lemmas]
    nouns = [p for p in paradigms if p.lemma.pos == "n" and p.readings]
    verbs = [p for p in paradigms if p.lemma.pos == "v" and p.readings]
    rng = random.Random("grammar")
    built: dict[str, list[Item]] = defaultdict(list)
    for p in nouns:
        cells = p.lemma.cells(CASES)
        for tag in cells:
            built["case"].append(_form_item(p, tag, cells, "case", rng))
        for form in sorted(p.readings):
            built["case-recognition"].append(_recognition_item(p, form, rng))
    for p in verbs:
        for tag in VERB_FORMS:
            built["verb"].append(_form_item(p, tag, VERB_FORMS, "verb", rng))
    candidates = sorted({c for p in nouns for tag in ENDINGS for c in joins(p.lemma.lemma, ENDINGS[tag])})
    rejected = set(candidates) - kspell.accepted(candidates)
    for p in nouns:
        for tag in ENDINGS:
            built["sandhi"].append(_sandhi_item(p, tag, rejected, rng))
    out = []
    for kind in ("case", "verb", "case-recognition", "sandhi"):
        items = [i for i in built[kind] if i is not None]
        chosen = sorted(rng.sample(range(len(items)), min(per_kind, len(items))))
        out += [_numbered(items[i], kind, n) for n, i in enumerate(chosen, start=1)]
    return out


def _numbered(item: Item, kind: str, n: int) -> Item:
    return replace(item, id=f"grammar-{kind}-{n:04d}")
