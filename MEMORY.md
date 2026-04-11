# MEMORY.md - 写作偏好与风格

## 小说项目

- **书名**：《末世·毒舌系统》
- **主角**：陈末
- **当前进度**：第四十八章完成（暗夜侦察·铁蝎帮120人三倍兵力·声波武器情报·观测者决定介入·新生深夜等待父亲归来·剧情点155·病毒凝固剂入手·明日晨观测者情报交接）
- **下一章目标**：第四十九章（晨曦·观测者情报交接·声波武器弱点·铁蝎帮兵力部署图·制定作战计划·新生与父亲的约定）

### 项目结构（已重构）
```
novel/
├── characters/          # 人物单独存档（5人）
├── outline/             # 大纲
│   ├── index.md         # 总导航
│   ├── structure.md     # 宏观结构
│   └── volumes/         # 分卷大纲（10卷全）
├── beats/
│   ├── template.md
│   └── TRACKING.md      # 伏笔追踪（核心！）
├── chapters/            # 章节正文（ch001-ch008）
├── inventory/           # 装备/道具存档
└── world.md / logline.md
```

### 写作规范
- 单章3000字以上
- 章节结尾必须有钩子
- 伏笔统一记入beats/TRACKING.md

## novel-agent 优化进展（2026-04-07）

### 已完成

**架构重构**：
- 新建 `config/` 目录（4个 YAML 配置文件，与具体小说项目无关）
  - `config/project.yaml` — 项目基础配置
  - `config/writing.yaml` — 写作规则
  - `config/validation.yaml` — 验证规则
  - `config/platforms.yaml` — 多平台配置
- 新建 `AGENT.md` — 平台无关的核心定义文件
  - 5个角色的输入/输出 schema
  - 任务类型定义
  - 状态机（7态）
  - 4条核心工作流
  - 角色交接规则
  - 人类决策点标准
- 重写 `SKILL.md` — OpenClaw 薄适配层（只含平台特定约定）
- 重写 `CLAUDE.md` — Claude Code/Codex 薄适配层

**核心架构原则**：
- AGENT.md 是业务核心，平台入口是薄适配层
- config/ 是框架级配置，与具体小说项目完全解耦
- 符合五份设计文档的要求

### 下一步（按优先级）
1. ~~建立 `index/` 结构化索引 schema~~ ✅ 已完成
2. ~~建立角色提示模板 `roles/`~~ ✅ 已完成
3. ~~建立 `scripts/workflow_state.py`~~ ✅ 已完成
4. ~~建立 `scripts/incremental_index_update.py`~~ ✅ 已完成
5. 更新 `SETUP_WIZARD.md`（对接新配置系统）
6. 把 AGENT.md + roles/ 真正接入 OpenClaw skill 执行流程

### 已创建的索引体系（index/）
- `README.md` — 总说明
- `characters_schema.md` — characters.json schema
- `chapters_schema.md` — chapters.json schema
- `beats_schema.md` — beats.jsonl schema（JSONL格式，append-only）
- `locations_schema.md` — locations.json schema
- `timeline_schema.md` — timeline.jsonl schema（含 knowledge_changes / state_changes）
- `decisions_schema.md` — decisions.jsonl schema
- `world_rules_schema.md` — world_rules.json schema

### 已创建的角色模板（roles/）
- `README.md` — 角色模板总说明
- `supervisor.md` — Supervisor 提示模板（任务分发、决策升级）
- `planner.md` — Planner 提示模板（大纲/章节规划）
- `writer.md` — Writer 提示模板（正文写作）
- `editor.md` — Editor 提示模板（审稿/一致性检查）
- `world.md` — World 提示模板（设定管理/冲突检测）

### 已创建的脚本（scripts/）
- `build_index.py` — 全量索引构建（扫描任意小说项目生成初始索引）
- `incremental_index_update.py` — 增量索引更新（7个命令：update_chapter/add_beat/update_beat/update_character/add_location/add_timeline_event/rebuild）
- `workflow_state.py` — 工作流状态管理（7个命令：start/advance/complete/status/waiting/resume/list）

## 写作偏好与风格

## 系统角色设定（重要！）
- 系统不是工具，是有血有肉的角色
- 毒舌贱嘴，但不是真的嫌弃
- 像老朋友/损友，关键时刻靠谱
- 口头禅示例："您"、"说真的"、"我都替您丢人"
- 毒舌要有创意，不能重复
- 例：嘲讽陈末的方式要多样化（蠢、笨、命大、运气差等）

## 系统示例对话（毒舌风格）
- 好："说真的，我都替您的智商着急。"
- 差："您真是个愚蠢的宿主。"
- 好："您知道猪是怎么死的吗？笨死的。"
- 差："您的决定非常不明智。"

## 场景描写规范（重要！）
- 禁止全段对话推动剧情
- 每段对话不超过3-5句
- 对话之间要有动作/心理/场景描写
- 动作描写：眼神、手、步伐、周围环境
- 心理描写：心跳、想法、回忆、直觉
- 场景描写：光线、声音、气味、温度
- 建议：描写和对话比例约1:1

## 常见错误提醒（已纠正过的）
- 错别字：需要写完后通读检查
- 语句通顺：避免长句堆叠
- 逻辑一致：注意前后时间线和状态
- "腰带"错字：已修正
- 第八章修正：周岩说话时"她是陈末"→"他是陈末"（性别错误）
- 第八章修正：铁蝎帮的 黑话 → 铁蝎帮的黑话（多余空格）

## 写作进化记录
- 2026-03-26：增设字数控制规范（最低3000字/章）
- 2026-03-26：修正第二章错别字和语句问题
- 2026-03-27：完成第八章（倒计时），揭示织星者真相（AI/冷战项目），获得血雾能力
- 2026-03-27：揭示关键信息：林雪父亲发现织星者→被其杀死→林雪复仇，星巢在江城地下分散节点
