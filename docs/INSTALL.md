# 安装指南

> 如何在任何 AI 平台上安装和使用 novel-agent

---

## 快速选择

| 平台 | 安装难度 | 安装文档 |
|------|---------|---------|
| **OpenClaw** | ⭐ 简单 | [INSTALL_OPENCLAW.md](./INSTALL_OPENCLAW.md) |
| **Claude Code** | ⭐ 简单 | [INSTALL_CLAUDE_CODE.md](./INSTALL_CLAUDE_CODE.md) |
| **Codex / Cursor** | ⭐ 简单 | [INSTALL_CODEX.md](./INSTALL_CODEX.md) |
| **通用 API** | ⭐⭐ 中等 | [INSTALL_GENERIC.md](./INSTALL_GENERIC.md) |
| **DeerFlow** | ⭐⭐ 中等 | 参考 [COMPATIBILITY.md](./COMPATIBILITY.md) |
| **Coze / 扣子** | ⭐⭐ 中等 | 参考 [COMPATIBILITY.md](./COMPATIBILITY.md) |

---

## 推荐：按平台选择

- 用 OpenClaw → 看 [INSTALL_OPENCLAW.md](./INSTALL_OPENCLAW.md)
- 用 Claude Code → 看 [INSTALL_CLAUDE_CODE.md](./INSTALL_CLAUDE_CODE.md)
- 用 Codex / Cursor → 看 [INSTALL_CODEX.md](./INSTALL_CODEX.md)
- 只想填 API Key → 看 [INSTALL_GENERIC.md](./INSTALL_GENERIC.md)

---

## 通用安装（所有平台）

```bash
git clone https://github.com/novel-agent/novel-agent.git
cd novel-agent
```

然后根据你的平台选择对应的安装文档。

---

## 前置要求

| 组件 | 是否必需 | 说明 |
|------|---------|------|
| Git | ✅ 必须 | 用于 clone 仓库 |
| Python 3.8+ | ❌ 可选 | 仅在使用 scripts 时需要 |
| AI 平台账号 | ✅ 必须 | OpenClaw / Claude Code / API Key 等 |

---

## 首次配置

无论用哪个平台，首次使用都要完成 Setup Wizard：

1. 对 Agent 说：「你好，帮我初始化小说设定」
2. 回答书名、题材、主角、世界规则等问题
3. Agent 自动生成工作目录结构

详细流程：[SETUP_WIZARD.md](../SETUP_WIZARD.md)

---

## 常见问题

**Q: 需要 Python 吗？**
A: 只有 scripts 需要 Python。如果只用 Agent 工作，不需要安装 Python。

**Q: 可以不用 workspace-template 吗？**
A: 可以。你可以直接在自己已有的文件夹里创建相应的结构，只要 Agent 能找到 SKILL.md 即可。

**Q: 可以同时写多本书吗？**
A: 可以，每个项目一个独立的文件夹，Agent 支持切换项目。
