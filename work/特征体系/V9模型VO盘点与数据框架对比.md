---
title: V9模型VO盘点与数据框架对比
date: 2026-04-13
tags: [work/特征体系, work/模型档案, indo/v9-model]
status: active
---

# V9模型VO盘点与数据框架对比

> [!note] 来源
> `inbox/印尼首贷特征VO盘点.xlsx` 盘点现有首贷准入V9模型全部特征，
> 对比 [[印尼风控数据分类框架]]（AI生成的数据全景）得出覆盖度矩阵。
> 原始文件已归档至 `归档/2026-04-13_印尼首贷特征VO盘点.xlsx`

---

## 一、V9 模型 VO 贡献度全景

V9 模型共入模 **2259 个特征**，分属 **73 个 VO**，总贡献度累计 100%。

### 贡献度 TOP 20 VO

| 排名 | 特征VO | 累计贡献度 | 特征数 | 含义 |
|------|--------|-----------|--------|------|
| 1 | AUTH_RISK | 11.36% | 97 | 鉴权特征（KYC全集） |
| 2 | IDN_AFPI_V5_INSTITUTION | 9.45% | 312 | AFPI机构码相关特征 |
| 3 | IDN_APP_CATEGORY_TIME_DIFF_V28 | 8.50% | 156 | APP分类时间差统计V28 |
| 4 | IDN_APP_EMBEDDING_V7 | 5.12% | 57 | APP Embedding V7 |
| 5 | IDN_AFPI_FILTER_RISK | 4.83% | 46 | AFPI过滤特征（去重复订单） |
| 6 | IDN_APP_CATEGORY_TIME_GAP_V11 | 4.22% | 104 | APP分类时间间隔V11 |
| 7 | IDN_APP_TIME_GAP_V2 | 4.14% | 96 | APP时间间隔V2 |
| 8 | IDN_APP_CATEGORY_STATE_V37 | 3.97% | 423 | APP分类状态统计V37（特征数最多）|
| 9 | IDN_APP_CATEGORY_TIME_INTERVAL_V32 | 3.83% | 78 | APP分类时间区间V32 |
| 10 | IDN_AFPI_RISK | 2.95% | 51 | AFPI风险统计特征 |
| 11 | IDN_TONG_DUN | 2.44% | 22 | 同盾设备指纹 |
| 12 | IDN_APP_CATEGORY_STATE_V15 | 2.21% | 54 | APP分类统计V15 |
| 13 | IDN_APP_CATEGORY_TIME_DIFF_V27 | 2.19% | 44 | APP分类时间差V27 |
| 14 | AFPI_ONE_TIME_NO_FILTER | 2.05% | 50 | AFPI一次性借款特征 |
| 15 | IDN_APP_EMBEDDING_V6 | 1.99% | 60 | APP Embedding V6 |
| 16 | IZI_DATA_TOP_UP_FEATURE | 1.91% | 37 | IZI充值行为特征（运营商） |
| 17 | ADVANCE_CUSTOM_V4_FEATURE | 1.77% | 10 | ADVANCE V4定制特征 |
| 18 | IZI_ID_AND_PHONE_FEATURE_MODIFY | 1.66% | 20 | IZI手机号/身份ID多头（去EC） |
| 19 | IDN_APP_CATEGORY_TIME_GAP_V29 | 1.65% | 42 | APP分类时间间隔V29 |
| 20 | IDN_APP_TF_IDF | 1.58% | 36 | APP TF-IDF特征 |

### VO 数据源分组汇总

| 数据源模块 | VO数量 | 总特征数 | 累计贡献度 |
|----------|--------|---------|----------|
| APP（安装/行为/Embedding）| 38 个VO | ~1500 | ~55% |
| AFPI（网贷协会）| 5 个VO | ~504 | ~21% |
| AUTH_RISK（鉴权）| 1 个VO | 97 | 11.36% |
| IZI（多头查询+充值+WhatsApp）| 8 个VO | ~120 | ~9% |
| 同盾 TongDun（设备指纹）| 2 个VO | 38 | 3.10% |
| ADVANCE（替代数据+OCR）| 3 个VO | ~27 | ~3% |
| ADDRESS + BASIC（地址/基础）| 2 个VO | 8 | 2.10% |
| OCR 衍生特征 | 1 个VO | 2 | 0.21% |
| **CBI（央行征信）** | **0 个VO** | **0** | **0%** |

> [!warning] 关键发现：CBI 在 V9 模型中完全未入模
> V9 准入模型中 **没有任何 CBI 央行征信特征**（搜索 2259 行特征名，CBI 命中 0 条）。
> CBI 模块在 xlsx 中有完整数据盘点，但均未进入 V9 模型。
> 可能原因：覆盖率低（仅覆盖有银行贷款记录人群）、数据接入延迟、或留给老客模型使用。

---

## 二、AI 框架 × V9 现有 VO 覆盖度矩阵

> AI框架来源：[[印尼风控数据分类框架]]（基于 `归档/2026-04-13_印尼风控数据分类.png` 生成）

| AI框架数据类别 | 量级 | 对应 V9 VO | 覆盖状态 |
|--------------|------|----------|---------|
| **1.1 身份证件认证**（Dukcapil/OCR）| 人数级 | `AUTH_RISK` + `ADVANCE_OCR_CHECK` + `OCR_DERIVATIVE_FEATURE` | ✅ 已覆盖 |
| **1.2 生物特征识别**（人脸/活体）| 人数级 | `AUTH_RISK`（face++） | ✅ 已覆盖 |
| **1.3 设备指纹**（IMEI/IP/VPN）| T4 | `IDN_TONG_DUN` + `TONG_DUN_V2` | ✅ 已覆盖（供应商：同盾）|
| **2.1 通话/短信元数据**（SNAP/Afrimme）| T3 | ❌ 无 | ❌ **完全空白** |
| **2.2 App 使用行为**（使用频率/时长）| T3 | APP系列VO（安装/更新时间戳）| ⚠️ 仅安装维度，无使用频率 |
| **2.3 电商账号行为**（Shopee/Tokopedia）| T4 | ❌ 无 | ❌ **完全空白** |
| **3.1 CBI 官方征信**（银行贷款记录）| T1 | ❌ V9无CBI特征 | ⚠️ **数据已接入，V9未入模** |
| **3.2 AFPI/P2P 网贷多头** | T1 | `IDN_AFPI_RISK` + `IDN_AFPI_V5_INSTITUTION` + `AFPI_FILTER` + `AFPI_ONE_TIME` + `AFPI_PAY_DAY` | ✅ 覆盖最深（21%贡献）|
| **3.3 IZI 多头查询** | T1–T2 | `IZI_ID_AND_PHONE` + `IZI_DUO_TOU_INQUIRIES_SCORE` + `IDN_IZI_DATA_MULTI_PLATFORM_TREND_*` + `IZI_DATA_PROPORTION` + `IZI_DATA_NT_TIME` + `IZI_DATA_NUMBER_SCORE` | ✅ 已覆盖（多维度）|
| **3.4 运营商金融行为**（账单/套餐）| T5 | `IZI_DATA_TOP_UP_FEATURE`（充值）+ ADVANCE电信充值 | ⚠️ 仅充值金额/间隔，账单/套餐空白 |
| **3.5 境外电商征信**（Shopee/Lazada信用分）| T0–T3 | ❌ 无 | ❌ **完全空白** |
| **4.1 个人基本特征**（教育/职业/收入）| T4 | `AUTH_RISK` + `IDN_BASIC_FEATURE` + `ADDRESS` | ✅ 已覆盖 |
| **4.2 教育机构授权**（PDR/SFU认证）| T2–T4 | ❌ 无 | ❌ **完全空白** |
| **4.3 BPJS 就业验证**（社保记录）| T2–T3 | ❌ 无 | ❌ **完全空白** |
| **4.4 社交/通讯录关系网络** | T4 | `IZI_WHATSAPP_OPEN_FEATURE`（4个特征，1.05%）| ⚠️ 极浅（仅WhatsApp开启状态）|

---

## 三、IZI 数据实际覆盖范围（超出预期）

> [!tip] IZI 不只是多头查询
> xlsx 揭示 IZI 数据实际包含多个维度，远比「多头查询」标签丰富：

| IZI VO | 特征数 | 贡献度 | 实际含义 |
|--------|--------|--------|---------|
| `IZI_DATA_TOP_UP_FEATURE` | 37 | 1.91% | 运营商充值行为（时段/金额/间隔）|
| `IZI_ID_AND_PHONE_FEATURE_MODIFY` | 20 | 1.66% | ID+手机号多头查询（去EC自身）|
| `IZI_DUO_TOU_INQUIRIES_SCORE_V2_MODIFY` | 22 | 1.23% | 多头综合评分（无EC）|
| `IZI_WHATSAPP_OPEN_FEATURE` | 4 | 1.05% | WhatsApp 开启/活跃状态 |
| `IZI_DATA_PREFERENCE_FEATURE` | 8 | 0.71% | 用户兴趣偏好标签 |
| `IZI_DATA_PROPORTION_MODIFY` | 7 | 0.31% | 多头类机构占比 |
| `IZI_DATA_NT_TIME_FEATURE` | 2 | — | 夜间查询时间特征 |
| `IZI_DATA_NUMBER_SCORE_FEATURE` | 1 | 0.07% | 号码质量评分 |
| `IDN_IZI_DATA_MULTI_PLATFORM_TREND_IDENTITY_*` | 21 | 0.22% | 身份证跨平台趋势 |
| `IDN_IZI_DATA_MULTI_PLATFORM_TREND_MOBILE_*` | 3 | — | 手机号跨平台趋势 |

IZI 实际提供：**多头查询 + 运营商充值 + WhatsApp行为 + 兴趣偏好 + 夜间行为**，是一个综合替代数据平台。

---

## 四、空白区域优先级（结合 V9 贡献度排名）

> 参考上一轮分析 [[印尼风控数据分类框架]] 中的高增益机会，结合 V9 现有 VO 的贡献度分布：

### 🔴 高优先级（空白且可行性高）

**1. 通话/短信元数据特征**（框架 2.1）
- 现状：V9 完全无此维度，SNAP/Afrimme/Linkis 已在框架中列为合作服务
- 信号：联系人质量、通话关系类型（雇主/家人/中介）= 就业核验的替代变量
- 参考：APP系列VO贡献55%，通讯录数据量级相当（T3），值得作为下一个大方向

**2. CBI 特征进入准入模型**（框架 3.1）
- 现状：CBI数据已接入，完整盘点在xlsx，但 **V9 = 0 特征**
- 动作：排查覆盖率，若首贷覆盖率 >30% 则直接实验CBI特征集
- 参考：CBI 在老客模型可能已有使用，可借鉴其特征体系

**3. 运营商账单/套餐特征**（框架 3.4，扩展）
- 现状：充值金额/间隔已有（IZI_DATA_TOP_UP，贡献1.91%，37个特征）
- 空白：账单支付准时率、套餐档位变化、数据流量消耗
- 动作：与 IZI 或 Telkomsel 确认是否可获取账单维度数据

### 🟡 中优先级（数据采购需要时间）

**4. 电商账号行为特征**（框架 2.3）
- Shopee/Tokopedia账号：注册时长、交易频次、支付方式、卖家状态
- 对信用白户（无AFPI/CBI记录）效果最强

**5. WhatsApp 行为深度特征**（框架 4.4 扩展）
- 现状：`IZI_WHATSAPP_OPEN_FEATURE` 仅4个特征（是否开启）
- 空白：WhatsApp 活跃频率、消息发送时段、联系人数量
- IZI 可能已有更多维度，确认是否可解锁

### 🔵 低优先级（新数据源，周期长）

**6. BPJS 就业验证**（框架 4.3）
**7. 教育机构认证**（框架 4.2）
**8. 境外电商征信**（框架 3.5）

---

## 五、xlsx 数据模块对应关系

| xlsx Sheet | 对应 V9 VO | 数据说明 |
|-----------|----------|---------|
| 准入V9模型 | 全部73个VO | V9模型特征列表+VO贡献度排名 |
| 鉴权数据 | AUTH_RISK | KYC鉴权字段盘点+省份/行业逾期率分布 |
| APP模块 | APP系列38个VO | App安装/更新时间戳体系 |
| AFPI模块 | AFPI系列5个VO | 网贷协会原始字段+特征设计 |
| IZI模块 | IZI系列10个VO | 多头查询报文结构（Object1/Self模块）|
| CBI模块 | **V9中无** | CBI数据字段盘点（CollateralDetail等10+模块）|
| TD模块 | IDN_TONG_DUN | 同盾设备指纹原始JSON（device_detail完整字段）|
| ADVANCE模块 | ADVANCE系列3个VO | OCR+多头查询+电信+贷后特征体系 |
| 埋点模块 | 埋点（V9未见独立VO）| 神策埋点事件分类（click/exposure/pageview）|
| 现有特征稳定性分析 | 全模块 | 特征PSI/稳定性月度监控 |

---

## 关联文档

- [[印尼风控数据分类框架]] — AI生成的数据全景框架（对比基准）
- [[CBI征信特征]] — CBI特征体系详细盘点
- [[AFPI网贷特征]] — AFPI特征体系
- [[IZI多头查询特征]] — IZI特征体系
- [[APP安装特征]] — APP特征体系
- [[ADVANCE替代数据特征]] — ADVANCE特征体系
- [[埋点行为特征]] — 埋点特征体系
- [[鉴权VO特征]] — AUTH_RISK特征体系
