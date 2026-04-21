---
title: 通用模型MCP需求
date: 2026-04-21
tags: [ai/mcp, risk-model, agent]
status: draft
---

# 通用模型MCP需求

## 一、需求背景

**提出方**：风控算法团队

**背景介绍**：公司正在建设 Agent 工作流体系，Agent 在执行自动化任务时需要调用模型进行打分（如风控评分模型、运营 Uplift 模型等）。目前各模型以独立服务形式部署，没有统一的 MCP 接口，Agent 无法通过标准协议直接调用，只能依赖人工中转或硬编码 HTTP 调用。

为此，需在公司现有 MCP Market（`mcp.easycash.id`）体系上搭建一个**通用模型 MCP 服务**，让 Agent 通过统一的 MCP 工具接口调用任意在线模型。

---

## 二、需求内容

### 1. 使用方

风控算法团队 / 使用 Agent 工作流的所有团队

### 2. 使用场景

| 场景 | 说明 |
|------|------|
| Agent 自动化决策 | Agent 在审批、运营等工作流中，调用风控模型或 Uplift 模型获取预测分，辅助决策 |
| 模型效果自动验证 | Agent 拉取样本后直接调用模型打分，与标签对比，自动输出效果报告 |
| 多模型对比 | Agent 同时调用多个模型版本，输出分数对比用于模型迭代评估 |

### 3. 具体需求逻辑

#### 3.1 设计原则

- **通用性**：单个 MCP 服务覆盖所有在线模型，通过 `model_name` 参数路由，避免每个模型单独发布一个 MCP
- **标准化**：统一输入/输出格式，Agent 侧无需关心各模型的底层差异
- **可发现性**：提供模型列表和元信息查询接口，Agent 可自主探索可用模型

#### 3.2 MCP 工具接口（Tools）

**Tool 1：`model_predict`** — 模型预测打分

```
输入参数：
  - model_name (string, 必填)：模型标识，如 "uplift-operation-v2"
  - features (object, 必填)：特征键值对，JSON 格式
  - model_version (string, 可选)：指定版本，默认使用线上最新版

输出：
  - score (number)：模型输出分数
  - probability (number)：概率值（0~1）
  - model_version (string)：实际使用的模型版本
  - request_id (string)：请求追踪 ID
  - inference_time_ms (number)：推理耗时（毫秒）
```

**Tool 2：`model_list`** — 查询可用模型列表

```
输入参数：无（可选 category 过滤）

输出：
  - models (array)：可用模型列表
    - model_name, display_name, category, status, latest_version
```

**Tool 3：`model_info`** — 查询模型元信息

```
输入参数：
  - model_name (string, 必填)

输出：
  - model_name, display_name, description
  - feature_list (array)：所需特征清单（字段名、类型、说明）
  - version_history (array)：版本列表
  - score_range：分数范围说明
  - threshold：推荐决策阈值（如有）
```

#### 3.3 后端实现要求

- 对接公司现有模型服务/模型仓库（如 ModelHub 或各模型的 HTTP endpoint）
- 统一封装为标准 HTTP 服务，对外暴露 `/model/predict`、`/model/list`、`/model/info` 三个路径
- 注册到 MCP Market（indo/prod），path 建议：`/risk-model-mcp-route`

#### 3.4 认证与权限

- 复用 MCP Market 现有 token 机制（`?token=<YOUR_TOKEN>`）
- 模型调用权限按 token 归属的工号做控制，避免越权

#### 3.5 MCP 注册信息（供发布参考）

```
name: risk-model-mcp
display_name: 风控通用模型MCP
category: risk-model
service_url: <模型网关 K8s service>
tags: [model, scoring, risk, uplift]
```

### 4. 预计影响范围

| 指标 | 预期影响 |
|------|---------|
| Agent 调用模型的接入成本 | 从人工对接降至 0（Agent 自助发现+调用） |
| 模型接入新 Agent 工作流的时间 | 从数天缩短至分钟级（install 即用） |
| 覆盖模型数量 | 预计覆盖现有全部在线模型（风控评分类 + 运营 Uplift 类，共约 N 个） |
| 后续新模型上线 | 注册到模型网关后自动纳入，无需重新发布 MCP |

### 5. 效果验证

- [ ] `mcp-market install risk-model-mcp` 成功，IDE 中出现对应 MCP 工具
- [ ] `model_list` 工具返回所有在线模型列表，与模型仓库一致
- [ ] `model_predict` 传入真实特征，返回分数与直接调用模型 HTTP 接口结果一致
- [ ] `model_info` 返回特征清单与模型文档对齐
- [ ] Agent 工作流（如运营 Uplift 场景）通过 MCP 调用模型，打分结果可追溯（request_id 可查日志）
- [ ] 无权限的 token 调用返回 403，不泄露模型数据

### 6. 需要哪些数据

| 数据 | 用途 | 负责方 |
|------|------|--------|
| 模型调用日志（model_name, request_id, latency, score） | 监控调用量和推理耗时，排查异常 | 模型服务侧落库 |
| 模型元信息（特征清单、版本、阈值） | 支持 `model_info` 接口返回 | 算法团队维护 |
| 错误日志（4xx/5xx 明细） | 接入问题排查 | MCP 服务侧落库 |

---

> [!note] 相关参考
> - [[模型档案/运营Uplift模型]] — 当前优先接入的模型
> - 公司 MCP Market：`mcp.easycash.id`（indo/prod）
> - CLI 工具：`mcp-market`，仓库见 `gitlab.yangqianguan.com/infra/cli-mcp-market`
