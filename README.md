# novel-agent

> 让 AI 成为你写长篇小说的搭档，而不是代笔

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green?logo=node.js)](https://nodejs.org/)
[![Platform](https://img.shields.io/badge/Platform-OpenClaw%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20Any%20API-blue)](https://github.com/novel-agent/novel-agent)

---

## 一句话介绍

一个通用的 AI 辅助长篇小说写作框架。帮你**规划大纲、追踪伏笔、检查一致性、整理设定库**，你做创意决策，Agent 做执行和校验。

---

## 核心能力

| 能力 | 说明 |
|------|------|
| **意图识别** | 用自然语言告诉 Agent 要做什么，不用记命令 |
| **多 Agent 协作** | Supervisor / Writer / Planner / Editor / World 各司其职 |
| **一致性检查** | 自动检测角色/武器/时间线前后矛盾 |
| **伏笔追踪** | 登记→逾期警告→回收验证 |
| **知识图谱** | 自动维护 Scene/Character/Faction/PlotBeat 实体 |
| **自我进化** | 用户每次纠正都记入 .learnings/，避免重复犯错 |
| **上下文压缩** | 长篇写作防止窗口溢出 |
| **多平台支持** | OpenClaw / Claude Code / Codex / 任何 LLM API |
| **叙事框架** | 三段式 / 起承转合 / 事件驱动 |
| **Web UI** | 浏览器打开，图形化浏览章节/角色/伏笔 |

---

## 快速开始

```bash
# Clone
git clone https://github.com/novel-agent/novel-agent.git
cd novel-agent

# 启动 Web UI（浏览器打开 http://localhost:8765）
node server.js

# 或者用 Agent（以 Claude Code 为例）
claude
```

首次使用，运行 Setup Wizard 或手动复制 `workspace-template/` 到你的小说目录。

---

## 文件结构

```
novel-agent/
├── SKILL.md                    ← Agent 工作手册（核心）
├── CLAUDE.md                   ← Claude Code 入口
├── SETUP_WIZARD.md            ← 首次使用引导
├── server.js                   ← Web UI 服务器（Node.js）
├── scripts/                    ← Python 验证脚本
│   ├── consistency_check.py    ← 一致性检查
│   ├── beat_tracker.py         ← 伏笔追踪
│   ├── context_compressor.py  ← 上下文压缩
│   └── outline_generator.py    ← 大纲生成
├── workspace-template/          ← 设定模板
│   ├── world_template.md
│   ├── characters/
│   ├── outline/
│   ├── beats/
│   └── style_guide_template.md
├── frameworks/                 ← 叙事框架文档
│   ├── 三段式_engine.md
│   ├── 起承转合.md
│   └── 事件驱动.md
├── memory/ontology/            ← 知识图谱
│   ├── schema.yaml
│   └── graph.jsonl
├── .learnings/                ← 自我进化记忆
│   ├── LEARNINGS.md
│   ├── ERRORS.md
│   └── FEATURE_REQUESTS.md
└── docs/                      ← 文档
    ├── INSTALL.md
    ├── INSTALL_OPENCLAW.md
    ├── INSTALL_CLAUDE_CODE.md
    ├── INSTALL_CODEX.md
    ├── INSTALL_GENERIC.md
    ├── COMPATIBILITY.md
    └── EXAMPLES.md
```

---

## Web UI

启动后访问 **http://localhost:8765**

```
node server.js
```

功能：章节浏览 / 伏笔看板 / 角色卡片 / 一致性检查 / 知识图谱统计

---

## 支持的平台

| 平台 | 入口文件 | 状态 |
|------|---------|------|
| OpenClaw | `SKILL.md` | ✅ |
| Claude Code | `CLAUDE.md` | ✅ |
| Codex / Cursor | `CLAUDE.md` | ✅ |
| 任何 LLM API | `SKILL.md` 作为 system prompt | ✅ |

详见 `docs/` 目录下的各平台安装指南。

---

## 许可证

MIT — 自由使用、修改、商业化。

---

*让 AI 成为你写作路上的靠谱搭档，而不是替代你思考的代笔。*
