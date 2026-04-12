---
title: QuizFun 数据库 Schema
date: 2026-04-09
tags:
  - project/quizfun
  - type/project
  - tech/supabase
status: active
related:
  - "[[QuizFun 项目概览]]"
---

# QuizFun 数据库 Schema

Supabase PostgreSQL，实例：`yjtywhwfqsxgjwhjdfml.supabase.co`

---

## 表关系

```
quizzes
  ├── questions
  │     └── question_options
  ├── personality_results
  ├── quiz_sources
  ├── quiz_stats          (1:1)
  └── quiz_completions    (1:N)

authors → quizzes.author_id

newsletter_subscribers   (独立)
```

---

## quizzes

测验主表。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | uuid | 主键 |
| `slug` | text | URL 标识，唯一 |
| `type` | enum | `trivia` \| `personality` |
| `category` | text | 分类名 |
| `category_icon` | text | 分类 emoji |
| `title` | text | 标题 |
| `description` | text | 描述 |
| `cover_image` | text | 封面图 URL |
| `intro_article` | text | 介绍文章（Markdown）|
| `difficulty` | enum | `easy` \| `medium` \| `hard` |
| `estimated_minutes` | int | 预计用时 |
| `play_count` | int | 播放次数 |
| `share_count` | int | 分享次数 |
| `tags` | text[] | 标签数组 |
| `locale` | text | 语言代码 |
| `status` | enum | `draft` \| `review` \| `published` |
| `author_id` | uuid | → authors |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

## questions

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | uuid | 主键 |
| `quiz_id` | uuid | → quizzes |
| `sort_order` | int | 题目顺序 |
| `text` | text | 题目文本 |
| `image_url` | text | 配图（可选）|
| `correct_answer_id` | uuid | → question_options（trivia 用）|
| `explanation` | text | 答案解析 |
| `fun_fact` | text | 趣味知识 |
| `source_url` | text | 来源链接 |

---

## question_options

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | uuid | 主键 |
| `question_id` | uuid | → questions |
| `option_key` | text | `a` \| `b` \| `c` \| `d` \| `e` |
| `sort_order` | int | 选项顺序 |
| `text` | text | 选项文本 |
| `image_url` | text | 图片选项（可选）|
| `personality_tag` | text | 人格标签（personality 类型用）|

---

## personality_results

人格测试结果类型定义，每个 `personality_tag` 对应一条。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | uuid | 主键 |
| `quiz_id` | uuid | → quizzes |
| `tag` | text | 标签名（与选项 personality_tag 对应）|
| `title` | text | 结果标题 |
| `description` | text | 结果描述 |
| `image_url` | text | 结果配图 |
| `emoji` | text | 结果 emoji |

---

## quiz_stats

每个测验的汇总统计，与 `quizzes` 1:1。

| 字段 | 类型 | 说明 |
|------|------|------|
| `quiz_id` | uuid | 主键，→ quizzes |
| `play_count` | int | 总播放次数 |
| `share_count` | int | 总分享次数 |
| `avg_score` | float | 平均分（trivia 用）|
| `completion_rate` | float | 完成率 |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

## quiz_completions

每次用户完成测验的记录。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | uuid | 主键 |
| `quiz_id` | uuid | → quizzes |
| `score` | int | 得分 |
| `total_questions` | int | 总题数 |
| `time_taken_seconds` | int | 用时（秒）|
| `locale` | text | 用户语言 |
| `created_at` | timestamptz | |

---

## SQL Functions

```sql
-- 原子递增播放数
increment_play_count(quiz_id uuid)

-- 原子递增分享数
increment_share_count(quiz_id uuid)
```

通过 Supabase RPC 调用，避免并发写入竞争。

---

## 迁移文件

位置：`supabase/migrations/`，通过 Supabase CLI 管理。

---

## 关联笔记

- [[QuizFun 项目概览]]
- [[QuizFun 架构详解]]
