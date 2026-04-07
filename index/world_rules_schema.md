# 世界规则索引 / World Rules Index

> 文件路径：`index/world_rules.json`
> 格式：JSON
> 用途：为 AI 生成一份世界规则的机器可读摘要，避免每次都读整个 world.md

---

## 背景

`world.md` 通常很长，而 AI 高频使用的只是其中几个关键规则。
`world_rules.json` 从 `world.md` 中提取 AI 最常查询的信息，生成结构化摘要。

不是 world.md 的副本，而是**为 AI 优化过的规则索引**。

---

## Schema

```json
{
  "power_system": [
    {
      "id": "rule_power_001",
      "title": "污染值不可逆增长",
      "summary": "角色每次过度使用能力都会增加污染值，超过阈值后失控。",
      "priority": "high",
      "source_file": "world.md",
      "source_section": "力量体系"
    }
  ],
  "world_constraints": [
    {
      "id": "rule_world_001",
      "title": "北境与南境交通中断",
      "summary": "常规商路不可通行，跨区移动必须依赖地下线路或军方残留设施。",
      "priority": "high",
      "source_file": "world.md",
      "source_section": "地理/交通"
    }
  ],
  "factions": [
    {
      "id": "faction_blackriver",
      "name": "黑水营",
      "summary": "盘踞北境贸易通道的半军事组织，以走私和情报交易为生。",
      "aligned_with": ["faction_other"],
      "opposed_by": ["faction_tiexie"]
    }
  ],
  "key_items": [
    {
      "id": "item_map_001",
      "name": "残缺地图",
      "summary": "标注了军方残留设施位置的残缺地图，主角的核心道具。",
      "key_property": "指向永辉地下实验室",
      "owner": "char_chenmo"
    }
  ],
  "updated_at": "2026-04-07T00:00:00+08:00"
}
```

---

## 字段说明

### power_system / world_constraints 通用字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一ID |
| `title` | string | ✅ | 规则标题 |
| `summary` | string | ✅ | 规则摘要（供 AI 快速读取） |
| `priority` | enum | ❌ | `high` / `medium` / `low` |
| `source_file` | string | ✅ | 来源文件 |
| `source_section` | string | ❌ | 来源章节/段落 |

### factions 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 势力ID |
| `name` | string | ✅ | 势力名称 |
| `summary` | string | ✅ | 势力摘要 |
| `aligned_with` | array[string] | ❌ | 友好势力 ID |
| `opposed_by` | array[string] | ❌ | 敌对势力 ID |

### key_items 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 道具ID |
| `name` | string | ✅ | 道具名称 |
| `summary` | string | ✅ | 道具摘要 |
| `key_property` | string | ❌ | 关键属性 |
| `owner` | string | ❌ | 当前持有者 ID |

---

## 用途

- **Agent**：写章节时快速读取世界规则约束，不必每次读完整的 world.md
- **Editor**：一致性检查时比对规则
- **World**：设定冲突检测
- **UI**：World Bible Rules 页

---

## 更新时机

- world.md 更新后，由 AI 或脚本重新提取
- 新增/删除势力时
- 世界规则重大变更时（触发人类决策）
