# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""The chat messages a model sees for 1 item."""

from kbench.suite.items import LETTERS, Item

SYSTEM = "You are taking a test of Kannada. Answer every question; do not explain."
CHOICE_RULE = "Reply with the letter of the correct option (A, B, C or D) and nothing else."
OPEN_RULE = "Reply with the answer only, on 1 line, and nothing else."


def user_message(item: Item) -> str:
    parts = []
    if item.passage:
        parts.append(f"Passage:\n{item.passage}")
    parts.append(item.question)
    if item.is_choice:
        parts.append(
            "\n".join(f"{letter}. {choice}" for letter, choice in zip(LETTERS, item.choices, strict=True))
        )
        parts.append(CHOICE_RULE)
    else:
        parts.append(OPEN_RULE)
    return "\n\n".join(parts)


def messages(item: Item) -> list[dict[str, str]]:
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_message(item)}]
