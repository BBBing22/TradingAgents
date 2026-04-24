#!/usr/bin/env bash
set -euo pipefail

if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

if ! curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
  nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
fi

for i in $(seq 1 30); do
  if curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

ollama pull tinyllama:1.1b

export TRADINGAGENTS_LLM_PROVIDER=ollama
export TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1
export TRADINGAGENTS_QUICK_THINK_LLM=tinyllama:1.1b
export TRADINGAGENTS_DEEP_THINK_LLM=tinyllama:1.1b

python scripts/ollama_smoke_test.py
