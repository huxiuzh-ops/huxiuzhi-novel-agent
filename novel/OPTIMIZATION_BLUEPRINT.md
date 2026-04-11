# novel-agent 产品优化蓝图

> 创建时间：2026-04-07
> 作者：神风大王

---

## 0. 产品目标重述

先把定位钉牢，不然后面设计容易跑偏。

### 产品目标

novel-agent 不是一个单纯的"AI 写小说工具"，而是一个：

**面向长篇小说创作的、开箱即用的 AI 协作工作台**

它需要同时满足 4 件事：

1. **新手可用** - 用户 clone / 下载后，哪怕不懂 agent 架构，也能开始用。
2. **多平台兼容** - 同一套核心方法，应尽量兼容：
   - OpenClaw
   - Claude Code
   - Codex / Cursor 类环境
   - 直接 API Key 模式
   - 本地 Web UI 模式
3. **AI 友好** - 项目结构、配置方式、上下文组织、任务拆分，要符合 LLM 的习惯：
   - 上下文可切片
   - 规则清楚
   - 文件层次分明
   - 结构化和自然语言并存
   - 尽量避免"全靠模型猜"
4. **长期可维护** - 不是只演示一次"能写一章"，而是可以持续支撑：
   - 长篇
   - 多卷
   - 长周期
   - 设定演化
   - 用户纠错
   - 版本修改

---

## 1. 总体优化方向

建议把这个项目优化成**三层架构**：

### 第一层：AI 工作层

就是 agent 真正干活的层：
- 任务识别
- 上下文拼装
- 写作 / 审稿 / 规划 / 查设定
- 决策点处理
- 输出与记录

这层要符合 OpenClaw / Claude / Codex / API 的习惯。

### 第二层：项目状态层

这是当前项目最缺的一层。它负责维护长期状态：
- 章节状态
- 角色状态
- 伏笔状态
- 时间线事件
- 世界规则
- 决策记录
- learnings
- 索引

这层是系统长期稳定的关键。

### 第三层：工作台层

这是用户能感知到的产品层：
- Web UI
- Dashboard
- Chapter Studio
- Timeline
- Beat Board
- Decision Center
- Reports
- Settings

### 一句话理解

你现在这个项目，已经有：
- AI 工作层的雏形
- 工作台层的轻原型

但最缺的是：**项目状态层**

而这个状态层，正是"结构化索引""时间线""决策记录""实体索引"的核心。

---

## 2. 多 Agent / 编排层怎么做

### 2.1 目标

不是为了炫技搞多 Agent，而是为了解决：
- 复杂任务拆分
- 上下文隔离
- 输出可复核
- 失败可回退
- 人机协作边界清楚

所以第一版不要追求"真的五个 agent 并发乱飞"，而是做成：

**单运行时 + 多角色协议 + 可选子任务拆分**

这更符合"开箱即用"。

### 2.2 推荐架构：Role-based Workflow，而不是重型图系统

第一版建议不要直接做成 LangGraph 那么重。而是做一个 role-based workflow engine：

**核心角色**
- Supervisor
- Planner
- Writer
- Editor
- World

**核心任务类型**
- plan_book
- plan_volume
- plan_chapter
- write_chapter
- review_chapter
- update_world
- query_knowledge
- resolve_decision

**核心状态**
- pending
- running
- blocked
- waiting_human
- done
- failed

### 2.3 任务流模型

每次请求都形成一个 Task：

```json
{
  "task_id": "task_20260407_001",
  "type": "write_chapter",
  "role": "Writer",
  "status": "running",
  "chapter": "ch008",
  "input_refs": [
    "outline/volumes/volume_01.md",
    "characters/chenmo.md",
    "beats/TRACKING.md"
  ],
  "depends_on": ["task_20260407_000_plan"],
  "outputs": [],
  "created_at": "2026-04-07T08:00:00Z"
}
```

### 2.4 任务执行方式

**方案 A：轻量串行**（最适合第一版）

- Supervisor 收到请求
- 识别任务类型
- 组装上下文
- 调用相应 role prompt
- 产出结果
- 如果需要，再进入下一步

比如写章节流程：
1. Supervisor 判断：这是 write_chapter
2. Planner 先产出本章 mini plan
3. Writer 写草稿
4. Editor 做审稿
5. 有冲突则 waiting_human 或回写修正
6. 最终交付

**为什么推荐串行？**
- 更稳定
- 更便于兼容 OpenClaw / Claude / Codex / API
- 更符合大多数 AI 工具的调用方式
- 不需要一开始就做复杂并发

### 2.5 跨平台兼容怎么设计

统一思路：不要把平台差异写死在业务逻辑里。应该拆成：
- **Core Workflow** - 负责任务类型、状态机、上下文拼装、角色切换、决策点、索引更新、结果输出
- **Platform Adapter** - 负责 OpenClaw 怎么读 skill、Claude Code 怎么读 CLAUDE.md、Codex 怎么接入口、API Key 模式怎么传 system prompt / context

### 2.6 平台适配建议

**OpenClaw**
- SKILL.md 为入口
- 强调任务分发、文件结构、脚本工具
- 推荐支持"主会话 + 子任务"

**Claude Code / Codex**
- CLAUDE.md / AGENT.md 类入口
- 以本地文件工作流为主
- 更偏单机使用

**API Key 模式**
- 提供统一 prompt bundle
- 或一个最小 server / sdk
- 用户只要填 key 和模型供应商即可

**Web UI 模式**
- 用内部 workflow engine
- UI 调 workflow API，而不是直接到处拼字符串

### 2.7 第一版不建议做什么

为了保持开箱即用，建议第一版不要做：
- 真正分布式多 agent
- 复杂消息队列
- 图数据库作为硬依赖
- 强绑定某个框架（比如必须 LangGraph）
- 很重的 infra

因为这会破坏"开箱即用"。

---

## 3. 配置系统怎么做

### 3.1 目标

把原来散落在 README / SKILL / CLAUDE 里的规则，变成统一可读配置。

### 3.2 配置分层

建议做四类配置：

#### 1）项目配置 `config/project.yaml`

```yaml
project:
  title: "末世废土长篇"
  language: "zh-CN"
  genre: "post-apocalyptic"
  narrative_framework: "three_act"
  default_autonomy: "L2"
```

#### 2）写作配置 `config/writing.yaml`

```yaml
writing:
  min_words_per_chapter: 3000
  max_consecutive_dialogue_lines: 5
  require_chapter_hook: true
  prefer_show_not_tell: true
  style_guide_path: "style_guide.md"
```

#### 3）验证配置 `config/validation.yaml`

```yaml
validation:
  consistency_check: true
  beat_tracking: true
  timeline_check: true
  style_review:
    enabled: false
    level: "light"
  report_level: "light"
```

#### 4）平台配置 `config/platforms.yaml`

```yaml
platforms:
  openclaw:
    enabled: true
    entry: "SKILL.md"
  claude_code:
    enabled: true
    entry: "CLAUDE.md"
  codex:
    enabled: true
    entry: "CLAUDE.md"
  api_mode:
    enabled: true
    provider: "openai"
    model: "gpt-4.1"
```

### 3.3 为什么这样分层？

这样能区分：
- 小说内容规则
- 写作执行规则
- 校验策略
- 平台接入方式

这样后面维护不会混乱。

### 3.4 UI 怎么用配置

UI 直接读取配置，展示：
- 当前最少字数
- 是否开启时间线检查
- 报告等级
- 当前平台入口
- 自主程度等级

### 3.5 Agent 怎么用配置

Agent 在执行前读取配置，决定：
- 是否先规划后写
- 是否必须审稿
- 是否遇到冲突就停
- 是否生成轻量报告还是深度报告

---

## 4. 结构化索引怎么做

### 4.1 一句话定义

结构化索引不是替代 markdown 正文，而是给 AI 和程序提供一套**稳定、快速、低 token 成本的检索层**。

### 4.2 为什么要做结构化索引？

因为 AI 处理长篇项目时，最怕两件事：
- 每次都重新读大量自然语言文件
- 每次都从自然语言中重新抽信息

这会导致：
- token 贵
- 不稳定
- 容易漏
- 速度慢

所以要做的不是"让 AI 更努力读"，而是：**提前把常用信息整理成机器可读索引**。

### 4.3 推荐的双层结构

**层 1：正文文件（人写、人读）**
- world.md
- characters/*.md
- outline/*.md
- chapters/*.md
- beats/TRACKING.md

**层 2：结构化索引（机器读）**
- index/characters.json
- index/chapters.json
- index/beats.jsonl
- index/locations.json
- index/timeline.jsonl
- index/decisions.jsonl

### 4.4 第一版建议做的 5 个索引

#### 1）角色索引 `index/characters.json`

```json
[
  {
    "id": "char_chenmo",
    "name": "陈墨",
    "file": "characters/chenmo.md",
    "role": "protagonist",
    "faction": "黑水营",
    "status": "alive",
    "first_appearance": "ch001",
    "last_appearance": "ch008"
  }
]
```

**用途**：快速列角色、快速定位角色文件、判断出场状态、章节检索

#### 2）章节索引 `index/chapters.json`

```json
[
  {
    "id": "ch008",
    "file": "chapters/ch008.md",
    "title": "黑夜渡口",
    "status": "draft",
    "word_count": 3520,
    "summary": "陈墨在渡口与林月再度交锋",
    "characters": ["char_chenmo", "char_linyue"],
    "locations": ["loc_dukou"],
    "beats_advanced": ["beat_002"]
  }
]
```

**用途**：Dashboard、章节列表、章节摘要调用、上下文选择

#### 3）伏笔索引 `index/beats.jsonl`

```jsonl
{"id":"beat_002","description":"残缺地图背后的军方实验","planted_in":"ch003","planned_payoff":"ch010","status":"pending","related_characters":["char_chenmo"]}
```

**用途**：哪些伏笔待回收、哪些伏笔逾期、写下一章时优先读哪些内容

#### 4）地点索引 `index/locations.json`

```json
[
  {
    "id": "loc_dukou",
    "name": "渡口",
    "region": "北境",
    "kind": "transport_hub",
    "first_appearance": "ch004",
    "last_appearance": "ch008"
  }
]
```

**用途**：Scene / Timeline / World Bible 页面、避免地点名混乱、帮助世界观一致性

#### 5）时间线索引 `index/timeline.jsonl`

属于结构化索引的一部分（见第5节）。

### 4.5 索引怎么生成？

推荐采用 **AI 提取 + 规则校验 + 人工可修正** 三步法。

**第一步：AI 提取**
当章节写完或设定更新后，自动从正文抽出：
- 新角色
- 新地点
- 新事件
- 新伏笔
- 状态变化

**第二步：规则校验**
脚本检查：
- id 是否重复
- chapter 是否存在
- status 是否合法
- 引用实体是否存在

**第三步：人工可修正**
如果 AI 抽错，用户能在 UI 里直接改，不要让索引变成不可控黑盒。

### 4.6 索引能带来什么提升？

**提升 1：减少 token 消耗** - 不用每次重读所有角色文件和章节文件。

**提升 2：提高稳定性** - 角色年龄、状态、势力不会每次被模型临时理解错。

**提升 3：提高速度** - UI 和 Agent 都可以先走索引，再决定读哪些正文。

**提升 4：让更高级功能成为可能** - 比如 timeline、ontology、决策点影响分析、版本追踪、风险检测。

---

## 5. 时间线系统设计

### 5.1 为什么必须做

结构化索引解决"查得快"，时间线系统解决"长期不乱"。

### 5.2 文件结构

```
timeline/
  events.jsonl
  constraints.yaml
  snapshots/
```

### 5.3 时间线最少要支持 4 种记录

- 事件发生
- 人物位置变化
- 信息获得
- 状态变化

### 5.4 系统能力

- 时间顺序检查
- 人物是否瞬移
- 谁何时知道什么
- 死亡/受伤/装备变化是否延续

---

## 6. 决策点系统设计

### 6.1 目标

把"人类掌舵"真正做成产品能力，而不是一句口号。

### 6.2 决策点类型

- 角色死亡
- 主线改动
- 世界规则变更
- 新势力登场
- 伏笔废弃
- 大纲偏移
- 高风险冲突

### 6.3 数据结构

```json
{
  "id": "decision_001",
  "type": "major_plot_change",
  "chapter": "ch012",
  "status": "waiting_human",
  "summary": "是否让主角提前得知真相",
  "why_it_matters": "会影响 ch018 的反转",
  "options": [
    {"id":"A","label":"提前得知","pros":["冲击强"],"cons":["削弱后续反转"]},
    {"id":"B","label":"只得到部分信息","pros":["保留悬念"],"cons":["当前刺激弱一点"]}
  ],
  "recommended": "B"
}
```

### 6.4 UI 展现

做一个 Decision Center：
- 待决策列表
- 风险等级
- 推荐方案
- 方案影响范围
- 一键确认或自定义

---

## 7. 报告系统设计

### 7.1 报告等级

- off
- light
- standard
- deep

### 7.2 规则型报告 vs 模型型报告

**规则型**
- 字数
- 对话比例
- 伏笔推进
- 时间线冲突
- 出场角色

**模型型**
- 文风偏差
- 节奏建议
- 修改建议
- 角色语气偏差

**默认策略**：先规则型，再按需模型型。

---

## 8. UI 工作台设计

### 8.1 核心页面

- Dashboard
- Chapter Studio
- World Bible
- Beat Board
- Timeline
- Decision Center
- Reports
- Settings

### 8.2 优先级建议

**P0**
- Dashboard
- Chapter Studio
- Beat Board

**P1**
- Timeline
- Decision Center
- Reports

**P2**
- World Bible
- Agent Trace / Logs

---

## 9. 可解释性 / Trace 设计

### 9.1 目标

让用户知道 AI 为什么这么做。

### 9.2 每个任务记录

- 输入文件
- 用到哪些索引
- 执行了哪些检查
- 哪些地方触发了决策点
- 最终改了哪些内容

---

## 10. 成本控制与上下文预算

### 10.1 核心原则

- 检索优先
- 摘要优先
- 规则检查优先
- 重模型只用于重任务

### 10.2 任务分级

- **轻任务**：查资料、列伏笔
- **中任务**：审稿、规划
- **重任务**：写章节、重构剧情

### 10.3 预算策略

- 先读索引
- 再读相关正文
- 超限就压缩
- 报告按等级开关

---

## 11. 开箱即用落地建议

### 11.1 Setup Wizard

第一次打开时，引导用户完成：
- 小说类型
- 框架
- 自主等级
- 是否启用时间线
- 是否启用深度报告
- 当前平台

### 11.2 Workspace Template

生成标准目录和初始模板。

### 11.3 Platform Presets

给几套预设：
- OpenClaw preset
- Claude Code preset
- Codex preset
- API-only preset

### 11.4 Safe Default

默认：
- 轻量报告
- 半自动
- 开启基础一致性检查
- 开启结构化索引
- 关闭高成本深度分析

---

## 12. 实施路线图

### 第一阶段（最值得先做）

1. 配置系统
2. 结构化索引
3. 章节索引 / 角色索引 / 伏笔索引
4. 轻量任务状态记录
5. Setup Wizard 强化

**这一阶段完成后**：项目会从"概念完整"变成"AI 真正更容易用"。

### 第二阶段

6. 时间线系统
7. 决策点系统
8. 轻量报告分级
9. Dashboard / Chapter Studio 升级

**这一阶段完成后**：项目会从"能用"变成"适合长期写作"。

### 第三阶段

10. Trace Layer
11. 更完整的 World Bible
12. 更成熟的跨平台 adapter
13. 更高级的模型路由 / 成本控制

**这一阶段完成后**：项目会从"工具"升级成"创作基础设施"。

---

## 核心判断

如果按产品定位来讲，这个项目最该优先优化的不是"更炫的 AI 能力"，而是这三件事：

**第一优先：结构化索引**

因为它直接决定：
- token 成本
- 稳定性
- 可扩展性
- 跨平台兼容性

**第二优先：轻量编排层**

因为它决定：
- 任务能不能真正分工
- 能不能保持"AI 习惯友好"
- 能不能做决策点和回退

**第三优先：开箱即用配置与引导**

因为这是产品能不能真正被别人用起来的关键。
