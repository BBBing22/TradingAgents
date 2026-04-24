# 本地 Ollama（Qwen/Gemma）接入 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改动现有 LLM 调用链的前提下，增强本地 Ollama 使用体验：CLI 可选 1B 小模型与 Qwen/Gemma tag；提供云端可闭环跑通的脚本与本地复现说明。

**Architecture:** 继续使用现有 OpenAI 兼容 client 的 `provider="ollama"` 路由，Ollama 模型通过 model tag 选择；新增“模型目录 + env 可选覆盖 + smoke scripts + 文档”来完成端到端验证。

**Tech Stack:** Python, LangChain (ChatOpenAI), LangGraph, Ollama (OpenAI compatible API `/v1/chat/completions`), unittest

---

## File Map

**Modify**
- `tradingagents/llm_clients/model_catalog.py`
- `tradingagents/default_config.py`
- `README.md`
- `tests/test_model_validation.py`

**Create**
- `.env.ollama.example`
- `scripts/ollama_smoke_test.py`
- `scripts/ollama_cloud_smoke.sh`
- `docs/ollama.md`

---

### Task 1: 扩展 Ollama 模型目录（含 Custom 入口）

**Files:**
- Modify: `tradingagents/llm_clients/model_catalog.py`
- Test: `tests/test_model_validation.py`

- [ ] **Step 1: 更新 Ollama quick/deep 选项，增加 1B 小模型与 Qwen/Gemma 示例 tag，并加入 Custom model**

将 `MODEL_OPTIONS["ollama"]` 改为如下结构（保留或调整现有条目均可，但必须包含 `tinyllama:1.1b` 与 `custom`）：

```python
"ollama": {
    "quick": [
        ("TinyLlama:1.1B (local, smoke test)", "tinyllama:1.1b"),
        ("Qwen2.5:0.5B (local)", "qwen2.5:0.5b"),
        ("Gemma2:2B (local)", "gemma2:2b"),
        ("Custom model tag", "custom"),
    ],
    "deep": [
        ("TinyLlama:1.1B (local, smoke test)", "tinyllama:1.1b"),
        ("Qwen2.5:1.5B (local)", "qwen2.5:1.5b"),
        ("Gemma2:2B (local)", "gemma2:2b"),
        ("Custom model tag", "custom"),
    ],
},
```

- [ ] **Step 2: 添加单测，确保 Ollama 目录包含 custom 选项**

在 `tests/test_model_validation.py` 增加测试（unittest 风格）：

```python
from tradingagents.llm_clients.model_catalog import get_model_options

def test_ollama_catalog_includes_custom_option(self):
    quick = [m for _, m in get_model_options("ollama", "quick")]
    deep = [m for _, m in get_model_options("ollama", "deep")]
    self.assertIn("custom", quick)
    self.assertIn("custom", deep)
```

- [ ] **Step 3: 运行测试确保通过**

Run:
```bash
pytest -q
```
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add tradingagents/llm_clients/model_catalog.py tests/test_model_validation.py
git commit -m "feat: expand ollama model catalog and enable custom tag"
```

---

### Task 2: 增加 env override（不改变默认 provider=openai）

**Files:**
- Modify: `tradingagents/default_config.py`
- Create: `.env.ollama.example`
- Test: `tests/test_model_validation.py`（或新建 `tests/test_default_config_env.py`）

- [ ] **Step 1: 让 LLM 关键配置支持环境变量覆盖（默认不变）**

在 `tradingagents/default_config.py` 将以下字段改为 `os.getenv` 覆盖模式（环境变量不存在时保持原默认值）：

```python
"llm_provider": os.getenv("TRADINGAGENTS_LLM_PROVIDER", "openai"),
"deep_think_llm": os.getenv("TRADINGAGENTS_DEEP_THINK_LLM", "gpt-5.4"),
"quick_think_llm": os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", "gpt-5.4-mini"),
"backend_url": os.getenv("TRADINGAGENTS_BACKEND_URL", "https://api.openai.com/v1"),
```

- [ ] **Step 2: 新增 `.env.ollama.example`**

内容如下（只做示例，不包含任何真实密钥）：

```bash
TRADINGAGENTS_LLM_PROVIDER=ollama
TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1
TRADINGAGENTS_QUICK_THINK_LLM=tinyllama:1.1b
TRADINGAGENTS_DEEP_THINK_LLM=tinyllama:1.1b
```

- [ ] **Step 3: 增加单测验证 env override 生效**

新建 `tests/test_default_config_env.py`：

```python
import os
import importlib

def test_default_config_env_override():
    os.environ["TRADINGAGENTS_LLM_PROVIDER"] = "ollama"
    os.environ["TRADINGAGENTS_BACKEND_URL"] = "http://localhost:11434/v1"
    os.environ["TRADINGAGENTS_QUICK_THINK_LLM"] = "tinyllama:1.1b"
    os.environ["TRADINGAGENTS_DEEP_THINK_LLM"] = "tinyllama:1.1b"

    import tradingagents.default_config as dc
    importlib.reload(dc)

    assert dc.DEFAULT_CONFIG["llm_provider"] == "ollama"
    assert dc.DEFAULT_CONFIG["backend_url"] == "http://localhost:11434/v1"
    assert dc.DEFAULT_CONFIG["quick_think_llm"] == "tinyllama:1.1b"
    assert dc.DEFAULT_CONFIG["deep_think_llm"] == "tinyllama:1.1b"
```

- [ ] **Step 4: 运行测试确保通过**

Run:
```bash
pytest -q
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tradingagents/default_config.py .env.ollama.example tests/test_default_config_env.py
git commit -m "feat: allow env overrides for local ollama profile"
```

---

### Task 3: 添加本地 Ollama LLM smoke test（快速验证）

**Files:**
- Create: `scripts/ollama_smoke_test.py`

- [ ] **Step 1: 新增 `scripts/ollama_smoke_test.py`（只验证 LLM 可调用）**

```python
import os

from tradingagents.llm_clients import create_llm_client


def main() -> None:
    base_url = os.getenv("TRADINGAGENTS_BACKEND_URL", "http://localhost:11434/v1")
    model = os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", "tinyllama:1.1b")

    client = create_llm_client(
        provider="ollama",
        model=model,
        base_url=base_url,
        timeout=60,
        max_retries=1,
    )
    llm = client.get_llm()

    resp = llm.invoke("Reply with exactly: OK")
    text = getattr(resp, "content", None) if hasattr(resp, "content") else str(resp)

    if not text or "OK" not in str(text):
        raise SystemExit(f"Unexpected response: {text}")

    print("OK")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 本地（或云端）手动运行验证**

Run:
```bash
python scripts/ollama_smoke_test.py
```
Expected: prints `OK` and exits 0

- [ ] **Step 3: Commit**

```bash
git add scripts/ollama_smoke_test.py
git commit -m "test: add ollama smoke test script"
```

---

### Task 4: 云端闭环脚本（安装/启动 Ollama + 拉取 1B 模型 + 跑 smoke）

**Files:**
- Create: `scripts/ollama_cloud_smoke.sh`

- [ ] **Step 1: 新增云端闭环脚本**

`scripts/ollama_cloud_smoke.sh` 内容如下（需要在 linux 环境可运行）：

```bash
#!/usr/bin/env bash
set -euo pipefail

if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

nohup ollama serve >/tmp/ollama-serve.log 2>&1 &

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
```

- [ ] **Step 2: 设置可执行权限并运行（云端闭环）**

Run:
```bash
chmod +x scripts/ollama_cloud_smoke.sh
./scripts/ollama_cloud_smoke.sh
```
Expected: 最终输出 `OK`，脚本退出码 0

- [ ] **Step 3: Commit**

```bash
git add scripts/ollama_cloud_smoke.sh
git commit -m "chore: add cloud ollama smoke runner"
```

---

### Task 5: 文档与 README 补充（让你拉回本地即可复现）

**Files:**
- Create: `docs/ollama.md`
- Modify: `README.md`

- [ ] **Step 1: 新增 `docs/ollama.md`（本地 Qwen/Gemma 指南）**

内容要求覆盖以下要点：

- 安装/启动 Ollama（仅给命令，不包含外链密钥）
- pull 1B smoke 模型：`ollama pull tinyllama:1.1b`
- pull Qwen/Gemma 示例（按 tag）：`ollama pull qwen2.5:1.5b`、`ollama pull gemma2:2b`
- CLI 运行：`python -m cli.main`，选择 provider=ollama，模型可选或用 custom 输入 tag
- 非交互快速验证：`python scripts/ollama_smoke_test.py`

- [ ] **Step 2: README 增加一段 “Local models with Ollama (Qwen/Gemma)” 并链接到 docs**

在 README 的 “Docker / For local models with Ollama” 附近加一个简短段落（不改变现有 docker 说明），包含：

- 1B smoke 测试命令
- 指向 `docs/ollama.md` 的链接

- [ ] **Step 3: Commit**

```bash
git add docs/ollama.md README.md
git commit -m "docs: add local ollama qwen/gemma guide"
```

---

## Plan Self-Review

- Spec 覆盖：模型目录增强、独立 profile（env override + `.env.ollama.example`）、云端闭环脚本、以及本地复现文档均已分配到任务
- Placeholder 扫描：无 TBD/TODO；每个变更点均给出具体文件路径、代码片段与命令

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-24-local-ollama-qwen-gemma-plan.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration
2. Inline Execution - Execute tasks in this session, batch execution with checkpoints

Which approach?

