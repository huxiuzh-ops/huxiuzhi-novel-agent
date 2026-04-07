#!/usr/bin/env python3
# novel_agent.py
# novel-agent 顶层执行器
# 用途：封装完整工作流，提供简单的命令行界面

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# 使用说明
# ─────────────────────────────────────────────────────────────
# 用法：python novel_agent.py <workspace> <command> [options]
#
# 示例：
#   python novel_agent.py ./my-novel init
#   python novel_agent.py ./my-novel write-chapter ch001
#   python novel_agent.py ./my-novel status
#   python novel_agent.py ./my-novel query-character char_chenmo
#
# 这个脚本是 workflows + index + state 的统一入口。
# 不需要数据库，不需要服务，直接文件系统。
# ─────────────────────────────────────────────────────────────

WORKSPACE_CONFIG = 'novel-agent.yaml'
INDEX_DIR = 'index'

def get_project_config(workspace):
    """读取项目配置（novel-agent.yaml），不存在则返回 None"""
    cfg_path = Path(workspace) / WORKSPACE_CONFIG
    if not cfg_path.exists():
        return None
    import yaml
    with open(cfg_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_yaml(path):
    """加载 YAML"""
    import yaml
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def cmd_init(workspace, args):
    """初始化项目：生成 novel-agent.yaml 和目录结构"""
    ws = Path(workspace)
    print(f"初始化项目: {ws}")

    # 目录
    dirs = ['characters', 'outline/volumes', 'beats', 'chapters', 'inventory', 'index', '.learnings', 'memory/ontology']
    for d in dirs:
        (ws / d).mkdir(parents=True, exist_ok=True)

    # 复制模板
    src = Path(__file__).parent.parent
    templates = [
        ('workspace-template/world_template.md', ws / 'world.md'),
        ('workspace-template/style_guide_template.md', ws / 'style_guide.md'),
        ('workspace-template/characters/protagonist_template.md', ws / 'characters/protagonist.md'),
        ('workspace-template/outline/structure_template.md', ws / 'outline/structure.md'),
        ('workspace-template/beats/tracking_template.md', ws / 'beats/TRACKING.md'),
    ]
    for src_f, dst_f in templates:
        if not dst_f.exists() and (src / src_f).exists():
            import shutil
            shutil.copy(src / src_f, dst_f)
            print(f"  复制: {src_f} → {dst_f}")

    print(f"\n✅ 初始化完成！")
    print(f"\n下一步：")
    print(f"  1. 编辑 {ws / 'world.md'} — 填写世界观")
    print(f"  2. 编辑 {ws / 'characters/protagonist.md'} — 填写主角")
    print(f"  3. 运行 python novel_agent.py {ws} build-index — 生成初始索引")
    print(f"  4. 运行 python novel_agent.py {ws} write-chapter ch001 — 写第一章")

def cmd_build_index(workspace, args):
    """运行索引构建"""
    sys.path.insert(0, str(Path(__file__).parent))
    from build_index import main as build_main
    sys.argv = ['build_index.py', workspace, '--output', str(Path(workspace) / INDEX_DIR)]
    build_main()

def cmd_write_chapter(workspace, args):
    """写章节（打印工作流指令，不是真的写正文）"""
    cfg = get_project_config(workspace)
    ch = args.chapter
    
    print(f"=" * 50)
    print(f"写章节工作流: {ch}")
    print(f"=" * 50)
    
    # 检查项目配置
    if not cfg:
        print(f"[WARN] 未找到 {WORKSPACE_CONFIG}，使用默认配置")
        cfg = {
            'writing': {'min_words_per_chapter': 3000, 'require_chapter_hook': True},
            'project': {'narrative_framework': 'three_act'}
        }
    
    print(f"\n[1] 读取 config/writing.yaml — 确认字数要求")
    print(f"    最少字数: {cfg.get('writing', {}).get('min_words_per_chapter', 3000)}")
    
    print(f"\n[2] 读取 index/chapters.json — 确认当前章节")
    ch_idx = Path(workspace) / INDEX_DIR / 'chapters.json'
    if ch_idx.exists():
        chapters = json.loads(open(ch_idx).read())
        print(f"    已有的章节: {len(chapters)} 个")
    else:
        print(f"    暂无索引，将从头构建")
    
    print(f"\n[3] 读取 beats 索引 — 确认待推进伏笔")
    beats_idx = Path(workspace) / INDEX_DIR / 'beats.jsonl'
    if beats_idx.exists():
        beats = {}
        for line in open(beats_idx):
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            beats[e['id']] = e
        pending = [b for b in beats.values() if b.get('status') in ('pending', 'active')]
        print(f"    待推进伏笔: {len(pending)} 个")
        for b in pending[:3]:
            print(f"      - {b['id']}: {b.get('description', '')[:40]}")
    else:
        print(f"    暂无伏笔索引")
    
    print(f"\n[4] 调用 Planner — 生成章节 mini plan")
    print(f"    → 读取 roles/planner.md 作为提示模板")
    print(f"    → Planner 输出: {ch} 的章节计划")
    
    print(f"\n[5] 调用 Writer — 写草稿")
    print(f"    → 读取 roles/writer.md 作为提示模板")
    print(f"    → Writer 输出: 草稿文本")
    
    print(f"\n[6] 调用 Editor — 审稿")
    print(f"    → 读取 roles/editor.md 作为提示模板")
    print(f"    → Editor 输出: verdict + issues")
    
    print(f"\n[7] 分流")
    print(f"    passed → 更新 index/chapters.json + beats.jsonl")
    print(f"    warning → 打回 Writer 修订")
    print(f"    requires_human → 生成决策卡片")
    
    print(f"\n[8] 更新索引")
    print(f"    python scripts/incremental_index_update.py {workspace} update_chapter {ch}")
    
    print(f"\n[9] 更新工作流状态")
    print(f"    python scripts/workflow_state.py {workspace} start write_chapter task_{ch}")
    print(f"    python scripts/workflow_state.py {workspace} advance")
    
    print(f"\n" + "=" * 50)
    print(f"提示: 以上是工作流步骤。")
    print(f"在 OpenClaw / Claude Code 中，读取 roles/*.md 执行对应角色即可。")
    print(f"=" * 50)

def cmd_status(workspace, args):
    """查看项目状态"""
    cfg = get_project_config(workspace)
    
    print(f"=" * 50)
    print(f"novel-agent 项目状态")
    print(f"=" * 50)
    
    if cfg:
        print(f"\n项目: {cfg.get('project', {}).get('title', '(未命名)')}")
        print(f"框架: {cfg.get('project', {}).get('narrative_framework', 'three_act')}")
        print(f"自主程度: {cfg.get('project', {}).get('default_autonomy', 'L2')}")
    else:
        print(f"\n未找到 {WORKSPACE_CONFIG}，尚未初始化")
    
    # 章节数
    ch_dir = Path(workspace) / 'chapters'
    if ch_dir.exists():
        ch_files = [f for f in os.listdir(ch_dir) if f.endswith('.md')]
        print(f"\n章节: {len(ch_files)} 个")
    
    # 索引
    idx_dir = Path(workspace) / INDEX_DIR
    if idx_dir.exists():
        for f in ['characters.json', 'chapters.json', 'beats.jsonl', 'locations.json']:
            fp = idx_dir / f
            if fp.exists():
                if f.endswith('.jsonl'):
                    lines = len(open(fp).readlines())
                    print(f"  {f}: {lines} 条")
                else:
                    data = json.loads(open(fp).read())
                    print(f"  {f}: {len(data)} 条")
    
    # 工作流状态
    wf_state = Path(workspace) / '.workflow' / 'state.json'
    if wf_state.exists():
        state = json.loads(open(wf_state).read())
        wf = state.get('current_workflow')
        if wf and wf.get('status') == 'running':
            print(f"\n运行中工作流: {wf['workflow']} ({wf['task_id']})")
            print(f"  当前角色: {wf['current_role']}")
        else:
            print(f"\n无运行中的工作流")
    else:
        print(f"\n无工作流记录")

def cmd_review_chapter(workspace, args):
    """审章节"""
    ch = args.chapter
    print(f"审章节: {ch}")
    print(f"\n调用 Editor — 读取 roles/editor.md")
    print(f"  → 输入: chapters/{ch}.md + index/*")
    print(f"  → Editor 输出: verdict + issues")

def cmd_add_character(workspace, args):
    """新增角色"""
    char_id = f"char_{args.name}"
    print(f"新增角色: {char_id}")
    print(f"\n调用 World — 读取 roles/world.md")
    print(f"  → 新增 characters/{args.name}.md")
    print(f"  → 更新 index/characters.json")
    print(f"  → 更新 index/decisions.jsonl（如需人类决策）")

def cmd_query(workspace, args):
    """查询"""
    target = args.target
    idx_dir = Path(workspace) / INDEX_DIR
    
    if args.type == 'character':
        print(f"查询角色: {target}")
        chars_file = idx_dir / 'characters.json'
        if chars_file.exists():
            chars = json.loads(open(chars_file).read())
            for c in chars:
                if c['id'] == target or c['name'] == target:
                    print(f"\n  ID: {c['id']}")
                    print(f"  名称: {c['name']}")
                    print(f"  角色: {c['role']}")
                    print(f"  状态: {c['status']}")
                    print(f"  出场: {c.get('first_appearance', '?')} - {c.get('last_appearance', '?')}")
                    print(f"  摘要: {c.get('summary', '')}")
                    return
        print(f"  未找到该角色")
    
    elif args.type == 'beat':
        print(f"查询伏笔: {target}")
        beats_file = idx_dir / 'beats.jsonl'
        if beats_file.exists():
            beats = {}
            for line in open(beats_file):
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                beats[e['id']] = e
            if target in beats:
                b = beats[target]
                print(f"\n  ID: {b['id']}")
                print(f"  类型: {b['type']}")
                print(f"  描述: {b['description']}")
                print(f"  状态: {b['status']}")
                print(f"  埋入: {b['planted_in']}")
                print(f"  计划回收: {b.get('planned_payoff', '?')}")
                return
        print(f"  未找到该伏笔")
    
    elif args.type == 'chapter':
        print(f"查询章节: {target}")
        chs_file = idx_dir / 'chapters.json'
        if chs_file.exists():
            chapters = json.loads(open(chs_file).read())
            for c in chapters:
                if c['id'] == target:
                    print(f"\n  ID: {c['id']}")
                    print(f"  标题: {c['title']}")
                    print(f"  状态: {c['status']}")
                    print(f"  字数: {c['word_count']}")
                    print(f"  摘要: {c['summary']}")
                    return
        print(f"  未找到该章节")

def main():
    if len(sys.argv) < 3:
        print("novel-agent 执行器")
        print()
        print("用法: python novel_agent.py <workspace> <command> [options]")
        print()
        print("命令:")
        print("  init <workspace>              初始化项目")
        print("  build-index <workspace>       构建初始索引")
        print("  write-chapter <chXXX>         打印写章节工作流")
        print("  review-chapter <chXXX>        打印审章节工作流")
        print("  add-character <name>          新增角色")
        print("  status                        查看项目状态")
        print("  query <type> <target>         查询角色/伏笔/章节")
        print()
        print("示例:")
        print("  python novel_agent.py ./my-novel init")
        print("  python novel_agent.py ./my-novel build-index")
        print("  python novel_agent.py ./my-novel write-chapter ch001")
        print("  python novel_agent.py ./my-novel status")
        print("  python novel_agent.py ./my-novel query character char_chenmo")
        sys.exit(1)
    
    workspace = sys.argv[1]
    if not os.path.exists(workspace):
        print(f"[ERROR] 工作空间不存在: {workspace}")
        sys.exit(1)
    
    cmd = sys.argv[2]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--chapter', help='章节ID')
    parser.add_argument('--name', help='角色名')
    parser.add_argument('--type', choices=['character', 'beat', 'chapter', 'location'], help='查询类型')
    parser.add_argument('--target', help='查询目标')
    args = parser.parse_args(sys.argv[3:])
    
    if cmd == 'init':
        cmd_init(workspace, args)
    elif cmd == 'build-index':
        cmd_build_index(workspace, args)
    elif cmd == 'write-chapter':
        if not args.chapter:
            print("[ERROR] 需要 --chapter 参数，如 ch001")
            sys.exit(1)
        cmd_write_chapter(workspace, args)
    elif cmd == 'review-chapter':
        if not args.chapter:
            print("[ERROR] 需要 --chapter 参数")
            sys.exit(1)
        cmd_review_chapter(workspace, args)
    elif cmd == 'add-character':
        if not args.name:
            print("[ERROR] 需要 --name 参数")
            sys.exit(1)
        cmd_add_character(workspace, args)
    elif cmd == 'status':
        cmd_status(workspace, args)
    elif cmd == 'query':
        if not args.type or not args.target:
            print("[ERROR] 需要 --type 和 --target")
            sys.exit(1)
        cmd_query(workspace, args)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
