# outline_generator.py
# 小说 Agent 通用大纲生成脚本
# 用途：根据用户选择的叙事框架，自动生成分卷/章节骨架

import os
import re
import sys

# ─────────────────────────────────────────────────────────────
# 使用说明
# ─────────────────────────────────────────────────────────────
# 运行方式：python outline_generator.py <路径/to/workspace> <框架类型>
# 示例：python outline_generator.py ./my-novel 三段式
#       python outline_generator.py ./my-novel 起承转合
#       python outline_generator.py ./my-novel 事件驱动
#
# 框架选项：
#   三段式     - 开局→发展→高潮
#   起承转合   - 起→承→转→合（循环）
#   事件驱动   - 关键事件为节点
# ─────────────────────────────────────────────────────────────

FRAMWORKS = {
    '三段式': {
        'volume_structure': """## 卷{N}：{卷名}

**核心主题**：{核心主题}
**章节范围**：ch{起始} - ch{结束}
**核心人物**：{核心人物}
**核心冲突**：{核心冲突}

### 开局（ch{起始}-ch{开局结束}）
**目标**：建立世界，引出人物，制造第一个钩子

| 章节 | 核心事件 | 预期字数 |
|------|---------|---------|
| ch{起始} | {开场事件} | 3000字 |
| ch{起始+1} | {事件2} | 3500字 |
| ch{起始+2} | {事件3} | 3500字 |

### 发展（ch{发展起始}-ch{发展结束}）
**目标**：冲突升级，支线展开，伏笔埋入

| 章节 | 核心事件 | 伏笔 |
|------|---------|------|
| ch{发展起始} | {事件} | B{伏笔号} |
| ... | ... | ... |

### 高潮（ch{高潮起始}-ch{结束}）
**目标**：所有积累的集中爆发

| 章节 | 核心事件 |
|------|---------|
| ch{高潮起始} | {高潮前奏} |
| ch{结束} | {最终高潮} |

### 本卷埋入的伏笔
- [ ] B{伏笔号}：{伏笔描述}
""",
        'chapter_note': """**章节规划备注**：
- 开局（前20%章节）：快速建置，节奏偏快
- 发展（中60%章节）：冲突升级，每10章一个小高潮
- 高潮（后20%章节）：集中爆发，节奏最强
"""
    },
    
    '起承转合': {
        'volume_structure': """## 卷{N}：{卷名}

**核心主题**：{核心主题}
**章节范围**：ch{起始} - ch{结束}

### 卷内起承转合节奏

| 阶段 | 起（ch{起始}) | 承（ch{承起始}) | 转（ch{转起始}) | 合（ch{合起始}) |
|------|--------------|----------------|----------------|----------------|
| 主要事件 | {起事件} | {承事件} | {转事件} | {合事件} |
| 情绪基调 | {起情绪} | {承情绪} | {转情绪} | {合情绪} |

### 每章起承转合循环

""",
        'chapter_note': """**章节规划备注**：
- 起：200字内进入场景，建立情绪
- 承：60%内容，推进事件
- 转：打破平衡，制造意外
- 合：情绪落点，承接下一章
- 下一章的"起"必须承接上一章的"合"
"""
    },
    
    '事件驱动': {
        'volume_structure': """## 卷{N}：{卷名}

**核心主题**：{核心主题}
**章节范围**：ch{起始} - ch{结束}
**事件密度**：{密度}（每N章1个核心事件）

### 卷内核心事件

| 事件序号 | 事件名称 | 触发章节 | 事件类型 | 核心人物 |
|---------|---------|---------|---------|---------|
| E{编号} | {事件名} | ch{章节} | 主线/支线 | {人物} |
| E{编号+1} | {事件名} | ch{章节} | 主线/支线 | {人物} |

### 事件串联逻辑

```
事件E{编号}的后果 → 触发事件E{编号+1}
事件E{编号}的揭示 → 让事件E{编号+2}的冲突升级
```

### 章节规划

| 章节 | 涉及事件 | 章节类型 | 预期字数 |
|------|---------|---------|---------|
| ch{起始} | E{编号} | 事件开头 | 3000字 |
| ... | ... | 事件发展 | ... |
| ch{某章} | E{编号+1} | 事件高潮 | 4000字 |
""",
        'chapter_note': """**章节规划备注**：
- 每个事件必须有触发→发展→高潮→后果
- 事件之间必须有逻辑串联
- 每个事件发生后主角必须有代价或收益
- 事件密度要符合预期，不能忽高忽低
"""
    }
}

def read_world_file(workspace_path):
    """读取世界观文件"""
    world_path = os.path.join(workspace_path, 'world.md')
    if not os.path.exists(world_path):
        return None
    try:
        with open(world_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def read_characters_file(workspace_path):
    """读取人物文件"""
    char_dir = os.path.join(workspace_path, 'characters')
    if not os.path.exists(char_dir):
        return None
    chars = {}
    for f in os.listdir(char_dir):
        if f.endswith('.md'):
            try:
                with open(os.path.join(char_dir, f), 'r', encoding='utf-8') as file:
                    chars[f] = file.read()
            except:
                pass
    return chars

def generate_volume(outline_dir, volume_num, framework, start_ch, end_ch, **kwargs):
    """生成单卷大纲"""
    fw = FRAMWORKS.get(framework)
    if not fw:
        print(f"[ERROR] 未知框架: {framework}")
        return None
    
    template = fw['volume_structure']
    
    # 计算章节分配
    total_chapters = end_ch - start_ch + 1
    
    if framework == '三段式':
        opening_end = start_ch + int(total_chapters * 0.2) - 1
        development_start = opening_end + 1
        development_end = start_ch + int(total_chapters * 0.8) - 1
        climax_start = development_end + 1
        
        params = {
            'N': volume_num,
            '卷名': kwargs.get('name', f'第{volume_num}卷'),
            '核心主题': kwargs.get('theme', ''),
            '起始': start_ch,
            '结束': end_ch,
            '核心人物': kwargs.get('characters', ''),
            '核心冲突': kwargs.get('conflict', ''),
            '开局结束': opening_end,
            '发展起始': development_start,
            '发展结束': development_end,
            '高潮起始': climax_start,
            '伏笔号': f'{volume_num:02d}01',
            '开场事件': kwargs.get('opening_event', ''),
            '事件2': '',
            '事件3': '',
            '事件': '',
            '高潮前奏': '',
            '最终高潮': '',
        }
    elif framework == '起承转合':
        quarter = total_chapters // 4
        params = {
            'N': volume_num,
            '卷名': kwargs.get('name', f'第{volume_num}卷'),
            '核心主题': kwargs.get('theme', ''),
            '起始': start_ch,
            '结束': end_ch,
            '起': start_ch,
            '承起始': start_ch + quarter,
            '转起始': start_ch + quarter * 2,
            '合起始': start_ch + quarter * 3,
            '起事件': kwargs.get('qi_event', ''),
            '承事件': kwargs.get('cheng_event', ''),
            '转事件': kwargs.get('zhuan_event', ''),
            '合事件': kwargs.get('he_event', ''),
            '起情绪': kwargs.get('qi_mood', ''),
            '承情绪': kwargs.get('cheng_mood', ''),
            '转情绪': kwargs.get('zhuan_mood', ''),
            '合情绪': kwargs.get('he_mood', ''),
        }
    elif framework == '事件驱动':
        params = {
            'N': volume_num,
            '卷名': kwargs.get('name', f'第{volume_num}卷'),
            '核心主题': kwargs.get('theme', ''),
            '起始': start_ch,
            '结束': end_ch,
            '密度': kwargs.get('density', '每10章'),
            '编号': volume_num * 10 + 1,
            '事件名': kwargs.get('event_name', ''),
            '章节': '',
            '人物': kwargs.get('event_characters', ''),
        }
    
    outline = template.format(**params)
    outline += '\n' + fw['chapter_note']
    
    return outline

def main():
    if len(sys.argv) < 3:
        print("用法: python outline_generator.py <路径/to/workspace> <框架> [卷数]")
        print("框架选项: 三段式 / 起承转合 / 事件驱动")
        print("示例: python outline_generator.py ./my-novel 三段式 3")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    framework = sys.argv[2]
    num_volumes = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    print(f"=" * 50)
    print(f"小说 Agent 大纲生成器")
    print(f"工作区: {workspace_path}")
    print(f"框架: {framework}")
    print(f"卷数: {num_volumes}")
    print(f"=" * 50)
    
    if framework not in FRAMWORKS:
        print(f"[ERROR] 不支持的框架: {framework}")
        print(f"支持的框架: {', '.join(FRAMWORKS.keys())}")
        sys.exit(1)
    
    # 读取现有设定
    world_content = read_world_file(workspace_path)
    chars_content = read_characters_file(workspace_path)
    
    # 计算每卷的章节分配（假设每卷30章）
    chapters_per_volume = 30
    
    outline_dir = os.path.join(workspace_path, 'outline', 'volumes')
    os.makedirs(outline_dir, exist_ok=True)
    
    all_outlines = []
    all_outlines.append(f"# 大纲总览\n")
    all_outlines.append(f"**框架**: {framework}\n")
    all_outlines.append(f"**总卷数**: {num_volumes}\n")
    all_outlines.append(f"**每卷章节数**: {chapters_per_volume}章\n")
    all_outlines.append(f"**总章节数**: {num_volumes * chapters_per_volume}章\n")
    all_outlines.append("")
    
    for i in range(1, num_volumes + 1):
        start_ch = (i - 1) * chapters_per_volume + 1
        end_ch = i * chapters_per_volume
        
        volume_outline = generate_volume(
            outline_dir, i, framework,
            start_ch, end_ch,
            name=f'第{i}卷（待命名）',
            theme='（待填写核心主题）',
            characters='（待填写核心人物）',
            conflict='（待填写核心冲突）',
        )
        
        if volume_outline:
            volume_file = os.path.join(outline_dir, f'volume_{i:02d}.md')
            with open(volume_file, 'w', encoding='utf-8') as f:
                f.write(volume_outline)
            
            all_outlines.append(f"## 卷{i}大纲 → `outline/volumes/volume_{i:02d}.md`")
            print(f"✅ 卷{i}大纲已生成: {volume_file}")
    
    # 生成总览文件
    index_file = os.path.join(workspace_path, 'outline', 'index.md')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_outlines))
    
    print()
    print(f"✅ 大纲生成完成！")
    print(f"📁 总览: {index_file}")
    print(f"📁 各卷大纲: {outline_dir}")
    print()
    print("💡 请打开各卷大纲文件，根据你的设定填写：")
    print("   - 卷名和核心主题")
    print("   - 核心人物")
    print("   - 核心冲突")
    print("   - 各章节的核心事件")

if __name__ == '__main__':
    main()
