# 兼容性说明

> 小说 Agent 在不同 Agent 平台上的使用方式

---

## 概览

小说 Agent 设计的核心原则是**平台无关**——它依赖的是：

1. 文件系统（Markdown 文件）
2. 标准工具（git、python）
3. 标准的 Agent 指令格式（SKILL.md）

因此理论上任何支持加载文件和执行命令的 Agent 环境都可以使用。

---

## OpenClaw ✅ 原生支持

**使用方式**：把 `小说Agent` 文件夹作为 OpenClaw 的 workspace 打开。

**优势**：
- 内置飞书集成，章节完成后自动推送通知
- 内置 Skill 加载机制，`SKILL.md` 自动识别
- 支持 cron 定时任务，可以设置自动写作

**配置示例**：

```yaml
# openclaw 配置中可添加
novel-agent:
  workspace: /path/to/novel-agent
  feishu:
    enabled: true
    app_id: $FEISHU_APP_ID
    app_secret: $FEISHU_APP_SECRET
```

---

## Claude Code ✅ 支持

**使用方式**：在 `novel-agent` 目录下启动 Claude Code。

```bash
cd novel-agent
claude
```

**优势**：
- Claude Code 自动读取当前目录的 SKILL.md
- Code Agent 模式可以调用 Python scripts
- 支持文件编辑、git 操作

**注意**：
- Claude Code 的 `Edit` 和 `Write` 工具直接读写 markdown 文件
- 可以用 `Bash` 工具运行 scripts

**示例指令**：
```
/project: 写第三章，接续上一章结尾的钩子
/project: 运行 consistency_check.py 检查我的小说
/project: 帮我规划第二卷的大纲
```

---

## Codex / Cursor ✅ 支持

**使用方式**：在 `novel-agent` 目录下打开 Cursor/Codex。

**优势**：
- 代码编辑器直接编辑 markdown
- 内置终端直接运行 scripts
- 支持多文件同时编辑

**注意**：
- Codex 模式下 Agent 更偏向"写代码"，需要明确告知"写小说"任务
- 建议使用 CLAUDE.md 或 .claude 文件增强上下文

---

## 其他 Agent 平台

### LangChain / LangGraph 应用

```python
# 基于 DeerFlow 或 LangGraph 构建的应用
# 只需要让 Agent 读取 SKILL.md 作为 system prompt
from langchain import ChatOpenAI

skill_md = open("SKILL.md").read()
llm = ChatOpenAI(model="gpt-4")
response = llm.invoke([
    {"role": "system", "content": skill_md},
    {"role": "user", "content": "写第三章"}
])
```

### Coze / 扣子

1. 创建一个 Bot
2. 把 `SKILL.md` 的内容作为 Bot 的"人设与回复逻辑"
3. 配置文件系统作为知识库
4. 接入飞书/微信/Telegram 作为渠道

---

## 平台差异对比

| 能力 | OpenClaw | Claude Code | Codex/Cursor |
|------|---------|------------|-------------|
| 自动读取 SKILL.md | ✅ | ✅ | ✅ |
| 飞书集成 | ✅ 原生 | ❌ 需配置 | ❌ 需配置 |
| 定时任务 | ✅ cron | ❌ | ❌ |
| scripts 执行 | ✅ | ✅ | ✅ |
| Web UI | 🔨 开发中 | ❌ | ❌ |
| 多 Agent 协作 | ✅ Supervisor 模式 | 有限 | 有限 |

---

## 共享同一套文件的推荐做法

如果你在多个平台使用同一个小说项目：

```
my-novel/
├── .git/              ← git 仓库（GitHub 同步）
├── world.md          ← 世界观（各平台共享）
├── characters/       ← 角色（各平台共享）
├── outline/          ← 大纲（各平台共享）
├── beats/            ← 伏笔（各平台共享）
├── chapters/         ← 正文（各平台共享）
└── style_guide.md    ← 风格偏好（各平台共享）
```

只要各平台指向同一个文件夹，就能共享所有数据。

---

## 跨平台协作建议

- **用 GitHub 作为数据中枢**：每个平台在 push/pull 后同步
- **不要在多个平台同时写作同一章**：容易产生冲突
- **用 beats/ 追踪任务分配**：哪个 Agent 负责哪部分一目了然
