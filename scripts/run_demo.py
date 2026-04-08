#!/usr/bin/env python3
# run_demo.py
# novel-agent 演示脚本
# 用途：不依赖任何外部 Agent 环境，纯粹用 Python 演示完整工作流

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

DEMO_DIR = Path(__file__).parent.parent / 'demo-novel'
SCRIPTS_DIR = Path(__file__).parent

YES_MODE = '--yes' in sys.argv
NO_CLEANUP = '--no-cleanup' in sys.argv or '--no_cleanup' in sys.argv

def c(text, color):
    colors = {
        'header': '\033[95m',
        'ok': '\033[92m',
        'warn': '\033[93m',
        'error': '\033[91m',
        'info': '\033[96m',
        'bold': '\033[1m',
        'end': '\033[0m',
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"

def header(text):
    print(f"\n{'='*60}")
    print(c(f"  {text}", 'header'))
    print(f"{'='*60}\n")

def step(text):
    print(c(f"  -> {text}", 'info'))

def ok(text):
    print(c(f"  OK {text}", 'ok'))

def warn(text):
    print(c(f"  WARN {text}", 'warn'))

def ask(prompt, default='y'):
    if YES_MODE:
        print(f"{prompt} {default}")
        return default
    if sys.stdin.isatty():
        return input(prompt).strip().lower() or default
    print(f"{prompt} {default}")
    return default

def check_dependencies():
    header("Step 0: 检查依赖")

    try:
        result = subprocess.run(
            ['python', '--version'],
            capture_output=True, text=True
        )
        ok(f"Python: {result.stdout.strip()}")
    except:
        warn("Python 未找到，请先安装 Python 3.7+")
        return False

    try:
        import yaml
        ok("PyYAML: 已安装")
    except ImportError:
        warn("PyYAML 未安装，运行: pip install pyyaml")

    return True

def init_demo_project():
    header("Step 1: 初始化演示项目")

    if DEMO_DIR.exists():
        warn(f"演示目录已存在: {DEMO_DIR}")
        response = ask("  是否删除重建？(y/N): ", 'n')
        if response == 'y':
            shutil.rmtree(DEMO_DIR)
            ok("已删除旧目录")
        else:
            print("  跳过初始化")
            return False

    step("创建目录结构...")
    dirs = [
        'characters', 'outline/volumes', 'beats',
        'chapters', 'inventory', 'index', '.learnings', 'memory/ontology'
    ]
    for d in dirs:
        (DEMO_DIR / d).mkdir(parents=True, exist_ok=True)

    step("复制 workspace-template...")
    template_dir = SCRIPTS_DIR.parent / 'workspace-template'

    files_to_copy = [
        ('world_template.md', 'world.md'),
        ('style_guide_template.md', 'style_guide.md'),
        ('outline/structure_template.md', 'outline/structure.md'),
        ('beats/tracking_template.md', 'beats/TRACKING.md'),
    ]

    for src_name, dst_name in files_to_copy:
        src = template_dir / src_name
        dst = DEMO_DIR / dst_name
        if src.exists():
            shutil.copy(src, dst)

    chars_src = template_dir / 'characters'
    chars_dst = DEMO_DIR / 'characters'
    if chars_src.exists():
        for f in chars_src.glob('*_template.md'):
            dst_f = chars_dst / f.name.replace('_template', '')
            shutil.copy(f, dst_f)

    ok(f"演示项目创建完成: {DEMO_DIR}")
    return True

def build_demo_index():
    header("Step 2: 生成初始索引")

    if not (DEMO_DIR / 'index').exists():
        (DEMO_DIR / 'index').mkdir(parents=True)

    step("运行 build_index.py...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'build_index.py'), str(DEMO_DIR)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(result.stdout)
            ok("索引构建完成")
        else:
            warn(f"索引构建有警告（可能是因为演示项目内容较少）")
            print(result.stdout)
    except FileNotFoundError:
        warn("build_index.py 未找到，跳过")
    except Exception as e:
        warn(f"索引构建出错: {e}")

    world_rules = {
        "power_system": [],
        "world_constraints": [
            {
                "id": "rule_demo_001",
                "title": "（演示用）这个世界有异能体系",
                "summary": "觉醒者分三级，代价是加速老化",
                "priority": "high"
            }
        ],
        "factions": [
            {
                "id": "faction_demo_001",
                "name": "（演示）安全区联盟",
                "summary": "人类最后的秩序之地"
            }
        ],
        "key_items": [],
        "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    }

    (DEMO_DIR / 'index' / 'world_rules.json').write_text(
        json.dumps(world_rules, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    ok("world_rules.json 生成完成")

def demo_workflow_state():
    header("Step 3: 演示工作流状态机")

    step("查看当前状态...")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / 'workflow_state.py'), str(DEMO_DIR), 'status'],
        capture_output=True, text=True
    )
    print(result.stdout)

    step("启动 write_chapter 工作流...")
    task_id = f"task_demo_{datetime.now().strftime('%H%M%S')}"
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'workflow_state.py'),
            str(DEMO_DIR), 'start', 'write_chapter', task_id,
            '--workflow', 'write_chapter',
            '--start_role', 'Planner'
        ],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        ok(f"工作流已启动: {task_id}")
    else:
        warn(f"工作流启动失败: {result.stderr}")

    step("推进到 Writer 角色...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'workflow_state.py'),
            str(DEMO_DIR), 'advance',
            '--next_role', 'Writer',
            '--output', 'chapters/ch001.md'
        ],
        capture_output=True, text=True
    )
    print(result.stdout)

    step("推进到 Editor 角色...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'workflow_state.py'),
            str(DEMO_DIR), 'advance',
            '--next_role', 'Editor'
        ],
        capture_output=True, text=True
    )
    print(result.stdout)

    step("标记等待人类决策（演示用）...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'workflow_state.py'),
            str(DEMO_DIR), 'waiting'
        ],
        capture_output=True, text=True
    )
    print(result.stdout)

    step("恢复工作流...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'workflow_state.py'),
            str(DEMO_DIR), 'resume',
            '--decision', 'A'
        ],
        capture_output=True, text=True
    )
    print(result.stdout)

    step("完成工作流...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'workflow_state.py'),
            str(DEMO_DIR), 'complete'
        ],
        capture_output=True, text=True
    )
    print(result.stdout)
    ok("工作流演示完成")

def demo_incremental_update():
    header("Step 4: 演示增量索引更新")

    step("更新章节状态...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'incremental_index_update.py'),
            str(DEMO_DIR), 'update_chapter', 'ch001',
            '--status', 'draft',
            '--word_count', '3850',
            '--title', '废墟微光',
            '--summary', '陈墨在废墟中拾荒，遭遇神秘女子，获得残缺地图。'
        ],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        ok("章节索引更新完成")
    else:
        warn(f"更新失败: {result.stderr}")

    step("新增一条伏笔...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'incremental_index_update.py'),
            str(DEMO_DIR), 'add_beat', 'beat_demo_001',
            '--type', 'foreshadow',
            '--description', '残缺地图背后指向军方实验设施',
            '--planted_in', 'ch001',
            '--planned_payoff', 'ch010',
            '--priority', 'high'
        ],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        ok("伏笔添加完成")

    step("新增地点...")
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / 'incremental_index_update.py'),
            str(DEMO_DIR), 'add_location', 'loc_yonghui',
            '--name', '永辉购物中心',
            '--kind', 'ruins',
            '--region', '江城市·三环内侧',
            '--first_appearance', 'ch001',
            '--summary', '末世前的大型商业中心，废墟中藏有物资。'
        ],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        ok("地点添加完成")

def show_final_status():
    header("Step 5: 查看项目最终状态")

    step("读取 index/chapters.json...")
    ch_file = DEMO_DIR / 'index' / 'chapters.json'
    if ch_file.exists():
        data = json.loads(ch_file.read_text(encoding='utf-8'))
        print(f"  共 {len(data)} 个章节")
        for ch in data:
            print(f"    - {ch.get('id')}: {ch.get('title', '无标题')} ({ch.get('status')})")

    step("读取 index/characters.json...")
    char_file = DEMO_DIR / 'index' / 'characters.json'
    if char_file.exists():
        data = json.loads(char_file.read_text(encoding='utf-8'))
        print(f"  共 {len(data)} 个角色")
        for c in data:
            print(f"    - {c.get('id')}: {c.get('name')} ({c.get('role')})")

    step("读取 beats 伏笔...")
    beats_file = DEMO_DIR / 'index' / 'beats.jsonl'
    if beats_file.exists():
        beats = {}
        for line in beats_file.read_text(encoding='utf-8').strip().split('\n'):
            if line.strip():
                e = json.loads(line)
                beats[e['id']] = e
        print(f"  共 {len(beats)} 条伏笔")
        for b in beats.values():
            print(f"    - {b.get('id')}: {b.get('description','')[:40]}... [{b.get('status')}]")

    step("读取地点索引...")
    loc_file = DEMO_DIR / 'index' / 'locations.json'
    if loc_file.exists():
        data = json.loads(loc_file.read_text(encoding='utf-8'))
        print(f"  共 {len(data)} 个地点")
        for l in data:
            print(f"    - {l.get('id')}: {l.get('name')} ({l.get('kind')})")

def cleanup():
    header("清理")
    if DEMO_DIR.exists():
        if NO_CLEANUP:
            ok("保留演示项目（--no-cleanup）")
            print(f"  演示项目位置: {DEMO_DIR}")
            return
        response = ask(f"是否删除演示项目 {DEMO_DIR}？(y/N): ", 'n')
        if response == 'y':
            shutil.rmtree(DEMO_DIR)
            ok("已删除")
        else:
            ok("保留演示项目")
            print(f"  演示项目位置: {DEMO_DIR}")

def main():
    print(c("""
    ===========================
       novel-agent 工作流演示
    ===========================
    """, 'header'))

    if not check_dependencies():
        sys.exit(1)

    if init_demo_project():
        build_demo_index()

    demo_workflow_state()
    demo_incremental_update()
    show_final_status()

    print(c("\n" + "="*60, 'header'))
    print(c("  演示完成！", 'ok'))
    print(c("="*60 + "\n", 'header'))

    cleanup()

    print("""
下一步：
  1. 填写 demo-novel/ 中的模板文件
  2. 运行 python scripts/build_index.py demo-novel/ 重新构建索引
  3. 在 OpenClaw / Claude Code 中打开 novel-agent，开始使用
  4. 详细文档见 README.md
    """)

if __name__ == '__main__':
    main()
