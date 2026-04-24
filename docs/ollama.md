# Local Models with Ollama (Qwen/Gemma)

## Prerequisites

- Install Ollama and start the service:

```bash
ollama serve
```

- Verify Ollama is reachable:

```bash
curl -fsS http://localhost:11434/api/tags
```

## Quick Smoke Test (1B)

```bash
ollama pull tinyllama:1.1b
export TRADINGAGENTS_LLM_PROVIDER=ollama
export TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1
export TRADINGAGENTS_QUICK_THINK_LLM=tinyllama:1.1b
export TRADINGAGENTS_DEEP_THINK_LLM=tinyllama:1.1b
python scripts/ollama_smoke_test.py
```

Expected output: `OK`

## Using Qwen / Gemma (local tags)

Pull one or more models:

```bash
ollama pull qwen2.5:1.5b
ollama pull gemma2:2b
```

Then point TradingAgents to those tags:

```bash
export TRADINGAGENTS_LLM_PROVIDER=ollama
export TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1
export TRADINGAGENTS_QUICK_THINK_LLM=qwen2.5:1.5b
export TRADINGAGENTS_DEEP_THINK_LLM=gemma2:2b
```

## CLI Run

```bash
python -m cli.main
```

In Step 6 select `Ollama`, then choose a model tag from the list or use `Custom model tag` to type your local tag.

## Yahoo Finance API 제한/代理

If your network hits Yahoo Finance rate limits or region blocks, set a proxy (Clash TUN works well):

```bash
export TRADINGAGENTS_YFINANCE_PROXY=http://127.0.0.1:7890
```

## Optional: Use .env Profile

```bash
cp .env.ollama.example .env
python -m cli.main
```
