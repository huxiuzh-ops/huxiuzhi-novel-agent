#!/usr/bin/env python3
# workflow_state.py
# 小说 Agent 工作流状态管理脚本
# 用途：记录当前工作流状态、任务队列、决策点
# 无需数据库，纯 JSON 文件存储

import os
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

STATE_DIR = '.workflow'
STATE_FILE = 'state.json'
TASKS_FILE = 'tasks.jsonl'
DECISIONS_FILE = 'decisions.jsonl'

TASK_STATUS = ['pending', 'running', 'blocked', 'waiting_human', 'done', 'failed', 'cancelled']
WORKFLOW_TYPES = ['write_chapter', 'review_chapter', 'update_world', 'query', 'plan_volume', 'plan_chapter', 'add_character']
ROLE_TYPES = ['Supervisor', 'Planner', 'Writer', 'Editor', 'World']

def get_state_path(workspace):
    return Path(workspace) / STATE_DIR

def ensure_state_dir(workspace):
    p = get_state_path(workspace)
    p.mkdir(exist_ok=True)
    return p

def load_state(workspace):
    p = get_state_path(workspace) / STATE_FILE
    if not p.exists():
        return {
            'version': '1.0',
            'current_workflow': None,
            'workflow_history': [],
            'last_updated': datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        }
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(workspace, state):
    state['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    p = get_state_path(workspace) / STATE_FILE
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_tasks(workspace):
    p = get_state_path(workspace) / TASKS_FILE
    if not p.exists():
        return []
    tasks = []
    with open(p, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                tasks.append(json.loads(line))
            except:
                continue
    return tasks

def save_task(workspace, task):
    p = get_state_path(workspace) / TASKS_FILE
    tasks = load_tasks(workspace)
    updated = False
    for i, t in enumerate(tasks):
        if t.get('task_id') == task.get('task_id'):
            tasks[i] = task
            updated = True
            break
    if not updated:
        tasks.append(task)
    with open(p, 'w', encoding='utf-8') as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + '\n')

def get_task_by_id(workspace, task_id):
    tasks = load_tasks(workspace)
    for t in tasks:
        if t.get('task_id') == task_id:
            return t
    return None

def task_to_history(task):
    return {k: v for k, v in task.items() if k not in ['running', 'pending']}

def fmt_outputs(outputs):
    if not outputs:
        return ''
    parts = []
    for o in outputs:
        if isinstance(o, str):
            parts.append(o)
        elif isinstance(o, dict):
            parts.append(o.get('file', str(o)))
        else:
            parts.append(str(o))
    return ', '.join(parts)

def cmd_start(workspace, args):
    state = load_state(workspace)

    if state.get('current_workflow') and state['current_workflow'].get('status') == 'running':
        print(f"[WARN] 当前有运行中的工作流: {state['current_workflow']['workflow']} ({state['current_workflow']['task_id']})")
        if not args.force:
            print("使用 --force 强制覆盖")
            sys.exit(1)

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    workflow = {
        'workflow': args.workflow,
        'task_id': args.task_id,
        'status': 'running',
        'started_at': now,
        'current_role': args.start_role or 'Supervisor',
        'current_step': 0,
        'steps': args.steps or get_default_steps(args.workflow),
        'input_refs': args.input_refs or [],
        'outputs': [],
        'task_payload': {}
    }

    state['current_workflow'] = workflow
    save_state(workspace, state)

    task = {
        'task_id': args.task_id,
        'workflow': args.workflow,
        'role': args.start_role or 'Supervisor',
        'status': 'running',
        'created_at': now,
        'input_refs': args.input_refs or [],
        'depends_on': args.depends_on or [],
        'outputs': [],
        'warnings': [],
        'requires_human': False,
        'metadata': {}
    }
    save_task(workspace, task)

    print(f"[OK] 工作流已启动: {args.workflow} ({args.task_id})")
    print(f"     下一步角色: {workflow['current_role']}")

def cmd_advance(workspace, args):
    state = load_state(workspace)
    wf = state.get('current_workflow')

    if not wf or wf.get('status') != 'running':
        print("[ERROR] 没有运行中的工作流")
        sys.exit(1)

    if args.task_id and wf.get('task_id') != args.task_id:
        print(f"[ERROR] 任务 ID 不匹配: {wf.get('task_id')} != {args.task_id}")
        sys.exit(1)

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    if args.next_role:
        wf['current_role'] = args.next_role
        wf['current_step'] = wf.get('current_step', 0) + 1

    if args.status:
        wf['status'] = args.status

    if args.output:
        wf['outputs'].append({
            'role': wf.get('current_role'),
            'file': args.output,
            'at': now
        })

    if args.payload:
        wf['task_payload'].update(args.payload)

    if args.warnings:
        wf.setdefault('warnings', []).extend(args.warnings)

    state['current_workflow'] = wf
    save_state(workspace, state)

    task = get_task_by_id(workspace, wf['task_id'])
    if task:
        task['role'] = wf['current_role']
        task['status'] = wf['status']
        if args.output:
            task['outputs'].append(args.output)
        save_task(workspace, task)

    print(f"[OK] 工作流已推进: {wf['workflow']}")
    print(f"     当前角色: {wf['current_role']}")
    print(f"     状态: {wf['status']}")

    if wf['status'] == 'waiting_human':
        print(f"     等待人类决策")

def cmd_complete(workspace, args):
    state = load_state(workspace)
    wf = state.get('current_workflow')

    if not wf:
        print("[ERROR] 没有运行中的工作流")
        sys.exit(1)

    if args.task_id and wf.get('task_id') != args.task_id:
        print("[ERROR] 任务 ID 不匹配")
        sys.exit(1)

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    wf['status'] = 'done'
    wf['completed_at'] = now
    state['workflow_history'].append(wf)
    state['current_workflow'] = None
    save_state(workspace, state)

    task = get_task_by_id(workspace, wf['task_id'])
    if task:
        task['status'] = 'done'
        save_task(workspace, task)

    print(f"[OK] 工作流已完成: {wf['workflow']} ({wf['task_id']})")

def cmd_status(workspace, args):
    state = load_state(workspace)
    wf = state.get('current_workflow')
    tasks = load_tasks(workspace)

    print(f"=" * 50)
    print(f"novel-agent 工作流状态")
    print(f"=" * 50)

    if wf and wf.get('status') == 'running':
        print(f"\n运行中工作流:")
        print(f"  任务 ID: {wf['task_id']}")
        print(f"  类型: {wf['workflow']}")
        print(f"  当前角色: {wf['current_role']}")
        print(f"  步骤: {wf.get('current_step', 0)}/{len(wf.get('steps', []))}")
        print(f"  开始于: {wf['started_at']}")
        if wf.get('outputs'):
            print(f"  输出: {fmt_outputs(wf['outputs'])}")
        if wf.get('warnings'):
            print(f"  警告: {', '.join(wf['warnings'])}")
    else:
        print(f"\n无运行中的工作流")

    if args.verbose and tasks:
        print(f"\n任务历史 ({len(tasks)} 条):")
        for t in tasks[-10:]:
            print(f"  [{t.get('status', '?')}] {t.get('task_id')} ({t.get('workflow')}) - {t.get('role')}")

    print()

def cmd_waiting(workspace, args):
    state = load_state(workspace)
    wf = state.get('current_workflow')

    if not wf:
        print("[ERROR] 没有运行中的工作流")
        sys.exit(1)

    wf['status'] = 'waiting_human'
    state['current_workflow'] = wf
    save_state(workspace, state)

    task = get_task_by_id(workspace, wf['task_id'])
    if task:
        task['status'] = 'waiting_human'
        task['requires_human'] = True
        save_task(workspace, task)

    print(f"[OK] 工作流已暂停，等待人类决策")

def cmd_resume(workspace, args):
    state = load_state(workspace)
    wf = state.get('current_workflow')

    if not wf or wf.get('status') != 'waiting_human':
        print("[ERROR] 没有等待中的人类决策工作流")
        sys.exit(1)

    if args.task_id and wf.get('task_id') != args.task_id:
        print("[ERROR] 任务 ID 不匹配")
        sys.exit(1)

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    wf['status'] = 'running'
    wf['resumed_at'] = now
    if args.decision:
        wf['task_payload']['human_decision'] = args.decision

    state['current_workflow'] = wf
    save_state(workspace, state)

    print(f"[OK] 工作流已恢复: {wf['workflow']}")

def cmd_list(workspace, args):
    tasks = load_tasks(workspace)
    if not tasks:
        print("暂无任务记录")
        return

    print(f"共 {len(tasks)} 条任务:")
    for t in tasks:
        print(f"  [{t.get('status', '?')}] {t.get('task_id')} | {t.get('workflow')} | {t.get('role')} | {t.get('created_at', '')[:10]}")

def get_default_steps(workflow):
    steps = {
        'write_chapter': [
            {'step': 0, 'role': 'Supervisor', 'action': '识别任务'},
            {'step': 1, 'role': 'Planner', 'action': '产出 mini plan'},
            {'step': 2, 'role': 'Writer', 'action': '写草稿'},
            {'step': 3, 'role': 'Editor', 'action': '审稿'},
            {'step': 4, 'role': 'Supervisor', 'action': '分流'}
        ],
        'review_chapter': [
            {'step': 0, 'role': 'Supervisor', 'action': '识别任务'},
            {'step': 1, 'role': 'Editor', 'action': '审稿'},
            {'step': 2, 'role': 'Supervisor', 'action': '交付'}
        ],
        'update_world': [
            {'step': 0, 'role': 'Supervisor', 'action': '识别任务'},
            {'step': 1, 'role': 'World', 'action': '处理变更'},
            {'step': 2, 'role': 'Supervisor', 'action': '交付'}
        ],
        'plan_volume': [
            {'step': 0, 'role': 'Supervisor', 'action': '识别任务'},
            {'step': 1, 'role': 'Planner', 'action': '生成分卷大纲'},
            {'step': 2, 'role': 'Supervisor', 'action': '交付'}
        ]
    }
    return steps.get(workflow, [])

def main():
    if len(sys.argv) < 2:
        print("用法: python workflow_state.py <workspace> <command> [options]")
        print()
        print("命令:")
        print("  start <workflow> <task_id>     启动工作流")
        print("  advance                        推进到下一步")
        print("  complete                       标记完成")
        print("  status                         查看状态")
        print("  waiting                        标记为等待人类决策")
        print("  resume                         从等待决策恢复")
        print("  list                           列出所有任务")
        print()
        print("示例:")
        print("  python workflow_state.py ./my-novel start write_chapter task_001")
        print("  python workflow_state.py ./my-novel advance --next_role Writer --output chapters/ch001.md")
        print("  python workflow_state.py ./my-novel status --verbose")
        sys.exit(1)

    workspace = sys.argv[1]
    if not os.path.exists(workspace):
        print(f"[ERROR] 工作空间不存在: {workspace}")
        sys.exit(1)

    ensure_state_dir(workspace)

    if len(sys.argv) < 3:
        cmd_status(workspace, argparse.Namespace(verbose=False))
        sys.exit(0)

    cmd = sys.argv[2]

    parser = argparse.ArgumentParser()
    parser.add_argument('--task_id', help='任务ID')
    parser.add_argument('--workflow', help='工作流类型')
    parser.add_argument('--start_role', help='起始角色')
    parser.add_argument('--next_role', help='下一步角色')
    parser.add_argument('--status', help='状态')
    parser.add_argument('--output', help='输出文件')
    parser.add_argument('--payload', type=json.loads, help='payload JSON')
    parser.add_argument('--warnings', nargs='+', help='警告列表')
    parser.add_argument('--input_refs', nargs='+', help='输入文件列表')
    parser.add_argument('--depends_on', nargs='+', help='依赖任务')
    parser.add_argument('--steps', nargs='+', help='步骤列表')
    parser.add_argument('--force', action='store_true', help='强制覆盖')
    parser.add_argument('--decision', help='人类决策结果')
    parser.add_argument('--verbose', action='store_true', help='详细信息')

    args = parser.parse_args(sys.argv[3:])

    if cmd == 'start':
        if not args.workflow or not args.task_id:
            print("[ERROR] start 需要 --workflow 和 --task_id")
            sys.exit(1)
        cmd_start(workspace, args)
    elif cmd == 'advance':
        cmd_advance(workspace, args)
    elif cmd == 'complete':
        cmd_complete(workspace, args)
    elif cmd == 'status':
        cmd_status(workspace, args)
    elif cmd == 'waiting':
        cmd_waiting(workspace, args)
    elif cmd == 'resume':
        cmd_resume(workspace, args)
    elif cmd == 'list':
        cmd_list(workspace, args)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
