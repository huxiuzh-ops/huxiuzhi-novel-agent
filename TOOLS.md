# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 技能说明

### self-improving-agent
- 路径：`skills/self-improving-agent`
- 日志文件：`.learnings/LEARNINGS.md`、`.learnings/ERRORS.md`、`.learnings/FEATURE_REQUESTS.md`
- Hook 已启用（`self-improvement`），每次启动自动注入自省提醒
- 触发：出错、被纠正、发现更好做法、用户请求不存在的能力

### ontology
- 路径：`skills/ontology`
- 存储：`memory/ontology/graph.jsonl`（append-only，每次操作追加一行 JSON）
- Schema：`memory/ontology/schema.yaml`
- Python 脚本（`scripts/ontology.py`）：此机器未装 Python，直接用文件操作代替
- 支持类型：Person、Project、Task、Event、Document、Action 等
- 关系约束可定义在 schema.yaml 中

### novel-writing
- 路径：`skills/novel-writing`
- 参考：Novel-Claude 工业级网文框架（三段式引擎：世界观→分卷→场景写作）
- 项目目录：`novel/`（logline.md、world.md、characters.md、outline/、beats/、chapters/）
- 流程：Logline → 世界观 → 人物 → 情节结构 → 场景打点 → 写作 → 修订
- 配合 ontology 记录实体（World、Character、Faction、PlotPoint）
