# workspace-template/ — 用户项目模板

> 这是用户新建小说项目时的起点。clone 后，用户填写这些模板文件，即完成项目初始化。

---

## 目录结构

```
workspace-template/
├── world_template.md           ← 世界设定模板
├── style_guide_template.md     ← 写作风格偏好模板
│
├── characters/                 ← 角色档案模板
│   ├── protagonist_template.md  ← 主角模板
│   ├── antagonist_template.md  ← 反派模板
│   ├── supporting_template.md  ← 配角模板
│   ├── mentor_template.md     ← 导师/引路人模板
│   └── minor_template.md       ← 龙套/次要角色模板
│
├── locations/                  ← 地点档案模板
│   └── template.md
│
├── inventory/                 ← 装备/道具模板
│   └── template.md
│
├── outline/                    ← 大纲
│   ├── index.md               ← 大纲总导航
│   ├── structure_template.md   ← 宏观结构模板
│   └── volumes/               ← 分卷大纲
│       └── volume_template.md ← 单卷模板
│
└── beats/                     ← 伏笔追踪
    └── tracking_template.md  ← 伏笔操作指南
```

---

## 使用方式

### 方式 1：自动初始化（推荐）

在 OpenClaw / Claude Code / Codex 中运行：

```
python scripts/novel_agent.py <你的小说目录> init
```

Agent 会帮你：
1. 创建目录结构
2. 复制模板文件到你的小说目录
3. 引导你填写 `novel-agent.yaml`

### 方式 2：手动

手动复制 `workspace-template/` 到你的小说目录，逐一填写模板文件。

---

## 每个模板文件的作用

| 模板 | 作用 | 生成的索引 |
|------|------|---------|
| `world_template.md` | 世界设定 | `world.md` + `index/world_rules.json` |
| `characters/*.md` | 角色档案 | `characters/` + `index/characters.json` |
| `locations/template.md` | 地点档案 | `locations/` + `index/locations.json` |
| `inventory/template.md` | 装备道具 | `index/world_rules.json` (key_items) |
| `outline/volumes/volume_*.md` | 分卷大纲 | `outline/volumes/` |
| `beats/tracking_template.md` | 伏笔追踪 | `index/beats.jsonl` |

---

## 自定义模板

如果你有特定类型的角色（如"系统觉醒者"、"变异体 NPC"），可以新增模板文件，放在 `characters/` 目录下。
