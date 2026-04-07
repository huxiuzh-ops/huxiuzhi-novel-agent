# TODO.md — novel-agent 开发路线图

> 最后更新：2026-04-07（v2 架构重构完成后）

---

## v2 已完成 ✅

- [x] `AGENT.md` — 平台无关核心定义
- [x] `SKILL.md` / `CLAUDE.md` — 薄适配层
- [x] `config/` — 4个框架配置文件
- [x] `roles/` — 5个角色提示模板
- [x] `index/` — 结构化索引 schema + 构建脚本
- [x] `scripts/` — 工作流状态机 + 增量更新脚本
- [x] `workspace-template/` — 完整用户模板（11个文件）
- [x] `SETUP_WIZARD.md` v2 — 对接新配置系统
- [x] `run_demo.py` — 工作流演示脚本

---

## v3 待完成

### 高优

- [ ] **接通实际 Agent 执行**：把 `AGENT.md` + `roles/` 真正接进 OpenClaw/Claude Code 工作流——目前文件建好了，但还没有真正在写作时调用它们
- [ ] **接 `build_index.py` → 实际小说项目**：在真实小说项目上跑一次，验证 schema 是否够用
- [ ] **写一个快速入门文档**：5 分钟上手指南，让别人 clone 后能立刻跑起来

### 中优

- [ ] **`index/world_rules.json` 提取脚本**：`build_index.py` 目前只生成了 world_rules.json 占位符，需要从 `world.md` 真正提取 `power_system` / `world_constraints` / `factions` / `key_items`
- [ ] **`decisions.jsonl` 的人类决策 UI**：`Decision Center` 在 UI 设计文档里，但还没有实现
- [ ] **Timeline 可视化**：`index/timeline.jsonl` schema 建好了，但 UI 没有
- [ ] **Beat Board 看板 UI**：伏笔追踪页要有真正的看板视图

### 低优

- [ ] **`context_compressor.py` 完善**：现有的太基础，需要能压缩旧章节摘要
- [ ] **`outline_generator.py` 完善**：根据叙事框架生成分卷大纲
- [ ] **GitHub Pages 文档站**：用 docsify 或 Jekyll 搭一个文档站
- [ ] **多语言支持**：英文 README / SKILL.md / CLAUDE.md

---

## 已知的 schema 扩展方向（v4+）

- [ ] **角色关系图生成**：从 `world_rules.json` 的 factions 关系 + characters 生成可视化的势力关系图
- [ ] **章节时间线可视化**：基于 `timeline.jsonl` 的事件图
- [ ] **API mode server**：`server.js` 完善 REST API，接入 Web UI
- [ ] **embedding 语义检索**：给 `index/` 加语义层，支持"找类似情节"等高级查询

---

## 用户故事（验收标准）

一个用户 clone 后，能在 10 分钟内完成：

1. [ ] 填写 Setup Wizard → 生成 `novel-agent.yaml`
2. [ ] 填写 `world.md` → 运行 `build_index.py` → 生成索引
3. [ ] 说"写第一章" → Agent 按 `supervisor → planner → writer → editor` 链路完成
4. [ ] 说"查一下伏笔状态" → Agent 从 `beats.jsonl` 读取并回答
5. [ ] 说"审一下第1章" → Editor 角色输出 verdict + issues

---

## Bug / 问题

- `build_index.py` 对中文文件名处理可能有编码问题（Python path → 文件名需要更好的规范化）
- `workflow_state.py` 的 task 更新策略是全量重写，JSONL 会越来越长（v3 考虑用 append-only + 读时取最新）
- `SKILL.md` 和 `novel-agent-skill/SKILL.md` 有重复内容，需要去重
