# kannada-llm-bench

How many tokens Kannada costs in language model tokenizers, and a Kannada test suite with answer keys. Everything reruns from pinned public sources. The grammar items also need a checkout of [kannada-spell](https://github.com/openkannada/kannada-spell).

## Token tax

The same text costs between 1.1 and 8.3 times as many tokens in Kannada as in English, depending on the tokenizer. More tokens means a higher bill, slower answers and less room in the context window for the same message.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="results/token-tax/token-tax-dark.png">
  <img alt="Kannada tokens per English token, by tokenizer, from 8.27 for cl100k down to 1.14 for Sarvam-1" src="results/token-tax/token-tax-light.png">
</picture>

The test text is the 960 English segments of [WMT24++](https://huggingface.co/datasets/google/wmt24pp) with their professional Kannada translations (Apache 2.0). A segment is a sentence or a short paragraph from news, social media posts, speech transcripts or literature, drawn from 170 documents. Each tokenizer counts both sides without special tokens.

2 measures, for 2 questions:

- **Kannada tokens per English token** is the token tax: how much more a Kannada user pays than an English user of the same model for the same text. It is the Kannada total over the English total, so it also depends on how well the tokenizer handles English.
- **Kannada tokens per Kannada word** compares tokenizers on Kannada alone, since every tokenizer divides by the same 23,778 words.

| Tokenizer | Used by | Kannada tokens per English token | 95% interval | Kannada tokens per Kannada word |
|---|---|---|---|---|
| cl100k | GPT-4, GPT-3.5, Granite 4.1 | 8.27 | 8.06 to 8.48 | 14.3 |
| GLM-5.3 | GLM-5.3 | 8.27 | 8.06 to 8.48 | 14.3 |
| Qwen 2.5 | Qwen 2.5, Qwen 3 | 6.52 | 6.37 to 6.68 | 11.4 |
| Kimi | Kimi K2, Kimi K3 | 3.42 | 3.35 to 3.50 | 5.9 |
| DeepSeek | DeepSeek V3, DeepSeek V4.1 Flash | 3.42 | 3.34 to 3.50 | 6.0 |
| Qwen 3.5 | Qwen 3.5, Qwen 3.8 | 2.88 | 2.82 to 2.95 | 5.0 |
| Tekken | Mistral Nemo, Mistral Medium 3.5, Sarvam-M, Krutrim-2 | 2.08 | 2.04 to 2.13 | 3.7 |
| o200k | GPT-4o, GPT-4.1, o-series, gpt-oss 20B and 120B, Phi-4-mini | 1.83 | 1.80 to 1.87 | 3.1 |
| Gemma 4 | Gemma 4 | 1.70 | 1.65 to 1.74 | 3.0 |
| Mistral Large 4 | Mistral Large 4 | 1.64 | 1.61 to 1.67 | 2.9 |
| Sarvam | Sarvam 30B, Sarvam 105B | 1.35 | 1.32 to 1.38 | 2.4 |
| Sarvam-1 | Sarvam-1 | 1.14 | 1.12 to 1.17 | 2.3 |

The interval comes from resampling whole documents, because segments from 1 document share names and style.

What the numbers say:

- 23 tokenizers reduce to 12 distinct ones on this text. Tokenizers in 1 row split every segment into the same tokens, because the models share a vocabulary: Sarvam-M and Krutrim-2 use Mistral's Tekken, and Granite 4.1 uses cl100k. [identical.txt](results/token-tax/identical.txt) lists the groups.
- Qwen cut its Kannada cost by more than half between Qwen 3 and Qwen 3.5. Mistral Large 4 is the only Mistral tokenizer measured below 2.
- Sarvam's own tokenizers come closest to parity. Sarvam-1's low ratio is partly English cost: it spends 48,257 tokens on the English side, against 40,372 to 42,398 for the others. On Kannada alone, Sarvam-1 (2.3 tokens per word) and Sarvam 30B and 105B (2.4) are close.
- Kannada joins suffixes onto words, so it has fewer words than the English (23,778 against 32,262). Tokens per word is therefore not comparable across the 2 languages; use it only to compare tokenizers on Kannada.
- News costs the most in every tokenizer. Speech costs the least in all but Kimi, where literature does. [summary.csv](results/token-tax/summary.csv) has the ratio for each domain, and [counts.csv](results/token-tax/counts.csv) has the counts for every segment. The [data card](results/token-tax/README.md) describes every column, the method and the limits.

Not measured:

| Tokenizer | Why |
|---|---|
| Llama 3.1, Llama 4 | Hugging Face gates the files behind Meta's license terms |
| Gemma 3 | Gated behind Google's Gemma terms. Gemma 4 is open |
| Tiny Aya | Gated behind Cohere's terms |
| Claude | Not public. Anthropic's token-counting API can count it with an API key |
| Gemini | Not public. Google's countTokens API can count it with an API key |

### Rerun it

```sh
uv sync --extra chart
uv run kbench token-tax         # downloads the pinned data and tokenizer files, writes results/token-tax
uv run kbench token-tax --only gemma4   # recount 1 tokenizer and keep the other counts
uv run kbench token-tax-chart   # draws the chart in light and dark, as SVG and PNG
```

Every source is pinned: the WMT24++ file by revision and SHA-256, each Hugging Face tokenizer by commit, and the OpenAI encodings by tiktoken's own checksums. Add a tokenizer in [registry.py](src/kbench/tokentax/registry.py).

## Test suite

2,037 Kannada items in 5 tasks, in [suite/items](suite/items). Each item has its answer key and says who or what vouches for that key:

- **human**: written and checked by the people who made the source dataset;
- **computed**: computed by a rule that needs no judgment about Kannada grammar, such as a digit mapping, a transliteration standard, or the standard modern letters for ೞ and ಱ;
- **needs-reader**: generated by code that encodes Kannada grammar. A Kannada reader has not checked these yet, so treat their scores as provisional.

| Task | Kinds | Items | Key | Source |
|---|---|---|---|---|
| Reading | Belebele questions on a passage, 4 options | 897 | human | [Belebele](https://huggingface.co/datasets/facebook/belebele) kan_Knda, CC BY-SA 4.0 |
| Grammar | case form, verb form, case recognition, joining a stem and a case ending; 4 options each | 480 | needs-reader | Paradigms from kannada-spell `a01fe20` (`kspell paradigm`) for 78 common nouns and verbs |
| Transliteration | Kannada to ISO 15919, and back; exact answer | 200 | computed | Words from WMT24++ (Apache 2.0); answers from [kannadi](https://github.com/openkannada/kannadi) |
| Numbers | Kannada digits to Western and back, arithmetic in Kannada digits; exact answer | 180 | computed | Random numbers |
| Numbers | Kannada number words to digits (exact), digits to words (4 options) | 120 | needs-reader | A number-word generator in this suite |
| Orthography | writing an Old Kannada word (ೞ, ಱ) with modern letters; spotting the word with an obsolete letter; 4 options | 160 | computed | 421 words from Kannada Wikisource (CC BY-SA 4.0) and modern words from WMT24++; answers from kannadi |

1,437 items are human-checked or computed; 600 wait on a Kannada reader.

### Scoring against shortcuts

In the generated multiple-choice kinds each letter is the answer equally often, in a shuffled order. Some kinds can still be partly guessed without Kannada, from the shape of the options. [results/suite-shortcuts.csv](results/suite-shortcuts.csv) scores 5 such strategies; read a model's score against the best of them as well as against chance (25%).

| Kind | Best strategy that ignores Kannada | Its score |
|---|---|---|
| Belebele | always the most common letter (B) | 28% |
| Case form | the option least like the others | 28% |
| Verb form | the option most like the others | 32% |
| Case recognition | the longest option | 29% |
| Sandhi | the option least like the others | 35% |
| Digits to words | the option most like the others | 28% |
| Modernize | none better than chance | 25% |
| Spot the old letter | the option least like the others | 38% |

### What a Kannada reader should check first

- **Grammar.** The paradigms were checked against gold analyses written by an AI annotator, not by a person. The builder already removes these:
  - forms the dictionary also reads as another word (ಕಾಲಕ್ಕೆ is also a form of ಕಾಲ, 'time'), though variant spellings of the same word (ಕಾರ್ for ಕಾರು) are allowed. This leaves ಬರು and ಅಳು with no items, so 78 of the 80 listed words are used;
  - imperatives, because the paradigms give ಬರಿ for ಬನ್ನಿ;
  - plurals of kinship and mass nouns (ಅಣ್ಣಂದಿರು, not ಅಣ್ಣರು);
  - ಕಾಲು and ಮರೆ, whose paradigms mix in wrong stems.

  The case and verb distractors are other forms of the same word, so a paradigm error would show up as a wrong cell, not as a non-word.
- **Sandhi.** The distractors are joins the dictionary rejects. After a final ು the short join (ಕಾಡಲ್ಲಿ) is common in writing, so it is never used as a wrong answer.
- **Number words.** They follow 1 common written style (ನೂರ ಇಪ್ಪತ್ತೈದು, ಎರಡು ಸಾವಿರದ ಐನೂರು). Other correct styles exist, such as ನೂರಾ ಇಪ್ಪತ್ತೈದು, and are not accepted in the exact-answer kind. In the 4-option kind the options form a 2 by 2 grid of digits, so the right one cannot be found as the option most like the rest.
- **Old Kannada.** The task changes letters only. A full modern spelling would also change ಪ to ಹ and add final vowels (modern ಹೇಳಿ for ಪೇೞ್ದು); the question says to change only the obsolete letters.

### Rebuild the items

```sh
cargo build --release --manifest-path oracle/Cargo.toml     # kannadi answer keys
uv run kbench suite-build --oracle <target>/release/oracle --tasks reading translit numbers orthography
# grammar also needs kspell and a dictionary from a kannada-spell checkout
uv run kbench suite-build --oracle <target>/release/oracle --kspell <kannada-spell target>/release/kspell \
    --dictionary ../kannada-spell/dict/kn_IN --tasks grammar
uv run kbench suite-old-words   # re-extract suite/old-kannada-words.tsv from the Wikisource dump
```

The build is deterministic. CI rebuilds every task except grammar and fails if one of those items changes; grammar is rebuilt and checked locally against kannada-spell `a01fe20`.

## Baselines on local models

`kbench run` answers a fixed sample of the suite (60 items of each kind, the same for every model) with 1 local model through [MLX](https://github.com/ml-explore/mlx-lm), greedily, with thinking turned off. Each reply is saved as it comes in `results/suite/<model>.jsonl`, so a stopped run resumes. `kbench report` re-scores the saved replies into `results/suite/summary.csv`, so a scorer change needs no rerun.

How replies are scored:

- **Multiple choice:** the first standalone letter A to D in the reply. A reply with no letter counts as wrong and is counted under `no_answer`.
- **Exact answers:** the first line of the reply, after its last `=` if it is an equation, without a leading "Answer:", "Transliteration:" or "Word:", and without quotes, backticks, asterisks or a final period. It is compared after Unicode NFC, with zero-width characters, byte-order marks and replacement characters removed, spaces collapsed and Latin lowercased. Diacritics count: kannada for kannaḍa is wrong.

```sh
uv sync --extra run
uv run kbench run --model qwen3.5-4b --budget 3000   # stops before the budget; rerun to resume
uv run kbench report
scripts/run-baselines.sh                               # every model in turn, each under a time limit
```

The models are open-licensed and ungated, pinned by commit in [models.py](src/kbench/harness/models.py): 4 small ones of 2 to 4 billion parameters, Gemma 4 12B, and Sarvam-M, a 24 billion parameter model trained further on Indian languages. Loading Sarvam-M, transformers warns that its tokenizer has Mistral's incorrect split pattern; the tokenizer.json at the pinned commit already has the corrected pattern, and the fix changes none of the 840 prompts.

Results on 16 and 17 November 2026, 60 items of each kind per model, 840 per model. With 60 items a single score has a 95% interval of about 12 points either way, and 2 models' scores near 50% need to differ by about 18 points before the difference means much. Scores on `needs-reader` kinds are provisional until a Kannada reader checks the keys. Chance and the best shortcut are computed on the same 60 items.

| Kind | Key | Qwen 3.5 4B | Gemma 4 E2B | Phi-4-mini | Granite 4.1 3B | Gemma 4 12B | Sarvam-M 24B | Chance | Best shortcut |
|---|---|---|---|---|---|---|---|---|---|
| Reading (Belebele) | human | 77% | 62% | 48% | 55% | 83% | 90% | 25% | 33% |
| Grammar: case form | needs-reader | 100% | 78% | 68% | 83% | 92% | 98% | 25% | 32% |
| Grammar: verb form | needs-reader | 93% | 92% | 57% | 72% | 95% | 97% | 25% | 32% |
| Grammar: case recognition | needs-reader | 85% | 45% | 27% | 48% | 77% | 58% | 25% | 28% |
| Grammar: sandhi | needs-reader | 58% | 57% | 45% | 58% | 58% | 65% | 25% | 35% |
| Transliteration to ISO 15919 | computed | 27% | 53% | 8% | 8% | 37% | 25% | 0% | 0% |
| Transliteration to Kannada | computed | 45% | 45% | 7% | 28% | 60% | 75% | 0% | 0% |
| Numbers: read Kannada digits | computed | 100% | 100% | 28% | 0% | 100% | 100% | 0% | 0% |
| Numbers: write Kannada digits | computed | 100% | 80% | 2% | 60% | 98% | 100% | 0% | 0% |
| Numbers: arithmetic in Kannada digits | computed | 38% | 35% | 0% | 0% | 52% | 45% | 0% | 0% |
| Numbers: number words to digits | needs-reader | 22% | 28% | 10% | 22% | 47% | 75% | 0% | 0% |
| Numbers: digits to number words | needs-reader | 47% | 50% | 20% | 30% | 65% | 72% | 25% | 28% |
| Orthography: modern letters | computed | 53% | 47% | 28% | 57% | 17% | 65% | 25% | 28% |
| Orthography: spot the old letter | computed | 80% | 95% | 57% | 42% | 100% | 52% | 25% | 37% |

What the numbers say:

- **Sarvam-M 24B and Gemma 4 12B lead.** Averaged over the 14 kinds they score 73% and 70%, against 66% for Qwen 3.5 4B and 62% for Gemma 4 E2B. On the 7 kinds with computed keys the top 4 are within 4 points of each other (63% to 66%); the larger models pull ahead mostly on reading, numbers and the `needs-reader` kinds.
- **Sarvam-M, built for Indian languages, is best at reading Kannada and at number words.** It leads on Belebele (90%), transliteration into Kannada (75%), number words to digits (75%, 28 points above any other model) and modern letters (65%).
- **Size does not fix every task.** Qwen 3.5 4B still leads on case recognition (85%, against 77% and 58%). Gemma 4 E2B leads on transliteration into ISO 15919 (53%); Sarvam-M gets 25% there, often writing informal romanization such as uttarisabahudu without diacritics.
- **Exact answers stay hard.** No model gets more than 75% of transliterations into Kannada, 53% into ISO 15919, or 52% of arithmetic in Kannada digits right.
- **Phi-4-mini and Granite 4.1 3B can barely use Kannada digits.** Granite misreads ೧೮೪೪೪೪ as 78444, and Phi-4-mini writes ೦೦೦೦೦೦0 for 80.
- **Some scores do not beat the floor.**
  - Gemma 4 12B on modern letters (17%) is below chance: it answers A on 34 of 60 items, while 15 keys are A.
  - Phi-4-mini on case recognition (27%) and on digits to number words (20%) is at or below the best shortcut.
  - Phi-4-mini on modern letters (28%) equals the best shortcut.
  - Granite on digits to number words (30%) and on spotting the old letter (42%) is within noise of it.
  - Sarvam-M on spotting the old letter (52%) is only 15 points above it.
- **Format slips are few.** Where Kannada digits were asked, Gemma 4 E2B wrote Western digits 5 times and Kannada words, often garbled, 7 times. The scorer accepts an equation's result and ignores a stray replacement character, which a detokenizer left before Kannada digits 3 times.
- **Run time.** On an Apple Silicon Mac with 4-bit weights, the 840 items took 23 minutes for Gemma 4 12B and 39 minutes for Sarvam-M, against 9 minutes for Qwen 3.5 4B.

Replies for every item are in `results/suite/<model>.jsonl`. `kbench report` re-scores them into [summary.csv](results/suite/summary.csv), and a test checks that the committed summary matches the replies.

## Install

You need Python 3.13 or later and [uv](https://docs.astral.sh/uv/). Rebuilding the suite's answer keys also needs Rust, and the grammar items need a checkout of kannada-spell. Running the baselines needs an Apple Silicon Mac, because the models run through MLX.

```sh
git clone https://github.com/openkannada/kannada-llm-bench
cd kannada-llm-bench
uv sync --extra chart --extra run   # chart draws the token-tax chart; run loads local models
```

## Development

```sh
uv run pytest            # offline tests, under 5 seconds
uv run pytest -m network # the test that downloads a tokenizer
uv run ruff check . && uv run ruff format --check .
```

## Limits

- **The token tax comes from 1 text source.** Code, chat, government forms and Kannada written in Latin letters may cost differently, and tokens are not price. The [data card](results/token-tax/README.md) lists the other limits.
- **Some tokenizers are not measured:** gated ones such as Llama and Gemma 3, and Claude and Gemini, whose tokenizers are not public.
- **600 of the 2,037 test items wait on a Kannada reader.** Treat scores on the grammar and number-word kinds as provisional.
- **The baselines are small.** 60 items of each kind give each score a 95% interval of about 12 points either way, and only local open models with 4-bit weights were run.

## License

Code: [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option. Copyright 2026 The Open Kannada Authors.

- Results, in `results/`: CC BY 4.0. Cite the token-tax results with [CITATION.cff](CITATION.cff).
- Test items written here (grammar, numbers, transliteration) and `suite/lemmas.tsv`: CC BY 4.0.
- Items copied from share-alike sources (reading, from Belebele and FLORES-200; orthography and `suite/old-kannada-words.tsv`, from Kannada Wikisource): CC BY-SA 4.0. Each file keeps its own license. Following CC BY-SA 4.0 for the whole folder also satisfies them all, if that is simpler.

[DATA-LICENSE.md](DATA-LICENSE.md) has the details, [NOTICE.md](NOTICE.md) the credits, and [LICENSES/](LICENSES) the full license texts; [REUSE.toml](REUSE.toml) covers every file. Contributions are welcome under the [DCO](CONTRIBUTING.md). The name Open Kannada is covered by [TRADEMARKS.md](TRADEMARKS.md).

Part of [Open Kannada](https://github.com/openkannada), free and open-source tools that make Kannada work properly on computers.
