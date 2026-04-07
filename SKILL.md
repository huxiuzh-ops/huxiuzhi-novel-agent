# SKILL.md — novel-agent · OpenClaw 入口

> **本文件是 OpenClaw 平台的薄适配层**，它加载 `AGENT.md` 作为核心定义。
>
> 所有通用的角色、任务、工作流定义，请查阅 `AGENT.md`。
> 本文件只包含 OpenClaw 平台特定的约定。

---

## 一、加载顺序

读取本文件后，Agent 应按以下顺序加载：

1. `AGENT.md` — 核心业务定义（必读）
2. `AGENT_EXEC.md` — 角色执行协调器规范（必读）
3. `config/project.yaml` — 项目基础配置
4. `config/writing.yaml` — 写作规则
5. `config/validation.yaml` — 验证规则
6. `config/platforms.yaml` — 平台配置
7. `roles/supervisor.md` — Supervisor 角色提示
8. `roles/planner.md` — Planner 角色提示
9. `roles/writer.md` — Writer 角色提示
10. `roles/editor.md` — Editor 角色提示
11. `roles/world.md` — World 角色提示

---

## 二、核心工作流：写章节（Supervisor → Planner → Writer → Editor）

### 流程图

```
用户："写第8章"
    ↓
Supervisor（接收请求，判断类型，装配上下文）
    ↓
Planner（生成章节 mini plan）
    ↓
Writer（根据 plan 写正文草稿）
    ↓
Editor（审稿：一致性/伏笔/风格/风险）
    ↓
Supervisor（根据 verdict 分流）
    ├─ passed → 更新索引 → 交付
    ├─ warning → 打回 Writer 修订 → 再次 Editor 审稿
    └─ requires_human → 生成决策卡片 → 暂停等确认
```

### 详细步骤

#### Step 1：Supervisor 接收请求

当用户说"写第8章"时，Supervisor 执行：

1. 读取 `config/writing.yaml` → 确认字数要求（如 3000 字）
2. 读取 `index/chapters.json` → 确认当前章节状态
3. 读取 `index/beats.jsonl` → 获取待推进伏笔
4. 读取 `index/characters.json` → 获取相关角色摘要
5. 组装 `planner_context`，传给 Planner

#### Step 2：Planner 产出 mini plan

Supervisor 调用 Planner，读取 `roles/planner.md` 作为提示。

Planner 输出格式化的章节计划：

```
chapter: ch008
goal: 推进地图线索，制造陈墨与林月的张力
opening: 从渡口夜风和戒备状态切入
middle: [陈墨试图确认交易对象, 林月识别地图符号并试探, 黑水营内部矛盾露头]
turning_point: 军方旧信号被意外激活
ending_hook: 有人在暗处呼叫陈墨的真名
must_include: [beat_002]
```

#### Step 3：Writer 写草稿

Supervisor 调用 Writer，读取 `roles/writer.md` 作为提示。

Writer 根据 plan + 相关角色正文 + style_guide 写 3000+ 字正文。

Writer 必须输出：
- 正文草稿
- 章节摘要（1-2 句话）
- 推进了哪些伏笔
- 新埋了哪些伏笔
- 时间线候选事件

#### Step 4：Editor 审稿

Supervisor 调用 Editor，读取 `roles/editor.md` 作为提示。

Editor 检查：
- **一致性**：角色状态是否延续、角色是否在同一时间出现在两个地点
- **伏笔**：must_include 的伏笔是否被推进
- **写作规范**：字数 >= 3000、对话连续不超过 5 行、结尾有钩子
- **风险**：识别高风险项

Editor 输出：
```
verdict: warning
issues: [{type, severity, message, suggested_fix, location}]
revision_required: true/false
requires_human_decision: true/false
```

#### Step 5：Supervisor 分流

- `verdict=passed` → 保存正文到 `chapters/ch008.md` → 更新 `index/chapters.json` + `index/beats.jsonl` → 交付
- `verdict=warning` + `revision_required=true` → 调用 Writer 修订 → 再次 Editor 审稿
- `requires_human=true` → 生成结构化决策卡片 → 暂停

#### Step 6：决策点处理（如果 requires_human）

决策卡片格式（来自 `AGENT.md`）：

```
decision_id: decision_001
type: major_plot_change
status: waiting_human
summary: 是否让林月在 ch012 提前得知实验真相？
why_it_matters: 会削弱 ch018 的反转力度
options: [
  {id: A, label: 提前得知, pros: [...], cons: [...]},
  {id: B, label: 只获取部分信息, pros: [...], cons: [...]}
]
recommended: B
```

Supervisor 将此写入 `index/decisions.jsonl`，并告诉用户：

> ⚠️ 需要你确认：xxx（选项 A/B/C）

用户确认后，Supervisor 继续执行。

---

## 三、OpenClaw 特有约定

### 3.1 文件写入

| 操作 | 方式 |
|------|------|
| 写章节正文 | `exec` → `chapters/chXXX.md` |
| 更新伏笔 | `exec` → 追加到 `beats/TRACKING.md` 和 `index/beats.jsonl` |
| 更新章节索引 | `exec` → `python scripts/incremental_index_update.py ...` |
| 更新角色状态 | `exec` → `python scripts/incremental_index_update.py ... update_character ...` |

### 3.2 索引读取优先级

**始终先读索引，再读正文**：

1. `index/chapters.json` — 有哪些章节、状态、摘要
2. `index/characters.json` — 有哪些角色、状态、出场
3. `index/beats.jsonl` — 伏笔状态
4. `index/locations.json` — 地点
5. `index/decisions.jsonl` — 待决策项
6. 最后才读 `chapters/*.md`、`characters/*.md`、`world.md`

### 3.3 工作流状态记录

```bash
# 启动工作流
python scripts/workflow_state.py <workspace> start write_chapter task_001 --workflow write_chapter --start_role Planner

# 推进工作流
python scripts/workflow_state.py <workspace> advance --next_role Writer

# 标记等待决策
python scripts/workflow_state.py <workspace> waiting

# 恢复工作流
python scripts/workflow_state.py <workspace> resume --decision A

# 查看状态
python scripts/workflow_state.py <workspace> status
```

### 3.4 定时任务

通过 OpenClaw cron 可设置：
- 每日伏笔状态检查（`python scripts/beat_tracker.py <workspace>`）
- 章节字数统计
- 一致性定期扫描（`python scripts/consistency_check.py <workspace>`）

### 3.5 消息推送

章节完成后可通过 OpenClaw 飞书集成推送通知。

---

## 四、入口命令参考

| 用户说 | 系统做 |
|--------|--------|
| "写第8章" | 执行 write_chapter workflow（Supervisor→Planner→Writer→Editor） |
| "审一下第5章" | 执行 review_chapter workflow（Supervisor→Editor） |
| "帮我规划第二卷" | 执行 plan_volume workflow（Supervisor→Planner） |
| "新增一个角色" | 调用 World.add_character |
| "这个角色在哪几章出现过" | 查询 `index/characters.json` |
| "检查一下伏笔" | 运行 `python scripts/beat_tracker.py <workspace>` |
| "检查一致性" | 运行 `python scripts/consistency_check.py <workspace>` |
| "改成全自动" | 更新 `novel-agent.yaml` 的 `default_autonomy: L1` |
| "重建索引" | 运行 `python scripts/build_index.py <workspace>` |

---

## 五、工作空间结构

```
workspace/                    ← 用户小说项目目录
├── novel-agent.yaml         ← 项目配置（Setup Wizard 生成）
├── world.md                 ← 世界设定
├── style_guide.md          ← 写作风格
├── characters/              ← 角色档案
├── outline/                 ← 大纲
├── beats/                   ← 伏笔追踪（手工）
├── chapters/               ← 章节正文
├── inventory/              ← 装备道具
├── index/                  ← 结构化索引（自动维护）
│   ├── characters.json
│   ├── chapters.json
│   ├── beats.jsonl
│   ├── locations.json
│   ├── timeline.jsonl
│   ├── decisions.jsonl
│   └── world_rules.json
└── .learnings/            ← 自我进化
    ├── LEARNINGS.md
    ├── ERRORS.md
    └── FEATURE_REQUESTS.md
```

---

## 六、快速开始

在 OpenClaw workspace 中打开本目录，对 Agent 说：

```
你好，我的小说 Agent，帮我初始化新书
```

Agent 会：
1. 复制 `workspace-template/` 到你的小说目录
2. 引导你填写 `novel-agent.yaml`
3. 引导你填写 `world.md` 和角色档案

---

## 七、相关文件

| 文件 | 作用 |
|------|------|
| `AGENT.md` | **核心定义**（角色/任务/工作流/索引 schema） |
| `AGENT_EXEC.md` | 角色执行协调器规范 |
| `config/*.yaml` | 框架配置（项目无关的通用参数） |
| `roles/*.md` | 5 个角色的具体提示模板 |
| `scripts/` | 工作流脚本、索引构建、状态管理 |
| `SKILL.md` | 本文件 — OpenClaw 平台入口 |
| `CLAUDE.md` | Claude Code / Codex 平台入口 |
| `SETUP_WIZARD.md` | 首次使用引导 |
| `docs/QUICKSTART.md` | 10 分钟快速入门 |
