---
title: Day 6 - 可配置的CLI助手
date: 2026-05-26
tags: [ai/agent, ai/application, learning/day6, cli]
status: draft
---

# Day 6 - 可配置的CLI助手

## 今日任务

给命令行助手增加 system prompt、模型名、温度等配置，让它从“能用”变成“可调”。

## 学习资料

- [OpenAI Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [[AI Agent工程师3个月学习计划]]

## 1小时安排

| 时间 | 任务 | 完成情况 |
|------|------|----------|
| 10 分钟 | 设计 CLI 助手角色和默认 system prompt |  |
| 20 分钟 | 增加模型、温度、system prompt 配置 |  |
| 20 分钟 | 测试不同参数对回答的影响 |  |
| 10 分钟 | 总结可配置项设计原则 |  |

## 预计产出

- 可配置版本的 `cli_assistant.py`
- 一组参数对比结果
- 一段关于配置项设计的总结

## 默认配置

```yaml
model:
temperature:
system_prompt:
```

## System Prompt 草案

```text

```

## 参数对比记录

| 参数组合 | 测试问题 | 回答特点 |
|----------|----------|----------|
|  |  |  |
|  |  |  |
|  |  |  |

## 配置项设计原则

- 

## 今日收获

- 

## 今日疑问

- 

## 明日准备

明天目标：完成第 1 周复盘，整理 API、prompt、schema 的关系。

- [ ] 回顾 Day 1 到 Day 6 的笔记
- [ ] 整理本周代码产出
- [ ] 写出下周工具调用学习的准备问题

