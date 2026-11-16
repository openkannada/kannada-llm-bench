# Working on kannada-llm-bench

Instructions for anyone changing this repository, human or AI agent.

## What this is

Measurements of how language models handle Kannada: the token cost of Kannada text in each tokenizer, and (in progress) a Kannada test suite with answer keys.

## Commands

```sh
uv sync --extra chart
uv run pytest                      # offline tests, under 5 seconds
uv run ruff check . && uv run ruff format --check .
uv run kbench token-tax            # recount every tokenizer; downloads pinned files
uv run kbench token-tax-chart      # redraw the chart from results/token-tax
```

## Architecture

```text
src/kbench/
  cli.py               the kbench command
  tokentax/
    registry.py        the tokenizers, each pinned to a revision, and the ones not measured
    loaders.py         a token counter for each kind of tokenizer file
    wmt.py             the WMT24++ en-kn segments, pinned by revision and hash
    measure.py         counts, ratios, bootstrap intervals, identical-tokenizer groups
    chart.py           the chart, light and dark
results/token-tax/     counts.csv, summary.csv, identical.txt and the chart
```

## Rules

- Pin every external input: a revision for Hugging Face files, a hash for downloaded data.
- Never download a gated model or dataset, and never accept a license on Hugging Face. Gated tokenizers go in `UNMEASURED` with the reason.
- No paid API calls. Claude and Gemini counts wait on an approved key.
- Commit results with the code that produced them; a test checks that `summary.csv` matches `counts.csv`.
- Every behavior change gets a test. For each new rule, remove it, confirm a test fails, then restore it, under a 5 second timeout.
- Comments only for what the code cannot say.

## Commits

Signed, as Prasad, with no AI attribution:

```sh
git -c user.name="Prasad Subrahmanya" -c user.email=prasadus92@gmail.com commit -S
```

## Writing

Plain short sentences, American spelling, digits for numbers, no em dashes, no hype.
