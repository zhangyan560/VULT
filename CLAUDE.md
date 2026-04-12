# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Obsidian Vault 规范

## 三区结构

```
VULT/
├── inbox/           ← raw zone：随手 dump，/digest 消化整理到 wiki
├── wiki/            ← wiki zone：LLM 主导维护的知识库
│   ├── 产品开发/
│   ├── 商业研究/
│   ├── 效率工具/
│   ├── 网站运营/
│   └── research/
├── output/          ← output zone：报告、导出（按 YYYY-MM-DD-主题.md 命名）
├── daily-notes/     ← 个人区（只读/limited write）
├── projects/        ← 个人区（只读/limited write）
└── _master-index.md ← 全局导航地图（≤80 行，路径+描述，不放内容）
```

每个 wiki domain 的结构：
```
wiki/domain/
├── _index.md   ← domain 索引（文件列表+一句话描述，必须维护）
└── topic/
    └── *.md
```

## 索引维护规则（强制）

每次在 wiki zone 创建或修改文件后，必须：
1. 更新该 domain 的 `_index.md`
2. 新 topic 或新 domain 时，同时更新 `_master-index.md`

## 格式规范

**文件命名**：中/英文与标题一致，不用特殊字符，多词英文用空格（wikilink 友好）

**Frontmatter**（每篇必须）：
```yaml
title: 与文件名一致
date: YYYY-MM-DD   # 字符串，不用 ISO 完整格式
tags: [topic/subtopic]  # 小写，统一在 frontmatter 管理
status: draft/active/archived  # 可选
```

**标题**：H1 唯一（与 title 一致），H2 主章节，H3 子章节，不跳级

**链接**：vault 内用 `[[wikilink]]`，支持 `[[名称|显示]]`、`[[名称#章节]]`；外部用 `[文字](url)`；不创建空占位笔记

**Callout**：仅视觉强调时用——`[!note]` / `[!important]` / `[!warning]` / `[!tip]` / `[!example]`；标题写具体，可折叠用 `[!type]-`

**图片**：放 `assets/`，引用格式 `![[image.png|600]]`

## AI 写入权限范围（Zero-Trust）

**可直接写入**：`wiki/`（含所有子域）、`output/`、`assets/`、`_master-index.md`、`wiki/*/_index.md`

**需用户确认**：`projects/`（修改已有笔记）、`daily-notes/`（/today skill 除外）

**禁止**：
- 写入 `inbox/`（只读取归档，不写入碎片）
- 删除笔记（改用 `status: archived`）
- 访问 `.obsidian/` 目录
- 将 Vault 内容发送到任何外部服务

长任务续接：进度记录到 `projects/进行中/{任务名}-progress.md`，/compact 前更新，新会话读取续接。
