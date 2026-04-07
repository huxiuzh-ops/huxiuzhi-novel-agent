# novel-agent

> 让 AI 成为你写长篇小说的靠谱搭档，而不是替代你思考的代笔。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-OpenClaw%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20Any%20API-blue)](https://github.com/novel-agent/novel-agent)

---

## 一句话介绍

一个通用的 AI 辅助长篇小说写作框架。采用**角色驱动工作流** + **结构化索引**，让 AI 能稳定地帮你规划、写作、审稿、追踪伏笔。你做创意决策，Agent 按流程执行。

---

## 核心能力

| 能力 | 说明 |
|------|------|
| **角色工作流** | Supervisor → Planner → Writer → Editor，清晰分工 |
| **结构化索引** | 角色/章节/伏笔/地点/时间线，全部机器可读 |
| **一致性检查** | 自动检测角色/武器/时间线前后矛盾 |
| **伏笔追踪** | 登记→逾期警告→回收验证，看板式管理 |
| **人类掌舵** | 关键决策点必须经过你确认，不是 AI 自说自话 |
| **多平台支持** | OpenClaw / Claude Code / Codex / 任何 LLM API |
| **开箱即用** | 克隆后回答几个问题即可开始，不需要懂 Agent 架构 |

---

## 快速开始

```bash
# Clone
git clone https://github.com/huxiuzh-ops/huxiuzhi-novel-agent.git
cd huxiuzhi-novel-agent

# 首次使用：回答几个问题即可
# 对 Agent 说："你好，帮我初始化新书"

# 之后直接用自然语言指挥
"写第一章"
"审一下第3章"
"帮我规划第二卷"
"新增一个配角"
"检查前10章有没有矛盾"
```

---

## 架构设计

```
                    平台入口（薄适配层）
                    SKILL.md / CLAUDE.md
                           │
                           ▼
                  ┌─────────────────┐
                  │   AGENT.md      │  ← 核心：角色/工作流/索引 schema
                  │  （平台无关）     │
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        roles/         config/        index/
     角色提示模板     框架配置        结构化索引
   supervisor.md     project.yaml    characters.json
   planner.md       writing.yaml    chapters.json
   writer.md        validation.yaml beats.jsonl
   editor.md        platforms.yaml  locations.json
   world.md                          timeline.jsonl
                                    decisions.jsonl
```

**设计原则**：
- `AGENT.md` 是核心，与任何平台无关
- `SKILL.md` / `CLAUDE.md` 只是薄薄一层适配
- `config/` 是框架级参数，与具体小说完全解耦
- `index/` 是 AI 优先读取的摘要层，不是正文副本

---

## 文件结构

```
novel-agent/
├── AGENT.md                    ← 核心：角色 schema / 工作流 / 状态机 / 索引定义
├── SKILL.md                    ← OpenClaw 入口
├── CLAUDE.md                   ← Claude Code / Codex 入口
├── SETUP_WIZARD.md            ← 首次使用引导
├── README.md                   ← 本文件
│
├── config/                    ← 框架级配置（项目无关）
│   ├── project.yaml            ← 书名/题材/叙事框架/自主程度
│   ├── writing.yaml            ← 字数/对话上限/章节钩子/描写比例
│   ├── validation.yaml         ← 一致性/伏笔/时间线/报告
│   └── platforms.yaml          ← 多平台入口配置
│
├── roles/                      ← 角色提示模板（平台无关）
│   ├── supervisor.md            ← 任务分发 / 流程控制 / 决策升级
│   ├── planner.md              ← 大纲规划 / 章节 mini plan
│   ├── writer.md               ← 正文写作 / 自审清单
│   ├── editor.md               ← 审稿 / 一致性检查 / 风险提示
│   └── world.md                ← 设定管理 / 冲突检测
│
├── index/                      ← 结构化索引 schema
│   ├── characters_schema.md     ← 角色索引
│   ├── chapters_schema.md       ← 章节索引
│   ├── beats_schema.md         ← 伏笔索引（JSONL）
│   ├── locations_schema.md      ← 地点索引
│   ├── timeline_schema.md       ← 时间线（含知识/状态变化）
│   ├── decisions_schema.md      ← 决策点索引
│   └── world_rules_schema.md    ← 世界规则索引
│
├── scripts/                    ← 工具脚本
│   ├── build_index.py           ← 全量索引构建（扫描小说项目）
│   ├── incremental_index_update.py  ← 增量索引更新
│   ├── workflow_state.py        ← 工作流状态管理
│   ├── consistency_check.py      ← 一致性检查
│   ├── beat_tracker.py          ← 伏笔追踪
│   ├── context_compressor.py   ← 上下文压缩
│   └── outline_generator.py     ← 大纲生成
│
├── novel-agent-skill/          ← OpenClaw skill 执行协议
│   └── SKILL.md
│
├── server.js                   ← Web UI 服务器
├── workspace-template/          ← 用户项目模板
├── frameworks/                 ← 叙事框架文档
├── memory/ontology/             ← 知识图谱
├── .learnings/                 ← 自我进化记忆
└── docs/                       ← 各平台安装指南
```

---

## 工作流

### 写章节

```
Supervisor → Planner → Writer → Editor → Supervisor（分流）
                                          ↓
                                    通过 → 更新索引 → 交付
                                    轻微问题 → 修订 → 再审
                                    重大问题 → 人类决策点
```

### 角色职责

| 角色 | 做什么 | 不做什么 |
|------|--------|---------|
| **Supervisor** | 任务分发、流程控制、决策升级 | 不写正文、不做细节审稿 |
| **Planner** | 大纲规划、章节 mini plan | 不写正文、不做审稿 |
| **Writer** | 写草稿、承接计划 | 不裁定设定冲突 |
| **Editor** | 审稿、一致性检查、风险提示 | 不写正文、不拍板重大剧情 |
| **World** | 设定管理、冲突检测 | 不写正文、不做日常审稿 |

---

## 支持的平台

| 平台 | 入口 | 状态 |
|------|------|------|
| OpenClaw | `SKILL.md` | ✅ |
| Claude Code | `CLAUDE.md` | ✅ |
| Codex / Cursor | `CLAUDE.md` | ✅ |
| 任何 LLM API | `AGENT.md` 作为 system prompt | ✅ |

---

## Web UI

```bash
node server.js
# 访问 http://localhost:8765
```

功能：章节浏览 / 伏笔看板 / 角色卡片 / 一致性检查 / 知识图谱统计

---

## 许可证

MIT — 自由使用、修改、商业化。

---

*让 AI 成为你写作路上的靠谱搭档，而不是替代你思考的代笔。*
