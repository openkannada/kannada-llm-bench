"""Run 1 local model over the items with MLX, greedily, saving each reply as it comes."""

import json
import time
from collections.abc import Sequence
from pathlib import Path

from kbench.harness import prompts
from kbench.harness.models import ModelSpec
from kbench.harness.replies import read_replies
from kbench.suite.items import Item

CHOICE_TOKENS = 8
EXACT_TOKENS = 48


def done_ids(path: Path) -> set[str]:
    return set(read_replies(path)) if path.exists() else set()


def run(spec: ModelSpec, items: Sequence[Item], out: Path, budget_seconds: float) -> int:
    """Answer the items not yet in `out`, stopping before `budget_seconds` runs out. Returns how many
    items were answered in this call."""
    from mlx_lm import generate, load

    model, tokenizer = load(spec.repo, revision=spec.revision)
    finished = done_ids(out)
    start = time.monotonic()
    answered = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        for item in items:
            if item.id in finished:
                continue
            if time.monotonic() - start > budget_seconds:
                break
            prompt = tokenizer.apply_chat_template(
                prompts.messages(item), add_generation_prompt=True, tokenize=False, enable_thinking=False
            )
            began = time.monotonic()
            reply = generate(
                model, tokenizer, prompt, max_tokens=CHOICE_TOKENS if item.is_choice else EXACT_TOKENS
            )
            row = {"id": item.id, "reply": reply, "seconds": round(time.monotonic() - began, 2)}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            answered += 1
    return answered
