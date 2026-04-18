---
title: "征信-APP联动特征"
tags: [特征体系/征信联动, AFPI, CBI, APP]
date: 2026-04-09
---

# 征信-APP联动特征

## 核心思路

将App安装状态与征信借款记录交叉，捕捉"用户装了某机构App但没在该机构借款"、"借了款但卸载了App"等行为信号。这类特征将**行为数据（App安装）**和**信贷数据（征信记录）**进行关联，产生远超单一数据源的风险区分力。

---

## 交叉矩阵

| App安装 | 有该机构借款 | 曾经逾期 | 是否结清 | 衍生指标 |
|---------|-----------|---------|---------|---------|
| 已安装 | 是 | 是 | 是/否 | 逾期金额/天数/平均额度/借款次数/机构数/时间间隔 |
| 已安装 | 否 | / | / | 安装App个数（探索性安装行为） |
| 未安装 | 是 | 是/否 | / | 逾期金额/天数/额度/次数/机构数（卸载行为信号） |

**业务含义解读**：
- **已安装+有借款+已逾期**：用户在该平台有不良记录，App仍保留（可能还在借贷循环中）
- **已安装+无借款**：探索性安装，可能在多平台比较利率/额度（多头信号前兆）
- **未安装+有借款**：曾借款后卸载App，可能想切断与该平台的联系（逃避催收信号）

---

## AFPI-APP联动特征（260个）

### 命名模式

```
AFPI_APP_DATA_FEATURE___installStatus{Status}___w{Window}___{Metric}___{Stat}
```

### 维度组合

| 维度 | 可选值 | 说明 |
|------|-------|------|
| installStatus | InstallBefore | 借款前安装 |
| | InstallAfter180d | 借款后180天安装 |
| | InstallIn180d | 借款后180天内安装 |
| | NotInstalled | 未安装 |
| Window | w3m / w6m / w12m / w24m / wall | 时间窗口 |
| Metric | tLoanAmount | 借款金额 |
| | tRepaymentRatio | 还款比率 |
| | tInstallmentShouldPay | 应还分期金额 |
| | creditDayPastDue | 逾期天数 |
| | creditFacPerfLongestArrearsDays | 最长逾期天数 |
| | tRepaidAmount | 已还金额 |
| | tLoanTerm | 借款期限 |
| | tIncome | 收入 |
| | creditOutstanding | 未结清金额 |
| | tRemainTerm | 剩余期限 |
| | tDpd | 逾期天数(DPD) |
| Stat | mean / sum / max / min / std / cv / count | 统计量 |

### 特征示例

```
AFPI_APP_DATA_FEATURE___installStatusInstallBefore___w6m___tLoanAmount___mean
-- 借款前已安装App的机构，近6个月借款金额的均值

AFPI_APP_DATA_FEATURE___installStatusNotInstalled___wall___creditDayPastDue___max
-- 未安装App的机构，历史最大逾期天数

AFPI_APP_DATA_FEATURE___installStatusInstallAfter180d___w12m___tRepaymentRatio___mean
-- 借款后180天才安装App的机构，近12个月还款比率均值
```

---

## CBI-APP联动特征（594个）

### 命名模式

```
CBI_APP_DATA_FEATURE___installStatus{Status}___w{Window}___{Metric}___{Stat}
```

### 维度组合

CBI特有的Metric（在AFPI基础上增加）：

| Metric | 说明 |
|--------|------|
| creditLiqCurrentMonth | 当月流动性 |
| creditInterestRate | 利率 |
| tInterestPerYear | 年化利息 |
| creditProjectValue | 项目价值 |
| creditPenalty | 罚款金额 |
| creditArrearsOnInterest | 利息欠款 |
| tOrderDateDiff | 订单日期差 |
| creditFacPerfMaxArrearsAmount | 最大欠款金额 |

CBI特征数量更多（594 vs 260），因为CBI央行征信包含更详细的信贷记录（利率、罚款、抵押等维度），维度组合更丰富。

### installStatus维度说明

| 状态 | 业务含义 | 风险信号 |
|------|---------|---------|
| InstallBefore | 借款前已安装App | 正常使用路径 |
| InstallIn180d | 借款后180天内安装 | 可能因催收提醒而安装 |
| InstallAfter180d | 借款后180天才安装 | 长期后才关注（可能重新借款） |
| NotInstalled | 有借款记录但未安装App | 卸载信号（逃避催收/已结清） |

---

## 特征开发要点

### 数据关联逻辑

1. 从App安装列表中提取用户已安装的App包名
2. 建立App包名到金融机构的映射表（需维护）
3. 从CBI/AFPI征信数据中提取用户在各机构的借款记录
4. 按installStatus维度交叉，计算各Metric的统计量

### 时间窗口定义

- `w3m`：最近3个月的借款记录
- `w6m`：最近6个月
- `w12m`：最近12个月
- `w24m`：最近24个月
- `wall`：全部历史记录

### 特征总量

| 数据源 | 特征数 | 说明 |
|--------|-------|------|
| AFPI-APP | 260 | 金融科技协会征信 x App安装 |
| CBI-APP | 594 | 央行征信 x App安装 |
| **合计** | **854** | |

---

## 关联文档

- [[图网络特征方法论]] - App图网络特征方法论
- [[借新还旧特征]] - 借新还旧特征体系
- [[埋点行为特征]] - 埋点行为特征体系
