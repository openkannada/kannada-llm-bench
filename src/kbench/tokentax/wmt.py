"""The English and Kannada sides of WMT24++ (Apache 2.0), pinned to 1 revision."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

REVISION = "fd7405c06494bc66a57b25f55d217a72f96e60dc"
URL = f"https://huggingface.co/datasets/google/wmt24pp/resolve/{REVISION}/en-kn_IN.jsonl"
SHA256 = "b5ac7ca05c4f6fc30aa8a0c37490ae0786d954969d4152fbd19f1e41e4f5c757"
DEFAULT_PATH = Path("data/raw/en-kn_IN.jsonl")


@dataclass(frozen=True)
class Segment:
    segment_id: int
    document_id: str
    domain: str
    english: str
    kannada: str


def fetch(path: Path = DEFAULT_PATH) -> Path:
    """Download the file once and check it against the pinned hash."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(urlopen(URL).read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SHA256:
        raise ValueError(f"{path} has sha256 {digest}, expected {SHA256}")
    return path


def parse(lines: list[str]) -> list[Segment]:
    """The segments with a good source; the dataset flags the rest, such as its canary line."""
    rows = (json.loads(line) for line in lines if line.strip())
    return [
        Segment(row["segment_id"], row["document_id"], row["domain"], row["source"], row["target"])
        for row in rows
        if not row["is_bad_source"]
    ]


def load(path: Path = DEFAULT_PATH) -> list[Segment]:
    return parse(fetch(path).read_text(encoding="utf-8").splitlines())
