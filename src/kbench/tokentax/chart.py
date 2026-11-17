# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""The token-tax chart: 1 bar per distinct tokenizer, in light and dark versions."""

import csv
from dataclasses import dataclass
from pathlib import Path

THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "bar": "#52514e",
        "ink": "#0b0b0b",
        "muted": "#6b6a65",
        "grid": "#e4e3df",
        "accent": "#c8102e",
    },
    "dark": {
        "surface": "#1a1a19",
        "bar": "#c3c2b7",
        "ink": "#f0efec",
        "muted": "#a3a29b",
        "grid": "#33332f",
        "accent": "#ff5a5f",
    },
}
TITLE = "Kannada costs {low:.1f} to {high:.1f} times the English token count"
SUBTITLE = "Kannada tokens per English token for the same text, by tokenizer"
SOURCE = (
    "Source: 960 English segments and their Kannada translations in WMT24++ (Apache 2.0). "
    "Tokenizers that split the text identically share a bar."
)


@dataclass(frozen=True)
class Bar:
    label: str
    ratio: float


def label(names: list[str], per_line: int = 2) -> str:
    lines = [", ".join(names[i : i + per_line]) for i in range(0, len(names), per_line)]
    return ",\n".join(lines)


def bars(summary: Path, groups: list[list[str]]) -> list[Bar]:
    """1 bar per group of identical tokenizers, highest ratio first."""
    with summary.open(encoding="utf-8") as f:
        rows = {r["tokenizer"]: r for r in csv.DictReader(f)}
    out = [
        Bar(label([rows[k]["label"] for k in group]), float(rows[group[0]]["ratio"]))
        for group in groups
        if group[0] in rows
    ]
    return sorted(out, key=lambda b: -b.ratio)


def draw(chart_bars: list[Bar], out_stem: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    low, high = min(b.ratio for b in chart_bars), max(b.ratio for b in chart_bars)
    for name, t in THEMES.items():
        plt.rcParams.update(
            {"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none", "svg.hashsalt": "kbench"}
        )
        fig, ax = plt.subplots(figsize=(8, 0.46 * len(chart_bars) + 1.9), dpi=200)
        fig.patch.set_facecolor(t["surface"])
        ax.set_facecolor(t["surface"])
        rows = list(reversed(chart_bars))
        for y, bar in enumerate(rows):
            ax.add_patch(
                FancyBboxPatch(
                    (0, y - 0.28),
                    bar.ratio,
                    0.56,
                    boxstyle="round,pad=0,rounding_size=0.06",
                    linewidth=0,
                    facecolor=t["bar"],
                    mutation_aspect=4,
                )
            )
            ax.text(bar.ratio + 0.08, y, f"{bar.ratio:.2f}", va="center", color=t["ink"], fontsize=9.5)
        ax.set_yticks(range(len(rows)), [b.label for b in rows], color=t["ink"], fontsize=9)
        ax.set_xlim(0, high * 1.1)
        ax.set_ylim(-0.7, len(rows) - 0.3)
        ax.axvline(1, color=t["accent"], linewidth=1.5)
        ax.text(1.06, len(rows) - 0.55, "parity with English", color=t["muted"], fontsize=8.5, va="center")
        ax.xaxis.grid(True, color=t["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", colors=t["muted"], labelsize=8.5, length=0)
        ax.tick_params(axis="y", length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.text(
            0.01,
            0.985,
            TITLE.format(low=low, high=high),
            fontsize=13,
            fontweight="bold",
            color=t["ink"],
            va="top",
        )
        fig.text(0.01, 0.985 - 0.32 / fig.get_figheight(), SUBTITLE, fontsize=9.5, color=t["muted"], va="top")
        fig.text(0.01, 0.012, SOURCE, fontsize=7.5, color=t["muted"], va="bottom", wrap=True)
        fig.subplots_adjust(
            left=0.36, right=0.97, top=1 - 0.75 / fig.get_figheight(), bottom=0.55 / fig.get_figheight()
        )
        for ext in ("svg", "png"):
            fig.savefig(
                out_stem.with_name(f"{out_stem.name}-{name}.{ext}"),
                facecolor=t["surface"],
                metadata={"Date": None} if ext == "svg" else None,
            )
        plt.close(fig)
