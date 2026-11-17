# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Downloaded inputs, each pinned by URL revision and SHA-256."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

RAW = Path("data/raw")


@dataclass(frozen=True)
class Source:
    url: str
    sha256: str
    name: str

    def fetch(self, raw: Path = RAW) -> Path:
        """Download once into `raw` and check the hash."""
        path = raw / self.name
        if not path.exists():
            raw.mkdir(parents=True, exist_ok=True)
            path.write_bytes(urlopen(self.url).read())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != self.sha256:
            raise ValueError(f"{path} has sha256 {digest}, expected {self.sha256}")
        return path


WMT24PP = Source(
    "https://huggingface.co/datasets/google/wmt24pp/resolve/fd7405c06494bc66a57b25f55d217a72f96e60dc/"
    "en-kn_IN.jsonl",
    "b5ac7ca05c4f6fc30aa8a0c37490ae0786d954969d4152fbd19f1e41e4f5c757",
    "en-kn_IN.jsonl",
)
BELEBELE = Source(
    "https://huggingface.co/datasets/facebook/belebele/resolve/7899cdfa4e1e0d733fd77c848e2c273cb1d32be2/"
    "data/kan_Knda.jsonl",
    "de094c4415ae4bf59f848dbcfdb6e7dab49e4a1eb90a8475e390192e4baff5f5",
    "belebele-kan_Knda.jsonl",
)
WIKISOURCE = Source(
    "https://dumps.wikimedia.org/knwikisource/20261101/knwikisource-20261101-pages-articles.xml.bz2",
    "66ec63b0474b7f68665f283e9761686a6627e2f38186a4f5911c8140ebb5318d",
    "knwikisource-20261101-pages-articles.xml.bz2",
)
