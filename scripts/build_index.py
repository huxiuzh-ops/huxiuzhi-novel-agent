#!/usr/bin/env python3
# build_index.py
# 小说 Agent 结构化索引构建脚本
# 用途：从已有小说项目中提取信息，生成结构化索引

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 使用说明
# ─────────────────────────────────────────────────────────────
# 运行方式：python build_index.py <路径/to/workspace> [--output index/]
#
# 示例：
#   python build_index.py ./my-novel
#   python build_index.py ./my-novel --output ./index/
#
# 功能：
#   1. 扫描 world.md，提取世界规则 → world_rules.json
#   2. 扫描 characters/，生成 → characters.json
#   3. 扫描 chapters/，生成 → chapters.json
#   4. 读取 beats/TRACKING.md，生成 → beats.jsonl
#   5. 从 chapters/ 提取地点，生成 → locations.json
#   6. 从 chapters/ 提取事件，生成 → timeline.jsonl
#   7. 生成 → build-meta.json
# ─────────────────────────────────────────────────────────────

def load_file(path):
    """安全加载文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read(), path
    except FileNotFoundError:
        return None, path
    except Exception as e:
        print(f"[WARN] 无法读取 {path}: {e}")
        return None, path

def parse_frontmatter(content):
    """解析 Markdown YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            import yaml
            return yaml.safe_load(match.group(1)), content[len(match.group(0)):]
        except:
            return {}, content
    return {}, content

def extract_chapter_num(filename):
    """从文件名提取章节号，如 ch001 → 1"""
    m = re.search(r'ch(\d+)', filename)
    return int(m.group(1)) if m else 0

def extract_word_count(content):
    """估算章节字数"""
    # 去除 frontmatter、markdown 语法后统计
    text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'[#*_~\[\]]', '', text)
    return len(text.strip())

def extract_title(content, filename):
    """提取章节标题"""
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # fallback：从文件名提取
    name = Path(filename).stem
    m = re.search(r'ch(\d+)(?:_(.+))?', name)
    if m:
        return f"第{m.group(1)}章" + (f" · {m.group(2)}" if m.group(2) else "")
    return name

def build_characters_index(char_dir):
    """扫描 characters/ 目录，生成 characters.json"""
    result = []
    if not os.path.exists(char_dir):
        print(f"[WARN] characters/ 目录不存在")
        return result
    
    char_files = [f for f in os.listdir(char_dir) if f.endswith('.md')]
    
    for fname in char_files:
        fpath = os.path.join(char_dir, fname)
        content, _ = load_file(fpath)
        if not content:
            continue
        
        # 提取角色名（文件名作为 fallback）
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else Path(fname).stem
        
        # 提取 role
        role = "supporting"
        if re.search(r'(主角|protagonist)', content, re.IGNORECASE):
            role = "protagonist"
        elif re.search(r'(反派|antagonist)', content, re.IGNORECASE):
            role = "antagonist"
        elif re.search(r'(配角|supporting)', content, re.IGNORECASE):
            role = "supporting"
        
        # 提取 status
        status = "alive"
        if re.search(r'(死亡|dead|已死)', content, re.IGNORECASE):
            status = "dead"
        elif re.search(r'(失踪|missing)', content, re.IGNORECASE):
            status = "missing"
        elif re.search(r'(受伤|injured)', content, re.IGNORECASE):
            status = "injured"
        
        # 提取 age
        age = None
        age_m = re.search(r'(年龄|age)[：:]\s*(\d+)', content, re.IGNORECASE)
        if age_m:
            age = int(age_m.group(2))
        
        # 提取 first_appearance（从正文或文件内容推断）
        first_app = None
        ch_m = re.search(r'第[一二三四五六七八九十百\d]+章', content)
        if ch_m:
            ch_n = re.search(r'(\d+)', ch_m.group(0))
            if ch_n:
                first_app = f"ch{ch_n.group(1).zfill(3)}"
        
        # 生成 ID
        char_id = f"char_{Path(fname).stem.lower()}"
        
        entry = {
            "id": char_id,
            "name": name,
            "aliases": [],
            "file": f"characters/{fname}",
            "role": role,
            "faction": None,
            "status": status,
            "age": age,
            "gender": None,
            "first_appearance": first_app or "ch001",
            "last_appearance": first_app or "ch001",
            "tags": [],
            "summary": content[:200].replace('#', '').strip(),
            "importance": "core" if role == "protagonist" else "supporting",
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        }
        result.append(entry)
    
    return result

def build_chapters_index(chapters_dir):
    """扫描 chapters/ 目录，生成 chapters.json"""
    result = []
    if not os.path.exists(chapters_dir):
        print(f"[WARN] chapters/ 目录不存在")
        return result
    
    files = sorted(
        [f for f in os.listdir(chapters_dir) if f.endswith('.md')],
        key=lambda x: extract_chapter_num(x)
    )
    
    prev_ch = None
    for i, fname in enumerate(files):
        fpath = os.path.join(chapters_dir, fname)
        content, _ = load_file(fpath)
        if not content:
            continue
        
        ch_num = extract_chapter_num(fname)
        ch_id = f"ch{ch_num:03d}"
        
        # 提取正文中的角色提及
        chars_mentioned = re.findall(r'【([^】]+)】', content)
        
        entry = {
            "id": ch_id,
            "file": f"chapters/{fname}",
            "title": extract_title(content, fname),
            "status": "final" if i < len(files) - 1 else "draft",
            "word_count": extract_word_count(content),
            "summary": content[:200].replace('#', '').strip(),
            "volume": "vol01",
            "characters": chars_mentioned[:10],
            "locations": [],
            "beats_advanced": [],
            "beats_planted": [],
            "previous_chapter": prev_ch,
            "next_chapter": None,
            "review_status": "passed",
            "risk_level": "low",
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        }
        
        if i + 1 < len(files):
            next_num = extract_chapter_num(files[i + 1])
            entry["next_chapter"] = f"ch{next_num:03d}"
        
        result.append(entry)
        prev_ch = ch_id
    
    return result

def build_beats_index(beats_file):
    """读取 beats/TRACKING.md，生成 beats.jsonl"""
    result = []
    content, _ = load_file(beats_file)
    if not content:
        print(f"[WARN] beats/TRACKING.md 不存在或为空")
        return result
    
    lines = content.split('\n')
    in_table = False
    for line in lines:
        if '| ID |' in line or '|ID|' in line:
            in_table = True
            continue
        if not in_table:
            continue
        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c and c != '---']
        
        if len(cells) >= 6:
            beat_id = cells[0]
            beat_type = cells[1].lower()
            description = cells[2]
            planted_in = cells[3].strip()
            planned_payoff = cells[4].strip()
            status = cells[5].lower().strip()
            
            if not beat_id or beat_id.startswith('#'):
                continue
            
            entry = {
                "id": beat_id,
                "type": beat_type if beat_type in ["foreshadow", "mystery", "revelation", "plot_twist", "character_arc"] else "foreshadow",
                "description": description,
                "status": status if status in ["pending", "active", "due_soon", "overdue", "resolved", "abandoned"] else "pending",
                "planted_in": planted_in,
                "planned_payoff": planned_payoff if planned_payoff != '-' else None,
                "actual_payoff": None,
                "related_characters": [],
                "related_locations": [],
                "priority": "medium",
                "notes": "",
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
            }
            result.append(entry)
    
    return result

def build_locations_index(chapters_dir, world_file):
    """从章节内容中提取地点，生成 locations.json"""
    locations = {}
    
    # 先从 world.md 提取已知地点
    world_content, _ = load_file(world_file)
    if world_content:
        # 简单提取：寻找 "## 地点" 或 "## 地理" 下的内容
        loc_sections = re.findall(r'(?:地点|地理|区域)[:：]?\s*\n(.*?)(?=\n##|\Z)', world_content, re.DOTALL)
        for section in loc_sections:
            names = re.findall(r'[#*]?\s*【?([^\n【】#*]+)】?', section)
            for name in names[:10]:
                name = name.strip()
                if len(name) < 2:
                    continue
                loc_id = f"loc_{name[:4]}"
                locations[loc_id] = {
                    "id": loc_id,
                    "name": name,
                    "aliases": [],
                    "kind": "unknown",
                    "region": None,
                    "file": "world.md",
                    "first_appearance": None,
                    "last_appearance": None,
                    "summary": section[:100].strip(),
                    "tags": [],
                    "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
                }
    
    # 从章节中提取地点
    if os.path.exists(chapters_dir):
        chapter_files = sorted(
            [f for f in os.listdir(chapters_dir) if f.endswith('.md')],
            key=lambda x: extract_chapter_num(x)
        )
        
        for fname in chapter_files:
            ch_num = extract_chapter_num(fname)
            ch_id = f"ch{ch_num:03d}"
            fpath = os.path.join(chapters_dir, fname)
            content, _ = load_file(fpath)
            if not content:
                continue
            
            # 提取【地点】格式的地点
            locs = re.findall(r'【([^】]+)】', content)
            for loc_name in locs[:5]:
                loc_name = loc_name.strip()
                if len(loc_name) < 2:
                    continue
                loc_id = f"loc_{loc_name[:4]}"
                if loc_id not in locations:
                    locations[loc_id] = {
                        "id": loc_id,
                        "name": loc_name,
                        "aliases": [],
                        "kind": "unknown",
                        "region": None,
                        "file": f"chapters/{fname}",
                        "first_appearance": ch_id,
                        "last_appearance": ch_id,
                        "summary": "",
                        "tags": [],
                        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
                    }
                else:
                    if locations[loc_id]["first_appearance"] is None:
                        locations[loc_id]["first_appearance"] = ch_id
                    locations[loc_id]["last_appearance"] = ch_id
    
    return list(locations.values())

def build_timeline_index(chapters_dir):
    """从章节中提取事件，生成 timeline.jsonl"""
    result = []
    if not os.path.exists(chapters_dir):
        return result
    
    chapter_files = sorted(
        [f for f in os.listdir(chapters_dir) if f.endswith('.md')],
        key=lambda x: extract_chapter_num(x)
    )
    
    for fname in chapter_files:
        ch_num = extract_chapter_num(fname)
        ch_id = f"ch{ch_num:03d}"
        fpath = os.path.join(chapters_dir, fname)
        content, _ = load_file(fpath)
        if not content:
            continue
        
        # 按场景分割（以空行或【场景X】分割）
        scenes = re.split(r'\n\s*\n|\n【场景', content)
        
        for seq, scene in enumerate(scenes[:20], 1):
            if len(scene.strip()) < 50:
                continue
            
            scene_id = f"sc{seq:02d}"
            
            # 提取参与者
            participants = re.findall(r'【([^】]+)】', scene)
            participants = [p.strip() for p in participants if p.strip()]
            
            # 提取时间标签
            time_label = re.search(r'(第[一二三四五六七八九十百\d]+[天日])', scene)
            time_label = time_label.group(1) if time_label else f"第{ch_num}日"
            
            entry = {
                "id": f"evt_{ch_id}_{scene_id}_{seq:02d}",
                "chapter": ch_id,
                "scene": scene_id,
                "time_label": time_label,
                "absolute_day": ch_num,
                "location": None,
                "participants": participants,
                "event_type": "other",
                "summary": scene[:100].replace('#', '').strip(),
                "knowledge_changes": [],
                "state_changes": [],
                "source": f"chapters/{fname}",
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
            }
            result.append(entry)
    
    return result

def main():
    parser = argparse.ArgumentParser(description='构建小说项目结构化索引')
    parser.add_argument('workspace', help='小说项目路径')
    parser.add_argument('--output', default='index', help='索引输出目录（默认: index/）')
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    output_dir = Path(args.output)
    
    if not workspace.exists():
        print(f"[ERROR] 工作空间不存在: {workspace}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"=" * 50)
    print(f"novel-agent 结构化索引构建")
    print(f"工作空间: {workspace}")
    print(f"输出目录: {output_dir}")
    print(f"=" * 50)
    print()
    
    # 1. characters.json
    print("[1/7] 扫描 characters/ ...")
    chars = build_characters_index(workspace / 'characters')
    chars_file = output_dir / 'characters.json'
    with open(chars_file, 'w', encoding='utf-8') as f:
        json.dump(chars, f, ensure_ascii=False, indent=2)
    print(f"    → {chars_file} ({len(chars)} 条)")
    
    # 2. chapters.json
    print("[2/7] 扫描 chapters/ ...")
    chapters = build_chapters_index(workspace / 'chapters')
    chapters_file = output_dir / 'chapters.json'
    with open(chapters_file, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    print(f"    → {chapters_file} ({len(chapters)} 条)")
    
    # 3. beats.jsonl
    print("[3/7] 读取 beats/TRACKING.md ...")
    beats = build_beats_index(workspace / 'beats' / 'TRACKING.md')
    beats_file = output_dir / 'beats.jsonl'
    with open(beats_file, 'w', encoding='utf-8') as f:
        for beat in beats:
            f.write(json.dumps(beat, ensure_ascii=False) + '\n')
    print(f"    → {beats_file} ({len(beats)} 条)")
    
    # 4. locations.json
    print("[4/7] 提取地点 ...")
    locs = build_locations_index(workspace / 'chapters', workspace / 'world.md')
    locs_file = output_dir / 'locations.json'
    with open(locs_file, 'w', encoding='utf-8') as f:
        json.dump(locs, f, ensure_ascii=False, indent=2)
    print(f"    → {locs_file} ({len(locs)} 条)")
    
    # 5. timeline.jsonl
    print("[5/7] 提取时间线事件 ...")
    timeline = build_timeline_index(workspace / 'chapters')
    timeline_file = output_dir / 'timeline.jsonl'
    with open(timeline_file, 'w', encoding='utf-8') as f:
        for evt in timeline:
            f.write(json.dumps(evt, ensure_ascii=False) + '\n')
    print(f"    → {timeline_file} ({len(timeline)} 条)")
    
    # 6. world_rules.json (placeholder)
    print("[6/7] 生成 world_rules.json (占位) ...")
    world_rules_file = output_dir / 'world_rules.json'
    world_rules = {
        "power_system": [],
        "world_constraints": [],
        "factions": [],
        "key_items": [],
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    }
    with open(world_rules_file, 'w', encoding='utf-8') as f:
        json.dump(world_rules, f, ensure_ascii=False, indent=2)
    print(f"    → {world_rules_file} (需要 AI 辅助提取)")
    
    # 7. build-meta.json
    print("[7/7] 生成构建元数据 ...")
    meta_file = output_dir / 'build-meta.json'
    meta = {
        "built_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "source_workspace": str(workspace),
        "builder_version": "1.0.0",
        "indexes": {
            "characters": len(chars),
            "chapters": len(chapters),
            "beats": len(beats),
            "locations": len(locs),
            "timeline_events": len(timeline)
        }
    }
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"    → {meta_file}")
    
    print()
    print("✅ 索引构建完成！")
    print()
    print("下一步建议：")
    print("  1. 检查 index/ 目录下的文件，手动修正明显错误")
    print("  2. 运行 AI 辅助提取 world_rules.json（从 world.md 提取规则摘要）")
    print("  3. 在 AGENT.md 中启用索引优先的上下文装配策略")

if __name__ == '__main__':
    main()
