---
title: QuizFun 项目概览
date: 2026-04-09
tags:
  - project/quizfun
  - type/project
  - tech/nextjs
  - tech/supabase
status: active
aliases:
  - quizfun
  - QuizFun
source: /Users/zhangyan/Projects/quizfun
---

# QuizFun 项目概览

QuizFun 是一个 AI 驱动的在线测验平台，通过 Google AdSense 广告变现，支持 8 种语言，面向全球用户提供人格测试、知识竞赛等 21+ 类别的测验内容。

> [!important] 项目路径
> 本地代码：`/Users/zhangyan/Projects/quizfun`
> 线上域名：`quizfunforyou.com`
> 部署平台：Vercel + Supabase

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 框架 | Next.js 16.2 + React 19 + TypeScript 5 |
| 样式 | Tailwind CSS 4 |
| 数据库 | Supabase (PostgreSQL) |
| AI 分析 | GLM (智谱 glm-4-flash) / MiniMax M2.7 |
| 图片生成 | SiliconFlow (Kolors / Qwen-Image) |
| 部署 | Vercel (ISR + Edge CDN) |
| 测试 | Playwright 1.58 |
| 分析 | Google Analytics 4 + GTM |
| 广告 | Google AdSense |

---

## 目录结构

```
src/
├── app/[locale]/          # 多语言路由（8 种语言）
│   ├── quiz/[slug]/
│   │   ├── q/[num]/       # ✅ 新架构：逐题作答
│   │   ├── play/          # ⚠️ 旧架构（已废弃）
│   │   └── result/        # 结果页
│   ├── category/[name]/
│   └── admin/             # 后台管理
├── api/                   # API 路由
├── components/            # UI 组件
├── lib/                   # 工具函数
├── data/                  # 静态题库数据
├── types/                 # TypeScript 类型
└── context/               # React Context
```

详见 [[QuizFun 架构详解]]。

---

## 核心功能

### 测验作答流程（新架构）

新架构采用**逐题翻页**模式（`/quiz/[slug]/q/[num]`），每道题一个页面：

```
开始测验 → Q1 → Q2 → ... → Q10 → 结果页
```

- 进度保存在 `localStorage`（24 小时有效）
- 私人浏览降级为 URL 参数
- 页面预取（Next.js prefetch），切题无感

> [!tip] 为什么改架构
> 旧架构（SPA 单页）每次测验仅 1–3 次广告曝光；新架构每次测验可产生 **11–23 次广告曝光**，广告收入提升最高 23 倍。

### 测验类型

| 类型 | 计分方式 | 结果呈现 |
|------|----------|----------|
| Trivia（知识竞赛）| 正确题数 / 总题数 | 分数 + 百分比 |
| Personality（人格测试）| 人格标签统计 | 类型描述 + emoji |

### AI 分析

结果页实时流式输出 AI 个性化分析，优先使用 GLM，降级到 MiniMax。结果按 `quiz_slug + 答案组合` 缓存 24 小时（内存缓存）。

---

## 广告变现

广告分三个成熟阶段渐进开启：

| 阶段 | 开启位置 | 每次测验曝光数 |
|------|----------|---------------|
| warmup | quizDetail + quizResult | 11 |
| growth | + quizExplanation + articleInline | 17 |
| mature | + 所有位置 | 23 |

> [!example] 收入预测（mature 阶段）
> 10,000 DAU → 每月 1,380 万广告曝光
> - CPM $5 → 约 $69,000/月
> - CPM $12 → 约 $165,600/月

广告位由 `NEXT_PUBLIC_AD_PHASE` 环境变量控制，当前：`warmup`。

---

## 数据库（Supabase）

主要表结构见 [[QuizFun 数据库 Schema]]。

核心表：

- `quizzes` — 题目元数据（slug、类型、分类、多语言）
- `questions` + `question_options` — 题目与选项
- `personality_results` — 人格测试结果类型
- `quiz_stats` — 播放数、分享数、平均分
- `quiz_completions` — 用户完成记录

数据来源优先级：Supabase（生产）→ 静态 TS 文件（兜底）。

---

## 多语言

支持 8 种语言，通过 URL 路径路由：

| 代码 | 语言 |
|------|------|
| `en` | English（默认）|
| `zh` | 中文 |
| `es` | Español |
| `fr` | Français |
| `de` | Deutsch |
| `pt` | Português |
| `ja` | 日本語 |
| `ko` | 한국어 |

Middleware 自动重定向无效 locale → `/en`。

---

## 渲染策略

| 路由 | 策略 | 缓存 |
|------|------|------|
| 首页 `[locale]` | SSG + ISR | 1 小时 |
| 测验页 `quiz/[slug]` | SSG + ISR | 1 小时 |
| 题目页 `q/[num]` | SSG（Top 20）+ 按需 | 1 小时 |
| 结果页 `result` | SSR | 无 |
| API 路由 | SSR | 无 |

---

## 开发命令

```bash
npm run dev       # 开发服务器 localhost:3000
npm run build     # 生产构建
npm run lint      # ESLint 检查
./quick-test.sh   # 5 分钟冒烟测试
./run-automated-tests.sh  # 完整 E2E（10 个用例）
```

---

## 当前状态

> [!success] Phase 1 已完成（2026-03-29）
> - 逐题翻页架构上线
> - LocalStorage 进度保存
> - Pinterest 分享按钮
> - AdSense React Strict Mode 修复
> - 10/10 自动化测试通过

> [!warning] Phase 2 进行中
> - Badge 系统（8 种徽章 + 解锁动画）
> - 用户统计展示
> - 手动浏览器测试（15 个用例）
> - Lighthouse 性能得分 > 90

---

## 关联笔记

- [[QuizFun 架构详解]]
- [[QuizFun 数据库 Schema]]
- [[QuizFun 广告优化记录]]
- [[QuizFun Phase 2 规划]]
