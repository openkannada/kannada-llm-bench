# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""A fixed sample of items per kind, the same for every model."""

import random
from collections import defaultdict
from collections.abc import Sequence

from kbench.suite.items import Item


def per_kind(items: Sequence[Item], n: int) -> list[Item]:
    """Up to n items of each kind, chosen with a fixed seed, in file order."""
    by_kind: dict[str, list[Item]] = defaultdict(list)
    for item in items:
        by_kind[item.kind].append(item)
    chosen = set()
    for kind, group in sorted(by_kind.items()):
        rng = random.Random(f"sample-{kind}")
        chosen |= {i.id for i in rng.sample(group, min(n, len(group)))}
    return [i for i in items if i.id in chosen]
