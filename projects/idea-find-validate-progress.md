---
title: idea-find-validate 调研进度
date: 2026-04-14
status: in-progress
tags: [projects/startup-validation]
---

# 创业想法挖掘 — 调研进度

> **目标**：轻量级 Android/Web，用户愿意付费 + 广告变现空间
> **偏好**：C 端订阅制，不做重内容运营，不进极度饱和赛道
> **技能**：Python、量化/风控算法、印尼现金贷行业、网球、滑雪

---

## Phase 0B：用户偏好

| 维度 | 选择 |
|------|------|
| Unfair advantage | Python 全栈、量化回测、印尼 fintech 风控内部视角、网球球员（教练需求）|
| 商业模式 | C 端 + 订阅制 |
| 排除方向 | 重内容运营、极度饱和赛道 |

---

## 机会卡片汇总（Reddit 实数据驱动）

### 🟢 机会 A：无代码回测工具（强信号）

**痛点**：散户有交易想法但无法验证，TradingView 太贵/需学 Pine Script，QuantConnect 太复杂

**Reddit 证据**：
- r/algotrading — [78赞] *"No code backtesting"*：10年机构量化研究员确认市场空白
  - 原话：*"most backtesting tools are either too simplistic (TradingView) or too complicated (NinjaTrader/QuantConnect)"*
- r/stocks — [93赞] *"The gap between retail investors and tools for institutional analysis is still absurd in 2026"*
- r/algotrading "What is worth paying for" — 交易者每月主动花 $100-200 购买数据/工具（Alpaca $100/月、tick data £160/年）

**付费意愿**：高（散户本身就在买工具）
**竞品弱点**：TradingView 需学专有语言；QuantConnect 门槛高；没有中间地带
**你的 unfair advantage**：★★★★★（Python + 量化背景，技术零成本）
**实现复杂度**：中（需要行情数据接入 + 策略引擎 + 可视化）

**待深挖**：
- [ ] 竞品分析：TradeStation / Streak / Composer 的差评
- [ ] 目标用户：海外散户（英文）还是国内（A股/港股）？

---

### 🟡 机会 B：订阅费追踪（中等信号，竞争存在）

**痛点**：用户不知道每月实际花了多少订阅费，忘记的订阅悄悄扣款

**Reddit 证据**：
- r/povertyfinance — [5,977赞] *"Checked my small monthly expenses and found $2,040 I didn't know I was spending"*
  - 原话：*"went through 6 months of bank statements and felt physically sick"*
- r/iosapps — [90赞] 独立开发者发布订阅追踪 App，顶评：*"The funniest part of your app would be that it works with a subscription"*（竞争已有人在做）
- r/iosapps — [97赞] 生命周期授权被撤销帖：用户强烈偏好**一次性买断**而非订阅

**关键发现**：
- 市场已有 Bobby、SubTrack、Subio（$14.99 Lifetime 免费活动）等竞品
- 用户痛点真实，但解决方案已存在
- **差异化机会**：用户偏好买断制 + 无需银行授权 + 极简 UI（类 Apple Card 风格）
- 独立开发者做的 Poketto（Apple Card 风格）得到正向反馈

**付费意愿**：中（偏好一次性买断，订阅模式有阻力）
**你的 unfair advantage**：★★☆☆☆（无明显技术壁垒）

**待深挖**：
- [ ] Bobby/SubTrack 的 Google Play 差评（用 market-insights-pro 爬取）
- [ ] 确认是否值得和现有免费竞品竞争

---

### 🔵 其他候选方向（待调研）

| # | 方向 | 信号强度 | 备注 |
|---|------|---------|------|
| C | 减烟追踪（非戒烟定位）| 🟡 中 | 有需求但 Reddit 上无明确"要 App"的信号 |
| D | 印尼信用教育工具 | 🟡 中 | 无 Reddit 证据，依赖行业内部知识 |
| E | 照片清理习惯 App | 🟡 中 | r/androidapps 有正向案例（柏林开发者），但竞品已存在 |
| F | FIRE 退休计算器 | 🟡 中 | 社区活跃但搜索结果未找到工具抱怨 |
| G | 网球训练日志 | 🟡 低中 | r/tennis 主要是专业球员讨论，业余追踪需求未验证 |

---

## 下一步（Phase 1 准备）

### 机会 A 回测工具 — 待决策
- 是做海外散户（英文，对标 TradingView 用户）还是国内散户（中文，A股/港股）？
- 需要跑竞品分析：Composer、Streak、Dumb Money 的用户差评

### 机会 B 订阅追踪 — 待决策
- 跑 Bobby / SubTrack Google Play 差评分析（用 market-insights-pro）
- 确认差异化角度是否成立（买断制 + 极简 + 无银行授权）

### 继续 Phase 0 挖掘
- 搜索 5-10 个新方向（待下次会话）
- 可选：用 /youtube-research-pipeline 搜索量化工具相关 YouTube 评论

---

## 会话记录

**2026-04-13**：完成 Phase 0B 偏好问卷、生成 8 张机会卡片、Reddit 实数据验证 6 个方向
**2026-04-14**：搜集订阅追踪竞品数据、回测工具信号数据，待续
