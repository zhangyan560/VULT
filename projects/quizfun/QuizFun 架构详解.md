---
title: QuizFun 架构详解
date: 2026-04-09
tags:
  - project/quizfun
  - type/project
  - tech/nextjs
status: active
related:
  - "[[QuizFun 项目概览]]"
---

# QuizFun 架构详解

## 双架构并存

QuizFun 当前维护新旧两套测验作答架构，旧架构保留兼容性，新架构为主要路径。

| 维度 | 旧架构（legacy） | 新架构（primary）|
|------|-----------------|-----------------|
| 路由 | `/quiz/[slug]/play` | `/quiz/[slug]/q/[num]` |
| 页面数 | 1 页（SPA） | N 题 + 1 结果页 |
| 广告曝光 | 1–3 次 | 11–23 次 |
| 进度保存 | 无 | LocalStorage + URL 降级 |
| 状态 | ⚠️ 废弃中 | ✅ 主力 |

---

## 新架构数据流

```
静态题库 (src/data/*.ts)
        ↓
Supabase PostgreSQL（生产优先）
        ↓
dbFetchQuizBySlug()         ← 2s 超时保护
        ↓
Server Component (page.tsx) ← 参数校验 + 非法跳转
        ↓
Client Component (QuizQuestionPage.tsx)
        ↓
LocalStorage quiz_progress_{quizId}
        ↓
结果计算 → Result Page
        ↓
AI 分析流式输出（GLM → MiniMax 降级）
```

---

## 进度持久化

**LocalStorage Key：** `quiz_progress_{quizId}`

存储内容：
```json
{
  "answers": { "q1": "b", "q2": "a" },
  "currentIndex": 3,
  "personalityCounts": { "introvert": 2, "extrovert": 1 },
  "expiresAt": 1234567890
}
```

- 有效期：24 小时
- 私人浏览降级：答案编码到 URL query string
- 结果页加载后清除进度

---

## 页面预取策略

每道题页面预取下一题，实现无感切换：

```tsx
// QuizQuestionPage.tsx
<Link href={`/quiz/${slug}/q/${currentNum + 1}`} prefetch>
  下一题
</Link>
```

Top 20 热门测验在构建时 SSG 预渲染所有题目页，其余按需生成并缓存。

---

## API 路由

### `/api/quiz-analysis`

AI 个性化分析，流式返回：

- 主力：GLM（智谱 glm-4-flash-250414）
- 降级：MiniMax M2.7
- 缓存：内存缓存，按 `{slug}_{answerHash}` 缓存 24 小时

### `/api/quiz-event`

用户行为埋点：

| 事件 | 触发时机 |
|------|----------|
| `quiz_start` | 进入 Q1 |
| `question_answer` | 选择选项 |
| `quiz_complete` | 进入结果页 |

### `/api/daily-challenge`

按日期种子轮换每日推荐测验，无随机性，每天固定。

---

## 渲染与缓存

**HTTP 缓存头（所有页面路由）：**
```
Cache-Control: public, s-maxage=3600, stale-while-revalidate=7200
```

- 1 小时内直接命中 CDN 缓存
- 1–2 小时内后台静默重新生成
- Vercel Edge Network 全球分发

**Supabase 超时保护：**
所有数据库查询包裹 2 秒超时，超时后降级使用静态 TS 题库文件，保证服务不中断。

---

## 组件职责

| 组件 | 职责 |
|------|------|
| `QuizQuestionPage.tsx` | 单题 UI，进度条，选项交互 |
| `QuizResultPage.tsx` | 得分展示，人格结果，分享按钮 |
| `AdUnit.tsx` | 广告槽渲染，React Strict Mode 兼容 |
| `ShareButtons.tsx` | FB / Twitter / WhatsApp / Pinterest |
| `FeedbackWidget.tsx` | 用户反馈表单 |
| `Header.tsx` | 导航 + 语言切换 |
| `Analytics.tsx` | GA4 + GTM 初始化 |

---

## 关联笔记

- [[QuizFun 项目概览]]
- [[QuizFun 数据库 Schema]]
