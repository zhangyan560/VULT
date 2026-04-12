---
title: Claude Code 高级技巧
date: 2026-04-09
tags:
  - research/youtube
  - research/claude-code
  - type/research
related:
  - "[[Chase-H-AI 频道分析]]"
  - "[[Claude Code 工具集成]]"
  - "[[Claude Code 核心教程]]"
---

# Claude Code 高级技巧

> [!note] 来源
> 本笔记整理自 [[Chase-H-AI 频道分析]] 中关于性能优化和进阶技术的视频系列。

## 类别定位

面向已掌握基础的用户，专注于：Context Rot 对抗、RAG 本地化、Caveman 模式、token 效率优化。

## 视频列表

| 视频标题 | 观看量 | URL |
|---------|--------|-----|
| 9 Hacks to Use Claude Code Better Than 90% of People | 21,658 | [链接](https://www.youtube.com/watch?v=XkSBO-CZDFs) |
| Caveman Claude Code Is the New Meta | 8,305 | [链接](https://www.youtube.com/watch?v=4FO1Liu-ttk) |
| Claude Code + LightRAG = UNSTOPPABLE | 65,659 | [链接](https://www.youtube.com/watch?v=QHlB-RJfx8w) |
| Claude Code + RAG-Anything = LIMITLESS | 26,287 | [链接](https://www.youtube.com/watch?v=rJCgvnXgOiU) |
| Claude Code: 100% Free. 100% Private. 100% Local. | 37,185 | [链接](https://www.youtube.com/watch?v=GHGGkIMYDxo) |
| Claude.md is RUINING Claude Code (w/ One Exception) | 10,921 | [链接](https://www.youtube.com/watch?v=V3xDTx2XwGg) |
| Google's Embedding 2 Is RAG on Steroids | 17,090 | [链接](https://www.youtube.com/watch?v=gmbW_lXXIkc) |
| Karpathy's Obsidian RAG + Claude Code = CHEAT CODE | 67,494 | [链接](https://www.youtube.com/watch?v=OSZdFnQmgRw) |
| i converted all my n8n agents to real code | 5,942 | [链接](https://www.youtube.com/watch?v=dSp4jL8R2o0) |

## 核心框架：Context Rot 对抗系统

> [!important] 最关键的 Claude Code 知识
> 上下文窗口管理是性能的决定性因素

```
0%         20-25%          200K tokens       满
|___________|_______________|_______________|
 正常工作     ← 清除阈值      "死亡区域"
              (清除上下文)    (性能暴跌)
```

**核心规则**：
1. 在 20-25% 使用率时主动清除上下文
2. 使用自定义 **Status Line** 实时显示使用率
3. 用 `/btw` 命令进行不污染上下文的侧边对话
4. 每次新任务开启新会话，不复用旧上下文

## Caveman 模式的科学依据

**发现**：极简指令 > 过度详细的 CLAUDE.md

**原理**：
- LLM 的注意力机制会稀释过长指令的权重
- 过多约束导致 Claude 在"遵循规则"上浪费 token
- 最优做法：只在必要时提供上下文，其余交给模型

**CLAUDE.md 的唯一正确用途**：
- 定义项目技术栈和范围边界
- 不超过 50 行
- 不写"始终做X"这类全局规则

## RAG 技术栈对比

| 方案 | 适用场景 | 复杂度 | 本地化 |
|------|---------|--------|--------|
| **LightRAG** | 中小型知识库 | 低 | 支持 |
| **RAG-Anything** | 多格式文档 | 中 | 支持 |
| **Karpathy Obsidian RAG** | 个人知识库 | 低 | 支持 |
| **Google Embedding 2** | 大规模语义搜索 | 高 | 不支持 |

## 9 大高效技巧

1. **Status Line**：终端显示 token 使用率 + 模型状态
2. **/btw 命令**：侧边问题，不进入主上下文
3. **Plan Mode 2.0**：先规划再执行，减少回溯
4. **Agent Loops**：循环验证直到达到标准
5. **Parallel Agents**：多个 Claude 实例并行处理子任务
6. **Surgical CLI**：每个任务只挂载需要的 CLI 工具
7. **Context Checkpointing**：关键里程碑前保存上下文摘要
8. **Adversarial Questioning**：主动问"What could go wrong?"
9. **/dream 整合**：定期整合记忆、清理过时信息

## 本地化运行栈

```
Ollama（本地 LLM 运行时）
    + Claude Code（agentic 框架）
    + LightRAG（本地向量库）
    + Obsidian（知识管理）
= 完全私有、零成本的 AI 开发环境
```

## 信息图

> [!warning] 信息图
> 生成因 Google 限速失败。重试命令：
> ```bash
> notebooklm generate infographic "Advanced Techniques: 对抗Context Rot——20-25%清除规则、状态栏监控、RAG本地化、Caveman模式科学原理" -n 5a01ed60-fafe-4dc6-bdc3-85dba3c9c581 --detail detailed --wait
> ```
