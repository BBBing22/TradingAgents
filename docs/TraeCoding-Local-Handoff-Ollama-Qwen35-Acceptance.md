# TradingAgents 本地接力（Trae Coding）一键跑通指南（Ollama + 千问 3.5 / Q4 量化）

> 目标：在你本地用 Trae Coding 接力，把 **本仓库代码下载 → 安装依赖 → 挂载本地 Ollama → 拉取千问 3.5（若无则用 Q4 量化版）→ 跑通最小案例 → 给出可视化验收结果 → 桌面一键启动** 全链路跑清楚。  
> 适用：Windows 优先（也附 macOS / Linux 方案）。

---

## 0. 你需要准备什么

- 已安装 Git（可选，但推荐）
- 已安装 Python 3.10+（推荐 3.11/3.12）
- 已安装 Ollama（并能启动服务）
- 机器配置允许跑本地模型（建议至少 8GB 内存；模型越大要求越高）

---

## 1. 下载代码（两种方式二选一）

### 方式 A：Git Clone（推荐）

1) 打开终端（Windows 推荐 PowerShell）  
2) 选择一个你本地的工作目录，比如 `D:\code`

```bash
cd D:\code
git clone https://github.com/BBBing22/TradingAgents.git
cd TradingAgents
```

### 方式 B：下载 ZIP（不装 Git）

1) 打开仓库页面：`https://github.com/BBBing22/TradingAgents`  
2) 点击 `Code` → `Download ZIP`  
3) 解压后进入解压目录（保证目录名类似 `TradingAgents`）

---

## 2. 创建 Python 虚拟环境 + 安装依赖

### Windows（PowerShell）

```powershell
cd D:\code\TradingAgents
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

### macOS / Linux（bash/zsh）

```bash
cd ~/code/TradingAgents
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

---

## 3. 安装/启动 Ollama，并确认服务可用

### 3.1 启动 Ollama 服务

- Windows：在开始菜单启动 Ollama 或运行 `ollama serve`
- macOS/Linux：

```bash
ollama serve
```

### 3.2 验证 Ollama 服务可访问

```bash
curl -fsS http://localhost:11434/api/tags
```

期望：返回 JSON（即使列表为空也可以）。

---

## 4. 拉取并选择“千问 3.5”（若没有就选 Q4 量化版本）

> 不同环境/不同 Ollama 仓库里模型 tag 可能不完全一致。这里给“优先顺序 + 兜底”。

### 4.1 优先尝试千问 3.5（示例 tag）

请先尝试以下之一（哪个能成功就用哪个）：

```bash
ollama pull qwen3.5:latest
```

如果报 “not found / pull denied / manifest unknown”，说明当前仓库没有该 tag。

### 4.2 如果没有千问 3.5：选“Q4 量化”版本（优先）

一般命名会带 `q4`（例如 `q4_K_M`、`q4_0` 等）。请按你实际能拉到的 tag 选择。

示例（仅示意，实际以你能 pull 成功的 tag 为准）：

```bash
ollama pull qwen3.5:7b-instruct-q4_K_M
```

### 4.3 再兜底：先用更常见的 Qwen tag 跑通链路

```bash
ollama pull qwen3:latest
```

---

## 5. 配置本项目指向 Ollama（两种方式二选一）

### 方式 A：用 `.env` 一键配置（推荐）

在仓库根目录执行：

```bash
cp .env.ollama.example .env
```

然后按你最终要用的模型 tag 修改 `.env` 里的两行，例如：

- `TRADINGAGENTS_QUICK_THINK_LLM=qwen3.5:latest`
- `TRADINGAGENTS_DEEP_THINK_LLM=qwen3.5:latest`

### 方式 B：直接在终端设置环境变量

#### Windows（PowerShell）

```powershell
$env:TRADINGAGENTS_LLM_PROVIDER="ollama"
$env:TRADINGAGENTS_BACKEND_URL="http://localhost:11434/v1"
$env:TRADINGAGENTS_QUICK_THINK_LLM="qwen3.5:latest"
$env:TRADINGAGENTS_DEEP_THINK_LLM="qwen3.5:latest"
```

#### macOS / Linux

```bash
export TRADINGAGENTS_LLM_PROVIDER=ollama
export TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1
export TRADINGAGENTS_QUICK_THINK_LLM=qwen3.5:latest
export TRADINGAGENTS_DEEP_THINK_LLM=qwen3.5:latest
```

---

## 6. 最小可跑案例（两段验证：非可视化 + 可视化）

### 6.1 非可视化最小验证（Smoke Test）

目的：确认 **Python → 本项目 → OpenAI 兼容协议 → Ollama → 模型** 能打通并拿到返回。

```bash
python scripts/ollama_smoke_test.py
```

期望输出：

```text
OK
```

### 6.2 可视化最小验证（CLI 运行一次最轻流程）

启动 CLI：

```bash
python -m cli.main
```

推荐的“最小选择”（尽量减少 LLM 调用次数）：

- Step 1 Ticker：`SPY`（默认即可）
- Step 2 Date：选一个不在未来的日期（默认通常可用）
- Step 3 Output Language：建议 `Chinese (中文)`
- Step 4 Analysts Team：只勾选 1 个（比如 `News Analyst` 或 `Market Analyst`）
- Step 5 Research Depth：选 `Shallow`
- Step 6 LLM Provider：选 `Ollama`
- Step 7 Thinking Agents：如果没有你要的 tag，就选 `Custom model tag` 输入本地真实 tag
- 保存报告：选 `Y`，路径用默认即可

---

## 7. 验收标准（必须“可视化 + 可追溯”）

### 7.1 可视化验收截图（至少 3 张）

1) CLI 初始化界面（能看到你选择了 `Ollama`）  
2) 运行中界面（能看到 Agents/Reports 在推进）  
3) 完成界面（出现 `Analysis Complete!`，并提示保存 report）

建议截图文件名：

- `01_cli_init.png`
- `02_running.png`
- `03_complete.png`

### 7.2 报告落盘证据

CLI 保存后会生成一个报告目录，里面有：

- `complete_report.md`（总报告）
- 多个子目录（analysts/research/trading/risk/portfolio 等）

你需要提供：

- 报告目录的文件树截图（或复制终端输出）
- 打开 `complete_report.md` 的截图（证明链路产出成功）

---

## 8. 桌面一键启动（快捷方式）

### 8.1 Windows：创建一键启动脚本（推荐）

在仓库根目录新建 `start_tradingagents_ollama.bat`，内容如下（请把路径改成你自己的）：

```bat
@echo off
setlocal

cd /d D:\code\TradingAgents

call .venv\Scripts\activate.bat

set TRADINGAGENTS_LLM_PROVIDER=ollama
set TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1
set TRADINGAGENTS_QUICK_THINK_LLM=qwen3.5:latest
set TRADINGAGENTS_DEEP_THINK_LLM=qwen3.5:latest

python -m cli.main
pause
```

然后：

1) 右键 `start_tradingagents_ollama.bat` → “发送到” → “桌面快捷方式”  
2) 双击桌面快捷方式即可一键启动

### 8.2 macOS：一键启动（简化版）

在仓库根目录创建 `start_tradingagents_ollama.command`：

```bash
#!/bin/bash
cd "$HOME/code/TradingAgents"
source .venv/bin/activate
export TRADINGAGENTS_LLM_PROVIDER=ollama
export TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1
export TRADINGAGENTS_QUICK_THINK_LLM=qwen3.5:latest
export TRADINGAGENTS_DEEP_THINK_LLM=qwen3.5:latest
python -m cli.main
```

并执行：

```bash
chmod +x start_tradingagents_ollama.command
```

把这个文件拖到桌面即可双击运行（系统可能提示安全确认）。

### 8.3 Linux：.desktop 快捷方式

在 `~/Desktop/TradingAgents-Ollama.desktop` 写入：

```ini
[Desktop Entry]
Type=Application
Name=TradingAgents (Ollama)
Terminal=true
Exec=bash -lc 'cd ~/code/TradingAgents && source .venv/bin/activate && export TRADINGAGENTS_LLM_PROVIDER=ollama && export TRADINGAGENTS_BACKEND_URL=http://localhost:11434/v1 && export TRADINGAGENTS_QUICK_THINK_LLM=qwen3.5:latest && export TRADINGAGENTS_DEEP_THINK_LLM=qwen3.5:latest && python -m cli.main'
```

并执行：

```bash
chmod +x ~/Desktop/TradingAgents-Ollama.desktop
```

---

## 9. 常见问题快速排障

### 9.1 连接失败（Connection refused）

- Ollama 是否在运行：`curl http://localhost:11434/api/tags`
- `TRADINGAGENTS_BACKEND_URL` 必须是：`http://localhost:11434/v1`

### 9.2 模型 tag 不存在

- 查看本地已有 tag：`ollama list`
- 用本地真实存在的 tag 写入 `.env` 或环境变量
- 先用小模型跑通链路，再换千问 3.5 / Q4

### 9.3 Yahoo Finance API 限制（429/地区限制/网络受限）

本项目已支持对 yfinance 的代理配置与 429 重试：

- 建议你在 Clash 开启 TUN 后，直接让系统环境变量生效（最省事）
- 或者显式设置 `TRADINGAGENTS_YFINANCE_PROXY`（优先级最高）

#### Windows（PowerShell）

```powershell
$env:TRADINGAGENTS_YFINANCE_PROXY="http://127.0.0.1:7890"
```

#### macOS / Linux

```bash
export TRADINGAGENTS_YFINANCE_PROXY=http://127.0.0.1:7890
```

快速验证（不跑全链路，先确认 Yahoo 数据能取到）：

```bash
python - <<'PY'
import yfinance as yf
from tradingagents.dataflows.stockstats_utils import configure_yfinance
configure_yfinance()
print(yf.Ticker("SPY").history(period="1d").tail(1))
PY
```

---

## 10. 最终交付物（建议你放一个文件夹）

建议整理到一个文件夹（例如 `D:\TradingAgents_Acceptance\`）：

- `01_cli_init.png`
- `02_running.png`
- `03_complete.png`
- 报告目录（包含 `complete_report.md`）
- 你使用的 `.env`（不要包含任何真实 API Key；本地 Ollama 不需要 key）
