# TODO.md — novel-agent 开发路线图

> 最后更新：2026-04-08

---

## v2 已完成 ✅

- [x] `AGENT.md` — 平台无关核心定义
- [x] `AGENT_EXEC.md` — 角色执行协调器规范
- [x] `SKILL.md` / `CLAUDE.md` — 薄适配层（完整工作流说明）
- [x] `config/` — 4个框架配置文件
- [x] `roles/` — 5个角色提示模板（supervisor/planner/writer/editor/world）
- [x] `index/` — 结构化索引 schema + 构建脚本
- [x] `scripts/` — 工作流状态机 + 增量更新脚本
- [x] `workspace-template/` — 完整用户模板（11个文件）
- [x] `SETUP_WIZARD.md` v2 — 对接新配置系统
- [x] `run_demo.py` — 工作流演示脚本
- [x] `docs/QUICKSTART.md` — 10分钟快速入门
- [x] `docs/UI_SPEC.md` — 浅色主题 UI 设计规格书
- [x] `web/index.html` — 浅色主题 v2.0（✅ 颜色变量替换 / ❌ 页面不完整）
- [x] GitHub push 记录：ae64bd2 / f57a3c1 / 0a5c18c / 168b564 / d00dc8a / de392f9

---

## 待完成（按优先级）

### 🔴 高优

- [ ] **实际项目验证 build_index.py**：在《末世·毒舌系统》小说项目上跑通，验证 schema 是否够用（当前 Python 环境 PATH 问题未解决）
- [ ] **真正接通 Agent 执行链路**：在 OpenClaw/Claude Code 中验证 supervisor→planner→writer→editor 链路是否 work，SKILL.md 和 CLAUDE.md 已写好，但未在实际写作场景测试
- [ ] **UI 页面补全（Phase 2）**：当前 web/index.html 只有浅色主题，但页面不完整：
  - ❌ 缺少"章节工作室"（Chapter Studio）— 选章节→看计划/草稿/信息的左右分栏布局
  - ❌ 缺少"决策中心"（Decision Center）— 决策卡片列表
  - ❌ 缺少"设置"（Settings）— 写作/审稿/自主级别/平台配置页面
  - ⚠️ 伏笔追踪还是简单表格，不是看板视图（Beat Board 看板是设计文档 MVP 页）
  - ⚠️ 章节工作室 Tab 逻辑未实现（switchStudioTab / loadStudio JS 函数缺失）

### 🟡 中优

- [ ] **`world_rules.json` 提取脚本**：从 `world.md` 真正提取 power_system / world_constraints / factions / key_items
- [ ] **Beat Board 看板视图**：伏笔追踪页从表格改为看板（Planted / Active / Due Soon / Overdue / Resolved / Abandoned 六列）
- [ ] **Timeline 可视化**：基于 `index/timeline.jsonl` 的事件时间线页面
- [ ] **docsify 文档站**：搭一个 GitHub Pages 文档站

### 🟢 低优

- [ ] **`context_compressor.py` 完善**：压缩旧章节摘要，降低 token 消耗
- [ ] **`outline_generator.py` 完善**：根据叙事框架生成分卷大纲
- [ ] **多语言支持**：英文 README / SKILL.md / CLAUDE.md
- [ ] **Python 环境修复**：让 `python` / `py` 命令在 PowerShell 中可用（PATH 问题）
- [ ] **API mode server 完善**：`server.js` REST API 补全（目前只有基础端点）

---

## v2 架构已确认的已知问题

| 问题 | 状态 |
|------|------|
| `build_index.py` Python PATH 问题 | 🔴 未解决 |
| `workflow_state.py` 全量重写 JSONL 会越来越长 | 🟡 已知，待优化 |
| `SKILL.md` 和 `novel-agent-skill/SKILL.md` 有重复内容 | 🟢 需去重 |
| UI 缺少 3 个页面（Studio / Decisions / Settings） | 🔴 高优 |
| Agent 执行链路未在实际环境验证 | 🔴 高优 |

---

## 用户验收标准（还差几步）

一个用户 clone 后，能在 10 分钟内完成：

1. [ ] 填写 Setup Wizard → 生成 `novel-agent.yaml`
2. [ ] 填写 `world.md` → 运行 `build_index.py` → 生成索引
3. [ ] 说"写第一章" → Agent 按链路完成（**链路未验证**）
4. [ ] 说"查一下伏笔状态" → 从 `beats.jsonl` 读取回答
5. [ ] 说"审一下第1章" → Editor 输出 verdict + issues
6. [ ] 打开 Web UI → 看仪表盘/伏笔/章节列表（**UI 页面不全**）
