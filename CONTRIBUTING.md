# Contributing to kannada-llm-bench

Thank you for helping. Wrong answer keys, bugs, tokenizers to add and ideas go in [GitHub issues](https://github.com/openkannada/kannada-llm-bench/issues). For a wrong key, give the item id and the answer you expect. For a security problem, follow [SECURITY.md](SECURITY.md) instead.

## Sign off every commit (DCO)

Open Kannada uses the [Developer Certificate of Origin](https://developercertificate.org/) (DCO), not a contributor license agreement. Every commit needs a `Signed-off-by` line with your name and email. It certifies that you wrote the change, or otherwise have the right to submit it under this repository's licenses.

`git commit -s` adds the line from your Git settings:

```text
Signed-off-by: Your Name <you@example.com>
```

If you forgot, `git commit --amend -s` signs off the last commit, and `git rebase --signoff origin/main` signs off every commit on your branch.

You keep the copyright in your work. It is licensed under the licenses of the files it changes, as the README's License section describes, and you join "The Open Kannada Authors".

CI checks every commit in a pull request for the line.

## Making a change

[AGENTS.md](AGENTS.md) has the commands, the layout and the rules, for people and AI agents alike. Items are generated, never edited by hand: change the builder and rebuild. Before you open a pull request, run:

```sh
uv run pytest
uv run ruff check . && uv run ruff format --check .
cargo test --manifest-path oracle/Cargo.toml
uvx reuse lint
```

Keep each data file under 1 license. A file copied from a share-alike source keeps that license; see [DATA-LICENSE.md](DATA-LICENSE.md).
