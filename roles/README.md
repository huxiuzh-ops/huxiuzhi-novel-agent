# roles/ — 角色提示模板

> 这里存放 5 个角色各自的提示模板，是 `AGENT.md` 中角色定义的具体实现。
> 平台无关——OpenClaw / Claude Code / Codex / API 都使用同一套模板。

---

## 文件说明

| 文件 | 角色 | 职责 |
|------|------|------|
| `supervisor.md` | Supervisor（主编） | 任务分发、流程控制、决策升级 |
| `planner.md` | Planner（策划） | 大纲规划、章节 mini plan |
| `writer.md` | Writer（写作） | 正文写作、草稿输出 |
| `editor.md` | Editor（审稿） | 审稿、一致性检查、风险提示 |
| `world.md` | World（世界观） | 设定管理、冲突检测 |

---

## 使用方式

当 Agent 需要扮演某个角色时，读取对应模板作为提示：

```
需要 Planner 时 → 读取 roles/planner.md → 按其指示输出结构化章节计划
需要 Writer 时 → 读取 roles/writer.md → 按其指示写正文
需要 Editor 时 → 读取 roles/editor.md → 按其指示审稿
```

---

## 模板结构

每个模板包含：

```
## 角色身份
## 核心职责
## 收到输入（JSON schema）
## 输出格式（JSON schema）
## 必须遵守的规则
## 边界（什么能做 / 什么不能做）
```

---

## 自定义

如果你的小说项目需要定制化角色行为（如 Writer 更注重某个风格），可以在用户小说的 `novel-agent.yaml` 中引用自定义模板路径来覆盖默认模板。
