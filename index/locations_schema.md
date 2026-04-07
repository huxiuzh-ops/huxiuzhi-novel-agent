# 地点索引 / Locations Index

> 文件路径：`index/locations.json`
> 格式：JSON Array
> 用途：让系统知道有哪些地点、归属、出现章节、类型

---

## Schema

```json
[
  {
    "id": "loc_yonghui",
    "name": "永辉购物中心",
    "aliases": ["永辉"],
    "kind": "ruins",
    "region": "江城市·三环内侧",
    "file": "world.md",
    "first_appearance": "ch001",
    "last_appearance": "ch048",
    "summary": "末世前的大型商业中心，废墟中藏有物资，是陈墨的主要拾荒点。",
    "tags": ["废墟", "拾荒点", "铁蝎帮据点"],
    "updated_at": "2026-04-07T00:00:00+08:00"
  }
]
```

---

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一ID，格式：`loc-{pinyin}` |
| `name` | string | ✅ | 地点主名 |
| `aliases` | array[string] | ❌ | 别名列表 |
| `kind` | enum | ✅ | `city` / `town` / `village` / `ruins` / `transport_hub` / `camp` / `building` / `underground` / `wilderness` |
| `region` | string | ❌ | 所属区域/地理归属 |
| `file` | string | ✅ | 地点出处文件（`world.md` 或具体章节） |
| `first_appearance` | string | ✅ | 首次出现章节，`chXXX` 格式 |
| `last_appearance` | string | ✅ | 最近出现章节，`chXXX` 格式 |
| `summary` | string | ✅ | 地点摘要（供 AI 快速读取） |
| `tags` | array[string] | ❌ | 标签 |
| `updated_at` | string | ✅ | ISO-8601 时间戳 |

---

## 允许值

- `kind`：`city`, `town`, `village`, `ruins`, `transport_hub`, `camp`, `building`, `underground`, `wilderness`

---

## 校验规则

1. `id` 全局唯一
2. `first_appearance` 和 `last_appearance` 格式为 `chXXX`
3. `last_appearance` 章节号 >= `first_appearance` 章节号

---

## 用途

- **Agent**：写作时保持地理一致性，避免"瞬移"
- **Editor**：检查时间线是否矛盾（同一角色同一时间出现在两地）
- **UI**：World Bible 地点页、Timeline 按地点筛选
- **Timeline**：事件发生在哪个地点

---

## 更新时机

- 新地点首次出现时
- 地点 summary 重写时
