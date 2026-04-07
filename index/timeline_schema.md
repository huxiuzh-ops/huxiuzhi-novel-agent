# 时间线索引 / Timeline Index

> 文件路径：`index/timeline.jsonl`
> 格式：JSONL（每行一条事件）
> 用途：记录故事中的事件、人物位置变化、知识获得、状态变化

---

## 设计原则

**不是简单记录"第几章发生什么"**，而是记录：
- **事件**（发生了什么）
- **人物位置**（谁在哪）
- **知识获得**（谁知道了什么）
- **状态变化**（谁的状态变了）

这样才能支持复杂的时间线一致性检查（瞬移检测、信息链检测、状态延续检测）。

---

## Schema（单行）

```jsonl
{"id":"evt_ch008_sc01_01","chapter":"ch008","scene":"sc01","time_label":"第8日·夜","absolute_day":8,"location":"loc_dukou","participants":["char_chenmo","char_linyue"],"event_type":"conflict","summary":"陈墨与林月在渡口发生冲突","knowledge_changes":[{"character":"char_linyue","learned":"陈墨持有地图"}],"state_changes":[{"entity":"char_chenmo","field":"injury","new_value":"left_arm_minor"}],"source":"chapters/ch008.md","updated_at":"2026-04-07T00:00:00+08:00"}
```

---

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一ID，格式：`evt_{chapter}_{scene}_{seq}` |
| `chapter` | string | ✅ | 所属章节，`chXXX` 格式 |
| `scene` | string | ✅ | 场景序号，`scXX` 格式 |
| `time_label` | string | ✅ | 故事内时间标签，如 `第8日·夜` |
| `absolute_day` | number | ✅ | 故事内绝对天数（从故事开始计算） |
| `location` | string | ✅ | 地点 ID |
| `participants` | array[string] | ✅ | 参与角色 ID 列表 |
| `event_type` | enum | ✅ | 见下表 |
| `summary` | string | ✅ | 事件简述 |
| `knowledge_changes` | array | ❌ | 知识获得列表，结构见下 |
| `state_changes` | array | ❌ | 状态变化列表，结构见下 |
| `source` | string | ✅ | 来源文件路径 |
| `updated_at` | string | ✅ | ISO-8601 时间戳 |

### event_type 允许值

`conflict` / `negotiation` / `discovery` / `movement` / `death` / `injury` / `item_acquired` / `item_lost` / `decision` / `revelation` / `plot_advance` / `foreshadow` / `other`

### knowledge_changes 结构

```json
[
  {
    "character": "char_chenmo",
    "learned": "林月是铁蝎帮的人",
    "from_whom": "char_linyue"
  }
]
```

### state_changes 结构

```json
[
  {
    "entity": "char_chenmo",
    "field": "injury",
    "old_value": null,
    "new_value": "left_arm_minor"
  },
  {
    "entity": "item_map_001",
    "field": "owner",
    "old_value": "char_chenmo",
    "new_value": "char_linyue"
  }
]
```

---

## 校验规则

1. `id` 全局唯一
2. `chapter` 格式为 `chXXX`
3. `absolute_day` >= 1
4. `participants` 中的角色 ID 应存在于 `characters.json`
5. `location` 应存在于 `locations.json`

---

## 时间线风险检测

基于 timeline.jsonl 可以检测：

| 风险类型 | 检测逻辑 |
|---------|---------|
| 瞬移 | 同一角色在 `absolute_day` 相同时出现在不同 `location` |
| 提前知情 | 角色在尚未获得某知识时表现出知情 |
| 状态断裂 | 受伤/死亡状态后续未延续 |
| 已故角色出现 | `status=dead` 的角色在更晚章节出现在 `participants` 中 |

---

## 用途

- **Agent**：判断角色是否"瞬移"、是否在正确时间知道正确的事
- **Editor**：时间线一致性检查
- **UI**：Timeline 页面（按章节/角色/地点三种视图）
- **World**：状态变化追踪

---

## 更新时机

- 章节写完后，从章节内容提取事件写入
- 角色状态重大变化时（死亡、受伤）
- 物品转移时（地图易手等）
- 知识获得发生时
