"""The local models run on the suite: small, open-licensed, ungated MLX builds pinned by commit."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    key: str
    label: str
    repo: str
    revision: str
    license: str
    """The upstream model's license. MLX builds do not always carry the tag: the Gemma 4 builds are
    tagged "gemma" or not at all and the Qwen 3.5 build has no tag, while google/gemma-4-E2B-it,
    google/gemma-4-12B-it, Qwen/Qwen3.5-4B and sarvamai/sarvam-m are Apache 2.0."""


MODELS: tuple[ModelSpec, ...] = (
    ModelSpec(
        "qwen3.5-4b",
        "Qwen 3.5 4B",
        "mlx-community/Qwen3.5-4B-4bit",
        "0e7ffd5c629ef7719d4cbc04069232580bfa9d9c",
        "Apache 2.0",
    ),
    ModelSpec(
        "gemma-4-e2b",
        "Gemma 4 E2B",
        "mlx-community/gemma-4-e2b-it-4bit",
        "238767527555cb75a05732a84dff5d6ba0dd6809",
        "Apache 2.0",
    ),
    ModelSpec(
        "phi-4-mini",
        "Phi-4-mini",
        "mlx-community/Phi-4-mini-instruct-4bit",
        "ac1c269cb4222a4e136a3d09edad301056c1f36a",
        "MIT",
    ),
    ModelSpec(
        "granite-4.1-3b",
        "Granite 4.1 3B",
        "mlx-community/granite-4.1-3b-4bit",
        "b1b476b5a17c46b7d6cd663b4a8ed44b66720aef",
        "Apache 2.0",
    ),
    ModelSpec(
        "gemma-4-12b",
        "Gemma 4 12B",
        "mlx-community/gemma-4-12B-it-4bit",
        "73bcf09092aa277861d5a191b989b666f7f32e8f",
        "Apache 2.0",
    ),
    ModelSpec(
        "sarvam-m",
        "Sarvam-M 24B",
        "mlx-community/sarvam-m-4bit",
        "5a59bc3756129d9f6bc058bf61954459a15d3d62",
        "Apache 2.0",
    ),
)


def by_key(key: str) -> ModelSpec:
    for spec in MODELS:
        if spec.key == key:
            return spec
    raise KeyError(key)
