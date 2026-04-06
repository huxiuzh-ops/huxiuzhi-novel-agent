# 安装到 Codex / Cursor

> Codex / Cursor / Windsurf 等基于 Codex 的 IDE 用户专用指南

---

## 方式一：直接 clone（推荐）

```bash
# 在终端里
git clone https://github.com/novel-agent/novel-agent.git
cd novel-agent
```

然后在 Codex / Cursor 中打开这个文件夹作为项目。

---

## 方式二：给你的写作项目加入 novel-agent

```bash
# 在你的写作项目目录里
git clone https://github.com/novel-agent/novel-agent.git .novel-agent-tmp
cp .novel-agent-tmp/SKILL.md ./
cp .novel-agent-tmp/CLAUDE.md ./
cp -r .novel-agent-tmp/scripts ./
cp -r .novel-agent-tmp/workspace-template ./
rm -rf .novel-agent-tmp
```

---

## 首次配置

1. 在 Codex / Cursor 中打开项目目录
2. 按 `Cmd/Ctrl + K` 打开 Agent 对话
3. 说：「请帮我初始化小说设定」
4. 填写书名、题材、主角、世界观等

---

## Codex 模式提示

Codex 长于代码生成，写小说时需要给它明确的上下文：

```
# 每次新会话前，建议先说：
"请阅读 SKILL.md 和我的世界设定（world.md），
然后帮我写第三章"
```

---

## 使用示例

```
# 写章节
/write chapter 3

# 检查一致性
/run python scripts/consistency_check.py .

# 检查伏笔
/run python scripts/beat_tracker.py . 30

# 新增角色
/add character
```

---

## 不需要 Python？

如果你不用 scripts，跳过 Python 安装也可以。

所有写作工作都可以直接通过对话完成：

```
你：请阅读 world.md 和 characters/protagonist.md，
    然后告诉我主角的核心动机是什么
```

---

## Cursor 特殊说明

Cursor 支持 `.cursor/rules` 目录来加载自定义规则。

novel-agent 的 `SKILL.md` 会自动被 Cursor 识别为主要的工作手册。

如果需要额外的规则，可以在 `.cursor/rules/` 下创建文件。
