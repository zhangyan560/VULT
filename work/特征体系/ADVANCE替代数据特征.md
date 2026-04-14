---
title: "ADVANCE特征盘点"
date: 2026-04-09
tags: [特征体系/ADVANCE]
company: EasyCash
---

# ADVANCE特征思维导图

## ADVANCE_OCR_COUNT_FEATURE
- **count_third_party_raw_data_time_created_recent30day**
  - Advance调用OCR的次数(过去30天)
- **count_third_party_raw_data_time_created_recent24h**
  - Advance调用OCR的次数(过去24小时)

## ADVANCE_ID_FORGERY_DETECTION_CODEMESSAGE
- **advance_id_forgery_detection_message**
  - advance假证检测返回message
- **advance_id_forgery_detection_code**
  - advance假证检测返回code

## IDN_ADVANCE_AI_FIRST_LOAN

### ocrInfoVO
- **宗教信息独热编码**
  - kristen (基督教)
  - katholik (天主教)
  - islam (伊斯兰教)
  - hindu (印度教)
  - budha (佛教)
  - other (其他)
  - missing (缺失)
- **registerAndOcrNameMatchScore**
  - OCR姓名与注册姓名的匹配分数
- **registerAndOcrIDNumberMatchScore**
  - OCR身份证号与注册身份证号的匹配分数
- **ocrSpecialOccupationMatchScore**
  - OCR职业是否为特殊职业分数
- **isWni**
  - 是否是印尼国籍
- **nationalityAndWniSimilarity**
  - 国籍与WNI相似度



### multiPlatformComplexVO

#### multiPlatformComplexIdVO (身份查询)
- **时间窗口**
  - 1h, 3h, 6h, 12h, 24h
  - 3d, 7d, 14d, 21d, 30d
  - 60d, 90d, 180d, 360d
- **机构类型**
  - bank (银行)
  - cateB (CATE_B)
  - ksp (KSP)
  - loanSupermarket (贷款市场)
  - multiFinance (多金融)
  - ojk (OJK)
  - otherFintech (其他金融科技)

#### multiPlatformComplexPhoneVO (电话查询)
- **时间窗口**
  - 1h, 3h, 6h, 12h, 24h
  - 3d, 7d, 14d, 21d, 30d
  - 60d, 90d, 180d, 360d
- **机构类型**
  - bank (银行)
  - cateB (CATE_B)
  - ksp (KSP)
  - loanSupermarket (贷款市场)
  - multiFinance (多金融)
  - ojk (OJK)
  - otherFintech (其他金融科技)

### ADVANCE_CUSTOM_V4_FEATURE_FIRST_LOAN

#### 基础信息特征 (General Features)
  - 来自nik的城市，X[0:2]
  - 来自nik的城市，X[0:4]
  - 来自nik的城市，X[0:6]
  - 年龄
  - 申请时刻的小时
  - 申请时刻的天

#### 身份证多头特征 (ID Multi-platform Features)

##### 时间维度特征
- **历史使用时间差**
  - 与第一次使用服务的时间差
  - 与最后一次使用服务的时间差
  - 使用时间差的平均值
  - 使用时间差的中位数
  - 使用时间差的标准差

##### 机构查询特征
- **OJK机构查询跨机构数**
  - 最近7天(168小时)
  - 最近30天(720小时)
  - 最近90天(2160小时)
  - 最近360天(8640小时)
  - 最近720天(17520小时)

- **MULTI_FINANCE机构查询跨机构数**
  - 最近180天(4320小时)
  - 最近360天(8640小时)
  - 最近720天(17520小时)

##### 服务类型查询特征
- **OCR服务查询**
  - 最近30天OJK机构查询跨机构数
  - 最近90天OJK机构查询跨机构数

- **CHECK服务查询**
  - 最近90天OJK机构查询跨机构数
  - 最近720天OJK机构查询跨机构数
  - 最近720天SOLUTION_PROVIDER机构查询跨机构数

- **BLACK服务查询**
  - 最近720天OJK机构查询跨机构数

- **MULTI服务查询**
  - 最近30天OJK机构查询跨机构数
  - 最近90天OJK机构查询跨机构数
  - 最近720天OJK机构查询跨机构数

- **SCORE服务查询**
  - 最近90天OJK机构查询跨机构数

##### MULTI服务深度分析
- **查询次数统计**
  - 最近90天MULTI服务查询次数
  - 最近360天MULTI服务查询次数
  - 最近720天MULTI服务查询次数
  - 最近720天MULTI_FINANCE机构查询次数

- **API调用频次**
  - 最近7天机构API调用次数最大值
  - 最近360天机构API调用次数最大值
  - 最近720天机构API调用次数最大值

- **API调用间隔分析**
  - 最大调用间隔(90天/180天/720天)
  - 最小调用间隔(90天/720天)
  - 调用间隔中位数(720天)
  - 调用间隔标准差(90天/360天/720天)

##### 时间模式特征
- **工作时间查询行为**
  - 最近7天工作日工作时间查询次数
  - 最近730天工作日工作时间查询次数

#### 电话号码多头特征 (Phone Multi-platform Features)

##### 时间维度特征
- **历史使用时间差**
  - 与第一次使用服务的时间差
  - 与最后一次使用服务的时间差
  - 使用时间差的平均值
  - 使用时间差的中位数
  - 使用时间差的标准差

##### 机构查询特征
- **OJK机构查询**
  - 最近720天查询跨机构数

- **SCORE服务查询**
  - 最近360天OJK机构查询跨机构数

##### 使用频率分析
- **时间分布特征**
  - 2年内频率最少的一天
  - 2年内频率最高的一天
  - 2年内频率最少的小时
  - 2年内频率最高的小时

##### 时间模式特征
- **工作时间查询行为**
  - 最近30天工作日工作时间查询次数
  - 最近180天工作日工作时间查询次数
  - 最近360天工作日工作时间查询次数
  - 最近730天工作日工作时间查询次数

#### 电信行为特征 (Telecom Features)

##### 充值金额分析
- **统计时段特征**
  - 最近30天充值金额标准差
  - 最近60天平均充值金额 & 标准差
  - 最近120天充值金额最小值
  - 最近180天充值金额统计(最小值/最大值/平均值)
  - 最近365天充值金额统计(最小值/离散系数)
  - 最近730天充值金额全面统计(最小值/最大值/平均值/中位数/总额/范围/离散系数)

##### 充值间隔分析
- **时间间隔统计**
  - 最近180天充值间隔(平均值/标准差/范围/离散系数)
  - 最近365天充值间隔(最小值/中位数/范围/离散系数)
  - 最近730天充值间隔完整统计(最小值/最大值/平均值/中位数/标准差/离散系数)

##### 时间节点特征
- **关键时间点**
  - 最近一次充值时间距今时长
  - 第一次充值时间距今时长
- **数据可用性**
  - 是否命中电信数据

#### 贷后相关特征 (Post-loan Features)

##### 贷后指标集合
- 贷后相关特征733
- 贷后相关特征738
- 贷后相关特征739
- 贷后相关特征1091
- 贷后相关特征1092
- 贷后相关特征1125
- 贷后相关特征1272
- 贷后相关特征1301
- 贷后相关特征1320-1322
- 贷后相关特征1324
- 贷后相关特征1328-1330

#### 6. 综合评分 (Comprehensive Score)







## 关联文档

- [[印尼现金贷风控体系]]
- [[特征工程方法论]]
