# novel-agent

> 让 AI 成为你写长篇小说的搭档，而不是代笔

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/novel-agent/novel-agent)](https://img.shields.io/github/stars/novel-agent/novel-agent)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-OpenClaw%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20Generic%20API-green)](https://github.com/novel-agent/novel-agent)

**中文** | [English](./docs/README_EN.md)

---

## 它是什么

一个通用的 AI 辅助长篇小说写作框架。

不是"AI 替你写书"那种没有灵魂的工具，而是像一个**靠谱的编辑搭档**：帮你规划大纲、追踪伏笔、检查前后矛盾、整理设定库。你做创意决策，Agent 做执行和校验。

适用于网文、出版小说、同人文，1 万字到 100 万字+都适用。

---

## 核心能力

| 能力 | 说明 |
|------|------|
| **意图识别** | 用自然语言告诉 Agent 要做什么，不用记固定命令 |
| **多 Agent 协作** | Supervisor（主编）/ Writer（写作）/ Planner（策划）/ Editor（审稿）各司其职 |
| **一致性检查** | 自动检测角色年龄、武器参数、时间线等前后矛盾 |
| **伏笔追踪** | 登记伏笔，自动提醒逾期未回收，避免"忘了埋了什么" |
| **上下文管理** | 长篇写作不怕上下文窗口爆炸，Agent 自动压缩和管理记忆 |
| **多入口支持** | OpenClaw / Claude Code / Codex / Web UI，同一套文件，多种使用方式 |
| **叙事框架** | 支持三段式 / 起承转合 / 事件驱动，开箱即用 |

---

## 快速开始

### 第一步：Clone 仓库

```bash
git clone https://github.com/novel-agent/novel-agent.git
cd novel-agent
```

### 第二步：运行 Setup Wizard

```bash
# 用任意支持 OpenClaw Skill 的 Agent 打开这个 workspace
# 然后对 Agent 说：

# "你好，我的小说Agent，我的新书是[你的书名]，请帮我初始化"

# 或者手动复制 workspace-template 下的所有文件到你自己的小说目录
```

### 第三步：告诉 Agent 你的小说设定

参考 `SETUP_WIZARD.md` 填写：
- 书名、题材、简介
- 选择叙事框架（三段式 / 起承转合 / 事件驱动）
- 主角和主要角色设定
- 世界底层规则
- 主要势力

### 第四步：开始写作

```
你：「写第三章」
Agent：读取你的设定 + 已有章节，写出符合世界观的内容，自动审稿，通知你完成
```

---

## 文件结构

```
novel-agent/
├── README.md                    ← 你在这里
├── LICENSE                      ← MIT，开源
├── SKILL.md                     ← Agent 的工作手册（核心）
├── SETUP_WIZARD.md              ← 首次使用引导
├── scripts/                     ← 通用验证脚本
│   ├── consistency_check.py     ← 一致性检查
│   ├── beat_tracker.py          ← 伏笔追踪
│   ├── context_compressor.py    ← 上下文压缩
│   └── outline_generator.py     ← 大纲生成
├── workspace-template/          ← 设定模板（用户填自己的）
│   ├── world_template.md
│   ├── characters/
│   ├── outline/
│   ├── beats/
│   └── style_guide_template.md
├── frameworks/                  ← 叙事框架
│   ├── 三段式_engine.md
│   ├── 起承转合.md
│   └── 事件驱动.md
└── docs/
    ├── INSTALL.md               ← 安装指南
    ├── FRAMEWORKS.md            ← 叙事框架说明
    └── EXAMPLES.md              ← 完整示例
```

---

## 工作流程

```
你：自然语言指令
    ↓
意图识别层：解析你想做什么
    ↓
Supervisor Agent：判断分发给谁
    ↓
Planner Agent ←→ Writer Agent ←→ Editor Agent
    ↓
知识库持久化（world/characters/outline/beats）
    ↓
你：收到完成通知 / 被问到关键决策
```

---

## Agent 架构

详见 `SKILL.md`，核心是 Harness 工程思想：

```
Agent = LLM（推理能力）+ Harness（管控系统）

Harness 包含：
- 隔离执行环境（Sandbox）
- 上下文与记忆管理
- 约束与规则引擎（硬约束，用代码而非提示词）
- 验证与反馈循环
- 可观测性
- Tools & Skills（可插拔技能）
```

---

## 自主程度

系统支持四级自主程度，由你在 Setup 时选择：

| 级别 | 说明 |
|------|------|
| L1 全自动 | Agent 全权决定，写完通知你 |
| L2 半自动 | 日常写作 Agent 定，关键节点（人物死亡/新增势力）需你确认 |
| L3 低自动 | 核心方向你定，Agent 执行细节 |
| L4 纯辅助 | 你说写什么，Agent 就写什么 |

---

## 叙事框架

### 三段式引擎
开局 → 发展 → 高潮。适合节奏型题材（都市异能、末世、打怪升级）。

### 起承转合
起（铺陈）、承（推进）、转（转折）、合（收束）。适合情感细腻的故事、群像戏。

### 事件驱动
以关键事件为节点推进，不追求细水长流。适合快节奏、高潮迭起型。

详见 `frameworks/` 目录。

---

## Web UI（开发中）

除了命令行，另有 React Web UI 提供可视化操作界面。

详见 `web/` 目录（即将推出）。

---

## 兼容性

| 平台 | 状态 |
|------|------|
| OpenClaw | ✅ 支持 |
| Claude Code | ✅ 支持 |
| Codex / Cursor | ✅ 支持 |
| Web UI | 🔨 开发中 |

---

## 贡献

欢迎提交 Issue 和 PR。如果你有好的叙事框架思路、新的验证脚本、或者工作流优化，欢迎交流。

---

## License

MIT — 可以自由使用、修改、商业化。

---

*让 AI 成为你写作路上的靠谱搭档，而不是替代你思考的代笔。*
