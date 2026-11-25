# Test suite details

How the 2,037 items resist shortcuts, what a Kannada reader should check first, and how to rebuild them. The [README](../README.md#test-suite) has the task table.

## Scoring against shortcuts

In the generated multiple-choice kinds each letter is the answer equally often, in a shuffled order. Some kinds can still be partly guessed without Kannada, from the shape of the options. [results/suite-shortcuts.csv](../results/suite-shortcuts.csv) scores 5 such strategies; read a model's score against the best of them as well as against chance (25%).

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

## What a Kannada reader should check first

- **Grammar.** The paradigms were checked against gold analyses written by an AI annotator, not by a person. The builder already removes these:
  - forms the dictionary also reads as another word (ಕಾಲಕ್ಕೆ is also a form of ಕಾಲ, 'time'), though variant spellings of the same word (ಕಾರ್ for ಕಾರು) are allowed. This leaves ಬರು and ಅಳು with no items, so 78 of the 80 listed words are used;
  - imperatives, because the paradigms give ಬರಿ for ಬನ್ನಿ;
  - plurals of kinship and mass nouns (ಅಣ್ಣಂದಿರು, not ಅಣ್ಣರು);
  - ಕಾಲು and ಮರೆ, whose paradigms mix in wrong stems.

  The case and verb distractors are other forms of the same word, so a paradigm error would show up as a wrong cell, not as a non-word.
- **Sandhi.** The distractors are joins the dictionary rejects. After a final ು the short join (ಕಾಡಲ್ಲಿ) is common in writing, so it is never used as a wrong answer.
- **Number words.** They follow 1 common written style (ನೂರ ಇಪ್ಪತ್ತೈದು, ಎರಡು ಸಾವಿರದ ಐನೂರು). Other correct styles exist, such as ನೂರಾ ಇಪ್ಪತ್ತೈದು, and are not accepted in the exact-answer kind. In the 4-option kind the options form a 2 by 2 grid of digits, so the right one cannot be found as the option most like the rest.
- **Old Kannada.** The task changes letters only. A full modern spelling would also change ಪ to ಹ and add final vowels (modern ಹೇಳಿ for ಪೇೞ್ದು); the question says to change only the obsolete letters.

## Rebuild the items

```sh
cargo build --release --manifest-path oracle/Cargo.toml     # kannadi answer keys
uv run kbench suite-build --oracle <target>/release/oracle --tasks reading translit numbers orthography
# grammar also needs kspell and a dictionary from a kannada-spell checkout
uv run kbench suite-build --oracle <target>/release/oracle --kspell <kannada-spell target>/release/kspell \
    --dictionary ../kannada-spell/dict/kn_IN --tasks grammar
uv run kbench suite-old-words   # re-extract suite/old-kannada-words.tsv from the Wikisource dump
```

The build is deterministic. CI rebuilds every task except grammar and fails if one of those items changes; grammar is rebuilt and checked locally against kannada-spell `a01fe20`.
