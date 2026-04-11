# novel-agent 5个角色详细落地运行设计文档

> 创建时间：2026-04-07
> 作者：神风大王

---

## 0. 结论前置

你现在最不需要做的，是再新增角色。你最需要做的，是把现有 5 个角色从"文档角色"变成"系统角色"。

也就是让系统明确这几件事：
- 什么时候该调用哪个角色
- 每个角色该看到什么上下文
- 每个角色输出什么格式
- 输出怎么交给下一个角色
- 哪些情况要中断并等人
- 哪些情况要重试或打回

**如果这套机制建立起来，5 个角色就够用而且很强。如果没有，哪怕写成 10 个角色，也只是概念图。**

---

## 1. 五个角色的系统定位

### 1.1 Supervisor

**系统定位**：总调度 / 总入口 / 流程控制者

**负责什么**：
- 接收用户请求
- 判断任务类型
- 选择 workflow
- 决定调用哪些角色
- 判断是否需要人类介入
- 汇总结果并交付

**不负责什么**：
- 不直接写章节
- 不直接做细节审稿
- 不直接维护世界观细节

**一句话**：Supervisor 是"调度器"，不是"全能写手"。

---

### 1.2 Planner

**系统定位**：结构规划器

**负责什么**：
- 全书大纲
- 分卷规划
- 单章 mini plan
- 事件顺序设计
- 节奏安排
- 伏笔植入点规划

**不负责什么**：
- 不直接写完整正文
- 不负责最终审稿

**一句话**：Planner 输出的是"路线图"，不是成品。

---

### 1.3 Writer

**系统定位**：正文生产者

**负责什么**：
- 章节草稿
- 局部重写
- 扩写缩写
- 承接前文
- 落实 Planner 的方案

**不负责什么**：
- 不最终裁定设定冲突
- 不决定重大剧情是否改线
- 不独自修改世界规则

**一句话**：Writer 负责"把计划写成文本"。

---

### 1.4 Editor

**系统定位**：质量检查员

**负责什么**：
- 一致性检查
- 伏笔检查
- 节奏/结构轻审
- 发现风险
- 提出修改意见
- 判断是否需要重写或人工确认

**不负责什么**：
- 不负责世界设定新增
- 不直接做大纲规划
- 不负责最终拍板重大剧情改动

**一句话**：Editor 负责"指出问题和风险"。

---

### 1.5 World

**系统定位**：设定管理员

**负责什么**：
- 新角色/新地点/新势力/新规则
- 设定冲突检查
- world 规则的维护
- world summary / world index 更新

**不负责什么**：
- 不负责日常章节写作
- 不负责普通审稿

**一句话**：World 负责"保证世界不乱"。

---

## 2. 每个角色的标准输入 / 输出

**这是最关键的一层。只有输入输出标准化，角色之间才真的能交接。**

### 2.1 Supervisor 的输入 / 输出

**输入**：Supervisor 接收的是"用户请求 + 项目状态"。

```json
{
  "user_request": "写第8章",
  "project_config": {...},
  "relevant_indexes": {
    "chapters": "...",
    "beats": "...",
    "characters": "..."
  },
  "current_context": {
    "latest_chapter": "ch007",
    "pending_decisions": [],
    "workflow_state": null
  }
}
```

**输出**：Supervisor 不直接产生成品，而是输出一个"任务决定"。

```json
{
  "workflow": "write_chapter",
  "next_role": "Planner",
  "task_type": "write_chapter",
  "task_payload": {
    "chapter": "ch008",
    "need_plan": true,
    "need_review": true
  }
}
```

---

### 2.2 Planner 的输入 / 输出

**输入**：Planner 需要的是"本次要写/要规划什么"以及最小必要上下文。

```json
{
  "task_type": "plan_chapter",
  "chapter": "ch008",
  "volume": "vol01",
  "outline_context": "...",
  "previous_chapter_summary": "...",
  "pending_beats": [...],
  "relevant_characters": [...],
  "constraints": {
    "must_include": ["beat_002"],
    "must_avoid": ["reveal_full_truth"]
  }
}
```

**输出**：Planner 输出应当是结构化章节计划，而不是一大段散文。

```json
{
  "chapter": "ch008",
  "goal": "推进地图线索并制造陈墨与林月的张力",
  "opening": "从渡口夜风和戒备状态切入",
  "middle": [
    "陈墨试图确认交易对象",
    "林月识别地图符号并故意试探",
    "黑水营内部矛盾露头"
  ],
  "turning_point": "军方旧信号被意外激活",
  "ending_hook": "有人在暗处呼叫陈墨的真名",
  "must_include": ["beat_002"],
  "new_entities_expected": [],
  "risk_notes": [
    "不能让林月提前知道全部真相"
  ]
}
```

---

### 2.3 Writer 的输入 / 输出

**输入**：Writer 输入要尽量聚焦，避免全量上下文。

```json
{
  "task_type": "write_chapter",
  "chapter": "ch008",
  "plan": {...},
  "style_guide": "...",
  "previous_chapter_text_or_summary": "...",
  "character_contexts": [...],
  "world_constraints": [...],
  "relevant_beats": [...]
}
```

**输出**：Writer 不应该只输出正文。建议最少输出 4 类东西：

```json
{
  "chapter": "ch008",
  "draft_text": "...完整章节正文...",
  "chapter_summary": "陈墨在渡口与林月对峙，地图线索推进，黑水营暗线浮出。",
  "beats_advanced": ["beat_002"],
  "beats_planted": ["beat_007"],
  "new_entities": {
    "characters": [],
    "locations": [],
    "items": []
  },
  "timeline_candidates": [
    {
      "time_label": "第8日·夜",
      "location": "loc_dukou",
      "participants": ["char_chenmo", "char_linyue"],
      "summary": "渡口冲突"
    }
  ]
}
```

---

### 2.4 Editor 的输入 / 输出

**输入**：Editor 输入应包含草稿与检查所需索引。

```json
{
  "task_type": "review_chapter",
  "chapter": "ch008",
  "draft_text": "...",
  "chapter_summary": "...",
  "indexes": {
    "chapters": [...],
    "characters": [...],
    "beats": [...],
    "timeline": [...]
  },
  "world_rules": [...],
  "review_config": {
    "consistency_check": true,
    "beat_check": true,
    "style_level": "light"
  }
}
```

**输出**：Editor 输出要非常清楚，不然后面没法自动处理。

```json
{
  "chapter": "ch008",
  "verdict": "warning",
  "issues": [
    {
      "id": "issue_001",
      "type": "consistency",
      "severity": "medium",
      "message": "林月识别地图符号的能力缺少前文铺垫",
      "suggested_fix": "补充她此前见过类似符号的暗示"
    }
  ],
  "strengths": [
    "本章结尾钩子有效",
    "主角与林月的互动张力较强"
  ],
  "revision_required": true,
  "requires_human_decision": false,
  "risk_level": "medium"
}
```

---

### 2.5 World 的输入 / 输出

**输入**：World 只在需要时出场，不要让它每章都跑。

```json
{
  "task_type": "update_world",
  "change_request": {
    "type": "add_faction",
    "summary": "新增一个控制北境补给线的势力"
  },
  "world_text": "...",
  "existing_indexes": {
    "characters": [...],
    "locations": [...],
    "world_rules": [...]
  },
  "related_chapters": [...]
}
```

**输出**：

```json
{
  "change_type": "add_faction",
  "proposed_updates": [
    {
      "target_file": "world.md",
      "summary": "新增"赤岸会"势力说明"
    }
  ],
  "new_entities": {
    "factions": [
      {
        "id": "faction_chianhui",
        "name": "赤岸会",
        "summary": "控制北境补给线的地下组织"
      }
    ]
  },
  "conflicts_found": [],
  "requires_human_decision": false
}
```

---

## 3. 角色之间怎么交接

**这是把角色变成 workflow 的核心。**

### 3.1 交接原则

每个角色的输出，必须能直接成为下一个角色的输入。**不要靠"下一个角色自己读懂上一段自然语言"。**

### 3.2 最重要的 4 条交接链

| 链路 | 说明 |
|------|------|
| **Supervisor → Planner** | Supervisor 决定"要不要先规划"，Planner 只负责输出结构化 plan |
| **Planner → Writer** | Writer 不自己从零决定章节方向，Writer 根据 plan 写正文 |
| **Writer → Editor** | Writer 输出草稿 + 摘要 + 事件候选，Editor 基于这些做检查 |
| **Editor → Supervisor** | Editor 不直接拍板重大剧情，只输出 verdict/issues/是否需要人工决策，最终由 Supervisor 决定：交付 / 打回重写 / 升级为 human decision |

### 3.3 World 的交接位置

**从 Supervisor 来**：当用户直接要求新增角色、改设定、改规则、新增势力时。

**从 Writer / Editor 来**：当发现本章引入新地点/新势力/新规则，或新规则与旧规则冲突时。

**World 决定**：是否更新 world 层、是否需要人工确认。

---

## 4. 哪些时候触发哪个角色

| 角色 | 触发条件 | 不触发条件 |
|------|---------|-----------|
| **Supervisor** | 总是触发，所有请求都先过 Supervisor | — |
| **Planner** | 写新章节前、规划卷/大纲、重大改写前、需要先拆分章节结构时 | 单纯查资料、简单一致性检查、轻量设定查询 |
| **Writer** | 写章节、续写、改写、扩写、局部润色 | — |
| **Editor** | 写完章节后、用户要求审稿、改写后复查、设定变更后做影响检查 | — |
| **World** | 新设定、设定冲突、新地点/新势力/新规则、世界规则变更、角色状态重大变化 | — |

---

## 5. 在具体 workflow 里怎么运行

### 5.1 写章节 Workflow

这是最重要的一条链路。

**Step 1：Supervisor**
- 识别请求：任务类型 write_chapter、章节号 ch008
- 输出给 Planner

**Step 2：Planner**
- 输出 chapter_plan
- 交给 Writer

**Step 3：Writer**
- 输出：draft_text、chapter_summary、beats_advanced、beats_planted、timeline_candidates、new_entities
- 交给 Editor

**Step 4：Editor**
- 检查：一致性、伏笔推进、轻风格问题、风险级别
- 输出：verdict、issues、revision_required、requires_human_decision
- 交给 Supervisor

**Step 5：Supervisor 分流**

| 情况 | 处理 |
|------|------|
| 通过 | 保存正文、更新索引、输出给用户 |
| 轻问题 | 派发 revise_chapter 给 Writer，再审一次 |
| 重大剧情问题 | 创建 human decision，状态变成 waiting_human |

---

### 5.2 审稿 Workflow

1. Supervisor 识别 review_chapter
2. Editor 审稿
3. 如果只是报告 → 直接返回用户
4. 如果用户允许修订 → 派给 Writer 做 revision
5. 修订后可再过 Editor

---

### 5.3 改设定 Workflow

1. Supervisor 识别 update_world
2. World 生成设定修改草案
3. 如影响已有章节，Editor 做影响提示
4. 如冲突重大，进入 human decision
5. 确认后更新正文与索引

---

### 5.4 查询 Workflow

1. Supervisor 识别为 query
2. 优先查结构化索引
3. 必要时补读正文
4. 返回答案
5. 不触发复杂多角色链路

---

## 6. 哪些情况必须升级给 Supervisor

**这个很重要，否则角色会越权。**

### Writer 必须升级给 Supervisor 的情况
- 发现 plan 无法落地
- 发现必须新增重大设定
- 发现要改主线方向
- 发现关键角色命运必须改变

### Editor 必须升级给 Supervisor 的情况
- 发现重大一致性冲突
- 发现审稿无法靠局部修复解决
- 发现涉及关键伏笔废弃
- 发现应触发人类决策点

### World 必须升级给 Supervisor 的情况
- 新设定与已有规则严重冲突
- 设定更新会影响大量历史章节
- 世界规则要发生根本变化

---

## 7. 哪些情况必须进入人类决策点

建议第一版写死这几类：
- 主角/核心角色死亡
- 主线目标重大改变
- 世界规则增删改
- 核心设定冲突无法自动修复
- 关键伏笔废弃
- 大纲偏离过大
- 新势力大幅改变势力平衡

---

## 8. 角色落地时最容易犯的错

### 错误 1：5 个角色最后都让同一个 prompt 顺手做完

**这会导致**：表面多角色，实际没有分工。

**正确做法**：哪怕底层是同一个模型，也要：
- 分 role prompt
- 分输入上下文
- 分输出 schema
- 分任务状态

---

### 错误 2：Planner 输出太虚

如果 Planner 只会说"本章要很有张力""注意人物情绪"，那对 Writer 没帮助。

**正确做法**：Planner 输出要能直接写：
- 开头怎么起
- 中段推进什么
- 转折点在哪里
- 必须推进哪条 beat
- 不能踩什么雷

---

### 错误 3：Editor 输出只有评价，没有可执行修订建议

比如只说"这里不够自然""有点问题"，这没法自动流转。

**正确做法**：Editor 要输出：
- 问题类型
- 严重程度
- 具体原因
- 修订建议
- 是否必须重写

---

### 错误 4：World 介入太频繁

如果每章都跑 World，会很重。

**正确做法**：World 只在：新设定、重大设定冲突、新地点/新势力/新规则时介入。

---

## 9. 第一版怎么最小落地

**MVP 工作链**：Supervisor → Planner → Writer → Editor → Supervisor

先别急着让 World 深度介入所有流程。World 第一版作为"按需触发角色"就够了。

**第一版需要做到的最小能力**：
1. 每个角色有独立 prompt/协议
2. 每个角色输入不同
3. 每个角色输出结构化
4. 有明确状态：pending / running / waiting_human / done / failed
5. 至少打通两个 workflow：write_chapter / review_chapter

---

## 10. 一句话收束

你现在这个项目已经有了 5 个角色的"灵魂"，接下来要做的是给它们装上"神经系统"和"交接规则"。

**不是再去发明更多角色，而是把这 5 个角色真正变成：**
- 能被调用
- 能交接
- 能回退
- 能暂停等人
- 能持续协作

**的系统角色**
