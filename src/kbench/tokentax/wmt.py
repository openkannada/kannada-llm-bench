# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""The English and Kannada sides of WMT24++ (Apache 2.0), pinned to 1 revision."""

import json
from dataclasses import dataclass

from kbench.sources import WMT24PP


@dataclass(frozen=True)
class Segment:
    segment_id: int
    document_id: str
    domain: str
    english: str
    kannada: str


def parse(lines: list[str]) -> list[Segment]:
    """The segments with a good source; the dataset flags the rest, such as its canary line."""
    rows = (json.loads(line) for line in lines if line.strip())
    return [
        Segment(row["segment_id"], row["document_id"], row["domain"], row["source"], row["target"])
        for row in rows
        if not row["is_bad_source"]
    ]


def load() -> list[Segment]:
    return parse(WMT24PP.fetch().read_text(encoding="utf-8").splitlines())
