# 快速入门

> 10 分钟快速上手 novel-agent。

---

## 第一步：Clone

```bash
git clone https://github.com/huxiuzh-ops/huxiuzhi-novel-agent.git
cd huxiuzhi-novel-agent
```

---

## 第二步：创建你的小说项目

```bash
# 方式 1：用命令行工具初始化
python scripts/novel_agent.py ./my-novel init

# 方式 2：手动复制模板
mkdir my-novel
cp -r workspace-template/* my-novel/
```

---

## 第三步：填写你的小说配置

打开 `my-novel/novel-agent.yaml`，填写：

```yaml
project:
  title: "我的小说"           # 改成你的书名
  language: "zh-CN"
  genre: "末世"              # 改成你的题材
  narrative_framework: "three_act"  # three_act / 起承转合 / event_driven
  default_autonomy: "L2"     # L1-L4，越高越自主
```

---

## 第四步：填写世界观

打开 `my-novel/world.md`，回答这几个问题：

```
## 地理/世界构造
这个世界分几个区域？每个区域的特点是什么？

## 力量体系/超凡规则（如有）
这个世界有什么特殊能力？规则是什么？

## 主要势力
有哪些势力？它们之间是什么关系？

## 核心矛盾
故事的核心冲突是什么？
```

---

## 第五步：填写主角

打开 `my-novel/characters/protagonist.md`，填写：
- 姓名、年龄、外貌、性格
- 核心目标/动机
- 背景故事

---

## 第六步：生成初始索引

```bash
python scripts/build_index.py ./my-novel
```

这会生成 `my-novel/index/` 下的所有结构化索引。

---

## 第七步：开始写作

### 在 OpenClaw 中

打开 `my-novel/` 作为 workspace，对 Agent 说：

```
你好，我的小说 Agent，帮我写第一章
```

### 在 Claude Code 中

```bash
cd my-novel
claude
```

然后说：

```
你好，帮我写第一章
```

### 直接命令行（不需要 Agent 环境）

```bash
python scripts/novel_agent.py ./my-novel write-chapter ch001
```

这会打印出完整的工作流步骤，你可以手动按步骤执行。

---

## 第八步：查看结果

写完第一章后：

```bash
# 查看项目状态
python scripts/novel_agent.py ./my-novel status

# 查看章节列表
python scripts/novel_agent.py ./my-novel query chapter ch001

# 查看伏笔状态
python scripts/novel_agent.py ./my-novel query beat beat_001
```

---

## 常用命令速查

| 任务 | 命令 |
|------|------|
| 初始化项目 | `python scripts/novel_agent.py ./my-novel init` |
| 构建索引 | `python scripts/build_index.py ./my-novel` |
| 重建索引 | `python scripts/incremental_index_update.py ./my-novel rebuild` |
| 查看状态 | `python scripts/workflow_state.py ./my-novel status` |
| 查看项目 | `python scripts/novel_agent.py ./my-novel status` |
| 更新章节索引 | `python scripts/incremental_index_update.py ./my-novel update_chapter ch001 --status final` |
| 新增伏笔 | `python scripts/incremental_index_update.py ./my-novel add_beat beat_001 --type foreshadow --description "..." --planted_in ch001` |
| 审稿 | `python scripts/beat_tracker.py ./my-novel 1` |
| 一致性检查 | `python scripts/consistency_check.py ./my-novel` |
| 运行演示 | `python scripts/run_demo.py` |

---

## 写作流程

```
你："写第一章"
    ↓
Supervisor（接收请求，判断任务类型）
    ↓
Planner（生成章节 mini plan）
    ↓
Writer（根据 plan 写正文）
    ↓
Editor（审稿，检查一致性和伏笔）
    ↓
Supervisor（根据 verdict 分流）
    ├─ 通过 → 更新索引 → 交付给你
    ├─ 小问题 → 打回 Writer 修订
    └─ 重大问题 → 暂停，等你确认
```

---

## 遇到问题？

1. **Agent 不按流程走？** — 检查 `AGENT.md` 是否被正确加载
2. **索引生成失败？** — 检查 `world.md` 和 `characters/` 是否非空
3. **脚本报错？** — 需要 Python 3.7+ 和 PyYAML：`pip install pyyaml`

更多文档：
- [README.md](README.md) — 项目整体介绍
- [SETUP_WIZARD.md](SETUP_WIZARD.md) — 完整初始化指南
- [docs/](docs/) — 各平台安装说明
