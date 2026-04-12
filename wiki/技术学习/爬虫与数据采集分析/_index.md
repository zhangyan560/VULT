---
title: 爬虫与数据采集分析 MOC
date: 2026-04-12
tags: [技术学习/爬虫, MOC, 数据采集]
status: active
---

# 爬虫与数据采集分析 MOC

> **多源数据采集与分析知识库**。覆盖社交媒体、电商、应用市场三大类数据源的完整技术体系。
>
> NotebookLM 研究笔记本：`340c1c92-91d7-423d-9315-c056178c2e44`（38 个视频源）
> 生成日期：2026-04-12

---

## 分类索引

| 分类 | 核心内容 | 关键工具 |
|------|----------|----------|
| [[社交媒体数据采集技术]] | Reddit/Twitter/Facebook 爬虫方案 | PRAW, Scrapy, Playwright |
| [[电商平台数据抓取方案]] | Amazon/Shopify/eBay 数据采集 | Bright Data, BeautifulSoup |
| [[应用市场评论爬取与分析]] | Google Play/App Store 评论批量采集 | google-play-scraper, SerpApi |
| [[反爬虫绕过与合规策略]] | Cloudflare 绕过、代理轮换、合规边界 | curl-cffi, 住宅代理 |
| [[多源数据分析实战案例]] | NLP 情感分析、竞品研究完整流程 | BERT, NLTK, Pandas |

---

## 多源数据采集与分析 SOP 总纲

### Phase 1：需求定义与数据源选择

```
明确分析目标
├── 舆情监控 → 社交媒体（Reddit/Twitter）
├── 竞品分析 → 电商平台（Amazon/Shopify）
├── 用户需求挖掘 → 应用市场（Google Play/App Store）
└── 全面情报 → 多源组合采集
```

### Phase 2：技术选型决策

**API 优先原则**（按平台）：

| 平台 | 首选方案 | 备选方案 |
|------|----------|----------|
| Reddit | PRAW + 官方 API | Pushshift 存档 / `.json` 端点 |
| Twitter | 官方 API v2 | XHR 请求截获 |
| Amazon | Bright Data API | BeautifulSoup + 住宅代理 |
| Shopify | `/products.json` 公开端点 | Shopify Spy 插件 |
| Google Play | google-play-scraper 库 | SerpApi / Octoparse |
| App Store | app-store-scraper 库 | iTunes RSS Feed |

### Phase 3：反爬策略配置

根据目标平台的反爬等级选择对应策略：

```
低防护（个人博客/小站）
    → requests + BeautifulSoup + 随机 User-Agent

中防护（大多数电商/论坛）
    → requests + 数据中心代理 + 随机延迟（2-5s）

高防护（Amazon/LinkedIn/Instagram）
    → Playwright/curl-cffi + 住宅代理 + 粘性会话

极高防护（Cloudflare 企业版）
    → Bright Data Unblocker / ZenRows + 托管浏览器
```

### Phase 4：数据采集执行

1. **小批量测试**：先采集 100 条，验证数据结构和字段完整性
2. **错误处理**：捕获 403/429/503，实现自动重试和代理切换
3. **断点续传**：记录已采集的 ID/时间戳，避免重复采集
4. **数据落地**：CSV（小批量）→ PostgreSQL（大规模）→ S3（原始备份）

```python
# 采集框架模板
import time, random, csv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 503])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def scrape_with_delay(url, session, proxy=None):
    time.sleep(random.uniform(2, 5))  # 随机延迟
    return session.get(url, proxies=proxy, timeout=15)
```

### Phase 5：数据清洗与分析

**标准清洗 Pipeline**：

```python
def clean_reviews(df):
    df = df.dropna(subset=['content'])         # 去空值
    df = df.drop_duplicates(subset=['content']) # 去重
    df['content'] = df['content'].str.strip()  # 去空白
    df['at'] = pd.to_datetime(df['at'])        # 时间标准化
    df = df[df['content'].str.len() > 10]      # 过滤过短文本
    return df
```

**情感分析选型**：

```
数据量 < 10,000 条 → VADER（快速，不需要 GPU）
数据量 > 10,000 条，需要高精度 → RoBERTa / DistilBERT
中文数据 → ERNIE 3.0 / 中文 BERT
金融/专业领域 → FinBERT / 领域预训练模型
```

### Phase 6：可视化与洞察输出

| 分析目标 | 可视化类型 | 工具 |
|----------|------------|------|
| 情感分布 | 饼图/柱状图 | Matplotlib/Seaborn |
| 时间趋势 | 折线图 | Plotly |
| 关键词特征 | 词云 | WordCloud |
| 用户画像 | 热力图 | Seaborn heatmap |
| 竞品对比 | 雷达图 | Plotly radar |

### Phase 7：自动化与部署

```
生产环境推荐技术栈：
- 调度：Airflow / GitHub Actions（定时触发）
- 采集：Python + Scrapy / Playwright
- 存储：PostgreSQL + S3
- 分析：Jupyter Notebook / FastAPI（推理服务）
- 监控：Grafana 告警面板
- 报告：自动生成 PDF + Slack/邮件推送
```

---

## YouTube 视频来源索引

### 社交媒体数据采集（10 个视频）

| # | 标题 | 频道 | 播放量 | URL |
|---|------|------|--------|-----|
| 1 | Reddit Data for Social Scientists | Professor Foote | 822 | https://www.youtube.com/watch?v=KBDJhhz4oXA |
| 2 | How to scrape Reddit posts and comments | Adrian \| The Web Scraping Guy | 23.1K | https://www.youtube.com/watch?v=PR3v57rAaMM |
| 3 | How to Scrape Data From Reddit \| Social Media Scraping API Tutorial | Decodo | 3.5K | https://www.youtube.com/watch?v=rccFawVomQg |
| 4 | How To Scrape TWEETS WITHOUT Using Twitter API in Python | Munch Dine | 2.7K | https://www.youtube.com/watch?v=PhEKFtq05G8 |
| 5 | How to Scrape Reddit | Adrian \| The Web Scraping Guy | 8.8K | https://www.youtube.com/watch?v=BlEogECNg2E |
| 6 | Python Scripts - Scraping Reddit via API (PRAW) | PyMoondra | 27.6K | https://www.youtube.com/watch?v=gIZJQmX-55U |
| 7 | How to do Web Scraping Reddit Posts Using Scrapy | Proxies API | 1.6K | https://www.youtube.com/watch?v=_z-nefoAl88 |
| 8 | 2023 NEW METHOD for Scraping Reddit Data using Python | HealthNus | 100 | https://www.youtube.com/watch?v=oG7R3WnyDyY |
| 9 | Scraping Reddit Data - Python & PRAW | Joseph Allen | 739 | https://www.youtube.com/watch?v=uVPWxD2fnK4 |
| 10 | How To Scrape Reddit & Automatically Label Data For NLP Projects | Patrick Loeber | 30.2K | https://www.youtube.com/watch?v=8VZhog5C3bU |

### 电商平台数据抓取（10 个视频）

| # | 标题 | 频道 | 播放量 | URL |
|---|------|------|--------|-----|
| 1 | How to Scrape Data from any E-commerce Website | Ultimate Web Scraper | 2.4K | https://www.youtube.com/watch?v=npx_9Fk9uIs |
| 2 | Shopify Scraper Tutorial | Shopify Spy | 1.7K | https://www.youtube.com/watch?v=EFvVwC9Qi_U |
| 3 | The Ultimate Guide to Scraping Product Data from Amazon | Tapicker | 12.5K | https://www.youtube.com/watch?v=QICvoFka36k |
| 4 | How to Scrape Data from any Ecommerce Website | ParseHub | 90.9K | https://www.youtube.com/watch?v=1o9E-I1HPok |
| 5 | Amazon Scraper \| How to extract all Amazon store data | epctex | 308 | https://www.youtube.com/watch?v=Aa5SOI5EHNU |
| 6 | Scrape Amazon Products & Reviews in MINUTES (n8n & apify) | Alex Followell | 5.4K | https://www.youtube.com/watch?v=vYxkJls0phE |
| 7 | Aliexpress products importer for Shopify | MyDataProvider | 3.2K | https://www.youtube.com/watch?v=szqHUZaFRFE |
| 8 | Python Scraper - Google Play and App Store Reviews | JiFacts | 17.9K | https://www.youtube.com/watch?v=GVwjR6lkS6Q |
| 9 | How to Scrape Google Play Reviews + Sentiment Analysis | Gagandeep Kundi | 13.3K | https://www.youtube.com/watch?v=pPUUxDThnq4 |
| 10 | How to Scrape App Reviews From Google Play | Octoparse | 9.3K | https://www.youtube.com/watch?v=MY_EuzPOfSk |

### 反爬虫绕过技术（8 个视频）

| # | 标题 | 频道 | 播放量 | URL |
|---|------|------|--------|-----|
| 1 | How to Bypass Cloudflare Protection When Web Scraping | Decodo | 39.0K | https://www.youtube.com/watch?v=2ucM62lMbyk |
| 2 | Bypass Cloudflare - Avoid Bot Detection | AutomationWave | 18.3K | https://www.youtube.com/watch?v=We_5Hq4K4-M |
| 3 | What Is Anti-botting and How to Bypass It? | Decodo | 17.5K | https://www.youtube.com/watch?v=Vp3tET-hNRs |
| 4 | Using proxies for web scraping | Apify | 5.3K | https://www.youtube.com/watch?v=ZFHXj_lQnOQ |
| 5 | This is How I Scrape 99% of Sites | John Watson Rooney | 365.4K | https://www.youtube.com/watch?v=ji8F8ppY8bs |
| 6 | How I Finally Bypassed Cloudflare Bot Detection | ven coding | 1.8K | https://www.youtube.com/watch?v=03R61xIzCow |
| 7 | Playwright Web Scraping + CAPTCHA Bypass Tutorial | Python Simplified | 70.9K | https://www.youtube.com/watch?v=RGR5Xj0Qqfs |
| 8 | Scrape Google Play Store App Reviews (SerpApi) | SerpApi LLC | 7.0K | https://www.youtube.com/watch?v=V-uc-Fi9SpI |

### 数据分析与情感分析（6 个视频）

| # | 标题 | 频道 | 播放量 | URL |
|---|------|------|--------|-----|
| 1 | End to End NLP Project \| Sentiment Analysis on Amazon Reviews | Satyajit Pattnaik | 105.2K | https://www.youtube.com/watch?v=6A2w-KYG4Ko |
| 2 | Python Sentiment Analysis Project with NLTK and Transformers | Rob Mulla | 534.2K | https://www.youtube.com/watch?v=QpzMWQvxXWk |
| 3 | Sentiment Analysis with BERT Neural Network | Nicholas Renotte | 154.3K | https://www.youtube.com/watch?v=szczpgOEdXs |
| 4 | AI Bot That Reads Market News and Predicts Sentiment | CodeTrading | 43.9K | https://www.youtube.com/watch?v=iW8NtsjTfN0 |
| 5 | TWITTER SENTIMENT ANALYSIS (NLP) | GeeksforGeeks | 211.4K | https://www.youtube.com/watch?v=4YGkfAd2iXM |
| 6 | Exploratory Data Analysis with Pandas Python | Rob Mulla | 673.9K | https://www.youtube.com/watch?v=xi0vhXFPegw |

---

*研究工具：YouTube + NotebookLM | 视频总数：38 个 | 生成：2026-04-12*
