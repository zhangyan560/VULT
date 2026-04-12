# VULT Git 维护指南

## 快速开始

### 1. 配置完成 ✅

Git 库已初始化在 `/Users/zhangyan/VULT/.git/`

```bash
# 当前状态
git status
git log --oneline -5
```

### 2. Obsidian Git 插件安装

#### 方式 A：从 Obsidian 社区插件市场安装（推荐）

1. 打开 Obsidian → 设置 → 第三方插件
2. 关闭「安全模式」
3. 浏览社区插件 → 搜索 `Obsidian Git`
4. 安装 Vinzent03 的 **Obsidian Git**
5. 启用插件

#### 方式 B：手动安装（如果社区市场无法访问）

插件文件已预配置在 `.obsidian/plugins/obsidian-git/`

### 3. 插件设置

打开 Obsidian 设置 → Obsidian Git，配置以下选项：

| 设置 | 值 | 说明 |
|------|-----|------|
| **Auto save interval** | 10 | 每 10 分钟自动提交一次 |
| **Auto pull interval** | 0 | 禁用自动拉取（避免冲突） |
| **Pull before push** | ✅ | 推送前先拉取 |
| **Show status bar** | ✅ | 显示状态栏 |
| **Auto backup after file change** | ✅ | 文件修改后自动备份 |

---

## 工作流

### 自动化流程（推荐）

**插件自动处理**：
- 每 10 分钟检测文件变化
- 自动 `git add` + `git commit` + `git push`
- 无需手动操作

**查看状态**：
- 打开 Obsidian 左侧边栏 → Source Control
- 或在状态栏看到「Git」图标

### 手动提交（如需精细控制）

```bash
# 查看变化
git status

# 添加文件
git add .

# 提交（必须包含 Co-Authored-By）
git commit -m "Update: 笔记描述

- 详细变动 1
- 详细变动 2

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# 推送
git push
```

---

## 提交规范

每次提交需遵循以下格式：

```
<type>: <subject>

<body>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

### 常见类型 (type)

| 类型 | 说明 | 示例 |
|------|------|------|
| `Add` | 新增内容 | `Add: Reddit 2026 市场洞察笔记` |
| `Update` | 更新现有内容 | `Update: 被动收入分类模型补充案例` |
| `Fix` | 修复错误 | `Fix: _index.md 链接错误` |
| `Refactor` | 重构笔记结构 | `Refactor: 商业研究 domain 分类` |
| `Delete` | 删除内容 | `Delete: 过期的 _MOC.md 文件` |

### Subject 规则

- 小写开头
- 50 字以内
- 不以句号结尾
- 使用祈使句（「Add」而非「Added」）

### Body 规则

- 说明「为什么」而不是「是什么」
- 每行 72 字以内
- 用 bullet list 列举变动

---

## 远程仓库配置

### 方式 A：GitHub（推荐）

```bash
# 1. 在 GitHub 上创建私有仓库 `VULT`
# 2. 添加远程

git remote add origin https://github.com/<你的用户名>/VULT.git

# 3. 推送
git branch -M main
git push -u origin main

# 4. 之后只需
git push  # 推送到 GitHub
```

### 方式 B：GitLab

```bash
git remote add origin https://gitlab.com/<你的用户名>/VULT.git
git branch -M main
git push -u origin main
```

### 方式 C：本地 bare 仓库（离线备份）

```bash
# 在另一块硬盘/NAS 创建裸仓库
git clone --bare /Users/zhangyan/VULT /Volumes/Backup/VULT.git

# 添加为远程
git remote add backup /Volumes/Backup/VULT.git
git push backup main
```

---

## 常见问题

### Q1：插件不显示「Source Control」怎么办？

**A**：
1. 确认插件已启用（设置 → 第三方插件 → Obsidian Git 启用）
2. 重启 Obsidian
3. 查看左侧边栏是否有「Git」图标（类似分支符号）

### Q2：自动提交失败了怎么办？

**A**：
1. 打开终端检查 git 状态
   ```bash
   cd /Users/zhangyan/VULT
   git status
   ```
2. 如有冲突，手动解决后提交
3. 检查是否配置了远程仓库
   ```bash
   git remote -v
   ```

### Q3：想暂停自动提交？

**A**：
- Obsidian 设置 → Obsidian Git → Auto save interval 改为 `0`
- 或禁用插件

### Q4：需要恢复历史版本？

**A**：
```bash
# 查看提交历史
git log --oneline

# 回到某个版本
git checkout <commit-hash>

# 创建新分支保存这个版本
git checkout -b restore-<date>
```

---

## 备份策略

### 三层备份（推荐）

| 层级 | 位置 | 更新频率 | 场景 |
|------|------|---------|------|
| **Layer 1** | `/Users/zhangyan/VULT/.git` | 实时（插件） | 日常工作版本 |
| **Layer 2** | GitHub/GitLab | 每天推送 | 异地备份、协作 |
| **Layer 3** | Time Machine / 外置硬盘 | 每周 | 灾难恢复 |

### 自动备份脚本（可选）

```bash
# 创建 ~/bin/backup-vult.sh
#!/bin/bash

cd /Users/zhangyan/VULT

# 推送到 GitHub
git push origin main

# 推送到本地备份
git push backup main

echo "VULT backup completed at $(date)"
```

然后配置 cron 每天执行：
```bash
crontab -e
# 添加行：0 23 * * * ~/bin/backup-vult.sh
```

---

## 工作流最佳实践

### ✅ DO

- 定期提交（10 分钟自动，或手动完成一个功能就提交）
- 提交信息清晰（他人能理解你做了什么）
- 使用分支进行大型重构（创建 `refactor/xxx` 分支）
- 定期推送到远程（避免本地版本丢失）

### ❌ DON'T

- 不要一次性提交太多变动（难以追溯）
- 不要跳过提交信息的 Body（为什么很重要）
- 不要在主分支进行大型实验（用分支）
- 不要忽视冲突警告（及时解决）

---

## 日常使用快速命令

```bash
# 查看状态
git status

# 查看最近 5 次提交
git log --oneline -5

# 查看文件变化
git diff <文件>

# 撤销未提交的修改
git checkout -- <文件>

# 查看远程状态
git remote -v

# 手动推送
git push

# 手动拉取
git pull
```

---

## 监控与告警

### 设置 Git Hook（可选高级）

如需在特定操作时自动触发动作（如生成文档、运行检查），可配置 Git Hooks：

```bash
# 在 .git/hooks/ 中创建 post-commit 脚本
# 示例：每次提交后自动生成 codemaps
```

---

## 支持文档

- [Obsidian Git 官方文档](https://github.com/Vinzent03/obsidian-git)
- [Git 官方教程](https://git-scm.com/doc)
- [GitHub 帮助中心](https://docs.github.com/en)

---

**最后更新**：2026-04-12
**VULT 版本**：v1.0（Git tracked）

