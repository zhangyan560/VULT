---
title: Claude Code 工具集成
date: 2026-04-09
tags:
  - research/youtube
  - research/claude-code
  - research/tools
  - type/research
related:
  - "[[Chase-H-AI 频道分析]]"
  - "[[Claude Code 核心教程]]"
  - "[[Claude Code 高级技巧]]"
---

# Claude Code 工具集成

![[Claude Code工具集成-infographic.png|600]]


> [!note] 来源
> 本笔记整理自 [[Chase-H-AI 频道分析]] 中关于工具集成的视频系列。

## 类别定位

**核心论点**：CLI > MCP。CLI 工具原生运行在终端，token 消耗更低、速度更快。

## 视频列表

| 视频标题 | 观看量 | URL |
|---------|--------|-----|
| 10 CLI Tools That Make Claude Code UNSTOPPABLE | 54,543 | [链接](https://www.youtube.com/watch?v=uULvhQrKB_c) |
| 10 Claude Code Plugins to 10X Your Projects | 72,205 | [链接](https://www.youtube.com/watch?v=OFyECKgWXo8) |
| CLI-Anything Just Brought Claude Code Into The Future | 80,373 | [链接](https://www.youtube.com/watch?v=Uzd2ckXnsg0) |
| Claude Code + Codex = AI GOD | 29,560 | [链接](https://www.youtube.com/watch?v=L7NPhaUBpZE) |
| Claude Code + Firecrawl = Web Scraping CHEAT CODE | 16,695 | [链接](https://www.youtube.com/watch?v=phuyYL0L7AA) |
| Claude Code + NotebookLM = CHEAT CODE | 143,306 | [链接](https://www.youtube.com/watch?v=usTeU4Uh0iM) |
| Claude Code + NotebookLM + Obsidian = GOD MODE | 65,731 | [链接](https://www.youtube.com/watch?v=kU3qYQ7ACMA) |
| Claude Code + Obsidian = UNSTOPPABLE | 110,059 | [链接](https://www.youtube.com/watch?v=eRr2rTKriDM) |
| Claude Code + Playwright = INSANE Browser Automations | 80,099 | [链接](https://www.youtube.com/watch?v=I9kO6-yPkfM) |
| Google's New CLI Just Fully Unlocked Claude Code | 19,625 | [链接](https://www.youtube.com/watch?v=M5AeWsQ2v58) |
| GSD 2 vs Claude Code: A New AI King? | 44,981 | [链接](https://www.youtube.com/watch?v=ZgfybHGxzJU) |
| OpenClaw Google Setup is a Nightmare (Here's the Fix) | 30,420 | [链接](https://www.youtube.com/watch?v=h_N2Y2XyR3M) |
| Clawdbot: What Nobody's Telling You | 10,853 | [链接](https://www.youtube.com/watch?v=5p8-K-nsQsc) |

## 核心框架：CLI vs MCP 对比

| 维度 | CLI | MCP Server |
|------|-----|-----------|
| Token 消耗 | 低（原生终端） | 高（协议开销）|
| 速度 | 快 | 慢 |
| 安装复杂度 | 简单 | 复杂 |
| 适用场景 | 大多数任务 | 特定深度集成 |

> [!example] 具体数据
> Playwright CLI 执行相同任务比 Playwright MCP 节省约 **90,000 tokens**

## 工具分类地图

### 数据获取
- **Firecrawl**：网页抓取，转为 Markdown 喂给 Claude
- **yt-dlp**：YouTube 视频/转录提取
- **Playwright**：浏览器自动化、E2E 测试

### 知识管理
- **Obsidian**：Vault 作为 Claude 的长期记忆层
- **NotebookLM**：多来源研究分析、音频摘要生成
- **LightRAG / RAG-Anything**：本地 RAG 系统

### AI 代码能力扩展
- **OpenAI Codex CLI**：代码生成辅助
- **Google Gemini CLI**：解锁免费 API 额度
- **CLI-Anything**：将任意工具转为 Claude 可调用的 CLI

### 开发工作流
- **GSD 2**：结构化开发流程工具
- **Clawdbot / OpenClaw**：Claude Code 的 GUI 封装

## Claude Code + Obsidian 工作流

```
Claude Code 工作
     ↓
记录为 Markdown 文件 → Obsidian Vault
     ↓
Obsidian 组织为知识图谱
     ↓
下次会话 Claude 读取 Vault → 继承记忆
     ↓
/dream 命令整合 + 清理过时内容
```

## Claude Code + NotebookLM 工作流

```
收集 YouTube/文档/网页 URL
     ↓
notebooklm source add → 建立知识库
     ↓
notebooklm ask → 深度问答分析
     ↓
notebooklm generate infographic/podcast → 交付物
     ↓
Claude Code 将结果写入 Obsidian
```

## 信息图

> [!note] 信息图位置
> `~/Downloads/Mastering the AI CLI Stack.png`（已下载）
