# SETUP_WIZARD.md — 首次使用引导（v2）

> 本向导将帮你完成 novel-agent 的初始化。
> 完成后，你的项目会包含：
> - 配置文件（`novel-agent.yaml`）
> - 世界观、角色、大纲
> - 结构化索引（`index/`）
> - 可选的 Web UI 数据

---

## 开始之前

你需要：
1. 一个支持 Agent 的环境（OpenClaw / Claude Code / Codex 等）
2. 将 `novel-agent/` 框架目录 clone 到本地
3. 创建一个空白目录作为你的小说项目文件夹

```
mkdir my-novel
cd my-novel
```

然后对 Agent 说：
```
你好，我的小说 Agent，帮我初始化新书
```

---

## 第一步：填写项目配置（写入 novel-agent.yaml）

回答以下问题，Agent 会帮你生成 `novel-agent.yaml`：

### 基础信息

```
书名：《              》
语言：□ 中文（zh-CN）  □ 英文（en-US）
题材：□ 都市  □ 废土  □ 仙侠  □ 西幻  □ 末世  □ 悬疑  □ 其他：
一句话简介：
```

### 选择叙事框架

| 框架 | 适合 | 特点 |
|------|------|------|
| 三段式 | 末世、打怪升级、都市异能 | 开局→发展→高潮，节奏清晰 |
| 起承转合 | 情感细腻、群像戏 | 起→承→转→合，节奏更细腻 |
| 事件驱动 | 快节奏、爽文 | 以关键事件为节点，不拖沓 |

```
选择：□ 三段式引擎  □ 起承转合  □ 事件驱动
```

### 选择自主程度

你想让 Agent 多自主？

| 级别 | Agent 决定 | 需你确认 |
|------|-----------|---------|
| L1 全自动 | 所有日常写作 | 主角死亡/主线变更 |
| L2 半自动 | 日常写作 | 关键剧情/新势力 |
| L3 低自动 | 执行细节 | 章节方向/重要转折 |
| L4 纯辅助 | 无 | 几乎所有决策 |

```
选择：□ L1  □ L2  □ L3  □ L4
```

---

## 第二步：填写世界观（写入 world.md）

参考 `workspace-template/world_template.md`：

```
## 地理/地点
这个世界分几个区域？每个区域的特点？

## 力量体系（如有）
这个世界有什么特殊能力？规则是什么？

## 主要势力
有哪些势力？它们之间是什么关系（敌对/盟友/中立）？

## 核心矛盾
故事的核心冲突是什么？
```

---

## 第三步：填写角色（写入 characters/*.md）

参考 `workspace-template/characters/` 下的模板，至少填写：

```
主角：
- 姓名/代号：
- 年龄、外貌特征：
- 性格：
- 核心目标/动机：
- 与核心矛盾的关系：

主要对手（如有）：
- 姓名/代号：
- 与主角的关系：
- 核心动机：

主要配角（1-2人）：
- 姓名：
- 在故事中的作用：
```

---

## 第四步：填写写作规范（写入 style_guide.md）

```
叙事视角：□ 第一人称  □ 第三人称全知  □ 第三人称限制
文风：□ 简洁利落  □ 华丽细腻  □ 中性
每章目标字数：    字（建议 3000+）
对话密度：□ 轻  □ 中  □ 重
是否需要章节钩子：□ 是（必须）  □ 否
其他偏好：
```

---

## 第五步：生成初始索引

初始化完成后，告诉 Agent：

```
帮我生成初始索引
```

Agent 会：
1. 运行 `python scripts/build_index.py <workspace>`
2. 生成 `index/characters.json`
3. 生成 `index/chapters.json`（空或根据已有章节）
4. 生成 `index/beats.jsonl`（空）
5. 生成 `index/locations.json`
6. 生成 `index/timeline.jsonl`（空）
7. 生成 `index/world_rules.json`（占位，需 AI 辅助填充）

---

## 第六步：生成初始大纲（可选）

如果你希望 Agent 生成一个分卷大纲，告诉 Agent：

```
帮我生成一个大纲框架
```

Agent 会根据你选择的三种框架，生成分卷骨架，写入 `outline/volumes/volume_01.md`。

---

## 第七步：开始写作

配置完成！现在你可以：

```
「写第一章」
「审一下第3章」
「帮我规划第二卷」
「新增一个角色」
「检查一下前10章有没有矛盾」
「这个角色出现在哪些章节」
```

---

## 文件结构（初始化后）

你的小说项目应该是这样：

```
my-novel/
├── novel-agent.yaml      ← 项目配置（你的填写结果）
├── world.md              ← 世界设定
├── style_guide.md        ← 写作规范
├── characters/           ← 角色档案
│   ├── protagonist.md
│   └── supporting.md
├── outline/             ← 大纲
│   ├── index.md
│   └── volumes/
├── beats/               ← 伏笔追踪
│   └── TRACKING.md
├── chapters/            ← 章节正文（你来写或让 Agent 写）
├── inventory/           ← 装备道具（可选）
├── index/               ← 结构化索引（自动维护）
│   ├── characters.json
│   ├── chapters.json
│   ├── beats.jsonl
│   ├── locations.json
│   ├── timeline.jsonl
│   └── decisions.jsonl
└── .learnings/          ← 自我进化
    ├── LEARNINGS.md
    ├── ERRORS.md
    └── FEATURE_REQUESTS.md
```

---

## 后续调整

**改自主程度**：
```
「我想把自主程度从 L2 改成 L1」
```
Agent 会更新 `novel-agent.yaml` 中的 `default_autonomy`。

**改叙事框架**：
```
「我想从三段式换成起承转合」
```

**重建索引**：
```
「重建索引」
```
Agent 会运行 `python scripts/build_index.py <workspace>` 重新扫描。

**查看当前状态**：
```
「现在写到哪了」
「有哪些待回收的伏笔」
```
Agent 会读取 `index/` 中的结构化索引回答。

---

## 常见问题

**Q: 世界观还没想清楚，能先开始写吗？**
A: 能。先填一个基础版，Agent 会在写作过程中帮你发现漏洞并提问。

**Q: 索引是什么，不懂有关系吗？**
A: 没关系。索引是给 Agent 用的，让它更快、更稳定。你只需要知道：Agent 会自动维护它。

**Q: 之后想换平台怎么办？**
A: novel-agent 是平台无关的。同一套 `novel-agent.yaml` + `world.md` + `characters/` 可以在 OpenClaw / Claude Code / Codex / API 模式下通用。

**Q: 能只用一部分功能吗？**
A: 可以。你完全可以只让 Agent 帮你写章节，而不使用索引/工作流/自我进化功能。
