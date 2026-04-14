---
title: "运营Uplift模型"
date: 2026-04-09
tags: [项目/进行中]
status: 进行中
---

# 运营 Uplift 模型（WA 投放）

## 项目概述

**目标**：识别"发 WA 相对不发 WA 能额外带来放款"的用户（Persuadables），替代人工规则圈人
**方法**：T-Learner + LGBM，Uplift = P(放款|发WA,X) − P(放款|不发WA,X)
**优先场景**：复贷续借（P0）→ 首贷未完件（P1）→ 首贷完件（P2）

## 当前状态

> [!info] 最新进展（2026-04-03）
> 建模方案确定，等待运营提供数据，开始数据 Profiling 和特征回溯

## 关键设计决策

| 决策点 | 选择 | 原因 |
|--------|------|------|
| 算法 | T-Learner（非 X-Learner） | 入模特征更具业务解释性，风险更低 |
| 样本粒度 | 人天（person-day） | 与每天早上跑批圈人的推理场景一致 |
| 归因方式 | 末次归因 | 有已读→取最近已读；无→发送成功；无→请求发送 |
| Y定义 | T+1/T+3 放款（0/1），额外尝试金额加权 | 量化增量放款 |

## 日志追踪

```dataview
TABLE date AS 日期
FROM "日志"
WHERE contains(projects, "运营Uplift模型")
SORT date DESC
```

## 沉淀到知识库

- 方法论 → [[Uplift因果推断方法论]]
- 模型档案 → [[运营Uplift模型]]
