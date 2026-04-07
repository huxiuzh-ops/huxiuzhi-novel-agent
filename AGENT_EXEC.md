# AGENT_EXEC.md — 角色执行协调器

> 这是 `AGENT.md` 的执行层补充，定义如何在实际对话中运行 5 个角色。
> 
> **注意**：这是一个 Python 脚本的规范定义，用于当需要实际执行角色逻辑时调用。
> 当 OpenClaw/Claude Code agent 工作时，直接读取 `roles/*.md` 中的提示模板即可。

---

## 概念

角色执行协调器（Role Executor）是一个上下文装配器：
- 接收用户请求 + 当前项目状态
- 决定调用哪个角色
- 组装该角色的输入上下文
- 让 LLM 以该角色身份生成输出
- 把输出转为结构化 JSON
- 交给下一个角色或结束

**不是多进程，不是真的并发，只是上下文隔离。**

---

## 核心接口

### execute_role(role, task_type, context) → dict

```python
def execute_role(
    role: str,           # "Supervisor" | "Planner" | "Writer" | "Editor" | "World"
    task_type: str,      # "write_chapter" | "review_chapter" | ...
    context: dict         # 任务相关的上下文数据
) -> dict:               # 角色的结构化输出
```

---

## 各角色的执行规范

### Supervisor.execute(task_type, user_request)

**职责**：接收请求，判断类型，装配 Supervisor 初始输出。

**输入 context**：
```python
{
    "user_request": "写第8章",
    "project_path": "/path/to/novel",
    "current_chapter": "ch007",
    "config": {...}  # config/writing.yaml 内容
}
```

**输出**：
```python
{
    "workflow": "write_chapter",
    "task_id": "task_20260407_001",
    "next_role": "Planner",
    "task_payload": {
        "chapter": "ch008",
        "need_plan": True,
        "need_review": True
    },
    "requires_human": False,
    "planner_context": {...}  # 装配好 Planner 需要的所有输入
}
```

---

### Planner.execute(task_type, planner_context)

**职责**：基于上下文，生成章节 mini plan。

**输入 context**（由 Supervisor 装配）：
```python
{
    "chapter": "ch008",
    "volume": "vol01",
    "outline_summary": "...",         # 当前卷大纲摘要
    "previous_chapter_summary": "...", # 上一章摘要
    "pending_beats": [...],          # 待推进伏笔
    "relevant_characters": [...],     # 相关角色摘要
    "constraints": {
        "must_include": ["beat_002"],
        "must_avoid": ["reveal_full_truth"]
    }
}
```

**输出**：
```python
{
    "chapter": "ch008",
    "goal": "推进地图线索，制造陈墨与林月的张力",
    "opening": "从渡口夜风和戒备状态切入",
    "middle": ["...", "...", "..."],
    "turning_point": "军方旧信号被意外激活",
    "ending_hook": "有人在暗处呼叫陈墨的真名",
    "must_include": ["beat_002"],
    "new_entities_expected": [],
    "risk_notes": ["不能让林月提前知道全部真相"]
}
```

**prompt 模板来源**：`roles/planner.md`

---

### Writer.execute(task_type, writer_context)

**职责**：根据 plan 写正文草稿。

**输入 context**（由 Supervisor 装配）：
```python
{
    "chapter": "ch008",
    "plan": {...},  # Planner 的输出
    "style_guide": "...",  # style_guide.md 全文
    "previous_chapter_text_or_summary": "...",
    "character_contexts": [...],  # 角色正文摘要
    "world_constraints": [...],
    "relevant_beats": [...],
    "writing_config": {
        "min_words": 3000,
        "max_consecutive_dialogue_lines": 5,
        "require_chapter_hook": True
    }
}
```

**输出**：
```python
{
    "chapter": "ch008",
    "draft_text": "...3000+字正文...",
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

**prompt 模板来源**：`roles/writer.md`

---

### Editor.execute(task_type, editor_context)

**职责**：审稿，输出一致性/伏笔/风格问题。

**输入 context**（由 Supervisor 装配）：
```python
{
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
        "consistency_check": True,
        "beat_check": True,
        "style_level": "light"
    }
}
```

**输出**：
```python
{
    "chapter": "ch008",
    "verdict": "warning",  # passed | warning | failed
    "issues": [
        {
            "id": "issue_001",
            "type": "consistency",  # consistency | beat | style | logic
            "severity": "medium",
            "message": "林月识别地图符号缺少前文铺垫",
            "suggested_fix": "补充她此前见过类似符号的暗示",
            "location": "ch008.md 第3段"
        }
    ],
    "strengths": ["本章结尾钩子有效", "张力较强"],
    "revision_required": True,
    "requires_human_decision": False,
    "risk_level": "medium"
}
```

**prompt 模板来源**：`roles/editor.md`

---

### World.execute(task_type, world_context)

**职责**：处理设定变更，检测冲突。

**输入 context**：
```python
{
    "task_type": "add_character",
    "change_request": {
        "type": "add_character",
        "summary": "新增一个控制北境补给线的地下组织"
    },
    "world_text": "...",
    "existing_indexes": {
        "characters": [...],
        "locations": [...],
        "factions": [...],
        "world_rules": [...]
    }
}
```

**输出**：
```python
{
    "change_type": "add_character",
    "proposed_updates": [
        {"target_file": "world.md", "summary": "新增'赤岸会'势力说明"}
    ],
    "new_entities": {
        "factions": [{"id": "faction_chianhui", "name": "赤岸会", "summary": "..."}]
    },
    "conflicts_found": [],
    "requires_human_decision": False
}
```

**prompt 模板来源**：`roles/world.md`

---

## 完整工作流执行

### write_chapter 完整流程

```python
def run_write_chapter(chapter: str, project_path: str) -> dict:
    # 1. Supervisor 初始判断
    supervisor_out = Supervisor.execute("write_chapter", {
        "user_request": f"写第{chapter}章",
        "project_path": project_path,
        "current_chapter": prev_chapter(project_path),
        "config": load_yaml(f"{project_path}/config/writing.yaml")
    })
    
    # 2. Planner 生成 mini plan
    planner_out = Planner.execute("plan_chapter", supervisor_out["planner_context"])
    
    # 3. Writer 写草稿
    writer_out = Writer.execute("write_chapter", {
        **supervisor_out["planner_context"],
        "plan": planner_out
    })
    
    # 4. Editor 审稿
    editor_out = Editor.execute("review_chapter", {
        **supervisor_out["planner_context"],
        "draft_text": writer_out["draft_text"],
        "chapter_summary": writer_out["chapter_summary"]
    })
    
    # 5. Supervisor 分流
    if editor_out["verdict"] == "passed":
        return {"status": "done", "draft": writer_out, "verdict": editor_out}
    elif editor_out["requires_human_decision"]:
        return {"status": "waiting_human", "issues": editor_out["issues"]}
    else:
        # revision loop
        ...
```

---

## OpenClaw 中的调用方式

在 OpenClaw skill 中，不需要真的写 Python 脚本。
只需要在 SKILL.md 中指示 agent：

```
当用户说"写第X章"时：
1. 读取 config/writing.yaml → 确认字数要求
2. 读取 roles/supervisor.md → 作为 Supervisor 的行为指导
3. 读取 roles/planner.md → 生成章节计划
4. 读取 roles/writer.md → 写正文
5. 读取 roles/editor.md → 审稿
6. 根据 verdict 决定：交付 / 打回修订 / 暂停等确认
```

---

## prompt 注入方式

```python
def build_role_prompt(role: str, task_context: dict) -> str:
    """为指定角色构建完整的 prompt"""
    role_template = Path(f"roles/{role.lower()}.md").read_text()
    
    # 将 role_template 中的变量占位符替换为 task_context
    prompt = role_template
    
    for key, value in task_context.items():
        prompt = prompt.replace(f"{{{key}}}", str(value))
    
    return prompt
```
