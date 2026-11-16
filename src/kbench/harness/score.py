"""Reading a model's reply and deciding whether it is right."""

import re
import unicodedata

from kbench.suite.items import Item

THINKING = re.compile(r"<think>.*?(</think>|$)", re.DOTALL)
LETTER = re.compile(r"\b([ABCD])\b")
INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\ufffd"))


def normalize(text: str) -> str:
    """NFC; no zero-width characters, byte-order marks or replacement characters (which a detokenizer
    can leave before a Kannada digit); collapsed spaces; lowercase Latin. Kannada and diacritics stay."""
    text = unicodedata.normalize("NFC", text).translate(INVISIBLE)
    return " ".join(text.split()).casefold()


def parse(item: Item, reply: str) -> str:
    """The answer in a reply: the first option letter for a choice item, else the first non-empty line,
    after its last "=" if it is an equation, without a leading "Answer:", quotes or a final period."""
    reply = THINKING.sub("", reply).strip()
    if item.is_choice:
        match = LETTER.search(reply[:200])
        return match.group(1) if match else ""
    line = next((line.strip() for line in reply.splitlines() if line.strip()), "")
    line = re.sub(r"^(answer|transliteration|word)\s*:\s*", "", line, flags=re.IGNORECASE)
    line = line.rsplit("=", 1)[-1]
    return line.strip("\"'`*. ")


def is_correct(item: Item, answer: str) -> bool:
    return normalize(answer) in {normalize(a) for a in item.answers}
