# roles/README.md — 角色提示模板

> 本目录存放 5 个角色的具体提示模板。
> 
> 每个角色的模板定义：
> - 该角色的系统提示（role system prompt）
> - 该角色收到的上下文结构
> - 该角色应输出的格式
> - 该角色的交接规则
> 
> 这些模板是 AGENT.md 中角色定义的具体实现。
> 不同平台（OpenClaw / Claude Code / API）都引用这些模板。

---

## 文件清单

| 文件 | 角色 | 用途 |
|------|------|------|
| `supervisor.md` | Supervisor | 任务分发、流程控制、决策升级 |
| `planner.md` | Planner | 大纲规划、章节 mini plan |
| `writer.md` | Writer | 正文写作、草稿输出 |
| `editor.md` | Editor | 审稿、一致性检查、风险提示 |
| `world.md` | World | 设定管理、冲突检测 |

---

## 使用方式

### OpenClaw
在 `SKILL.md` 或 `AGENT.md` 中，通过 `exec` 读取角色模板：
```
读取 roles/supervisor.md → 作为 Supervisor 的 system prompt
```

### Claude Code / Codex
在 `CLAUDE.md` 中指示 Agent：
```
当需要 Planner 时，读取 roles/planner.md 并按其指示工作
```

### API Mode
在组装上下文时，把对应角色的模板作为 system prompt 的一段注入。

---

## 模板结构

每个角色模板都包含：

```
## 角色身份
[该角色是什么]

## 核心职责
[该角色做什么]

## 收到的输入
[从上一个角色/系统传来什么数据]

## 输出格式
[该角色必须按什么格式输出]

## 交接规则
[输出交给谁、下一步怎么做]

## 边界
[什么情况必须升级、什么情况不能做]
```

---

## 平台无关性

这些模板**不包含任何平台特定的工具调用**。
平台特定的执行方式（如怎么写文件、怎么运行脚本）由各平台的适配层（SKILL.md / CLAUDE.md）负责。
