# Notice

kannada-llm-bench. Copyright 2026 The Open Kannada Authors. The code is under the MIT License or the Apache License 2.0, at your option. Data written for this project is under CC BY 4.0. [DATA-LICENSE.md](DATA-LICENSE.md) gives the license of each data file, and `REUSE.toml` covers every file.

This repository includes or is built from the third-party material below.

| Material | License | How it is used | In this repository |
| --- | --- | --- | --- |
| [Belebele](https://huggingface.co/datasets/facebook/belebele) kan_Knda, by Lucas Bandarkar et al. (Meta), revision `7899cdfa` | CC BY-SA 4.0 | Reading items | Yes, in `suite/items/reading.jsonl` (CC BY-SA 4.0) |
| [FLORES-200](https://github.com/facebookresearch/flores), by the NLLB Team and the FLORES authors | CC BY-SA 4.0 | The passages of the Belebele items | Yes, in `suite/items/reading.jsonl` (CC BY-SA 4.0) |
| [WMT24++](https://huggingface.co/datasets/google/wmt24pp) en-kn_IN, by Google, revision `fd7405c0` | Apache 2.0 | Token counts; single words for the transliteration items | Words only, in `suite/items/translit.jsonl`. The segments are downloaded and not stored. |
| [Kannada Wikisource](https://kn.wikisource.org), by its contributors, dump of 1 November 2026 | CC BY-SA 4.0 | Old Kannada words and their counts | Yes, in `suite/old-kannada-words.tsv` and `suite/items/orthography.jsonl` (CC BY-SA 4.0) |
| [kannada-spell](https://github.com/openkannada/kannada-spell) commit `a01fe20` | Code MIT; dictionary ODbL 1.0 | Paradigms for the grammar items | Generated forms only; see DATA-LICENSE.md |
| [kannadi](https://github.com/openkannada/kannadi) | MIT | The oracle's transliteration and Old Kannada letters | No, a build dependency of `oracle/` |
| Tokenizer files listed in `src/kbench/tokentax/registry.py` | Each publisher's own license | Token counts | No. Downloaded at pinned revisions and never stored. |
| Python packages in `uv.lock` and Rust crates in `oracle/Cargo.lock` | MIT, Apache-2.0, BSD and other permissive licenses | Dependencies | No |
