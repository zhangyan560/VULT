---
title: "评级版本迭代SOP"
date: 2026-04-09
tags: [方法论/建模, SOP]
company: EasyCash
aliases: [模型迭代SOP, 子分迭代SOP]
---

# 子分模型迭代 SOP (V14+)

## 一、目录结构规范

```
yanzhang1_data/V{版本号}开发/
├── {模型名}/
│   ├── {模型名}.ipynb                   # 主开发notebook (9-section结构)
│   ├── models/
│   │   ├── v{版本号}_model_{缩写}/             # 全量特征版
│   │   ├── v{版本号}_model_{缩写}_sel/         # 筛选特征版
│   │   └── v{版本号}_model_{缩写}_stable/      # 稳定特征版
│   ├── stability_analysis/                     # 稳定性分析产出
│   └── data/                                   # 模型专用数据 (标签等)
├── 模型上线部署/
├── 模型监控部署/
└── 评级版本迭代代码管理SOP.md
```

所有模型（包括前置C卡）均采用统一的目录和命名格式，不再有特例。

### Notebook 标准结构 (9个Section)

每个子分模型的 notebook 统一采用以下 9-section 结构：

| Section | 标题 | 内容 | 标准化程度 |
|---------|------|------|-----------|
| 1 | 样本和标签加载 | imports + 工具库 | 全部统一 |
| 2 | 样本定义 | df_master + df_sample_type + 额外数据 | 部分统一 + 模型特有 |
| 3 | Y定义 | delq_data + 模型特有标签处理 | 部分统一 + 模型特有 |
| 4 | 训练样本定义 | train/valid/OOT 样本拆分 | 模型特有 |
| 5 | 特征选取 | all_vars / 特征子集 | 模型特有 |
| 6 | 模型训练 | 全量训练 + 筛选重训 | 模型特有 |
| 7 | 特征筛选 | WOE/PSI/消融稳定性分析 | 模型特有 |
| 8 | 模型评估 | AUC/KS/sloping/逾期率 | 模型特有 |
| 9 | 模型上线 | feat_upload + ETL配置 | 全部统一 |

---

## 二、子分迭代完整流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                       子分模型版本迭代流程                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 0: 确定迭代范围                                                │
│    └─ 选择需要迭代的模型, 确认 X表/Y表/标签/额外数据                  │
│                                                                     │
│  Step 1: 数据源更新                                                  │
│    ├─ 建模宽表 (df_master) — 新版 ETL parquet                        │
│    ├─ Y值表 (delq_data) — 新版逾期数据                               │
│    └─ 额外数据 — 模型特有标签/特征表                                  │
│                                                                     │
│  Step 2: 各子分模型开发 (标准LGB流程)                                 │
│    ├─ 2.1 全量特征初筛训练 (2000轮, ES=100)                          │
│    ├─ 2.2 特征重要性筛选 (gfr, perc > 0.01)                         │
│    ├─ 2.3 筛选特征再训练 (2000轮, ES=100)                            │
│    ├─ 2.4 自动化特征稳定性分析流水线                                  │
│    │     ├─ WOE稳定性 → PSI稳定性 → 特征消融                        │
│    │     └─ 子分消融 (可选, 融合模型用)                              │
│    └─ 2.5 最终版训练 (5000轮, ES=100)                                 │
│                                                                     │
│  Step 2-B: 特殊模型流程                                              │
│    ├─ 图像子分: 图像爬取 → ResNet18训练                              │
│    ├─ XGB双塔(15): vector_leaf 双目标训练 → 联合评估                 │
│    ├─ XGB生存分析(19): survival:aft 区间删失 → AFT回归               │
│    ├─ 弹性模型(18): 弹性标签构造 → 多子模型训练                      │
│    ├─ 蒸馏子分(20): Teacher打分加载 → regression蒸馏                 │
│    └─ 金额逾期(21): 金额加权样本 → 多阈值实验                        │
│                                                                     │
│  ※ 前置C卡遵循标准 LGB 流程，仅训练样本不同（需抽样好样本）          │
│                                                                     │
│  Step 3: 评估模型分替换                                              │
│    ├─ 各子分集体打分                                                 │
│    └─ OOT AUC/KS/逾期率评估                                         │
│                                                                     │
│  Step 4: 模型上线                                                    │
│    ├─ feat_upload() 生成特征配置 (fea_new.txt / fea_old.txt)         │
│    ├─ 线上回溯一致性校验                                              │
│    └─ 阈值切分 (cut_score_bins)                                      │
│                                                                     │
│  Step 5: 监控部署                                                    │
│    └─ AUC/KS/PSI 定期监控                                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、版本架构设计（含V13基线）

> 每次大版本迭代（约3个月一次）需先确定版本级架构设计，再进入各子分开发。以下以 V13 为基线参考，V14+ 迭代时可直接对照调整。

### 3.0 版本级设计决策模板

每次迭代启动时，需明确以下架构选择项：

| 决策项 | 需确认内容 | V13 基线 | V14 填写 |
|--------|-----------|---------|---------|
| **双Y值策略** | 主评级使用哪些Y值并行建模 | MOB1 7+（短期）+ MOB3 7+（中期） | |
| **子分层训练窗口** | 子分模型训练数据的时间范围 | 2023.7.1 ~ 2025.6.30 | |
| **融合层训练窗口** | 上层融合模型训练数据的时间范围 | 2024.8.1 ~ 2025.7.31 | |
| **OOT 窗口** | 时间外验证起始 | 2025.8.1 至今 | |
| **样本拆分比例** | 融合层 INS / OOS 比例 | 80% INS + 20% OOS | |
| **融合策略** | 不同Y值的融合样本约束 | MOB1 用全量样本；MOB3 用 3 期及以上样本 | |
| **子分模型规模** | 计划开发 / 入模子分数量 | 130 个开发，78 个入模 (60%) | |
| **特征池规模** | 宽表粗筛后特征维度 | 79,801 → 19,479 | |

### 3.1 V13 整体架构参考

| 项目 | V13 设计 |
|------|---------|
| 双Y值 | MOB1 7+（短期）+ MOB3 7+（中期），并行建模 |
| 训练窗口 | 上层融合 24.8.1~25.7.31；子分 23.7.1~25.6.30 |
| OOT窗口 | 2025.8.01至今 |
| 样本拆分 | 融合层80% INS + 20% OOS；子分层含全量+80% INS |
| 融合策略 | MOB1用全量样本，MOB3用3期及以上样本 |

### 3.2 V13 特征筛选管线（宽表级）

> 此管线在宽表产出阶段执行（Step 1 之前），与 notebook 内的 `gfr()` / `run_stability_pipeline()` 筛选属于不同层级。宽表级筛选产出粗筛特征集，notebook 内筛选在此基础上进一步精筛。

| 数据源 | 备选特征 | 稳定性筛 | 效果筛 | 最终粗筛 |
|--------|---------|---------|--------|---------|
| APP | 33,063 | 16,369 | 4,879 | **4,879** |
| AFPI | 12,674 | 10,912 | 5,873 | **5,873** |
| CBI | 23,949 | 15,494 | 5,240 | **5,240** |
| IZI | 8,641 | 5,841 | 2,109 | **2,109** |
| 鉴权 | 515 | 469 | 469 | **469** |
| ADVANCE | 315 | 265 | 265 | **265** |
| 同盾(TD) | 644 | 644 | 644 | **644** |
| **合计** | **79,801** | — | — | **19,479** |

### 3.3 V13 增益归因（MOB1 短逾 +1.2pp）

> 版本迭代时应做增益归因分析，量化各因素对 AUC 提升的贡献，作为下一版本优化方向的参考。

| 增益来源 | 贡献 | 说明 |
|---------|------|------|
| 样本拉新（OOT延长2.5月到25.7.31） | **+0.6pp** | 最大增益来源 |
| 关联类特征（图谱特征V2稳定版本） | +0.3pp | App图网络V2 |
| 复贷AFPI分类特征 | +0.2pp | 特征增量 |
| 新Target Encoding | +0.1pp | 特征工程 |

**增益规律**：样本拉新 > 特征增量 > 模型架构优化。每次迭代应优先确认数据时间窗口是否充分拉新。

---

## 四、模型配置注册表

下表记录21个V13子分模型的完整配置。迭代新版本时，仅需更新路径和时间窗口参数。

### 3.1 概览表

| # | 模型名 | 框架 | objective | X表来源 | target_col | 特殊流程 |
|---|--------|------|-----------|---------|------------|---------|
| 1 | V13埋点子分 | LGB | binary | etl埋点(3000042633) | mob1/2/3_label7 + shilian1 | 多label训练 |
| 2 | 前置C卡 | LGB | binary | 标准V13宽表 | mob1_label7 | 标准流程，需抽样好样本(比例需实验) |
| 3 | 同盾子分 | LGB | binary | V13_td_644 | label_180 + mob2_label7 | 使用df_tar_180 |
| 4 | 图像子分 | PyTorch+LGB | binary | ResNet18图像特征 | mob2_label7 | 图像爬取+ResNet训练 |
| 5 | 多头增长模型 | LGB | tweedie | V13_3156 + delta特征 | tweedie_target(delta) | delta特征非空过滤 |
| 6 | 多头风险子分 | LGB | binary | etl(3000041793) | mob2_label7 | mob2_days>=7 + 评级分组 |
| 7 | 失联模型 | LGB | binary | 标准V13宽表 | shilian | 失联标签 + mob1_days>=7 |
| 8 | 资质风险模型 | LGB | binary | V13_5166 + 鉴权编码 | mob3_label7 | auth+cbi+afpi子集 |
| 9 | 还款金额预测 | LGB | tweedie | 标准V13宽表 | paid_principal_sum_180d | Tweedie回归 |
| 10 | 待还金额预测 | LGB | tweedie | 标准V13宽表 | principal_unpaid_180d | Tweedie回归 |
| 11 | 逾期天数预测 | LGB | regression | 独立4000维数据集 | 逾期天数 | 独立数据集 |
| 12 | 长短逾模型 | LGB | binary | 标准V13宽表 | label1 | 外部ovd标签 |
| 13 | 差异化模型 | LGB | tweedie | 标准V13宽表 | label1 | 外部ovd标签 |
| 14 | 额度变化预测 | LGB | tweedie | V13_5166 + 新特征 | info_edu_ratio_180d | 额度变化标签 |
| 15 | XGB双塔模型 | **XGB** | binary(双目标) | 视变体而定 | 双目标 (风险+转化/额度) | XGB vector_leaf 双塔, 含2个变体 |
| 16 | 历史子分 | LGB | binary | 标准V13宽表 | mob2/3_label7 | 2024H2短窗口训练 |
| 17 | 头部客群子分 | LGB | binary | 标准V13宽表 | mob1/3_label7 | ABC评级客群过滤 |
| 18 | 弹性模型 | LGB | binary | 标准V13宽表 | 弹性标签(初好后坏) | MOB1好→MOB3坏 / MOB3好→MOB6坏 |
| 19 | 生存分析子分 | **XGB** | survival:aft | 标准V13宽表 | AFT标签(首逾MOB期数) | XGB AFT生存分析 |
| 20 | 蒸馏子分 | LGB | regression | 标准V13宽表 | Teacher模型分(V11/V12) | 知识蒸馏 |
| 21 | 金额逾期模型 | LGB | binary | 标准V13宽表 | mob2_label7 | 金额加权(principal weight) |

### 3.2 详细配置

#### (1) V13埋点子分

| 项目 | 配置 |
|------|------|
| **X表** | ETL埋点数据 `/data/etl_data_overseas/{date}/3000042633/data/` |
| **Y表** | 标准 delq_data + 失联标签 `失联标签V13_1229.csv` |
| **target_col** | mob1_label7, mob2_label7, mob3_label7, shilian1 (多label逐个训练) |
| **sample_filter** | `second_done_date` 时间切分 (非 `first_done_date`) |
| **feature_subset** | `all_ava_md_stable_vars` (排除不稳定埋点特征) |
| **params** | params_with_balance (binary) |
| **注意** | df_master 的 index 用 `loanAccountId` 而非标准index |

#### (2) 前置C卡

> **前置C卡不属于特殊模型**，遵循标准 LGB 训练流程，唯一区别在于建模样本构造需要抽样好样本加入训练。抽样比例需要通过实验确定最优值。

| 项目 | 配置 |
|------|------|
| **X表** | 统一建模宽表 |
| **Y表** | 标准 delq_data |
| **target_col** | mob1_label7 |
| **sample_filter** | `mob1_label1>0` (入催用户) — 默认仅包含入催样本 |
| **feature_subset** | all_vars |
| **params** | 强正则化 params (reg_alpha=60, reg_lambda=80, Optuna 调优) |

**好样本抽样说明：**

前置C卡的目标客群 (`is_mob1_pd1_delq=1`) target rate 极高，直接训练模型区分度差。解决方案是从 `is_mob1_pd1_delq=0` 的好样本中按比例抽样加入训练集。

| 实验名 | 模型后缀 | 抽样比例 | 好坏比 | 说明 |
|--------|---------|---------|--------|------|
| baseline | `_no0` | 不加好样本 | 原始(极高) | 仅入催样本 |
| 抽样法A | `_samp0_033` | 3.3% | ≈1:10 | 较多好样本 |
| 抽样法B | `_samp0_016` | 1.6% | ≈1:20 | 中等 |
| 抽样法C | `_samp0_011` | 1.1% | ≈1:30 | 通常效果较好 |

抽样后使用标准 `train.ModelConfig` + `train.train_lgb_model` 训练，无需进入特殊模型流程。

最优单模型可进一步与线上模型分 (`modelId_200001042`) 做浅层 LGB 融合 (max_depth=2, num_leaves=4)。

#### (3) 同盾子分

| 项目 | 配置 |
|------|------|
| **X表** | 同盾独立特征表 `V13_td_644.pqt` |
| **Y表** | 180天标签表 `delq_new_from23_label180_{date}.pqt` (df_tar_180) |
| **target_col** | label_180, mob2_label7 (两个label分别训练) |
| **sample_filter** | `label_180>=0`, 训练样本分两段 (2023-01前全量 + 2024-08后ins_only) |
| **feature_subset** | flt_vars + int_vars (从dtypes区分) |
| **params** | params_with_balance (binary) |
| **注意** | 使用 df_tar_180 而非标准 delq_data 做样本交集 |

#### (4) 图像子分

| 项目 | 配置 |
|------|------|
| **X表** | ResNet18 提取的图像特征 (best + env 双图) |
| **Y表** | 标准 delq_data |
| **target_col** | mob2_label7 (训练), mob1_label7 (OOT评估) |
| **sample_filter** | `mob2_label7>=0`, 排除oos |
| **模型架构** | MultiImageResNet18 (PyTorch, BCELoss, Adam) |
| **参考notebook** | 训练: `/data/public_data/cpu4/yanzhang1/20250722_图像子分/img/V13_train_resnet_addtrans_2101_250630_bestenv_oot2501-mob2-0305.ipynb` |
| **图像爬取** | `/data/public_data/cpu4/yanzhang1/20250722_图像子分/img/img_crawler_v2-GPU_24062505.ipynb` |
| **训练参数** | lr_fc=1e-3, lr_bone=3e-7, batch_size=1028, epochs=10, CosineAnnealingLR |
| **后融合** | ResNet分数 + modelId_200001042 → 浅层LGB |

#### (5) 多头增长模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 + delta特征 (etl 3000041793) |
| **Y表** | 标准 delq_data |
| **target_col** | tweedie_target (IziDataDuoTouIn90D_totalOfInstitution_delta1) |
| **sample_filter** | `IziDataDuoTouIn90D_totalOfInstitution_delta1.notna()` (delta非空) |
| **feature_subset** | v13_all_vars |
| **params** | tweedie objective (params_with_balance 改 objective='tweedie') |

#### (6) 多头风险子分

| 项目 | 配置 |
|------|------|
| **X表** | ETL多头数据 `/data/etl_data_overseas/{date}/3000041793/data/` |
| **Y表** | 标准 delq_data, 需要 `principal_unpaid_ratio` |
| **target_col** | mob2_label7 |
| **sample_filter** | `mob2_days>=7`, 按评级分组训练 (ABC / DEFG) |
| **feature_subset** | all_vars_duotou |
| **params** | params_with_balance (binary) |
| **注意** | 需定义 `pingji_li1=['A','A1','B','B1','C']`, `pingji_li2=['D','D1','E','E1','F','G']` |

#### (7) 失联模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data + 失联标签 csv |
| **target_col** | shilian (失联=1, 未失联=0, 无标签=-1) |
| **sample_filter** | `mob1_days>=7 and shilian != -1` |
| **feature_subset** | all_vars |
| **params** | params_with_balance (binary) |
| **注意** | 需 `delq_data1 = concat(delq_data, df_label)`, 后续用 delq_data1 |

#### (8) 资质风险模型

| 项目 | 配置 |
|------|------|
| **X表** | 5166维宽表 `V13_all_feature_5166_{date}.pqt` + 鉴权编码 pkl |
| **Y表** | 标准 delq_data |
| **target_col** | mob3_label7 |
| **sample_filter** | `mob3_label7>=0` |
| **feature_subset** | auth_vars + cbi_vars + afpi_vars (排除CBI_SCORINGDETAIL) + 鉴权编码 |
| **params** | params_with_balance (binary), 有 Optuna best_params 覆盖 |
| **注意** | 多个子实验: nocbiscore / abc / fea2 等组合 |

#### (9) 还款金额预测模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data + `total_paid_principal_180d_{date}.csv` |
| **target_col** | paid_principal_sum_180d (Tweedie: target = paid / principal) |
| **sample_filter** | `paid_principal_sum_180d>=0` |
| **feature_subset** | auth_vars + cbi_vars + iziwhatsapp_vars (子集) |
| **params** | tweedie objective |

#### (10) 待还金额预测模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data + `total_unpaid_principal_fd180_{date}.pt` |
| **target_col** | principal_unpaid_180d (Tweedie) |
| **sample_filter** | `principal_unpaid_180d>=0` |
| **feature_subset** | v13_all_vars |
| **params** | tweedie objective |

#### (11) 逾期天数预测子分

| 项目 | 配置 |
|------|------|
| **X表** | 独立4000维数据集 `460万建模样本4000维变量.pt` |
| **Y表** | `ovd_days_from_bill_202211.csv` (逾期天数) |
| **target_col** | 逾期天数 (连续值) |
| **sample_filter** | 按时间切分 (train < 2025-05, OOT >= 2025-05) |
| **feature_subset** | model_data 全部特征 |
| **params** | regression objective, metric=l2 |
| **注意** | 不使用标准V13宽表, 完全独立的数据集 |

#### (12) 长短逾模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data + `ovd_days_from_bill_202211_to_202506.parquet` |
| **target_col** | label1 (长逾期=1, 短逾期=0, binary) |
| **sample_filter** | `label1>=0` |
| **feature_subset** | all_vars |
| **params** | binary objective |

#### (13) 差异化模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data + `ovd_days_from_bill_202211_to_202506.parquet` |
| **target_col** | label1 (好坏差异度, Tweedie) |
| **sample_filter** | `label1>=0` |
| **feature_subset** | all_vars |
| **params** | tweedie objective |

#### (14) 额度变化预测模型

| 项目 | 配置 |
|------|------|
| **X表** | 5166维宽表 + 新特征 (etl 3000041877) |
| **Y表** | 标准 delq_data + `eduinfo_{date}_ratio180d_info.csv` |
| **target_col** | info_edu_ratio_180d (Tweedie) |
| **sample_filter** | `info_edu_ratio_180d>=0` |
| **feature_subset** | auth_vars + cbi_vars + iziwhatsapp_vars + 新特征 |
| **params** | tweedie objective |

#### (15) XGB双塔模型

XGB 双塔模型使用 `vector_leaf` 机制在同一棵树上同时优化两个目标。当前有两个变体：

**变体 A: 下单率风险双塔**

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 + df1 (etl 3000042158) + df2 (etl 3000042157) |
| **Y表** | 独立 delq_data (`delq_new_from23_gj_{date}_withDuplicatedL1.pt`) |
| **塔1 (风险)** | mob1_label7 |
| **塔2 (转化)** | tixian (下单率) |
| **sample_filter** | `tixian>=0` 或 `mob1_label7>=0`, label 拼接为 [N,2] |
| **feature_subset** | 标准宽表特征 + df1/df2 特征 |
| **注意** | `rut` 字段值为 `'Android'` 而非 `'安卓'` |

**变体 B: 风险额度双塔**

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data, 额外构造 `quota_rate_label` |
| **塔1 (风险)** | mob3_label7 |
| **塔2 (额度)** | quota_rate_label (`1 if principal >= info else 0`) |
| **sample_filter** | `mob3_label7>=0`, 标准时间窗口 |
| **feature_subset** | 全量特征, 排除不稳定IZI (drop_list) |

**两个变体的共同配置:**

| 项目 | 配置 |
|------|------|
| **框架** | **XGBoost** (非LGB), `vector_leaf=True, vector_leaf_dim=2` |
| **objective** | `binary:logistic` (双目标) |
| **params** | XGB vector_leaf 参数 (详见第八章 8-C 节) |
| **训练方式** | Y 为 `[N,2]` 矩阵, 两个塔共享特征分裂、各自学叶值 |
| **预测输出** | `pred[:, 0]` = 塔1 (风险), `pred[:, 1]` = 塔2 (转化/额度) |
| **评估** | 各塔独立AUC + 联合 `pred[:,0]*pred[:,1]` |
| **早停依据** | 以塔1 (风险) AUC 为准 |

#### (16) 历史子分

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data |
| **target_col** | mob2_label7, mob3_label7 (分别训练两个模型) |
| **sample_filter** | 训练窗口仅 2024H2: `apply_date >= 20240701 & < 20250101`, 排除 OOS |
| **feature_subset** | 全量3156维, 排除不稳定IZI特征 (drop_list) |
| **params** | params_with_balance (binary), 初筛2000轮/最终版5000轮, ES=100 |
| **特点** | 短窗口训练 (仅半年数据), 捕捉近期风险特征变化 |

#### (17) 头部客群子分

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data |
| **target_col** | mob1_label7, mob3_label7 (分别训练) |
| **sample_filter** | `af_model_bin in ['A','A1','B','B1','C']` (头部客群), 标准时间窗口 |
| **feature_subset** | 全量3156维 |
| **params** | params_with_balance (binary), 初筛2000轮/最终版5000轮, ES=100 |
| **特点** | 仅限头部ABC评级客群, 捕捉优质客群内的风险差异 |

#### (18) 弹性模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data, 需构造弹性标签 |
| **target_col** | 弹性标签: MOB1好→MOB3坏 (label_13), MOB3好→MOB6坏 (label_36) |
| **sample_filter** | mob1to3: `is_mob1_pd7_delq==0` 的样本中区分 mob3 好坏; mob3to6 类似 |
| **feature_subset** | 全量3156维, 排除不稳定IZI (drop_list) |
| **params** | params_with_balance (binary), 初筛2000轮/最终版5000轮, ES=100 |
| **Y构造** | `bad13 = mob1好 & mob3坏`, `good13 = mob1好 & mob3好` |
| **特点** | 预测"初期表现好但后期恶化"的客户, 两个子模型分别训练 |

#### (19) 生存分析子分

| 项目 | 配置 |
|------|------|
| **框架** | **XGBoost** (非LGB), objective=`survival:aft` |
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data, 需构造 AFT 区间标签 |
| **target_col** | AFT标签: `label_lower_bound` 和 `label_upper_bound` (区间删失) |
| **sample_filter** | 标准时间窗口 |
| **feature_subset** | 全量特征, 筛选 perc>0.015 |
| **params** | XGB AFT 参数 (详见下方) |
| **Y构造** | 最早逾期MOB期数 (1-9), 右截断=10, upper=10+terms |
| **评估** | score = 20 - aft_pred (转为风险分, 越高越危险) |

**AFT 标签构造逻辑**:
```python
# 找最早逾期的MOB期数
data_target['i1_label7_term'] = data_target['is_mob1_pd7_delq'].apply(lambda x: 1 if x==1 else 10)
data_target['i2_label7_term'] = data_target['is_mob2_pd7_delq'].apply(lambda x: 2 if x==1 else 10)
# ... i3 ~ i9 类似
data_target['aft_label'] = data_target[['i1_label7_term','i2_label7_term',...]].min(axis=1)
data_target['aft_upper'] = data_target['aft_label'] + terms  # 右截断上界
```

**XGB AFT 参数**:
```python
params_aft = {
    'booster': 'gbtree', 'tree_method': 'hist',
    'objective': 'survival:aft', 'eval_metric': 'aft-nloglik',
    'aft_loss_distribution': 'normal',
    'aft_loss_distribution_scale': 1.0,
    'max_depth': 5, 'learning_rate': 0.05,
    'subsample': 0.8, 'colsample_bytree': 0.75,
    'seed': 2023,
}
```

#### (20) 蒸馏子分

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | Teacher 模型的线上打分 (etl 3000042080) |
| **target_col** | Teacher 模型分 (regression): modelId_200001042 (V11子分), modelId_200001315 (V12 MOB1), modelId_200001313 (V12 MOB3), modelId_200001314 (V12额度系数) |
| **sample_filter** | 需要 Teacher 分数非空: `set(delq_data.index) & set(data.index) & set(data_score.index)` |
| **feature_subset** | 全量3156维 |
| **params** | regression objective, metric=rmse, 初筛2000轮/最终版5000轮, ES=100 |
| **特点** | 将 V11/V12 模型知识蒸馏到 V13 特征空间; 每个 Teacher 分数分别训练一个 Student 模型 |
| **筛选阈值** | perc > 0.002 (远低于标准0.03, 因为回归任务特征重要性分布更均匀) |

#### (21) 金额逾期模型

| 项目 | 配置 |
|------|------|
| **X表** | 标准V13宽表 `V13_all_feature_3156_{date}.pqt` |
| **Y表** | 标准 delq_data |
| **target_col** | mob2_label7 |
| **sample_filter** | 标准时间窗口 |
| **feature_subset** | 全量3156维, 排除不稳定IZI (drop_list) |
| **params** | params_with_balance (binary), 初筛2000轮/最终版5000轮, ES=100 |
| **特殊权重** | 按本金/逾期金额加权: `w_amt = mob1_unpaid_7d * label + principal * (1-label)`, 按金额阈值 (100w/200w/500w等) 分段实验 |
| **特点** | 通过金额加权提升高本金客户的区分力, 多个金额阈值做对比实验 |
| **筛选阈值** | perc > 0.025 |

### 3.3 线上模型ID映射表（V13基线）

> 开发期模型名与线上部署 modelId 的映射关系。V14 迭代时需申请新的 modelId 并更新此表。

#### 一次风控模型

| 模型ID | 线上名称 | 用途 |
|--------|---------|------|
| 200001608 | LOAN_RISK_MOB1_V13 | MOB1 主评级 |
| 200001609 | LOAN_RISK_MOB3_V13 | MOB3 主评级 |
| 200001611 | LOAN_RISK_FREE_MOB1_V13 | 免费前筛 |
| 200001610 | LOAN_RISK_LOSS_CONTACT_V13_SCORE | 失联融合 |
| 200001606 | LOAN_RISK_EDU_MODEL_V13 | 额度系数 |

#### 二次风控模型

| 模型ID | 线上名称 | 描述 |
|--------|---------|------|
| 200001616 | SECOND_FPD31_V13 | 二次FPD31（无埋点） |
| 200001617 | SECOND_FPD31_MAIDIAN_V13 | 二次FPD31（含埋点） |
| 200001618 | SECOND_MOB1_V9 | 二次MOB1（无埋点） |
| 200001619 | SECOND_MAIDIAN_MOB1_V9 | 二次MOB1（含埋点） |
| 200001620 | SECOND_MOB3_V9 | 二次MOB3（无埋点） |
| 200001621 | SECOND_MAIDIAN_MOB3_V9 | 二次MOB3（含埋点） |
| 200001612~15 | SECOND_LC_*_V13 | 二次失联 x4 版本 |

### 3.4 子分体系分类概览（V13基线）

> V13 共开发 130 个新增子分，其中 78 个入模（入模率约 60%）。以下按类别汇总各子分的数量和增益参考值。

| 子分类型 | 数量 | 核心模型 | 增益参考 |
|---------|------|---------|---------|
| 数据源子分 | 12 | 各数据源 MOB2/LABEL180 双Y | CBI +0.73pp, 鉴权 +1.4pp |
| 蒸馏系列 | 8 | V10/V11/V12/额度/复贷蒸馏 | V12 蒸馏 AUC=0.639 |
| 历史子分 | 74 | 半年切片 x 评级分组 x 窗口 | 42 个未入模 |
| 弹性模型 | 2 | MOB1to3, MOB3to6 | 1to3 增益 +2.7pp |
| 金额加权 | 3 | 1500w/1000w/500w | 1000w 增益 +2.6pp |
| 双塔系列 | 4 | 下单率/额度使用率 x 风险 | STAR 架构 |
| 流入系列 | 4 | MOB1D1/3D1/6D1/9D1 | 9m1d 增益 +4.7pp |
| 头尾部拆分 | 4 | 头部/D评级 x 短期/长期 | 按评级切分 |
| Y值差异化 | 5 | 逾期90/180D/Tweedie/MOB2D7 | 非标Y值 |
| 反欺诈子分 | 3 | FPD31/资金饥渴/失联 | FPD31 +1.65pp |
| 复贷系列 | 4 | 首贷特征 1/3/6/9m7d | 复贷样本建模 |
| 业务场景 | 5 | 前置C卡/额度/下单双塔 | 额度系数专用 |
| 额度系数 | 4 | 多头/资质/提额gap/还款 | 仅多头+资质有增益 |

**V14 迭代参考**: 子分入模率约 60% 是正常水平。历史子分数量最多 (74个) 但入模率较低 (仅约 43%)，应重点关注增益确认后再批量开发。增益最高的类别为流入系列 (+4.7pp) 和弹性模型 (+2.7pp)。

---

## 五、AI协作: 自动化代码生成接口

### 4.1 用户输入规范

迭代某个子分时，只需告诉AI以下信息，即可自动生成完整的 Sections 2-8 代码：

```
模型名称: <模型名>
X表: <路径或描述, 如 "标准V14宽表" / "独立特征表 /path/to/feature.pqt">
Y表: <路径或描述, 如 "标准V14 delq" / "自定义标签 /path/to/label.csv">
建模标签: <target_col名, 如 mob1_label7 / label1 / tweedie_target>
objective: <binary / tweedie / regression>
样本过滤: <训练样本的额外过滤条件, 如 "mob2_days>=7" / "label1>=0" / 无>
额外数据: <需要额外加载的数据表及路径, 如 "失联标签 /path/to/shilian.csv">
特征子集: <all / auth+cbi+afpi / 自定义列表>
OOT起始: <YYYY-MM-DD, 如 2025-11-01>
评级分组: <不分组 / ABC_DEFG>
```

### 4.2 AI自动生成内容

AI 根据上述输入，参照本 SOP 中的模型配置注册表和代码模板，自动生成：

| Section | 自动生成内容 |
|---------|-------------|
| S2 样本定义 | df_master 加载代码 + df_sample_type + bf_ins/oos + 额外数据加载 |
| S3 Y定义 | delq_data 加载 + label 处理 + 额外标签 merge |
| S4 训练样本定义 | com_ids_all + train/valid/OOT query (根据 sample_filter 和 OOT起始) |
| S5 特征选取 | all_vars 或 feature_subset 代码 |
| S6 模型训练 | 全量训练 + gfr筛选 + 筛选重训 (含参数配置) |
| S7 特征筛选 | 稳定性分析流水线调用代码 + 稳定特征重训 |
| S8 模型评估 | AUC/KS/sloping 评估代码 |

### 4.3 示例: 迭代"失联模型"到V14

用户输入:
```
模型名称: 失联模型
X表: 标准V14宽表
Y表: 标准V14 delq + 新版失联标签 /data/.../失联标签V14.csv
建模标签: shilian
objective: binary
样本过滤: mob1_days>=7 and shilian != -1
额外数据: 失联标签 /data/.../失联标签V14.csv
特征子集: all
OOT起始: 2025-11-01
评级分组: 不分组
```

AI 生成完整 notebook 代码，用户只需review并执行。

---

## 六、数据源更新 (Step 1)

每次版本迭代，以下核心数据源需要更新：

| 数据 | 说明 | 路径格式 |
|------|------|---------|
| **建模宽表** | 每次迭代提供一个合并的 ETL 特征宽表 (全部模型共用) | `/data/public_data/gpu2/wangleilei/V{ver}/V{ver}_all_feature_{dim}_{date}.pqt` |
| **Y值表** | 贷后逾期数据 | `/data/public_data/gpu4/yonghaoduan/loan_infrastructure/delq_data/delq_new_from23_fk_{date}.pt` |
| **样本拆分表** | ins/oos划分 | `/data/public_data/cpu1/mabufa/10_v{ver}模型开发/01_样本拆分/data/01_v{ver}建模样本拆分/01_df_sample_type_v2_{date}.pqt` |

> 注: 以前宽表分 3156 维 (标准) 和 5166 维 (扩展) 两个文件，从 V14 起合并为一个统一宽表，各模型在特征选取阶段自行选择子集。

### 标准加载代码

```python
# ── 建模宽表 (统一宽表) ──
df_master = pd.read_parquet('<新宽表路径>')
df_master.columns = [x.replace('___','.') for x in df_master]
df_master = df_master[~df_master.index.duplicated()]
df_master.columns = etlName_replace(df_master.columns)

# ── 样本拆分表 ──
df_sample_type = pd.read_parquet('<新样本拆分表路径>')
bf_ins_idx = df_sample_type[df_sample_type['sample_type']=='ins']['loan_account_id'].tolist()
bf_oos_idx = df_sample_type[
    (df_sample_type['sample_type']=='oos') &
    (df_sample_type['first_done_date']>='2024-08-01')
]['loan_account_id'].tolist()

# ── Y值表 ──
delq_data = gdw("<新Y值表路径>")
delq_data['mob1_ripe_days'] = pd.to_numeric(delq_data['mob1_ripe_days'])

for i in range(1,7):
    delq_data[f'm{i}'] = np.where(
        pd.to_numeric(delq_data[f'mob{i}_ripe_days']) >= 7,
        delq_data[f'mob{i}_principal_unpaid_7d'], np.nan)
    delq_data[f'mob{i}_label7'] = pd.to_numeric(np.where(
        pd.to_numeric(delq_data[f'mob{i}_ripe_days']) >= 7,
        delq_data[f'is_mob{i}_pd7_delq'], np.nan))

delq_data['cl_type'] = np.where(
    delq_data['first_risk_flow_id'].astype(float).isin([1825,1826,1842,1843]), 'v11',
    np.where(delq_data['first_risk_flow_id'].astype(float).isin(
        [1869,1870,1895,1896,1904,1905]), 'v12', 'other'))

delq_data['fpd31_principal'] = pd.to_numeric(delq_data['fpd31_principal'])
delq_data['fdp_ripe_days'] = pd.to_numeric(delq_data['fdp_ripe_days'])
delq_data['is_fpd31'] = delq_data['fpd31_principal'].apply(lambda x: 1 if float(x)>0 else 0)
delq_data.loc[delq_data['fdp_ripe_days']<30, 'is_fpd31'] = np.nan

for i in range(1,7):
    delq_data[f'mob{i}_ripe_days'] = pd.to_numeric(delq_data[f'mob{i}_ripe_days'])
    delq_data[f'mob{i}_label1'] = np.where(
        pd.to_numeric(delq_data[f'mob{i}_ripe_days']) >= 1,
        delq_data[f'is_mob{i}_pd1_delq'], np.nan)

delq_data['week'] = pd.to_datetime(delq_data['first_done_date']).dt.to_period('W').dt.start_time
delq_data = delq_data[~delq_data.index.duplicated()]
```

### 时间窗口更新

| 参数 | 说明 | 更新方式 |
|------|------|---------|
| 训练起始日期 | 保持 `2023-07-01` | 固定 |
| 训练截止日期 | = OOT起始日期 | 根据数据调整 |
| OOT起始日期 | 最近有成熟数据的月份 | 如 `2025-11-01` |
| 验证集 | bf_oos_idx (样本拆分表) | 不用时间切分 |

> **⚠ 关键规则**: 所有子分模型的训练集必须剔除 `bf_oos_idx`。`bf_oos_idx` 是上层融合模型的验证集，若子分训练集包含这些样本，会导致融合模型评估时产生数据泄露。默认使用 `loan_account_id not in @bf_oos_idx` 进行剔除，不要使用 `bf_ins_idx` 取交集（因为 ins+oos 不一定覆盖全部样本）。

### 标准训练样本拆分模板

```python
com_ids_all = fcc(delq_data.index, df_master.index, 1)[1]

# train: 排除oos, 满足样本过滤条件
train_idx = delq_data.reindex(com_ids_all).query(
    f'loan_account_id not in @bf_oos_idx '
    f'and {TARGET_FILTER} '                     # 如 "mob1_label7>=0" / "label1>=0"
    f'and {rut} in ("IOS","安卓") '
    f'and risk_type in ("首贷风控","首贷回捞") '
    f'and first_done_date <"{OOT_START}" '      # OOT起始
    f'and first_done_date >="2023-07-01"'       # 训练起始
).index.tolist()

# valid: oos样本
valid_idx = delq_data.reindex(com_ids_all).query(
    f'loan_account_id in @bf_oos_idx '
    f'and {TARGET_FILTER} '
    f'and {rut} in ("IOS","安卓") '
    f'and risk_type in ("首贷风控","首贷回捞") '
    f'and first_done_date <"{OOT_START}" '
    f'and first_done_date >="2023-07-01"'
).index.tolist()

# OOT: 时间窗口外
oot_idx_m1 = delq_data.reindex(com_ids_all).query(
    f'mob1_label7>=0 and {rut} in ("IOS","安卓") '
    f'and risk_type=="首贷风控" '
    f'and first_done_date >="{OOT_START}"'
).index.tolist()

# 回捞OOT / 大赦天下OOT
oot_idx_m1_hl = delq_data.reindex(com_ids_all).query(
    f"mob1_label7>=0 and first_done_date >='{OOT_START}' "
    f"and {rut} in ('安卓', 'IOS') and risk_type =='首贷回捞'"
).index.tolist()
oot_idx_m1_dstx = delq_data.reindex(com_ids_all).query(
    f"mob1_label7>=0 and first_done_date >='{OOT_START}' "
    f"and {rut} in ('大赦天下') and risk_type =='首贷风控'"
).index.tolist()
```

#### 前置C卡: 好样本抽样训练集构造

前置C卡使用标准 LGB 流程训练，唯一区别是训练样本需要从好样本 (`is_mob1_pd1_delq=0`) 中抽样加入。抽样比例需要通过实验确定（通常从 1.1%~3.3% 范围尝试，一般 1.1% 左右效果较好）。

```python
import random

rc_bad_idx = delq_data.reindex(com_ids_all).query(
    'mob1_label7>=0 and mob1_label1>0 '
    'and loan_account_id not in @bf_oos_idx '
    f'and first_done_date <"{OOT_START}" and first_done_date >="2023-07-01"'
).index.tolist()

rc_good_pool = delq_data.reindex(com_ids_all).query(
    'mob1_label7>=0 and mob1_label1==0 '
    'and loan_account_id not in @bf_oos_idx '
    f'and first_done_date <"{OOT_START}" and first_done_date >="2023-07-01"'
).index.tolist()

SAMPLE_RATIO = 0.011   # 抽样比例，需实验: 0.033 / 0.016 / 0.011
random.seed(42)
rc_good_sampled = random.sample(rc_good_pool, int(len(rc_good_pool) * SAMPLE_RATIO))

samp_train_idx = rc_bad_idx + rc_good_sampled  # 最终训练集
```

---

## 七、模型训练流程 (Step 2)

### 7.0 特征筛选全景：宽表级 vs Notebook级

模型迭代的特征筛选分为两个层级，在不同阶段执行：

```
┌─────────────────────────────────────────────────────────────────┐
│  宽表级筛选 (Step 1 之前, 由数据团队完成)                          │
│  79,801 原始特征 → 稳定性筛 → 效果筛 → 19,479 粗筛特征           │
│  产出: V{ver}_all_feature_{dim}_{date}.pqt                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │ df_master.columns = 粗筛后特征
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Notebook级筛选 (Step 2, 各子分独立执行)                          │
│  all_vars → gfr() 重要性筛 → select_vars                        │
│  select_vars → run_stability_pipeline() → final_stable_vars     │
│  产出: 各模型 models/ 目录下的 model.model + feature.txt          │
└─────────────────────────────────────────────────────────────────┘
```

**V13 基线**: 宽表级从 6 大数据源 79,801 维筛选至 19,479 维（保留率 24.4%），各数据源保留率差异大（APP 14.8%、AFPI 46.3%、CBI 21.9%、同盾 100%）。Notebook 级在此基础上进一步筛选至数百维（因模型而异）。

### 6.1 标准LGB训练-筛选-重训流水线

```
                    ┌──────────────────────┐
                    │  S5: 确定 all_vars   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ 6.1.1 全量特征初筛    │
                    │ 2000轮, ES=100       │
                    │ → 保存模型到 models/  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ 6.1.2 特征重要性筛选  │
                    │ gfr() → perc>0.03    │
                    │ → select_vars        │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ 6.1.3 筛选特征再训练  │
                    │ 2000轮, ES=100       │
                    │ → 保存 _sel/ 模型    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ 6.1.4 稳定性分析      │
                    │ WOE + PSI + 消融     │
                    │ → final_stable_vars  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ 6.1.5 最终版训练      │
                    │ 5000轮, ES=100       │
                    │ → 保存 _stable/ 模型 │
                    └──────────────────────┘
```

### 6.1.1 全量特征初筛训练

```python
sys.path.append('/data/public_data/cpu4/yanzhang1/easycash_yh/')
from src.utils.tools import *
from src.utils import train

# ── 确定特征集 ──
all_vars = df_master.columns.tolist()
# 或模型特有子集:
# all_vars = auth_vars + cbi_vars + afpi_vars  (资质风险)
# all_vars = flt_vars + int_vars               (同盾)

# ── 参数选择 ──
# binary模型
params_with_balance = {
    'boosting_type': 'gbdt', 'objective': 'binary', 'metric': 'auc',
    'is_unbalance': 'true', 'num_leaves': 44, 'learning_rate': 0.035,
    'bagging_fraction': 0.69, 'feature_fraction': 0.83,
    'bagging_freq': 20, 'max_depth': 7,
    'reg_alpha': 0.01, 'reg_lambda': 0.02,
    'min_data_in_leaf': 100, 'verbose': -1,
}

# tweedie模型 (多头增长/差异化/还款/待还/额度变化)
params_tweedie = {
    'boosting_type': 'gbdt', 'objective': 'tweedie',
    'tweedie_variance_power': 1.5, 'metric': 'rmse',
    'num_leaves': 44, 'learning_rate': 0.035,
    'bagging_fraction': 0.69, 'feature_fraction': 0.83,
    'bagging_freq': 20, 'max_depth': 7,
    'reg_alpha': 0.01, 'reg_lambda': 0.02,
    'min_data_in_leaf': 100, 'verbose': -1,
}

# (可选) Optuna 调优后覆盖
best_params = {'num_leaves': 25, 'learning_rate': 0.038, ...}
params_with_balance.update(best_params)

# ── 构造 OOT 评估集 ──
test_ids_dict = {
    'oot_cg': [oot_idx_m1, TARGET_COL],
    'oot_hl': [oot_idx_m1_hl, TARGET_COL],
    'oot_dstx': [oot_idx_m1_dstx, TARGET_COL],
}

# ── 训练 (使用 train.ModelConfig) ──
MODEL_NAME = "v14_model_{缩写}"
MODEL_DIR = f"./models/{MODEL_NAME}"

model_config = train.ModelConfig(
    MODEL_NAME,                     # 模型描述
    MODEL_DIR,                      # 模型输出路径
    params_with_balance,            # 超参数
    2000,                           # 初筛训练轮数
    all_vars,                       # 特征集合
    TARGET_COL,                     # 标签列名
    [],                             # 排除特征 (空)
    train_idx,                      # 训练样本 ids
    test_ids_dict,                  # 测试集合 {name: [ids, target]}
    None,                           # 样本权重 (None 或 weight_col)
    100,                            # 每N轮输出测试集结果
    callback=[lgb.early_stopping(stopping_rounds=100, verbose=True)],
    score_ids=oot_idx_m1 + oot_idx_m1_hl + oot_idx_m1_dstx,  # 输出模型分的样本
)
train.train_lgb_model(model_config, df_master, delq_data)
```

`train.ModelConfig` 参数说明:

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | str | 模型描述 (用于打印) |
| `path` | str | 模型输出目录 (自动创建, 保存 lgb.model / feature.txt / scores.pkl 等) |
| `params` | dict | LGB 超参数 |
| `num_boost_round` | int | 最大训练轮数 |
| `features` | list | 特征列名列表 |
| `target` | str | 标签列名 (在 delq_data 中) |
| `drop_features` | list | 从 features 中排除的特征 |
| `train_ids` | list | 训练样本 loan_account_id 列表 |
| `test_ids_dict` | dict | 测试集: `{name: [id_list, target_col]}` |
| `weight` | str/None | 样本权重列名 (None 则不加权) |
| `verbose_eval` | int | 每N轮打印一次测试指标 |
| `callback` | list | LGB回调列表 (如 early_stopping) |
| `score_ids` | list | 需要输出预测分的样本 ids (保存到 scores.pkl) |

### 6.1.2 特征重要性筛选

> **⚠ 路径一致性检查**: `train.train_lgb_model` 在目标目录已有模型文件时会自动改名为 `{name}_copy_1`。执行特征筛选前**必须确认 `gfr()` 读取的路径与实际保存的模型路径一致**，否则会读到旧模型的特征重要性，导致筛选结果完全错误。
>
> **异常信号**: 若筛选后特征数出现断崖式下降（如 3000+ → 不足 100），或后续 AUC 明显不符合预期，应首先排查：(1) gfr 读取的模型路径是否正确；(2) 该目录下的 model.model 是否为本次训练产出。

```python
# 确认模型路径
import os
assert os.path.exists(f'{MODEL_DIR}/model.model'), f"模型文件不存在: {MODEL_DIR}"
print(f"读取模型路径: {MODEL_DIR}, 文件列表: {os.listdir(MODEL_DIR)}")

fi = gfr(MODEL_DIR)[0]
fi['perc'] = fi['gain'] / fi['gain'].sum()
select_vars = fi[fi['perc'] > 0.01].index.tolist()
print(f"全量: {len(all_vars)} → 筛选后: {len(select_vars)}")

pd.DataFrame(select_vars, columns=['feature']).to_csv(
    f'{MODEL_DIR}/select_vars.csv', index=False)
```

### 6.1.3 筛选特征再训练

```python
MODEL_NAME_SEL = f"v14_model_{缩写}_sel"
MODEL_DIR_SEL = f"./models/{MODEL_NAME_SEL}"

model_config_sel = train.ModelConfig(
    MODEL_NAME_SEL,
    MODEL_DIR_SEL,
    params_with_balance,
    2000,                           # 初筛训练轮数
    select_vars,                    # 筛选后的特征集
    TARGET_COL,
    [],
    train_idx,
    test_ids_dict,
    None,
    100,
    callback=[lgb.early_stopping(stopping_rounds=100, verbose=True)],
    score_ids=oot_idx_m1 + oot_idx_m1_hl + oot_idx_m1_dstx,
)
train.train_lgb_model(model_config_sel, df_master, delq_data)
```

### 6.1.4 自动化特征稳定性分析流水线

```python
from utils.auto_feature_stability import run_stability_pipeline

pipeline_result = run_stability_pipeline(
    df_master=df_master,
    delq_data=delq_data,
    select_vars=select_vars,
    target_col=TARGET_COL,
    train_idx=train_idx,
    oot_idx=oot_idx_m1,
    model_path=MODEL_DIR_SEL,
    sub_list=None,                    # 融合模型传入子分列表
    woe_corr_threshold=0.5,
    psi_threshold=0.25,
    run_woe=True,
    run_psi=True,
    run_ablation=True,
    run_subscore=False,               # 融合模型设为True
    params=params_with_balance,
    weight_col=None,                  # 长期模型设 'weight_time'
    save_dir=f'./stability_analysis/{MODEL_NAME_SEL}/',
    verbose=True
)
final_stable_vars = pipeline_result['final_stable_vars']
print(f"筛选: {len(select_vars)} → 稳定: {len(final_stable_vars)}")
```

#### WOE 稳定性分析

| 项目 | 说明 |
|------|------|
| **原理** | 训练集做WOE分箱 → 分别计算训练集/OOT各bin的bad_rate → 计算bin-wise相关系数 |
| **自动判定** | corr > 0.5 → 稳定; 0 < corr ≤ 0.5 → 边界; corr ≤ 0 → 不稳定 |
| **输出** | `woe_stability_report.csv` + `woe_stable_vars.json` |

#### PSI 分布稳定性分析

| 项目 | 说明 |
|------|------|
| **原理** | 计算每个特征在训练集 vs OOT 的 PSI |
| **自动判定** | PSI < 0.1 → 稳定; 0.1 ≤ PSI < 0.25 → 警告; PSI ≥ 0.25 → 不稳定 |
| **输出** | `psi_stability_report.csv` |

#### 特征消融 (Permutation Importance)

| 项目 | 说明 |
|------|------|
| **原理** | 对OOT数据, 逐个打乱特征值, 测量AUC下降幅度 |
| **自动判定** | importance_mean > 0 → 正贡献(保留); ≤ 0 → 可剔除 |
| **参数** | n_repeats=5, max_samples=150000 |
| **输出** | `permutation_importance.csv` |

#### 子分消融 (融合模型使用)

| 项目 | 说明 |
|------|------|
| **适用场景** | 失联融合模型、FPD31融合模型等包含子分特征的模型 |
| **Step 1** | 高相关子分去重 (corr > 0.85 剔除) |
| **Step 2** | 贪心消融: 每轮去掉AUC影响最小的子分, 直到AUC下降超过0.001 |
| **输出** | `subscore_ablation.csv` |

### 6.1.5 最终版训练 (稳定特征)

```python
MODEL_NAME_STABLE = f"v14_model_{缩写}_stable"
MODEL_DIR_STABLE = f"./models/{MODEL_NAME_STABLE}"

model_config_stable = train.ModelConfig(
    MODEL_NAME_STABLE,
    MODEL_DIR_STABLE,
    params_with_balance,
    5000,                           # 最终版训练轮数
    final_stable_vars,              # 稳定性筛选后的特征集
    TARGET_COL,
    [],
    train_idx,
    test_ids_dict,
    None,
    100,
    callback=[lgb.early_stopping(stopping_rounds=100, verbose=True)],
    score_ids=oot_idx_m1 + oot_idx_m1_hl + oot_idx_m1_dstx,
)
train.train_lgb_model(model_config_stable, df_master, delq_data)
```

---

## 八、特殊模型流程 (Step 2-B)

### 7-A. 图像子分专用流程

图像子分使用 PyTorch + ResNet18，流程与标准LGB完全不同：

```
图像爬取 (img_crawler)
    → 解析 best + env 两类图像
    → MultiImageResNet18 训练 (PyTorch)
    → ResNet分数输出
    → (可选) ResNet分数 + 线上模型分 → 浅层LGB融合
```

| 步骤 | 说明 | 参考 |
|------|------|------|
| 图像爬取 | API拉取用户居住环境图片 (best+env) | `img_crawler_v2-GPU_24062505.ipynb` |
| 模型训练 | MultiImageResNet18, BCELoss, Adam, CosineAnnealingLR | `V13_train_resnet_addtrans_*.ipynb` |
| 训练label | mob2_label7 (训练集), mob1_label7 (OOT) | |
| 训练参数 | lr_fc=1e-3, lr_bone=3e-7, batch=1028, epochs=10 | |
| 数据增强 | 水平翻转, 15度旋转, 颜色抖动, RandomResizedCrop(224) | |
| 多GPU | DataParallel (8卡) | |

### 7-B. XGBoost 双塔模型 (vector_leaf)

> 适用于: **(15) XGB双塔模型** (含变体A: 下单率风险双塔, 变体B: 风险额度双塔)

#### 7-B-1. 核心机制

双塔模型使用 **XGBoost vector_leaf** 特性，在同一棵树结构上同时优化两个目标。每个叶节点输出一个二维向量 `[score_tower1, score_tower2]`，两个"塔"共享特征分裂但各自学习独立的叶值。

关键区别于 LGB:
- 框架: **XGBoost** (非 LightGBM)
- 数据容器: `xgb.DMatrix` (非 lgb.Dataset)
- Y 为 `[N, 2]` 矩阵: 第0列=塔1标签, 第1列=塔2标签
- 预测输出为 `[N, 2]` 矩阵: `pred[:, 0]`=塔1分, `pred[:, 1]`=塔2分
- 特征重要性: `model.get_score(importance_type='gain')`, 返回 `f{i}` 格式需映射回原始特征名

#### 7-B-2. 两个变体的配置对比

| 项 | 变体A: 下单率风险双塔 | 变体B: 风险额度双塔 |
|---|---|---|
| 塔1目标 | mob1_label7 (风险) | mob3_label7 (风险) |
| 塔2目标 | tixian (下单率/转化) | quota_rate_label (额度率 = principal >= info) |
| X表 | V13宽表 + df1 + df2 (额外ETL) | 标准V13宽表 |
| Y表 | 独立 delq (含gj/withDuplicatedL1) | 标准 delq + 构造 quota_rate |
| rut字段 | `'Android'` (注意不是`'安卓'`) | `'安卓'` / `'IOS'` |
| tree_method | `hist` / `gpu_hist` | `hist` |
| num_boost_round | 1000~2000 | 1000 |
| 早停 | 以风险AUC为准 | 以风险AUC为准 |
| 评估 | 风险AUC + 下单AUC + 联合(prod) | 风险AUC + 额度AUC |

#### 7-B-3. XGB 双塔标准参数

```python
xgb_params = {
    'booster': 'gbtree',
    'objective': 'binary:logistic',
    'tree_method': 'hist',       # 或 'gpu_hist' (需GPU)
    'max_depth': 5,
    'subsample': 0.8,
    'colsample_bytree': 0.75,
    'eta': 0.03,                 # learning_rate
    'seed': 300,
    'alpha': 1,                  # L1正则
    'gamma': 0.6,                # 最小分裂增益
    'min_child_weight': 10,
    'max_bin': 256,
    'scale_pos_weight': 4,
    'vector_leaf': True,         # 启用双塔
    'vector_leaf_dim': 2,        # 输出维度=2 (两个塔)
}
```

#### 7-B-4. 训练代码模板

```python
import xgboost as xgb
from sklearn.metrics import roc_auc_score

# ── 1. 构造双目标标签 [N, 2] ──
y_train = data_target.reindex(id_train)[[TARGET_TOWER1, TARGET_TOWER2]]
y_test  = data_target.reindex(id_test)[[TARGET_TOWER1, TARGET_TOWER2]]

# ── 2. 构造 DMatrix ──
X_train = data.reindex(id_train)[feats_valid]; X_train[np.isinf(X_train)] = np.nan
X_test  = data.reindex(id_test)[feats_valid];  X_test[np.isinf(X_test)]   = np.nan
dtrain = xgb.DMatrix(X_train, y_train)
dtest  = xgb.DMatrix(X_test,  y_test)

# ── 3. 自定义双塔评估函数 ──
def auc_func(preds, dtrain):
    y = dtrain.get_label().reshape(-1, 2)
    auc_tower1 = roc_auc_score(y[:, 0], preds[:, 0])
    auc_tower2 = roc_auc_score(y[:, 1], preds[:, 1])
    if auc_func.iteration % 100 == 0:
        print(f"Iter {auc_func.iteration}: AUC_tower1={auc_tower1:.4f}, AUC_tower2={auc_tower2:.4f}")
    auc_func.iteration += 1
    return 'AUC_tower1', auc_tower1  # 以塔1(风险)AUC决定早停
auc_func.iteration = 0

# ── 4. 训练 ──
model = xgb.train(
    xgb_params, dtrain,
    num_boost_round=2000,
    evals=[(dtest, 'eval'), (dtrain, 'train')],
    verbose_eval=100,
    feval=auc_func,  # 或 custom_metric=auc_func (xgb>=2.0)
)

# ── 5. 保存模型 ──
os.makedirs(f'./{MODEL_DIR}/', exist_ok=True)
model.save_model(f'./{MODEL_DIR}/dual_tower.model')

# ── 6. 预测与评估 ──
pred = model.predict(dtest)  # shape [N, 2]
print(f"塔1 AUC: {roc_auc_score(y_test.iloc[:,0], pred[:,0]):.4f}")
print(f"塔2 AUC: {roc_auc_score(y_test.iloc[:,1], pred[:,1]):.4f}")
print(f"联合 AUC: {roc_auc_score(y_test.iloc[:,0], pred[:,0]*pred[:,1]):.4f}")
```

#### 7-B-5. XGB 特征重要性与筛选

XGB vector_leaf 的特征名自动映射为 `f0, f1, f2, ...`，需要手动映射回原始特征名:

```python
def xgb_importance(model, feature_names):
    fea_dict = {f'f{i}': name for i, name in enumerate(feature_names)}
    gain = model.get_score(importance_type='gain')
    weight = model.get_score(importance_type='weight')
    gain_df = pd.DataFrame.from_dict(gain, orient='index', columns=['gain'])
    weight_df = pd.DataFrame.from_dict(weight, orient='index', columns=['weight'])
    imp = pd.concat([gain_df, weight_df], axis=1)
    imp['total_gain'] = imp['gain'] * imp['weight']
    imp.sort_values('total_gain', ascending=False, inplace=True)
    imp['perc'] = imp['total_gain'] / imp['total_gain'].sum() * 100
    imp['feature'] = imp.index.map(fea_dict)
    return imp.reset_index(drop=True)

imp_df = xgb_importance(model, feats_valid)
fea_sel = list(imp_df[imp_df['perc'] > 0.011]['feature'])
```

#### 7-B-6. 联合评估与选分

双塔模型两个维度可以独立使用或联合使用:

| 用途 | 取分方式 | 说明 |
|------|---------|------|
| 纯风险评估 | `pred[:, 0]` | 塔1分即风险分 |
| 纯转化/额度评估 | `pred[:, 1]` | 塔2分即转化/额度分 |
| 联合评分 | `pred[:, 0] * pred[:, 1]` | 乘积融合, 兼顾两个维度 |

注意: 变体A (下单率双塔) 的 `rut` 字段值为 `'Android'` 而非其他模型的 `'安卓'`。

### 7-C. 其他新增特殊模型说明

#### 7-C-1. 弹性模型

弹性模型预测"初期表现好但后期恶化"的客户，需特殊的标签构造:

```python
# MOB1好→MOB3坏 弹性标签
bad13  = set(data_target.query("is_mob1_pd7_delq==0 and is_mob3_pd7_delq==1").reindex(id_train_mob3).dropna().index)
good13 = set(data_target.query("is_mob1_pd7_delq==0 and is_mob3_pd7_delq==0").reindex(id_train_mob3).dropna().index)
id_train_13 = list(bad13 | good13)
data_target.loc[list(bad13), 'label_13'] = 1
data_target.loc[list(good13), 'label_13'] = 0

# MOB3好→MOB6坏 弹性标签 (需 MOB6 成熟样本)
bad36  = data_target.query("is_mob3_pd7_delq==0 and is_mob6_pd7_delq==1").reindex(id_train_mob6).dropna()
good36 = data_target.query("is_mob3_pd7_delq==0 and is_mob6_pd7_delq==0").reindex(id_train_mob6).dropna()
```

两个子模型独立训练: `config_mob1to3` 和 `config_mob3to6`。

#### 7-C-2. 蒸馏子分

蒸馏模型需加载线上 Teacher 打分作为标签:

```python
# 加载 Teacher 模型打分 (ETL)
data_score = pd.read_parquet("/data/etl_data_overseas/{date}/3000042080/data/")
data_score.index = data_score.loanAccountId.astype(int)
data_score = data_score.drop_duplicates(subset=['loanAccountId'], keep='first')

# 取交集: X表 ∩ Y表 ∩ Teacher分 都有的样本
id_list = list(set(data_target.index) & set(data.index) & set(data_score.index))
data_target = pd.concat([data_target.reindex(id_list),
    data_score.reindex(id_list)[['modelId_200001042','modelId_200001315',
                                  'modelId_200001313','modelId_200001314']]], axis=1)

# 每个 Teacher 分分别训练一个 Student (regression/rmse)
configs = {
    'V11子分':   ('modelId_200001042', './V13_V11_model/'),
    'V12 MOB1':  ('modelId_200001315', './V13_V12_mob1_model/'),
    'V12 MOB3':  ('modelId_200001313', './V13_V12_mob3_model/'),
    'V12额度系数': ('modelId_200001314', './V13_V12_edu_model/'),
}
```

#### 7-C-3. 头部客群子分

头部客群限定 ABC 评级:

```python
data_target['head_type'] = data_target.af_model_bin.apply(
    lambda x: 1 if x in ['A', 'A1', 'B', 'B1', 'C'] else 0
)
# 训练/测试样本额外过滤: head_type == 1
```

---

## 九、模型评估 (Step 3)

> 参考: `yanzhang1_data/V13开发/V13二次风控fpd31/二次风控fpd31评估.ipynb`
> 工具库: `yanzhang1_data/模型评估模版准备/Evaluate_style/styler_evaluate_tools.py`
> 底层依赖: `Evaluate_style/styler_model_evalution.py`

### 8.0 评估工具库路径与导入

```python
sys.path.append('/data/automl/yanzhang1/yanzhang1_data/模型评估模版准备/Evaluate_style')
from styler_evaluate_tools import *
```

该工具库提供完整的模型评估流水线，支持 **Notebook 内渲染** 和 **导出 HTML** 两种模式。

### 8.1 评估数据准备

评估前需拼合以下数据:

```python
# ── 1. 加载逾期标签 ──
delq_data = gdw(f"/data/public_data/.../delq_new_from23_fk_{date}.pt")
delq_data = delq_data[~delq_data.index.duplicated()]

# 派生金额逾期列 m1~m6 (用于 sloping)
for i in range(1, 7):
    delq_data[f'm{i}'] = np.where(delq_data[f'mob{i}_ripe_days'] >= 7,
                                   delq_data[f'mob{i}_principal_unpaid_7d'], np.nan)

# ── 2. 加载模型打分 (scores.pkl 或 predict) ──
all_result = []
for path in glob.glob('./models/*/scores.pkl'):
    df_sub = pd.read_pickle(path)
    df_sub = pd.DataFrame(df_sub, columns=[path.split('/')[-2]])
    all_result.append(df_sub)
all_result = pd.concat(all_result, axis=1)

# ── 3. 拼合所有数据 ──
com_ids = fcc(delq_data.index, all_result.index, 1)[1]
all_result = pd.concat([
    all_result.reindex(com_ids),
    delq_data.reindex(com_ids),
    # 可选: 加入旧版本模型分、评级、白户标签等对比维度
], axis=1)
```

### 8.2 评估变量定义

```python
# ── 基础标签别名 ──
m1 = 'is_mob1_pd7_delq'
m2 = 'is_mob2_pd7_delq'
m3 = 'is_mob3_pd7_delq'

# ── 需评估的模型分列表 ──
score_lst = ['V14子分模型A', 'V14子分模型B', 'V13子分模型(baseline)']

# ── 时间粒度 ──
period = 'week'  # 或 'month'

# ── AUC 评估的 target 列表 (支持多target) ──
auc_target_lst = [m1, m2, m3, 'is_fpd31']

# ── Sloping 评估的 target 列表 (金额维度, 字段值 = 逾期金额) ──
sloping_target_lst = ['m1', 'm2', 'm3']

# ── 分 bin ──
sloping_bin_name_lst = []   # 提前切好的 bin 列名 (recut=True 时可留空)

# ── Cross 风险: 自定义聚合函数 ──
def cross_func(sub_df, all_df):
    return pd.Series({
        "数量": sub_df.shape[0],
        "占比": sub_df.shape[0] / all_df.shape[0],
        '订单逾期率mob1_7': (sub_df.loc[sub_df[m1].notna(), m1] > 0).mean(),
        '订单逾期率mob2_7': (sub_df.loc[sub_df[m2].notna(), m2] > 0).mean(),
        '订单逾期率mob3_7': (sub_df.loc[sub_df[m3].notna(), m3] > 0).mean(),
        '金额逾期率mob1_7': sub_df.loc[sub_df['m1'].notna(),'m1'].sum() / sub_df.loc[sub_df['m1'].notna(),'principal'].sum(),
        '金额逾期率mob2_7': sub_df.loc[sub_df['m2'].notna(),'m2'].sum() / sub_df.loc[sub_df['m2'].notna(),'principal'].sum(),
        "平均成交金额（rmb）": sub_df['principal'].mean() / 2100,
        "平均期限": sub_df['terms'].astype(float).mean(),
        "额度使用率": sub_df['principal'].sum() / sub_df['info'].sum(),
    })
```

### 8.3 一键全流程评估 (推荐)

`generate_analysis_to_markdown` 一次调用包含全部分析模块:

```python
generate_analysis_to_markdown(
    df=all_result,
    score_lst=score_lst,
    period=period,
    auc_target_lst=auc_target_lst,
    sloping_target_lst=sloping_target_lst,
    cross_target_lst=['m1', 'm2', 'm3'],
    cross_index='评级_bin',          # cross 纵轴 (评级 bin 或已切好的模型分 bin)
    sloping_bin_name_lst=[],
    cross_score_lst=score_lst,
    cross_bin_name_lst=[],
    decision_trace='cl_type',        # 按决策流拆分 (可选, None 跳过)
    kequn_col='dataset',             # 按客群拆分 (可选, None 跳过)
    recut=True,                      # True=按各 target 自动等频切 bin
    nbins=10,
    need_fold=True,                  # Notebook 中折叠显示
    to_html=False,                   # True 则同时导出 HTML
    html_path='./eval_report.html',
)
```

此函数内部依次调用:
1. `generate_analysis_to_markdown_edd` — EDD 分析
2. `generate_analysis_to_markdown_performance` — 单分性能 (AUC/KS)
3. `generate_analysis_to_markdown_slopping` — 风险 Sloping
4. `generate_analysis_to_markdown_crossrisk` — Cross 交叉风险

### 8.4 分模块调用

也可按需单独调用各个模块:

#### 8.4.1 EDD 分析

```python
generate_analysis_to_markdown_edd(
    df=all_result,
    score_lst=score_lst,
    period=period,
    auc_target_lst=auc_target_lst,     # 可选，新版支持
    kequn_col='dataset',                # 可选
    need_fold=True,
    to_html=False,
    html_path=None,
)
```

输出内容:
- 1\. 样本量分布 (BY 月/周)
- 2\. 模型分 describe
- 3\. top10 取值分布
- 4\. BY 时间段平均值 (热力图着色)
- 5\. BY 时间段缺失率
- 6\. 相关性矩阵 (多模型时)

#### 8.4.2 单分性能 (AUC / KS)

```python
generate_analysis_to_markdown_performance(
    df=all_result,
    score_lst=score_lst,
    period=period,
    auc_target_lst=auc_target_lst,
    sloping_target_lst=sloping_target_lst,
    sloping_bin_name_lst=[],
    baseline_score='V13子分模型(baseline)',  # 基线模型 (计算 AUC-GAIN)
    decision_trace='cl_type',               # 按决策流拆分
    kequn_col='dataset',                    # 按客群拆分
    recut=True,
    nbins=10,
    need_fold=True,
    to_html=False,
    html_path=None,
)
```

输出内容:
- 1.1 全部 AUC (表格: target × model, 含 AUC-GAIN vs baseline)
- 1.2 全部 AUC by 客群
- 1.3 全部 AUC by 客群 × 决策流
- 2.1 BY 月/周 AUC (时间序列热力图)
- 2.2 BY 月/周 AUC by 客群
- 2.3 BY 月/周 AUC by 客群 × 决策流

#### 8.4.3 风险 Sloping

```python
generate_analysis_to_markdown_slopping(
    df=all_result,
    score_lst=score_lst,
    period=period,
    auc_target_lst=auc_target_lst,
    sloping_target_lst=sloping_target_lst,
    sloping_bin_name_lst=[],
    decision_trace='cl_type',
    kequn_col='dataset',
    recut=True,
    nbins=10,
    need_fold=True,
    to_html=False,
    html_path=None,
)
```

输出内容 (每个 score × target 组合):
- 金额逾期率 / 金额逾期倍数
- 订单逾期率 / 订单逾期倍数
- 平均成交金额 / 平均成交期限
- 可看人数
- 支持 by 客群、by 客群×决策流 拆分

#### 8.4.4 Cross 交叉风险

```python
# 先切 bin
for score in score_lst:
    all_result[f'{score}_bin'], _ = cut_score_bins(all_result[score], bins_num=10)

generate_analysis_to_markdown_crossrisk(
    df=all_result,
    cross_index='主模型_bin',                 # 纵轴 (评级或模型分 bin)
    cross_func=cross_func,                    # 自定义聚合函数
    cross_target_lst=['m1', 'm2', 'm3'],
    cross_score_lst=score_lst,
    cross_bin_name_lst=[f'{s}_bin' for s in score_lst],
    col_multi_col=['订单逾期率mob1_7', '金额逾期率mob1_7', ...],
    decision_trace='cl_type',
    kequn_col='dataset',
    recut=False,
    need_fold=True,
    to_html=False,
    html_path=None,
)
```

输出内容: 纵轴(评级/bin) × 横轴(模型分bin) 交叉表，含金额逾期/标的逾期/逾期倍数/首尾区分度汇总。

#### 8.4.5 稳定性分析 (PSI + 分布 + 分bin逾期率)

```python
results = generate_stability_analysis(
    df=all_result[all_result['dataset'] == 'cg'],
    score_col=score_lst,
    period_col=period,
    cross_func=cross_func,
    sloping_bin_name_lst=sloping_bin_name_lst,
    target_col=sloping_target_lst,
    psi_method='quantile',
    psi_bins=10,
    stability_bins=10,
    need_fold=True,
    to_html=False,
    html_path=None,
)
```

输出内容:
- 1\. PSI 矩阵 (每个时间段两两对比，多模型横向合并)
- 2\. 分布稳定性 (count/mean/std/median/Q1/Q3 按时间段展示)
- 3\. 按时间段的模型分 bin 逾期率 (使用 `cross_bin_slp`)
- 4\. 稳定性指标汇总 (多模型时: 平均PSI/最大PSI/PSI>0.25比例/均值标准差/均值范围)

### 8.5 工具函数速查

| 函数 | 来源 | 功能 |
|------|------|------|
| `generate_analysis_to_markdown()` | styler_evaluate_tools | 一键全流程 (EDD+性能+Sloping+Cross) |
| `generate_analysis_to_markdown_edd()` | styler_evaluate_tools | EDD: 样本量/describe/top10/均值/缺失率/相关性 |
| `generate_analysis_to_markdown_performance()` | styler_evaluate_tools | 单分性能: AUC/KS + AUC-GAIN + BY月分群分流 |
| `generate_analysis_to_markdown_slopping()` | styler_evaluate_tools | 风险Sloping: 金额逾期/订单逾期倍数 + 分群分流 |
| `generate_analysis_to_markdown_crossrisk()` | styler_evaluate_tools | Cross交叉风险: 纵横交叉表 + 首尾区分度 |
| `generate_stability_analysis()` | styler_evaluate_tools | 稳定性: PSI矩阵 + 分布统计 + 分bin逾期率 |
| `generate_analysis_to_markdown_yewu()` | styler_evaluate_tools | 业务指标: 多头/额度/给额率等自定义聚合 |
| `cut_score_bins()` | styler_model_evalution | 分位点/等频切bin |
| `evaluate_performance()` | styler_model_evalution | 单次KS+AUC计算(可选画图) |
| `generate_model_result()` | styler_model_evalution | 多score×多target的KS/AUC表格 |
| `generate_model_result_by_month()` | styler_model_evalution | 按月评估KS/AUC |
| `bin_sloping_risk()` | styler_evaluate_tools | 底层sloping计算 |
| `cross_risk_ly()` | styler_evaluate_tools | 底层cross风险pivot |
| `calculate_psi()` | styler_evaluate_tools | PSI计算 |

### 8.6 通用参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `score_lst` | list[str] | 需评估的模型分列名 |
| `period` | str | 时间分组列: `'week'` / `'month'` |
| `auc_target_lst` | list[str] | AUC 评估的 target 列名 (二值化: >0 为正) |
| `sloping_target_lst` | list[str] | Sloping 评估的 target (金额维度, 如 `'m1'`) |
| `baseline_score` | str/None | 基线模型分列名 (用于计算 AUC-GAIN) |
| `decision_trace` | str/None | 决策流分组列 (如 `'cl_type'`, `'baihu_type'`) |
| `kequn_col` | str/None | 客群分组列 (如 `'dataset'`) |
| `recut` | bool | True=按各target可看样本自动等频切bin; False=使用预切好的bin |
| `nbins` | int | 自动切bin数 (默认10) |
| `need_fold` | bool | Notebook中是否折叠显示 (复制到Excel建议False) |
| `to_html` | bool | 是否同时导出为HTML文件 |
| `html_path` | str | HTML输出路径 |
| `cross_func` | callable | Cross风险的自定义聚合函数 `f(sub_df, all_df) -> pd.Series` |

### 8.7 线上效果校验（Step 4 前置）

> 模型上线前必须通过线上回溯校验，确保离线训练结果与线上预测一致。

#### 验收标准

| 指标 | 通过标准 | 说明 |
|------|---------|------|
| 离线/线上 AUC 差异 | < 0.001 | 绝对值差异 |
| 离线/线上分数相关系数 | > 0.99 | Pearson 相关 |

#### V13 校验基线

| 模型 | 离线AUC | 线上AUC | DIFF | 相关系数 |
|------|---------|---------|------|---------|
| MOB1 一次 | 0.6626 | 0.6621 | -0.0005 | 0.994 |
| MOB3 一次 | 0.6451 | 0.6443 | -0.0008 | 0.997 |
| 免费前筛 | 0.6144 | 0.6143 | -0.0002 | 0.999 |
| 额度系数 | 0.6460 | 0.6461 | +0.0001 | 0.999 |
| 二次MOB1(含埋点) | 0.7032 | 0.7026 | -0.0006 | 0.997 |
| 二次FPD31(含埋点) | 0.6973 | 0.6971 | -0.0002 | 0.991 |

> V13 所有模型离线/线上 AUC 差异均 < 0.001，全部验证通过。

#### 校验未通过的排查方向

| 排查项 | 常见原因 |
|--------|---------|
| 特征一致性 | 线上 ETL 特征名映射错误、fea_new.txt 配置遗漏 |
| 缺失值处理 | 线上默认值填充与离线训练时不一致 |
| 数据穿越 | 线上使用了训练时未来信息（时间戳对齐问题） |
| 数据类型 | 线上 int/float 精度截断导致分数偏移 |
| 特征覆盖率 | 某些特征线上缺失率远高于离线（数据源未对接） |

---

## 十、模型上线 (Step 4)

参考: `yanzhang1_data/V13开发/模型上线.ipynb`

### 9.1 生成特征配置

```python
import numpy as np
from glob import glob

# 加载新旧特征名映射字典
feats_adv4OLDNEW_dict = np.load(
    "/data/public_data/gpu4/yonghaoduan/v11/feats_adv4OLDNEW_dict.npy",
    allow_pickle=True
).item()

# 模型路径
model_path = f"./models/{MODEL_NAME_STABLE}/"

# 读取模型使用的特征列表
sele = pd.read_csv(f'{model_path}/feature.txt', header=None)[0].tolist()
sele = [x.replace('___','.').replace('_loan_account_details_','_') for x in sele]

# 新旧特征名映射
sele_new = [feats_adv4OLDNEW_dict.get(x, x) for x in sele]

# 识别子模型分特征
feats_model = [x for x in sele if 'LOAN_RISK' in x]

# 生成 ETL 配置文件
feat_upload(sele, feats_model=feats_model, drop_fea=[])
# 输出: {model_path}/fea_new.txt, {model_path}/fea_old.txt
```

### 9.2 配置文件格式

`fea_new.txt` / `fea_old.txt` 为 TSV 格式，包含以下列：

| 列名 | 说明 |
|------|------|
| 索引 | 特征序号 |
| 向量名称 | ETL 中的特征名 (或 reserveFeature) |
| source | 数据源标识 (或 null) |
| 默认值 | 缺失时的填充值 |
| 类型 | FEATURE (普通特征) / MODEL (子模型分) |
| 入模分组 | 分组标识 |
| reshape规则 | 预处理规则 |
| bin分箱 | 分箱规则 |

### 9.3 上线 Checklist

- [ ] `feature.txt` 已从训练好的模型中导出
- [ ] `fea_new.txt` / `fea_old.txt` 已生成
- [ ] 线上回溯一致性校验通过
- [ ] 阈值切分 (`get_score_bins`) 已完成

---

## 十一、监控部署 (Step 5)

> 模型上线后需配置持续监控，及时发现模型衰减和数据异常。

### 11.1 监控脚本矩阵

| 脚本 | 监控维度 | 告警阈值 | 频率 |
|------|---------|---------|------|
| `idn_model_auc_alert.py` | AUC / KS | 7天 vs 前7天差 > ±0.03 | 日频 |
| `idn_model_psi_alert.py` | PSI | > 0.005 | 日频 |
| `idn_model_psi_avg_cov.py` | 覆盖率 / 均值 | 差 > 3% | 日频 |
| `idn_model_done_pass_mean_score_new.py` | 通过率 / 均值分 | 均值异常波动 | 日频 |
| `idn_model_mob_trace_rate.py` | 贷后表现 | MOB trace rate 异常 | 周频 |
| `idn_model_mob_unplay_rate_new.py` | 未复贷率 | unplay rate 异常 | 周频 |

### 11.2 告警阈值参考

| 指标 | 正常 | 警告 | 严重 |
|------|------|------|------|
| AUC 滑窗差值 | < 0.01 | 0.01 ~ 0.03 | > 0.03 |
| PSI | < 0.005 | 0.005 ~ 0.01 | > 0.01 |
| 特征覆盖率差异 | < 1% | 1% ~ 3% | > 3% |
| 模型分均值偏移 | < 2% | 2% ~ 5% | > 5% |

### 11.3 异常排查流程

```
告警触发
  ├─ AUC/KS 下降
  │   ├─ 检查近期数据源变更 (ETL上线/字段变动)
  │   ├─ 检查特征覆盖率是否下降
  │   ├─ 检查客群分布是否漂移 (评级/白户比例/产品结构)
  │   └─ 区分一次/二次风控分别排查
  ├─ PSI 异常
  │   ├─ 定位 PSI 贡献最大的特征
  │   ├─ 检查该特征的数据源是否有版本变更
  │   └─ 评估是否需要触发模型重训
  └─ 通过率/均值异常
      ├─ 检查策略规则是否有调整
      ├─ 检查客群准入条件是否变化
      └─ 检查模型分阈值是否被修改
```

### 11.4 监控部署 Checklist

- [ ] 6 个核心监控脚本已配置并验证数据产出
- [ ] 告警阈值已根据新版本模型分布调整
- [ ] 告警通知渠道已确认（邮件/IM）
- [ ] 首周已完成人工复核确认无误报

---

## 十二、模型命名规范

### Notebook命名

```
V{版本号}_{模型名}.ipynb
```

### 模型文件命名

```
v{版本号}_model_{缩写}[_sel][_stable][_wgt][_abc]
```

| 缩写 | 含义 |
|------|------|
| `toubu` | 头部客群 (A/B/C评级) |
| `D` | D评级客群 (D/E/F/G评级) |
| `md` | 埋点数据 |
| `td` | 同盾数据 |
| `sl` | 失联模型 |
| `zizhi` | 资质风险 |
| `dtfx` | 多头风险 |
| `dtzz` | 多头增长 |
| `hkje` | 还款金额 |
| `dhje` | 待还金额 |
| `yqts` | 逾期天数 |
| `cdyu` | 长短逾 |
| `cyh` | 差异化 |
| `edbd` | 额度变化 |
| `stfx` | XGB双塔-下单率风险 (变体A) |
| `stmx` | XGB双塔-风险额度 (变体B) |
| `rc` | 前置C卡(入催模型) |
| `img` | 图像子分 |
| `lishi` | 历史子分 |
| `tbkq` | 头部客群子分 |
| `tanx` | 弹性模型 |
| `scfx` | 生存分析子分 |
| `zheng` | 蒸馏子分 |
| `jeyq` | 金额逾期模型 |
| `sel` | 特征重要性筛选版 |
| `stable` | 经稳定性流水线筛选的最终版 |
| `wgt` | 使用样本权重 |
| `samp0_xxx` | 前置C卡抽样比例 |
| `abc` / `defg` | 评级分组 |

---

## 十三、客群与标签定义

### 客群

| 客群 | af_model_bin | 适用模型 |
|------|-------------|---------|
| 头部 | A, A1, B, B1, C | 头部长期、头部短期 |
| D评级 | D, D1, E, E1, F, G | D评级短期、D评级长期 |
| 全量 | 不筛选 | 埋点、失联、同盾、资质等通用子分 |
| 前置C卡 | 不筛选 + is_mob1_pd1_delq=1 | 仅入催用户 |

### 标签完整一览

| 标签名 | 定义 | objective | 适用模型 |
|--------|------|-----------|---------|
| `mob1_label7` | mob1成熟(≥7天)是否pd7逾期 | binary | 埋点/前置C卡/失联/XGB双塔变体A(塔1) |
| `mob2_label7` | mob2成熟 pd7逾期 | binary | 同盾/多头风险/图像 |
| `mob3_label7` | mob3成熟 pd7逾期 | binary | 资质风险 |
| `label_180` | 180天观察期逾期标签 | binary | 同盾 |
| `label1` | 长短逾分类(长=1,短=0) | binary/tweedie | 长短逾/差异化 |
| `shilian` | 失联标签(1=失联,0=未失联,-1=无标签) | binary | 失联 |
| `paid_principal_sum_180d` | 180天已还本金 | tweedie | 还款金额预测 |
| `principal_unpaid_180d` | 180天待还本金 | tweedie | 待还金额预测 |
| `info_edu_ratio_180d` | 180天额度变化率 | tweedie | 额度变化预测 |
| `tweedie_target` | 多头增长delta | tweedie | 多头增长 |
| `tixian` | 下单/转化率 | binary | XGB双塔变体A(塔2) |
| `quota_rate_label` | 额度率 (principal>=info → 1) | binary | XGB双塔变体B(塔2) |
| `逾期天数` | 实际逾期天数(连续值) | regression | 逾期天数预测 |
| `label_13` | 弹性标签: MOB1好→MOB3坏 | binary | 弹性模型 |
| `label_36` | 弹性标签: MOB3好→MOB6坏 | binary | 弹性模型 |
| `aft_label` / `aft_upper` | AFT区间删失标签 (首逾MOB期数) | survival:aft | 生存分析子分 |
| `modelId_200001042` 等 | Teacher模型打分(V11/V12) | regression(rmse) | 蒸馏子分 |
| `w_amt_m1` | 金额加权标签 (本金*逾期额加权) | binary(加权) | 金额逾期模型 |
| `is_fpd31` | fpd31逾期标签 | binary | 二次风控FPD31 |
| `is_mob1_pd1_delq` | mob1首日逾期(入催标记) | — | 前置C卡样本筛选用 |

---

## 十四、稳定性分析产出目录

```
stability_analysis/{MODEL_NAME}/
├── woe/
│   ├── woe_stability_report.csv    # 每个特征: iv, corr, status
│   └── woe_stable_vars.json        # 稳定特征名列表
├── psi/
│   └── psi_stability_report.csv    # 每个特征: psi, status
├── permutation/
│   └── permutation_importance.csv  # 每个特征: importance_mean, std
├── subscore/                       # 仅融合模型
│   └── subscore_ablation.csv
└── pipeline_summary.json           # 流水线汇总
```

---

## 十五、版本迭代 Checklist

### 版本架构设计
- [ ] 确定本版本双Y值策略（参考第三章模板）
- [ ] 确定训练窗口 / OOT窗口 / 样本拆分比例
- [ ] 确定融合策略（不同Y值的样本约束）
- [ ] 确认特征筛选管线已完成（宽表级：原始特征 → 粗筛特征）

### 数据准备
- [ ] 确认新版本统一建模宽表已产出
- [ ] 确认新版本 delq 数据已更新
- [ ] 确认新版本样本拆分表已产出 (df_sample_type)
- [ ] 确认新版本 flow_id 已确定
- [ ] 确认模型特有的额外数据已更新 (失联标签/180d标签/ovd标签等)

### 模型开发 (每个子模型)
- [ ] 创建 V{版本号}开发/{模型名}/ 目录
- [ ] 生成 notebook (AI根据模型配置注册表自动生成 Sections 2-8)
- [ ] Review 自动生成的代码, 确认数据路径和参数
- [ ] 执行 S1-S4: 数据加载 + 样本定义
- [ ] 执行 S5: 确认特征集
- [ ] 执行 S6.1: 全量特征初筛训练 (2000轮, ES=100)
- [ ] 执行 S6.2: 特征重要性筛选 (perc>0.03)
- [ ] 执行 S6.3: 筛选特征再训练 (2000轮, ES=100)
- [ ] 执行 S7: 运行稳定性分析流水线
- [ ] 执行 S6.5: 最终版训练 (5000轮, ES=100)
- [ ] 执行 S8: 模型评估 (AUC/KS/sloping)
- [ ] 检查 stability_analysis/ 产出报告

### 前置C卡 (标准流程，附加好样本抽样)
- [ ] 确认样本拆分表 (`df_sample_type`) 已更新
- [ ] 确认线上模型分数据 (`modelId_200001042`) 可用
- [ ] 构建入催训练集 + 好样本抽样 (比例需实验: 1.1%/1.6%/3.3%)
- [ ] 多个抽样比例对比评估 (入催OOT + 全量OOT)
- [ ] 最优模型 + 线上模型分浅层融合 (可选)

### 模型评估
- [ ] 各子分集体打分
- [ ] OOT AUC/KS 评估
- [ ] 与上一版本 baseline 对比
- [ ] 逾期率/逾期倍数校验
- [ ] 完成增益归因分析（vs 上一版本，拆解增益来源）

### 模型上线
- [ ] 导出 feature.txt
- [ ] 生成 fea_new.txt / fea_old.txt (feat_upload)
- [ ] 线上回溯校验通过（AUC 差 < 0.001, 相关系数 > 0.99）
- [ ] 阈值切分 (get_score_bins)
- [ ] 更新线上模型ID映射表（第四章 3.3 节）

### 模型监控
- [ ] 配置 6 个核心监控脚本（参考第十一章）
- [ ] 确认告警阈值已根据新版本分布调整
- [ ] 验证监控数据产出
- [ ] 首周人工复核确认无误报

---

## 十六、工具函数参考

训练流程依赖以下两个工具包：

### tools (yonghaoduan)

路径: `/data/public_data/gpu4/yonghaoduan/easycash_yh/src/utils/tools.py`

| 函数 | 用途 |
|------|------|
| `gdw(path)` | 加载 parquet/pickle/feather 数据, 自动设置 loan_account_id 为 index |
| `fcc(idx1, idx2, ret_col=False)` | 取两个 index 的交集, 返回 (intersect, common_ids) |
| `gfr(model_path, key=None)` | 从已训练的LGB模型中提取特征重要性 DataFrame |
| `etlName_replace(cols)` | 将 ETL 列名标准化 (去除前缀, 统一格式) |
| `feat_upload(sele, feats_model, drop_fea)` | 生成上线用的 fea_new.txt / fea_old.txt |
| `rut` | 变量, 值为 `'risk_usertype'`, 用于 query 字符串中 |

### tools_zy (yanzhang1)

路径: `/data/public_data/cpu4/yanzhang1/tools_zy/`

| 模块 | 关键函数 | 用途 |
|------|---------|------|
| `lgb_train_tools_zy` | `train_lgbm_principal(...)` | 主训练函数 (含 principal 校正) |
| | `train_lgbm_simple(...)` | 简化训练函数 |
| | `train_lgbm_wcem(...)` | 加权交叉熵训练 |
| `model_containers` (mc) | `evaluate_performance_v3(...)` | 模型评估 (AUC/KS/sloping) |
| | `KS_AUC_v2(list_df_config)` | 批量 KS/AUC 计算 |
| | `sloping_v2(list_df_config)` | 批量逾期率分层 |
| | `show_woe_stats(...)` | WOE 分箱可视化 |
| | `get_score_bins(...)` | 分数分箱/阈值切分 |
| `model_evalution` | 模型评估辅助 | |
| `eval_slopping_tools` | Sloping 分析 | |
| `feature_vlm_plot` (fmp) | 特征 VLM 可视化 | |
| `toolkit_zy` (tk) | `woe_tools_lw_new` (wt) | WOE 分析工具 |

### Evaluate_style (模型评估报告工具)

路径: `/data/automl/yanzhang1/yanzhang1_data/模型评估模版准备/Evaluate_style/`

> 注意: 此路径下的版本比 `tools_zy/Evaluate_style/` 更新，新增了 `generate_analysis_to_markdown_slopping`、`generate_stability_analysis`、`baseline_score`/`AUC-GAIN`、`kequn_col`/`decision_trace` 分群分流等功能。

| 文件 | 关键函数 | 用途 |
|------|---------|------|
| `styler_evaluate_tools.py` | `generate_analysis_to_markdown()` | 一键全流程 (EDD+性能+Sloping+Cross) |
| | `generate_analysis_to_markdown_edd()` | EDD: 样本量/describe/top10/均值/缺失率/相关性 |
| | `generate_analysis_to_markdown_performance()` | 单分性能: AUC/KS/AUC-GAIN + BY月 + by客群×决策流 |
| | `generate_analysis_to_markdown_slopping()` | 风险Sloping: 金额/订单逾期倍数 + by客群×决策流 |
| | `generate_analysis_to_markdown_crossrisk()` | Cross交叉风险: 纵横交叉表 + 首尾区分度 |
| | `generate_stability_analysis()` | 稳定性: PSI矩阵 + 分布统计 + 分bin逾期率 |
| | `generate_analysis_to_markdown_yewu()` | 业务指标: 自定义聚合 (多头/额度/给额率等) |
| | `cut_score_bins()` | 分位点切bin (等频/自定义cutoff) |
| | `bin_sloping_risk()` | 底层sloping计算 (金额/标的逾期率) |
| | `cross_risk_ly()` | 底层cross风险pivot表 |
| | `calculate_psi()` | PSI计算 (quantile/等距) |
| | `colour_cross()` | cross结果着色 |
| `styler_model_evalution.py` | `evaluate_performance()` | 单次KS+AUC (可选画ROC曲线) |
| | `generate_model_result()` | 多score×多target KS/AUC表格 |
| | `generate_model_result_by_month()` | 按月评估KS/AUC |
| | `get_score_bins()` | 分数切bin |
| | `calc_vintage()` | Vintage (金额逾期率/标的逾期率) |
| | `var_vintage()` | 按变量分组的Vintage |

### 标准 imports

```python
import sys
sys.path.append('/data/public_data/gpu4/yonghaoduan/easycash_yh/src/utils')
sys.path.append('/data/public_data/cpu4/yanzhang1/tools_zy')
sys.path.append('/data/public_data/cpu4/yanzhang1/tools_zy/Evaluate_style')

from tools import *
from lgb_train_tools_zy import *
from model_evalution import *
import model_containers as mc
from eval_slopping_tools import *
from data_tools import *
import toolkit_zy as tk
from toolkit_zy import woe_tools_lw_new as wt
import feature_vlm_plot as fmp

# ── 模型评估报告工具 (推荐使用更新版本) ──
sys.path.append('/data/automl/yanzhang1/yanzhang1_data/模型评估模版准备/Evaluate_style')
from styler_evaluate_tools import *
```

---

## 十七、常见问题

### Q: 新版本特征数与旧版本不同？
A: 使用 `all_vars = df_master.columns.tolist()` 自动获取。特征筛选环节自动处理。

### Q: 旧模型的 feature 在新宽表中不存在？
A: 加载旧模型进行 baseline 对比时先检查特征覆盖度：
```python
gbm = lgb.Booster(model_file='old_model.model')
missing = [x for x in gbm.feature_name() if x not in df_master.columns]
```

### Q: 稳定性流水线很慢怎么办？
A: 特征消融 (Permutation Importance) 是最耗时的步骤。可以调整参数：
- 减少 `n_repeats` (默认5, 可改为3)
- 减少 `max_samples` (默认150000)
- 仅对 `psi_stable_vars` 做消融 (流水线已自动串联)

### Q: 如何让AI自动生成迭代代码？
A: 按照第四章"AI协作接口"的格式, 提供模型名称/X表/Y表/标签/额外数据/OOT起始等信息。AI会参照本SOP中的模型配置注册表和代码模板, 自动生成完整的 Sections 2-8 代码。

### Q: 训练集时间窗口如何确定？
A: 训练起始固定 2023-07-01 (数据完整性起点), 截止日期为 OOT 起始日期。验证集使用 bf_oos_idx (外部样本拆分表)。

### Q: 模型类型选择 (binary vs tweedie vs regression)？
A: 根据标签性质:
- 0/1 分类标签 → binary (AUC评估)
- 连续非负金额/比率 → tweedie (RMSE评估)
- 连续天数 → regression (L2评估)

### Q: 前置C卡的好样本抽样比例如何选择？
A: 前置C卡使用标准 LGB 流程，唯一区别是训练样本需要抽样好样本。通常从 3.3% (≈1:10), 1.6% (≈1:20), 1.1% (≈1:30) 开始实验。关注入催 OOT 上的 AUC/KS, 同时兼顾全量 OOT 表现。一般 1.1% 附近效果较好，但每次迭代建议重新实验确认。

### Q: 前置C卡为什么不用时间切分验证集？
A: 因为入催样本量有限且分布随时间波动较大。使用外部样本拆分表 (df_sample_type) 的 ins/oos 划分可以保证分布一致。

### Q: 前置C卡的正则化为什么比标准模型强很多？
A: 入催样本 target rate 极高, 模型容易过拟合。强正则化 (reg_alpha=60, reg_lambda=80) 约束复杂度。参数来自 Optuna 调优。注意前置C卡是标准流程模型，只是超参数更偏向强正则化。

### Q: 融合模型的子分消融如何启用？
A: 设置 `run_subscore=True` 并传入 `sub_list`:
```python
sub_list = [col for col in df_master.columns if 'LOAN_RISK' in col]
pipeline_result = run_stability_pipeline(..., sub_list=sub_list, run_subscore=True)
```

### Q: 同盾子分为什么使用两段式训练集？
A: 因为 label_180 需要180天成熟期, 早期数据量大但无 ins/oos 拆分, 故 2024-08 前全量进训练集, 2024-08 后仅 ins 进训练集。

### Q: XGB双塔变体A 的 rut 值为什么不同？
A: XGB双塔变体A (下单率风险双塔) 的 `rut` 值为 `'Android'` 而非其他模型的 `'安卓'`, 需在 query 中使用 `('Android', 'IOS')`。变体B 使用标准的 `'安卓'`/`'IOS'`。

### Q: 特征筛选后数量断崖式下降或 AUC 异常怎么排查？
A: 这是 V14 头部长期模型训练中实际遇到的问题，根本原因和排查步骤如下：

**典型症状**: 3537 维全量特征 → 筛选后仅剩不到 100 个；或筛选模型 AUC 远低于初筛模型。

**排查清单**:
1. **模型保存路径冲突**: `train.train_lgb_model` 在目标目录已有模型时自动改名为 `_copy_1`。若 `gfr()` 仍读取旧路径，则读到的是旧模型（可能用了错误的训练集或更少的样本），导致特征重要性分布完全不同。→ 检查 `gfr()` 路径与实际模型保存路径是否一致。
2. **训练集定义错误**: 若误用 `bf_ins_idx` 取交集（而非 `not in @bf_oos_idx` 剔除），可能丢失大量样本。→ 检查 `len(train_idx)` 是否符合预期。
3. **标签列引用错误**: 如用 `label1` 替代 `mob3_label7`，或样本过滤条件中标签名不一致。→ 检查 `TARGET_COL` 变量和 query 中的标签名。

**处理流程**: 发现异常后，不要继续执行后续 cell，先回溯检查 cell 4-13 的定义和输出，确认 train_idx、TARGET_COL、MODEL_DIR 等核心变量的值是否正确。

### Q: 每次版本迭代的增益主要来自哪里？
A: 根据 V13 经验，增益来源优先级为：**样本拉新 > 特征增量 > 模型架构优化**。V13 最大增益（+0.6pp）来自 OOT 延长 2.5 个月的样本拉新。每次迭代应优先确认数据时间窗口是否充分拉新，再考虑新增特征和架构调整。

### Q: 子分模型入模比例通常多高？
A: V13 共开发 130 个子分，78 个入模，入模率约 60%。历史子分数量最多（74个）但入模率较低（约 43%），而弹性模型（+2.7pp）和流入系列（+4.7pp）增益最高。建议优先开发高增益类别，历史子分可选择性开发。

### Q: 线上校验的验收标准是什么？
A: 离线 AUC 与线上 AUC 差异 < 0.001，离线/线上分数相关系数 > 0.99。V13 所有模型（一次+二次共6个）均满足此标准。校验未通过时，按以下优先级排查：特征一致性 → 缺失值处理 → 数据穿越 → 数据类型精度。详见第九章 8.7 节。

### Q: 版本迭代周期和节奏是怎样的？
A: 约每 3 个月一次大版本迭代。典型节奏：第 1 月完成架构设计+数据准备+子分开发；第 2 月完成评估+上线+校验；第 3 月监控稳定性并规划下一版本。
