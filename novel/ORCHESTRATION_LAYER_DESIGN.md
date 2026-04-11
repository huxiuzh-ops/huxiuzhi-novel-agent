# novel-agent 多 Agent / 编排层详细设计文档 v1

> 创建时间：2026-04-07
> 作者：神风大王

---

## 0. 结论前置

对这个项目来说，最合适的不是"重型多 Agent 框架"，而是一个**轻量的 Role-Based Workflow Engine（基于角色的工作流引擎）**。

也就是说：
- 对外看起来是多 Agent
- 对内先不一定要真并发、真分布式
- 但要有清晰的角色、任务、状态、决策点、回退机制

---

## 1. 编排层的目标

### 1.1 它要解决什么问题

结构化索引解决的是"怎么查得准、查得快"。编排层解决的是：

**系统现在在做什么、下一步该谁做、失败了怎么办、什么时候该停下来等人。**

如果没有编排层，系统就会退化成：
- 用户发一个请求 → AI 自己脑补流程
- 可能写了、也可能检查了
- 但过程不可控
- 出错不易回退
- 多角色只存在于文档里

所以编排层的本质，是把：
> "AI 应该这样工作"
变成
> "系统真的按这个流程工作"

### 1.2 它不是为了炫技

这里的设计原则是：

**编排层的价值**：
- 提高稳定性
- 明确边界
- 便于追踪
- 支持人类决策点
- 降低 AI 自说自话

**编排层不追求**：
- 一开始就并发五个子 agent
- 一开始就图工作流 + 队列 + 多 worker
- 一开始就做复杂 runtime infra

---

## 2. 总体架构：Role-Based Workflow Engine

### 2.1 为什么不用一开始就上重型图框架

比如 LangGraph 那种节点图、状态图，确实强。但对这个项目的第一阶段，有几个问题：
- 门槛高
- 对平台耦合大
- 影响开箱即用
- 作者不一定需要理解这么复杂的结构
- 会让"产品原型"变成"工程项目"

所以 novel-agent 先做成：
> **角色驱动 + 任务驱动 + 状态驱动**
> 而不是图驱动 + 框架驱动

### 2.2 核心思想

编排层由 4 个基础对象组成：

1. **Role** - 谁来做
   - Supervisor、Planner、Writer、Editor、World

2. **Task** - 做什么
   - write_chapter、review_chapter、update_world、query_character、plan_volume

3. **State** - 做到哪了
   - pending / running / blocked / waiting_human / done / failed

4. **Transition** - 下一步往哪走
   - 写完草稿 → 进入审稿
   - 审稿发现冲突 → 进入 blocked
   - 关键冲突 → waiting_human
   - 审稿通过 → done

### 2.3 一句话模型

一个"知道任务该交给谁、什么时候暂停、什么时候继续"的**轻量 AI 调度器**。

---

## 3. 角色设计

### 3.1 角色不是模型，角色是职责

角色更应该理解为**一种带职责边界的工作模式**：
- 可能用同一个模型
- 但用不同的 role prompt / context policy / output schema
- 扮演不同职责

这样最适合开箱即用。

### 3.2 推荐的 5 个基础角色

#### A. Supervisor

**职责**：
- 接收用户请求
- 判断请求类型
- 选择 workflow
- 组装上下文
- 决定是否需要其他角色参与
- 处理最终交付或升级为人类决策点

**适合做的事**：
- "写第 8 章"
- "帮我规划第二卷"
- "这个角色设定冲突了吗？"
- "新增一个势力"

**不做什么**：
- 不直接承担细节写作
- 不直接做深度审稿
- 不承担世界规则维护细节

#### B. Planner

**职责**：
- 做大纲
- 做章节 mini plan
- 生成结构骨架
- 明确本章/本卷的目标、节奏、转折、钩子

**输出重点**：简洁结构化方案，不是大段散文，便于 Writer 接手

#### C. Writer

**职责**：
- 写章节草稿
- 做局部改写
- 扩写、润色、补桥段
- 承接上一章和大纲约束

**输出重点**：
- 正文
- 本章新增要点摘要
- 新增实体候选项

#### D. Editor

**职责**：
- 一致性检查
- 伏笔推进检查
- 风格/结构轻审
- 提出修改建议
- 标记风险等级

**输出重点**：
- 审稿结果
- 风险清单
- 建议修订项
- 是否需要人类确认

#### E. World

**职责**：
- 处理世界设定变更
- 新角色/新势力/新地点写入
- 检查规则冲突
- 更新世界规则摘要和索引

**输出重点**：
- 更新后的设定草案
- 冲突说明
- 相关章节影响提示

---

## 4. 任务系统设计

### 4.1 Task 是编排层的核心单位

每一个用户请求，最终都要被映射成一个或多个 Task。

**Task 的作用**：
- 记录任务类型
- 记录执行角色
- 记录当前状态
- 记录输入/输出
- 记录依赖关系
- 记录是否需要人工参与

### 4.2 Task Schema（第一版）

```json
{
  "task_id": "task_20260407_001",
  "type": "write_chapter",
  "role": "Writer",
  "status": "pending",
  "priority": "normal",
  "chapter": "ch008",
  "volume": "vol01",
  "created_by": "user",
  "created_at": "2026-04-07T12:00:00Z",
  "input_refs": [
    "index/chapters.json",
    "index/beats.jsonl",
    "characters/chenmo.md",
    "outline/volume_01.md"
  ],
  "depends_on": [],
  "outputs": [],
  "warnings": [],
  "requires_human": false,
  "metadata": {}
}
```

### 4.3 核心任务类型

**写作类**：
- write_chapter
- revise_chapter
- continue_chapter

**规划类**：
- plan_book
- plan_volume
- plan_chapter

**审核类**：
- review_chapter
- check_consistency
- check_beats
- check_timeline

**设定类**：
- add_character
- update_character
- add_faction
- update_world_rule
- add_location

**查询类**：
- query_character
- query_plotline
- query_timeline

**决策类**：
- resolve_decision
- request_human_decision

### 4.4 状态设计

| 状态 | 含义 |
|------|------|
| pending | 任务已创建，尚未执行 |
| running | 任务执行中 |
| blocked | 因缺失依赖、检测失败、冲突未解而中断 |
| waiting_human | 需要用户确认 |
| done | 完成 |
| failed | 执行失败，且未恢复 |
| cancelled | 用户取消 |

---

## 5. Workflow 设计

### 5.1 Workflow 是任务模板

比如"写章节"不是一个动作，而是一个流程：
1. 识别请求
2. 读取相关上下文
3. 做章节小规划
4. 写草稿
5. 审稿
6. 判断是否通过
7. 可能修订
8. 更新索引
9. 交付

### 5.2 第一版建议的 4 条核心 Workflow

| Workflow | 适用请求 |
|----------|---------|
| **写章节** | 写第 X 章、继续写、根据大纲写这一章 |
| **审章节** | 帮我审稿、看这一章有没有问题、检查一致性 |
| **改设定** | 新增角色、修改世界观、新增势力、改规则 |
| **查询/问答** | 这个角色在哪些章节出现过、某条伏笔什么时候埋的 |

---

## 6. 关键 Workflow 细化

### 6.1 Workflow A：写章节

**Step 1：Supervisor 识别任务**

输入：用户请求、当前项目配置、章节索引、伏笔索引、时间线索引

输出：创建 write_chapter workflow、选择章节号、确定是否先规划

---

**Step 2：Planner 产出 mini plan**

输入：当前卷大纲、上一章摘要、本章待推进伏笔、相关角色摘要、自主等级配置

输出示例：

```json
{
  "chapter": "ch008",
  "goal": "推进地图线索，制造陈墨与林月关系张力",
  "opening": "从渡口夜风与戒备氛围切入",
  "middle": "双方交锋，地图相关信息被隐约揭示",
  "turning_point": "林月识别出地图符号",
  "ending_hook": "远处出现军方旧信号",
  "must_include": ["beat_002"],
  "must_avoid": ["主角提前得知全部真相"]
}
```

**为什么需要这个步骤**：因为直接让 Writer 写，容易失控。有了 mini plan，Writer 的自由度还在，但方向被钉住了。

---

**Step 3：Writer 写草稿**

输入：mini plan、相关角色正文、style_guide、上一章正文/摘要、本章相关设定

输出：章节草稿、本章摘要、新增角色/地点/伏笔候选项、本章事件候选项

---

**Step 4：Editor 审稿**

输入：草稿、章节索引、角色索引、伏笔索引、时间线索引、world_rules

输出：

```json
{
  "result": "warning",
  "issues": [
    {
      "type": "consistency",
      "severity": "medium",
      "message": "林月在上一章并未知晓地图存在，本章识别符号缺少铺垫。"
    }
  ],
  "revision_required": true,
  "requires_human": false
}
```

---

**Step 5：分流**

| 情况 | 处理 |
|------|------|
| 通过 | 更新章节状态、更新索引、交付 |
| 轻微问题 | 生成 revise_chapter task、Writer 修订、再次审稿 |
| 重大剧情冲突 | 生成 decision point、状态变成 waiting_human |

---

**Step 6：更新索引**

- 更新 chapters.json
- 更新 beats.jsonl
- 更新 timeline.jsonl
- 如有新增实体，更新对应索引

---

### 6.2 Workflow B：审章节

适用场景：用户已有草稿、用户只想检查、用户不想自动改

流程：
1. Supervisor 识别为 review_chapter
2. Editor 审稿
3. 规则脚本辅助检查
4. 输出审稿报告
5. 如用户同意，再派生 revise_chapter

---

### 6.3 Workflow C：改设定

适用场景：新增角色、修改势力、增加世界规则、改人物设定

流程：
1. Supervisor 判断任务类型
2. World 处理设定变更草案
3. 检查是否与现有规则冲突
4. 如影响重大，进入 decision point
5. 更新正文与索引

---

### 6.4 Workflow D：查询/问答

适用场景：某角色第一次出现在哪、某条伏笔状态是什么、某地点发生过什么

流程：
1. 优先查索引
2. 必要时回读正文
3. 输出答案
4. 不必触发复杂 workflow

---

## 7. 决策点怎么插入工作流

### 7.1 决策点不是额外功能，而是 workflow 的分支

任何 workflow 在执行中都可能进入 `waiting_human`，而不是"先完成，再问用户"。

### 7.2 触发决策点的类型（第一版最少）

- 主角/核心角色死亡
- 主线目标改变
- 世界规则修改
- 新势力加入主线
- 伏笔废弃或提前回收
- 重大一致性冲突无法自动修复

### 7.3 决策点输出格式

不要问一句"要不要这样改"，而是要输出结构化卡片：

```json
{
  "decision_id": "decision_20260407_001",
  "type": "major_plot_change",
  "status": "waiting_human",
  "summary": "是否让林月在 ch012 提前知道实验真相",
  "why_it_matters": "会削弱 ch018 的反转力度",
  "options": [
    {
      "id": "A",
      "label": "提前得知",
      "pros": ["当前章节张力更强"],
      "cons": ["后续反转力度下降"]
    },
    {
      "id": "B",
      "label": "只获得部分信息",
      "pros": ["保留悬念"],
      "cons": ["需要补一段误导信息"]
    }
  ],
  "recommended": "B"
}
```

### 7.4 决策后如何恢复流程

用户选择后：
1. 写入 decisions.jsonl
2. 原 workflow 从 waiting_human 恢复
3. 后续 Writer / World / Editor 读取该决策结果继续执行

---

## 8. 上下文装配策略

### 8.1 编排层不直接"喂全量上下文"

编排层应该控制上下文拼装逻辑：
- 先读索引
- 再选正文
- 最后按任务拼装最小必要上下文

### 8.2 按角色定上下文

| 角色 | 需要的上下文 |
|------|------------|
| Planner | 当前卷大纲、上一章摘要、待推进 beats、相关角色摘要 |
| Writer | mini plan、上一章正文或摘要、相关角色正文、style guide、必要世界规则 |
| Editor | 当前草稿、索引、时间线、伏笔、关键规则 |
| World | world.md、相关设定文件、已有索引、相关章节摘要 |

### 8.3 好处

每个角色都不会读太多无关内容，既省 token，又符合 AI 习惯。

---

## 9. 跨平台兼容设计

### 9.1 核心原则

**业务逻辑要和平台入口解耦**：
- Workflow engine 是一套
- Platform adapter 是另一套

### 9.2 Platform Adapter 职责

每个平台适配层只负责：
- 怎么接收用户请求
- 怎么读项目配置
- 怎么传给 workflow engine
- 怎么把结果显示给用户

而**不是**在平台层重新实现一套工作流。

### 9.3 各平台建议

**OpenClaw**：
- 适合：skills 驱动、文件工作流、任务分发、子任务调度
- 建议：skill 中明确"先索引、后正文"，workflow 可通过工具链跑起来

**Claude / Codex**：
- 适合：本地工程目录、文件编辑、prompt 驱动工作流
- 建议：CLAUDE.md / AGENT.md 里约定 workflow，同样以索引为第一读取入口

**API Mode**：
- 适合：Web UI 调用、轻 server 模式、统一 prompt bundle
- 建议：workflow engine 在 server 端，API mode 只负责模型调用

---

## 10. 任务记录与 Trace

编排层一定要有最小 trace，不然系统不可控。

### 10.1 每个 task 记录什么

```json
{
  "task_id": "task_001",
  "workflow": "write_chapter",
  "role": "Writer",
  "status": "done",
  "inputs": [
    "index/chapters.json",
    "characters/chenmo.md",
    "outline/volume_01.md"
  ],
  "checks": [
    {"name": "beat_check", "status": "passed"},
    {"name": "timeline_check", "status": "warning"}
  ],
  "outputs": [
    "chapters/ch008.md",
    "index/timeline.jsonl"
  ],
  "duration_ms": 8120,
  "updated_at": "2026-04-07T12:00:00Z"
}
```

### 10.2 为什么要有 trace

用户未来一定会问：
- 为什么这样写？
- 为什么你说这里冲突？
- 你到底读了哪些文件？
- 你是怎么决定让它等我确认的？

**没有 trace，就只能靠 AI 现编解释。**

---

## 11. 错误处理与回退机制

### 11.1 第一版必须处理的错误

- AI 返回结构化结果失败
- 索引更新失败
- 设定冲突
- 审稿发现重大矛盾
- 平台调用失败
- 超时

### 11.2 回退策略

| 级别 | 策略 |
|------|------|
| 轻错误 | 自动重试一次，或退化为简化模式 |
| 中错误 | 标 warning，不阻断主要流程 |
| 重错误 | 进入 blocked、输出原因、提示用户决定下一步 |

### 11.3 不要做什么

**不要在出错时让系统"假装成功"**。这是很多 AI 产品的坏习惯。

---

## 12. 第一版实现建议

### Phase 1：做轻量 Workflow Engine

实现：
- task schema
- workflow schema
- 状态流转
- role dispatch
- decision point

> 此时甚至不用真多模型，只要同一模型按不同 role prompt 工作即可。

### Phase 2：先接最关键的两个 workflow

- write_chapter
- review_chapter

> 这两个一打通，产品就有主价值。

### Phase 3：接索引更新

让 workflow 和结构化索引打通：
- 写完更新 chapters/timeline/beats
- 审完更新 review 状态

### Phase 4：再接设定类 workflow

- add/update character
- add/update faction
- update world rule

### Phase 5：最后再扩查询和 UI 控制台

这样不会一开始就摊太大。

---

## 13. 一句话收束

> 这个编排层的真正作用，不是把项目"包装成多 agent"，而是：
> **把 AI 从"会写一段文字"提升成"能按明确流程、明确职责、明确边界长期协作的工作系统"。**
>
> 如果结构化索引是骨架，那编排层就是**神经系统**。
