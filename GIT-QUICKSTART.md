# VULT Git 快速开始（5 分钟）

## ✅ 完成状态

- ✅ Git 库已初始化
- ✅ 127 个文件已提交（包括所有 wiki、inbox、projects、daily-notes）
- ✅ Obsidian Git 插件已配置
- ✅ 自动备份每 10 分钟触发一次

---

## 🚀 立即使用

### 第 1 步：在 Obsidian 中启用插件

1. 打开 Obsidian
2. 进入 **设置 → 第三方插件 → 社区插件**
3. 搜索 `Obsidian Git`（作者：Vinzent03）
4. 点击 **安装** → **启用**
5. 关闭设置

✅ 完成！Obsidian 左侧边栏应该出现「Git」图标

### 第 2 步：配置自动备份（可选）

在 Obsidian 设置 → **Obsidian Git**：

| 设置项 | 推荐值 | 说明 |
|--------|--------|------|
| Auto save interval | `10` | 每 10 分钟自动备份 |
| Disable popups | `✅` | 禁用弹窗提示 |
| Show status bar | `✅` | 底部显示 Git 状态 |

✅ 保存后，Obsidian 会自动在后台运行

### 第 3 步：配置远程仓库（推荐）

这样你的 VULT 会备份到云端。选择一个方案：

#### 方案 A：GitHub（最推荐）

```bash
cd /Users/zhangyan/VULT

# 1. 在 GitHub 上创建新私有仓库 "VULT"
# https://github.com/new

# 2. 添加远程并推送
git remote add origin https://github.com/<你的用户名>/VULT.git
git branch -M main
git push -u origin main

# 3. 完成！之后自动推送到 GitHub
```

#### 方案 B：GitLab

```bash
git remote add origin https://gitlab.com/<你的用户名>/VULT.git
git branch -M main
git push -u origin main
```

#### 方案 C：仅本地备份（无云端）

跳过这一步，仅在本地 `.git` 中维护历史记录

---

## 📊 查看备份状态

### 在 Obsidian 中

- 点击左侧边栏的 **Git 图标** → 查看最近提交
- 或在右侧 **Source Control** 面板监控

### 在终端中

```bash
# 查看状态
git status

# 查看最近提交
git log --oneline -10

# 查看文件变化
git diff
```

---

## 🎯 日常使用（无需操作）

自动运行 ✅：
- 每 10 分钟检测文件变化
- 自动 `commit` + 自动 `push`（如配置了远程）
- Obsidian 退出时自动最终提交

**你什么都不用做，专注写笔记即可！**

---

## 🆘 常见问题

### Q：Git 插件找不到？

A：确认已关闭「安全模式」
- 设置 → 第三方插件 → 右上角「关闭安全模式」

### Q：自动提交失败？

A：
```bash
# 查看错误
git status

# 手动提交
git add .
git commit -m "Manual commit"
```

### Q：想看提交历史？

A：
```bash
# 图形化查看
git log --graph --oneline --all -20

# 或在 GitHub/GitLab 上查看
```

### Q：需要恢复旧版本？

A：
```bash
# 查看历史
git log --oneline

# 回到某个版本
git checkout <commit-hash>

# 创建分支保存
git checkout -b recover-<date>
```

---

## 📋 提交规范（仅当手动提交时）

```bash
git commit -m "Type: 简短描述

- 详细点 1
- 详细点 2

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

常见类型：`Add`, `Update`, `Fix`, `Refactor`, `Delete`

---

## 📁 目录结构（已备份）

```
VULT/
├── wiki/                    ← 所有知识库笔记（按 domain 分类）
├── inbox/                   ← 原始数据备份
├── projects/                ← 个人项目
├── daily-notes/             ← 日记
├── output/                  ← 导出报告
├── _master-index.md         ← 全局导航
├── .git/                    ← Git 历史记录
├── .gitignore               ← Git 规则
└── GIT-SETUP.md            ← 详细指南
```

所有内容都被 Git 追踪 ✅

---

## 🔄 三层备份架构

| 层 | 存储 | 频率 | 恢复时间 |
|----|------|------|---------|
| **1** | `/Users/zhangyan/VULT/.git` | 实时 | 秒级（本地） |
| **2** | GitHub/GitLab 云端 | 每 10 分钟 | 分钟级（下载） |
| **3** | Time Machine / 外置硬盘 | 每周 | 小时级（恢复） |

---

## ✨ 后续优化

### 可选：自动 push 到远程

如果希望更频繁地 push（默认仅自动 commit）：

在 Obsidian 设置 → Obsidian Git：
- `Auto push interval` = `10`（每 10 分钟推送一次）

### 可选：设置 GitHub Actions 自动生成文档

在仓库中添加 `.github/workflows/` 来自动生成 README、目录等

---

## 📞 需要帮助？

查看完整指南：[[GIT-SETUP.md]]

或参考官方文档：
- [Obsidian Git GitHub](https://github.com/Vinzent03/obsidian-git)
- [Git 官方文档](https://git-scm.com/doc)

---

**配置完成时间**：2026-04-12
**VULT 已备份**：✅ Yes（共 2 次提交）
**远程配置**：⏳ 待你连接 GitHub/GitLab

