# 本地 Ollama（Qwen/Gemma）接入设计

日期：2026-04-24

## 背景

当前项目已支持 OpenAI 兼容协议的 provider 路由，并内置 `provider="ollama"` 的 base_url（默认 `http://localhost:11434/v1`），因此本地模型接入的核心不在于重写调用链，而在于：

- 让 CLI/配置能明确选择 Ollama 下的具体模型 tag（例如 qwen/gemma）
- 提供云端闭环验证路径：云端安装 Ollama + 拉取 1B 小模型 + 跑通一次完整流程
- 提供你拉取回本地后可复现的操作说明与最小配置

## 目标

- 在不改变现有 LLM 调用链的前提下，增强 `provider=ollama` 的本地模型可用性
- CLI 中可直接选择本地 Qwen/Gemma（通过 Ollama 的 model tag）
- 云端环境可挂载云端安装的 Ollama，并用 1B 左右小模型跑通
- 你拉回本地后可直接用本地 Ollama 替换/升级模型继续验证

## 非目标

- 不新增 `qwen_local` / `gemma_local` 等独立 provider（统一走 ollama）
- 不实现“自动发现本地模型”作为必须能力（可作为后续增强）
- 不引入与项目无关的推理框架或额外服务（除 Ollama 外）

## 方案概述（统一走 Ollama）

### 调用链

- 仍使用现有 OpenAI 兼容 client：`OpenAIClient(provider="ollama")`
- 请求发送到 `http://localhost:11434/v1` 的 Chat Completions
- 不需要 API Key（client 内部对 Ollama 写死为占位 key）

### 模型选择策略

在 `MODEL_OPTIONS["ollama"]` 中提供：

- 用于云端快速闭环验证的 1B 级模型（优先 `tinyllama:1.1b`）
- 典型本地 Qwen/Gemma 的 tag 示例（由用户在本地自行 pull）
  - 示例：`qwen2.5:0.5b`、`qwen2.5:1.5b`、`gemma2:2b` 等

说明：Ollama 的模型命名以本地已 pull 的 tag 为准，目录仅用于 CLI 选择与校验提示；实际可通过 “Custom model ID” 输入任意 tag。

### 配置与 profile

提供一个本地 profile（独立于默认配置，不影响线上默认 OpenAI）：

- `llm_provider=ollama`
- `backend_url=http://localhost:11434/v1`
- `quick_think_llm=tinyllama:1.1b`
- `deep_think_llm=tinyllama:1.1b`

落地形式二选一（实现阶段择优）：

1) 新增示例 env 文件：`.env.ollama.example`
2) 新增示例 config 文件（JSON/YAML，需与现有 config 读取方式一致）

## 云端闭环验证

### 云端安装与启动 Ollama

- 在云端 sandbox 安装 `ollama`（使用官方安装脚本或包管理）
- 启动 `ollama serve`（监听 11434）
- 拉取小模型：`ollama pull tinyllama:1.1b`

### 验证用例

最小闭环验证应覆盖：

- quick_think 与 deep_think 各发起至少一次 LLM 调用（确保两路都可用）
- 走完整 CLI 主流程一次（选 provider=ollama，模型为 tinyllama）

验收标准：

- 程序不报连接错误、认证错误、模型校验错误
- 能得到非空的模型输出（内容质量不作为验收要求）

## 本地复现路径

你拉取修改后的代码后，按以下方式在本地复现：

1) 安装并启动 Ollama
2) `ollama pull <你要的模型tag>`（例如 `qwen2.5:1.5b` 或 `gemma2:2b`）
3) 运行 CLI，选择 provider=ollama，并选择/输入对应 tag
4) 如需更大模型，只需更换 tag，不需要改代码

## 风险与边界处理

- Ollama 未启动：需要在 CLI/运行时报明确的连接失败提示
- 模型未 pull：Ollama 会返回错误；项目侧提供“Custom model”入口让用户自行输入 tag
- 模型目录与实际 tag 不一致：目录只作为引导，不作为强约束

## 变更点清单（实现阶段）

- 更新 `tradingagents/llm_clients/model_catalog.py`：补充 Ollama 的 1B 验证模型与 Qwen/Gemma 示例 tag
- 新增本地 Ollama profile 示例文件（不修改默认 provider=openai）
- 新增云端验证脚本/文档：安装 Ollama、启动服务、pull 小模型、跑通 CLI
- 增加一条最小测试（可选）：验证 `provider=ollama` 的模型名称允许通过、以及配置组合可构造 client

