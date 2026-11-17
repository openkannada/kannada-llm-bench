# Data card: Kannada token tax

How many tokens 23 public tokenizers spend on the same text in Kannada and in English. Measured on 16 November 2026.

## What it measures

Each tokenizer counts the tokens in 960 English segments and in their professional Kannada translations. The headline figure is the token tax: Kannada tokens per English token, the Kannada total over the English total. A ratio of 2 means a Kannada user of that model pays twice as many tokens as an English user for the same text.

## Source text

- **Dataset:** [WMT24++](https://huggingface.co/datasets/google/wmt24pp) (Deutsch et al. 2025), file `en-kn_IN.jsonl`, revision `fd7405c06494bc66a57b25f55d217a72f96e60dc`, SHA-256 `b5ac7ca0…f5c757`. Apache 2.0.
- **Segments:** the 960 segments the dataset does not flag as a bad source, from 170 documents in 4 domains: 494 social media posts, 206 from literature, 149 news and 111 speech transcripts.
- **Words:** 32,262 English and 23,778 Kannada, split on whitespace.

The text itself is not stored here. `kbench token-tax` downloads it and checks the hash.

## Method

- Every tokenizer counts without special tokens: no start, end or chat-template tokens.
- Hugging Face tokenizers are pinned to a commit in [registry.py](../../src/kbench/tokentax/registry.py). The OpenAI encodings (cl100k, o200k) come from tiktoken 0.14.0, which checks their hashes.
- The 95% interval is the 2.5th to 97.5th percentile of the ratio over 1,000 resamples of the 170 documents with replacement, seed 0. It resamples documents because segments from 1 document share names and style. The domain ratios have no interval.
- Hugging Face tokenizers are loaded with `tokenizers` 0.23.3.
- 2 tokenizers are in the same group when they give the same count for every segment on both sides. 23 tokenizers form 12 groups.

## Files

### counts.csv

1 row per tokenizer and segment, 22,080 rows.

| Column | Meaning |
|---|---|
| `tokenizer` | the tokenizer's key in registry.py |
| `segment_id` | the segment's id in WMT24++ |
| `document_id` | the document the segment comes from |
| `domain` | news, social, speech or literary |
| `en_tokens` | tokens in the English segment |
| `kn_tokens` | tokens in the Kannada segment |

### summary.csv

1 row per tokenizer.

| Column | Meaning |
|---|---|
| `tokenizer` | the tokenizer's key in registry.py |
| `label` | a readable name |
| `models` | models that use this tokenizer |
| `en_tokens` | English tokens over all segments |
| `kn_tokens` | Kannada tokens over all segments |
| `ratio` | `kn_tokens` over `en_tokens`: the token tax, to 4 decimals |
| `ratio_low` | lower end of the 95% interval |
| `ratio_high` | upper end of the 95% interval |
| `kn_tokens_per_word` | Kannada tokens per Kannada word, to 2 decimals |
| `ratio_news` | the ratio on news segments only, to 3 decimals, like the other domains |
| `ratio_social` | the ratio on social media segments only |
| `ratio_speech` | the ratio on speech segments only |
| `ratio_literary` | the ratio on literature segments only |
| `same_counts_as` | other tokenizers with identical counts, space-separated; empty if none |

### identical.txt

1 line per group of tokenizers with identical counts, space-separated keys.

### The chart

`token-tax-light` and `token-tax-dark`, each as SVG and PNG. `kbench token-tax-chart` redraws them from summary.csv, deterministically.

## Limits

- **1 text source.** Half the segments are social media posts; the rest are literature, news and speech. Code, chat, government forms and colloquial Kannada written in Latin letters may cost differently.
- **The ratio depends on English too.** A tokenizer that spends more on English shows a lower ratio. Sarvam-1 spends 48,257 tokens on the English side against 40,372 to 42,398 for the others. Use `kn_tokens_per_word` to compare tokenizers on Kannada alone.
- **Words are not comparable across the 2 languages.** Kannada joins suffixes onto words, so the same text has fewer Kannada words.
- **Tokens are not price.** Providers price input and output tokens differently.
- **Not measured:** Llama 3.1, Llama 4, Gemma 3 and Tiny Aya, whose files are gated behind license terms on Hugging Face, and Claude and Gemini, whose tokenizers are not public and need an API key to count.

## License

The files in this folder are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit "Prasad Subrahmanya, Kannada token tax, 2026", or cite [CITATION.cff](../../CITATION.cff). They hold counts derived from WMT24++ (Apache 2.0), not its text.

## Reproduce

```sh
uv sync --extra chart
uv run kbench token-tax
uv run kbench token-tax-chart
```

A test checks that summary.csv and identical.txt follow from counts.csv.
