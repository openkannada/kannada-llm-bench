"""Command-line entry point: kbench <command>."""

import argparse
from collections import defaultdict
from pathlib import Path

from kbench.tokentax import chart, loaders, measure, wmt
from kbench.tokentax.registry import TOKENIZERS, by_key

TOKEN_TAX_DIR = Path("results/token-tax")


def token_tax(args: argparse.Namespace) -> None:
    segments = wmt.load()
    specs = [by_key(k) for k in args.only] if args.only else list(TOKENIZERS)
    counts = []
    for spec in specs:
        print(f"counting {spec.key}", flush=True)
        counts += measure.count(spec, loaders.load(spec), segments)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    existing = out / "counts.csv"
    if args.only and existing.exists():
        counts = measure.merge(measure.read_counts(existing), counts)
    order = {spec.key: i for i, spec in enumerate(TOKENIZERS)}
    counts.sort(key=lambda c: (order[c.tokenizer], c.segment_id))
    measure.write_counts(existing, counts)
    summarize(out, segments)


def summarize(out: Path, segments: list[wmt.Segment]) -> None:
    grouped = defaultdict(list)
    for c in measure.read_counts(out / "counts.csv"):
        grouped[c.tokenizer].append(c)
    kannada_words = sum(measure.words(s.kannada) for s in segments)
    summaries = sorted(
        (measure.summarize(by_key(key), counts, kannada_words) for key, counts in grouped.items()),
        key=lambda s: -s.ratio,
    )
    groups = measure.identical_groups(grouped)
    measure.write_summary(out / "summary.csv", summaries, groups)
    measure.write_groups(out / "identical.txt", groups)
    for s in summaries:
        print(f"{s.label:22} {s.ratio:5.2f}  ({s.ratio_low:.2f} to {s.ratio_high:.2f})")


def token_tax_chart(args: argparse.Namespace) -> None:
    out = Path(args.out)
    groups = measure.read_groups(out / "identical.txt")
    chart.draw(chart.bars(out / "summary.csv", groups), out / "token-tax")


def main() -> None:
    parser = argparse.ArgumentParser(prog="kbench")
    commands = parser.add_subparsers(required=True)
    tax = commands.add_parser("token-tax", help="count tokens on WMT24++ en-kn and write the ratios")
    tax.add_argument("--only", nargs="*", help="recount these tokenizer keys and keep the other counts")
    tax.add_argument("--out", default=str(TOKEN_TAX_DIR))
    tax.set_defaults(run=token_tax)
    tax_chart = commands.add_parser("token-tax-chart", help="draw the chart from the written results")
    tax_chart.add_argument("--out", default=str(TOKEN_TAX_DIR))
    tax_chart.set_defaults(run=token_tax_chart)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
