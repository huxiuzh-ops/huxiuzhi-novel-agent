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

## 系统商店商品定价（固定价格表）
> 首次出现后锁定，不可随意改动

| 商品 | 价格 | 说明 |
|------|------|------|
| 闪火弹 | 30点/颗 | 致盲3秒，近距离有效 |
| 肾上腺素注射剂 | 15点/支 | 全队+30%运动能力，持续3分钟 |
| 活血膏 | 10点/管 | 止痛消肿 |
| 战术通讯器 | 15点/个 | 5公里实时通话 |
| 通讯扫描 | 10点/次 | 截获加密频道（需3小时） |
| 烟雾弹 | 20点/颗 | 能见度归零，持续10秒 |
| 噪音弹 | 25点/颗 | 制造2秒失聪 |

### 剧情点状态
- ch016结束时：75点（-30闪火弹，-15肾上腺素，-10活血膏，-10通讯扫描）
- ch017：-30闪火弹（赊账），当前剩余75点
- ch001起始：0点（赊账30）
- ch012完成：170点

## 地点表（出现过的地点）

| 地点 | 首次出现 | 备注 |
|------|---------|------|
| 江城市 | ch001 | 末世第三年的主要活动区域 |
| 永辉购物中心 | ch001 | 首次全称，后续简称"永辉"，三环内侧，有铁蝎帮据点 |
| 青云巷 | ch002 | 下水道入口，主角规划的路线之一 |
| 建设路 | ch002 | 路线A段，丧尸密度中等 |
| 西南医科大学 | ch001 | 备选物资点，距离远，有T1活动区 |

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
