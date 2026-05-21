# Day 1 实操代码

## Demo Agent

`recent_docs_agent.py` 是第一个 demo agent。它基于 OpenAI Agents SDK quickstart 的结构：

- `Agent`：定义 agent 名称、指令、模型和工具
- `Runner.run`：运行 agent
- `@function_tool`：把本地 Python 函数注册成 agent 工具

这个 demo 的工具只扫描文件元数据：相对路径、修改时间、扩展名和文件大小；不会读取文档正文内容，也会跳过 `.obsidian/`、`.git/` 等目录。

## 安装

```bash
uv venv
uv pip install -r requirements.txt
```

## 本地验证扫描工具

不需要 API key：

```bash
uv run python recent_docs_agent.py --scan-only
```

## 运行 Agent

复制 `.env.example` 为 `.env`，填入本地 key：

```bash
cp .env.example .env
uv run python recent_docs_agent.py
```

默认示例配置为 DeepSeek：

```bash
AGENT_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
AGENT_MODEL=deepseek-chat
```

也可以切换回 OpenAI：

```bash
AGENT_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
AGENT_MODEL=gpt-5.5
uv run python recent_docs_agent.py
```

## 周报撰写专家

`weekly_report_agent.py` 定义了一个单独的 specialist agent：

- 名称：`周报撰写专家`
- 目标：读取 `VULT/work/日志/每日进展/` 中本周日报，自动整理成周报
- 输出目录：`VULT/work/日志/周报/`

它使用：

- 动态 `instructions` 回调：把周起止日期等运行时信息注入 instructions
- 简短 `handoff_description`：方便后续被路由 agent 选中
- `output_type=WeeklyReportDraft`：让下游代码拿到结构化结果后再写文件
- `RunContextWrapper.context`：把本地路径、日期窗口、输出目录等上下文留在应用侧，不直接塞进模型上下文

运行：

```bash
uv run python weekly_report_agent.py
```
