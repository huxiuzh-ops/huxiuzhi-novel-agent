# FEATURE_REQUESTS.md

> 记录用户请求的新功能，以及你想给 agent 加的新能力。

---

## 添加条目的格式

```markdown
## [FEAT-YYYYMMDD-NNN] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending | implemented
**Area**: skill | script | workflow | integration

### Requested Capability
用户想要什么功能

### User Context
为什么需要它，想解决什么问题

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
如何实现，可以扩展什么

### Metadata
- Frequency: first_time | recurring
- Related Features: 现有相关功能
```

---

## 示例

```markdown
## [FEAT-20260406-001] scene_ontology_auto_update

**Logged**: 2026-04-06T10:00:00
**Priority**: high
**Status**: pending
**Area**: workflow

### Requested Capability
写完一章后，自动提取场景信息写入 ontology/graph.jsonl

### User Context
用户在审稿时发现很多场景细节没被追踪，希望 agent 自动维护知识图谱

### Complexity Estimate
medium

### Suggested Implementation
在 Editor Agent 审稿通过后，增加一步：
1. 读取章节内容
2. 提取场景：地点、时间、人物、情绪、关键事件
3. 追加到 ontology/graph.jsonl
4. 更新 scene 计数

### Metadata
- Frequency: first_time
- Related Features: ontology, editor_agent
```

---

## 已实现的功能

（从 FEATURE_REQUESTS 里迁移到这里，表示已实现）
