# context_compressor.py
# 小说 Agent 通用上下文压缩脚本
# 用途：当 Agent 的上下文窗口接近上限时，压缩旧章节的详细内容，保留关键信息

import os
import re
import sys

# ─────────────────────────────────────────────────────────────
# 使用说明
# ─────────────────────────────────────────────────────────────
# 运行方式：python context_compressor.py <路径/to/workspace> [压缩到第N章]
# 示例：python context_compressor.py ./my-novel 30
#   将前30章压缩成摘要，保留关键信息
#
# 功能：
# 1. 读取已完成的章节（chapters/ 目录）
# 2. 为每个章节生成压缩摘要
# 3. 保存到 chapters/compressed/ 目录
# 4. 保留：核心事件、人物状态变化、伏笔埋入/回收、设定变更
# 5. 删除：详细描写、对话（保留关键对白）、场景细节
#
# 压缩比例：约 90%（5000字 → 500字摘要）
# ─────────────────────────────────────────────────────────────

def load_chapters(chapters_dir, up_to_chapter=None):
    """加载章节"""
    if not os.path.exists(chapters_dir):
        return []
    
    chapter_files = sorted([f for f in os.listdir(chapters_dir) if f.startswith('ch') and f.endswith('.md')])
    
    chapters = []
    for ch_file in chapter_files:
        # 提取章节号
        ch_num_match = re.match(r'ch(\d+)', ch_file)
        if not ch_num_match:
            continue
        
        ch_num = int(ch_num_match.group(1))
        
        if up_to_chapter and ch_num > up_to_chapter:
            break
        
        ch_path = os.path.join(chapters_dir, ch_file)
        try:
            with open(ch_path, 'r', encoding='utf-8') as f:
                content = f.read()
            chapters.append({
                'num': ch_num,
                'file': ch_file,
                'content': content
            })
        except Exception as e:
            print(f"[WARNING] 无法读取章节 {ch_file}: {e}")
    
    return chapters

def extract_chapter_title(content):
    """提取章节标题"""
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return title_match.group(1).strip() if title_match else "无标题"

def extract_key_events(content):
    """提取核心事件（用于摘要）"""
    events = []
    
    # 简化实现：查找关键句子
    # 实际使用时应该用 LLM 来做这件事，这里是 fallback 方案
    
    # 查找以特定关键词开头的句子（可能包含重要事件）
    key_patterns = [
        r'他/她/主角决定(.+?)。',
        r'突然(.+?)。',
        r'最后(.+?)。',
        r'结果(.+?)。',
        r'然而(.+?)。',
        r'就在这时(.+?)。',
    ]
    
    sentences = content.split('。')
    for sentence in sentences:
        for pattern in key_patterns:
            if re.search(pattern, sentence):
                events.append(sentence.strip())
                break
    
    return events[:5]  # 最多保留5个关键事件

def extract_character_changes(content):
    """提取人物状态变化"""
    changes = []
    
    # 查找人物死亡/加入/关系变化
    death_patterns = [
        r'(\w+)死了',
        r'(\w+)死了',
        r'(\w+)去世',
        r'(\w+)被杀了',
    ]
    
    join_patterns = [
        r'(\w+)加入了',
        r'(\w+)出现了',
        r'(\w+)登场',
    ]
    
    relation_patterns = [
        r'(\w+)和(\w+)的关系',
        r'(\w+)对(\w+)的态度',
    ]
    
    for pattern in death_patterns + join_patterns + relation_patterns:
        matches = re.findall(pattern, content)
        if matches:
            changes.append((pattern, matches))
    
    return changes

def extract_foreshadowing(content):
    """提取伏笔相关"""
    foreshadowing = []
    
    # 查找可能的伏笔句
    hint_patterns = [
        r'他/她似乎在隐藏什么',
        r'那时候他还不知道',
        r'后来证明',
        r'这个选择',
        r'伏笔',
    ]
    
    for pattern in hint_patterns:
        if re.search(pattern, content):
            foreshadowing.append(pattern)
    
    return foreshadowing

def extract_world_changes(content):
    """提取世界观/设定变更"""
    changes = []
    
    # 查找新设定提及
    patterns = [
        r'新增了(.+?)规则',
        r'发现(.+?)能力',
        r'(.+?)异能',
        r'(.+?)等级',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if len(str(match)) > 2:
                changes.append(str(match))
    
    return list(set(changes))[:3]

def compress_chapter(chapter):
    """压缩单个章节"""
    content = chapter['content']
    ch_num = chapter['num']
    title = extract_chapter_title(content)
    
    events = extract_key_events(content)
    char_changes = extract_character_changes(content)
    foreshadowing = extract_foreshadowing(content)
    world_changes = extract_world_changes(content)
    
    # 构建压缩摘要
    summary_lines = [
        f"# 第{ch_num}章压缩摘要",
        f"## 标题：{title}",
        f"## 原始字数：约{len(content)}字",
        "",
        "## 核心事件：",
    ]
    
    if events:
        for i, event in enumerate(events, 1):
            summary_lines.append(f"{i}. {event}")
    else:
        summary_lines.append("（无明显核心事件记录）")
    
    if char_changes:
        summary_lines.append("")
        summary_lines.append("## 人物变化：")
        for change in char_changes:
            summary_lines.append(f"- {change}")
    
    if foreshadowing:
        summary_lines.append("")
        summary_lines.append("## 伏笔标记：")
        for fs in foreshadowing:
            summary_lines.append(f"- {fs}")
    
    if world_changes:
        summary_lines.append("")
        summary_lines.append("## 设定变更：")
        for wc in world_changes:
            summary_lines.append(f"- {wc}")
    
    summary_lines.append("")
    summary_lines.append("## 详细正文：")
    summary_lines.append(f"（已压缩，原文保存在 chapters/{chapter['file']}）")
    
    return '\n'.join(summary_lines)

def main():
    if len(sys.argv) < 2:
        print("用法: python context_compressor.py <路径/to/workspace> [压缩到第N章]")
        print("示例: python context_compressor.py ./my-novel 30")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    up_to_chapter = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"=" * 50)
    print(f"小说 Agent 上下文压缩")
    print(f"检查路径: {workspace_path}")
    if up_to_chapter:
        print(f"压缩范围：ch001 - ch{up_to_chapter}")
    print(f"=" * 50)
    
    chapters_dir = os.path.join(workspace_path, 'chapters')
    
    if not os.path.exists(chapters_dir):
        print(f"[ERROR] 章节目录不存在: {chapters_dir}")
        sys.exit(1)
    
    # 加载章节
    chapters = load_chapters(chapters_dir, up_to_chapter)
    
    if not chapters:
        print("[INFO] 未找到章节文件")
        return
    
    print(f"找到 {len(chapters)} 个章节待压缩")
    
    # 创建压缩目录
    compressed_dir = os.path.join(chapters_dir, 'compressed')
    os.makedirs(compressed_dir, exist_ok=True)
    
    # 压缩每个章节
    for chapter in chapters:
        compressed = compress_chapter(chapter)
        output_file = f"ch{chapter['num']:03d}_summary.md"
        output_path = os.path.join(compressed_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(compressed)
        
        original_size = len(chapter['content'])
        compressed_size = len(compressed)
        ratio = (1 - compressed_size/original_size) * 100
        
        print(f"  ch{chapter['num']:03d}: {original_size}字 → {compressed_size}字（压缩{ratio:.1f}%）")
    
    print()
    print(f"✅ 压缩完成，共 {len(chapters)} 章")
    print(f"📁 压缩文件保存在: {compressed_dir}")
    print()
    print("💡 提示：压缩后，Agent 在加载上下文时应优先读取 compressed/ 目录的摘要文件，")
    print("   仅在需要时再读取原始正文。")

if __name__ == '__main__':
    main()
