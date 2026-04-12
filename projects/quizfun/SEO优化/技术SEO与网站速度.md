---
title: 技术SEO与网站速度
date: 2026-04-11
tags:
  - topic/seo
  - topic/technical-seo
  - topic/core-web-vitals
  - project/quizfun
status: active
related:
  - "[[内容优化与结构化数据]]"
  - "[[用户体验与Core Web Vitals]]"
  - "[[projects/quizfun/SEO优化/_index]]"
---

# 技术 SEO 与网站速度

> 技术 SEO 是 2024-2025 年排名的基石。Core Web Vitals 已成为排名信号，网站速度直接影响用户行为信号。

![[技术SEO与网站速度.png|600]]

## 1. Core Web Vitals 三大指标

### LCP（最大内容绘制）— 目标 < 2.5 秒
测量页面最大元素（图片或大段文字）的加载时间。

**优化步骤：**
1. 尽量让**文字**成为 LCP 元素（比图片加载快得多）
2. 必须用图片时，转换为 **WebP 格式**压缩
3. 使用 CDN 加速静态资源
4. 对首屏图片使用 `fetchpriority="high"` 属性

### INP（交互到下一次绘制）— 目标 < 200ms
替代 FID 的新指标，测量用户点击后的响应速度。

**优化步骤：**
1. 减少阻塞主线程的 JavaScript
2. 在 Staging 环境逐个关闭插件，定位性能瓶颈
3. 使用代码分割（Code Splitting）按需加载
4. 测验互动场景特别重要（每次选项点击都是 INP 测量点）

### CLS（累积布局偏移）— 目标 < 0.1
衡量页面加载中元素意外位移的情况。

**优化步骤：**
1. 图片和广告预留**固定尺寸空间**（width/height 属性）
2. 避免动态注入影响布局的内容
3. 字体使用 `font-display: swap`

## 2. 网站速度综合优化

### 图片优化清单
- [ ] 所有图片转为 WebP 格式
- [ ] 使用 `srcset` 响应式图片
- [ ] 懒加载非首屏图片（`loading="lazy"`）
- [ ] 首屏图片预加载（`<link rel="preload">`）

### JavaScript 优化
- [ ] 删除未使用的 JS（Tree Shaking）
- [ ] 延迟加载非关键 JS（`defer` / `async`）
- [ ] 减少第三方脚本（分析、广告、聊天插件）
- [ ] 使用 WP Rocket / Cloudflare 等缓存工具

### 诊断工具
| 工具 | 用途 |
|------|------|
| Google PageSpeed Insights | 全面诊断，给出具体建议 |
| GTmetrix | 详细瀑布图分析 |
| Chrome DevTools | 实时调试 |
| Search Console → Core Web Vitals | 真实用户数据（Field Data） |

**诊断起点：** 创建一个空白页面进行基准测试，确认主题/框架本身是否影响速度。

## 3. 移动端优化

- 响应式设计（移动端优先索引已是默认）
- 测验题目在手机上的点击区域 ≥ 44px
- 避免横向滚动
- 测试工具：Google Mobile-Friendly Test

## 4. 网站架构与内部链接

### 扁平化架构
```
首页
├── 分类页（如：性格测验 / 知识问答 / 娱乐测验）
│   ├── 测验 A
│   ├── 测验 B
│   └── 测验 C
└── 静态页面（关于/联系）
```
- 任何页面从首页点击 ≤ 3 次可达
- 避免孤儿页面（无内部链接指向的页面）

### 内部链接策略（反向筒仓 Reverse Silo）
- 相关测验之间互相链接
- 分类页链接到所有下属测验
- 高权重页面将权重传递给新内容页
- 锚文字使用**描述性关键词**，而非"点击这里"

### XML Sitemap
- 包含所有测验页面
- 排除低价值页面（标签页、分页页）
- 每次发布新测验后提交更新

## 5. 索引与爬取优化

### robots.txt 配置
- 阻止爬取：管理员页面、用户个人页、重复内容页
- 允许爬取：所有测验页、结果分享页

### 规范化（Canonical）
- 每个测验结果页设置正确的 canonical URL
- 防止参数 URL 造成重复内容
- 分享变体页（`?share=true`）指向主页 canonical

### 状态码监控
- 定期检查 404 错误
- 301 重定向旧 URL（不要裸删）

## 关联笔记

- [[用户体验与Core Web Vitals]] — CWV 的用户体验维度
- [[内容优化与结构化数据]] — 技术架构承载内容
- [[projects/quizfun/SEO优化/_index]] — 研究总索引
