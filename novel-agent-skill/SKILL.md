# novel-agent OpenClaw Skill

> 本 skill 是 novel-agent 在 OpenClaw 环境下的执行层。
> 它不是平台入口（那是 SKILL.md），而是**工作流的实际执行协议**。

---

## 工作原理

OpenClaw agent 读取本 skill 后，按照以下流程工作：

```
用户请求
  ↓
读取 AGENT.md（核心定义）
  ↓
按 roles/*.md 中的模板执行对应角色
  ↓
通过 scripts/workflow_state.py 记录状态
  ↓
通过 scripts/incremental_index_update.py 更新索引
  ↓
交付结果
```

---

## 快速执行命令

### 写章节（完整流程）

```
1. 读取 config/writing.yaml 确认字数要求
2. 读取 index/chapters.json 确认当前写到了哪章
3. 读取 beats 索引确认待推进伏笔
4. 按 roles/planner.md 执行 Planner → 输出 mini plan
5. 按 roles/writer.md 执行 Writer → 输出草稿
6. 按 roles/editor.md 执行 Editor → 输出 verdict
7. 根据 verdict：
   - passed → 更新 index/chapters.json + beats.jsonl → 通知用户
   - warning → 打回 Writer → 重新 Editor
   - requires_human → 生成决策卡片 → 等用户确认
```

### 审章节

```
1. 按 roles/editor.md 执行 Editor → 输出 verdict + issues
2. 返回审稿报告给用户
3. 如用户同意修订 → 派给 Writer → revise → 再审
```

### 查询（如"角色出现在哪"）

```
1. 优先读取 index/characters.json
2. 必要时读取 characters/*.md
3. 返回答案
```

---

## 脚本工具

| 场景 | 命令 |
|------|------|
| 初始化项目索引 | `python scripts/build_index.py <workspace>` |
| 更新章节索引 | `python scripts/incremental_index_update.py <workspace> update_chapter chXXX --status draft --summary "..."` |
| 新增伏笔 | `python scripts/incremental_index_update.py <workspace> add_beat beat_XXX --type foreshadow --description "..." --planted_in chXXX` |
| 更新伏笔状态 | `python scripts/incremental_index_update.py <workspace> update_beat beat_XXX --status resolved --actual_payoff chXXX` |
| 启动工作流 | `python scripts/workflow_state.py <workspace> start <workflow> <task_id> --workflow write_chapter` |
| 推进工作流 | `python scripts/workflow_state.py <workspace> advance --next_role Writer` |
| 标记等待决策 | `python scripts/workflow_state.py <workspace> waiting` |
| 查看状态 | `python scripts/workflow_state.py <workspace> status` |

---

## 索引读取优先级

当需要了解项目状态时，**先读索引，再读正文**：

1. `index/chapters.json` — 有哪些章节、状态、摘要
2. `index/characters.json` — 有哪些角色、状态、出场
3. `index/beats.jsonl` — 伏笔状态（取最新行）
4. `index/locations.json` — 地点列表
5. `index/timeline.jsonl` — 最近事件
6. 最后才读正文文件

---

## 决策点处理

遇到 `requires_human` 的情况：

1. 生成结构化决策卡片（见 AGENT.md 第三节）
2. 写入 `index/decisions.jsonl`（状态：`waiting_human`）
3. 展示给用户，等待选择
4. 用户决策后，更新 decisions.jsonl（状态：`resolved`）
5. 恢复工作流

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 写作字数不足 | 打回 Writer 补充 |
| 一致性冲突 | Editor 列出冲突项，等修正 |
| 脚本执行失败 | 记录到 `.learnings/ERRORS.md`，尝试降级 |
| 上下文超限 | 触发 `context_compressor.py` |
