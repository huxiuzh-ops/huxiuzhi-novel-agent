# novel-agent UI 浅色主题 — 设计规格书

## 目标
将 `web/index.html` 从深色主题改为浅色主题，保留全部交互逻辑，仅修改 CSS 颜色系统。

---

## 设计语言

**风格**: 浅色工具型界面，类似 Linear / Notion / Craft
**主色**: `#5B4FDD`（紫蓝）
**强调色**: `#16A34A`（绿）、`#D97706`（橙）、`#DC2626`（红）
**背景**: `#F5F5F7`（浅灰）
**卡片**: `#FFFFFF`
**边框**: `#E5E5EA`
**文字**: `#1A1A1E`（主）、`#8E8E93`（次）
**字体**: Inter（正文） + JetBrains Mono（代码/数字）

---

## 颜色变量（CSS Variables）

```css
:root {
  --primary:       #5B4FDD;
  --primary-dim:   #4338CA;
  --primary-light: rgba(91,79,221,0.07);
  --primary-border:rgba(91,79,221,0.18);

  --green:        #16A34A;
  --green-light:  #F0FDF4;
  --green-border: #86EFAC;

  --yellow:       #D97706;
  --yellow-light: #FFFBEB;
  --yellow-border:#FDE68A;

  --red:          #DC2626;
  --red-light:    #FEF2F2;
  --red-border:   #FECACA;

  --purple:       #7C3AED;
  --purple-light: #F5F3FF;
  --purple-border:#DDD6FE;

  --bg:           #F5F5F7;
  --surface:      #FFFFFF;
  --card:         #FFFFFF;
  --border:       #E5E5EA;
  --border-bright:#D1D1D6;

  --text:         #1A1A1E;
  --text-secondary:#3C3C43;
  --text-muted:   #8E8E93;
  --text-placeholder:#C7C7CC;
}
```

---

## 页面结构（9个页面）

### 1. 仪表盘（Dashboard）
- 顶部 Hero 区域：渐变背景 `#F8F7FF → #EEF6FF`，紫色边框，标题 + 描述 + 快捷按钮
- 统计卡片区：4 列 grid，每卡片含标签（大写英文）、大数字（28px 紫色）、说明文字
- 双列区：左侧逾期伏笔列表，右侧最近章节列表
- 底部：知识图谱概览

### 2. 章节列表（Chapters）
- 刷新按钮 + cli 列表
- 每行：章节号（紫色等宽）、标题、字数

### 3. 章节工作室（Chapter Studio）
- **左栏（240px 宽）**：章节列表，可选中高亮
- **右栏**：顶部章节名 + 字数，3个 Tab（计划/草稿/信息）
  - 计划 Tab：plan-item 列表，每项含标签（大写英文）+ 内容
  - 草稿 Tab：textarea 编辑器
  - 信息 Tab：info-grid，key-value 网格

### 4. 伏笔追踪（Beats）
- 刷新 + 导出按钮
- 表格：ID（紫色标签）、类型、内容、埋入章节、计划章节、状态标签

### 5. 角色档案（Characters）
- 卡片 grid，每卡含角色名、角色类型标签（主角/反派/配角）、年龄、势力、状态

### 6. 世界设定（World）
- 单个 card，内含 world.md 渲染内容

### 7. 检查工具（Tools）
- 一致性检查 card：说明 + 运行按钮 + 输出区
- 伏笔追踪 card：同上
- 知识图谱 card：实体类型统计 grid

### 8. 决策中心（Decisions）
- 决策卡片列表，每卡含标题、元信息（类型/风险/章节）、操作按钮

### 9. 设置（Settings）
- 写作设置 card：数字输入、下拉选择、toggle 开关
- 审稿设置 card：toggle 开关 + 下拉
- 自主级别 card：下拉 + toggle
- 平台 card：两个下拉

---

## 组件样式

### 侧边栏
- 宽 220px，白色背景，右侧细边框
- Logo 区：紫色图标方块 + 文字
- 导航项：hover 浅灰，选中紫色背景 + 左侧紫色竖线
- 底部：v2.0

### 按钮
- 默认：白底 + 灰边框，hover 浅灰
- 主要（btn-p）：紫色背景，白字，hover 深紫
- 小尺寸：btn-sm

### Toggle 开关
- 40×22px，关闭灰色，开启紫色
- 右侧圆形滑块

### 状态标签（bg-*）
- 绿色：绿底绿字（已回收 / alive）
- 橙色：橙底橙字（待回收 / due soon）
- 红色：红底红字（逾期 / 已故 / high risk）
- 紫色：紫底紫字（主角）
- 粉色：粉底粉字（配角）

### 表格
- 表头：10px 大写字母，灰色，底部 2px 深灰边框
- 行 hover：浅灰背景

### Modal
- 半透明黑色遮罩（35% opacity）+ blur
- 白色圆角卡片，最大高度 85vh

---

## JS 交互逻辑（保持不变）
- `nav(p)` — 切换页面
- `loadDash()` — 拉取 /api/stats 填充统计卡片
- `loadChapters()` — 章节列表
- `loadStudio()` / `switchStudioTab()` — 章节工作室
- `loadBeats()` / `exportBeats()` — 伏笔追踪
- `loadChars()` — 角色档案
- `loadWorld()` / `loadStyle()` — 世界设定
- `runConsistency()` / `runBeats()` — 运行检查
- `loadTools()` / `loadDecisions()` — 工具和决策
- `toggle(el)` — 切换 toggle 状态
- `closeModal()` / `openChapter()` — 弹窗

API 端点：
- `GET /api/stats` → `{chapterCount, beatCount, charCount, overdueBeats, totalWords, resolvedBeats, activeChars}`
- `GET /api/chapters` → `[{num, title, file, words}]`
- `GET /api/beats` → `[{id, type, description, plantedChapter, plannedChapter, status}]`
- `GET /api/characters` → `[{name, role, age, faction, status}]`
- `GET /api/read?path=xxx` → 文件文本
- `GET /api/ontology` → `[{type, name, id}]`
- `GET /api/run?script=xxx` → 执行脚本返回文本

---

## 输出要求
- 单文件 `web/index.html`
- 全部 CSS 内联在 `<style>` 中
- 全部 JS 内联在 `<script>` 中
- Google Fonts CDN：Inter + JetBrains Mono
- 保留原有的全部 9 个 page div 和 JS 逻辑
- 仅修改 CSS 颜色变量和具体颜色值，从深色改为浅色
