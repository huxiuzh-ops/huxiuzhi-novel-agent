# 决策索引 / Decisions Index

> 文件路径：`index/decisions.jsonl`
> 格式：JSONL（每行一条决策）
> 用途：记录需要人类拍板的关键决策点及其结果

---

## 设计原则

把"人类掌舵"从口号变成可追踪的系统行为。

**什么时候写入 decisions.jsonl？**
当 workflow 执行中触发了 `waiting_human` 状态时，创建一条决策记录。
当用户做出选择后，更新该记录的 `resolved_with` 和 `status`。

---

## Schema（单行）

```jsonl
{"id":"decision_001","type":"major_plot_change","chapter":"ch012","status":"waiting_human","summary":"是否让林月在ch012提前得知实验真相","why_it_matters":"会影响ch018的反转力度","options":[{"id":"A","label":"提前得知","pros":["当前章节张力更强"],"cons":["后续反转力度下降"]},{"id":"B","label":"只获取部分信息","pros":["保留悬念"],"cons":["需要补一段误导信息"]},{"id":"C","label":"保持未知","pros":["完全保留反转"],"cons":["当前刺激较弱"]}],"recommended":"B","resolved_with":null,"resolved_notes":null,"created_at":"2026-04-07T12:00:00+08:00","resolved_at":null}
```

---

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一ID，格式：`decision_XXX` |
| `type` | enum | ✅ | 见下表 |
| `chapter` | string | ✅ | 触发决策的章节，`chXXX` |
| `status` | enum | ✅ | `waiting_human` / `resolved` / `cancelled` |
| `summary` | string | ✅ | 决策问题简述 |
| `why_it_matters` | string | ❌ | 为什么这个决策重要 |
| `options` | array | ✅ | 选项列表，结构见下 |
| `recommended` | string | ❌ | 系统推荐的选项 ID |
| `resolved_with` | string \| null | ❌ | 用户选择的选项 ID |
| `resolved_notes` | string \| null | ❌ | 用户补充说明 |
| `created_at` | string | ✅ | ISO-8601 时间戳 |
| `resolved_at` | string \| null | ❌ | 解决时间 |

### type 允许值

`character_death` / `major_plot_change` / `world_rule_change` / `new_faction_entry` / `foreshadowing_abandoned` / `outline_deviation` / `high_risk_conflict`

### options 结构

```json
[
  {
    "id": "A",
    "label": "提前得知",
    "pros": ["当前章节张力更强"],
    "cons": ["后续反转力度下降"],
    "impact_scope": ["ch018", "ch020"]
  }
]
```

---

## 允许值

- `status`：`waiting_human`, `resolved`, `cancelled`

---

## 校验规则

1. `id` 全局唯一
2. `resolved_with` 必须是 `options` 中存在的 ID
3. `status=resolved` 时 `resolved_with` 不能为 `null`
4. `status=waiting_human` 时 `resolved_at` 必须为 `null`

---

## 用途

- **Agent**：读取决策结果，恢复 `waiting_human` 的 workflow
- **UI**：Decision Center 页面，集中展示所有待决策/已决策
- **Trace**：用户可以追溯"为什么剧情这样走"

---

## 更新时机

- 触发人类决策点时（新增一行，`status: "waiting_human"`）
- 用户决策后（追加新行更新 `resolved_with` / `status`）
- 用户取消时（追加新行 `status: "cancelled"`）
