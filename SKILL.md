# SKILL.md — novel-agent · OpenClaw 入口

> **本文件是 OpenClaw 平台的薄适配层**，它加载 `AGENT.md` 作为核心定义。
> 
> 所有通用的角色、任务、工作流定义，请查阅 `AGENT.md`。
> 本文件只包含 OpenClaw 平台特定的约定。

---

## 一、加载顺序

读取本文件后，Agent 应按以下顺序加载：

1. `AGENT.md` — 核心业务定义（必读）
2. `config/project.yaml` — 项目基础配置
3. `config/writing.yaml` — 写作规则
4. `config/validation.yaml` — 验证规则
5. `config/platforms.yaml` — 平台配置

---

## 二、意图识别（复用 AGENT.md 定义）

用户输入 → 分类 → 分发，详见 `AGENT.md 第二节`。

| 意图类型 | 分发目标 |
|---------|---------|
| 写章节 | Writer |
| 规划/大纲 | Planner |
| 审稿/检查 | Editor |
| 新增/修改设定 | World |
| 查询 | KB 查询 |
| 决策点 | Supervisor |

---

## 三、OpenClaw 特有约定

### 3.1 工具调用

| 场景 | 方式 |
|------|------|
| 写章节 | 调用 `exec` 写入 `chapters/chXXX.md` |
| 更新伏笔 | 追加到 `beats/TRACKING.md` 或 `index/beats.jsonl` |
| 运行检查脚本 | `exec` → `python scripts/consistency_check.py <workspace>` |
| 知识图谱写入 | 追加到 `memory/ontology/graph.jsonl` |
| 索引更新 | 写入/更新 `index/*.json` 或 `index/*.jsonl` |

### 3.2 定时任务

可通过 OpenClaw cron 设置自动任务：
- 每日伏笔状态检查
- 章节字数统计
- 一致性定期扫描

### 3.3 消息推送

章节完成后，可通过 OpenClaw 的飞书集成推送通知。

---

## 四、入口命令参考

以下为常用指令示例（实际以用户自然语言为主）：

| 用户说 | 系统做 |
|--------|--------|
| "写第8章" | 执行 write_chapter workflow |
| "审一下第5章" | 执行 review_chapter workflow |
| "帮我规划第二卷" | 执行 plan_volume workflow |
| "新增一个角色" | 调用 World → add_character |
| "这个角色在哪几章出现过" | 执行 query → 读 index/characters.json |
| "检查一下一致性" | 运行 consistency_check.py |
| "改成全自动" | 更新 config/project.yaml → default_autonomy: L1 |

---

## 五、工作空间结构（OpenClaw 下）

```
workspace/                    ← 用户小说项目目录
├── AGENT.md                 ← 本文件（不属用户项目）
├── world.md                 ← 世界设定
├── characters/              ← 角色档案
├── outline/                 ← 大纲
├── beats/                   ← 伏笔追踪
├── chapters/               ← 章节正文
├── inventory/              ← 装备道具
├── style_guide.md          ← 写作风格
├── memory/ontology/         ← 知识图谱
│   ├── schema.yaml
│   └── graph.jsonl
├── index/                  ← 结构化索引（第一版可选）
│   ├── characters.json
│   ├── chapters.json
│   ├── beats.jsonl
│   ├── locations.json
│   └── timeline.jsonl
└── .learnings/            ← 自我进化
    ├── LEARNINGS.md
    ├── ERRORS.md
    └── FEATURE_REQUESTS.md
```

---

## 六、快速开始（OpenClaw 用户）

在 OpenClaw workspace 中打开本目录，对 Agent 说：

```
你好，我的小说 Agent，帮我初始化新书
```

或直接告诉 Agent 你要做什么：
- "帮我写第一章"
- "规划一下世界观"
- "审一下第3章"

Agent 会自动读取 `AGENT.md` 和 `config/` 中的定义，按工作流执行。

---

## 七、相关文件

| 文件 | 作用 |
|------|------|
| `AGENT.md` | **核心定义**（角色/任务/工作流/索引 schema） |
| `config/*.yaml` | 框架配置（项目无关的通用参数） |
| `SKILL.md` | 本文件 — OpenClaw 平台入口 |
| `CLAUDE.md` | Claude Code / Codex 平台入口 |
| `SETUP_WIZARD.md` | 首次使用引导 |
| `README.md` | 项目介绍 |
| `server.js` | Web UI 服务器 |
| `scripts/*.py` | 验证脚本 |
