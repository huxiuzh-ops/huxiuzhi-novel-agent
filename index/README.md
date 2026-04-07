# 结构化索引 / Structured Index

> 本目录存放 AI 与程序高频访问的结构化状态数据。
> 
> **设计原则**：
> - 正文文件（`world.md`、`characters/`、`chapters/` 等）由人写、人读
> - 索引文件由系统维护，AI 优先读取索引而不是正文
> - 索引是"摘要层"，不是"全文复制层"
> - 所有索引均可被人类修正

---

## 索引文件一览

| 文件 | 格式 | 用途 |
|------|------|------|
| `characters.json` | JSON | 角色摘要索引 |
| `chapters.json` | JSON | 章节摘要索引 |
| `beats.jsonl` | JSONL | 伏笔/剧情线索追踪 |
| `locations.json` | JSON | 地点摘要索引 |
| `timeline.jsonl` | JSONL | 事件级时间线 |
| `decisions.jsonl` | JSONL | 人类决策点记录 |
| `world_rules.json` | JSON | 世界规则机器摘要 |
| `build-meta.json` | JSON | 索引构建元数据 |

---

## 数据流

```
正文变更（人/AI）
    ↓
触发提取（AI 提取 或 规则脚本）
    ↓
生成/更新索引候选
    ↓
Schema 校验
    ↓
写入 index/
    ↓
消费者：Agent / UI / 脚本 / Platform Adapter
```

---

## 更新策略

三种方式共存：

| 方式 | 触发时机 |
|------|---------|
| **任务后增量更新** | 写完章节、修改设定、审稿完成后自动更新 |
| **手动全量重建** | 提供 `scripts/rebuild_index.py`，扫描全项目重新生成 |
| **UI 手动修正** | 在界面上直接改角色状态、伏笔状态等 |

---

## Schema 校验

详见各文件注释。必做校验：
- 必填字段是否存在
- ID 是否唯一
- status 是否在允许集合中
- 引用实体是否存在（章节ID、角色ID等）
- 逻辑约束（last_appearance >= first_appearance 等）

---

## 跨平台说明

索引目录和 schema 不依赖任何平台。OpenClaw / Claude / Codex / API 模式都使用同一套索引。
