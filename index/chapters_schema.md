# 章节索引 / Chapters Index

> 文件路径：`index/chapters.json`
> 格式：JSON Array
> 用途：让系统快速知道有哪些章节、状态、摘要、关联实体

---

## Schema

```json
[
  {
    "id": "ch001",
    "file": "chapters/ch001.md",
    "title": "废墟微光",
    "status": "final",
    "word_count": 3847,
    "summary": "陈墨在永辉购物中心废墟中拾荒，遭遇神秘女子，获得残缺地图。",
    "volume": "vol01",
    "characters": ["char_chenmo", "char_linyue"],
    "locations": ["loc_yonghui"],
    "beats_advanced": [],
    "beats_planted": ["beat_001", "beat_002"],
    "previous_chapter": null,
    "next_chapter": "ch002",
    "review_status": "passed",
    "risk_level": "low",
    "updated_at": "2026-04-07T00:00:00+08:00"
  }
]
```

---

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 章节ID，格式 `chXXX` |
| `file` | string | ✅ | 章节正文文件路径 |
| `title` | string | ✅ | 章节标题 |
| `status` | enum | ✅ | `planned` / `draft` / `reviewing` / `revised` / `final` |
| `word_count` | number | ✅ | 字数 |
| `summary` | string | ✅ | 章节摘要（供 AI 快速读取，建议 1-3 句话） |
| `volume` | string | ❌ | 所属分卷，如 `vol01` |
| `characters` | array[string] | ✅ | 本章出场角色 ID 列表 |
| `locations` | array[string] | ❌ | 本章主要地点 ID 列表 |
| `beats_advanced` | array[string] | ✅ | 本章推进的伏笔 ID 列表 |
| `beats_planted` | array[string] | ✅ | 本章新埋的伏笔 ID 列表 |
| `previous_chapter` | string \| null | ✅ | 上一章 ID，无则 `null` |
| `next_chapter` | string \| null | ✅ | 下一章 ID，无则 `null` |
| `review_status` | enum | ✅ | `pending` / `passed` / `warning` / `failed` |
| `risk_level` | enum | ✅ | `low` / `medium` / `high` |
| `updated_at` | string | ✅ | ISO-8601 时间戳 |

---

## 允许值

- `status`：`planned`, `draft`, `reviewing`, `revised`, `final`
- `review_status`：`pending`, `passed`, `warning`, `failed`
- `risk_level`：`low`, `medium`, `high`

---

## 校验规则

1. `id` 全局唯一
2. `word_count` >= 0
3. `previous_chapter` 和 `next_chapter` 引用的章节应存在
4. `characters` / `locations` / `beats_advanced` / `beats_planted` 中的 ID 应有对应的索引条目（警告级）

---

## 用途

- **Agent**：写下一章时先读上一章摘要，不用重读全文
- **Editor**：审稿时检查角色/地点是否应该延续
- **UI**：章节列表页、Dashboard、章节摘要卡片
- **Planner**：生成章节计划时的上下文输入

---

## 更新时机

- 章节写完/修改后
- 章节 status 变化时
- 章节 summary 重写时
- 新增伏笔/推进伏笔后
