# 安装到 Claude Code

> Claude Code / Claude for Desktop 用户专用指南

---

## 方式一：直接 clone（推荐）

```bash
# 在你的终端里
git clone https://github.com/novel-agent/novel-agent.git
cd novel-agent
claude
```

Claude Code 会自动读取项目中的 `CLAUDE.md` 文件，并进入小说写作模式。

---

## 方式二：已有项目？

如果你想给已有的写作项目加入 novel-agent：

```bash
# 在你的项目目录里
git clone https://github.com/novel-agent/novel-agent.git ../novel-agent-templates

# 复制模板到你的项目
cp ../novel-agent-templates/workspace-template/* ./your-novel/
cp ../novel-agent-templates/SKILL.md ./
cp ../novel-agent-templates/CLAUDE.md ./

# 然后删除 clone（不再需要）
rm -rf ../novel-agent-templates
```

---

## 首次配置

1. 在项目目录启动 Claude Code
2. 运行 `/project` 或直接说：「请帮我初始化小说设定」
3. 按照提示填写：
   - 书名、题材
   - 主角设定
   - 世界规则
   - 叙事框架
   - 自主程度

---

## 使用示例

```bash
# 启动
cd my-novel
claude

# 常用指令
/write chapter 3                    # 写第三章
/check consistency                  # 检查一致性
/check beats                        # 检查伏笔状态
/plan volume 2                      # 规划第二卷
/add character                      # 新增角色
```

---

## 不需要 Python

scripts（一致性检查、伏笔追踪等）是可选的。

如果你不需要这些功能，**不需要安装 Python**。

如果需要，在 macOS/Linux：

```bash
# 安装 Python 3.8+
python3 --version

# 运行检查
python3 scripts/consistency_check.py .
python3 scripts/beat_tracker.py . 30
```

---

## 验证安装

```bash
claude
# 然后说：「你好，请介绍一下你自己」
```

Claude Code 应该能识别项目中的 `CLAUDE.md`，并以小说 Agent 的身份响应。
