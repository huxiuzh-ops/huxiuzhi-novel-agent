#!/usr/bin/env python3
"""
workflow_engine.py
novel-agent 工作流执行引擎
负责：角色串联执行、index-first 数据读取、config 驱动行为、decision 点闭环

用法：
    python workflow_engine.py <workspace> <workflow> <task_id> [options]
    python workflow_engine.py ./my-novel write_chapter task_001 --chapter ch009
    python workflow_engine.py ./my-novel review_chapter task_002 --chapter ch008
    python workflow_engine.py ./my-novel resume --decision A

工作流：
    write_chapter: Supervisor → Planner → Writer → Editor → Supervisor(分流)
    review_chapter: Supervisor → Editor → Supervisor(交付)
    plan_volume:   Supervisor → Planner → Supervisor(交付)
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# 路径配置
# ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_CONFIG = 'novel-agent.yaml'
INDEX_DIR = 'index'
ROLES_DIR = SCRIPT_DIR.parent / 'roles'
CONFIG_DIR = SCRIPT_DIR.parent / 'config'

AUTONOMY_LEVELS = {
    'L1': 'ask_everything',      # 事事询问
    'L2': 'ask_major',            # 重大决策询问（默认）
    'L3': 'auto_except_critical', # 除致命外全自动
    'L4': 'fully_auto'            # 全自动
}

DECISION_TYPES_MAJOR = [
    'major_plot_change', 'character_death', 'world_rule_change',
    'foreshadow_abandon', 'consistency_conflict', 'outline_deviation'
]

# ─────────────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────────────

def load_yaml(path):
    try:
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return None

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def load_jsonl(path):
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
            except Exception:
                continue
    return result

def load_role_template(role_name):
    """读取角色提示模板"""
    role_file = ROLES_DIR / f'{role_name.lower()}.md'
    if not role_file.exists():
        return None
    with open(role_file, 'r', encoding='utf-8') as f:
        return f.read()

def load_project_config(workspace):
    """加载项目配置（优先级：workspace novel-agent.yaml > config/project.yaml）"""
    cfg = {}
    proj_cfg = CONFIG_DIR / 'project.yaml'
    if proj_cfg.exists():
        d = load_yaml(proj_cfg)
        if d:
            cfg.update(d)
    ws_cfg = Path(workspace) / WORKSPACE_CONFIG
    if ws_cfg.exists():
        d = load_yaml(ws_cfg)
        if d:
            cfg.update(d)
    return cfg

def get_autonomy(config):
    """从配置中获取 autonomy level"""
    val = config.get('project', {}).get('default_autonomy', 'L2')
    return val if val in AUTONOMY_LEVELS else 'L2'

def is_major_decision(decision_type):
    return decision_type in DECISION_TYPES_MAJOR

def should_pause_for_human(decision_type, autonomy):
    """根据 autonomy 级别决定是否暂停"""
    if autonomy == 'L1':
        return True
    if autonomy == 'L2':
        return is_major_decision(decision_type)
    if autonomy == 'L3':
        return is_major_decision(decision_type) and decision_type in [
            'character_death', 'world_rule_change', 'foreshadow_abandon'
        ]
    return False  # L4

# ─────────────────────────────────────────────────────────────────
# Index 读取（index-first 原则）
# ─────────────────────────────────────────────────────────────────

def read_chapters_index(workspace):
    path = Path(workspace) / INDEX_DIR / 'chapters.json'
    return load_json(path) or []

def read_beats_index(workspace):
    path = Path(workspace) / INDEX_DIR / 'beats.jsonl'
    return load_jsonl(path)

def read_characters_index(workspace):
    path = Path(workspace) / INDEX_DIR / 'characters.json'
    return load_json(path) or []

def read_decisions_index(workspace):
    path = Path(workspace) / INDEX_DIR / 'decisions.jsonl'
    return load_jsonl(path)

def read_locations_index(workspace):
    path = Path(workspace) / INDEX_DIR / 'locations.json'
    return load_json(path) or []

def get_latest_decision(workspace):
    """获取最新的 waiting_human 决策"""
    decisions = read_decisions_index(workspace)
    waiting = {k: v for k, v in decisions.items() if v.get('status') == 'waiting_human'}
    if not waiting:
        return None
    return sorted(waiting.values(), key=lambda x: x.get('created_at', ''))[-1]

# ─────────────────────────────────────────────────────────────────
# Workflow State 集成
# ─────────────────────────────────────────────────────────────────

def get_wf_state_path(workspace):
    return Path(workspace) / '.workflow' / 'state.json'

def load_wf_state(workspace):
    p = get_wf_state_path(workspace)
    if not p.exists():
        return {
            'version': '1.0',
            'current_workflow': None,
            'workflow_history': [],
            'last_updated': datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        }
    return load_json(str(p))

def save_wf_state(workspace, state):
    state['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    p = get_wf_state_path(workspace)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def init_workflow(workspace, workflow, task_id, start_role='Supervisor', chapter=None):
    """初始化工作流"""
    state = load_wf_state(workspace)
    if state.get('current_workflow') and state['current_workflow'].get('status') == 'running':
        print(f"[WARN] 当前有运行中的工作流: {state['current_workflow']['workflow']} ({state['current_workflow']['task_id']})")
        print("使用 --force 强制覆盖")
        return None

    steps = {
        'write_chapter': [
            {'step': 0, 'role': 'Supervisor', 'action': '识别任务并装配上下文'},
            {'step': 1, 'role': 'Planner', 'action': '产出章节 mini plan'},
            {'step': 2, 'role': 'Writer', 'action': '写草稿'},
            {'step': 3, 'role': 'Editor', 'action': '审稿'},
            {'step': 4, 'role': 'Supervisor', 'action': '分流'}
        ],
        'review_chapter': [
            {'step': 0, 'role': 'Supervisor', 'action': '识别任务'},
            {'step': 1, 'role': 'Editor', 'action': '审稿'},
            {'step': 2, 'role': 'Supervisor', 'action': '交付'}
        ],
        'plan_volume': [
            {'step': 0, 'role': 'Supervisor', 'action': '识别任务'},
            {'step': 1, 'role': 'Planner', 'action': '生成分卷大纲'},
            {'step': 2, 'role': 'Supervisor', 'action': '交付'}
        ]
    }

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    workflow_obj = {
        'workflow': workflow,
        'task_id': task_id,
        'status': 'running',
        'started_at': now,
        'current_role': start_role,
        'current_step': 0,
        'steps': steps.get(workflow, []),
        'chapter': chapter,
        'outputs': [],
        'task_payload': {},
        'decisions': []
    }

    state['current_workflow'] = workflow_obj
    save_wf_state(workspace, state)
    return workflow_obj

def advance_workflow(workspace, next_role=None, output_file=None, verdict=None, requires_human=False):
    """推进工作流到下一角色"""
    state = load_wf_state(workspace)
    wf = state.get('current_workflow')
    if not wf or wf.get('status') != 'running':
        print("[ERROR] 没有运行中的工作流")
        return None

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    if next_role:
        wf['current_role'] = next_role
        wf['current_step'] = wf.get('current_step', 0) + 1

    if output_file:
        wf['outputs'].append({
            'role': wf.get('current_role'),
            'file': output_file,
            'verdict': verdict,
            'at': now
        })

    if verdict:
        wf['task_payload']['last_verdict'] = verdict

    if requires_human:
        wf['status'] = 'waiting_human'
        print(f"⏸ 工作流暂停，等待人类决策...")
    else:
        wf['status'] = 'running'

    state['current_workflow'] = wf
    save_wf_state(workspace, state)
    return wf

def complete_workflow(workspace):
    """标记工作流完成"""
    state = load_wf_state(workspace)
    wf = state.get('current_workflow')
    if not wf:
        print("[ERROR] 没有运行中的工作流")
        return

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    wf['status'] = 'done'
    wf['completed_at'] = now
    state['workflow_history'].append(wf)
    state['current_workflow'] = None
    save_wf_state(workspace, state)
    print(f"✅ 工作流已完成: {wf['workflow']} ({wf['task_id']})")

# ─────────────────────────────────────────────────────────────────
# Decision 点管理
# ─────────────────────────────────────────────────────────────────

def save_decision(workspace, decision):
    """追加决策到 decisions.jsonl"""
    path = Path(workspace) / INDEX_DIR / 'decisions.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(decision, ensure_ascii=False) + '\n')
    print(f"📋 决策卡片已记录: {decision.get('id')} — {decision.get('summary', '')[:40]}")

def make_decision_record(workspace, decision_id, decision_type, chapter, summary, why_it_matters, options, recommended=None):
    """生成结构化决策卡片"""
    return {
        'id': decision_id,
        'type': decision_type,
        'chapter': chapter,
        'status': 'waiting_human',
        'summary': summary,
        'why_it_matters': why_it_matters,
        'options': options,
        'recommended': recommended,
        'created_at': datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        'decided_at': None,
        'chosen_option': None,
        'notes': ''
    }

def record_decision(workspace, decision_id, chosen_option, notes=''):
    """记录人类决策结果，更新并关闭决策卡片"""
    decisions = read_decisions_index(workspace)
    if decision_id not in decisions:
        print(f"[ERROR] 决策不存在: {decision_id}")
        return False

    entry = decisions[decision_id].copy()
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    entry['status'] = 'decided'
    entry['decided_at'] = now
    entry['chosen_option'] = chosen_option
    entry['notes'] = notes

    # 追加更新后的记录
    save_decision(workspace, entry)
    print(f"✅ 决策已记录: {decision_id} → {chosen_option}")
    return True

def generate_decision_id(workspace):
    """生成唯一决策 ID"""
    decisions = read_decisions_index(workspace)
    nums = []
    for k in decisions.keys():
        m = k.replace('decision_', '')
        if m.isdigit():
            nums.append(int(m))
    next_num = (max(nums) + 1) if nums else 1
    return f"decision_{next_num:03d}"

# ─────────────────────────────────────────────────────────────────
# Config 驱动行为
# ─────────────────────────────────────────────────────────────────

def get_writing_config(workspace):
    """读取写作配置"""
    cfg_file = CONFIG_DIR / 'writing.yaml'
    if cfg_file.exists():
        return load_yaml(cfg_file) or {}
    return {'min_words_per_chapter': 3000, 'require_chapter_hook': True}

def get_validation_config(workspace):
    """读取验证配置"""
    cfg_file = CONFIG_DIR / 'validation.yaml'
    if cfg_file.exists():
        return load_yaml(cfg_file) or {}
    return {}

def apply_autonomy_behavior(autonomy, context):
    """根据 autonomy 级别调整行为描述"""
    level_desc = {
        'L1': '【L1 模式】事事确认，所有决策均需用户批准',
        'L2': '【L2 模式】重大决策确认（角色死亡/主线变化/世界规则改变），其余自动',
        'L3': '【L3 模式】仅致命决策（角色死亡/世界规则）需确认，其余自动',
        'L4': '【L4 模式】全自动执行，不询问'
    }
    return level_desc.get(autonomy, level_desc['L2'])

# ─────────────────────────────────────────────────────────────────
# 角色执行（生成提示上下文）
# ─────────────────────────────────────────────────────────────────

def build_supervisor_context(workspace, workflow, chapter, config):
    """为 Supervisor 构建输入上下文"""
    chapters = read_chapters_index(workspace)
    beats = read_beats_index(workspace)
    chars = read_characters_index(workspace)
    decisions = read_decisions_index(workspace)
    autonomy = get_autonomy(config)
    writing_cfg = get_writing_config(workspace)

    pending_decisions = [v for v in decisions.values() if v.get('status') == 'waiting_human']

    last_ch = None
    if chapters:
        last_ch = max(chapters, key=lambda x: int(x.get('chapter_num', 0)))

    pending_beats = [b for b in beats.values() if b.get('status') in ('pending', 'active')]

    return {
        'user_request': f'执行 {workflow} {chapter}' if chapter else f'执行 {workflow}',
        'workflow': workflow,
        'chapter': chapter,
        'project_config': config,
        'autonomy_level': autonomy,
        'autonomy_behavior': apply_autonomy_behavior(autonomy, {}),
        'writing_config': writing_cfg,
        'current_chapter': last_ch.get('id') if last_ch else None,
        'pending_decisions': pending_decisions,
        'pending_beats': [{'id': k, **v} for k, v in list(pending_beats)[:10]],
        'relevant_characters': chars[:5],
        'chapter_count': len(chapters),
        'index_dir': INDEX_DIR
    }

def build_planner_context(workspace, chapter, config):
    """为 Planner 构建输入上下文"""
    chapters = read_chapters_index(workspace)
    beats = read_beats_index(workspace)
    chars = read_characters_index(workspace)

    prev_ch = None
    for ch in sorted(chapters, key=lambda x: int(x.get('chapter_num', 0))):
        if chapter and ch.get('id') == chapter:
            break
        prev_ch = ch

    pending_beats = [b for b in beats.values() if b.get('status') in ('pending', 'active')]
    writing_cfg = get_writing_config(workspace)

    return {
        'task_type': 'plan_chapter',
        'chapter': chapter,
        'previous_chapter_summary': prev_ch.get('summary', '') if prev_ch else '',
        'pending_beats': [{'id': k, 'description': v.get('description', ''),
                           'priority': v.get('priority', 'medium')}
                          for k, v in list(pending_beats)[:5]],
        'relevant_characters': [{'id': c.get('id'), 'name': c.get('name', ''),
                                  'summary': c.get('summary', '')}
                                 for c in chars[:5]],
        'constraints': {
            'min_words': writing_cfg.get('min_words_per_chapter', 3000),
            'must_include': [b['id'] for b in pending_beats[:3] if b.get('priority') == 'high']
        }
    }

def execute_role(role_name, context, workspace):
    """
    执行角色（打印角色输入上下文 + 提示模板位置）
    在真正的 AI 执行环境中，这里会调用 LLM。
    目前打印详细上下文供人工或 AI 执行参考。
    """
    template = load_role_template(role_name)
    print(f"\n{'='*60}")
    print(f"🎭 执行角色: {role_name}")
    print(f"{'='*60}")

    if template:
        # 显示角色模板片段（限制长度）
        lines = template.split('\n')
        if len(lines) > 60:
            print("【角色模板】:")
            print('\n'.join(lines[:60]))
            print(f"  ... [{len(lines)-60} 行省略] ...")
        else:
            print("【角色模板】:")
            print(template)

    print(f"\n【角色输入上下文】:")
    ctx_json = json.dumps(context, ensure_ascii=False, indent=2)
    if len(ctx_json) > 3000:
        print(ctx_json[:3000])
        print(f"  ... [{len(ctx_json)-3000} 字符省略] ...")
    else:
        print(ctx_json)

    print(f"\n{'='*60}")
    return context

# ─────────────────────────────────────────────────────────────────
# Workflow 执行
# ─────────────────────────────────────────────────────────────────

def run_write_chapter(workspace, chapter, config, simulate=False):
    """执行 write_chapter 工作流"""
    autonomy = get_autonomy(config)
    print(f"\n🚀 write_chapter 工作流启动")
    print(f"   章节: {chapter}")
    print(f"   自主级别: {autonomy} — {apply_autonomy_behavior(autonomy, {})}")

    task_id = f"task_{chapter}"
    wf = init_workflow(workspace, 'write_chapter', task_id, start_role='Supervisor', chapter=chapter)
    if not wf:
        return

    # Step 0: Supervisor 识别任务
    print(f"\n[Step 0] Supervisor 识别任务")
    ctx = build_supervisor_context(workspace, 'write_chapter', chapter, config)
    execute_role('Supervisor', ctx, workspace)

    # Step 1: Planner
    print(f"\n[Step 1] Planner 产出章节计划")
    planner_ctx = build_planner_context(workspace, chapter, config)
    plan_output = execute_role('Planner', planner_ctx, workspace)

    if simulate:
        print("\n【SIMULATE模式】跳过 AI 执行，直接推进工作流")
        wf = advance_workflow(workspace, next_role='Writer', output_file=f'chapters/{chapter}_plan.json')
        print(f"   → 已生成章节计划，Planner 输出: chapters/{chapter}_plan.json")
    else:
        wf = advance_workflow(workspace, next_role='Writer')

    # Step 2: Writer
    print(f"\n[Step 2] Writer 写草稿")
    writer_cfg = {
        'chapter': chapter,
        'chapter_plan': plan_output,
        'writing_config': get_writing_config(workspace),
        'chapter_file': f'chapters/{chapter}.md'
    }
    execute_role('Writer', writer_cfg, workspace)

    if simulate:
        print("\n【SIMULATE模式】跳过 Writer 执行")
        wf = advance_workflow(workspace, next_role='Editor', verdict='passed')
    else:
        wf = advance_workflow(workspace, next_role='Editor')

    # Step 3: Editor
    print(f"\n[Step 3] Editor 审稿")
    editor_ctx = {
        'chapter': chapter,
        'chapter_file': f'chapters/{chapter}.md',
        'validation_config': get_validation_config(workspace),
        'writing_config': get_writing_config(workspace)
    }
    execute_role('Editor', editor_ctx, workspace)

    # Step 4: Supervisor 分流
    print(f"\n[Step 4] Supervisor 分流")

    # 检查是否有等待中的决策
    latest_decision = get_latest_decision(workspace)
    if latest_decision and latest_decision.get('status') == 'waiting_human':
        decision_type = latest_decision.get('type', 'unknown')
        if should_pause_for_human(decision_type, autonomy):
            print(f"\n⏸ 检测到等待中的人类决策: {latest_decision.get('id')}")
            print(f"   决策内容: {latest_decision.get('summary', '')[:50]}")
            print(f"   请先运行: python workflow_engine.py {workspace} resolve_decision --id {latest_decision.get('id')} --option A")
            return

    # simulate 模式：默认 passed
    verdict = 'passed' if simulate else input("Editor verdict [passed/warning/requires_human] (默认 passed): ").strip() or 'passed'

    if verdict == 'passed':
        complete_workflow(workspace)
        print(f"\n✅ 章节 {chapter} 已完成！")
        print(f"   建议运行: python scripts/incremental_index_update.py {workspace} update_chapter {chapter} --status final")
    elif verdict == 'warning':
        print(f"\n⚠️  需要修订，打回 Writer...")
        wf = advance_workflow(workspace, next_role='Writer', verdict='warning')
    else:  # requires_human
        decision_id = generate_decision_id(workspace)
        decision = make_decision_record(
            workspace, decision_id,
            decision_type='major_plot_change',
            chapter=chapter,
            summary='需要人类确认的关键决策',
            why_it_matters='此决策影响主线走向',
            options=[
                {'id': 'A', 'label': '选项A', 'pros': [], 'cons': []},
                {'id': 'B', 'label': '选项B', 'pros': [], 'cons': []}
            ],
            recommended='B'
        )
        save_decision(workspace, decision)
        advance_workflow(workspace, verdict='requires_human', requires_human=True)
        print(f"\n⏸ 已生成决策卡片，等待确认...")
        print(f"   决策ID: {decision_id}")
        print(f"   请运行: python workflow_engine.py {workspace} resolve_decision --id {decision_id} --option A")

def run_review_chapter(workspace, chapter, config):
    """执行 review_chapter 工作流"""
    print(f"\n🚀 review_chapter 工作流启动")
    print(f"   章节: {chapter}")

    task_id = f"review_{chapter}"
    wf = init_workflow(workspace, 'review_chapter', task_id, start_role='Supervisor', chapter=chapter)
    if not wf:
        return

    # Supervisor → Editor
    print(f"\n[Step 0] Supervisor 识别任务")
    ctx = build_supervisor_context(workspace, 'review_chapter', chapter, config)
    execute_role('Supervisor', ctx, workspace)

    print(f"\n[Step 1] Editor 审稿")
    editor_ctx = {
        'chapter': chapter,
        'chapter_file': f'chapters/{chapter}.md',
        'validation_config': get_validation_config(workspace),
        'writing_config': get_writing_config(workspace)
    }
    execute_role('Editor', editor_ctx, workspace)

    verdict = input("审稿 verdict [passed/warning] (默认 passed): ").strip() or 'passed'

    if verdict == 'passed':
        complete_workflow(workspace)
        print(f"\n✅ 章节 {chapter} 审稿通过！")
    else:
        print(f"\n⚠️  审稿有警告，请根据 issues 修订")

def run_resolve_decision(workspace, decision_id, chosen_option, notes=''):
    """解决一个等待中的决策"""
    decisions = read_decisions_index(workspace)
    if decision_id not in decisions:
        print(f"[ERROR] 决策不存在: {decision_id}")
        return

    decision = decisions[decision_id]
    if decision.get('status') != 'waiting_human':
        print(f"[ERROR] 决策不是等待状态: {decision.get('status')}")
        return

    record_decision(workspace, decision_id, chosen_option, notes)

    # 恢复 workflow
    state = load_wf_state(workspace)
    wf = state.get('current_workflow')
    if wf and wf.get('status') == 'waiting_human':
        wf['status'] = 'running'
        wf['task_payload']['human_decision'] = {
            'decision_id': decision_id,
            'chosen': chosen_option,
            'notes': notes
        }
        state['current_workflow'] = wf
        save_wf_state(workspace, state)
        print(f"✅ 工作流已恢复: {wf['workflow']} ({wf['task_id']})")

def show_status(workspace, verbose=False):
    """显示当前工作流状态"""
    state = load_wf_state(workspace)
    wf = state.get('current_workflow')
    decisions = read_decisions_index(workspace)
    waiting = [v for v in decisions.values() if v.get('status') == 'waiting_human']

    print(f"\n{'='*50}")
    print(f"novel-agent 工作流状态")
    print(f"{'='*50}")

    if wf and wf.get('status') == 'running':
        print(f"\n运行中工作流:")
        print(f"  任务ID: {wf['task_id']}")
        print(f"  类型:   {wf['workflow']}")
        print(f"  章节:   {wf.get('chapter', '-')}")
        print(f"  当前角色: {wf['current_role']}")
        print(f"  步骤:   {wf.get('current_step', 0)}/{len(wf.get('steps', []))}")
        print(f"  开始于: {wf['started_at']}")
        if wf.get('outputs'):
            print(f"  输出文件: {', '.join(str(o) for o in wf['outputs'])}")
    else:
        print(f"\n无运行中的工作流")

    if waiting:
        print(f"\n⏸ 等待决策 ({len(waiting)}项):")
        for d in waiting:
            print(f"  [{d.get('id')}] {d.get('summary', '')[:50]}")
            print(f"    类型: {d.get('type')} | 章节: {d.get('chapter')} | 推荐: {d.get('recommended', '?')}")
    else:
        print(f"\n无等待中的决策")

    if verbose and wf:
        print(f"\n工作流步骤:")
        for s in wf.get('steps', []):
            marker = '→' if s['step'] == wf.get('current_step') else ' '
            print(f"  {marker} [{s['step']}] {s['role']}: {s['action']}")

    print()

def show_pending_decisions(workspace):
    """显示所有等待中的决策"""
    decisions = read_decisions_index(workspace)
    waiting = [v for v in decisions.values() if v.get('status') == 'waiting_human']

    if not waiting:
        print("暂无等待中的决策")
        return

    print(f"\n⏸ 等待决策 ({len(waiting)}项):")
    for d in waiting:
        print(f"\n  [{d.get('id')}] {d.get('summary', '')}")
        print(f"  类型: {d.get('type')} | 章节: {d.get('chapter')}")
        print(f"  为什么重要: {d.get('why_it_matters', '')}")
        print(f"  选项:")
        for opt in d.get('options', []):
            print(f"    [{opt.get('id')}] {opt.get('label', '')}")
            pros = opt.get('pros', [])
            cons = opt.get('cons', [])
            if pros: print(f"        优点: {', '.join(pros)}")
            if cons: print(f"        缺点: {', '.join(cons)}")
        if d.get('recommended'):
            print(f"  推荐: {d.get('recommended')} ({d.get('recommended')})")

# ─────────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("novel-agent workflow_engine")
        print("用法: python workflow_engine.py <workspace> <command> [options]")
        print()
        print("命令:")
        print("  write-chapter <chXXX>    执行写章节工作流")
        print("  review-chapter <chXXX>  执行审章节工作流")
        print("  status [--verbose]       查看当前状态")
        print("  decisions                列出等待中的决策")
        print("  resolve-decision --id <id> --option <A|B|...>  解决决策")
        print("  simulate <workflow> <chXXX>  模拟运行（不调AI）")
        print()
        print("示例:")
        print("  python workflow_engine.py ./my-novel write-chapter ch009 --simulate")
        print("  python workflow_engine.py ./my-novel status --verbose")
        print("  python workflow_engine.py ./my-novel decisions")
        print("  python workflow_engine.py ./my-novel resolve-decision --id decision_001 --option A")
        sys.exit(1)

    workspace = sys.argv[1]
    if not os.path.exists(workspace):
        print(f"[ERROR] 工作空间不存在: {workspace}")
        sys.exit(1)

    cmd = sys.argv[2] if len(sys.argv) > 2 else None

    # 无命令时显示状态
    if not cmd or cmd == 'status':
        verbose = '--verbose' in sys.argv
        show_status(workspace, verbose=verbose)
        return

    if cmd == 'decisions':
        show_pending_decisions(workspace)
        return

    config = load_project_config(workspace)
    chapter = None

    # 解析通用参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--chapter', '--ch', dest='chapter', help='章节ID')
    parser.add_argument('--simulate', action='store_true', help='模拟运行（不调AI）')
    parser.add_argument('--id', dest='decision_id', help='决策ID')
    parser.add_argument('--option', dest='option', help='选择的选项')
    parser.add_argument('--notes', dest='notes', default='', help='备注')
    parser.add_argument('--force', action='store_true', help='强制覆盖')
    args = parser.parse_args(sys.argv[3:] if len(sys.argv) > 3 else [])
    chapter = args.chapter

    if cmd == 'write-chapter' or cmd == 'write_chapter':
        if not chapter:
            # 自动取下一章
            chapters = read_chapters_index(workspace)
            if chapters:
                nums = [int(c.get('chapter_num', c.get('id', 'ch').replace('ch', '').strip('_') or '0'))
                        for c in chapters]
                next_num = max(nums) + 1
            else:
                next_num = 1
            chapter = f'ch{next_num:03d}'
            print(f"[INFO] 未指定章节，自动为: {chapter}")
        run_write_chapter(workspace, chapter, config, simulate=args.simulate)

    elif cmd == 'review-chapter' or cmd == 'review_chapter':
        if not chapter:
            print("[ERROR] 需要 --chapter 参数")
            sys.exit(1)
        run_review_chapter(workspace, chapter, config)

    elif cmd == 'resolve-decision' or cmd == 'resolve_decision':
        if not args.decision_id or not args.option:
            print("[ERROR] 需要 --id 和 --option 参数")
            sys.exit(1)
        run_resolve_decision(workspace, args.decision_id, args.option, args.notes)

    elif cmd == 'simulate':
        workflow = sys.argv[3] if len(sys.argv) > 3 else 'write_chapter'
        ch = sys.argv[4] if len(sys.argv) > 4 else None
        if not ch:
            chapters = read_chapters_index(workspace)
            nums = [int(c.get('chapter_num', 0)) for c in chapters]
            ch = f'ch{(max(nums)+1) if nums else 1:03d}'
        run_write_chapter(workspace, ch, config, simulate=True)

    else:
        print(f"[ERROR] 未知命令: {cmd}")
        print("可用命令: write-chapter, review-chapter, status, decisions, resolve-decision, simulate")
        sys.exit(1)

if __name__ == '__main__':
    main()
