# 项目配置 / Project Config

> 本目录存放 novel-agent 的框架级配置。
> **这些配置是项目无关的通用参数**，适用于任何小说项目。
> 不要在这里写任何具体小说内容（角色名、势力名、具体章节等）。

---

## config/project.yaml

项目基础信息。

```yaml
project:
  # 小说标题（用户填写，或由 Setup Wizard 写入）
  title: ""
  
  # 语言：zh-CN / en-US 等
  language: "zh-CN"
  
  # 题材：post-apocalyptic / urban-fantasy / xianxia / sci-fi 等
  genre: ""
  
  # 叙事框架：three_act / four_stage / event_driven
  narrative_framework: "three_act"
  
  # 默认自主程度：L1 / L2 / L3 / L4
  default_autonomy: "L2"
  
  # Agent 默认模型（可被 platforms.yaml 覆盖）
  default_model: ""

# 自主程度说明
# L1 全自动：Agent 全权决定，写完通知用户
# L2 半自动：日常写作 Agent 定，关键节点需确认
# L3 低自动：核心方向用户定，Agent 执行细节
# L4 纯辅助：用户说写什么，Agent 就写什么
```

---

## config/writing.yaml

写作执行规则。

```yaml
writing:
  # 每章最少字数
  min_words_per_chapter: 3000
  
  # 对话最大连续行数（超过则必须插入动作/心理/场景描写）
  max_consecutive_dialogue_lines: 5
  
  # 是否必须章节结尾钩子
  require_chapter_hook: true
  
  # 动作/心理/场景描写占比下限（建议 >= 40%）
  min_narrative_ratio: 0.4
  
  # 风格偏好文件路径（相对于 workspace 根目录）
  style_guide_path: "style_guide.md"

# 对话密度偏好（可选，用于报告生成）
# light: 对话占比 < 30%
# medium: 对话占比 30-50%
# heavy: 对话占比 > 50%
dialogue_density: "medium"
```

---

## config/validation.yaml

验证与检查规则。

```yaml
validation:
  # 是否启用一致性检查
  consistency_check: true
  
  # 是否启用伏笔追踪检查
  beat_tracking: true
  
  # 是否启用时间线检查
  timeline_check: false
  
  # 报告生成等级：off / light / standard / deep
  report_level: "light"
  
  # 风格审稿（目前为轻量，基于规则）
  style_review:
    enabled: false
    level: "light"
  
  # 风险检测
  risk_detection:
    enabled: true
    # 哪些情况下标记为高风险
    high_risk_types:
      - "character_death_major"
      - "main_plot_change"
      - "world_rule_change"
      - "foreshadowing_abandoned"

# 伏笔追踪规则
beats:
  # 逾期多少章后标记为 warning
  overdue_warning_threshold: 3
  # 逾期多少章后标记为 high_risk
  overdue_danger_threshold: 5
```

---

## config/platforms.yaml

多平台接入配置。

```yaml
platforms:
  # OpenClaw 平台
  openclaw:
    enabled: true
    # 入口文件（相对于 novel-agent 根目录）
    entry: "SKILL.md"
    # 核心文件
    core: "AGENT.md"
  
  # Claude Code / Claude CLI
  claude_code:
    enabled: true
    entry: "CLAUDE.md"
    core: "AGENT.md"
  
  # Codex / Cursor
  codex:
    enabled: true
    entry: "CLAUDE.md"  # 与 Claude Code 共用同一入口
    core: "AGENT.md"
  
  # API 模式（Web UI / 直接 API 调用）
  api_mode:
    enabled: true
    # server.js 是否启用
    server_enabled: true
    # 默认端口
    default_port: 8765
    # 默认 provider
    default_provider: "openai"
    # 默认模型
    default_model: "gpt-4"
```

---

## 配置读取优先级

当以下位置出现同一配置时，**后者覆盖前者**：

1. `config/*.yaml`（默认值）
2. 项目 workspace 根目录的 `novel-agent.yaml`（用户覆盖）
3. 环境变量 `NOVEL_AGENT_*`（运行时覆盖）

---

## 与 Setup Wizard 的关系

`SETUP_WIZARD.md` 引导用户填写的答案，会写入项目 workspace 的 `novel-agent.yaml`。

`config/` 里的文件是**框架默认值**，始终保持项目无关。
