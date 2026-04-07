# 伏笔追踪模板

> 每条伏笔/剧情线索对应一条记录。
> 由 Agent 或用户手动添加到 `index/beats.jsonl`（以及 `beats/TRACKING.md`）。
> 
> **为什么要用这个模板**：每条伏笔都是一枚定时炸弹——埋下去不难，难的是准时引爆。
> 用这个模板追踪，确保不会埋了忘收。

---

## 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `id` | 唯一标识 | `beat_001` |
| `type` | 伏笔类型 | `foreshadow` / `mystery` / `revelation` / `plot_twist` / `character_arc` |
| `description` | 伏笔描述（1-2句话） | "残缺地图背后指向军方实验设施" |
| `status` | 当前状态 | `pending` / `active` / `due_soon` / `overdue` / `resolved` / `abandoned` |
| `planted_in` | 埋入章节 | `ch003` |
| `planned_payoff` | 计划回收章节 | `ch010` |
| `actual_payoff` | 实际回收章节（回收后填写） | `ch012` |
| `related_characters` | 关联角色ID | `["char_chenmo", "char_linyue"]` |
| `related_locations` | 关联地点ID | `["loc_yonghui"]` |
| `priority` | 优先级 | `high` / `medium` / `low` |

---

## 状态说明

| 状态 | 含义 |
|------|------|
| `pending` | 伏笔已埋，等待推进 |
| `active` | 正在被提及/推进 |
| `due_soon` | 临近计划回收（当前章 >= planned_payoff - 3） |
| `overdue` | 超过计划回收章节尚未回收 |
| `resolved` | 已回收 |
| `abandoned` | 已废弃（不再回收） |

---

## 添加新伏笔

在 `beats/TRACKING.md` 中追加一行：

```
| beat_001 | foreshadow | 残缺地图背后指向军方实验设施 | ch003 | ch010 | pending |
```

同时运行：
```bash
python scripts/incremental_index_update.py <workspace> add_beat beat_001 \
  --type foreshadow \
  --description "残缺地图背后指向军方实验设施" \
  --planted_in ch003 \
  --planned_payoff ch010 \
  --priority high
```

---

## 更新伏笔状态

```bash
# 伏笔被推进时
python scripts/incremental_index_update.py <workspace> update_beat beat_001 --status active

# 伏笔回收时
python scripts/incremental_index_update.py <workspace> update_beat beat_001 \
  --status resolved --actual_payoff ch012

# 伏笔废弃时
python scripts/incremental_index_update.py <workspace> update_beat beat_001 --status abandoned
```

---

## 类型说明

| 类型 | 含义 | 例子 |
|------|------|------|
| `foreshadow` | 预兆/伏笔 | "这个符号之后会再次出现" |
| `mystery` | 谜团 | "林月为什么认识这个符号？" |
| `revelation` | 揭露 | "主角的真实身份曝光" |
| `plot_twist` | 剧情转折 | "盟友其实是幕后黑手" |
| `character_arc` | 角色弧光 | "对手最终倒戈" |
