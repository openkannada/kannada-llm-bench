# Data licenses

The code is under the MIT License or the Apache License 2.0, at your option (`LICENSE-MIT`, `LICENSE-APACHE`). The data has its own licenses. Data written here is under CC BY 4.0. Share-alike applies only to files copied from a share-alike source, and it stays with that file. The full license texts are in `LICENSES/`, and `REUSE.toml` gives the license of every file.

| Path | License | Source |
|---|---|---|
| `results/token-tax/` | CC BY 4.0 | Token counts computed here on WMT24++ en-kn_IN (Apache 2.0, Google), revision `fd7405c0`. The text itself is not stored in this repository. |
| `results/suite/`, `results/suite-shortcuts.csv` | CC BY 4.0 | Model replies and scores computed here. |
| `suite/lemmas.tsv`, `suite/items/grammar.jsonl`, `suite/items/numbers.jsonl` | CC BY 4.0 | Written for this suite. Grammar forms are generated with kannada-spell; see "kannada-spell and the ODbL" below. |
| `suite/items/translit.jsonl` | CC BY 4.0 | Single words from the Kannada side of WMT24++ (Apache 2.0, Google), with answers computed here. Single words are generally not copyrightable; they are credited to WMT24++. |
| `suite/items/reading.jsonl` | CC BY-SA 4.0 | Belebele kan_Knda (Bandarkar et al. 2023, Meta), revision `7899cdfa`, with its passages from FLORES-200 (CC BY-SA 4.0). |
| `suite/old-kannada-words.tsv`, `suite/items/orthography.jsonl` | CC BY-SA 4.0 | Single words and their counts from Kannada Wikisource (CC BY-SA 4.0), dump of 1 November 2026. |

Each file keeps its own license. Following CC BY-SA 4.0 for the whole folder also satisfies them all, if that is simpler. The tokenizer files are downloaded from their publishers at pinned revisions and are not stored here. Each stays under its publisher's license.

## kannada-spell and the ODbL

The grammar items are inflected forms of 78 of the 80 lemmas in `suite/lemmas.tsv`, generated from their paradigms in [kannada-spell](https://github.com/openkannada/kannada-spell) commit `a01fe20` (`kspell paradigm`). kannada-spell's dictionary is under the ODbL 1.0 because it is derived from Alar. The lemmas and glosses were written for this suite, the forms come from kannada-spell's code, and the items hold no other dictionary entry. Judgment of 17 November 2026: 78 paradigms are an insubstantial extract of a dictionary of over 139,000 entries, so the ODbL's share-alike terms do not apply to the grammar items.

## Credit

When you use or redistribute the data, credit this project and the sources of the files you use:

- Belebele: Lucas Bandarkar et al., "The Belebele Benchmark: a Parallel Reading Comprehension Dataset in 122 Language Variants", 2023, CC BY-SA 4.0.
- FLORES-200: the NLLB Team and the FLORES authors, CC BY-SA 4.0.
- WMT24++: Google, Apache 2.0.
- Kannada Wikisource: its contributors, CC BY-SA 4.0.

`NOTICE.md` lists the same sources with links.
