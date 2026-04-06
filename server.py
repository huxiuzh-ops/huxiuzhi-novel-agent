#!/usr/bin/env python3
"""
server.py — novel-agent Web UI API Server
Run: python server.py
Serves on http://localhost:8765
"""

import json
import re
import os
import subprocess
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8765
BASE = os.path.dirname(os.path.abspath(__file__))


# ─── Markdown helpers ─────────────────────────────────────────────────────

def parse_markdown_table(content):
    """Extract table data from markdown."""
    lines = content.split('\n')
    rows = []
    in_table = False
    for line in lines:
        if '| ID |' in line or '|ID|' in line:
            in_table = True
            continue
        if in_table and not line.strip():
            in_table = False
            continue
        if in_table and '|' in line:
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]
            if cells and not cells[0].startswith('-'):
                rows.append(cells)
    return rows


# ─── Chapter data ──────────────────────────────────────────────────────────

def get_chapters():
    chapters_dir = os.path.join(BASE, 'chapters')
    if not os.path.exists(chapters_dir):
        return []
    files = sorted([f for f in os.listdir(chapters_dir) if f.endswith('.md')])
    result = []
    for f in files:
        # Extract chapter number from filename like ch001.md or ch_001.md
        m = re.match(r'ch[_\s]*(\d+)', f, re.I)
        num = int(m.group(1)) if m else 0
        # Extract title from first # heading
        path = os.path.join(chapters_dir, f)
        title = '无标题'
        word_count = 0
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                content = fp.read()
                word_count = len(content)
                hm = re.search(r'^#\s+(.+)$', content, re.M)
                if hm:
                    title = hm.group(1).strip()
        except:
            pass
        result.append({'file': f, 'num': num, 'title': title, 'words': word_count})
    return sorted(result, key=lambda x: x['num'])


# ─── Beat data ────────────────────────────────────────────────────────────

def get_beats(current_chapter=None):
    """Parse beats from TRACKING.md and graph.jsonl."""
    beats = []
    # Try TRACKING.md
    tracking_path = os.path.join(BASE, 'beats', 'TRACKING.md')
    if os.path.exists(tracking_path):
        with open(tracking_path, 'r', encoding='utf-8') as f:
            content = f.read()
        in_table = False
        for line in content.split('\n'):
            if '| ID |' in line or '|ID|' in line:
                in_table = True
                continue
            if in_table and not line.strip():
                in_table = False
                continue
            if in_table and '|' in line:
                cells = [c.strip() for c in line.split('|')]
                cells = [c for c in cells if c]
                if len(cells) >= 6 and cells[0].startswith('B'):
                    status_str = cells[5].lower()
                    planned = 0
                    try:
                        planned = int(re.sub(r'[^\d]', '', cells[4].replace('ch', '')))
                    except:
                        pass
                    beats.append({
                        'id': cells[0],
                        'type': cells[1],
                        'description': cells[2],
                        'plantedChapter': re.sub(r'[^\d]', '', cells[3].replace('ch', '')),
                        'plannedChapter': str(planned),
                        'status': status_str
                    })
    # Try graph.jsonl for PlotBeat
    graph_path = os.path.join(BASE, 'memory', 'ontology', 'graph.jsonl')
    if os.path.exists(graph_path):
        with open(graph_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    if obj.get('type') == 'PlotBeat':
                        # Avoid duplicates
                        existing_ids = [b['id'] for b in beats]
                        if obj.get('id') not in existing_ids:
                            beats.append(obj)
                except:
                    pass
    # Determine overdue status
    if current_chapter is None:
        chapters = get_chapters()
        current_chapter = max([c['num'] for c in chapters], default=0)
    for b in beats:
        try:
            planned = int(b.get('plannedChapter', 0))
            if planned > 0 and planned < current_chapter and b.get('status') != 'resolved':
                b['status'] = 'overdue'
        except:
            pass
    return beats


# ─── Character data ───────────────────────────────────────────────────────

def get_characters():
    chars = []
    char_dir = os.path.join(BASE, 'characters')
    if not os.path.exists(char_dir):
        return []
    for f in os.listdir(char_dir):
        if not f.endswith('.md'):
            continue
        path = os.path.join(char_dir, f)
        try:
            with open(path, 'r', encoding='utf-8') as fp:
                content = fp.read()
            # Extract fields
            name_m = re.search(r'^#\s+(.+)$', content, re.M)
            name = name_m.group(1).strip() if name_m else f.replace('.md', '')
            age_m = re.search(r'(?i)(年龄|age)[：:]\s*(\d+)', content)
            age = int(age_m.group(2)) if age_m else None
            role_m = re.search(r'(?i)(role|角色)[：:]\s*(\w+)', content)
            role = role_m.group(2).lower() if role_m else 'supporting'
            faction_m = re.search(r'(?i)(faction|势力)[：:]\s*(.+)', content)
            faction = faction_m.group(2).strip() if faction_m else None
            status = 'alive'
            if '已故' in content or '死了' in content or '死亡' in content:
                status = 'dead'
            first_m = re.search(r'(?i)(初现|首次|first)[：:]\s*(ch?\d+)', content)
            first = first_m.group(2) if first_m else None
            chars.append({'name': name, 'age': age, 'role': role, 'faction': faction, 'status': status, 'firstAppearance': first})
        except:
            pass
    return chars


# ─── Stats ──────────────────────────────────────────────────────────────

def get_stats():
    chapters = get_chapters()
    beats = get_beats()
    chars = get_characters()
    total_words = sum(c['words'] for c in chapters)
    resolved = sum(1 for b in beats if b.get('status') == 'resolved')
    overdue = sum(1 for b in beats if b.get('status') == 'overdue')
    active_chars = sum(1 for c in chars if c.get('status') == 'alive')
    return {
        'chapterCount': len(chapters),
        'totalWords': total_words,
        'beatCount': len(beats),
        'resolvedBeats': resolved,
        'overdueBeats': overdue,
        'charCount': len(chars),
        'activeChars': active_chars
    }


# ─── Ontology ─────────────────────────────────────────────────────────────

def get_ontology():
    path = os.path.join(BASE, 'memory', 'ontology', 'graph.jsonl')
    if not os.path.exists(path):
        return []
    result = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                result.append(json.loads(line.strip()))
            except:
                pass
    return result


# ─── Run script ───────────────────────────────────────────────────────────

def run_script(name):
    """Run a Python script and return output."""
    script_map = {
        'beats': 'scripts/beat_tracker.py',
        'consistency': 'scripts/consistency_check.py',
        'context': 'scripts/context_compressor.py',
        'outline': 'scripts/outline_generator.py',
    }
    script_file = script_map.get(name)
    if not script_file:
        return f"[ERROR] Unknown script: {name}"
    script_path = os.path.join(BASE, script_file)
    if not os.path.exists(script_path):
        return f"[ERROR] Script not found: {script_file}"
    try:
        result = subprocess.run(
            [sys.executable, script_path, BASE],
            capture_output=True, text=True, timeout=60,
            cwd=BASE
        )
        output = result.stdout + result.stderr
        return output if output else "(脚本执行完成，无输出)"
    except subprocess.TimeoutExpired:
        return "[ERROR] Script timed out after 60s"
    except Exception as e:
        return f"[ERROR] {str(e)}"


# ─── HTTP Handler ─────────────────────────────────────────────────────────

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == '/api/stats':
            self.send_json(get_stats())
        elif parsed.path == '/api/chapters':
            self.send_json(get_chapters())
        elif parsed.path == '/api/beats':
            ch = qs.get('chapter', [None])[0]
            self.send_json(get_beats(int(ch) if ch else None))
        elif parsed.path == '/api/characters':
            self.send_json(get_characters())
        elif parsed.path == '/api/ontology':
            self.send_json(get_ontology())
        elif parsed.path.startswith('/api/read'):
            file_path = qs.get('path', [None])[0]
            if not file_path:
                self.send_error(400, 'Missing path')
                return
            # Security: prevent directory traversal
            file_path = os.path.normpath(file_path).lstrip(os.sep)
            full_path = os.path.join(BASE, file_path)
            if not full_path.startswith(BASE):
                self.send_error(403, 'Forbidden')
                return
            if os.path.exists(full_path) and os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.send_content(content, 'text/plain; charset=utf-8')
                except:
                    self.send_error(500, 'Read error')
            else:
                self.send_error(404, 'Not found')
        elif parsed.path.startswith('/api/run'):
            script = qs.get('script', [None])[0]
            output = run_script(script)
            self.send_content(output, 'text/plain; charset=utf-8')
        elif parsed.path == '/api/health':
            self.send_json({'status': 'ok'})
        else:
            # Serve static files from web/
            if parsed.path == '/':
                static_path = os.path.join(BASE, 'web', 'index.html')
            else:
                static_path = os.path.join(BASE, 'web', parsed.path.lstrip('/'))
            if os.path.exists(static_path) and os.path.isfile(static_path):
                ext = os.path.splitext(static_path)[1]
                mime_types = {'.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon'}
                mime = mime_types.get(ext, 'application/octet-stream')
                try:
                    with open(static_path, 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-Type', mime)
                        self.end_headers()
                        self.wfile.write(f.read())
                except:
                    self.send_error(500)
            else:
                self.send_error(404)

    def send_json(self, data):
        self.send_content(json.dumps(data, ensure_ascii=False, indent=2), 'application/json; charset=utf-8')

    def send_content(self, content, content_type):
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    print(f"novel-agent server starting on http://localhost:{PORT}")
    print(f"Base directory: {BASE}")
    print("Open http://localhost:8765 in your browser")
    server = HTTPServer(('localhost', PORT), Handler)
    server.serve_forever()
