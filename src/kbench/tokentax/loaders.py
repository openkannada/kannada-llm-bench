# SPDX-FileCopyrightText: 2026 The Open Kannada Authors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""Turn a tokenizer spec into a function that counts tokens."""

from collections.abc import Callable

import tiktoken
from huggingface_hub import hf_hub_download
from tiktoken.load import load_tiktoken_bpe
from tokenizers import Tokenizer

from kbench.tokentax.registry import Kind, TokenizerSpec

Counter = Callable[[str], int]

# Kimi's split pattern, from tokenization_kimi.py in moonshotai/Kimi-K2-Instruct (identical in Kimi-K3).
KIMI_PATTERN = "|".join(
    [
        r"""[\p{Han}]+""",
        r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]*[\p{Ll}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
        r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]+[\p{Ll}\p{Lm}\p{Lo}\p{M}&&[^\p{Han}]]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
        r"""\p{N}{1,3}""",
        r""" ?[^\s\p{L}\p{N}]+[\r\n]*""",
        r"""\s*[\r\n]+""",
        r"""\s+(?!\S)""",
        r"""\s+""",
    ]
)


def _download(spec: TokenizerSpec) -> str:
    return hf_hub_download(spec.source, spec.file, revision=spec.revision)


def load(spec: TokenizerSpec) -> Counter:
    """A function giving the number of tokens in a text, without special tokens."""
    match spec.kind:
        case Kind.TIKTOKEN:
            encoding = tiktoken.get_encoding(spec.source)
            return lambda text: len(encoding.encode_ordinary(text))
        case Kind.KIMI:
            encoding = tiktoken.Encoding(
                spec.key,
                pat_str=KIMI_PATTERN,
                mergeable_ranks=load_tiktoken_bpe(_download(spec)),
                special_tokens={},
            )
            return lambda text: len(encoding.encode_ordinary(text))
        case Kind.HF:
            tokenizer = Tokenizer.from_file(_download(spec))
            return lambda text: len(tokenizer.encode(text, add_special_tokens=False).ids)
