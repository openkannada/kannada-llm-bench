# Baselines on local models


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

The models are open-licensed and ungated, pinned by commit in [models.py](../src/kbench/harness/models.py): 4 small ones of 2 to 4 billion parameters, Gemma 4 12B, and Sarvam-M, a 24 billion parameter model trained further on Indian languages. Loading Sarvam-M, transformers warns that its tokenizer has Mistral's incorrect split pattern; the tokenizer.json at the pinned commit already has the corrected pattern, and the fix changes none of the 840 prompts.

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

Replies for every item are in `results/suite/<model>.jsonl`. `kbench report` re-scores them into [summary.csv](../results/suite/summary.csv), and a test checks that the committed summary matches the replies.
