# AGENTS.md — novel-agent · Codex / Codex 入口

> **本文件是 Codex / Codex 平台的薄适配层**，它加载 `AGENT.md` 作为核心定义。
>
> 所有通用的角色、任务，工作流定义，请查阅 `AGENT.md`。
> 本文件只包含 Codex / Codex 平台特定的约定。

---

## 一、加载顺序

进入本目录后，Codex 会自动读取本文件。建议按以下顺序理解项目：

1. 本文件 — 了解入口方式
2. `AGENT.md` — 核心业务定义（必读）
3. `AGENT_EXEC.md` — 角色执行协调器规范（必读）
4. `config/` — 框架配置
5. `roles/` — 5 个角色提示模板（必读，用于实际写作时）
6. `SETUP_WIZARD.md` — 如果首次使用
7. `docs/QUICKSTART.md` — 10 分钟快速入门

---

## 二、快速开始

在 `novel-agent` 目录下启动 Codex：

```bash
cd novel-agent
Codex
```

然后直接告诉 Agent 你要做什么：

```
帮我初始化一个新项目
写第三章
审一下第5章
规划第二卷的大纲
新增一个角色
检查一下前10章有没有矛盾
```

---

## 三、核心工作流：写章节

当你说"写第8章"时，Agent 会按以下链路执行：

```
Supervisor → Planner → Writer → Editor → Supervisor（分流）
```

**不要跳过中间步骤，直接写正文**。这样做的好处：
- Planner 先钉住章节方向，Writer 不会跑偏
- Editor 做一致性检查，避免前后矛盾
- 全程有记录，出问题可回溯

### 各角色职责

| 角色 | 做什么 | 参考模板 |
|------|--------|---------|
| **Supervisor** | 判断任务类型，装配上下文，决定是否等用户确认 | `roles/supervisor.md` |
| **Planner** | 生成章节 mini plan（目标/开头/中段/转折/结尾钩子） | `roles/planner.md` |
| **Writer** | 根据 plan 写正文，输出草稿 + 摘要 + 伏笔变化 | `roles/writer.md` |
| **Editor** | 审稿，检查一致性/伏笔/风格/风险 | `roles/editor.md` |
| **World** | 处理设定变更，检测冲突 | `roles/world.md` |

### 工作流中的索引读取

**先读索引，再读正文**：

```python
# 写章节前，先读这些
index/chapters.json       # 当前章节状态
index/beats.jsonl        # 待推进伏笔
index/characters.json     # 相关角色摘要
index/locations.json      # 地点
```

---

## 四、Codex 特有约定

### 4.1 工具使用

| 操作 | 工具 |
|------|------|
| 写章节正文 | `Write` / `Edit` 工具 → `chapters/chXXX.md` |
| 更新伏笔 | `Edit` → 追加到 `beats/TRACKING.md` 或 `index/beats.jsonl` |
| 更新索引 | `Write` → 写入 `index/*.json` 或 `index/*.jsonl` |
| 运行检查脚本 | `Bash` → `python scripts/*.py <workspace>` |
| 知识图谱写入 | `Append` → `memory/ontology/graph.jsonl` |

### 4.2 工作流状态

```bash
# 启动工作流
python scripts/workflow_state.py <workspace> start write_chapter task_001 --workflow write_chapter

# 推进工作流
python scripts/workflow_state.py <workspace> advance --next_role Writer

# 标记等待决策
python scripts/workflow_state.py <workspace> waiting

# 恢复工作流
python scripts/workflow_state.py <workspace> resume --decision A

# 查看状态
python scripts/workflow_state.py <workspace> status
```

### 4.3 环境要求

- Python 3.7+（用于运行 `scripts/*.py`）
- PyYAML：`pip install pyyaml`

---

## 五、常用命令

| 你说 | Agent 做 |
|------|---------|
| `写第 X 章` | 执行 write_chapter workflow |
| `审一下第 X 章` | 执行 review_chapter workflow |
| `帮我规划第二卷` | 执行 plan_volume workflow |
| `新增一个角色` | 调用 World.add_character |
| `查一下这个角色` | 读 `index/characters.json` |
| `查伏笔状态` | 读 `index/beats.jsonl` |
| `检查一致性` | `python scripts/consistency_check.py <workspace>` |
| `检查伏笔` | `python scripts/beat_tracker.py <workspace>` |
| `重建索引` | `python scripts/build_index.py <workspace>` |
| `改成全自动` | 更新 `novel-agent.yaml` 的 `default_autonomy: L1` |

---

## 六、目录结构

```
novel-agent/
├── AGENT.md              ← 核心定义（角色/任务/工作流/schema）
├── AGENT_EXEC.md        ← 角色执行协调器规范
├── SKILL.md              ← OpenClaw 入口
├── AGENTS.md             ← 本文件 — Codex / Codex 入口
├── SETUP_WIZARD.md       ← 首次使用引导
├── docs/QUICKSTART.md   ← 10 分钟快速入门
├── README.md             ← 项目介绍
├── config/               ← 框架配置（4个 YAML）
│   ├── project.yaml
│   ├── writing.yaml
│   ├── validation.yaml
│   └── platforms.yaml
├── roles/                 ← 角色提示模板
│   ├── supervisor.md
│   ├── planner.md
│   ├── writer.md
│   ├── editor.md
│   └── world.md
├── scripts/               ← 工具脚本
│   ├── build_index.py
│   ├── incremental_index_update.py
│   ├── workflow_state.py
│   ├── consistency_check.py
│   ├── beat_tracker.py
│   └── run_demo.py
├── memory/ontology/        ← 知识图谱
│   ├── schema.yaml
│   └── graph.jsonl
├── index/                  ← 结构化索引 schema
├── workspace-template/      ← 用户项目模板
└── docs/                  ← 各平台安装指南
```

---

## 七、用户项目放在哪？

**本目录是 novel-agent 的框架代码**，你的小说项目应该在同级另一个目录里。

建议结构：

```
projects/
├── novel-agent/           ← 本仓库（框架，不改）
└── my-novel/             ← 你的小说项目
    ├── novel-agent.yaml
    ├── world.md
    ├── characters/
    ├── chapters/
    ├── outline/
    ├── beats/
    ├── index/
    └── style_guide.md
```

进入你的小说目录后，告诉 Agent：
```
使用 novel-agent 框架帮我写小说
```
或直接：
```
初始化新书
```

---

## 八、相关文件

| 文件 | 作用 |
|------|------|
| `AGENT.md` | **核心定义**（角色/任务/工作流/索引 schema） |
| `AGENT_EXEC.md` | 角色执行协调器规范 |
| `config/*.yaml` | 框架配置（项目无关的通用参数） |
| `roles/*.md` | 5 个角色的具体提示模板 |
| `scripts/` | 工作流脚本、索引构建、状态管理 |
| `SKILL.md` | OpenClaw 平台入口 |
| `AGENTS.md` | 本文件 — Codex / Codex 入口 |
| `SETUP_WIZARD.md` | 首次使用引导 |
| `docs/QUICKSTART.md` | 10 分钟快速入门 |
