---
title: Claude Code - 上下文窗口与Token原理
date: 2026-04-09
tags:
  - research/claude-code
  - research/token-optimization
  - type/research
status: active
related:
  - "[[02-提示词压缩技巧]]"
  - "[[03-上下文窗口管理]]"
  - "[[效率工具/Claude Code省Token研究/_index]]"
---

# Claude Code - 上下文窗口与Token原理

> [!important] 理解原理是一切优化的基础
> 不理解 Claude 的无状态机制，所有省 token 技巧都只是表面操作。

## 核心机制：无状态复利计费

Claude 采用**无状态（Stateless）**工作模式——它在不同消息之间没有任何记忆。

**每次发送新消息时，Claude 都会从头重读整个对话历史**，包括：
- 所有历史消息（用户 + 模型）
- 系统提示词
- `CLAUDE.md` 指令文件
- 已连接的 MCP 服务器工具定义
- 已加载的文件内容
- 已定义的技能（Skills）

### Token 消耗增长曲线

```
第  1 条消息：   500 token（正常）
第 10 条消息：  3,000 token（累计历史）
第 30 条消息： 15,000 token（指数级飙升）
第 N 条消息：  ~98.5% 的 token 都在重读旧历史
```

这是**复利增长**，而非线性增长。这也是为什么长会话成本会失控。

## 五大 Token 消耗来源

| 来源 | 典型消耗量 | 说明 |
|------|-----------|------|
| 对话历史重读 | 占总量 ~98.5% | 长会话的主要杀手 |
| MCP 服务器 | ~18,000 token/条/服务器 | 每个服务器每条消息都加载工具定义 |
| 大文件读取 | 最高 25k token/文件 | Claude 默认文件读取上限 |
| 终端输出 | 最高 30,000 字符 | 大型构建日志的常见陷阱 |
| 子代理启动 | 普通会话的 7–10 倍 | 每个子代理都加载完整上下文 |
| 思考模式 | 额外 ++ | `think`/`think harder` 关键词触发 |

## 「中间信息丢失」现象

当上下文窗口塞满时，模型会优先关注**开头**（首要效应）和**结尾**（近因效应），中间的内容往往被忽略或降权。

**后果：**
- 重复之前已讨论的内容
- 遗忘重要的约束条件
- 输出质量明显下降

> [!warning] 上下文满 ≠ 信息全部被处理
> 满的上下文窗口反而会让模型变"笨"，过多无关 token 就是噪声。

## 缓存机制（Prompt Cache）

Claude 有自动缓存机制，但有关键限制：
- **缓存有效期：约 5 分钟**
- 系统提示词、`CLAUDE.md`、项目指令可被缓存（计费更低）
- 离开电脑超过 5 分钟再回来提问 = 缓存失效 = 全额重新处理

**实践：** 长时间离开前，先执行 `/compact` 或 `/clear`，不要让缓存在你不在时自然失效。

## settings.json 关键配置

`~/.claude/settings.json`（或 `main.claude` 文件夹中）：

```json
{
  "autoCompactPercentageOverride": 75,
  "cleanupPeriodDays": 365,
  "terminalOutputCharLimit": 150000
}
```

| 字段 | 默认值 | 建议值 | 说明 |
|------|--------|--------|------|
| `autoCompactPercentageOverride` | 95% | 70–75% | 提前触发自动压缩 |
| `cleanupPeriodDays` | 30天 | 365天 | 保留更长会话历史 |
| `terminalOutputCharLimit` | 30,000 | 150,000 | 支持读取大型日志 |

## 关联笔记

- [[02-提示词压缩技巧]] — 知道原理后，如何写更省 token 的提示词
- [[03-上下文窗口管理]] — /clear 和 /compact 的具体用法
- [[04-工具调用与MCP优化]] — MCP 服务器的 token 成本控制
- [[05-工作流设计与避坑]] — 系统化省 token 的工作流设计
