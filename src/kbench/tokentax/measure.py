"""Token counts per segment, and the ratios computed from them."""

import csv
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from kbench.tokentax.loaders import Counter
from kbench.tokentax.registry import TokenizerSpec
from kbench.tokentax.wmt import Segment

DOMAINS = ("news", "social", "speech", "literary")
COUNT_FIELDS = ("tokenizer", "segment_id", "document_id", "domain", "en_tokens", "kn_tokens")


@dataclass(frozen=True)
class Count:
    tokenizer: str
    segment_id: int
    document_id: str
    domain: str
    en_tokens: int
    kn_tokens: int


@dataclass(frozen=True)
class Summary:
    key: str
    label: str
    models: str
    en_tokens: int
    kn_tokens: int
    ratio: float
    ratio_low: float
    ratio_high: float
    kn_tokens_per_word: float
    domain_ratios: dict[str, float]


def identical_groups(counts_by_key: dict[str, Sequence[Count]]) -> list[list[str]]:
    """Keys whose per-segment counts are all equal, in the order the keys come; such
    tokenizers split this text identically, as when models share 1 vocabulary."""
    groups: dict[tuple[tuple[int, int], ...], list[str]] = {}
    for key, counts in counts_by_key.items():
        groups.setdefault(tuple((c.en_tokens, c.kn_tokens) for c in counts), []).append(key)
    return list(groups.values())


def words(text: str) -> int:
    return len(text.split())


def count(spec: TokenizerSpec, counter: Counter, segments: Iterable[Segment]) -> list[Count]:
    return [
        Count(spec.key, s.segment_id, s.document_id, s.domain, counter(s.english), counter(s.kannada))
        for s in segments
    ]


def ratio(counts: Sequence[Count]) -> float:
    """Kannada tokens per English token over the whole text, so long segments weigh more."""
    return sum(c.kn_tokens for c in counts) / sum(c.en_tokens for c in counts)


def bootstrap(counts: Sequence[Count], rounds: int = 1000, seed: int = 0) -> tuple[float, float]:
    """A 95% interval for the ratio, resampling whole documents, since segments of 1 document
    share names and style."""
    totals: dict[str, list[int]] = {}
    for c in counts:
        en_kn = totals.setdefault(c.document_id, [0, 0])
        en_kn[0] += c.en_tokens
        en_kn[1] += c.kn_tokens
    documents = list(totals.values())
    rng = random.Random(seed)
    samples = sorted(_ratio_of(rng.choices(documents, k=len(documents))) for _ in range(rounds))
    return samples[int(0.025 * rounds)], samples[int(0.975 * rounds) - 1]


def _ratio_of(documents: Sequence[list[int]]) -> float:
    return sum(kn for _, kn in documents) / sum(en for en, _ in documents)


def summarize(spec: TokenizerSpec, counts: Sequence[Count], kannada_words: int) -> Summary:
    low, high = bootstrap(counts)
    kn = sum(c.kn_tokens for c in counts)
    return Summary(
        key=spec.key,
        label=spec.label,
        models=spec.models,
        en_tokens=sum(c.en_tokens for c in counts),
        kn_tokens=kn,
        ratio=ratio(counts),
        ratio_low=low,
        ratio_high=high,
        kn_tokens_per_word=kn / kannada_words,
        domain_ratios={d: ratio([c for c in counts if c.domain == d]) for d in DOMAINS},
    )


def merge(old: Iterable[Count], new: Sequence[Count]) -> list[Count]:
    """The old counts of tokenizers not recounted, then the new counts."""
    recounted = {c.tokenizer for c in new}
    return [c for c in old if c.tokenizer not in recounted] + list(new)


def write_counts(path: Path, counts: Iterable[Count]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(COUNT_FIELDS)
        for c in counts:
            writer.writerow((c.tokenizer, c.segment_id, c.document_id, c.domain, c.en_tokens, c.kn_tokens))


def read_counts(path: Path) -> list[Count]:
    with path.open(encoding="utf-8") as f:
        return [
            Count(
                r["tokenizer"],
                int(r["segment_id"]),
                r["document_id"],
                r["domain"],
                int(r["en_tokens"]),
                int(r["kn_tokens"]),
            )
            for r in csv.DictReader(f)
        ]


def write_groups(path: Path, groups: Iterable[list[str]]) -> None:
    """1 line per group of tokenizers with identical counts."""
    path.write_text("".join(" ".join(g) + "\n" for g in groups), encoding="utf-8")


def read_groups(path: Path) -> list[list[str]]:
    return [line.split() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_summary(path: Path, summaries: Iterable[Summary], groups: Iterable[list[str]] = ()) -> None:
    same = {key: [k for k in g if k != key] for g in groups for key in g}
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(
            (
                "tokenizer",
                "label",
                "models",
                "en_tokens",
                "kn_tokens",
                "ratio",
                "ratio_low",
                "ratio_high",
                "kn_tokens_per_word",
                *(f"ratio_{d}" for d in DOMAINS),
                "same_counts_as",
            )
        )
        for s in summaries:
            writer.writerow(
                (
                    s.key,
                    s.label,
                    s.models,
                    s.en_tokens,
                    s.kn_tokens,
                    f"{s.ratio:.4f}",
                    f"{s.ratio_low:.4f}",
                    f"{s.ratio_high:.4f}",
                    f"{s.kn_tokens_per_word:.2f}",
                    *(f"{s.domain_ratios[d]:.3f}" for d in DOMAINS),
                    " ".join(same.get(s.key, [])),
                )
            )
