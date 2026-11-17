import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import pytest

from kbench.tokentax import chart, measure, wmt
from kbench.tokentax.measure import Count
from kbench.tokentax.registry import TOKENIZERS, UNMEASURED, Kind, by_key

ROOT = Path(__file__).parent.parent
RESULTS = ROOT / "results" / "token-tax"


def committed_counts() -> dict[str, list[Count]]:
    grouped = defaultdict(list)
    for c in measure.read_counts(RESULTS / "counts.csv"):
        grouped[c.tokenizer].append(c)
    return grouped


def count(segment_id: int, en: int, kn: int, document: str = "d", tokenizer: str = "t") -> Count:
    return Count(tokenizer, segment_id, document, "news", en, kn)


def row(segment_id: int, bad: bool, domain: str = "news") -> str:
    return json.dumps(
        {
            "segment_id": segment_id,
            "document_id": "doc",
            "domain": domain,
            "is_bad_source": bad,
            "source": f"en {segment_id}",
            "target": f"kn {segment_id}",
        }
    )


def test_parse_drops_flagged_sources():
    segments = wmt.parse([row(0, True, "canary"), row(1, False), "", row(2, False, "social")])
    assert [(s.segment_id, s.domain, s.english) for s in segments] == [
        (1, "news", "en 1"),
        (2, "social", "en 2"),
    ]


def test_ratio_weighs_segments_by_length():
    counts = [count(1, 10, 20), count(2, 30, 30)]
    assert measure.ratio(counts) == pytest.approx(50 / 40)


def test_bootstrap_interval_contains_the_ratio():
    counts = [count(i, 10 + i % 3, 20 + i % 7, document=str(i // 4)) for i in range(200)]
    low, high = measure.bootstrap(counts)
    assert low <= measure.ratio(counts) <= high
    assert measure.bootstrap(counts) == (low, high)


def test_bootstrap_resamples_documents_not_segments():
    one_document = [count(i, 10, 10 + i % 2 * 30, document="d") for i in range(100)]
    assert measure.bootstrap(one_document) == (measure.ratio(one_document), measure.ratio(one_document))


def test_identical_groups_join_only_equal_count_vectors():
    a = [count(1, 1, 2, tokenizer="a"), count(2, 3, 4, tokenizer="a")]
    b = [count(1, 1, 2, tokenizer="b"), count(2, 3, 4, tokenizer="b")]
    c = [count(1, 1, 2, tokenizer="c"), count(2, 3, 5, tokenizer="c")]
    assert measure.identical_groups({"a": a, "b": b, "c": c}) == [["a", "b"], ["c"]]


def test_merge_keeps_counts_of_tokenizers_not_recounted():
    old = [count(1, 1, 1, tokenizer="a"), count(1, 2, 2, tokenizer="b")]
    new = [count(1, 9, 9, tokenizer="b")]
    assert measure.merge(old, new) == [old[0], new[0]]


def test_counts_round_trip(tmp_path: Path):
    counts = [Count("cl100k", 7, "doc", "speech", 12, 99)]
    measure.write_counts(tmp_path / "c.csv", counts)
    assert measure.read_counts(tmp_path / "c.csv") == counts


def test_chart_labels_wrap_after_2_names():
    assert chart.label(["A", "B", "C"]) == "A, B,\nC"


def test_registry_keys_are_unique_and_pinned_to_commits():
    keys = [s.key for s in TOKENIZERS]
    assert len(keys) == len(set(keys))
    assert all(re.fullmatch(r"[0-9a-f]{40}", s.revision) for s in TOKENIZERS if s.kind is not Kind.TIKTOKEN)


def test_committed_counts_cover_every_tokenizer_and_segment():
    grouped = committed_counts()
    assert set(grouped) == {s.key for s in TOKENIZERS}
    assert all(len(counts) == 960 for counts in grouped.values())


def test_committed_summary_and_groups_regenerate_exactly(tmp_path: Path):
    grouped = committed_counts()
    kannada_words = 23_778
    summaries = sorted(
        (measure.summarize(by_key(k), c, kannada_words) for k, c in grouped.items()), key=lambda s: -s.ratio
    )
    groups = measure.identical_groups(grouped)
    measure.write_summary(tmp_path / "summary.csv", summaries, groups)
    measure.write_groups(tmp_path / "identical.txt", groups)
    for name in ("summary.csv", "identical.txt"):
        assert (tmp_path / name).read_bytes() == (RESULTS / name).read_bytes(), name


def test_readme_table_matches_each_group():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    grouped = committed_counts()
    for group in measure.read_groups(RESULTS / "identical.txt"):
        s = measure.summarize(by_key(group[0]), grouped[group[0]], 23_778)
        cells = f"| {s.ratio:.2f} | {s.ratio_low:.2f} to {s.ratio_high:.2f} | {s.kn_tokens_per_word:.1f} |"
        rows = [
            line for line in readme if line.endswith(cells) and all(by_key(k).models in line for k in group)
        ]
        assert rows, (group, cells)


def test_readme_lists_every_unmeasured_tokenizer():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert all(u.label in readme for u in UNMEASURED)


@pytest.mark.network
def test_cl100k_counts_kannada_by_bytes():
    from kbench.tokentax.loaders import load

    count = load(by_key("cl100k"))
    assert count("hello") == 1
    assert count("ಕನ್ನಡ") > 5


def test_data_card_describes_every_column_of_the_results():
    card = (RESULTS / "README.md").read_text(encoding="utf-8")
    for name in ("counts.csv", "summary.csv"):
        with (RESULTS / name).open(encoding="utf-8") as f:
            header = next(csv.reader(f))
        section = card.split(f"### {name}", 1)[1].split("###", 1)[0]
        documented = [line.split("`")[1] for line in section.splitlines() if line.startswith("| `")]
        assert sorted(documented) == sorted(header), name
