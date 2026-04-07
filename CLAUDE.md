# CLAUDE.md — novel-agent · Claude Code / Codex 入口

> **本文件是 Claude Code / Codex 平台的薄适配层**，它加载 `AGENT.md` 作为核心定义。
> 
> 所有通用的角色、任务、工作流定义，请查阅 `AGENT.md`。
> 本文件只包含 Claude Code / Codex 平台特定的约定。

---

## 一、加载顺序

进入本目录后，Claude Code 会自动读取本文件。建议按以下顺序理解项目：

1. 本文件 — 了解入口方式
2. `AGENT.md` — 核心业务定义（必读）
3. `config/` — 框架配置
4. `SETUP_WIZARD.md` — 如果首次使用

---

## 二、快速开始

在 `novel-agent` 目录下启动 Claude Code：

```bash
cd novel-agent
claude
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

## 三、Claude Code 特有约定

### 3.1 工作命令

| 你说 | Agent 做 |
|------|---------|
| `写第 X 章` | write_chapter workflow |
| `审一下第 X 章` | review_chapter workflow |
| `规划第 X 卷` | plan_volume workflow |
| `新增角色` | World.add_character |
| `检查一致性` | 运行 `python scripts/consistency_check.py <workspace>` |
| `查一下这个角色` | 读 `index/characters.json` 或 `characters/*.md` |

### 3.2 工具使用

- **写章节**：用 `Write` / `Edit` 工具操作 `chapters/chXXX.md`
- **更新伏笔**：用 `Edit` 追加到 `beats/TRACKING.md` 或 `index/beats.jsonl`
- **运行脚本**：`Bash` 工具运行 `python scripts/*.py`
- **知识图谱**：`Append` 到 `memory/ontology/graph.jsonl`

### 3.3 环境要求

- 需要 Python 3.7+（用于运行 `scripts/*.py`）
- 项目文件为 Markdown 格式，无需编译

---

## 四、目录结构

```
novel-agent/
├── AGENT.md              ← 核心定义（角色/任务/工作流/schema）
├── SKILL.md              ← OpenClaw 入口
├── CLAUDE.md             ← 本文件 — Claude Code / Codex 入口
├── SETUP_WIZARD.md       ← 首次使用引导
├── README.md             ← 项目介绍
├── config/               ← 框架配置（4个 YAML）
│   ├── project.yaml
│   ├── writing.yaml
│   ├── validation.yaml
│   └── platforms.yaml
├── server.js             ← Web UI 服务器
├── scripts/              ← Python 验证脚本
│   ├── consistency_check.py
│   ├── beat_tracker.py
│   ├── context_compressor.py
│   └── outline_generator.py
├── memory/ontology/       ← 知识图谱
│   ├── schema.yaml
│   └── graph.jsonl
├── index/                 ← 结构化索引（第一版可选）
├── workspace-template/    ← 用户项目模板
└── docs/                  ← 各平台安装指南
```

---

## 五、用户项目放在哪？

**本目录是 novel-agent 的框架代码**，你的小说项目应该在同级另一个目录里。

建议结构：

```
projects/
├── novel-agent/           ← 本仓库（框架，不改）
└── my-novel/             ← 你的小说项目
    ├── world.md
    ├── characters/
    ├── chapters/
    ├── outline/
    ├── beats/
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

## 六、相关文件

| 文件 | 作用 |
|------|------|
| `AGENT.md` | **核心定义**（角色/任务/工作流/索引 schema） |
| `config/*.yaml` | 框架配置（项目无关的通用参数） |
| `SKILL.md` | OpenClaw 平台入口 |
| `CLAUDE.md` | 本文件 — Claude Code / Codex 入口 |
| `SETUP_WIZARD.md` | 首次使用引导 |
| `README.md` | 项目介绍 |
| `docs/COMPATIBILITY.md` | 各平台详细说明 |
