# index/ — 结构化索引

> 结构化索引是 AI 与程序高频访问的项目状态摘要层。
> **正文由人写、人读；索引由系统维护，AI 优先读索引而不是全文。**

---

## 文件说明

| 文件 | 格式 | 用途 |
|------|------|------|
| `characters.json` | JSON | 角色摘要索引 |
| `chapters.json` | JSON | 章节摘要索引 |
| `beats.jsonl` | JSONL | 伏笔/剧情线索追踪（append-only） |
| `locations.json` | JSON | 地点摘要索引 |
| `timeline.jsonl` | JSONL | 事件级时间线（含知识/状态变化） |
| `decisions.jsonl` | JSONL | 人类决策点记录 |
| `world_rules.json` | JSON | 世界规则机器摘要 |

每个文件对应的 **schema 定义文档**（描述每个字段的含义）在 `../index/` 目录下，与本 `index/` 数据目录分开。

---

## 数据流

```
正文变更（人/AI）
    ↓
触发提取（AI 提取 或 规则脚本）
    ↓
Schema 校验
    ↓
写入 index/
    ↓
消费者：Agent / UI / 脚本
```

---

## 生成初始索引

```bash
python scripts/build_index.py <你的小说项目路径>
```

这会扫描你的 `world.md`、`characters/`、`chapters/`、`beats/` 目录，生成 `index/` 下的所有索引文件。

---

## 增量更新

```bash
# 更新章节索引
python scripts/incremental_index_update.py <workspace> update_chapter ch008 --status final

# 新增伏笔
python scripts/incremental_index_update.py <workspace> add_beat beat_055 --type foreshadow --description "..."

# 更新角色状态
python scripts/incremental_index_update.py <workspace> update_character char_chenmo --status injured
```

完整命令列表见 `incremental_index_update.py --help`。

---

## 与正文的关系

- **索引是摘要，不是副本**——不存储正文内容，只存储 AI 高频查询的信息（id/状态/摘要/关系）
- **正文是 source of truth**——如果索引和正文冲突，以正文为准，手动修正索引

---

## .gitignore

`index/` 目录通常不需要提交到 Git（由 `build_index.py` 自动生成）。已在 `.gitignore` 中排除。
