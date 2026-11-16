"""The saved replies of 1 model: 1 JSON object per line with the item id, reply and time."""

import json
from pathlib import Path


def read_replies(path: Path) -> dict[str, str]:
    """Each item's reply. A last line cut off by a stopped run is skipped; rerunning answers it."""
    replies = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            result = json.loads(line)
        except json.JSONDecodeError:
            continue
        replies[result["id"]] = result["reply"]
    return replies
