---
title: Claude Code 网页设计
date: 2026-04-09
tags:
  - research/youtube
  - research/claude-code
  - research/web-design
  - type/research
related:
  - "[[Chase-H-AI 频道分析]]"
  - "[[Claude Code 核心教程]]"
---

# Claude Code 网页设计

> [!note] 来源
> 本笔记整理自 [[Chase-H-AI 频道分析]] 中关于 AI 辅助网页设计的视频系列。

## 类别定位

使用 Claude Code 创建"premium"级别网站，明确反对"AI Slop"（紫色渐变、千篇一律的 AI 设计）。核心方法：**Site Teardown + 3D 动画 + 设计词汇积累**。

## 视频列表

| 视频标题 | 观看量 | URL |
|---------|--------|-----|
| The 7 Levels of Building ELITE Websites with Claude Code | 61,299 | [链接](https://www.youtube.com/watch?v=1PXFAFMgdns) |
| Claude Code Now DESTROYS Web Design with Stitch 2.0 | 74,401 | [链接](https://www.youtube.com/watch?v=qqcpiDXPCvY) |
| Claude Code + Nano Banana 2 = Insane 3D Websites | 58,093 | [链接](https://www.youtube.com/watch?v=QutvJAP06-A) |
| Claude Code + Nano Banana = Beautiful Animated Websites | 19,802 | [链接](https://www.youtube.com/watch?v=jQxHo9PC19Q) |
| I STOLE a $100K Website in 15 Minutes with Claude Code | 7,205 | [链接](https://www.youtube.com/watch?v=i-jawzwnjSA) |
| Stealing $10K Website Designs with Claude Code | 35,122 | [链接](https://www.youtube.com/watch?v=AaO6ujcx6TY) |

## 核心框架：The 7 Levels of ELITE Websites

```
Level 1 - Static HTML/CSS    → 基础页面
Level 2 - Responsive         → 移动端适配
Level 3 - Interaction        → 悬停/点击动效
Level 4 - Scroll Animation   → 滚动触发动画
Level 5 - 3D Elements        → Three.js / WebGL
Level 6 - Site Teardown      → 拆解专业网站风格
Level 7 - Custom Design Sys  → 完整品牌设计系统
```

## Site Teardown 方法论

> "偷学"是最快的进步路径

**流程**：
1. 在 [Awwwards](https://www.awwwards.com) / [Dribbble](https://dribbble.com) 找到目标网站
2. 打开 DevTools，复制关键 HTML/CSS/JS 片段
3. 将代码喂给 Claude Code："用这个风格重建我的网站"
4. 逐步迭代，积累"设计词汇"

**工具**：
- **Stitch 2.0**（Google）：UI 截图 → 代码转换
- **Nano Banana**：3D 动画快速实现库
- **Firecrawl**：自动抓取目标网站的完整代码

## 避免 AI Slop 的原则

> [!warning] AI Slop 常见特征
> - 紫色/蓝色渐变背景
> - 圆角卡片 + 白色背景
> - 过度使用 emoji 作为图标
> - 千篇一律的 Hero 区域布局

**解决方案**：
- 明确提供视觉参考（URL 或截图）
- 使用"设计食谱"：真实网站代码片段
- 要求具体的字体、颜色、间距规范
- 多轮迭代，而非单次生成

## 3D 动画实现路径

```
Nano Banana 库（入门）
    ↓ 升级
Three.js + GSAP（中级）
    ↓ 升级
Custom WebGL Shader（高级）
```

## 信息图

> [!warning] 信息图
> 生成因 Google 限速失败。重试命令：
> ```bash
> notebooklm generate infographic "Web Design with Claude Code: ELITE网站7等级、Site Teardown方法、3D动画、避免AI Slop设计原则" -n 5a01ed60-fafe-4dc6-bdc3-85dba3c9c581 --detail detailed --wait
> ```
