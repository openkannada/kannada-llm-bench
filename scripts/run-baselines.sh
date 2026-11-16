#!/bin/sh
# Run each local model on the suite sample, 1 at a time, each under a hard time limit. Set
# HEAVY_SERIAL to a queueing wrapper (it gets the directory, then the command) to share the
# machine with other heavy jobs. Rerun to resume: answered items are skipped.
set -eu
LIMIT=${LIMIT_SECONDS:-3600}
for model in ${MODELS:-qwen3.5-4b gemma-4-e2b phi-4-mini granite-4.1-3b}; do
  ${HEAVY_SERIAL:+$HEAVY_SERIAL "$PWD"} perl -e 'alarm shift; exec @ARGV' "$LIMIT" \
    uv run kbench run --model "$model" --budget $((LIMIT - 300)) "$@" || echo "$model stopped early"
done
uv run kbench report
