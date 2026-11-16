"""The 2 programs that compute answer keys: kannada-spell's kspell and this repository's oracle."""

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


def run_lines(command: Sequence[str], lines: Sequence[str]) -> list[str]:
    """Feed 1 input per line and return the output lines."""
    result = subprocess.run(
        command,
        input="".join(line + "\n" for line in lines),
        capture_output=True,
        text=True,
        check=True,
        timeout=300,
    )
    return result.stdout.splitlines()


@dataclass(frozen=True)
class Oracle:
    binary: Path

    def translit(self, words: Sequence[str], source: str, target: str) -> list[str]:
        return run_lines([str(self.binary), "translit", source, target], words)

    def modernize(self, words: Sequence[str]) -> list[str]:
        return run_lines([str(self.binary), "modernize"], words)

    def has_old(self, words: Sequence[str]) -> list[bool]:
        return [line == "1" for line in run_lines([str(self.binary), "has-old"], words)]


@dataclass(frozen=True)
class Kspell:
    binary: Path
    dictionary: Path

    def _run(self, command: str, words: Sequence[str]) -> list[tuple[str, str]]:
        lines = run_lines([str(self.binary), command, "--dictionary", str(self.dictionary)], words)
        return [tuple(line.split("\t")[:2]) for line in lines]  # type: ignore[misc]

    def paradigm(self, lemma: str) -> list[tuple[str, str]]:
        """Every (form, reading) of a lemma, such as ("ಮರಕ್ಕೆ", "ಮರ+n+dat")."""
        return self._run("paradigm", [lemma])

    def readings(self, words: Sequence[str]) -> dict[str, set[str]]:
        """Every reading the dictionary gives each word; an empty set for a word it rejects."""
        found: dict[str, set[str]] = {word: set() for word in words}
        for word, reading in self._run("analyze", words):
            if reading != "?":
                found[word].add(reading)
        return found

    def accepted(self, words: Sequence[str]) -> set[str]:
        """The words the dictionary accepts with any reading."""
        return {word for word, readings in self.readings(words).items() if readings}
