# 伏笔索引 / Beats Index

> 文件路径：`index/beats.jsonl`
> 格式：JSONL（每行一条 JSON）
> 用途：追踪伏笔/剧情线索的埋入、推进、回收状态

---

## 为什么用 JSONL

- **append-friendly**：新增伏笔直接追加一行，不需要读写整个 JSON 数组
- **易增量写入**：每次更新只追加新状态行，不修改历史
- **更适合事件型记录**：伏笔状态变化本身就是事件

---

## 状态变更规则

伏笔状态变更采用**追加新行**的方式：
- 新增伏笔：追加一行 `status: "pending"`
- 状态推进：追加新行，更新 `status` / `actual_payoff` / `notes`
- 标记废弃：追加新行 `status: "abandoned"`

读取时取每条伏笔的**最新一行**作为当前状态。

---

## Schema（单行）

```jsonl
{"id":"beat_001","type":"foreshadow","description":"残缺地图背后指向军方实验设施","status":"pending","planted_in":"ch001","planned_payoff":"ch010","actual_payoff":null,"related_characters":["char_chenmo"],"related_locations":["loc_yonghui"],"priority":"high","notes":"","updated_at":"2026-04-07T00:00:00+08:00"}
{"id":"beat_002","type":"mystery","description":"林月似乎认识地图背面的符号","status":"pending","planted_in":"ch001","planned_payoff":"ch012","actual_payoff":null,"related_characters":["char_linyue"],"related_locations":["loc_yonghui"],"priority":"medium","notes":"","updated_at":"2026-04-07T00:00:00+08:00"}
```

---

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一ID，格式 `beat_XXX` |
| `type` | enum | ✅ | `foreshadow` / `mystery` / `revelation` / `plot_twist` / `character_arc` |
| `description` | string | ✅ | 伏笔描述 |
| `status` | enum | ✅ | `pending` / `active` / `due_soon` / `overdue` / `resolved` / `abandoned` |
| `planted_in` | string | ✅ | 埋入章节，`chXXX` 格式 |
| `planned_payoff` | string \| null | ❌ | 计划回收章节 |
| `actual_payoff` | string \| null | ❌ | 实际回收章节 |
| `related_characters` | array[string] | ❌ | 关联角色 ID 列表 |
| `related_locations` | array[string] | ❌ | 关联地点 ID 列表 |
| `priority` | enum | ✅ | `high` / `medium` / `low` |
| `notes` | string | ❌ | 备注 |
| `updated_at` | string | ✅ | ISO-8601 时间戳 |

---

## 状态说明

| 状态 | 含义 |
|------|------|
| `pending` | 伏笔已埋，等待推进 |
| `active` | 伏笔正在被推进/提及 |
| `due_soon` | 临近计划回收节点（当前章 >= planned_payoff - 3） |
| `overdue` | 超过计划回收章节尚未回收 |
| `resolved` | 已回收 |
| `abandoned` | 已废弃 |

---

## 允许值

- `type`：`foreshadow`, `mystery`, `revelation`, `plot_twist`, `character_arc`
- `status`：`pending`, `active`, `due_soon`, `overdue`, `resolved`, `abandoned`
- `priority`：`high`, `medium`, `low`

---

## 校验规则

1. `id` 全局唯一
2. `planted_in` 格式为 `chXXX`
3. `planned_payoff` 如果有，格式为 `chXXX`，且章节号 >= `planted_in`
4. `actual_payoff` 如果有，章节号 >= `planted_in`

---

## 用途

- **Agent**：写章节时自动提醒哪些伏笔要推进
- **Editor**：审稿时检测本章是否应回收某条线索
- **UI**：Beat Board 看板（Planned / Active / Due Soon / Overdue / Resolved / Abandoned）
- **Dashboard**：逾期伏笔提醒

---

## 更新时机

- 新伏笔埋入时（追加 pending 行）
- 伏笔被提及/推进时（追加 active 行）
- 伏笔回收时（追加 resolved 行，填 actual_payoff）
- 伏笔废弃时（追加 abandoned 行）
- 计划回收章节变更时（追加新行更新 planned_payoff）
