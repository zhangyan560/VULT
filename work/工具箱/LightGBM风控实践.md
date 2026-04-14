---
title: "LightGBM 使用要点"
date: 2026-04-09
tags: [工具箱/算法, LightGBM]
aliases: [LGBM, 梯度提升树]
---

# LightGBM 使用要点

> 参考论文：[[04-资源/论文/NIPS-2017-lightgbm]]（NeurIPS 2017）

## 核心特性

| 特性 | 说明 |
|------|------|
| 叶子生长（Leaf-wise） | 每次选择增益最大的叶子分裂，比 Level-wise 更快 |
| Histogram 算法 | 特征值离散化，大幅降低内存和计算量 |
| GOSS | 梯度单侧采样，保留大梯度样本 |
| EFB | 互斥特征捆绑，减少特征维度 |

## 风控场景关键参数

```python
params = {
    'n_estimators': 1000,
    'learning_rate': 0.05,
    'max_depth': 6,          # 控制过拟合
    'num_leaves': 31,        # 叶子数，2^max_depth 以内
    'min_child_samples': 100, # 叶子最小样本数，正则化
    'subsample': 0.8,        # 行采样
    'colsample_bytree': 0.8, # 列采样
    'reg_alpha': 0.1,        # L1正则
    'reg_lambda': 0.1,       # L2正则
    'class_weight': 'balanced', # 处理正负样本不均衡
}
```

## 特征重要性

```python
# 三种重要性
lgb.plot_importance(model, importance_type='split')   # 分裂次数
lgb.plot_importance(model, importance_type='gain')    # 信息增益
# SHAP（最准确的可解释性）
import shap
shap.summary_plot(shap_values, X_test)
```

## 交叉验证最佳实践

```python
# 5折时序CV（防止数据穿越）
tscv = TimeSeriesSplit(n_splits=5)
```

## 关联文档

- [[模型评估与监控方法论]]
- [[特征工程方法论]]
