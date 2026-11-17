# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Numbers: Kannada digits, arithmetic in Kannada digits, and number words."""

import random

from kbench.suite.items import Check, Item, multiple_choice
from kbench.suite.script import attach, without_final_vowel

KANNADA_DIGITS = "೦೧೨೩೪೫೬೭೮೯"
TO_KANNADA = str.maketrans("0123456789", KANNADA_DIGITS)
SOURCE_DIGITS = "Numbers drawn at random; answers computed"
SOURCE_WORDS = "Number words written by a generator in this suite"

UNITS = ["", "ಒಂದು", "ಎರಡು", "ಮೂರು", "ನಾಲ್ಕು", "ಐದು", "ಆರು", "ಏಳು", "ಎಂಟು", "ಒಂಬತ್ತು"]
TEENS = ["ಹತ್ತು", "ಹನ್ನೊಂದು", "ಹನ್ನೆರಡು", "ಹದಿಮೂರು", "ಹದಿನಾಲ್ಕು", "ಹದಿನೈದು", "ಹದಿನಾರು", "ಹದಿನೇಳು", "ಹದಿನೆಂಟು", "ಹತ್ತೊಂಬತ್ತು"]
TENS = ["", "", "ಇಪ್ಪತ್ತು", "ಮೂವತ್ತು", "ನಲವತ್ತು", "ಐವತ್ತು", "ಅರವತ್ತು", "ಎಪ್ಪತ್ತು", "ಎಂಬತ್ತು", "ತೊಂಬತ್ತು"]
HUNDREDS = ["", "ನೂರು", "ಇನ್ನೂರು", "ಮುನ್ನೂರು", "ನಾನೂರು", "ಐನೂರು", "ಆರುನೂರು", "ಏಳುನೂರು", "ಎಂಟುನೂರು", "ಒಂಬೈನೂರು"]


def kannada_digits(n: int) -> str:
    return str(n).translate(TO_KANNADA)


def _below_100(n: int) -> str:
    if n < 10:
        return UNITS[n]
    if n < 20:
        return TEENS[n - 10]
    tens, unit = divmod(n, 10)
    return attach(without_final_vowel(TENS[tens]), UNITS[unit]) if unit else TENS[tens]


def _below_1000(n: int) -> str:
    hundreds, rest = divmod(n, 100)
    if not hundreds:
        return _below_100(rest)
    if not rest:
        return HUNDREDS[hundreds]
    return f"{without_final_vowel(HUNDREDS[hundreds])} {_below_100(rest)}"


def number_words(n: int) -> str:
    """Kannada words for 1 to 99,999, in 1 common written style: ಇಪ್ಪತ್ತೊಂದು, ನೂರ ಐದು,
    ಎರಡು ಸಾವಿರದ ಐನೂರು."""
    if not 1 <= n < 100_000:
        raise ValueError(n)
    thousands, rest = divmod(n, 1000)
    if not thousands:
        return _below_1000(rest)
    head = f"{_below_100(thousands)} ಸಾವಿರ"
    return f"{head}ದ {_below_1000(rest)}" if rest else head


def _magnitude(rng: random.Random) -> int:
    return rng.randrange(1, 10 ** rng.randint(1, 6))


def _digit_items(rng: random.Random, per_kind: int) -> list[Item]:
    items = []
    for n in range(1, per_kind + 1):
        value = _magnitude(rng)
        items.append(
            Item(
                id=f"numbers-read-digits-{n:04d}",
                task="numbers",
                kind="read-digits",
                question=f"Write this number, given in Kannada digits, in Western digits 0 to 9: "
                f"{kannada_digits(value)}",
                answers=(str(value),),
                check=Check.COMPUTED,
                source=SOURCE_DIGITS,
            )
        )
    for n in range(1, per_kind + 1):
        value = _magnitude(rng)
        items.append(
            Item(
                id=f"numbers-write-digits-{n:04d}",
                task="numbers",
                kind="write-digits",
                question=f"Write the number {value} in Kannada digits (೦ to ೯).",
                answers=(kannada_digits(value),),
                check=Check.COMPUTED,
                source=SOURCE_DIGITS,
            )
        )
    for n in range(1, per_kind + 1):
        a, b = rng.randrange(10, 1000), rng.randrange(10, 1000)
        op = rng.choice("+-×")
        if op == "-" and b > a:
            a, b = b, a
        value = a + b if op == "+" else a - b if op == "-" else a * b
        items.append(
            Item(
                id=f"numbers-arithmetic-{n:04d}",
                task="numbers",
                kind="arithmetic",
                question=f"Compute {kannada_digits(a)} {op} {kannada_digits(b)}. "
                f"Give the answer in Kannada digits.",
                answers=(kannada_digits(value),),
                check=Check.COMPUTED,
                source=SOURCE_DIGITS,
            )
        )
    return items


def grid(value: int, rng: random.Random) -> list[int]:
    """`value` and 3 numbers that form a 2 by 2 grid with it: 2 digit positions, each with 2 digits.
    Every option then differs from 2 others in 1 digit and from 1 in 2, so the right one cannot be
    found as the option most like the rest."""
    digits = list(str(value))
    first, second = rng.sample(range(len(digits)), 2)

    def other(position: int) -> str:
        low = 1 if position == 0 else 0
        return rng.choice([d for d in "0123456789"[low:] if d != digits[position]])

    swaps = (other(first), other(second))
    values = []
    for a in (digits[first], swaps[0]):
        for b in (digits[second], swaps[1]):
            changed = list(digits)
            changed[first], changed[second] = a, b
            values.append(int("".join(changed)))
    return values


def _word_items(rng: random.Random, per_kind: int) -> list[Item]:
    items = []
    for n in range(1, per_kind + 1):
        value = rng.randrange(1, 10 ** rng.randint(1, 5))
        items.append(
            Item(
                id=f"numbers-words-to-digits-{n:04d}",
                task="numbers",
                kind="words-to-digits",
                question=f"Write this Kannada number in Western digits 0 to 9: {number_words(value)}",
                answers=(str(value),),
                check=Check.NEEDS_READER,
                source=SOURCE_WORDS,
                meta={"value": str(value)},
            )
        )
    for n in range(1, per_kind + 1):
        value = rng.randrange(11, 10 ** rng.randint(2, 5))
        values = grid(value, rng)
        words = {number_words(v): v for v in values}
        choices, letter = multiple_choice(number_words(value), [number_words(v) for v in values[1:]], rng)
        items.append(
            Item(
                id=f"numbers-digits-to-words-{n:04d}",
                task="numbers",
                kind="digits-to-words",
                question=f"Which is the number {value} written in Kannada words?",
                choices=choices,
                answers=(letter,),
                check=Check.NEEDS_READER,
                source=SOURCE_WORDS,
                meta={"value": str(value), "options": " ".join(str(words[c]) for c in choices)},
            )
        )
    return items


def build(per_kind: int = 60) -> list[Item]:
    rng = random.Random("numbers")
    return _digit_items(rng, per_kind) + _word_items(rng, per_kind)
