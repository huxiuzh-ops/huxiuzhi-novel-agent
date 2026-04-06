# 安装到 OpenClaw

> OpenClaw 用户专用指南

---

## 方式一：直接 clone（推荐）

```bash
# 找到你的 OpenClaw workspace 目录，通常是：
# C:\Users\<用户名>\.openclaw\workspace

# 克隆仓库到你的 workspace
git clone https://github.com/novel-agent/novel-agent.git ./my-novel

# 重命名（可选）
mv my-novel novel-agent
```

或者直接在 OpenClaw 的 web 界面里，点击"新建会话"并指向这个文件夹。

---

## 方式二：用 OpenClaw 的 skills 命令

```bash
# 如果 OpenClaw 支持 skills add
openclaw skills add https://github.com/novel-agent/novel-agent
```

---

## 首次配置

1. 用 OpenClaw 打开 `novel-agent` workspace
2. 对 Agent 说：「你好，我的小说Agent，请帮我初始化」
3. Agent 会引导你完成 Setup Wizard
4. 或者手动复制 `workspace-template/` 下的文件到你的小说目录

---

## 飞书通知配置（可选）

如果你想让 Agent 在章节完成后通过飞书通知你：

在 OpenClaw 配置中设置环境变量：

```bash
FEISHU_APP_ID=cli_xxxx
FEISHU_APP_SECRET=your_secret
FEISHU_NOTIFY_USER=ou_xxxx  # 你的飞书用户 ID
```

---

## 配置自主程度

在 Agent 对话里说：

「把自主程度设置成 L2 半自动」

---

## 定时写作任务

如果你想设置自动写作（比如每天早上 9 点写一章）：

```bash
# 对 Agent 说：
「请设置每天早上 9 点自动写一章」
```

Agent 会帮你配置好 cron 任务。

---

## 验证安装

说：「你好，小说Agent，请自我介绍一下」

Agent 应该能识别自己是小说写作助手，并说明当前小说的状态。
