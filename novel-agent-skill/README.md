# novel-agent-skill/ — OpenClaw Skill 执行协议

> 本目录存放 OpenClaw 平台下 novel-agent 的 skill 定义。
> 它不是平台入口（那是 `SKILL.md`），而是**工作流的具体执行协议**。

---

## SKILL.md 内容

`SKILL.md` 定义了：
- 在 OpenClaw 环境下如何执行各角色
- 如何调用 `scripts/` 中的工具
- 工作流的实际步骤

---

## 与 SKILL.md 的关系

```
SKILL.md（OpenClaw 平台入口）
    ↓ 引用
novel-agent-skill/SKILL.md（OpenClaw 执行协议）
    ↓ 引用
AGENT.md（平台无关核心定义）
```

`novel-agent-skill/SKILL.md` 包含 OpenClaw 平台特定的**工具调用方式**（如怎么用 exec 写文件、怎么触发脚本），而 `AGENT.md` 保持完全平台无关。

---

## 为什么要分开

保持 `AGENT.md` 纯净——它只描述业务逻辑，不包含任何平台特定代码。

这样同一个 `AGENT.md` 可以被：
- OpenClaw 通过 `SKILL.md` + `novel-agent-skill/SKILL.md` 调用
- Claude Code 通过 `CLAUDE.md` 调用
- API 模式直接作为 system prompt 使用
