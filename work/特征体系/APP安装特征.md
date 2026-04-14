---
title: "APP安装特征盘点"
date: 2026-04-09
tags: [特征体系/APP]
company: EasyCash
---

# APP特征分类思维导图

## 1. 时间间隔特征
### 1.1 安装时间间隔
- **最小间隔**
  - V40P4UpdateNoSysGapLast180Dcoarse_mob2_class_5
  - V40P4UpdateNoSysGapLast30Dcoarse_fpd31_class_4
  - V11NoSystop_100
- **平均间隔**
  - V30NoSyshigh_education_level1
  - V40P4InstallNoSysGapLast90Dcoarse_mob2_class_4
  - V11NoSysregisteredCLApp
- **最大间隔**
  - V39P2InstallNoSysGapLast180DallLoanPackage
  - V40P4InstallNoSysGapLast180Dcoarse_mob1_class_5
- **总共间隔**
  - V40P4InstallNoSysGapLast180Dcoarse_mob2_class_4
  - V11NoSystop_100

### 1.2 更新时间间隔
- **最小间隔**
  - V40P4InstallNoSysGapLastrefined_fpd31_class_5
  - V39P2UpdateNoSysGapLast30DallLoanPackage
- **平均间隔**
  - V39P2UpdateNoSysGapLast180DallLoanPackage
  - V40P4UpdateNoSysGapLast3Dcoarse_fpd31_class_4
- **最大间隔**
  - V40P4UpdateNoSysGapLast90Dcoarse_mob1_class_4
  - V14NoSyspeerApp

### 1.3 距离时间点
- **最早安装距今天数**
  - V40P4InstallNoSysGapLast180Drefined_fpd31_class_7
  - V11NoSysothersApp
- **最晚安装距今天数**
  - V39P2InstallNoSysGapLast180DothersApp
  - V42P1UpdateNoSysGapLast180Dpay_wallet
- **最早更新距今天数**
  - V11NoSysInstallLast90Dtop_200
  - V40P4UpdateNoSysGapLast30Drefined_fpd31_class_4

## 2. 统计特征
### 2.1 分类统计
- **类别占比统计**
  - V15NoSys-类别Debtpaying占比
  - V12NoSys-类别GAME_ACTION占比
  - V16NoSys-类别Kids占比
- **时间差异统计**
  - V28NoSysTimeDiff-类别78_monster_merge_master
  - V27NoSysTimeDiff-类别PRODUCTIVITY
- **安装/更新统计**
  - V37NoSysInstallAll-类别zong_he_lv_you_fu_wu占比
  - V16NoSysUpdateApp-类别BusinessHighRelate占比

### 2.2 占比统计
- **安装占比**
  - 非系统App安装占比Update30D
  - 全部App安装占比Update30D
  - 系统App安装占比Update7D
- **时间趋势占比**
  - AllInstallTrend14DTo21D
  - AllInstallTrend21DTo90D

## 3. Embedding特征
### 3.1 向量统计
- **求和统计**
  - V6第31位求和
  - V13NoSysInstall第84位求和
  - V13NoSysInstallLast180D第34位求和
- **均值统计**
  - V13NoSysInstall第78位求均值
  - V13NoSysInstallLast180D第84位求均值
- **最值统计**
  - V13NoSysInstallLast180D第16位最小值
  - V13NoSysInstallLast30D第18位最大值
- **标准差统计**
  - EmbeddingUtilWithOperationsV2Residue0第13位求标准差

### 3.2 不同时间范围
- **最近30天**
  - V13NoSysInstallLast30D第47位最大值
  - V13NoSysInstallLast30D第1位求均值
- **最近180天**
  - V13NoSysInstallLast180D第30位最小值
  - V13NoSysInstallLast180D第67位求和

## 4. 关注列表特征
### 4.1 特定App统计
- **安装时间相关**
  - com.google.android.apps.photos-安装距最后一次更新天数
  - com.whatsapp-安装距今天数
- **更新时间相关**
  - com.google.android.apps.magazines-最后一次更新距今天数
  - com.shopee.id-最后一次更新距今天数
- **时间占比**
  - com.whatsapp.w4b-安装距最后一次更新天数占安装总天数比

### 4.2 范围统计
- **安装占比范围**
  - V5-50To100范围安装占比
  - V5-0To100范围安装占比
  - V6-0To100范围安装占比
- **安装总数范围**
  - V6-0To100范围安装总数
  - V6-0To2500范围安装总数

## 5. 基础统计特征
### 5.1 数量统计
- 系统app总数Total
- app总数Total
- 统计包含关键词gamepackage个数

### 5.2 时间基准
- 首次安装非系统app距今天Total
- 从最后一个app的安装时间到风控计算时间的时间间隔天数
- 从最早一个app的安装时间到风控计算时间的时间间隔天数

## 6. 特殊技术特征
### 6.1 TF-IDF特征
- tfIdfV1NoSysInstallLast180Dtop_30最小值
- tfIdfV1NoSysInstallLast180Dtop_400总和
- tfIdfAndCategoryV45InstallNoSysLast3D最小值

### 6.2 分类模型特征
- 不同风险等级分类
- 不同用户等级分类
- 不同教育水平分类

## 关联文档

- [[印尼现金贷风控体系]]
- [[图网络特征方法论]]
- [[特征工程方法论]]
