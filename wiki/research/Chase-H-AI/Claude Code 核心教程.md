---
title: Claude Code 核心教程
date: 2026-04-09
tags:
  - research/youtube
  - research/claude-code
  - type/research
related:
  - "[[Chase-H-AI 频道分析]]"
  - "[[Claude Code 工具集成]]"
  - "[[Claude Code 高级技巧]]"
---

# Claude Code 核心教程

![[Claude Code核心教程-infographic.png|600]]


> [!note] 来源
> 本笔记整理自 [[Chase-H-AI 频道分析]] 频道中的基础教学类视频。

## 类别定位

面向无技术背景的用户，从"零"到"AI 开发者"的系统路径。核心理念：终端素养 + 协作心态 + Skills 架构。

## 视频列表

| 视频标题 | 时长 | 观看量 | URL |
|---------|------|--------|-----|
| 567 Hours of Claude Code Lessons in 20 Minutes | 21min | 62,657 | [链接](https://www.youtube.com/watch?v=rVEoyx349Hk) |
| All 35 Claude Code Concepts Explained for Non Coders | 57min | 3,765 | [链接](https://www.youtube.com/watch?v=UAMAAoSPu8o) |
| The 6 Levels of Claude Code Explained | 33min | 112,970 | [链接](https://www.youtube.com/watch?v=TUKYbUIXLOE) |
| Learn 90% of Claude Code in 31 Minutes | 31min | 39,286 | [链接](https://www.youtube.com/watch?v=TwkdDcO4vWQ) |
| 10 Minute Masterclass: Claude Code Skills | 10min | 31,468 | [链接](https://www.youtube.com/watch?v=UtGszoiwrsQ) |
| Claude Code Skills Just Got a MASSIVE Upgrade | 12min | 105,719 | [链接](https://www.youtube.com/watch?v=UxfeF4bSBYI) |
| Caveman Claude Code Is the New Meta | 11min | 8,305 | [链接](https://www.youtube.com/watch?v=4FO1Liu-ttk) |
| Claude Code: 100% Free. 100% Private. 100% Local. | 13min | 37,185 | [链接](https://www.youtube.com/watch?v=GHGGkIMYDxo) |
| Did Claude Code Just Get Plan Mode 2.0? | 9min | 13,118 | [链接](https://www.youtube.com/watch?v=eEYbwJWVQtQ) |
| Claude Code's Hidden /dream Feature | 9min | 26,673 | [链接](https://www.youtube.com/watch?v=E-1Lmyv6Cjo) |

## 核心框架：The 6 Levels of Claude Code

```
Level 1 - Prompt Engineer    → 使用 web UI，无终端
Level 2 - Vibe Coder         → 进入终端，盲目接受所有输出
Level 3 - Collaborator       → 理解构建模块，主动提问
Level 4 - Skills Builder     → 创建并测试自定义 Skills
Level 5 - Architect          → 设计多工具 Pipeline
Level 6 - Orchestrator       → 编排多个 AI Agent 并行工作
```

## 核心框架：35 Claude Code 概念图谱

分为四个阶段：
1. **必须知道的基础**：安装、终端使用、权限设置
2. **提升效率的核心**：Plan Mode、Skills、上下文管理
3. **进阶工具**：多 Agent、并行任务、工具集成
4. **Power User 技巧**：自定义 Skills、AB 测试、Status Line

## Skills 核心理解

- **定义**：Skills 是 Markdown 文件，是"专业化 Prompt 指令"
- **两种类型**：
  - **能力提升**：让 Claude 做到它本来无法做的事（如 frontend-design skill）
  - **编码偏好**：强制 Claude 按你的工作流执行特定流程
- **原则**：用 Skill Creator 做 A/B 测试，只安装任务所需的 skill

## Caveman 模式的科学原理

> "Less is more" in prompt engineering

- 极简指令反而比过度详细的 CLAUDE.md 效果更好
- 原因：过多指令稀释注意力，降低核心任务权重
- 例外：有且只有一个场景需要 CLAUDE.md — 定义项目范围

## 本地化运行（Free + Private）

- 使用 Ollama 运行本地模型（如 Llama、Mistral）
- 完全离线，数据不离开本机
- 适合：敏感数据处理、离线环境、成本控制

## 信息图

> [!note] 信息图位置
> `~/Downloads/AI Software Developer Masterclass Guide.png`（已下载）
