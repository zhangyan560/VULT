---
title: "Uplift因果推断方法论"
tags: [方法论/因果推断, Uplift]
date: 2026-04-09
---

# Uplift因果推断方法论

## 一、Uplift建模核心概念

### 1.1 四象限用户分类

Uplift建模的核心目标不是预测"谁会转化"，而是预测"干预对谁有增量效果"。用户按是否干预(Treatment/Control)和是否转化(Y=1/Y=0)，可分为四类：

| 用户类型 | 干预后转化 | 不干预也转化 | 干预效果 | 最优策略 |
|---------|----------|-----------|---------|---------|
| **Persuadables（可说服）** | Y=1 | Y=0 | 正向 | 必须干预 |
| **Sure Things（必然转化）** | Y=1 | Y=1 | 零 | 无需干预（节省成本） |
| **Lost Causes（无药可救）** | Y=0 | Y=0 | 零 | 无需干预 |
| **Sleeping Dogs（反效果）** | Y=0 | Y=1 | 负向 | 绝不干预 |

**关键洞察**：传统响应模型（Response Model）混淆了 Persuadables 和 Sure Things，因为两者干预后都转化。Uplift模型的价值在于区分这两类用户，只对 Persuadables 投入资源。

### 1.2 CATE估计

**CATE（Conditional Average Treatment Effect）** 是Uplift建模的核心估计目标：

```
CATE(x) = E[Y(1) - Y(0) | X = x]

其中：
- Y(1): 干预条件下的潜在结果
- Y(0): 未干预条件下的潜在结果
- X: 用户特征向量
```

**根本困难（因果推断的基本问题）**：对于每个用户，我们只能观察到一个潜在结果（要么被干预，要么未被干预），另一个是反事实（counterfactual），永远无法直接观测。所有Uplift方法本质上都是在估计这个不可观测的反事实。

### 1.3 ATE与ITE

| 概念 | 定义 | 层级 |
|------|------|------|
| ATE（Average Treatment Effect） | E[Y(1) - Y(0)]，总体平均效应 | 群体 |
| CATE | E[Y(1) - Y(0) \| X=x]，条件平均效应 | 子群体 |
| ITE（Individual Treatment Effect） | Y_i(1) - Y_i(0)，个体效应 | 个体 |

实际建模中，ITE不可直接估计（因果推断基本问题），我们估计的是CATE作为ITE的近似。

---

## 二、Meta-Learner方法对比

### 2.1 S-Learner（Single Model）

**原理**：将Treatment指示变量T作为一个特征，与其他特征X一起输入单一模型。

```
训练：f(X, T) -> Y
预测：CATE(x) = f(x, T=1) - f(x, T=0)
```

**代码模板**：
```python
import lightgbm as lgb

# 将treatment作为特征
train_features = pd.concat([X_train, T_train.rename('treatment')], axis=1)
model = lgb.LGBMClassifier().fit(train_features, y_train)

# 预测CATE
X_t1 = X_test.copy(); X_t1['treatment'] = 1
X_t0 = X_test.copy(); X_t0['treatment'] = 0
cate = model.predict_proba(X_t1)[:, 1] - model.predict_proba(X_t0)[:, 1]
```

**优点**：简单，只需训练一个模型
**缺点**：当Treatment效应相对于基线转化率较小时，模型倾向于忽略Treatment变量（正则化将其系数压向0）

**适用场景**：Treatment效应较大、样本量充足

### 2.2 T-Learner（Two Models）

**原理**：对Treatment组和Control组分别训练独立模型，差值即为CATE。

```
训练：
  mu_1(X) = E[Y | X, T=1]    # Treatment组模型
  mu_0(X) = E[Y | X, T=0]    # Control组模型

预测：
  CATE(x) = mu_1(x) - mu_0(x)
```

**代码模板**：
```python
# 分别训练两个模型
model_t = lgb.LGBMClassifier().fit(X_train[T==1], y_train[T==1])
model_c = lgb.LGBMClassifier().fit(X_train[T==0], y_train[T==0])

# 预测CATE
cate = model_t.predict_proba(X_test)[:, 1] - model_c.predict_proba(X_test)[:, 1]
```

**优点**：
- Treatment效应和基线效应完全解耦
- 两组可以使用不同的特征或超参数
- 实现简单，易于理解和调试

**缺点**：
- 需要两倍训练成本
- 当两组样本量差异大时，小样本组模型不稳定
- 没有利用两组数据的共享信息

**适用场景**：Treatment组和Control组的特征-响应关系差异较大，两组样本量相对均衡

**运营Uplift场景选择T-Learner的原因**：
1. WA推送的Treatment效应（额外放款率提升约3%）相对于基线放款率较小，S-Learner容易忽略
2. 实现简单，便于快速迭代和调试
3. 两个模型可以独立解释，便于业务理解

### 2.3 X-Learner

**原理**：在T-Learner基础上引入反事实估计步骤，利用两组数据的交叉信息提高估计精度。

```
Step 1: 基础模型训练（同T-Learner）
  mu_0(X) = E[Y | X, T=0]
  mu_1(X) = E[Y | X, T=1]

Step 2: 伪个体处理效应（Imputed ITE）
  D_1 = Y_1 - mu_0(X_1)    # Treatment组的伪ITE
  D_0 = mu_1(X_0) - Y_0    # Control组的伪ITE

Step 3: 二阶模型训练
  tau_1(X) = E[D_1 | X]    # 用Treatment组数据训练
  tau_0(X) = E[D_0 | X]    # 用Control组数据训练

Step 4: 加权融合
  CATE(x) = g(x) * tau_0(x) + (1 - g(x)) * tau_1(x)
  其中 g(x) = P(T=1|X=x) 即倾向得分
```

**代码模板**：
```python
# Step 1: 基础模型
model_0 = lgb.LGBMRegressor().fit(X[T==0], y[T==0])
model_1 = lgb.LGBMRegressor().fit(X[T==1], y[T==1])

# Step 2: 伪ITE
d1 = y[T==1] - model_0.predict(X[T==1])     # Treatment组反事实差
d0 = model_1.predict(X[T==0]) - y[T==0]     # Control组反事实差

# Step 3: 二阶模型
tau_1 = lgb.LGBMRegressor().fit(X[T==1], d1)
tau_0 = lgb.LGBMRegressor().fit(X[T==0], d0)

# Step 4: 加权融合（g为倾向得分）
propensity = lgb.LGBMClassifier().fit(X, T).predict_proba(X_test)[:, 1]
cate = propensity * tau_0.predict(X_test) + (1 - propensity) * tau_1.predict(X_test)
```

**优点**：
- 比T-Learner更高效地利用数据（交叉使用两组信息）
- 在Treatment/Control比例不均衡时表现更好
- 理论上估计精度更高

**缺点**：实现复杂，多步骤误差累积

**适用场景**：Treatment和Control样本量不均衡、需要更精确的效应估计

### 2.4 方法选型指南

| 条件 | 推荐方法 | 原因 |
|------|---------|------|
| 样本量大、两组均衡、快速迭代 | T-Learner | 简单稳健 |
| 样本量大、效应大 | S-Learner | 最简单 |
| 两组不均衡、需高精度 | X-Learner | 交叉估计更准 |
| 需差异化定价、多Treatment水平 | X-Learner | 反事实估计灵活 |

---

## 三、样本设计方法论

### 3.1 人天粒度设计

运营触达场景（如WA推送）的样本粒度应与推理场景一致：

```
推理场景：每天早上跑批，对每个用户决定"今天是否发WA"
样本粒度：人天（person-day），即 (user_id, date) 为一条样本

而非：
- 人级（person）：丢失了时间维度，无法捕捉"什么时候发更有效"
- 事件级（event）：过于细粒度，与跑批决策不匹配
```

### 3.2 对照组选择

对照组的选择直接决定因果效应估计的有效性：

| 对照组类型 | 是否可用 | 原因 |
|-----------|---------|------|
| 随机全局Holdout | 可用（推荐） | 随机分配，无选择偏差 |
| AB实验空白组 | 可用 | 随机分配 |
| 频控未发WA的用户 | **不可用** | 选择偏差：频控规则与用户特征相关 |
| 规则拦截未发WA的用户 | **不可用** | 系统性差异：被拦截用户本身就不同 |

**核心原则**：对照组必须是**随机分配**的，而非因为某种规则或条件而"恰好"没有被干预的用户。后者存在选择偏差，会导致CATE估计有偏。

### 3.3 同一用户跨期的处理

在人天粒度下，同一用户可能在不同日期分别出现在Treatment组和Control组：

```
用户A：
  Day 1: T=1（发了WA）--> 属于Treatment样本
  Day 5: T=0（在Holdout中）--> 属于Control样本
  Day 8: T=1（发了WA）--> 属于Treatment样本
```

**处理策略**：

1. **允许跨期贡献**：同一用户可以同时贡献Treatment和Control样本
2. **静默窗口隔离**：两次干预之间需要足够的间隔（如3-7天），避免前次干预的残留效应污染后次的对照
3. **历史干预特征化**：将"历史WA接收次数"、"距上次WA间隔天数"作为特征输入模型，让模型自适应学习累积效应

```python
# 静默窗口处理
SILENCE_WINDOW = 3  # 天

for user in users:
    events = sorted(user.wa_events, key=lambda e: e.date)
    for i, event in enumerate(events):
        if i > 0:
            gap = (event.date - events[i-1].date).days
            if gap < SILENCE_WINDOW:
                event.exclude = True  # 排除距上次干预过近的样本
```

### 3.4 WA归因原则（末次归因）

当一个用户在观察窗口内被多次干预时，需要明确的归因规则：

**末次归因规则**（Last Touch Attribution）：

```
优先级链：
  已读 > 发送成功 > 请求发送

具体规则：
1. 如果有已读记录 --> 归因到最近一次已读的WA
2. 如果无已读但有发送成功 --> 归因到最近一次发送成功的WA
3. 如果仅有请求发送 --> 归因到最近一次请求发送的WA
4. 未归因的WA --> 强制 Y=0（不可丢弃）
```

**关键设计**：未归因的WA样本必须保留为Y=0，**不可丢弃**。如果丢弃这些样本，相当于只保留"有效触达"的样本，会系统性高估触达效果。

---

## 四、目标变量设计

### 4.1 Y1主目标：T+N放款 x 金额加权

```
Y1 = I(T+N内是否放款) * amount_weight

其中：
- I(): 指示函数，T+N天内放款则为1
- N: 观察窗口，通常取 T+1（次日）或 T+3（3日内）
- amount_weight: 金额归一化权重
```

**金额加权的原因**：
- 业务目标是放款金额最大化，而非放款人数最大化
- 放100万和放10万的用户价值不同
- 金额加权让模型更关注高价值用户的转化

```python
# 金额加权Y值计算
def compute_y1(row, window_days=3):
    """T+N放款 x 金额加权"""
    if row['payout_within_N_days']:
        return row['payout_amount'] / AMOUNT_NORMALIZER
    return 0.0
```

**T+1 vs T+3的选择**：
- T+1：响应更快、信号更纯，但可能遗漏"犹豫型"用户
- T+3：覆盖更全，但引入更多噪声（3天内的其他影响因素）

### 4.2 Y2辅助目标：回归

```
Y2 = sum(表现期内放款金额)    # 连续值回归目标
```

Y2用回归方式直接预测放款金额，与Y1互补：
- Y1关注"是否转化"（分类）
- Y2关注"转化多少"（回归）
- 最终可以将Y1和Y2的模型分联合使用

---

## 五、X-Learner在定价场景的应用

### 5.1 费率敏感模型的X-Learner实践

在差异化定价场景中，X-Learner用于估计"降低费率对用户下单率的增量影响"：

```
Treatment: 降低费率/调整期限组合
Control: 维持原有费率
Y: 是否下单

CATE(x) = P(下单 | 降费, X=x) - P(下单 | 不降费, X=x)
```

**X-Learner的步骤（定价场景）**：

```python
# Step 1: 用Control组训练基础模型
mu_0 = lgb.LGBMClassifier().fit(X_control, y_control)  # 不降费下的下单模型

# Step 2: 用Treatment组训练基础模型
mu_1 = lgb.LGBMClassifier().fit(X_treatment, y_treatment)  # 降费下的下单模型

# Step 3: 用mu_0预测Treatment组的反事实
# "如果这些降费用户没有降费，他们的下单率是多少？"
d1 = y_treatment - mu_0.predict_proba(X_treatment)[:, 1]

# Step 4: 用mu_1预测Control组的反事实
# "如果这些没降费的用户降了费，他们的下单率是多少？"
d0 = mu_1.predict_proba(X_control)[:, 1] - y_control

# Step 5: 训练二阶效应模型
tau_1 = lgb.LGBMRegressor().fit(X_treatment, d1)
tau_0 = lgb.LGBMRegressor().fit(X_control, d0)

# Step 6: 融合
cate = g * tau_0.predict(X_new) + (1 - g) * tau_1.predict(X_new)
```

### 5.2 因果推断用于差异化定价

费率敏感模型的输出不是单独使用的，而是与意愿模型配合形成定价策略：

```
┌─────────────────────────────────┐
│     意愿双塔模型                  │
│  (下单意愿 x 风险)               │
│                                 │
│  输出：高意愿 / 中意愿 / 低意愿    │
└──────────┬──────────────────────┘
           │
           v
┌─────────────────────────────────┐
│     费率敏感模型（X-Learner）      │
│                                 │
│  在每个意愿层内，识别：             │
│  - 高敏感用户 --> 提供优惠费率      │
│  - 低敏感用户 --> 维持标准费率      │
└──────────┬──────────────────────┘
           │
           v
    差异化定价执行
```

**决策矩阵**：

| 意愿水平 | 费率敏感度 | 策略 |
|---------|----------|------|
| 高意愿 | 不敏感 | 标准费率（本来就会下单） |
| 高意愿 | 高敏感 | 适度优惠（锦上添花） |
| 中意愿 | 高敏感 | 大力优惠（核心目标用户） |
| 中意愿 | 不敏感 | 标准费率 |
| 低意愿 | - | 不干预（成本收益不划算） |

### 5.3 多Treatment水平

费率定价天然是多Treatment水平场景（不同利率/期限组合）。X-Learner可以扩展为：

```
# 多Treatment: 不同的费率优惠幅度
treatments = ['base_rate', 'rate_minus_10pct', 'rate_minus_20pct', 'rate_minus_30pct']

# 对每对(treatment, control)估计CATE
for t in treatments[1:]:
    cate_t = estimate_xlearner(X, y, T=(treatment==t), C=(treatment=='base_rate'))
```

---

## 六、评估方法

### 6.1 Qini曲线

Qini曲线是Uplift模型的标准评估工具，类似于ROC曲线：

```
X轴：按Uplift预测值从高到低排序，累积处理的用户比例
Y轴：累积增量效应 = (n_t1 * Y_t1 / N_t) - (n_c1 * Y_c1 / N_c)

其中：
- n_t1: 前x%用户中Treatment组的转化数
- Y_t1: Treatment组转化率
- N_t: Treatment组总人数
- n_c1, Y_c1, N_c: Control组对应值
```

**解读**：Qini曲线越高越好。如果模型有效，对排序靠前的用户进行干预的增量效应应显著大于随机选择。

### 6.2 AUUC（Area Under Uplift Curve）

```
AUUC = 曲线下面积 / 完美模型下面积

AUUC范围：
- = 1.0: 完美模型
- = 0.5: 随机模型（等同于不做Uplift）
- < 0.5: 模型有害（不如随机选择）
```

### 6.3 Lift对比

按Uplift预测值分桶（如10分位），计算每个桶内的实际增量效应：

```python
def uplift_by_decile(y_treatment, y_control, uplift_score, n_bins=10):
    """按Uplift分数分桶，计算每桶的实际增量"""
    bins = pd.qcut(uplift_score, n_bins, labels=False)
    results = []
    for b in range(n_bins):
        mask = bins == b
        treat_rate = y_treatment[mask & (T==1)].mean()
        control_rate = y_control[mask & (T==0)].mean()
        actual_uplift = treat_rate - control_rate
        results.append({
            'decile': b,
            'treatment_rate': treat_rate,
            'control_rate': control_rate,
            'actual_uplift': actual_uplift,
            'predicted_uplift': uplift_score[mask].mean()
        })
    return pd.DataFrame(results)
```

**理想结果**：
- 头部桶（预测Uplift高）：实际增量效应显著为正
- 尾部桶（预测Uplift低或负）：实际增量效应为零或为负
- 预测值和实际值的排序一致性高

### 6.4 校准曲线

检验模型预测的Uplift值是否与实际增量效应匹配：

```python
# 校准检验
predicted_uplift_bins = pd.qcut(predicted_uplift, 20)
calibration = pd.DataFrame({
    'predicted': predicted_uplift.groupby(predicted_uplift_bins).mean(),
    'actual': actual_uplift.groupby(predicted_uplift_bins).mean()
})
# 理想情况下 predicted ≈ actual
```

### 6.5 评估注意事项

1. **必须有真实的随机对照组**：没有随机分配的Control组，所有评估指标都不可信
2. **样本量要求**：Uplift效应通常比直接效应小一个数量级，需要更大的样本量才能获得统计显著性
3. **负向Uplift的监控**：特别关注Sleeping Dogs，如果某些用户群的干预效果为负，应立即停止干预
4. **时间维度的评估**：分别在不同OOT月份评估，检查模型稳定性

---

## 关联文档

- [[费率敏感模型]]：X-Learner在差异化定价中的具体实践
- [[运营敏感模型_现状与迭代方向]]：T-Learner在WA运营触达中的应用
- [[双塔风险模型]]：意愿双塔模型，与Uplift模型配合使用
- [[建模全流程SOP]]：通用建模流程，Uplift模型的训练/评估遵循相同框架
- [[特征工程方法论]]：Uplift模型的特征工程方法
