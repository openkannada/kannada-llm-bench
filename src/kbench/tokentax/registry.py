"""The tokenizers measured, each pinned to an exact file revision."""

from dataclasses import dataclass
from enum import Enum


class Kind(Enum):
    TIKTOKEN = "tiktoken"
    HF = "hf"
    KIMI = "kimi"


@dataclass(frozen=True)
class TokenizerSpec:
    key: str
    label: str
    models: str
    kind: Kind
    source: str
    revision: str = ""
    file: str = "tokenizer.json"


@dataclass(frozen=True)
class Unmeasured:
    label: str
    reason: str


def hf(key: str, label: str, models: str, repo: str, revision: str) -> TokenizerSpec:
    return TokenizerSpec(key, label, models, Kind.HF, repo, revision)


TOKENIZERS: tuple[TokenizerSpec, ...] = (
    TokenizerSpec("cl100k", "GPT-4 (cl100k)", "GPT-4, GPT-3.5", Kind.TIKTOKEN, "cl100k_base"),
    TokenizerSpec("o200k", "GPT-4o (o200k)", "GPT-4o, GPT-4.1, o-series", Kind.TIKTOKEN, "o200k_base"),
    hf(
        "gpt-oss",
        "gpt-oss",
        "gpt-oss 20B and 120B",
        "openai/gpt-oss-20b",
        "6cee5e81ee83917806bbde320786a8fb61efebee",
    ),
    hf(
        "qwen2.5",
        "Qwen 2.5",
        "Qwen 2.5",
        "Qwen/Qwen2.5-7B-Instruct",
        "a09a35458c702b33eeacc393d103063234e8bc28",
    ),
    hf("qwen3", "Qwen 3", "Qwen 3", "Qwen/Qwen3-8B", "b968826d9c46dd6066d109eabc6255188de91218"),
    hf("qwen3.5", "Qwen 3.5", "Qwen 3.5", "Qwen/Qwen3.5-4B", "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"),
    hf("qwen3.8", "Qwen 3.8", "Qwen 3.8", "Qwen/Qwen3.8-27B", "37561816e66b5b9153b1b64c10968c18c1e6f4a0"),
    hf(
        "deepseek-v3",
        "DeepSeek V3",
        "DeepSeek V3",
        "deepseek-ai/DeepSeek-V3",
        "e815299b0bcbac849fa540c768ef21845365c9eb",
    ),
    hf(
        "deepseek-v4.1",
        "DeepSeek V4.1",
        "DeepSeek V4.1 Flash",
        "deepseek-ai/DeepSeek-V4.1-Flash",
        "314113f8a7dadb388215396ba5fbee2c610a04d6",
    ),
    hf(
        "mistral-nemo",
        "Mistral Nemo",
        "Mistral Nemo",
        "mistralai/Mistral-Nemo-Instruct-2407",
        "04d8a90549d23fc6bd7f642064003592df51e9b3",
    ),
    hf(
        "mistral-medium-3.5",
        "Mistral Medium 3.5",
        "Mistral Medium 3.5",
        "mistralai/Mistral-Medium-3.5-128B",
        "22b2b868a15677cfa6061277ed2f653d1349a9ab",
    ),
    hf(
        "mistral-large-4",
        "Mistral Large 4",
        "Mistral Large 4",
        "mistralai/Mistral-Large-4-1T-A52B",
        "af26e7869af601441d5cdf75a1272469ddc3d059",
    ),
    hf("gemma4", "Gemma 4", "Gemma 4", "google/gemma-4-E4B-it", "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c"),
    hf("sarvam-1", "Sarvam-1", "Sarvam-1", "sarvamai/sarvam-1", "e9607337286ddf496d4a2562b194e489dcf3feea"),
    hf("sarvam-m", "Sarvam-M", "Sarvam-M", "sarvamai/sarvam-m", "01534a53c46f2788e392dbb3d994e0fa8f04d3fd"),
    hf(
        "sarvam-30b",
        "Sarvam 30B",
        "Sarvam 30B",
        "sarvamai/sarvam-30b",
        "2784c524a2f2a08f597adc5530d13ec66079e347",
    ),
    hf(
        "sarvam-105b",
        "Sarvam 105B",
        "Sarvam 105B",
        "sarvamai/sarvam-105b",
        "abe264bdb8fb2244daadaa59ebc2020b3c139e89",
    ),
    TokenizerSpec(
        "kimi-k2",
        "Kimi K2",
        "Kimi K2",
        Kind.KIMI,
        "moonshotai/Kimi-K2-Instruct",
        "fd1984e2b7a3350dbf7305fe73a4ede25c14de50",
        "tiktoken.model",
    ),
    TokenizerSpec(
        "kimi-k3",
        "Kimi K3",
        "Kimi K3",
        Kind.KIMI,
        "moonshotai/Kimi-K3",
        "f831ab66814297da540d832a5235f8e904f29d06",
        "tiktoken.model",
    ),
    hf("glm-5.3", "GLM-5.3", "GLM-5.3", "zai-org/GLM-5.3", "ba32f8c19c8738e2c57c71798c601d477a7bf844"),
    hf(
        "phi-4-mini",
        "Phi-4-mini",
        "Phi-4-mini",
        "microsoft/Phi-4-mini-instruct",
        "cfbefacb99257ffa30c83adab238a50856ac3083",
    ),
    hf(
        "granite-4.1",
        "Granite 4.1",
        "Granite 4.1",
        "ibm-granite/granite-4.1-8b",
        "1504002f650e656a0a3789d99574df12e3e94ed0",
    ),
    hf(
        "krutrim-2",
        "Krutrim-2",
        "Krutrim-2",
        "krutrim-ai-labs/Krutrim-2-instruct",
        "b2f4411404153b4afe4b8c721bd5ca5dc3481b89",
    ),
)

UNMEASURED: tuple[Unmeasured, ...] = (
    Unmeasured("Llama 3.1", "Hugging Face gates the files behind Meta's license terms"),
    Unmeasured("Llama 4", "Hugging Face gates the files behind Meta's license terms"),
    Unmeasured("Gemma 3", "Hugging Face gates the files behind Google's Gemma terms"),
    Unmeasured("Tiny Aya", "Hugging Face gates the files behind Cohere's terms"),
    Unmeasured("Claude", "the tokenizer is not public; countable through Anthropic's token-counting API"),
    Unmeasured("Gemini", "the tokenizer is not public; countable through Google's countTokens API"),
)


def by_key(key: str) -> TokenizerSpec:
    for spec in TOKENIZERS:
        if spec.key == key:
            return spec
    raise KeyError(key)
