# 角色索引 / Characters Index

> 文件路径：`index/characters.json`
> 格式：JSON Array
> 用途：让系统快速知道有哪些角色、状态、文件位置、出场信息

---

## Schema

```json
[
  {
    "id": "char_chenmo",
    "name": "陈墨",
    "aliases": ["阿墨"],
    "file": "characters/chenmo.md",
    "role": "protagonist",
    "faction": "faction_blackriver",
    "status": "alive",
    "age": null,
    "gender": null,
    "first_appearance": "ch001",
    "last_appearance": "ch048",
    "tags": [],
    "summary": "",
    "importance": "core",
    "updated_at": "2026-04-07T00:00:00+08:00"
  }
]
```

---

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 稳定唯一ID，格式：`char-{pinyin}` |
| `name` | string | ✅ | 角色主名 |
| `aliases` | array[string] | ❌ | 别名/称呼列表 |
| `file` | string | ✅ | 角色正文文件路径（相对于 workspace 根目录） |
| `role` | enum | ✅ | `protagonist` / `antagonist` / `supporting` / `minor` / `mentor` |
| `faction` | string | ❌ | 所属势力ID（引用 `locations.json` 中的势力或自定义） |
| `status` | enum | ✅ | `alive` / `dead` / `missing` / `injured` / `unknown` |
| `age` | number \| null | ❌ | 年龄 |
| `gender` | string \| null | ❌ | `male` / `female` / `other` |
| `first_appearance` | string | ✅ | 首次出场章节，格式 `chXXX` |
| `last_appearance` | string | ✅ | 最近出场章节，格式 `chXXX` |
| `tags` | array[string] | ❌ | 便于检索的标签，如 `["主角", "拾荒者"]` |
| `summary` | string | ✅ | 角色摘要（供 AI 快速读取，建议 1-3 句话） |
| `importance` | enum | ✅ | `core` / `major` / `minor` |
| `updated_at` | string | ✅ | ISO-8601 时间戳 |

---

## 允许值

- `role`：`protagonist`, `antagonist`, `supporting`, `minor`, `mentor`
- `status`：`alive`, `dead`, `missing`, `injured`, `unknown`
- `importance`：`core`, `major`, `minor`

---

## 校验规则

1. `id` 全局唯一，不重复
2. `first_appearance` 和 `last_appearance` 格式为 `chXXX`（X 为数字，可含前导零）
3. `last_appearance` 对应的章节号 >= `first_appearance` 对应的章节号
4. `file` 引用的文件应存在（警告级，不阻止写入）

---

## 用途

- **Agent**：写章节时快速检索相关角色，不必读所有角色文件
- **Editor**：审稿时检查角色状态是否延续
- **UI**：角色列表、筛选核心角色、显示最近出场与状态
- **Dashboard**：角色统计、最近新增

---

## 更新时机

- 新增角色时
- 角色状态变化时（死亡、失踪、受伤）
- 角色出场新章节时
- 角色 summary 重写时
