# scripts/ — 工具脚本

> novel-agent 的工具脚本集合，提供索引构建、工作流管理、一致性检查等能力。
> **所有脚本无需数据库，直接文件系统操作。**

---

## 必需脚本（核心）

| 脚本 | 用途 |
|------|------|
| `build_index.py` | 扫描小说项目，生成初始结构化索引 |
| `incremental_index_update.py` | 增量更新索引（章节/伏笔/角色/地点/时间线） |
| `workflow_state.py` |管理工作流状态（启动/推进/完成/等待决策） |
| `novel_agent.py` | 顶层执行器，封装常用命令 |

---

## 辅助脚本

| 脚本 | 用途 |
|------|------|
| `consistency_check.py` | 一致性检查（角色/武器/时间线） |
| `beat_tracker.py` | 伏笔追踪检查（逾期警告） |
| `context_compressor.py` | 上下文压缩（防止窗口溢出） |
| `outline_generator.py` | 大纲生成（根据叙事框架生成分卷骨架） |

---

## 演示脚本

| 脚本 | 用途 |
|------|------|
| `run_demo.py` | 一键演示完整工作流（初始化→构建索引→工作流→更新） |

运行：`python scripts/run_demo.py`

---

## 使用方式

```bash
# 构建初始索引
python scripts/build_index.py ./my-novel

# 查看项目状态
python scripts/workflow_state.py ./my-novel status

# 运行伏笔检查
python scripts/beat_tracker.py ./my-novel 50
```

---

## 依赖

- Python 3.7+
- PyYAML（用于 build_index.py）

安装依赖：`pip install pyyaml`
