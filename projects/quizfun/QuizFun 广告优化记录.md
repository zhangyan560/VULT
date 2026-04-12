---
title: QuizFun 广告优化记录
date: 2026-04-09
tags:
  - project/quizfun
  - type/project
  - topic/monetization
status: active
related:
  - "[[QuizFun 项目概览]]"
---

# QuizFun 广告优化记录

## 广告位清单

| 广告位 ID | 位置 | 出现时机 |
|----------|------|----------|
| `quizDetail` | 题目页顶部 Banner | 每道题 |
| `quizExplanation` | 题目页答案下方 Rectangle | 每道题 |
| `quizResult` | 结果页顶部 | 结束后 |
| `articleInline` | 结果页相关测验上方 | 结束后 |
| `homeBanner` | 首页 Banner | 首页 |
| `categoryBanner` | 分类页 Banner | 分类页 |

---

## 阶段配置

通过 `NEXT_PUBLIC_AD_PHASE` 环境变量控制。

### warmup（当前）

> [!note] 适用于 AdSense 账户审核期
> 保守开启，降低违规风险。

- 开启：`quizDetail` + `quizResult`
- 每次测验（10 题）曝光：**11 次**

### growth

- 新增：`quizExplanation` + `articleInline`
- 每次测验曝光：**17 次**

### mature

- 全部广告位开启
- 每次测验曝光：**23 次**

---

## React Strict Mode 兼容修复

**问题：** React 18 Strict Mode 在开发环境下双重挂载组件，导致 AdSense `adsbygoogle.push()` 被调用两次，报错 `adsbygoogle already pushed`。

**解决方案（`AdUnit.tsx`）：**

```tsx
// 检查是否已初始化，避免重复 push
const adEl = adRef.current;
if (adEl?.getAttribute('data-adsbygoogle-status')) return;

// 使用 useId() 生成唯一 key，防止复用同一 DOM 节点
const id = useId();
```

**清理函数：** 组件卸载时移除 ad slot，防止重新挂载时复用旧状态。

---

## 收入预测

基于新架构（逐题翻页）：

| DAU | 月曝光量 | CPM $5 | CPM $12 |
|-----|---------|--------|---------|
| 1,000 | 138 万 | $6,900 | $16,560 |
| 10,000 | 1,380 万 | $69,000 | $165,600 |
| 100,000 | 1.38 亿 | $690,000 | $1,656,000 |

> [!warning] 注意
> 以上为理论峰值，实际 CPM 受地区、内容类别、广告竞争度影响，亚洲地区 CPM 通常低于北美。

---

## 关联笔记

- [[QuizFun 项目概览]]
- [[QuizFun Phase 2 规划]]
