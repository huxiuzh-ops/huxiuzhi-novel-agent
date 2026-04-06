# 通用 API 方式（填个 Key 就用）

> 不需要安装 OpenClaw / Claude Code / Codex，任何支持 API 调用的 AI 都能用

---

## 原理

novel-agent 本质上是一套 **Markdown 文件**（SKILL.md + templates）。

任何能调用 AI API 的工具，都可以：

1. 把 `SKILL.md` 的内容作为 **system prompt** 发送
2. 把你的小说设定（world.md、characters/ 等）作为 **上下文** 发送
3. 然后正常对话即可

---

## 最简单的方式：用 LangChain / LangGraph

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# 读取 SKILL.md 作为系统提示词
with open('SKILL.md', 'r', encoding='utf-8') as f:
    skill_md = f.read()

# 读取你的小说设定
with open('my-novel/world.md', 'r', encoding='utf-8') as f:
    world_md = f.read()

# 初始化模型
llm = ChatOpenAI(model="gpt-4o", api_key="your-api-key")

# 发送
response = llm.invoke([
    {"role": "system", "content": skill_md + "\n\n# 当前小说设定\n\n" + world_md},
    {"role": "user", "content": "请阅读我的世界设定，然后告诉我目前的主要矛盾是什么"}
])
print(response.content)
```

---

## 用 DeerFlow（推荐）

DeerFlow（字节开源的 super agent harness）原生支持飞书、Slack 等 IM 渠道。

1. 安装 DeerFlow
2. 把 `SKILL.md` 内容作为 lead agent 的 system prompt
3. 把 `my-novel/` 目录作为 workspace 挂载

---

## 用 Coze（扣子）

1. 在 Coze 创建一个 Bot
2. 把 `SKILL.md` 内容粘贴到"人设与回复逻辑"
3. 把 `my-novel/` 目录的文件作为知识库上传
4. 选择飞书/微信/Telegram 作为渠道

---

## 用任意 ChatGPT / Claude 网页版

1. 打开 ChatGPT 或 Claude 网页
2. 把 `SKILL.md` 的**全部内容**复制到 System Prompt（或 Custom Instructions）
3. 把 `world.md` 和 `characters/` 的内容也粘贴进去
4. 开始对话

---

## .env 配置模板

创建一个 `.env` 文件来存储 API Key：

```bash
# OpenAI
OPENAI_API_KEY=sk-xxxx

# Anthropic（Claude）
ANTHROPIC_API_KEY=sk-ant-xxxx

# 火山引擎（豆包）
ARK_API_KEY=xxxx

# DeepSeek
DEEPSEEK_API_KEY=xxxx
```

> **安全提醒**：`.env` 文件不要提交到 GitHub！
> 确认 `.gitignore` 里包含 `.env`

---

## .gitignore 建议

在仓库根目录添加 `.gitignore`：

```gitignore
.env
.env.local
my-novel/           # 你的私人小说项目
chapters/           # 不要把正文提交到公共仓库
*.pyc
__pycache__/
.DS_Store
```

> 注意：novel-agent 仓库本身不包含你的私人小说内容。
> `workspace-template/` 只是模板，不会暴露你的设定。

---

## 快速验证

安装完成后，对 AI 说：

> 「请阅读 SKILL.md，然后告诉我你的职责是什么，以及当前支持哪些功能」

如果 AI 能正确回答，说明配置成功。
