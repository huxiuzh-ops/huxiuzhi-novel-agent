# LEARNINGS.md

> 记录每次被纠正的内容，形成自我修正记忆。

每次用户纠正你的写法、指出错误、或者你自己发现更好的做法，都记录在这里。

---

## 添加条目的格式

```markdown
## [LRN-YYYYMMDD-NNN] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending | resolved
**Area**: style | consistency | plot | character | pacing | dialogue

### Summary
一句话描述学到了什么

### Details
完整上下文：发生了什么、哪里不对、正确的是什么

### Suggested Action
具体的修正或改进

### Metadata
- Source: user_feedback | self_reflection | error
- Related Files: 相关文件路径
- Tags: tag1, tag2
- Recurrence-Count: 1
```

---

## 示例

```markdown
## [LRN-20260406-001] character_voice

**Logged**: 2026-04-06T10:00:00
**Priority**: high
**Status**: resolved
**Area**: character

### Summary
主角在紧张场面时不能用冷幽默，要用更真实的反应

### Details
ch047 写主角在铁蝎帮来袭时用调侃缓解气氛，用户指出不对：
紧张场面应该用更真实的恐惧/紧张反应，冷幽默只适合日常。

### Suggested Action
在 style_guide.md 中添加：
- 紧张场面：不用冷幽默，用真实情绪反应
- 冷幽默只用于日常对话和轻度紧张场面

### Metadata
- Source: user_feedback
- Related Files: workspace/style_guide.md
- Tags: 角色声音, 情绪真实性
- Recurrence-Count: 1
```
