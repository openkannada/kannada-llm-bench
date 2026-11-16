"""Command-line entry point: kbench <command>."""

import argparse
from collections import defaultdict
from pathlib import Path

from kbench.tokentax import chart, loaders, measure, wmt
from kbench.tokentax.registry import TOKENIZERS, by_key

TOKEN_TAX_DIR = Path("results/token-tax")
SUITE_TASKS = ("reading", "grammar", "translit", "numbers", "orthography")


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


def suite_build(args: argparse.Namespace) -> None:
    from kbench.suite import build
    from kbench.suite.tools import Kspell, Oracle

    kspell = Kspell(Path(args.kspell), Path(args.dictionary)) if args.kspell else None
    if kspell:
        build.check_kannada_spell(Path(args.dictionary), allow_other=args.any_kannada_spell)
    tools = build.Tools(Oracle(Path(args.oracle)), kspell)
    build.write_all(build.build_all(tools, set(args.tasks)))


def suite_shortcuts(_: argparse.Namespace) -> None:
    from kbench.suite import build, items, shortcuts

    table = shortcuts.scores([i for task in SUITE_TASKS for i in items.read(build.ITEMS / f"{task}.jsonl")])
    shortcuts.write(Path("results/suite-shortcuts.csv"), table)
    for kind, result in table.items():
        print(f"{kind:18} best {max(result.values()):.0%}")


def suite_old_words(_: argparse.Namespace) -> None:
    from kbench.suite import build

    print(f"{build.extract_old_words()} words")


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
    suite = commands.add_parser("suite-build", help="build the test items and their answer keys")
    suite.add_argument("--oracle", required=True, help="the oracle binary built from oracle/")
    suite.add_argument("--kspell", help="kspell from kannada-spell, for the grammar items")
    suite.add_argument("--dictionary", help="the kannada-spell dictionary, such as kannada-spell/dict/kn_IN")
    suite.add_argument(
        "--any-kannada-spell",
        action="store_true",
        help="build grammar from a kannada-spell commit other than the pinned one",
    )
    suite.add_argument("--tasks", nargs="+", default=list(SUITE_TASKS), choices=SUITE_TASKS)
    suite.set_defaults(run=suite_build)
    cuts = commands.add_parser("suite-shortcuts", help="score strategies that ignore Kannada on the items")
    cuts.set_defaults(run=suite_shortcuts)
    old = commands.add_parser("suite-old-words", help="extract the Old Kannada words from Kannada Wikisource")
    old.set_defaults(run=suite_old_words)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
