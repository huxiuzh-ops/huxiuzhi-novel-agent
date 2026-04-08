#!/usr/bin/env python3
"""
decision_manager.py
novel-agent 决策点管理 API 服务
独立运行于 localhost:8767，或被 server.js 调用

用途：
    - 记录新决策（waiting_human）
    - 查询等待中的决策列表
    - 解决决策（record + resume workflow）
    - 决策历史

调用方式（作为模块）：
    from decision_manager import DecisionManager
    dm = DecisionManager(workspace)
    dm.list_pending()
    dm.resolve(decision_id, option, notes)

HTTP API:
    GET  /pending          → 所有等待中的决策
    GET  /decision/<id>   → 单个决策详情
    POST /decide/<id>     → 解决决策 {option, notes}
    GET  /history          → 决策历史
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

INDEX_DIR = 'index'
DECISIONS_FILE = 'decisions.jsonl'

class DecisionManager:
    def __init__(self, workspace):
        self.workspace = workspace
        self.index_dir = Path(workspace) / INDEX_DIR
        self.decisions_file = self.index_dir / DECISIONS_FILE
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def _load_all(self):
        """加载所有决策记录（id → latest entry）"""
        if not self.decisions_file.exists():
            return {}
        result = {}
        with open(self.decisions_file, 'r', encoding='utf-8') as f:
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

    def list_pending(self):
        """返回所有等待中的决策"""
        all_decisions = self._load_all()
        pending = {k: v for k, v in all_decisions.items() if v.get('status') == 'waiting_human'}
        return sorted(pending.values(), key=lambda x: x.get('created_at', ''))

    def list_all(self):
        """返回所有决策（含历史）"""
        decisions = self._load_all()
        return sorted(decisions.values(), key=lambda x: x.get('created_at', ''), reverse=True)

    def get(self, decision_id):
        """获取单个决策"""
        all_decisions = self._load_all()
        return all_decisions.get(decision_id)

    def create(self, decision_type, chapter, summary, why_it_matters, options, recommended=None, creator='system'):
        """创建新决策"""
        all_decisions = self._load_all()
        # 生成新 ID
        nums = []
        for k in all_decisions.keys():
            import re
            m = re.match(r'decision_(\d+)', k)
            if m:
                nums.append(int(m.group(1)))
        next_id = f"decision_{max(nums)+1 if nums else 1:03d}"

        entry = {
            'id': next_id,
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
            'notes': '',
            'creator': creator
        }

        # 追加到文件
        with open(self.decisions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        return entry

    def resolve(self, decision_id, chosen_option, notes=''):
        """解决决策"""
        all_decisions = self._load_all()
        if decision_id not in all_decisions:
            return None, f"决策不存在: {decision_id}"

        entry = all_decisions[decision_id].copy()
        if entry.get('status') != 'waiting_human':
            return None, f"决策状态不是 waiting_human: {entry.get('status')}"

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        entry['status'] = 'decided'
        entry['decided_at'] = now
        entry['chosen_option'] = chosen_option
        entry['notes'] = notes

        # 追加更新后的记录
        with open(self.decisions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        # 尝试恢复工作流
        self._resume_workflow(chosen_option, notes)

        return entry, None

    def _resume_workflow(self, chosen_option, notes):
        """恢复工作流"""
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from workflow_engine import load_wf_state, save_wf_state
            state = load_wf_state(self.workspace)
            wf = state.get('current_workflow')
            if wf and wf.get('status') == 'waiting_human':
                wf['status'] = 'running'
                wf['task_payload']['human_decision'] = {
                    'chosen': chosen_option,
                    'notes': notes
                }
                state['current_workflow'] = wf
                save_wf_state(self.workspace, self.workspace)
        except Exception as e:
            print(f"[WARN] 无法自动恢复工作流: {e}")

    def get_stats(self):
        """决策统计"""
        all_decisions = self._load_all()
        pending = [v for v in all_decisions.values() if v.get('status') == 'waiting_human']
        decided = [v for v in all_decisions.values() if v.get('status') == 'decided']
        return {
            'total': len(all_decisions),
            'pending': len(pending),
            'decided': len(decided)
        }


def http_main():
    """HTTP API 服务（独立运行）"""
    import http.server
    import urllib.parse

    PORT = 8767

    class Handler(http.server.BaseHTTPRequestHandler):
        def send_json(self, data, status=200):
            body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

        def get_workspace(self):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            ws = qs.get('workspace', ['./'])[0]
            return ws

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path.rstrip('/')

            if path == '/pending':
                ws = self.get_workspace()
                dm = DecisionManager(ws)
                self.send_json({'decisions': dm.list_pending()})
                return

            if path == '/history':
                ws = self.get_workspace()
                dm = DecisionManager(ws)
                self.send_json({'decisions': dm.list_all()})
                return

            if path == '/stats':
                ws = self.get_workspace()
                dm = DecisionManager(ws)
                self.send_json(dm.get_stats())
                return

            if path.startswith('/decision/'):
                decision_id = path.split('/')[-1]
                ws = self.get_workspace()
                dm = DecisionManager(ws)
                d = dm.get(decision_id)
                if d:
                    self.send_json(d)
                else:
                    self.send_json({'error': 'Not found'}, 404)
                return

            self.send_json({'error': 'Not found'}, 404)

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path.rstrip('/')

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length else ''
            data = json.loads(body) if body else {}

            if path.startswith('/decide/'):
                decision_id = path.split('/')[-1]
                ws = data.get('workspace', self.get_workspace())
                dm = DecisionManager(ws)
                entry, err = dm.resolve(decision_id, data.get('option', ''), data.get('notes', ''))
                if err:
                    self.send_json({'error': err}, 400)
                else:
                    self.send_json({'status': 'ok', 'decision': entry})
                return

            if path == '/create':
                ws = data.get('workspace', self.get_workspace())
                dm = DecisionManager(ws)
                entry = dm.create(
                    decision_type=data.get('type', 'unknown'),
                    chapter=data.get('chapter', ''),
                    summary=data.get('summary', ''),
                    why_it_matters=data.get('why_it_matters', ''),
                    options=data.get('options', []),
                    recommended=data.get('recommended')
                )
                self.send_json({'status': 'ok', 'decision': entry})
                return

            self.send_json({'error': 'Not found'}, 404)

        def log_message(self, format, *args):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

    server = http.server.HTTPServer(('localhost', PORT), Handler)
    print(f"Decision Manager API running at http://localhost:{PORT}")
    print("Endpoints:")
    print(f"  GET  /pending?workspace=<path>")
    print(f"  GET  /decision/<id>?workspace=<path>")
    print(f"  GET  /history?workspace=<path>")
    print(f"  GET  /stats?workspace=<path>")
    print(f"  POST /decide/<id>  {{option, notes, workspace}}")
    print(f"  POST /create        {{type, chapter, summary, why_it_matters, options, workspace}}")
    print(f"\nPress Ctrl+C to stop")
    server.serve_forever()

if __name__ == '__main__':
    if '--http' in sys.argv:
        http_main()
    else:
        print("decision_manager.py — Decision API module")
        print("Usage: python decision_manager.py --http  (run as HTTP server)")
        print("Or:    from decision_manager import DecisionManager; dm = DecisionManager('./my-novel')")
