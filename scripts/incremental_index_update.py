#!/usr/bin/env python3
# incremental_index_update.py
# 小说 Agent 增量索引更新脚本
# 用途：章节写完后，自动更新相关索引文件

import os
import re
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# 使用说明
# ─────────────────────────────────────────────────────────────
# 运行方式：python incremental_index_update.py <路径/to/workspace> <操作> [参数]
#
# 示例：
#   # 更新 chapters 索引（章节写完后）
#   python incremental_index_update.py ./my-novel update_chapter ch008 --file chapters/ch008.md
#
#   # 更新 beats 索引（新增伏笔）
#   python incremental_index_update.py ./my-novel add_beat beat_055 --type foreshadow --description "..."
#
#   # 更新 characters 索引（角色状态变化）
#   python incremental_index_update.py ./my-novel update_character char_chenmo --status injured
#
#   # 全量刷新（基于现有文件）
#   python incremental_index_update.py ./my-novel rebuild
# ─────────────────────────────────────────────────────────────

INDEX_DIR = 'index'

def load_jsonl(path):
    """读取 JSONL 文件，返回 {id: latest_entry}"""
    result = {}
    if not os.path.exists(path):
        return result
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                result[entry.get('id', '')] = entry
            except:
                continue
    return result

def save_jsonl(path, entries):
    """保存为 JSONL（所有行重写）"""
    with open(path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def load_json(path):
    """读取 JSON 文件"""
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    """保存 JSON 文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_word_count(content):
    """估算字数"""
    text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'[#*_~\[\]]', '', text)
    return len(text.strip())

def extract_title(content, fallback):
    """提取章节标题"""
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return fallback

def extract_chapter_num(filename):
    """从文件名提取章节号"""
    m = re.search(r'ch(\d+)', filename)
    return int(m.group(1)) if m else 0

# ── 操作：update_chapter ──────────────────────────────────────

def cmd_update_chapter(workspace, args):
    """更新 chapters.json 中某章节的索引"""
    chapters_file = Path(workspace) / INDEX_DIR / 'chapters.json'
    chapters = load_json(chapters_file)
    
    # 找到该章节
    target = None
    for ch in chapters:
        if ch['id'] == args.chapter or ch['file'] == args.file:
            target = ch
            break
    
    if not target:
        print(f"[WARN] 章节 {args.chapter} 不在索引中，将新增")
        target = {
            'id': args.chapter,
            'file': args.file,
            'status': 'draft',
            'characters': [],
            'locations': [],
            'beats_advanced': [],
            'beats_planted': [],
            'previous_chapter': None,
            'next_chapter': None,
            'review_status': 'pending',
            'risk_level': 'low'
        }
        chapters.append(target)
    
    # 更新字段
    target['status'] = args.status or target.get('status', 'draft')
    target['word_count'] = args.word_count or target.get('word_count', 0)
    target['summary'] = args.summary or target.get('summary', '')
    target['title'] = args.title or target.get('title', '')
    target['updated_at'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    if args.review_status:
        target['review_status'] = args.review_status
    if args.risk_level:
        target['risk_level'] = args.risk_level
    
    # 按章节号排序
    chapters.sort(key=lambda x: extract_chapter_num(x['id']))
    
    # 重建 previous_chapter / next_chapter 链
    for i, ch in enumerate(chapters):
        ch['previous_chapter'] = chapters[i-1]['id'] if i > 0 else None
        ch['next_chapter'] = chapters[i+1]['id'] if i < len(chapters)-1 else None
    
    save_json(chapters_file, chapters)
    print(f"[OK] chapters.json 已更新: {args.chapter}")

# ── 操作：add_beat ────────────────────────────────────────────

def cmd_add_beat(workspace, args):
    """新增一条伏笔到 beats.jsonl"""
    beats_file = Path(workspace) / INDEX_DIR / 'beats.jsonl'
    beats = load_jsonl(beats_file)
    
    beat_id = args.beat_id or f"beat_{len(beats)+1:03d}"
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    entry = {
        "id": beat_id,
        "type": args.type or "foreshadow",
        "description": args.description or "",
        "status": "pending",
        "planted_in": args.planted_in or "ch001",
        "planned_payoff": args.planned_payoff,
        "actual_payoff": None,
        "related_characters": args.characters or [],
        "related_locations": args.locations or [],
        "priority": args.priority or "medium",
        "notes": "",
        "updated_at": now
    }
    
    beats[beat_id] = entry
    
    with open(beats_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"[OK] 新增伏笔: {beat_id}")

# ── 操作：update_beat ─────────────────────────────────────────

def cmd_update_beat(workspace, args):
    """更新伏笔状态"""
    beats_file = Path(workspace) / INDEX_DIR / 'beats.jsonl'
    beats = load_jsonl(beats_file)
    
    if args.beat_id not in beats:
        print(f"[ERROR] 伏笔不存在: {args.beat_id}")
        sys.exit(1)
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    entry = beats[args.beat_id].copy()
    
    if args.status:
        entry['status'] = args.status
    if args.planned_payoff is not None:
        entry['planned_payoff'] = args.planned_payoff
    if args.actual_payoff is not None:
        entry['actual_payoff'] = args.actual_payoff
    if args.notes:
        entry['notes'] = args.notes
    
    entry['updated_at'] = now
    
    # 追加新行
    with open(beats_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"[OK] 伏笔已更新: {args.beat_id} → {entry['status']}")

# ── 操作：update_character ─────────────────────────────────────

def cmd_update_character(workspace, args):
    """更新角色状态"""
    chars_file = Path(workspace) / INDEX_DIR / 'characters.json'
    chars = load_json(chars_file)
    
    target = None
    for c in chars:
        if c['id'] == args.char_id:
            target = c
            break
    
    if not target:
        print(f"[ERROR] 角色不存在: {args.char_id}")
        sys.exit(1)
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    if args.status:
        target['status'] = args.status
    if args.last_appearance:
        target['last_appearance'] = args.last_appearance
    if args.summary:
        target['summary'] = args.summary
    
    target['updated_at'] = now
    
    save_json(chars_file, chars)
    print(f"[OK] 角色已更新: {args.char_id} → {target.get('status')}")

# ── 操作：add_location ────────────────────────────────────────

def cmd_add_location(workspace, args):
    """新增地点"""
    locs_file = Path(workspace) / INDEX_DIR / 'locations.json'
    locs = load_json(locs_file)
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    entry = {
        "id": args.loc_id,
        "name": args.name,
        "aliases": args.aliases or [],
        "kind": args.kind or "unknown",
        "region": args.region,
        "file": args.source_file or "world.md",
        "first_appearance": args.first_appearance or "ch001",
        "last_appearance": args.last_appearance or args.first_appearance or "ch001",
        "summary": args.summary or "",
        "tags": args.tags or [],
        "updated_at": now
    }
    
    # 检查是否已存在
    for i, loc in enumerate(locs):
        if loc['id'] == args.loc_id:
            locs[i] = entry
            save_json(locs_file, locs)
            print(f"[OK] 地点已更新: {args.loc_id}")
            return
    
    locs.append(entry)
    save_json(locs_file, locs)
    print(f"[OK] 新增地点: {args.loc_id}")

# ── 操作：add_timeline_event ──────────────────────────────────

def cmd_add_timeline_event(workspace, args):
    """新增时间线事件"""
    tl_file = Path(workspace) / INDEX_DIR / 'timeline.jsonl'
    
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    entry = {
        "id": args.event_id,
        "chapter": args.chapter,
        "scene": args.scene or "sc01",
        "time_label": args.time_label or f"第{int(args.chapter[2:]):d}日",
        "absolute_day": args.absolute_day or int(args.chapter[2:]),
        "location": args.location,
        "participants": args.participants or [],
        "event_type": args.event_type or "other",
        "summary": args.summary or "",
        "knowledge_changes": args.knowledge_changes or [],
        "state_changes": args.state_changes or [],
        "source": args.source or f"chapters/{args.chapter}.md",
        "updated_at": now
    }
    
    with open(tl_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"[OK] 时间线事件已添加: {args.event_id}")

# ── 操作：rebuild ─────────────────────────────────────────────

def cmd_rebuild(workspace, args):
    """全量重建（调用 build_index.py）"""
    import subprocess
    script_path = Path(__file__).parent / 'build_index.py'
    result = subprocess.run(
        [sys.executable, str(script_path), workspace, '--output', str(Path(workspace) / INDEX_DIR)],
        capture_output=False
    )
    sys.exit(result.returncode)

# ── 主入口 ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("用法: python incremental_index_update.py <workspace> <command> [options]")
        print("命令: update_chapter, add_beat, update_beat, update_character, add_location, add_timeline_event, rebuild")
        print("示例: python incremental_index_update.py ./my-novel update_chapter ch008 --file chapters/ch008.md --status final")
        sys.exit(1)
    
    workspace = sys.argv[1]
    cmd = sys.argv[2]
    
    if not os.path.exists(workspace):
        print(f"[ERROR] 工作空间不存在: {workspace}")
        sys.exit(1)
    
    # 创建索引目录（如果不存在）
    idx_dir = Path(workspace) / INDEX_DIR
    idx_dir.mkdir(exist_ok=True)
    
    # 解析参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--chapter', help='章节ID，如 ch008')
    parser.add_argument('--file', help='文件路径，如 chapters/ch008.md')
    parser.add_argument('--status', help='状态')
    parser.add_argument('--word_count', type=int, help='字数')
    parser.add_argument('--summary', help='章节摘要')
    parser.add_argument('--title', help='章节标题')
    parser.add_argument('--review_status', help='审稿状态')
    parser.add_argument('--risk_level', help='风险等级')
    parser.add_argument('--beat_id', help='伏笔ID')
    parser.add_argument('--type', help='伏笔类型')
    parser.add_argument('--description', help='描述')
    parser.add_argument('--planted_in', help='埋入章节')
    parser.add_argument('--planned_payoff', help='计划回收章节')
    parser.add_argument('--actual_payoff', help='实际回收章节')
    parser.add_argument('--priority', help='优先级')
    parser.add_argument('--characters', nargs='+', help='关联角色ID')
    parser.add_argument('--locations', nargs='+', help='关联地点ID')
    parser.add_argument('--notes', help='备注')
    parser.add_argument('--char_id', help='角色ID')
    parser.add_argument('--last_appearance', help='最近出场章节')
    parser.add_argument('--loc_id', help='地点ID')
    parser.add_argument('--name', help='名称')
    parser.add_argument('--aliases', nargs='+', help='别名')
    parser.add_argument('--kind', help='地点类型')
    parser.add_argument('--region', help='区域')
    parser.add_argument('--source_file', help='来源文件')
    parser.add_argument('--first_appearance', help='首次出场')
    parser.add_argument('--tags', nargs='+', help='标签')
    parser.add_argument('--event_id', help='事件ID')
    parser.add_argument('--scene', help='场景')
    parser.add_argument('--time_label', help='时间标签')
    parser.add_argument('--absolute_day', type=int, help='绝对天数')
    parser.add_argument('--location', help='地点ID')
    parser.add_argument('--participants', nargs='+', help='参与者')
    parser.add_argument('--event_type', help='事件类型')
    parser.add_argument('--knowledge_changes', type=json.loads, help='知识变化 JSON')
    parser.add_argument('--state_changes', type=json.loads, help='状态变化 JSON')
    
    args = parser.parse_args(sys.argv[3:])
    
    if cmd == 'update_chapter':
        cmd_update_chapter(workspace, args)
    elif cmd == 'add_beat':
        cmd_add_beat(workspace, args)
    elif cmd == 'update_beat':
        cmd_update_beat(workspace, args)
    elif cmd == 'update_character':
        cmd_update_character(workspace, args)
    elif cmd == 'add_location':
        cmd_add_location(workspace, args)
    elif cmd == 'add_timeline_event':
        cmd_add_timeline_event(workspace, args)
    elif cmd == 'rebuild':
        cmd_rebuild(workspace, args)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
