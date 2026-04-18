  

**面向对象**：AI Champion、数据分析师、产品经理、希望深度使用 AI 的员工

  

**课程目标**：

- 理解 Agent / Rule / MCP / Skill 的工作机制，建立进阶使用的概念框架
    
- 会用 Cursor / Claude Code 为代表的工作台完成真实任务
    
- 配置内部 MCP 服务，封装可复用 Skill，建立团队级 AI 资产
    
      
    

**前置要求**：已完成 L1 课程，能熟练使用 ChatGPT 或 Gemini 完成日常任务

  

**对应工具**：Cursor、Claude Code

  

---

  

## 第一章：从 Chat 到 Agent——为什么只会聊天已经不够

  

### 1.1 L1 课程解决了什么问题

  

L1 课程帮你建立了对 AI 的基本认知，学会了写有效的提示词，掌握了 ChatGPT、Gemini 等对话型工具的使用方法。

  

但用久了，你会遇到新的瓶颈：

- **"每次都要重新说背景，太烦了"** ——今天告诉 AI 你是财务，明天开新对话还得再说一遍
    
- **"AI 的输出格式总是不对，要反复调整"** ——每次都要在提示词里重写格式要求
    
- **"有些任务每周都要做，能不能自动化"** ——同样的分析流程手工重复执行
    
- **"团队里其他人怎么用我好不容易摸索出来的方法？"** ——经验积累在个人，无法传递
    
- **"我的** **AI 怎么才能真正帮我自动化****？"**——希望它能自己读取和操作其他系统，替我完成任务
    
      
    

这些问题的根本原因是：**Chat 类工具的设计边界**。

  

### 1.2 Chat 类工具适合什么，不适合什么

  

Chat 类工具（ChatGPT、Gemini、Claude 网页端等）本质上是**多轮对话助手**——你输入问题，它返回答案，每次对话相互独立。

**Chat 类工具的强项**：

- 文案写作、翻译、总结
    
- 通用问答、思路梳理
    
- 单次任务的快速处理
    
- 文件上传、图片识别等有限的工具调用
    
      
    

**Chat 类工具的局限**：

|局限|具体表现|
|---|---|
|上下文不持久|每次对话需重新交代背景，无法记住你的偏好和项目信息|
|无法连接外部系统|不能主动读取飞书文档、操作数据库、调用内部 API|
|任务是一次性的|无法自主规划多步骤任务，无法在中途调整执行路径|
|经验无法沉淀|好的提示词只存在你自己脑子里，无法变成团队资产|

  

### 1.3 为什么真实工作需要 AI 围绕目标持续推进

  

Chat 类工具的局限，不只是"步骤多"的问题——而是它**根本无法触碰你的真实工作环境**。

  

来看一个每月都要做的真实任务：**生成月度 VAT 对账报告**。

  

**用 Chat 工具的做法**：

1. 手动打开服务器或本地文件夹，找到这个月的 Excel 数据文件
    
2. 打开 Excel，把关键数据手动复制粘贴到 ChatGPT 对话框
    
3. 告诉 AI 怎么分析，等它输出文字结果
    
4. 把输出内容手动复制出来，粘贴进报告模板
    
5. 手动调整格式，保存文件，上传到飞书
    
6. **下个月，从第 1 步重来**
    

Chat 工具在这里做的，其实只有第 3 步——回答你粘贴进来的问题。其余所有步骤，**都是你在做**。

  

**用 Agent 的做法**：

```Plain
本月 VAT 对账报告，原始数据在 ./data/vat_2025_04.xlsx，对应要求如下：
1.按发票类型（FV/VAT-UE/VAT-IMP）分组汇总
2.标注异常记录（VAT-UE 金额不为 0、单笔 VAT 超过 3,000 PLN）
3.核对分类合计与总计行，误差不超过 0.01 PLN
4.生成标准 Markdown 汇总报告，保存至 `./reports/`
5.上传飞书个人空间归档
```

Agent 自动完成全部步骤：读取文件 → 执行分析计算 → 生成报告 → 保存文件 → 调用飞书 MCP 上传。**你只需要最后核查结果。**

  

**两者的本质差距**：

|能力|Chat 工具|Agent|
|---|---|---|
|读取你本地的文件|❌ 需要你手动粘贴内容|✅ 直接访问文件系统|
|运行代码、处理数据|❌ 只能描述怎么做|✅ 真正执行并产出结果文件|
|连接飞书、数据库等系统|❌ 无法访问|✅ 通过 MCP 直接操作|
|自主完成多步骤|❌ 每一步都需要你驱动|✅ 围绕目标自主推进到完成|
|下次重复同样任务|❌ 还是要从头来|✅ 封装成 Skill，一行命令搞定|

Chat 工具是一个**只能坐在那里回答问题的顾问**——你得把材料带来，听完建议还得自己去执行。Agent 是一个**能直接进你的系统、动手把事情做完的助理**。

  

### 1.4 Agent：从"回答问题"到"完成任务"

**Agent（智能体）**，就是让 AI 从"回答问题"升级到"完成任务"的关键。

如果说普通 AI 是一个"只会说话的顾问"，那 Agent 就是一个"能动手干活的助理"。

  

**L2 课程要解决的，正是这些问题**：

|概念|解决的问题|
|---|---|
|**Rule / CLAUDE.md**|持久化上下文，告别每次重新交代背景|
|**MCP**|连接外部系统，让 AI 能读取飞书、查询数据库、调用工具|
|**Skill**|封装流程，把个人经验变成团队可复用的能力|
|**Agent 模式**|自主规划和执行多步骤任务|

本课程对应工具：**Cursor 和 Claude Code**——这类"工作台"工具，是 Agent 能力的主要载体。

  

---

  

## 第二章：Agent 基础——AI 是如何围绕目标完成任务的

### 2.1 Agent 是什么

**Agent = 能够自主规划和执行任务的 AI 系统**

  

普通 Chat AI 的工作方式：你说 → 它回 → 结束

Agent 的工作方式：你给目标 → 它规划步骤 → 它调用工具 → 它执行 → 它验证结果 → 它调整策略 → 直到完成目标

Agent 不只是"更聪明的 AI"，它是一个**有目标感的执行系统**。

  

### 2.2 Agent 和普通聊天 AI 的区别

|维度|普通 Chat AI|Agent|
|---|---|---|
|工作单位|一问一答|目标 → 完成|
|执行能力|只输出文本|可以调用工具、操作文件、执行代码|
|规划能力|无|自动拆解任务步骤|
|上下文|对话窗口内|跨会话持久记忆|
|纠错能力|靠人追问修正|自动反思和调整策略|
|适合任务|单次问答|多步骤、需要工具的复杂任务|

  

### 2.3 Agent 的典型能力模块

  

#### ① 上下文 / Memory（记忆）

AI 在整个任务执行过程中保留的信息，包括：

- 项目背景
    
- 历史操作
    
- 中间结果
    

👉 **扩展说明：**

- 持久化记忆（如 Rules / CLAUDE.md）可以让 AI 在每次启动时都“认识你”
    

---

#### ② Planning（规划）

Agent 在接收到目标后，会先进行任务拆解，并安排执行顺序。

👉 **示例：** 当被要求做「竞品分析」时，Agent 会自动规划：

1. 搜索资料
    
2. 整理信息
    
3. 分析对比
    
4. 输出报告
    

---

#### ③ Tool Use（工具调用）

Agent 可以调用外部工具获取信息或执行操作。

👉 **常见方式：**

- 通过 MCP 连接：飞书文档、数据库、API 接口、搜索引擎等
    
- 通过 Skill 调用封装好的标准流程
    

---

#### ④ Act / Reflect（执行与反思）

**执行（Act）：**

- 运行代码
    
- 写入文件
    
- 调用 API
    

**反思（Reflect）：**

- 检查执行结果是否符合预期
    
- 若存在偏差，自动调整策略并再次执行
    

  

### 2.4 Agent 如何完成一个任务

  

**任务**："帮我分析本月竞品动态，生成一份竞品报告"

**Step 1｜规划**：Agent 把任务拆解为 ①搜索竞品最新动态 ②整理关键信息 ③对比分析 ④生成报告

**Step 2｜执行（调用工具）**：通过搜索 MCP 获取竞品新闻，通过飞书 MCP 读取上月报告，通过 Skill 调用"竞品分析报告模板"

**Step 3｜判断**：Agent 检查搜集到的信息是否完整，发现某竞品数据不足

**Step 4｜反思 + 调整**：自动追加搜索该竞品的官方博客和发布记录

**Step 5｜输出**：生成符合模板格式的竞品报告，保存到本地文件夹

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NjdiYjYzOWMyYmM5M2E2NTY4MGJmMDQ5NDk5NzA3ODdfS2o1YjZVY3NaaGVOalZESzhYbXh1N2JMNmhjQ1Fnck1fVG9rZW46QjFCMmJFbmxtb1Exbmd4UXRoQmNKNGxubk1FXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

  

### 2.5 三者的协同：MCP + Skill + Agent

Agent 在执行过程中同时用到了 MCP 和 Skill——这三者不是独立的，而是协同工作的整体：

- **MCP** 负责"连接"——让 Agent 能接触到外部世界的数据和工具
    
- **Skill** 负责"复用"——把人工摸索的最优流程固化下来
    
- **Agent** 负责"完成"——调度 MCP 和 Skill，把目标变成结果
    

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MTczODliNjFhMmU0MjhiMzliMTYzZTg1NDE5Njg1MTFfT1pzR1FqeUQybEQ1STVwaHFtcll4aG1oYnVaWW1QdWNfVG9rZW46U2VoT2JxeWVCb0M0R2J4RnkzYWN4UWhSbk5lXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

  

### 2.6 常见产品形态：Cursor / Claude Code 这类工具

  

目前市场上 Agent 工具分两类：

  

**代码 / 文档工作台类（本课程重点）**

- **Cursor**：基于 VS Code 的 AI 工作台，界面友好，适合非技术同学入门
    
- **Claude Code**：终端原生 Agent，功能更强大，适合有一定技术基础的用户
    
      
    

**通用 Agent 平台类**

- Manus、Coze、Dify 等——适合构建自动化工作流
    
      
    

> 本课程重点介绍 Cursor 和 Claude Code。

  

#### **Cursor 界面快速入门**

Cursor账号申请流程：[Cursor/Junie/Qcli账号申请及配额提升说明](https://fintopia.feishu.cn/wiki/Lbmmwj8EuiyzJ9kKpKFcf3jfnYg?from=from_copylink)

Cursor安装教程：[Cursor安装教程](https://cursor.com/cn/docs/get-started/quickstart)

安装并登录后，选择工作目录，进入主界面：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ODgxYTdkOTYwMGVmYzU1ZjBmODBmM2FlMTg0Mjc3NzBfdEdHbEF6OFpGZmI3TlFTdTdqUEd0dnlMOWhzT2N2Ym9fVG9rZW46U1pyamI5R1VIb09rWDh4MEJ6MWNvUDN0bk1XXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Cursor 欢迎界面

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NzE1MzhlNGQ0MjZiYWZjYTRiZjk1NmExNmVlOGEwYThfTm9xOXBKZWtldGpvT3FOTzlxSEplQTNoR2VlOTlNYVlfVG9rZW46T3RheGJFVVd5b2VXSFF4bXZvOGNxaUJPbk1iXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Cursor 主工作界面

右侧 Chat 窗口用自然语言描述需求即可开始工作。Cursor 提供四种工作模式（点击输入框左侧切换）：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NGNjZDg1ZGY3ZWUxMjMyNmIzYmNkZWU1NThhMDUwZDhfelNhT1NJenFjeU1vTktQZFZQdDRoNEdmd2I0SkZjQ1pfVG9rZW46UGpwY2JJTnppb1NTYlR4bGp3OGN0V0Jzbm1iXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Cursor 四种工作模式

Cursor 支持多种 AI 模型，可在对话框底部切换：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=M2Y2NzE1OGYyMzRmYmJmMWExZjE4MDA1OTk2NTZiZjhfQ280NDZLQjdmTlllUERmSTQ2QnlrOVlVQjlLQ2tCZGFfVG9rZW46UXVKT2IzczRMb2o2NXV4VTFvdWNjQzVCbnNmXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Cursor 模型切换

  

#### **Claude Code 界面快速入门**

**安装教程**

[Claude code一键安装](https://fintopia.feishu.cn/wiki/FwLewJpBui2m1EkDs54cfE2XnKg)

在终端启动后，显示欢迎界面：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDk0YmZiNThjNWI5NjY5OTNiYmMyYWU1NTdmNmI4MGNfb25ZUEppNU8xY1U1MjR3d3NoVDY2UXVBb0M0UVRnMGlfVG9rZW46S3A5U2JSbWc1b2RSNDh4UXVLT2NtR0tZblZFXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Claude Code 欢迎界面

界面说明：

- **左侧**：显示当前用户名、当前使用的模型（如 `Sonnet 4.5 with high effort`）、计费方式（API Usage Billing）和当前项目路径
    
- **右侧**：快速入门提示（Tips for getting started），提示可以运行 `/init` 来生成 CLAUDE.md；以及最近的活动记录（Recent activity）
    
- **底部输入框**：即可输入你的需求，开始工作
    

  

欢迎界面消失后，进入简洁的主工作界面：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ZjE4NmJlOGFhNzk3NWM4MDg1MDdjMDk3ZjI0ZTQ2NDNfeGtXc3dZZnZrZ2gwSlRpbWhIZ3FWM3dXOWdEM1B3d05fVG9rZW46TWR5WWJpcGR6bzI3MTF4RkhjMGN4ekl3bmJnXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Claude Code 主工作界面

界面说明：

- **顶部**：版本号（v2.1.84）、当前模型和项目路径
    
- **输入提示符** **`>`**：在此输入任务需求
    
- **底部提示**：输入 `?` 可查看快捷键列表
    

> 提示：每完成一个独立任务后，输入 `/clear` 清空上下文，避免上下文干扰下一个任务。

  

在执行任务时，可以看到实时的过程反馈：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NDY2MDc2ZTAxMWJmZGJkMzJhOTQxN2JkOGIzNzZlMGZfWE5ZOGxzbUp0V1k5b1ZMQW1DZGJDTjdleGppMkM5UVlfVG9rZW46UVRHNWJSY0tib2dmaUN4ejJ1OWN5cWx3bkNnXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Claude Code 执行反馈界面

  

延伸资料： [吴恩达agent教程课](https://www.bilibili.com/video/BV1DfrdByE2H/?spm_id_from=333.337.search-card.all.click)

[黑马程序员大模型RAG与Agent智能体项目实战教程](https://www.bilibili.com/video/BV1yjz5BLEoY/?spm_id_from=333.337.search-card.all.click)

[AI 核心概念大串联](https://www.bilibili.com/video/BV1E7wtzaEdq/?spm_id_from=333.337.search-card.all.click)

  

---

## 第三章：持久化上下文——如何让 AI 稳定理解要求

  

---

### 3.1 为什么每次重复交代背景很低效

  

> "你好，我是 Fintopia 财务部的分析师，我们公司主要做……我现在需要……输出格式要用中文，金额带 PLN，报告存到 reports 文件夹，FV 是国内发票，VAT-UE 是跨境的税率是 0……"

  

每次开新对话都要从头说背景——不只是麻烦，更是实实在在的浪费：这段话本身就要消耗几百个 token，AI 才能开始真正"干活"。

  

而且背景说得越模糊，输出就越偏——这不是 AI 不够聪明，是它根本不知道你的项目规则。

  

**根本原因**：工作台工具每次对话是独立的，AI 没有跨会话的"记忆"。

---

  

### 3.2 **持久化上下文在解决什么问题**

  

持久化上下文，在不同工具里叫法不同：在 Cursor 里，它叫 Rules，存储在 .cursor/rules/*.mdc；在 Claude Code 里，它叫 CLAUDE.md。形式不同，解决的是同一个问题——把「每次对话都需要 AI 知道的事」写进配置文件，工具在启动时自动注入，省去每次重复交代的麻烦

  

**Rule / CLAUDE.md** 是工作台工具提供的**持久化配置机制**。

  

把项目背景、工作偏好、输出规范写进配置文件，AI 每次启动时自动读取整个会话——相当于给 AI 配置了一份"永久入职说明书"，从第一句话起就已经了解你的项目。

  

> 你写什么，AI 就遵守什么。告诉它"金额带 PLN、报告存 ./reports/"，它整个会话里的每一次输出都会遵守。这不是魔法，就是上下文注入——但用好了威力很大。

  

**两个工具的对应关系**：

|工具|主配置文件|个人私有覆盖|模块化拆分|
|---|---|---|---|
|Claude Code|`CLAUDE.md`（项目根目录）|`CLAUDE.local.md`|`.claude/rules/*.md`|
|Cursor|`.cursor/rules/*.mdc`|User Rules（Settings）|多个 `.mdc` 文件|

---

  

### 3.3 配置文件的层级结构

不管使用 Cursor 还是 Claude Code，配置都支持多个层级。对大多数同学来说，只需要关注两个层级：

• 团队层：写项目里所有人都需要遵守的规范，提交 Git，新人克隆项目即可生效 • 个人层：写只属于你自己的偏好，不进 Git，不影响其他人

|**层级**|**Claude Code**|**Cursor**|
|---|---|---|
|团队层（提交 Git）|CLAUDE.md（项目根目录）|Project Rule（.cursor/rules/*.mdc）|
|个人层（不进 Git）|CLAUDE.local.md|User Rule（Settings 里设置）|

这两层覆盖了日常 90% 的使用场景，团队协作中最常见的配置结构。

  

两个工具都支持多层配置，越具体的层级优先级越高，下层配置会覆盖上层。

**【扩展参考】完整层级结构（供需要深入了解的同学参考）**

**Claude Code：6 个层级**

|层级|文件位置|用途|是否提交 Git|
|---|---|---|---|
|1. 组织策略|`/etc/claude-code/CLAUDE.md`|公司级别约束|—|
|2. 项目团队|`./CLAUDE.md`|团队共享，**最常用**|✅ 提交|
|3. 模块规则|`.claude/rules/*.md`|按模块拆分，支持路径作用域|✅ 提交|
|4. 个人全局|`~/.claude/CLAUDE.md`|个人偏好，对所有项目生效|❌ 不提交|
|5. 个人项目|`./CLAUDE.local.md`|个人对当前项目的覆盖，**最常用**|❌ 不提交|
|6. 自动记忆|`~/.claude/projects/`|Claude 通过 `/memory` 自己写入的关键信息|—|

实际使用中，最常用的是 **第 2 层 + 第 5 层** 组合：

- `CLAUDE.md`：写团队都要遵守的规则，提交 Git，人人共享
    
- `CLAUDE.local.md`：写只属于你的偏好，加入 `.gitignore`，不影响别人
    
      
    

**Cursor：4 个层级**

|层级|配置位置|用途|是否提交 Git|
|---|---|---|---|
|1. 个人全局|Settings → User Rule|个人偏好，对所有项目生效|❌ 不提交|
|2. 项目共享|`.cursor/rules/*.mdc`（Project Rule）|团队共享，**最常用**|✅ 提交|
|3. 模块规则|`.cursor/rules/` 下多个 `.mdc`（Glob 模式）|针对特定文件类型按需加载|✅ 提交|
|4. 旧格式兼容|`.cursorrules`（项目根目录）|旧版格式，已不推荐使用|✅ 提交|

  

**两个工具的对比一览**：

|对比项|Claude Code|Cursor|
|---|---|---|
|团队共享配置|`CLAUDE.md`|Project Rule（`.cursor/rules/*.mdc`）|
|个人私有覆盖|`CLAUDE.local.md`（gitignore）|User Rule（Settings）|
|模块化拆分|`.claude/rules/*.md`（支持 paths 作用域）|多个 `.mdc` 文件（支持 Glob 匹配）|
|文件格式|标准 Markdown|Markdown + YAML frontmatter|
|自动生成|`/init` 命令扫描项目生成|对话后让 Cursor 帮你生成|
|自动记忆|`/memory` 命令写入|无对应机制|

  

---

### 3.4 什么适合写进 Rule 或 CLAUDE.md

  

两个工具的配置文件格式不同，但判断逻辑一致。

  

**核心判断标准：如果这件事在这个项目的每次对话里都需要 AI 知道，就写进配置；如果只是这次任务需要，写进提示词。**

  

**Claude Code —** **`CLAUDE.md`** **/** **`CLAUDE.local.md`**

✅ **`CLAUDE.md`****（团队共享）该写**：项目背景、文件路径约定、业务术语、输出规范、禁止事项

✅ **`CLAUDE.local.md`****（个人私有）该写**：个人回复偏好、个人工作习惯、本机私有路径

  

❌ **两者都不该写**：

|不该写的内容|原因|应该放哪里|
|---|---|---|
|代码格式规则（缩进、引号等）|应由 `.prettierrc` / `eslint` 统一管理|linter 配置文件|
|临时任务描述|这是提示词，不是规则|对话提示词|
|完整文档链接|Claude 无法读取链接，浪费 token|用 `@file` 引用本地文件|
|API Key、密码、Token|安全红线，绝对禁止|环境变量|
|长篇技术原理|指令要精炼，越短遵守度越高|另存参考文档|

**该放什么、不该放什么：**

|该放的|不该放的|
|---|---|
|Claude 猜不到的构建命令（如 `make run-dev`）|Claude 看代码就能知道的东西|
|与默认不同的代码风格规则|标准语言规范（"写干净的代码"）|
|测试方式和偏好的测试框架|详细 API 文档（给链接即可）|
|分支命名、PR 规范|频繁变化的信息|
|架构决策和项目特有的坑|一目了然的内容|
|业务背景、指标定义（团队共用）|个人偏好（放个人 Skills）|

> **关键原则：简洁、清晰、长期有效**
> 
> **写 CLAUDE.md 的目标不是"越短越好"，而是让每一行都能稳定影响模型行为——短只是保持清晰度的常见结果，不是目标本身。**
> 
> **对每一行问自己："删掉这行会让 Claude 犯错吗？" 如果不会，就删；但有效的规则不该为了凑短而砍掉。太长反而让 Claude 忽略真正重要的指令，所以冗余内容要删，有价值的规则要留。**

  

⚠️ **`CLAUDE.md`** **建议控制在 200 行以内**。通常建议在 200 行左右。这不是硬规则，而是经验值——关键在于是否影响模型对重点约束的识别。若文件已经很长，先检查是否有冗余内容可以删减；如果每行都有实际作用，超过 200 行也是合理的。

  

**Cursor — User Rule / Project Rule**

✅ **User Rule（个人全局）该写**：个人通用偏好，适用于所有项目，不区分业务场景

✅ **Project Rule** **`alwaysApply: true`****（每次加载）该写**：项目核心背景、必须遵守的输出格式、禁止操作清单

✅ **Project Rule Glob 模式（按需加载）该写**：针对特定文件类型的规范（如只在处理 `.xlsx` 时才需要的数据处理规则）

  

❌ **不该写**：代码格式规则（放 `.editorconfig`）、临时任务、API Key、超过 500 字的长文背景

⚠️ **单个** **`.mdc`** **文件建议控制在 500 字以内**。这是经验值，不是固定上限——项目复杂时，拆成多个文件分模块管理比强行压缩更有效；关键看每条规则是否都能被模型清晰识别。

  

---

### 3.5 实战样例背景：VAT 对账项目

  

**如果没有 Rule / CLAUDE.md，会发生什么？**

  

Fintopia 波兰子公司财务部，每月月末需要处理供应商开具的 VAT 对账单（Excel 格式），生成标准汇总报告，上传飞书归档。

这是一个真实的月度任务。在没有任何配置的情况下，**每次打开新对话，你都要从头交代一遍：**

```Plain
你好，我是 Fintopia 财务部的分析师，
我们需要处理波兰子公司的 VAT 对账单，
数据文件在 ./data/ 目录，命名规则是 vat_YYYY_MM.xlsx，
报告要存到 ./reports/ 目录，
发票分三种类型：FV 是国内普通发票税率 23% 或 8%，
VAT-UE 是 EU 跨境服务 0% 税率 VAT 金额应为 0，
VAT-IMP 是进口货物由海关代征……
金额格式要带 PLN 加千位逗号，两位小数，
报告要包含执行摘要、分类汇总表、异常标注和核对结论，
单笔 VAT 超过 3,000 PLN 要加粗，
各分类合计之和必须等于总计行误差不超过 0.01 PLN，
不要修改原始文件……
```

**这段话超过 150 个字，每月重复一次。** 而且说得越潦草，输出越偏——哪次忘了说"VAT-UE 的 VAT 金额应为 0"，AI 就不会帮你做这项校验。

  

---

**这个任务，为什么特别适合写进项目配置文件？**

不是所有任务都值得写配置文件。这个场景有三个特点，让它成为 **Rule / CLAUDE.md 的典型候选**：

|特点|具体表现|对配置的意义|
|---|---|---|
|**重复性高**|每月执行，流程固定，换月只是文件名不同|规则写一次，长期复用|
|**规则明确**|发票类型固定分类、金额有格式要求、报告有结构规范|规则清晰，适合精确描述|
|**需要校验**|必须核对分类合计与总计行，有明确验收标准|校验逻辑写进配置，每次自动执行|

> **判断标准**：如果一件事在这个项目的**每次对话**里 AI 都需要知道，就写进配置——这正是 Rule / CLAUDE.md 要解决的问题。

---

**数据说明**

vat_2025_04.xlsx

原始数据文件 `vat_2025_04.xlsx` 包含 20 条发票记录，涉及三种发票类型：

|发票类型|含义|税率规则|
|---|---|---|
|FV|国内普通 VAT 发票|23%（标准）或 8%（低税率，餐饮/印刷品）|
|VAT-UE|EU 跨境服务发票|0%，买方反向征税，VAT 金额应为 0|
|VAT-IMP|进口货物发票|23%，由海关代征，需单独列示|

本月数据：税前合计 **150,630.00 PLN**，VAT 合计 **23,077.40 PLN**。

  

**任务目标**

每月执行以下固定流程，生成一份符合规范的汇总报告：

```Plain
读取 Excel → 按发票类型分组汇总 → 标注异常记录
→ 核对各分类合计 → 生成 Markdown 报告
```

  

---

  

### 3.6 在 Claude Code 里怎么配置对应的CLAUDE（含实操）

#### 理论：五步配置流程

  

**第一步：用** **`/init`** **生成初始版本**

在 Claude Code 中输入 `/init`，Claude 会自动扫描项目结构并生成一份初始 `CLAUDE.md`。生成后手动精简到核心内容，不要照单全收。

  

**第二步：写团队共享的** **`CLAUDE.md`**

聚焦"团队规则"：路径约定、术语定义、输出格式、禁止事项。控制在 100 行以内。

  

**第三步：写个人私有的** **`CLAUDE.local.md`**

把只属于你的偏好写在这里，并将文件名加入 `.gitignore`，不影响团队其他人。

  

**第四步：用** **`.claude/rules/`** **模块化拆分（项目复杂时）**

当 `CLAUDE.md` 开始变长，把不同模块的规则拆到独立文件，支持路径作用域——只在处理特定目录的文件时才加载，避免无关规则占用上下文。

  

**第五步：用** **`/memory`** **让 Claude 自动维护记忆**

会话中遇到重要结论或约定，输入 `/memory`，Claude 会把当前对话中的关键信息自动写入记忆文件，比手动维护高效得多。

  

---

#### 实操：VAT 对账项目的 Claude Code 配置

**① 创建** **`CLAUDE.md`****（团队共享，提交 Git）**

在对应的项目文件夹下，构建对应的**`CLAUDE.md`** **文件**

```Markdown
# Project: Fintopia VAT 对账

## 项目背景
Fintopia 波兰子公司财务部，处理每月供应商 VAT 对账单，生成汇总报告。

## 文件路径
- 原始数据：./data/（命名规则：vat_YYYY_MM.xlsx）
- 输出报告：./reports/（命名规则：vat_report_YYYY_MM.md）
- 报告模板：./templates/vat_report_template.md

## 发票类型
- FV：国内普通 VAT 发票，税率 23%（标准）或 8%（低税率）
- VAT-UE：EU 跨境服务，0% 税率，买方反向征税，VAT 金额应为 0
- VAT-IMP：进口货物，海关代征 VAT，单独列示

## 输出规范
- 所有输出用中文
- 金额格式：两位小数 + PLN + 千位逗号，例：12,500.00 PLN
- 报告必须包含：执行摘要 / 分类汇总表 / 异常标注 / 核对结论
- 单笔 VAT 超过 3,000 PLN 的记录用**加粗**标注

## 核对要求
- 各分类合计之和必须等于总计行，误差不超过 0.01 PLN
- VAT-UE 类发票 VAT 金额如不为 0，标记为数据异常
- 报告末尾注明"数据已与原始文件交叉核验"

## 禁止事项
- 不要修改 ./data/ 目录下的原始文件
- 不要把 API Key 或数据库密码写入任何文件
```

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MjYwMTdhMDBmNDdkNzA4MzIxOTdhYjFlZjFkN2UwMTNfMHBvZ0FxY3FPUTRTR0NENk9ZNjJTdVpPQ0lQOFlDV2dfVG9rZW46RnZIdmJ0SUxCb2JMVll4Z3JMMGMzeXAzbk1iXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**② 创建** **`CLAUDE.local.md`****（个人私有，加入** **`.gitignore`****）**

```Markdown
# 我的个人偏好（不提交 Git）
- 用中文回复
- 操作前先告诉我你打算做什么，等我确认再执行写操作
- 遇到数据异常先问我，不要自己判断怎么处理
- 计算结果给我看中间过程，不只给最终数字
```

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NDM1YzJmMDQ3YTJkNzFhYmY5Mjk0NDk5MTE3ZTk4MDZfVzFyV2NlclFrOTRLZU8wNEtwdkRZNWFTRWVYRHVpSGRfVG9rZW46U3lmTmJhNW90b2ZNTXp4SjhpbWNJeUpvbkF0XzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**③ 创建** **`.claude/rules/data-rules.md`****（指定路径作用域，按需加载）**

```Markdown
---
paths:
  - "data/**/*.xlsx"
  - "data/**/*.csv"
---
# 数据文件处理规则
- 读取 Excel 前先输出：列名列表 + 前 3 行数据，等我确认结构正确后再继续
- 处理结果另存新文件，不覆盖原始数据
- 发现空值或格式异常的单元格，列出位置后询问处理方式
```

> 这条规则只在 Claude 处理 `data/` 目录下的 `.xlsx` 或 `.csv` 文件时才加载——处理报告文件时不会出现，精准控制上下文。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MzY5YTg1ZDVhYmMxMDk2MjEyOWVlYTU3MjQwNWY0ZWRfZHlGd2ZHTDZNSkx1bWhyS0JFbWhQWkJWRDU5b3d1Z0tfVG9rZW46UWxJcmJBa0dub21mdWF4RXN3UWN3TVhYbldkXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

其实除了**我们人工总结项目维度需要注意的一些规则和共性内容构建对应的CLAUDE.md文件，也可以在一个任务完成后，让claude code自己帮我们总结更新对应的文件，在任务完成的会话中输入如下文本**：

```SQL
任务完成后帮我更新对应项目下的 CLAUDE.md 文件
```

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MDMxY2IyM2FlMDk1YWZlZjZhNjgyYmZhNWNiMDUzZTZfNFJnWGlXTHlKWEFBZjE1bWZWUk5jQkhPU2FKanB4T2lfVG9rZW46VTZPR2JOeU5Qb1IwR3R4clFzV2NtZlZnbktmXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Claude 自己会提炼任务流程中你告诉他的一些关键信息，例如：数据格式、数据字段含义、输出的样式等

**④ 配置完成后，每次只需一句话**

```Plain
处理 ./data/vat_2025_04.xlsx，生成本月 VAT 对账报告
```

Claude 自动知道：**先确认数据结构、发票类型怎么分、金额格式是什么、报告存哪、核验逻辑是什么、遇到异常怎么处理。全在配置里，不需要每次在提示词中重复**。

  

**⑤ 效果对比**

||配置之前|配置之后|
|---|---|---|
|每次对话的开场白|100+ 字的背景说明|一句话任务描述|
|输出格式|每次不一样，反复调整|始终符合规范，拿到即用|
|新同事上手|口头交接一遍规则|克隆项目，配置自动生效|
|核验逻辑|靠记忆、靠每次提示词|固化在配置里，自动执行|
|个人偏好 vs 团队规范|混在一起，互相干扰|CLAUDE.md / CLAUDE.local.md 分层管理|

---

  

### 3.7 在 Cursor 里怎么配置（含实操）

#### 理论：User Rule vs Project Rule

**入口**：`Cursor Settings（Cmd/Ctrl + ,）→ 左侧导航 Rules, Skills, Subagents`

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MDg1ZjI3MGVmZjI3YWQ5Mzk3OWU4MGVmZmQwNmY3ZTdfc1V4TlhqSmp2MXhoTXRaanNmY3FrM2YxRlpZNEQ3VkNfVG9rZW46TjFaTmJiY0hKb1VPSHp4UHNlZWNTdXl0bllmXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

进入后，顶部有三个 Tab：**All**（全部）/ **User**（个人规则）/ **项目名**（当前项目规则）。点击右侧 `+ New` 按钮，出现三个选项：

---

  

**① User Rule — 个人全局规则**

- **作用范围**：你在 Cursor 里打开的**所有项目**都生效
    
- **存储位置**：Cursor 内部，不对应项目目录下的任何文件，不会进入 Git
    
- **适合写**：只属于你的个人习惯，与具体项目无关
    
      
    

> 截图中 "Always respond in 中文" 就是一条 User Rule——无论打开哪个项目，Cursor 都会用中文回复。

  

---

  

**② Project Rule — 项目专属规则**

- **作用范围**：仅在**当前项目**中生效
    
- **存储位置**：项目根目录 `.cursor/rules/` 目录，扩展名 `.mdc`，可提交 Git 与团队共享
    
- **适合写**：项目背景、路径约定、业务术语、输出规范、禁止事项
    

`.mdc` 文件通过 YAML frontmatter 控制加载时机，支持四种模式：

|模式|配置方式|加载时机|适合场景|
|---|---|---|---|
|**Always**（始终加载）|`alwaysApply: true`|每次对话都加载|项目基础背景、核心规范|
|**Auto Attached**（自动匹配）|`globs: ["**/*.py"]`|上下文中有匹配文件时自动加载|语言特定规范（如 Python 风格）|
|**Agent Requested**（AI 按需调用）|只写 `description`，其余不填|AI 判断当前任务需要时自动引入|特定场景的参考规范|
|**Manual**（手动引用）|frontmatter 全部留空|在对话中用 `@rule名称` 显式引用|不常用、按需查阅的参考资料|

> 截图中 "CLAUDE" 规则后面跟着路径 `context-hub/plugins/project-plugin-check/**`，就是一条 Glob 模式的 Project Rule——只在处理该路径下的文件时才加载。

  

---

**③ Add from GitHub/GitLab — 从公开仓库导入**

可以直接导入他人分享在 GitHub/GitLab 上的 Rules 文件，快速复用社区最佳实践，在此基础上修改为自己的版本。

---

**User Rule vs Project Rule 核心区别**：

|   |   |   |
|---|---|---|
|对比项|User Rule|Project Rule|
|生效范围|你的所有项目|仅当前项目|
|存储位置|Cursor 内部|`.cursor/rules/*.mdc`|
|是否进 Git|❌ 不进仓库|✅ 可提交，团队共享|
|适合写|个人习惯和偏好|项目规范和业务背景|
|类比 Claude Code|`~/.claude/CLAUDE.md`|`./CLAUDE.md`|

---

#### 实操：VAT 对账项目的 Cursor 配置

  

**① 创建 User Rule（个人全局，所有项目生效）**

进入 `Settings → Rules, Skills, Subagents → + New → User Rule`，填写：

```Plain
- Always respond in 中文
- 操作前先说你打算做什么，等我确认再执行写操作
- 遇到不确定的先问我，不要自己猜
- 给出方案时说明取舍，不只给一个答案
```

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YzJlMzVmYWE0M2FjYTM4ZTc0ODNiMjM2Zjg2OTU0YjZfaTR4anhpenhhaTA2U3M3ODIyVUY2QlQ1UnVtWDNlNTFfVG9rZW46SnFJSWI5OUNub0xBU3l4WWdjYmNqNE1HbmcyXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

> 这条规则保存后，对你在 Cursor 里打开的所有项目都生效，无需重复设置。

  

**② 创建 Project Rule：核心规范（alwaysApply，每次加载）**

在 Cursor 对话框中输入内置命令 `/create-rule`，Cursor 会引导你填写规则名称和内容，并自动在 `.cursor/rules/` 目录下生成对应的 `.mdc` 文件：

```Plain
/create-rule
```

在弹出的交互中，填写规则名称 `vat-project`，然后粘贴以下内容：

```YAML
---
description: VAT 对账项目核心规范
alwaysApply: true
---

# 项目背景
Fintopia 波兰子公司财务部，处理每月供应商 VAT 对账单，生成汇总报告。

# 文件路径
- 原始数据：./data/（命名规则：vat_YYYY_MM.xlsx）
- 输出报告：./reports/（命名规则：vat_report_YYYY_MM.md）

# 发票类型
- FV：国内普通 VAT 发票，税率 23%（标准）或 8%（低税率）
- VAT-UE：EU 跨境服务，0% 税率，VAT 金额应为 0
- VAT-IMP：进口货物，海关代征 VAT，单独列示

# 输出规范
- 所有输出用中文
- 金额格式：12,500.00 PLN
- 报告必须包含：执行摘要 / 分类汇总表 / 异常标注 / 核对结论
- 单笔 VAT 超过 3,000 PLN 的记录用**加粗**标注

# 禁止事项
- 不要修改 ./data/ 目录下的原始文件
```

Cursor 会自动将文件保存至 `.cursor/rules/vat-project.mdc`，并在 Settings 的 Project Rules 列表中可见。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YWViNmM1ZTU0NTFmNzNjZWQ4NDk0NTUwODBhODY3YWFfTHdqdlFzZEFGYlZMNWN6ZHlYbDg5ZFY2dkhCejM2MEJfVG9rZW46UXc4ZGJVbE9wb0taa3p4QmVWcGNZTExWbkhrXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

  

**③ 创建 Project Rule：数据处理规则（Glob 模式，按需加载）**

同样使用 `/create-rule` 命令，创建第二条规则，命名为 `data-rules`，填写以下内容：

```YAML
---
description: 数据文件处理规范，处理 xlsx/csv 文件时自动加载
globs:
  - "data/**/*.xlsx"
  - "data/**/*.csv"
---

# 数据文件处理规则
- 读取 Excel 前先输出列名列表 + 前 3 行数据，等我确认结构正确后再继续
- 处理结果另存新文件，不覆盖 ./data/ 下的原始数据
- 发现空值或格式异常的单元格，列出位置后询问处理方式

# 核对要求
- 各分类合计之和必须等于总计行，误差不超过 0.01 PLN
- VAT-UE 类发票 VAT 金额如不为 0，标记为数据异常
- 报告末尾注明"数据已与原始文件交叉核验"
```

Cursor 自动保存至 `.cursor/rules/data-rules.mdc`。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NmQ5NGY5MWY0Yjg5NjRmZmM4MGY1MzBjYTg3NGU2YThfN094YVRDTVpHSnJJUVlhc2IzWnZaZ3RORFdXUGhCM2pfVG9rZW46QTRsbmJ4Sm9Cb2kxVVV4bU9GWWNDZmF4bnVnXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

> 这条规则配置了 `globs` 路径匹配，只在 Cursor 处理 `data/` 目录下 `.xlsx` 或 `.csv` 文件时才加载，不会在写报告或处理其他文件时多余地占用上下文。

  

**④ 配置完成后，直接下发任务**

```Plain
处理 ./data/vat_2025_04.xlsx，生成本月 VAT 对账报告
```

Cursor 自动加载：每次对话的项目规范（来自 `vat-project.mdc`）+ 处理 Excel 时的数据规则（来自 `data-rules.mdc`）+ 你的个人偏好（来自 User Rule）。三层配置自动叠加，不需要在提示词里重复任何一条。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NmNkM2U5YmQ2YmZiOGMxN2JmYjE2OTZlYzk1NTU1NjhfNTY1U2Z2YmI5UkJRZjM2ZXBXeE5vbVh4blZiTlZlUEFfVG9rZW46SEJwcGJUMUZUb2FvMVB4eldFVmM5aUZ5bnRoXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Tips: cursor中需要确认操作，在流程中交互确认。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MmRlOTU1NjQ0M2YyOTFmNTgxYTlhYzY5ZDQzNTE5YjFfQ0cyOWdtMVc2eXNnSkl3ZFdhTFZUWWlVaXAzWDVYMWZfVG9rZW46TkZWamI4aVlBb3JuOFB4T0U0WGMxeTVabkNmXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**⑤ 推荐创建方式：先跑任务，再让 Cursor 固化**

如果不确定该写什么，可以先正常跑一次完整的 VAT 对账任务，跑通后在对话框说：

```Plain
根据我们刚才的对话内容，帮我生成一份 Project Rule 文件，
保存到 .cursor/rules/vat-project.mdc，设置 alwaysApply: true
```

Cursor 会自动提取对话中用到的背景信息和规范，生成对应的规则文件。

  

**⑥ 查看当前加载了哪些规则**

对话框底部 context 区域可见当前对话已加载的 Rules 文件名；输入 `@` 可手动引用某条规则。

---

**构建完对应Rules/CLAUDE.md期望的项目目录结构**

```Plain
fintopia-vat/                   # 项目文件夹
├── CLAUDE.md                   # 团队配置（提交 Git）
├── CLAUDE.local.md             # 个人偏好（加入 .gitignore）
├── .claude/
│   └── rules/
│       └── data-rules.md       # 数据文件处理规则（路径作用域）
├── .cursor/
│   └── rules/
│       ├── vat-project.mdc     # 项目核心规范（alwaysApply）
│       └── data-rules.mdc      # 数据处理规则（Glob 匹配）
├── data/
│   └── vat_2025_04.xlsx        # 原始对账数据
├── reports/                    # 输出报告目录
└── templates/
    └── vat_report_template.md  # 报告模板
```

同一份项目，`CLAUDE.md` 和 `.claude/rules/` 供 Claude Code 读取，`.cursor/rules/` 供 Cursor 读取——两个工具可以共存于同一个项目目录。

---

## 第四章：MCP 介绍——让 AI 连接外部世界

  

### 4.1 为什么 AI 只靠内置知识不够

  

大模型本身的知识有两个核心限制：

1. **知识有截止日期**：不知道今天发生了什么、你的系统里现在有什么数据
    
2. **无法操作外部系统**：不能读你的飞书文档、不能查你的数据库、不能发消息
    

  

这意味着：如果你问 AI "帮我把这份飞书文档总结一下"，它做不到——它访问不了飞书。

  

### 4.2 MCP 在解决什么问题

  

**MCP = Model Context Protocol（模型上下文协议）**

MCP 是一套标准规范，定义了 AI 如何与外部系统"说话"。

可以把 MCP 理解成 AI 世界的 **USB 接口**——不管你接的是飞书、数据库还是搜索引擎，只要符合 MCP 标准，AI 就能认识它、使用它。

  

MCP 统一规范后，一个 MCP Server 可以被 Cursor、Claude Code、任何支持 MCP 的工具直接使用——无需为每个平台单独开发接口。

  

### 4.3 MCP 帮 AI 连接四大资源

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YThiODlkNWVmNDgxZDM1NTNmNjQyOTQ3MWI0MWRjYTNfTHZvODFNb0VXTkswdkliOXZjbUJ0b1JKUjgyTmpWcGZfVG9rZW46S2hpT2JudXMyb1hzVWR4MXNQVGNiNER4bmg4XzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

  

|资源类型|举例|实际用途|
|---|---|---|
|**数据源**|数据库、数据仓库|AI 直接查询业务数据|
|**文件与文档**|飞书文档、本地文件|AI 读取和写入文档|
|**工具与 API**|搜索引擎、内部 API|AI 调用外部服务获取信息|
|**系统操作**|发送消息、创建任务|AI 触发实际业务动作|

**没有 MCP 时**：AI 只能基于你粘贴进来的文本内容进行回答，每次都要手动复制数据。

**有了 MCP 后**：AI 主动调用工具获取最新数据，直接操作文档，完成端到端任务。

  

### 4.4 让 MCP 连通公司内部知识--以飞书文档为例

  

在日常工作中，我们经常需要阅读已有的文档、提炼关键信息，再将学习或协作的过程沉淀为新的文档记录。这类工作流如果全靠手工完成，既耗时又容易遗漏。

  

本次实践任务模拟了一个真实的工作场景：

> 你需要将飞书上的一份重要文档（如需求模板、设计规范、操作手册）的核心内容提取出来，保存在本地，方便随时查看、搜索或作为后续工作的输入素材。

  

这个任务展示了 AI 助手最基础也最实用的能力之一：用一句自然语言，代替你完成"打开文档 → 阅读理解 → 提炼要点 → 写入本地文件"这一完整操作链，无需手动切换任何工具。

**任务提示词如下**：

```Plain
读取飞书文档，文档链接:https://fintopia.feishu.cn/wiki/GVsYwZ8JRiyTcZkDMRkci1Gxn7d，并将该文档中的重要内容保存在本地。
```

  

### 4.5 在 Cursor 里怎么接 MCP

##### **第一步：进入配置界面**

Cursor Settings → 左侧导航 **Tools & MCP** → 点击 **Add Custom MCP**：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YjcxMDE2Y2RiMTI3MTlkNDhhNWY1ZWE2ZmI0ZDMzY2JfWmlzSHZMU3JBTVpOYm91UDNIUWVnODRWS2hjNlpuU2tfVG9rZW46SkFWWmJaQUNHb1lVVDR4QXZuMWN0dXpXbldoXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

##### **第二步：申请内部 MCP**

访问公司内部 AI 中台的 MCP 广场，找到需要的工具并申请：https://ai.fintopia.tech/hub/mcp-market

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ZGVkYTJlMzQwNmVmOTA3ZGU4YjMxZDFmMTZhYzllMjhfcE4yRW00SkxyTmE1RnllOFpKSldxbXBkTHI4UUNPbExfVG9rZW46TkI1R2JETVJrb1RDdU54Y0Fab2NxeG5RbkZoXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

申请通过后，在详情页复制 `mcpServers` 配置内容：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YmI2ZTg3YzZiYTZmNGRhZWE1NWQ2NWFiZWRmNTBkNGJfY1duVE9oMWtxdjdpTzJvbDY5VXBwWnQ2bHdKeGJURWJfVG9rZW46Tk9TRWJNdGdkb21SZXJ4b0NtcWN1QWQybkhoXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

##### **第三步：填写配置**

将复制的配置粘贴到 Cursor 弹出的 `mcp.json` 文件中保存：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=N2RhNWM3MTQ5OGY3MzRjYzI5NGFmZThhMWZlNjkwNTBfR1pTZXhZZnJWOVRZQjNOUWxuZjBSUnR2bWQzZGhnNUZfVG9rZW46Q0VUZWJ3ZlpJb20wMEJ4UUlreGNIODRSbjVjXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

##### **第四步：验证连接，查看可用工具并执行任务**

配置完成后，在 Tools & MCP 页面看到工具列表，说明配置成功：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=Y2VjODFlNjk3MTczODYwYTYzYmM1YjllNWQ1YzA4M2ZfR1U2VXdRNnNDa0wwY1JCSGJzOWJRdFhZODk4VjI5bzBfVG9rZW46U21Ha2JjZ1Rjb2dUNjd4d0ZHMGMwZDhJbkZnXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

我们直接将4.4小节中的样例提示词复制粘贴到cursor的chat对话窗口中下发任务

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NjRiM2MxYTEzMGZmY2Y4NzdmMTBjZmQyODM3MDE1OWFfYllESlBJRTJHckFNY05KYzFodGxKckVSeVlHbHk1VjRfVG9rZW46Rk1zMmJKRzFwb0hnY1R4UjRramNmUHkxbllZXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

首次使用时，Cursor 会弹出授权确认，允许对应域名即可。**配置成功后**，即可在对话中直接调用 MCP 提供的能力。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NDQzMTQ3NzM1NzFhMWQ5MDA2ZjVlZjI1MWVkOWQ3ZmFfYldSOE03U2ROaGJUTVNhd2REUjJmblRBMk1vSnZFWWJfVG9rZW46R2JrRmJLUTlqb2dGMUt4aTJGNWN4cTFYbmRnXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

通过飞书 MCP 读取文档内容并汇总保存为本地文件：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ZGY5NmVhODJmNjg3N2NiZWQ1MjBiYmViYmQxMjE1Y2FfY0NrRkU3R1AxMkVybFA4T1RaZzBVSjNsVFZrdmxxOEdfVG9rZW46RXlnRWJ5U0pQb3FhV3J4Zk9pRWM1ZFozbkRBXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**`提示`**`：完成一个相关任务后，点击「+」新建对话窗口，避免上下文干扰下一个任务。`

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=OTAyZWY5NzliYTI0YWRhNzIyYzE5MWE2ZWQzYjcwOWZfSFNUUXo1VmdTMWc3YjJIQXNrOWI1eE55cXU2elFRTlNfVG9rZW46TzR1UWIyeVBsb1FiVmp4MnExc2NGeE5FbmRoXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

  

### 4.6 在 Claude Code 里怎么接 MCP

  

MCP 让 Claude Code 能够连接飞书、TAPD、数据库等外部系统，从"只能处理本地文件"升级为"能操作整个工作生态"。

##### 第一步：了解配置文件位置

|配置级别|路径|作用范围|
|---|---|---|
|项目级配置|`.claude/<plugin-name>/mcp.json`|仅当前项目生效|
|全局配置|`~/.claude/plugins/cache/<plugin-id>/mcp-*.json`|所有项目生效|

##### 第二步：申请内部 MCP 并填写配置

访问内部 AI 中台的 MCP 广场，找到需要的 MCP 工具并申请。

可以按照Cursor 里怎么接 MCP章节中如何申请**申请内部 MCP资源**的方式申请对应的MCP

申请通过后，在详情页复制配置内容，填入 mcp.json 文件，或者直接将对应的mcp配置粘贴给claude 让它帮你配置。

  

**配置方式（推荐：直接告诉 Claude）**：

```Plain
我需要配置飞书 MCP，配置内容如下：[粘贴内部MCP广场申请到的配置内容]，请帮我写入到对应的配置文件。
```

**手动配置格式**：

```JSON
{
  "mcpServers": {
    "feishu": {
      "type": "http",
      "url": "https://your-mcp-server.company.com",
      "headers": {
        "Authorization": "${env:FEISHU_TOKEN}"
      }
    }
  }
}
```

##### 第三步：验证连接，查看可用工具并执行任务

**验证连接**：配置完成后，询问 Claude 当前可用的 MCP 工具，Claude 会返回已配置的工具列表：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MDUxZDg2YWMxM2U2ZDIxMzEyYjM3NThjYWU2MWE0MmVfZkpoMnVNNWlWOFo5SVNOR1ZDbVpxclRNZTVWeFRheFZfVG9rZW46Q1ZLT2JMRmpUb2R6UHN4cWQxU2M1eE4xbm5iXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

在claude code 中配置好飞书mcp后，将对应的样例提示词复制粘贴给claude：

**执行过程**（Claude Code 通过飞书 MCP 完整执行）：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NTAwZjJjNDQ5MmI4YzIzODk2MjEzZDEyYTAwNGZlYjJfbEkwdXg2ZE5RRGpxT0lDZ3VMMW5ENEdTOEZWM2JMZlJfVG9rZW46SFRvZ2I4bDJob2ZlZ2p4Q012OGM2cndXbjdiXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Claude 首先调用工具了解飞书 MCP 功能，然后搜索并读取相关文件并进行了总结，最终完成任务。

  

> **使用建议**：完成一个 MCP 相关任务后，立即新建对话（Cursor 点 `+`，Claude Code 输入 `/clear`），避免上下文干扰下一个任务。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YmRmNzRjOGE5MmI5NGMwOWE1NWU4OWEwYmUxMmIzM2Nfc1NiNk1HUjRoMVRwWEtQa3VUUVU5RzNzQWgzYkh2NTZfVG9rZW46Q3QxY2JSamJ2bzNiZk14QXV3b2NYR05QbkRXXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

首次调用 MCP 工具时，Claude 会弹出权限确认：

- **Allow**：本次允许
    
- **Always allow this tool**：加入白名单，后续自动通过
    
- 用 `/permissions` 命令可统一管理白名单
    
      
    

### 4.7 更多 mcp

为了支持公司级别的MCP资产能力的建设，AI中台也构建了[对应的平台](https://fintopia.feishu.cn/wiki/EwRfwrWM9inIfBka0YZc3WMBnjh#share-I4ljdrXJTorPBox0IORcOFsNngb)进行管理：

**公司内可接入的数据源**（以实际 MCP 广场为准）：

- 飞书文档 / 知识库
    
- TAPD 项目管理
    
- 内部数据仓库
    
- RAG 知识检索
    
- 更多见 AI 中台 MCP 广场
    
      
    

除公司内部 MCP 广场外，国内外已有成熟的开放 MCP 市场，可按需查找和接入：

|平台|特点|地址|
|---|---|---|
|MCP 官方 Server 列表|Anthropic 官方维护，覆盖 GitHub、Google Drive、Slack、数据库等常用工具|https://github.com/modelcontextprotocol/servers|
|Smithery|社区最大的 MCP 注册中心，可搜索并一键配置|https://smithery.ai/|
|MCP.so|国际主流 MCP 聚合目录，分类清晰|https://mcp.so/|
|modelscope|国内第一AI开源社区魔搭（ModelScope）MCP广场|https://www.modelscope.cn/mcp|

> **使用建议：** 接入外部 MCP 前，涉及安全隐私数据的请确认已通过公司安全团队审批。公司内部优先使用 AI 中台 MCP 广场中的工具。

  

延伸资料：

[MCP简易入门教程](https://www.bilibili.com/video/BV1HFd6YhErb/?spm_id_from=333.337.search-card.all.click)

[从原理到实战，带你深入掌握MCP](https://www.bilibili.com/video/BV1uronYREWR/?spm_id_from=333.337.search-card.all.click)

  

---

  

## 第五章：Skill 介绍——把经验和流程变成可复用能力

### 5.1 为什么"只有我自己会用"不可持续

  

假设你花了一个月摸索出了一套高效的竞品分析流程：先搜集动态、再整理成对比表格、然后做 SWOT 分析、最后输出报告。这套流程很好用，但：

- **只有你自己会用**——新同事加入，还是要从零开始摸索
    
- **每次还是要告诉 AI 流程**——虽然你知道怎么做，但每次对话还要重新描述步骤
    
- **个人经验无法沉淀**——其他同事无法获取到你的经验流程
    

这就是 Skill 要解决的问题。

  

### 5.2 Skill 在解决什么问题

  

**Skill = 把流程和经验打包成的"能力插件"**

把一套完整的工作流程封装好，AI 下次遇到同类任务，直接调用这个能力包执行，不需要你再解释一遍怎么做。

  

**Skill 带来的三个价值**：

① **经验可以沉淀**：团队积累的最佳实践，写进 Skill，让每次 AI 执行都按最优路径走

② **流程可以标准化**：同样的任务，不管谁调用，都按同一套规范执行，输出一致

③ **门槛更低**：用户不需要懂技术细节，只需要说"帮我做竞品分析"，Skill 自动处理并交付结果

  

**Skill 的聪明之处：按需加载**

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YWRiMTllOWMyMjVlNGE1MTY1NmZmYjMzYWY4ZTQ1YjNfMUVoRUdjdDlQNEtrNFNZSkg3bjNsSzl0dW9CV21uV0lfVG9rZW46SVZTYmJwVWVUb1lMTjR4ZFhuTWM0NnZZbmZmXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Skill 不是把所有内容一次性塞给 AI，而是分三层按需加载：

- **第一层（平时）**：AI 只知道"我有这个技能"（技能名称和简介）
    
- **第二层（需要时）**：才调出"怎么做"（执行步骤）
    
- **第三层（执行时）**：才打开"具体工具"（脚本、模板、参考资料）
    
      
    

这样设计是因为 AI 的上下文窗口有限——如果把所有 Skill 的全部内容同时塞进来，反而什么都做不好。

  

### 5.3 Skill 和 Prompt、Rule、MCP 的区别

|概念|本质|作用域|举例|
|---|---|---|---|
|**Prompt**|一次性任务描述|当前对话|"帮我分析这份数据"|
|**Rule**|持久化背景/规范|整个项目|"我是财务部的，输出用中文"|
|**MCP**|外部工具/数据连接|系统级|连接飞书、数据库、搜索引擎|
|**Skill**|封装好的可复用流程|项目/团队|`/竞品分析 → 完整执行搜集+整理+报告`|

**一个类比**：

- Rule 是"员工手册"——告诉 AI 基本规范
    
- MCP 是"工具箱"——给 AI 配备各种工具
    
- Skill 是"标准操作程序（SOP）"——AI 按照 SOP 完成特定任务
    

  

### 5.4 用 Skill 固化重复工作流——以 VAT 对账报告为例

在日常工作中，有很多任务并不复杂，却高度重复——每月、每周都要做同样的事：

- 打开同一份数据文件
    
- 按同样的逻辑汇总
    
- 生成格式相同的报告
    
- 上传到同一个地方归档
    

若每次都靠手工完成，不只是费时，更大的问题是：每次都要重新告诉 AI 怎么做。发票类型怎么分、金额格式怎么写、报告结构是什么、存到哪里——这些规则每次都要重复交代一遍，稍有遗漏输出就会出问题。

  

本次实践任务模拟了一个财务团队的真实场景：

每月月末，你需要处理波兰子公司的 VAT 对账单（Excel 格式），按发票类型分组汇总，生成一份标准格式的 Markdown 报告，保存到本地 `./reports/` 目录，并上传到飞书归档。

这个流程步骤固定、规则明确、每月重复。

对应文档样例如下：vat_2025_04.xlsx

该样例和[3.5 实战样例背景：VAT 对账项目一致](https://fintopia.feishu.cn/wiki/EwRfwrWM9inIfBka0YZc3WMBnjh#share-GzKMd8PQjoj5oCxzy2fcdVV6nbe)

**任务提示词如下：**

```Plaintext
本月 VAT 对账报告，原始数据在 ./data/vat_2025_04.xlsx，对应要求如下：
1.按发票类型（FV/VAT-UE/VAT-IMP）分组汇总
2.标注异常记录（VAT-UE 金额不为 0、单笔 VAT 超过 3,000 PLN）
3.核对分类合计与总计行，误差不超过 0.01 PLN
4.生成标准 Markdown 汇总报告，保存至 `./reports/`
5.使用infra-feishu-mcp上传飞书个人空间归档
```

  

---

**Skill 的价值：固化跑通的工作流**

这类任务展示了 Skill 最核心的价值：把一个跑通过的完整工作流固化下来，让下一次执行不再需要重新描述步骤和规则。

你只需要说一句：

```SQL
/vat-monthly-report 帮我处理一下VAT对账报告，原始数据在 ./data/vat_2025_04.xlsx
```

AI 就会自动完成"读取 Excel → 按类型汇总 → 标注异常 → 核对数据 → 生成报告 → 上传飞书"这一完整操作链，无需手动切换任何工具，也无需重复交代任何背景。

  

  

### 5.5 在 Cursor 里怎么写 Skill

---

**Skill 文件结构**

Cursor 的 Skill 以**文件夹**为单位存放在 `.cursor/skills/` 目录下，每个 Skill 对应一个独立文件夹：

```Plain
.cursor/skills/
└── vat-monthly-report/          # Skill 名称（文件夹名）
    ├── SKILL.md                 # 核心描述文件（必须）
    ├── scripts/                 # 可执行脚本（可选）
    │   └── process_vat.py
    └── references/              # 参考资料（可选）
        └── vat_report_template.md
```

> **文件夹名即 Skill 的调用名**。命名建议使用小写 + 连字符，清晰描述 Skill 的用途。

---

**SKILL.md 核心格式**

`SKILL.md` 是 Skill 的核心文件，通过 YAML frontmatter 定义元信息，正文描述执行步骤和输出规范：

```YAML
---
name: vat-monthly-report
description: 当用户要处理月度 VAT 对账单、生成汇总报告时使用此 Skill
version: 1.0
---

# 月度 VAT 对账报告 Skill

## 执行步骤
1. 读取 ./data/vat_YYYY_MM.xlsx，输出列名列表 + 前 3 行数据，等待确认数据结构
2. 按发票类型分组汇总（FV / VAT-UE / VAT-IMP）
3. 标注异常记录：VAT-UE 发票 VAT 金额不为 0、单笔 VAT 超过 3,000 PLN 的记录加粗
4. 核对各分类合计之和是否等于总计行，误差不超过 0.01 PLN
5. 生成标准 Markdown 汇总报告，保存至 ./reports/vat_report_YYYY_MM.md
6. 上传飞书归档

## 输出格式
- 文件名：vat_report_YYYYMM.md
- 所有内容用中文
- 金额格式：两位小数 + PLN + 千位逗号，例：12,500.00 PLN
- 报告结构：执行摘要 / 分类汇总表 / 异常标注 / 核对结论
- 报告末尾注明"数据已与原始文件交叉核验"

## 禁止事项
- 不要修改 ./data/ 目录下的原始文件
- 发现数据异常先列出，等待确认后再继续
```

---

**生成 Skill 的推荐方式（通过对话生成）**

  

> **不需要从零手写 SKILL.md。推荐先跑通一次完整流程，再让 Cursor 帮你固化。**

  

当一次完整的 VAT 对账流程跑通后，直接在对话中说：

```Plain
我们刚才完成的 VAT 对账流程很好，请把这个流程固化成一个 Skill，
保存到 .cursor/skills/vat-monthly-report/ 目录
```

Cursor 会自动提取对话中用到的步骤、规则和输出格式，生成对应的 `SKILL.md` 文件。

**好处**：内容来自真实执行过的流程，不是凭空写出来的——生成的 Skill 更贴合实际，不容易遗漏细节。

  

---

**调用方式**

Skill 固化完成后，下次处理月度对账单只需一条指令：

```Plain
/vat-monthly-report
```

Cursor 自动执行完整操作链：

```Plain
读取 Excel → 确认数据结构 → 按类型汇总 → 标注异常
→ 核对数据 → 生成报告 → 上传飞书
```

**第一次跑通，之后每次都一样。**

  

Cursor 会自动生成符合规范的 Skill 文件：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=YjFiMzQ4MWZkZjlkN2E0ZDM0NGUzMzg2NjNiM2ZkMTFfVzVRNkkzTkpZelBXUVJyaUpkc08xMFFiaWZiZDZuQjJfVG9rZW46VHBiZWI1SXFDb1JLT3Z4RDJqZ2NZdTlmbnpoXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

固化为 Skill 后，只需简单说出需求，AI 就能自动读取 Skill 并按流程执行：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MTA3YWMzODJhNWNiZmVjMTZjN2YyYjhjYTQyZDAzZTlfRjhiSTFwYW05a1JsMmNyQk5SMkdNTndqUUp1UkJRVXlfVG9rZW46R1JlaGIzdlFWbzF6UWl4THJSYmN0RjI0bmhkXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**调用 Skill 的两种方式**：

- **手动调用**：对话框输入 `/`，从弹出列表选择 Skill，按回车执行
    
- **AI 自动触发**：当对话内容与 Skill 的 `description` 高度匹配时，AI 自动调用
    
      
    

**查看已有 Skill**：`Cursor Settings → Rules → Agent Decides` 区域，快捷键 `Cmd/Ctrl + Shift + J`

  

### 5.6 在 Claude Code 里怎么写和调用 Skill

  

Claude Code 的 Skill 机制与 Cursor **完全兼容**，文件结构和格式相同，只是存储路径不同：

|作用范围|存储路径|
|---|---|
|项目专用|`.claude/skills/`|
|全局通用|`~/.claude/skills/`|

**SKILL.md 核心格式：**

```Markdown
---
name: skill-id
description: 一句话说明这个技能是做什么的，以及什么时候用它
disable-model-invocation: false
---

## 操作步骤
1. 第一步：具体操作说明
2. 第二步：如有脚本，使用以下命令执行：
   `scripts/your-script.sh <参数>`

## 输出说明
描述执行后会产生什么结果，以什么格式输出。
```

|YAML 字段|说明|重要性|
|---|---|---|
|`name`|Skill 的唯一标识符，用于 `/name` 触发|必填|
|`description`|描述何时触发此 Skill，AI 读取用于自动匹配|必填，写清楚触发场景|
|`disable-model-invocation`|`true` 时只能手动 `/` 调用，禁止 AI 自动触发|高风险操作时设置|

按照[5.5 在 Cursor 里怎么写 Skill中的样例提示词](https://fintopia.feishu.cn/wiki/EwRfwrWM9inIfBka0YZc3WMBnjh#share-UKWwdzzhFoika0xYaKAcxByUnJd) 在对应的项目文件夹下进入claude code进行对应任务提示词的执行。对应的任务处理截图如下：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ODgzZmIxYjE1YWU4ZThiNjhjN2I4NzhiMjNkNjdlNzdfWE5tYWdHQTJRS1FQTGhIMkJqMlFxS2J1R3V2SlZGTlBfVG9rZW46Q3QxSmJLVlRYb09XUGx4NHdpRGNESnQzbjRnXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**当该任务完成后可以将该流程固化下来形成对应的skill**

**方式一：通过对话生成（推荐入门）**

```Plain
刚才的 VAT 对账流程帮我固化成 Skill，存放在 .claude/skills/ 目录
```

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MTNhZDQ4NGM4YTQ5MTc3OTUwMmUzZGE5YjIwN2U0NDBfSm96bVZxcUQzS1FpOHUyQzFLaTRSWERKUWZhYkNqOFVfVG9rZW46TzF5NWJXZmwxb3dwc1h4RDI0WWNOT1NTbkpjXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**方式二：手动创建**

按Skill 文件结构手动创建文件夹和 `SKILL.md`，在对话框输入 `/技能名` 测试是否触发。

  

**方式三：使用插件**

**官方插件辅助构建**：Claude Code 还支持通过 `skill-creator` 插件构建 Skill，引导你描述用途、触发场景和执行步骤，自动生成规范文件

https://claude.com/plugins/skill-creator

安装官方plugin，使用插件帮助构建对应流程的skill。

  

**调用方式**：对话框输入 `/技能名` 触发，或由 AI 根据任务描述自动识别触发(对应的描述`description`要写好，覆盖使用场景需要的描述)。

  

延伸资料：

[什么是skill](https://www.bilibili.com/video/BV1dz6oBWEWx/?spm_id_from=333.337.search-card.all.click)

[skill原理及使用教程](https://www.bilibili.com/video/BV1cGigBQE6n/?spm_id_from=333.337.search-card.all.click)

[Cursor Skills 配置完全教程](https://fintopia.feishu.cn/wiki/KrnQwbchbiWQ1okrpFxcvNiSnBh)

  

## 第六章：进阶使用——如何把 Agent 用得更稳、更强

  

前五章讲了基础概念和配置方法。这一章讲**如何用得更好**——就像 L1 里学了提示词基础原则之后，还有进阶技巧让输出质量上一个台阶。

### 6.1 什么样的任务适合交给 Agent

并非所有任务都适合 Agent。用对了事半功倍，用错了反而浪费时间。

**适合 Agent 的任务特征**：

|特征|说明|示例|
|---|---|---|
|有明确的输入和输出|知道给什么、要什么|上传 Excel → 生成汇总报告|
|步骤可以被拆解|不是模糊的大方向|搜集 → 整理 → 分析 → 输出|
|结果可以被验证|你能判断对不对|数据汇总结果可以核对|
|重复性强|每次做同类任务|每周的数据报告、合同审查|
|涉及多个工具|需要跨系统操作|读飞书 → 处理数据 → 写回飞书|

**不适合 Agent 的任务**：

- **策略性判断**：做哪个方向、怎么定优先级——AI 可以辅助但不能替代
    
- **模糊的探索性任务**：没有清晰的输出定义，每次结果都不确定
    
- **需要最终拍板的决策**：涉及数字/合规/对外的内容，必须人工审核确认
    
      
    

> **核心原则**：Agent 是高效的执行者，不是万能的探索者。执行者需要明确的任务书。

  

### 6.2 Result as a Service：先定义结果，再调用能力

**一个常见误区**：把问题越说越大，让 AI 自己去探索。

❌ **坏问法**：

```Plain
"帮我做一下我们产品的数据分析"
"研究一下我们的竞争对手"
"看看有什么可以改进的地方"
```

这类问题有一个共同特点：**输出是不确定的**。AI 会努力回答，但你得到的是一个通用的、无法直接使用的结果。你花了时间，AI 也花了 token，最后还要重来。

**根本原因**：问题空间太开放，没有给 AI 一个可以收敛的目标。

  

**Result as a Service（RaaS）的核心思路**：

> 先定义你要的结果长什么样，再让 AI 去完成它。把 AI 当做一个高效的执行者，而不是一个万能的探索者。
> 
>   

✅ **好问法**：

```Plain
"读取 ./data/monthly_vat.xlsx，按发票类型分组汇总金额，
生成一份包含：执行摘要 + 数据表格 + 核对结论的 Markdown 报告，
保存到 ./reports/2025-04-vat-summary.md"
```

**好问题 vs 坏问题对照**：

|坏问题|好问题|差异|
|---|---|---|
|"帮我分析数据"|"读取 data.xlsx，按月份汇总销售额，输出 Markdown 表格"|明确了输入、操作、输出|
|"研究竞争对手"|"搜索 A、B、C 三家公司最近 30 天的产品更新，整理成对比表"|明确了范围和格式|
|"看看代码有没有问题"|"检查 app.py 中的所有数据库查询，找出 SQL 注入风险，列出行号和修复建议"|明确了检查范围和预期产出|

**规律**：坏问题缺少的，往往就是 Rule / Skill / MCP 应该提前写好的那些东西。

  

**工作建议**：

```Plain
① 提出需求
② 让 AI 反问问题（确保双方对齐）
③ 阐述细节
④ 开始工作
⑤ AI 检查结果
```

这个步骤能显著提高 AI 的工作质量。

  

### 6.3 按任务复杂度选择正确的工作方式-学会使用Plan模式

|任务类型|推荐工作方式|原因|
|---|---|---|
|简单、可逆的任务|**直接 Agent 模式**|出错了可以修正，快速执行更高效|
|复杂、步骤多的任务|**先 Plan 模式，确认后执行**|先对齐计划，避免执行到一半方向错了|
|有风险的操作（删除、部署）|**Plan 模式 + 逐步确认**|不可逆操作必须提前审查|
|重复性任务|**封装成 Skill**|固化流程，下次直接调用|

**Plan 模式介绍**：

在 Cursor 中切换到 Plan 模式，可以在对应的chat窗口的左下角切换对应的模式：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MjU2YzM4ZDc3NzQ1YWNhMzE2YTFkNWIwMWE5MjAxYmNfaTRaVHVEd1NvN3pESFhDcGpDTDVLNm90cHJLeENUV01fVG9rZW46QXdCaGJjeVdlb3Nsamt4SnkxVGNEaXkzbnFnXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

在 Claude Code 中按 `Shift+Tab` 切换到 Plan 模式：

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=MDkwYjA4ODVhZWU5YzdjOTUwODhmNzI3MTA0Mjg0NWZfcTFJVmFEQVk1OVpvbGNab3ZXaE92WWZEQjFWSzZ6YzdfVG9rZW46QTZOcmJsdnNob0dIbmh4Tnp0SGNZTzBmblRmXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

Plan 模式工作流：

```Plain
描述需求 → AI 提出澄清问题 → AI 生成详细执行计划 → 你审查并修改 → 确认后切换 Agent 执行
```

  

**一个判断技巧**：

> 如果 AI 做错了，我能发现吗？能改回来吗？
> 
> - 能 → 直接 Agent 模式
>     
> - 不确定 / 改不回来 → 先用 Plan 模式对齐
>     

  

### 6.4 Token 怎么合理节省

Token 是 AI 工作台的"燃料"，合理使用可以降低成本、提高效率。

**消耗 Token 的主要来源**：

- 每次对话中的历史消息（上下文越长，每轮消耗越多）
    
- 上传的文件和图片
    
- Rule 和 Skill 文件的内容
    
- AI 的思考过程（thinking tokens）
    
      
    

**节省 Token 的实践建议**：

**① 任务完成后立即开新对话**

```Plain
# Cursor：点击 + 新建对话窗口
# Claude Code：输入 /clear
```

避免无关的历史上下文一直累积，干扰下一个任务。

  

**② 只提供与当前任务直接相关的信息**

- 不要把整个项目文档全部引用进来
    
- 上传文件只选当前任务需要的部分
    
- 避免一次性粘贴大量原始数据——让 AI 直接读文件更高效
    
      
    

**③ Rule 文件保持精简**

- 全局 Rule 建议 500 字以内
    
- Skill 的 SKILL.md 保持简洁，详细资料放 `references/` 目录
    
- 不要把所有历史提示词都堆进 Rule
    
      
    

**④** **合理选择模型档位**

- 简单任务用较轻量的模型（如 Haiku、Sonnet 快速模式）
    
- 复杂推理任务用能力更强的模型（如 Opus、Sonnet 高思考模式）
    
- Cursor 可在对话框底部切换模型：
    

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDM1NjIwYTVkNWI0MWVmMzczOGQzM2ViOTViYWRlODhfWFJseE5nQ3BlMmxCWXhzdkl3a2U5eUhQeTlWOVVDZUNfVG9rZW46THpkdmJNcVBwb3pyclV4U2VYRWN3RkZtbk9iXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

  

各类模型适配任务可参考：

|场景|推荐模型|
|---|---|
|日常对话、简单任务|Auto（自动选择）|
|复杂代码生成、架构设计|Opus 4.6 / GPT-5.4|
|快速迭代、轻量任务|Sonnet 4.6|
|数学推理、多模态分析|Gemini 3.1 Pro|
|大量代码执行、测试生成|GPT-5.3 Codex|

详细模型评测数据参见：[御三家模型评测与提示词指南_2026Q1](https://fintopia.feishu.cn/docx/PshvdbrKwoAITaxexlqcP5HWnCf?from=from_copylink)

  

**⑤ 用 Plan 模式控制执行路径**

- Plan 模式下 AI 不执行操作，Token 消耗少
    
- 确认计划正确后再切换 Agent 模式执行
    
- 避免走错方向后大量重做
    
      
    

### 6.5 提升 Agent 输出质量的技巧

  

**① 先让 AI 提问，再开始工作**

```Plain
"我需要做一个月度竞品分析报告。在开始之前，请先问我几个问题，
确保你理解了我的需求和预期结果，再开始执行。"
```

这一步能显著提高任务完成质量。

  

**② 分阶段执行，每步验证**

复杂任务不要一次全扔，分步进行：

```Plain
步骤1：先读取数据文件，告诉我数据结构  →  我确认后  →
步骤2：按我的需求处理数据  →  我核查中间结果  →
步骤3：生成最终报告
```

  

**③ 建立「执行 → 验证 → 修正」闭环**

每次 Agent 执行完成后：

1. 核查结果文件的关键内容是否正确。
    
2. 如有问题，告诉 AI 具体哪里不对，继续修正。
    
3. 同一个问题纠正超过 3 次还不对 →建议 claude中输入 `/clear` 或者Cursor中新开chat对话窗口，梳理思路，用更清晰的提示词重新开始。
    

  

**④ 利用检查点（Checkpoint）与回滚**

无论 Cursor 还是 Claude Code，都支持在操作前自动创建检查点，出了问题随时回滚：

- **Cursor**：Agent 做大改动前自动创建快照，支持一键回滚
    

每次对话沟通执行的任务窗口右下角有回滚的箭头，点击会弹窗让你确认回滚到对应快照。

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=ODIyNmFjMDhhNTk5ZTgyNjM0NjIyYTgxZTkyMTVmYzhfY3Zyb1M0dDR2eGJHM1l3cXZtSFFQalRJUTk5UzY3bktfVG9rZW46RnNReGJONVBUb2xmSU14MGZaYmMySTJqbmloXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

- **Claude Code**：按 `Esc+Esc` 或输入 `/rewind` 打开回滚菜单
    
    ![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NTRhN2VjNjBlNWI0NDJjMGMxZTViNDI5ZTUwYjI2MTVfWmpFemNiRzVvSkdIWHk4QVB0eUd4RzN5THhyb292TzVfVG9rZW46VWtxNGJjeGpPb3FzU0p4ZHpOdmN3SE4zbklKXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)
    

回滚菜单支持三种粒度：只回滚代码、只回滚对话、同时回滚代码和对话。

  

### 6.6 并行会话：高效处理多任务

当你有多个独立任务时，不必等一个任务完成再开始另一个：

- **Cursor**：支持消息队列，可以连续下发任务，AI 按顺序执行
    
- **Claude Code**：通过 Git Worktree 开启独立隔离会话，多任务真正并行
    

![](https://fintopia.feishu.cn/space/api/box/stream/download/asynccode/?code=NzI1ZTBjMWVkNDY3NDZmNzY0NDY3OGNjZTI2ZDQ1MjJfWnVock1SOU9WZDJGOVFoaENFUDY0MzVzMHo0cGhFWU5fVG9rZW46WVZEeGJjRXBDb2E5MTZ4OGVrYmM4VkxGbmpkXzE3NzYyMzk0MTc6MTc3NjI0MzAxN19WNA)

**典型并行场景**：

```Plain
会话1：处理月度财务报表
会话2：整理竞品分析数据
会话3：审查合同条款
```

每个 Worktree 在独立的工作目录中运行，互不影响。

  

### 6.7 从个人使用到团队资产：AI Champion 的视角

  

AI Champion 的核心价值，不是"会用最复杂的工具"，而是**把个人经验转化成任何人都能直接调用的团队资产**。

**判断哪些工作流值得封装为团队 Skill**：

一个好的团队 Skill 需要同时满足三个条件：

- **重复性高**：这个流程每周/每月都要做
    
- **步骤固定**：不同人做的步骤基本相同
    
- **输出明确**：有清晰的验收标准
    

同时满足三条 → 值得花时间封装成团队 Skill；只满足前两条 → 可以先做个人 Skill；只有第一条 → 维护一份参考文档即可。

  

**建立团队 AI 使用框架的四步**：

```Plain
① 定义输出：这个任务的结果长什么样？（报告格式、表格结构）
② 约束输入：AI 需要哪些数据和上下文？（MCP 配置哪些数据源、Rule 写什么背景）
③ 选对工具：简单任务用 Agent，复杂任务用 Plan，重复任务封装 Skill
④ 闭环验收：结果是否符合预期？不符合就修正 Skill 或 Rule，而不是每次手动调整
```

  

---

  

## 第七章：边界与治理——AI 工作台的安全使用

  

Agent 工具的能力越强，需要注意的边界也越多。本章是所有用户的**必读内容**。

  

### 7.1 自动化与人工兜底

  

Agent 能自主执行多步骤任务，但**不能完全无人值守运行**。

**核心原则：AI 生成，人工确认**

|操作类型|要求|
|---|---|
|读取文件、搜索信息|可以自动执行|
|写入文件、生成报告|建议人工核查关键内容|
|执行代码（含计算逻辑）|必须验证计算结果|
|SQL 写操作（INSERT / UPDATE / DELETE）|必须人工审查后再执行|
|发送消息、对外发布内容|必须人工审核确认|
|部署到生产环境|必须经过代码审查|

  

**推荐的验证方式**：

- 数字类结果：与原始数据交叉核验
    
- 代码类结果：阅读 AI 生成的关键逻辑
    
- 文档类结果：检查关键结论和引用来源
    
      
    

### 7.2 权限管理

---

#### Cursor：敏感文件保护（.cursorignore）

在项目根目录创建 `.cursorignore` 文件，列出不允许 AI 访问的目录和文件：

```Plain
.env
secrets/
credentials/
*.key
*.pem
customer_data/
```

> **原理**：`.cursorignore` 的语法与 `.gitignore` 相同。列出的路径对 Cursor 不可见，AI 既无法读取，也无法修改。

---

  

#### Claude Code：敏感文件保护（settings.json 权限配置）

  

Claude Code **没有** `.claudeignore` 文件。敏感文件保护通过 `.claude/settings.json` 中的权限规则实现。

**配置文件路径**

```Plain
your-project/
├── .claude/
│   ├── settings.json        # 团队共享权限配置（提交 Git）
│   └── settings.local.json  # 个人权限覆盖（加入 .gitignore）
```

**settings.json 权限配置示例**

```JSON
{
  "permissions": {
    "deny": [
      "Read(.env*)",
      "Edit(.env*)",
      "Read(./secrets/**)",
      "Edit(./secrets/**)",
      "Read(./credentials/**)",
      "Edit(./credentials/**)",
      "Read(**/*.key)",
      "Read(**/*.pem)",
      "Edit(**/*.key)",
      "Edit(**/*.pem)",
      "Read(./customer_data/**)",
      "Edit(./customer_data/**)"
    ]
  }
}
```

**规则语法说明**

|写法|含义|示例|
|---|---|---|
|`Read(路径)`|禁止 AI 读取该路径|`Read(.env*)`|
|`Edit(路径)`|禁止 AI 修改该路径|`Edit(./secrets/**)`|
|`*`|匹配单层目录下的文件|`Read(*.key)`|
|`**`|递归匹配所有子目录|`Read(./secrets/**)`|
|`.env*`|匹配所有以 `.env` 开头的文件|`.env`、`.env.local`、`.env.production`|

> **注意**：`deny` 规则只对 Claude Code 的内置工具（Read / Edit / Write）生效，不会限制 Bash 命令。如果需要连 `cat .env` 这类 Bash 命令也一并拦截，需要额外在 `CLAUDE.md` 的禁止事项中注明，或使用沙箱功能。

  

---

**两个工具的对比**

|对比项|Cursor|Claude Code|
|---|---|---|
|配置文件|`.cursorignore`（项目根目录）|`.claude/settings.json`|
|语法格式|与 `.gitignore` 相同，直接列路径|JSON，需写 `Read(路径)` / `Edit(路径)`|
|作用范围|AI 对列出路径完全不可见|内置工具（Read/Edit/Write）不可访问|
|是否提交 Git|✅ 建议提交，团队共享|✅ 建议提交，团队共享|
|个人覆盖|无对应机制|`settings.local.json`（加入 `.gitignore`）|

---

**实践建议**

**最低配置**：项目创建后，立即在 `.claude/settings.json` 或 `.cursorignore` 中把以下路径加入拒绝列表——

```Plain
.env
.env.*
secrets/
credentials/
*.key
*.pem
```

> 这是一条安全底线：**不论用哪个工具，这几类文件都不应让 AI 读取或修改。**

  

**MCP 最小权限原则**：

- 仅授予 MCP 最小必要的访问权限
    
- 定期审查已安装 MCP 的权限范围，只保留实际在用的工具
    
- 连接公司内部系统的 MCP 必须经过安全团队审批
    
      
    

**Skill 安全规则**：

- Skill 文件中**禁止包含**密码、Token 等敏感凭证
    
- 高风险 Skill（如部署到生产、删除数据）必须设置 `disable-model-invocation: true`，要求手动触发，防止误执行
    
      
    

### 7.3 数据安全红线

无论使用哪个工具，以下原则不可逾越：

  

**❌ 禁止输入 AI 工具的内容**：

- 客户个人信息（姓名、手机号、身份证号、银行卡号）
    
- 未公开的业务数据
    
- 系统密码、API Key、数据库连接串
    
- 未公开的商业策略文件
    
      
    

**✅ 脱敏后可以输入**：

- 已脱敏的统计数据（如将具体金额替换为数量级）
    
- 虚构的示例数据（用于调试和测试）
    
- 公开的行业信息
    
- 通用性的工作问题
    
      
    

**不确定时**：咨询你的直属领导或 AI 部门，不要自行判断。

  

**各工具的数据处理说明**（以实际官方政策为准，本表仅供参考）：

|工具|数据存储|训练使用|
|---|---|---|
|Cursor|默认不存储代码内容|企业版可关闭数据训练|
|Claude Code|本地运行，数据不上传|API 调用受 Anthropic 隐私政策约束|
|公司内部服务|按公司数据治理规范|不用于模型训练|

  

### 7.4 合规边界

  

**代码合规**：AI 生成的代码在进入生产环境前，必须经过代码审查。

  

**数据访问合规**：通过 MCP 访问的数据，适用与直接访问相同的数据安全规范——你没有权限访问的数据，AI 也不能绕过权限访问。

  

**版权合规**：

- AI 生成的内容对外发布前，需确认是否存在版权风险
    
- 营销物料中不要生成含具体收益率、利率数字的图片（合规风险）
    
- 重要场景的版权问题请咨询法务
    
      
    

**成本意识**：

- 上传大文件或粘贴大量原始数据会消耗大量 Token
    
- 建议只提供与当前任务直接相关的信息
    
- 使用完毕及时关闭不必要的 MCP 连接
    
      
    

### 7.5 常见误区对照

|误区|正确做法|
|---|---|
|"AI 生成的结果我就直接用"|涉及数字、事实、合规的内容，必须人工核验|
|"把所有文件都给 AI 分析"|只提供当前任务直接需要的文件和数据|
|"Rule 里写了 API Key 更方便"|API Key 必须用环境变量，绝不硬编码|
|"让 AI 自动执行所有操作，我不看"|自动化流程必须有人工审核节点|
|"MCP 配置越多越好"|只保留实际在用的 MCP，定期清理|
|"AI 说代码没问题就没问题"|生产代码必须经过人工代码审查|

  

---

  

## 附录

### 术语速查

|术语|释义|
|---|---|
|Agent|能够自主规划和执行多步骤任务的 AI 系统|
|MCP|Model Context Protocol，AI 连接外部工具和数据的标准协议|
|Skill|封装了完整工作流程的可复用能力插件|
|Rule|Cursor 的持久化配置文件，项目启动时自动加载|
|CLAUDE.md|Claude Code 的持久化配置文件，功能类似 Cursor 的 Rule|
|Token|AI 处理文本的基本单位，约 1 个中文字 ≈ 1.5 个 token|
|Plan 模式|只分析规划不执行操作的工作模式，用于对齐复杂任务|
|Agent 模式|自主执行操作的模式，可读写文件、运行代码|
|Git Worktree|Claude Code 的并行隔离会话机制|
|Checkpoint|操作前自动创建的代码快照，支持一键回滚|
|RaaS|Result as a Service，先定义结果再调用 AI 能力的使用思路|
|AI Champion|负责在团队内推动 AI 工具使用、建立 AI 资产的角色|

  

### Cursor 快捷键速查

|功能|macOS|Windows|
|---|---|---|
|打开 Chat 窗口|`Cmd + L`|`Ctrl + L`|
|打开 Agent 模式|`Cmd + I`|`Ctrl + I`|
|切换 Plan / Debug 模式|`Shift + Tab`（输入框内）|同左|
|查看已加载 Skills|`Cmd + Shift + J`|`Ctrl + Shift + J`|
|立即打断 Agent 任务|`Cmd + Enter`|`Ctrl + Enter`|
|打开 Cursor Settings|`Cmd + ,`|`Ctrl + ,`|
|全局搜索|`Cmd + Shift + F`|`Ctrl + Shift + F`|
|打开/关闭终端|`` Cmd + ` ``|`` Ctrl + ` ``|

具体更加明细的学习指南详见：[Cursor · 新手学习指南](https://fintopia.feishu.cn/wiki/Lx6nwQP1XiYU3zko24hc0xq8n5e)

cursor也有众多的插件可以使用，在此不再详述：[Cursor Marketplace | Cursor Plugins](https://cursor.com/cn/marketplace)

  

### Claude Code 常用命令速查

##### 会话中的键盘操作

|操作|Mac|Windows / Linux|
|---|---|---|
|中断当前生成|`Ctrl+C`|`Ctrl+C`|
|退出 Claude Code|`Ctrl+D`|`Ctrl+D`|
|循环切换三种模式|`Shift+Tab`|`Shift+Tab`|
|打开回滚菜单|`Esc+Esc`|`Esc+Esc`|
|中断当前操作（保留上下文）|`Esc`|`Esc`|
|查看 Claude 思考过程|`Ctrl+O`|`Ctrl+O`|
|在编辑器中编辑提示词/计划|`Ctrl+G`|`Ctrl+G`|
|粘贴图片/截图|`Ctrl+V`|`Ctrl+V`|
|将当前任务转入后台|`Ctrl+B`|`Ctrl+B`|
|清屏（保留对话）|`Ctrl+L`|`Ctrl+L`|
|切换模型|`Option+P`|`Alt+P`|
|切换深度思考|`Option+T`|`Alt+T`|
|语音输入（需开启）|长按 `Space`|长按 `Space`|

##### 常用会话内斜杠命令速查

|命令|功能|
|---|---|
|`/clear`|清空上下文，开始新对话（会话历史保留）|
|`/compact`|压缩上下文，保留关键信息释放空间|
|`/compact 指令`|带指令压缩，如 `/compact 保留所有API改动`|
|`/rewind`|打开回滚菜单（支持代码/对话分离回滚）|
|`/init`|自动扫描项目，生成 CLAUDE.md 初始版本|
|`/permissions`|管理权限白名单|
|`/model`|切换模型|
|`/effort`|调整思考深度|
|`/btw 问题`|侧问——不进历史，不消耗主上下文|
|`/insights`|生成使用分析报告（HTML，在浏览器打开）|
|`/simplify`|启动三路并行代码审查并自动修复|
|`/security-review`|分析当前改动的安全漏洞|
|`/branch 名称`|从当前节点分叉对话（别名 `/fork`）|
|`/loop 5m 命令`|定时循环执行，如每 5 分钟检查构建状态|
|`/rc`|开启远程控制，允许从 claude.ai 手机端操作|
|`/export`|导出当前对话为纯文本|
|`@文件名`|精准引用文件|
|`!命令`|直接运行 Shell 命令|

  

### 行动清单

**入门阶段**：

- 安装 Cursor，登录账号，打开一个工作项目文件夹
    
- 在 Cursor Settings 中配置全局 Rule（写入你的角色和输出偏好）
    
- 使用 Agent 模式完成一个简单任务（如处理一份 Excel 文件）
    
- 体验 Plan 模式：用 Plan 模式规划一个复杂任务后再执行
    

  

**进阶阶段**：

- 在项目中创建第一个项目级 Rule（写入业务背景和输出规范）
    
- 申请并配置一个内部 MCP（推荐先从飞书 MCP 开始）
    
- 将一个高频任务的完整流程跑通，生成第一个 Skill
    
- 完整跑一次任务闭环（取数 → 分析 → 报告）
    

  

**AI Champion 阶段**：

- 整理本岗位的知识资产，写出团队 Rules 模板
    
- 创建至少一个团队级 Skill，让同事能直接调用
    
- 定期收集团队使用反馈，持续迭代 Skill 和 Rules
    
- 联系技术团队了解更多内部 MCP 接入规范
    

  

### 延伸阅读

- MCP 官方规范文档（modelcontextprotocol.io/docs）
    
- Anthropic 官方指南：Building Effective Agents
    
- Cursor 新手学习指南（内部文档）
    
- 御三家模型评测与提示词指南（内部文档）
    
      
    

---

_本文档基于公司内部培训材料整理，对应工具截图数据截至 2026 年 4 月。_

  

## 相关文档及其链接对应表

| 章节                                                                                                                   | 文档中文本                                                                                                          | url                                                         |
| -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 第二章                                                                                                                  | [Cursor/Junie/Qcli账号申请及配额提升说明](https://fintopia.feishu.cn/wiki/Lbmmwj8EuiyzJ9kKpKFcf3jfnYg?from=from_copylink) | https://fintopia.feishu.cn/wiki/Lbmmwj8EuiyzJ9kKpKFcf3jfnYg |
| [Cursor安装教程](https://cursor.com/cn/docs/get-started/quickstart)                                                      | https://cursor.com/cn/docs/get-started/quickstart                                                              |                                                             |
| [Claude code一键安装](https://fintopia.feishu.cn/wiki/FwLewJpBui2m1EkDs54cfE2XnKg)                                       | https://fintopia.feishu.cn/wiki/FwLewJpBui2m1EkDs54cfE2XnKg                                                    |                                                             |
| [吴恩达agent教程课](https://www.bilibili.com/video/BV1DfrdByE2H/?spm_id_from=333.337.search-card.all.click)                | https://www.bilibili.com/video/BV1DfrdByE2H/?spm_id_from=333.337.search-card.all.click                         |                                                             |
| [黑马程序员大模型RAG与Agent智能体项目实战教程](https://www.bilibili.com/video/BV1yjz5BLEoY/?spm_id_from=333.337.search-card.all.click) | https://www.bilibili.com/video/BV1yjz5BLEoY/?spm_id_from=333.337.search-card.all.click                         |                                                             |
| [AI 核心概念大串联](https://www.bilibili.com/video/BV1E7wtzaEdq/?spm_id_from=333.337.search-card.all.click)                 | https://www.bilibili.com/video/BV1E7wtzaEdq/?spm_id_from=333.337.search-card.all.click                         |                                                             |
| 第四章                                                                                                                  | https://ai.fintopia.tech/hub/mcp-market                                                                        | https://ai.fintopia.tech/hub/mcp-market                     |
| https://github.com/modelcontextprotocol/servers                                                                      | https://github.com/modelcontextprotocol/servers                                                                |                                                             |
| https://smithery.ai/                                                                                                 | https://smithery.ai/                                                                                           |                                                             |
| https://mcp.so/                                                                                                      | https://mcp.so/                                                                                                |                                                             |
| https://www.modelscope.cn/mcp                                                                                        | https://www.modelscope.cn/mcp                                                                                  |                                                             |
| [MCP简易入门教程](https://www.bilibili.com/video/BV1HFd6YhErb/?spm_id_from=333.337.search-card.all.click)                  | https://www.bilibili.com/video/BV1HFd6YhErb/?spm_id_from=333.337.search-card.all.click                         |                                                             |
| [从原理到实战，带你深入掌握MCP](https://www.bilibili.com/video/BV1uronYREWR/?spm_id_from=333.337.search-card.all.click)           | https://www.bilibili.com/video/BV1uronYREWR/?spm_id_from=333.337.search-card.all.click                         |                                                             |
| 第五章                                                                                                                  | vat_2025_04.xlsx                                                                                               | 暂时无法在飞书文档外展示此内容                                             |
| https://claude.com/plugins/skill-creator                                                                             | https://claude.com/plugins/skill-creator                                                                       |                                                             |
| [什么是skill](https://www.bilibili.com/video/BV1dz6oBWEWx/?spm_id_from=333.337.search-card.all.click)                   | https://www.bilibili.com/video/BV1dz6oBWEWx/?spm_id_from=333.337.search-card.all.click                         |                                                             |
| [skill原理及使用教程](https://www.bilibili.com/video/BV1cGigBQE6n/?spm_id_from=333.337.search-card.all.click)               | https://www.bilibili.com/video/BV1cGigBQE6n/?spm_id_from=333.337.search-card.all.click                         |                                                             |
| [Cursor Skills 配置完全教程](https://fintopia.feishu.cn/wiki/KrnQwbchbiWQ1okrpFxcvNiSnBh)                                  | https://fintopia.feishu.cn/wiki/KrnQwbchbiWQ1okrpFxcvNiSnBh                                                    |                                                             |
| 第六章                                                                                                                  | [御三家模型评测与提示词指南_2026Q1](https://fintopia.feishu.cn/docx/PshvdbrKwoAITaxexlqcP5HWnCf?from=from_copylink)         | https://fintopia.feishu.cn/wiki/GpVSwC3oNi79wxkwjOcc0YZknlb |
| 附录                                                                                                                   | [Cursor · 新手学习指南](https://fintopia.feishu.cn/wiki/Lx6nwQP1XiYU3zko24hc0xq8n5e)                                 | https://fintopia.feishu.cn/wiki/Lx6nwQP1XiYU3zko24hc0xq8n5e |
|                                                                                                                      | [Cursor Marketplace \| Cursor Plugins](https://cursor.com/cn/marketplace)                                      | https://cursor.com/cn/marketplace                           |