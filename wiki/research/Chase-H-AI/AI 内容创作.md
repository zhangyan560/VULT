---
title: AI 内容创作
date: 2026-04-09
tags:
  - research/youtube
  - research/ai
  - research/content-creation
  - type/research
related:
  - "[[Chase-H-AI 频道分析]]"
  - "[[Claude Code 工具集成]]"
---

# AI 内容创作

![[AI内容创作-infographic.png|600]]


> [!note] 来源
> 本笔记整理自 [[Chase-H-AI 频道分析]] 中关于 AI 辅助内容生产的视频系列。

## 类别定位

利用 Claude Code 自动化内容生产全流程——从单个长视频到跨平台分发的"内容级联"系统。

## 视频列表

| 视频标题 | 观看量 | URL |
|---------|--------|-----|
| These Claude Code Automations Got Me 10M Views in 1 Month | 11,888 | [链接](https://www.youtube.com/watch?v=7q_rbT1a9dE) |
| How to make ELITE AI Videos in 2026 | 3,326 | [链接](https://www.youtube.com/watch?v=BlOm87GiShg) |
| AI Influencers are Lying to You | 63,875 | [链接](https://www.youtube.com/watch?v=WHtyjjDnTfM) |
| Building AI Influencers Has Changed (Full Tutorial) | 5,039 | [链接](https://www.youtube.com/watch?v=ao7-rtF18Eo) |
| how to get the most out of the best AI video model EVER | 3,176 | [链接](https://www.youtube.com/watch?v=iZn61BARgsI) |
| Claude Code + NotebookLM + Obsidian = GOD MODE | 65,731 | [链接](https://www.youtube.com/watch?v=kU3qYQ7ACMA) |

## 核心框架：Content Cascade 系统

```
长视频（YouTube）
     ↓ Claude Code 自动处理
┌────────────────────────────────┐
│  转录 → 提取关键点              │
│  生成短视频脚本（TikTok/Reels） │
│  生成博客文章                   │
│  生成推特/X 线程                │
│  生成 LinkedIn 文章             │
│  生成 Newsletter 邮件           │
└────────────────────────────────┘
     ↓ 一键多平台发布
10M+ Views / 月
```

## AI 视频制作工作流

**工具栈**：
- **Kling / Runway**：AI 视频生成
- **ElevenLabs**：声音克隆
- **Heygen**：AI 头像视频
- **CapCut**：自动剪辑 + 字幕

**关键技巧**：
- 专业电影语言指令：景别、运动、光线、情绪
- 一致性维护：同一个 AI 形象跨视频保持一致
- 脚本优先：先写好脚本，再生成画面

## AI Influencer 搭建

> [!warning] 诚实披露
> Chase 明确指出大多数"AI Influencer"频道都是虚假的，但技术本身是合法的。

**合法使用场景**：
- 品牌吉祥物
- 教育内容代言人
- 需要保护隐私的内容创作者

**工具**：Heygen + ElevenLabs + 自定义角色设定

## 研究工作流（NotebookLM + Obsidian）

```
收集 YouTube / 文档 / 网页
     ↓
notebooklm → 深度分析 + 音频摘要
     ↓
Claude Code 提取关键洞察
     ↓
写入 Obsidian Vault（持久记忆）
     ↓
生成内容脚本 → 多平台发布
```

## 信息图

> [!warning] 信息图
> 生成因 Google 限速失败。重试命令：
> ```bash
> notebooklm generate infographic "Content Creation with AI: Content Cascade系统、AI视频制作工作流、多平台内容分发自动化" -n 5a01ed60-fafe-4dc6-bdc3-85dba3c9c581 --detail detailed --wait
> ```
