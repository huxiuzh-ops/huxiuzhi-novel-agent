# novel-agent 结构化索引详细设计

> 创建时间：2026-04-07
> 作者：神风大王

---

## 1. 设计目标

### 1.1 为什么需要结构化索引

novel-agent 的核心问题不是"能不能生成一章"，而是：**如何让 AI 在长篇、多卷、多角色、多设定的项目里，稳定、低成本、持续协作。**

如果没有结构化索引，系统会长期依赖：
- 每次重新读取大量 markdown
- 每次从自然语言中临时抽角色信息
- 每次靠模型猜"哪些内容和当前任务相关"

这会带来 4 个问题：

1. **token 成本高** - 每次写一章、审一章、查一个角色，都可能读很多无关文件
2. **稳定性差** - 年龄、势力、角色状态、伏笔状态容易被模型临时理解错
3. **速度慢** - UI 和 Agent 都需要先扫大量文件，响应会拖
4. **高级能力难做** - 没有稳定索引，就很难做好时间线、决策点影响分析、章节风险提示、世界观查询、报告生成、检索增强

### 1.2 结构化索引的定义

结构化索引不是替代正文，也不是把小说写成数据库。它的定位是：

**为 AI 和程序提供一层机器可读、低成本、可校验、可更新的"项目状态入口"。**

#### 一句话理解

- **正文负责表达**
- **索引负责检索、定位、状态管理**

### 1.3 设计原则

**原则 A：人写 markdown，AI/系统读索引**

不要逼作者把所有内容写成 JSON。作者仍然应该主要写 world.md、characters/*.md、outline/*.md、chapters/*.md。结构化索引由系统辅助维护。

**原则 B：索引是"摘要层"，不是"全文复制层"**

索引不存整章全文，不复制整份设定。它只存 AI 高频要用的信息：文件位置、实体 id/name、状态、摘要、关系、时间、标签。

**原则 C：先做高频索引，不一口气全做完**

第一版只做最有价值的索引：
1. 角色索引
2. 章节索引
3. 伏笔索引
4. 地点索引
5. 时间线索引

**原则 D：允许 AI 生成，但必须可校验、可修正**

索引可以由 AI 提取，但不能完全相信 AI。要有：schema 约束、脚本校验、UI 修正入口、手动覆盖能力。

**原则 E：对多平台透明**

无论入口是 OpenClaw、Codex、Claude、API 模式、Web UI，都应该使用同一套索引目录和格式。

---

## 2. 总体架构

### 2.1 双层知识架构

建议整个项目采用双层结构：

**第一层：内容层 Content Layer**
```
world.md
characters/
outline/
chapters/
beats/
style_guide.md
```

**第二层：索引层 Index Layer**
```
index/
  characters.json
  chapters.json
  beats.jsonl
  locations.json
  timeline.jsonl
  decisions.jsonl
  tags.json
```

### 2.2 数据流

```
作者/AI 修改正文
  ↓
触发提取器（AI 或规则脚本）
  ↓
生成/更新索引候选项
  ↓
schema 校验
  ↓
写入 index/
  ↓
UI / Agent / 脚本使用索引
```

### 2.3 谁来消费索引

索引的消费者有 4 类：

1. **Agent** - 检索相关角色、检索本章相关伏笔、决定读哪些正文、生成报告
2. **Web UI** - Dashboard、列表页、快速筛选、风险提示、时间线展示
3. **脚本工具** - consistency check、beat tracking、timeline check、report generation
4. **平台适配器** - OpenClaw / Claude / Codex / API 模式统一上下文准备

---

## 3. 目录设计

### 3.1 推荐目录

```
index/
  README.md
  characters.json
  chapters.json
  beats.jsonl
  locations.json
  timeline.jsonl
  decisions.jsonl
  world_rules.json
  build-meta.json
```

### 3.2 各文件职责

- **characters.json** - 角色摘要索引
- **chapters.json** - 章节摘要索引
- **beats.jsonl** - 伏笔/剧情线索索引
- **locations.json** - 地点摘要索引
- **timeline.jsonl** - 事件级时间线索引
- **decisions.jsonl** - 人类决策点记录
- **world_rules.json** - 世界规则的机器摘要
- **build-meta.json** - 记录索引构建时间、版本、来源、生成方式

---

## 4. 核心索引详细设计

### 4.1 角色索引 `index/characters.json`

**目标**：让系统快速知道有哪些角色、角色在哪个文件、当前状态是什么、最近出现在哪、属于哪个阵营、是否是高优先角色。

**建议格式**：

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
    "age": 22,
    "gender": "male",
    "first_appearance": "ch001",
    "last_appearance": "ch008",
    "tags": ["主角", "拾荒者", "冷静"],
    "summary": "废土世界中的年轻拾荒者，持有残缺地图，与黑水营和军方实验线相关。",
    "importance": "core",
    "updated_at": "2026-04-07T08:00:00Z"
  }
]
```

**字段说明**：
- `id` - 稳定 ID，供系统引用
- `name` - 角色主名
- `aliases` - 别名/称呼
- `file` - 角色正文文件路径
- `role` - protagonist / antagonist / supporting / mentor 等
- `faction` - 引用势力 ID
- `status` - alive / dead / missing / injured / unknown
- `first_appearance` - 首次出场章节
- `last_appearance` - 最近出场章节
- `tags` - 便于检索
- `summary` - 角色摘要，供 AI 快速读取
- `importance` - core / major / minor

**用途**：
- Agent 侧：写章节时快速找"当前相关角色"、审稿时检查角色状态延续、查询时快速返回角色信息
- UI 侧：角色列表、筛选核心角色、显示最近出场与状态

**第一版注意事项**：不要一开始往角色索引塞太多"深层心理""复杂关系网"。第一版先保留：身份、状态、文件位置、出场信息、摘要。够用了。

---

### 4.2 章节索引 `index/chapters.json`

**目标**：让系统快速知道有哪些章节、每章状态如何、每章讲了什么、本章涉及哪些角色、地点、伏笔、是否已审稿/定稿。

**建议格式**：

```json
[
  {
    "id": "ch008",
    "file": "chapters/ch008.md",
    "title": "黑夜渡口",
    "status": "draft",
    "word_count": 3520,
    "summary": "陈墨在渡口与林月再次交锋，地图线索推进，黑水营内部矛盾开始显现。",
    "volume": "vol01",
    "characters": ["char_chenmo", "char_linyue"],
    "locations": ["loc_dukou"],
    "beats_advanced": ["beat_002"],
    "beats_planted": ["beat_007"],
    "previous_chapter": "ch007",
    "next_chapter": null,
    "review_status": "pending",
    "risk_level": "medium",
    "updated_at": "2026-04-07T08:00:00Z"
  }
]
```

**字段说明**：
- `status` - planned / draft / reviewing / revised / final
- `review_status` - pending / passed / warning / failed
- `risk_level` - low / medium / high
- `characters` - 本章出现的角色 ID
- `locations` - 本章主要地点 ID
- `beats_advanced` - 推进的伏笔
- `beats_planted` - 新增伏笔

**关键建议**：章节索引里的 summary 很重要。它将来是上下文预算优化的核心之一。因为重任务时不必重读整章，而是先读：前一章 summary、当前卷 summary、相关角色 summary。

---

### 4.3 伏笔索引 `index/beats.jsonl`

**目标**：让系统对"伏笔/剧情线索"有稳定追踪能力。

beats 用 JSONL 而不是纯 JSON，原因是：append-friendly、易增量写入、更适合事件型记录。

**建议格式**：

```jsonl
{"id":"beat_002","type":"foreshadow","description":"残缺地图背后指向军方实验设施","status":"pending","planted_in":"ch003","planned_payoff":"ch010","actual_payoff":null,"related_characters":["char_chenmo"],"related_locations":["loc_heishui"],"priority":"high","updated_at":"2026-04-07T08:00:00Z"}
{"id":"beat_007","type":"mystery","description":"林月似乎认识地图背面的符号","status":"pending","planted_in":"ch008","planned_payoff":"ch012","actual_payoff":null,"related_characters":["char_linyue"],"related_locations":["loc_dukou"],"priority":"medium","updated_at":"2026-04-07T08:00:00Z"}
```

**状态**：
- pending
- active
- due_soon
- overdue
- resolved
- abandoned

**关键建议**：beats 一定要做成显式系统，不要只藏在正文里。否则长篇越写越容易"埋了不收"。

---

### 4.4 地点索引 `index/locations.json`

**目标**：让系统知道有哪些地点、地点属于哪里、哪些章节出现过、地点类型是什么。

**建议格式**：

```json
[
  {
    "id": "loc_dukou",
    "name": "渡口",
    "aliases": ["黑水渡口"],
    "kind": "transport_hub",
    "region": "北境",
    "file": "world.md",
    "first_appearance": "ch004",
    "last_appearance": "ch008",
    "summary": "黑水镇边缘的重要交通节点，也是黑水营走私与情报交易的关键地点。",
    "tags": ["交通枢纽", "危险地带"],
    "updated_at": "2026-04-07T08:00:00Z"
  }
]
```

---

### 4.5 时间线索引 `index/timeline.jsonl`

**目标**：这不是简单记录"第几章发生什么"，而是记录事件、人物位置、知识获得、状态变化。

**建议格式**：

```jsonl
{"id":"evt_ch008_sc01_01","chapter":"ch008","scene":"sc01","time_label":"第8日·夜","absolute_day":8,"location":"loc_dukou","participants":["char_chenmo","char_linyue"],"event_type":"conflict","summary":"陈墨与林月在渡口发生冲突","knowledge_changes":[{"character":"char_linyue","learned":"陈墨持有地图"}],"state_changes":[{"entity":"char_chenmo","field":"injury","new_value":"left_arm_minor"}],"source":"chapters/ch008.md","updated_at":"2026-04-07T08:00:00Z"}
```

**字段分组**：

- 基本定位：id、chapter、scene、time_label、absolute_day、location
- 参与信息：participants
- 事件信息：event_type、summary
- 变化信息：knowledge_changes、state_changes

---

### 4.6 决策索引 `index/decisions.jsonl`

**目标**：把"人类掌舵"的关键节点记录下来。

**建议格式**：

```jsonl
{"id":"decision_001","type":"major_plot_change","chapter":"ch012","status":"waiting_human","summary":"是否让主角提前得知军方实验真相","why_it_matters":"会影响 ch018 的反转力度","options":[{"id":"A","label":"提前得知"},{"id":"B","label":"只获取部分信息"},{"id":"C","label":"保持未知"}],"recommended":"B","resolved_with":null,"updated_at":"2026-04-07T08:00:00Z"}
```

---

### 4.7 世界规则索引 `index/world_rules.json`

**目标**：world.md 往往很长，而 AI 最常用的其实是那几个关键规则。所以建议额外生成一份规则摘要。

**建议格式**：

```json
{
  "power_system": [
    {
      "id": "rule_power_001",
      "title": "污染值不可逆增长",
      "summary": "角色每次过度使用能力都会增加污染值，超过阈值后失控。",
      "priority": "high"
    }
  ],
  "world_constraints": [
    {
      "id": "rule_world_001",
      "title": "北境与南境交通中断",
      "summary": "常规商路不可通行，跨区移动必须依赖地下线路或军方残留设施。",
      "priority": "high"
    }
  ],
  "factions": [
    {
      "id": "faction_blackriver",
      "name": "黑水营",
      "summary": "盘踞北境贸易通道的半军事组织。"
    }
  ],
  "updated_at": "2026-04-07T08:00:00Z"
}
```

---

## 5. 索引构建机制

### 5.1 更新策略

三种更新方式共存：

**方式 A：任务后增量更新**
每次写完一章、修改设定、审稿完成后，自动更新相关索引。

**方式 B：手动全量重建**
提供一个"重建索引"功能，扫描全项目重新生成索引。

**方式 C：UI 手动修正**
在界面上直接改角色状态、伏笔状态、时间线事件摘要。

### 5.2 推荐流程

写完章节后的流程：
1. 保存 chapters/ch008.md
2. AI 提取：本章摘要、出场角色、主要地点、伏笔推进、时间线事件
3. 写入候选索引
4. 跑 schema 校验
5. 更新 index/chapters.json
6. 更新 index/timeline.jsonl
7. 如发现新角色/新地点/新伏笔，再更新对应索引

### 5.3 全量重建场景

适用于：旧项目迁移、索引损坏、升级 schema、大量历史内容导入。

---

## 6. Schema 与校验

结构化索引最怕"越积越脏"。所以一定要有校验机制。

### 6.1 必做的校验

**基础校验**：
- 必填字段是否存在
- 类型是否正确
- status 是否在允许集合中
- id 是否唯一

**引用校验**：
- 章节引用是否存在
- 角色 ID 是否存在
- 地点 ID 是否存在
- 伏笔关联对象是否存在

**逻辑校验**：
- last_appearance 不能早于 first_appearance
- planned_payoff 不能早于 planted_in
- 决策状态必须合法

### 6.2 校验失败处理

- **低风险**：自动修正常见格式问题
- **中风险**：标记 warning，允许继续
- **高风险**：阻止写入，并提示人工修正

---

## 7. AI 提取策略

### 7.1 AI 在结构化索引中的角色

AI 不负责"定义 schema"，AI 负责：
- 从正文抽摘要
- 抽取出场角色
- 抽取事件
- 识别新增实体
- 判断本章推进了哪些伏笔

### 7.2 AI 输出要求

所有索引提取都应该要求 AI 返回结构化 JSON，而不是大段解释。

例如：
```json
{
  "chapter_summary": "...",
  "characters": ["char_chenmo", "char_linyue"],
  "locations": ["loc_dukou"],
  "beats_advanced": ["beat_002"],
  "new_beats": [],
  "timeline_events": [...]
}
```

### 7.3 AI 提取的最佳实践

**先提取，后校验**：AI 负责候选结果，规则脚本负责兜底。

**小任务拆分**：不要一次让 AI 输出整个世界的所有索引。应该按任务粒度做：章节提取、角色文件提取、world 规则提取、beats 更新提取。这样更稳。

---

## 8. 检索与上下文拼装策略

### 8.1 推荐的上下文拼装顺序

当系统要执行"写第 9 章"时：

**第一步：先读索引**
- chapters.json 找到 ch008 摘要
- beats.jsonl 找到近期待回收伏笔
- characters.json 找到本章相关角色摘要
- timeline.jsonl 找到最近关键事件

**第二步：再决定读哪些正文**
比如只补读：chapters/ch008.md、characters/chenmo.md、characters/linyue.md、outline/volume_01.md

**第三步：必要时读更深层材料**
world.md、style_guide.md

### 8.2 带来的提升

- token 大幅下降
- 相关性上升
- 模型不容易被无关内容干扰
- 响应更快

---

## 9. UI 如何使用索引

| 页面 | 数据来源 |
|------|---------|
| Dashboard | chapters.json - 章节数、草稿数、待回收伏笔数、高风险章节、待决策项 |
| Chapter Studio | 章节索引、时间线索引、伏笔索引 - 本章摘要、角色、地点、推进内容、风险 |
| Beat Board | beats.jsonl - pending / due_soon / overdue / resolved |
| Timeline | timeline.jsonl - 按角色/地点/章节筛选 |
| Decision Center | decisions.jsonl |

---

## 10. 跨平台兼容设计

### 10.1 核心原则

索引目录和 schema 不依赖任何平台。OpenClaw / Claude / Codex / API 都可以用同一套索引。

### 10.2 平台适配只负责"怎么读"

- **OpenClaw**：技能里优先读 index，再读正文
- **Claude / Codex**：入口 prompt 指定先看 index/
- **API mode**：server 在组装上下文时优先读取索引

---

## 11. 版本与演进策略

### v1 范围

- characters.json
- chapters.json
- beats.jsonl
- locations.json
- timeline.jsonl
- schema 校验
- 增量更新

### v2 再做

- decisions.jsonl
- world_rules.json
- 更复杂的关系索引
- 报告缓存索引
- 风格偏差索引

### v3 再考虑

- 图查询能力
- 更复杂的实体关系网络
- 语义检索 embedding 层
- 多项目统一索引管理

---

## 12. 落地顺序建议

1. **先定义 schema** - 先把这 5 个索引文件的字段定下来
2. **做全量构建器** - 给旧项目或样例项目生成一次完整索引
3. **做增量更新器** - 写完章节后自动更新索引
4. **让 Agent 先消费索引** - 先别急着做很复杂 UI，先让 Agent 上下文拼装改成索引优先
5. **再让 UI 消费索引** - 这样 UI 自然就会很快

---

## 13. 最终价值总结

结构化索引层做好了，会直接给 novel-agent 带来 6 个核心提升：

1. **更符合 AI 的习惯** - AI 不再反复扫全文，而是先读摘要层
2. **更便宜** - token 降很多
3. **更稳** - 角色状态、伏笔状态、章节状态不容易漂
4. **更快** - 无论是 UI 还是 Agent 响应都会明显更顺
5. **更容易做高级功能** - 时间线、决策中心、报告、风险检测都会有基础
6. **更适合跨平台** - OpenClaw / Claude / Codex / API 可以共享同一套"项目状态层"

---

## 14. 一句话收束

把"长篇小说项目"的长期状态，从散落的自然语言文件中抽出来，变成 AI 可以稳定读取和更新的项目骨架。

**没有这层，系统能演示；有了这层，系统才有机会长期可用。**
