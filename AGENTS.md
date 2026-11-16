# Working on kannada-llm-bench

Instructions for anyone changing this repository, human or AI agent.

## What this is

Measurements of how language models handle Kannada: the token cost of Kannada text in each tokenizer, and a Kannada test suite with answer keys.

## Commands

```sh
uv sync --extra chart
uv run pytest                      # offline tests, under 5 seconds
uv run ruff check . && uv run ruff format --check .
uv run kbench token-tax            # recount every tokenizer; downloads pinned files
uv run kbench token-tax-chart      # redraw the chart from results/token-tax
cargo build --release --manifest-path oracle/Cargo.toml
uv run kbench suite-build --oracle <path> [--kspell <path> --dictionary <path>]
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
  suite/
    items.py           an item, its answer key and who vouches for it; option balancing
    sources.py         pinned downloads
    tools.py           calls to the oracle and to kspell
    script.py          joining Kannada stems and endings
    words.py           Kannada words from text and dumps
    reading.py, grammar.py, translit.py, numbers.py, orthography.py   1 builder per task
    build.py           builds and checks every item file
    shortcuts.py       scores of strategies that ignore Kannada
oracle/                Rust CLI over kannadi: transliteration and Old Kannada letters
results/token-tax/     counts.csv, summary.csv, identical.txt and the chart
suite/items/           the test items, 1 JSONL file per task
suite/lemmas.tsv       the nouns and verbs the grammar items use
suite/old-kannada-words.tsv   Old Kannada words from Wikisource
```

## Rules

- Pin every external input: a revision for Hugging Face files, a hash for downloaded data.
- Never download a gated model or dataset, and never accept a license on Hugging Face. Gated tokenizers go in `UNMEASURED` with the reason.
- No paid API calls. Claude and Gemini counts wait on an approved key.
- Commit results with the code that produced them; a test checks that `summary.csv` matches `counts.csv`.
- Every behavior change gets a test. For each new rule, remove it, confirm a test fails, then restore it, under a 5 second timeout.
- Every item says how its key is checked: `human`, `computed` or `needs-reader`. Never mark generated Kannada grammar `computed`.
- Items are generated, never edited by hand. Change the builder and rebuild. CI fails if a rebuild changes a reading, transliteration, numbers or orthography item; grammar needs kannada-spell, so rebuild it locally after any change to the suite code and commit the result.
- After changing items, rerun `kbench suite-shortcuts` and update the shortcut table in the README.
- Comments only for what the code cannot say.

## Commits

Signed, as Prasad, with no AI attribution:

```sh
git -c user.name="Prasad Subrahmanya" -c user.email=prasadus92@gmail.com commit -S
```

## Writing

Plain short sentences, American spelling, digits for numbers, no em dashes, no hype.
