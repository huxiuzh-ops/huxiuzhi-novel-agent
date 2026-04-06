# ERRORS.md

> 记录命令失败、异常、工具错误等。

---

## 添加条目的格式

```markdown
## [ERR-YYYYMMDD-NNN] command_or_tool

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending | resolved
**Area**: script | tool | integration | config

### Summary
简要描述什么失败了

### Error
实际的错误信息或输出

### Context
- 尝试的命令/操作
- 使用的输入或参数
- 环境细节（如相关）

### Suggested Fix
如果可以识别，给出可能的修复方案

### Metadata
- Reproducible: yes | no | unknown
- Related Files: 相关文件路径
```

---

## 示例

```markdown
## [ERR-20260406-001] consistency_check

**Logged**: 2026-04-06T14:00:00
**Priority**: medium
**Status**: resolved
**Area**: script

### Summary
consistency_check.py 无法读取包含中文章节号的文件名

### Error
FileNotFoundError: chapters/ch第一章.md not found

### Context
- 脚本使用正则 r'ch(\d+)' 提取章节号
- 中文文件名格式为 ch第一章.md

### Suggested Fix
更新正则表达式支持中文数字：
r'ch(?:第)?([一二三四五六七八九十百千万\d]+)章?'

### Metadata
- Reproducible: yes
- Related Files: scripts/consistency_check.py
```

---

## 未解决的问题

（在此记录还未解决的错误）
