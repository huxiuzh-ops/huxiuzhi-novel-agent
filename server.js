/**
 * server.js — novel-agent Web UI API Server
 * Run: node server.js
 * Serves on http://localhost:8765
 *
 * P0 fixes applied:
 * - timeout: 60 → 60000 (ms)
 * - PYTHONIOENCODING: utf-8 for Chinese output
 * - WORKSPACE global variable for multi-workspace
 * - /api/workspace POST endpoint
 * - Decision API (/api/decisions)
 * - Workflow API (/api/workflow)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT = 8765;
const BASE = __dirname;
let WORKSPACE = BASE;

function sendJson(res, data, status = 200) {
  const body = Buffer.from(JSON.stringify(data, null, 2));
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
  res.end(body);
}

function sendText(res, text, contentType = 'text/plain; charset=utf-8') {
  const buf = Buffer.from(text, 'utf8');
  res.writeHead(200, { 'Content-Type': contentType, 'Content-Length': buf.length, 'Access-Control-Allow-Origin': '*' });
  res.end(buf);
}

function readFileSafe(filePath) {
  try { return fs.readFileSync(filePath, 'utf8'); } catch (e) { return null; }
}

// ─── Chapter index ────────────────────────────────────────────

function getChapters() {
  const dir = path.join(WORKSPACE, 'chapters');
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir).filter(function(f) { return f.endsWith('.md'); }).sort();
  return files.map(function(f) {
    const num = parseInt(f.match(/ch[_\s]*(\d+)/i)?.[1] || '0');
    const content = readFileSafe(path.join(dir, f)) || '';
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return { file: f, num: num, title: titleMatch ? titleMatch[1].trim() : '无标题', words: content.length };
  }).sort(function(a, b) { return a.num - b.num; });
}

// ─── Beats ───────────────────────────────────────────────────

function getBeats(currentCh) {
  var beats = [];
  var trackingPath = path.join(WORKSPACE, 'beats', 'TRACKING.md');
  if (fs.existsSync(trackingPath)) {
    var content = readFileSafe(trackingPath) || '';
    var lines = content.split('\n');
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (line.includes('| ID |') || line.includes('|ID|')) continue;
      if (!line.trim()) continue;
      if (line.includes('---')) continue;
      if (!line.includes('|')) continue;
      var cells = line.split('|').map(function(c) { return c.trim(); }).filter(Boolean);
      if (cells.length >= 6 && cells[0].charAt(0) === 'B') {
        var planned = parseInt(cells[4].replace(/[^\d]/g, '')) || 0;
        var status = cells[5].toLowerCase();
        if (planned > 0 && planned < currentCh && status !== 'resolved') status = 'overdue';
        beats.push({
          id: cells[0], type: cells[1], description: cells[2],
          plantedChapter: cells[3].replace(/[^\d]/g, ''),
          plannedChapter: String(planned),
          status: status
        });
      }
    }
  }
  var graphPath = path.join(WORKSPACE, 'memory', 'ontology', 'graph.jsonl');
  if (fs.existsSync(graphPath)) {
    var graphContent = readFileSafe(graphPath) || '';
    var graphLines = graphContent.split('\n');
    for (var j = 0; j < graphLines.length; j++) {
      try {
        var obj = JSON.parse(graphLines[j].trim());
        if (obj.type === 'PlotBeat') {
          var exists = beats.some(function(b) { return b.id === obj.id; });
          if (!exists) {
            var p = parseInt(obj.plannedChapter) || 0;
            var s = obj.status || 'pending';
            if (p > 0 && p < currentCh && s !== 'resolved') s = 'overdue';
            beats.push({ id: obj.id, type: obj.subtype || obj.type, description: obj.description, plantedChapter: obj.plantedChapter, plannedChapter: String(p), status: s });
          }
        }
      } catch (err) { }
    }
  }
  return beats;
}

// ─── Characters ──────────────────────────────────────────────

function getCharacters() {
  var dir = path.join(WORKSPACE, 'characters');
  if (!fs.existsSync(dir)) return [];
  var files = fs.readdirSync(dir).filter(function(f) { return f.endsWith('.md'); });
  return files.map(function(f) {
    var content = readFileSafe(path.join(dir, f)) || '';
    var nameMatch = content.match(/^#\s+(.+)$/m);
    var ageMatch = content.match(/(?:年龄|age)[：:]\s*(\d+)/i);
    var roleMatch = content.match(/(?:role|角色)[：:]\s*(\w+)/i);
    var factionMatch = content.match(/(?:faction|势力)[：:]\s*(.+)/i);
    var firstMatch = content.match(/(?:初现|首次)[：:]\s*(ch?\S+)/i);
    var name = nameMatch ? nameMatch[1].trim() : f.replace('.md', '');
    var role = roleMatch ? roleMatch[1].toLowerCase() : 'supporting';
    if (['protagonist', 'antagonist', 'supporting'].indexOf(role) === -1) role = 'supporting';
    var status = 'alive';
    if (/已故|死了|死亡/.test(content)) status = 'dead';
    return { name: name, age: ageMatch ? parseInt(ageMatch[1]) : null, role: role, faction: factionMatch ? factionMatch[1].trim() : null, status: status, firstAppearance: firstMatch ? firstMatch[1] : null };
  });
}

// ─── Stats ───────────────────────────────────────────────────

function getStats() {
  var chapters = getChapters();
  var currentCh = chapters.length ? Math.max.apply(null, chapters.map(function(c) { return c.num; })) : 0;
  var beats = getBeats(currentCh);
  var chars = getCharacters();
  return {
    chapterCount: chapters.length,
    totalWords: chapters.reduce(function(s, c) { return s + c.words; }, 0),
    beatCount: beats.length,
    resolvedBeats: beats.filter(function(b) { return b.status === 'resolved'; }).length,
    overdueBeats: beats.filter(function(b) { return b.status === 'overdue'; }).length,
    charCount: chars.length,
    activeChars: chars.filter(function(c) { return c.status === 'alive'; }).length
  };
}

// ─── Ontology ─────────────────────────────────────────────────

function getOntology() {
  var p = path.join(WORKSPACE, 'memory', 'ontology', 'graph.jsonl');
  if (!fs.existsSync(p)) return [];
  var content = readFileSafe(p) || '';
  return content.split('\n').filter(Boolean).map(function(line) { try { return JSON.parse(line); } catch (e) { return null; } }).filter(Boolean);
}

// ─── Decisions ───────────────────────────────────────────────

function getDecisions() {
  var p = path.join(WORKSPACE, 'index', 'decisions.jsonl');
  if (!fs.existsSync(p)) return { pending: [], all: [] };
  var content = readFileSafe(p) || '';
  var all = {};
  var lines = content.split('\n');
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (!line) continue;
    try {
      var entry = JSON.parse(line);
      if (entry && entry.id) all[entry.id] = entry;
    } catch (e) { }
  }
  var pending = Object.values(all).filter(function(d) { return d.status === 'waiting_human'; });
  return { pending: pending, all: Object.values(all).sort(function(a, b) {
    return (b.created_at || '').localeCompare(a.created_at || '');
  })};
}

// ─── Workflow State ───────────────────────────────────────────

function getWorkflowState() {
  var p = path.join(WORKSPACE, '.workflow', 'state.json');
  if (!fs.existsSync(p)) return null;
  try { return JSON.parse(readFileSafe(p) || '{}'); } catch (e) { return null; }
}

// ─── Project Config ──────────────────────────────────────────

function getProjectConfig() {
  var p = path.join(WORKSPACE, 'novel-agent.yaml');
  if (!fs.existsSync(p)) {
    // Fallback to config/project.yaml
    p = path.join(BASE, 'config', 'project.yaml');
  }
  if (!fs.existsSync(p)) return {};
  try {
    var yaml = require('js-yaml');
    return yaml.load(readFileSafe(p)) || {};
  } catch (e) {
    return {};
  }
}

// ─── Run Python Script ───────────────────────────────────────

function runScript(name, workspace) {
  var scripts = { beats: 'beat_tracker.py', consistency: 'consistency_check.py', context: 'context_compressor.py', outline: 'outline_generator.py' };
  var file = scripts[name];
  if (!file) return '[ERROR] Unknown script: ' + name;
  var scriptPath = path.join(BASE, 'scripts', file);
  if (!fs.existsSync(scriptPath)) return '[ERROR] Script not found: ' + scriptPath;
  var targetDir = workspace || WORKSPACE;
  var startTime = Date.now();
  try {
    var env = Object.assign({}, process.env, { PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' });
    var out = execSync('python "' + scriptPath + '" "' + targetDir + '"', { timeout: 60000, encoding: 'utf-8', shell: true, env: env });
    return out || '(脚本执行完成，无输出)';
  } catch (e) {
    var duration = ((Date.now() - startTime) / 1000).toFixed(1);
    var errMsg = (e.stdout || '') + (e.stderr || '');
    if (e.killed) {
      return '[ERROR] Script timed out after ' + duration + 's (script: ' + file + ', timeout: 60s). Try running manually: python "' + scriptPath + '" "' + targetDir + '"';
    }
    return '[ERROR] Script failed after ' + duration + 's\nCommand: python "' + scriptPath + '" "' + targetDir + '"\nOutput: ' + (errMsg || e.message);
  }
}

// ─── MIME types ───────────────────────────────────────────────

var MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.svg': 'image/svg+xml'
};

// ─── HTTP Server ─────────────────────────────────────────────

http.createServer(function(req, res) {
  var parsed;
  try {
    parsed = new URL(req.url, 'http://localhost:' + PORT);
  } catch (e) {
    res.writeHead(400); res.end('Invalid URL'); return;
  }
  var qs = {};
  parsed.searchParams.forEach(function(val, key) { qs[key] = val; });

  console.log('[' + new Date().toISOString() + '] ' + req.method + ' ' + parsed.pathname);

  // ─── CORS preflight ──────────────────────────────────────
  if (req.method === 'OPTIONS') {
    res.writeHead(200, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type' });
    res.end(); return;
  }

  // ─── Workspace switch ─────────────────────────────────────
  if (parsed.pathname === '/api/workspace' && req.method === 'POST') {
    var body = '';
    req.on('data', function(chunk) { body += chunk; });
    req.on('end', function() {
      try {
        var data = JSON.parse(body);
        if (data.workspace && fs.existsSync(data.workspace)) {
          WORKSPACE = data.workspace;
          sendJson(res, { status: 'ok', workspace: WORKSPACE });
        } else {
          res.writeHead(400); res.end('Invalid workspace path');
        }
      } catch (e) {
        res.writeHead(400); res.end('Invalid JSON');
      }
    });
    return;
  }

  // ─── GET /api/health ──────────────────────────────────────
  if (parsed.pathname === '/api/health') { sendJson(res, { status: 'ok' }); return; }

  // ─── GET /api/stats ────────────────────────────────────────
  if (parsed.pathname === '/api/stats') { sendJson(res, getStats()); return; }

  // ─── GET /api/config ───────────────────────────────────────
  if (parsed.pathname === '/api/config') { sendJson(res, getProjectConfig()); return; }

  // ─── GET /api/chapters ────────────────────────────────────
  if (parsed.pathname === '/api/chapters') { sendJson(res, getChapters()); return; }

  // ─── GET /api/beats ───────────────────────────────────────
  if (parsed.pathname === '/api/beats') {
    var ch = qs.chapter ? parseInt(qs.chapter) : null;
    var chapters = getChapters();
    var currentCh = ch || (chapters.length ? Math.max.apply(null, chapters.map(function(c) { return c.num; })) : 0);
    sendJson(res, getBeats(currentCh)); return;
  }

  // ─── GET /api/characters ──────────────────────────────────
  if (parsed.pathname === '/api/characters') { sendJson(res, getCharacters()); return; }

  // ─── GET /api/ontology ────────────────────────────────────
  if (parsed.pathname === '/api/ontology') { sendJson(res, getOntology()); return; }

  // ─── GET /api/decisions ───────────────────────────────────
  if (parsed.pathname === '/api/decisions') {
    sendJson(res, getDecisions()); return;
  }

  // ─── GET /api/decisions/:id ───────────────────────────────
  var decisionsMatch = parsed.pathname.match(/^\/api\/decisions\/(.+)$/);
  if (decisionsMatch && req.method === 'GET') {
    var decisionId = decisionsMatch[1];
    var allDecisions = getDecisions().all;
    var found = allDecisions.find(function(d) { return d.id === decisionId; });
    if (found) { sendJson(res, found); return; }
    sendJson(res, { error: 'Decision not found' }, 404); return;
  }

  // ─── POST /api/decisions/:id/resolve ─────────────────────
  if (parsed.pathname.match(/^\/api\/decisions\/(.+)\/resolve$/) && req.method === 'POST') {
    var id = parsed.pathname.match(/^\/api\/decisions\/(.+)\/resolve$/)[1];
    var body = '';
    req.on('data', function(chunk) { body += chunk; });
    req.on('end', function() {
      try {
        var data = JSON.parse(body);
        var allDecisions = getDecisions().all;
        var entry = allDecisions.find(function(d) { return d.id === id; });
        if (!entry) { sendJson(res, { error: 'Decision not found' }, 404); return; }
        if (entry.status !== 'waiting_human') { sendJson(res, { error: 'Not waiting_human' }, 400); return; }
        // Update status
        entry.status = 'decided';
        entry.decided_at = new Date().toISOString();
        entry.chosen_option = data.option || '';
        entry.notes = data.notes || '';
        // Append to file
        var p = path.join(WORKSPACE, 'index', 'decisions.jsonl');
        fs.appendFileSync(p, JSON.stringify(entry) + '\n');
        sendJson(res, { status: 'ok', decision: entry });
      } catch (e) {
        sendJson(res, { error: e.message }, 400);
      }
    });
    return;
  }

  // ─── GET /api/workflow ────────────────────────────────────
  if (parsed.pathname === '/api/workflow') {
    sendJson(res, getWorkflowState() || { current_workflow: null }); return;
  }

  // ─── POST /api/workflow/start ─────────────────────────────
  if (parsed.pathname === '/api/workflow/start' && req.method === 'POST') {
    var body = '';
    req.on('data', function(chunk) { body += chunk; });
    req.on('end', function() {
      try {
        var data = JSON.parse(body);
        var wfType = data.workflow || 'write_chapter';
        var taskId = data.task_id || 'task_' + Date.now();
        var chapter = data.chapter || null;
        // Use workflow_engine.py to init
        var scriptPath = path.join(BASE, 'scripts', 'workflow_state.py');
        if (!fs.existsSync(scriptPath)) {
          sendJson(res, { error: 'workflow_state.py not found' }, 500); return;
        }
        var env = Object.assign({}, process.env, { PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' });
        var cmd = 'python "' + scriptPath + '" "' + WORKSPACE + '" start ' + wfType + ' ' + taskId + ' --workflow ' + wfType + ' --start_role Supervisor' + (chapter ? ' --chapter ' + chapter : '');
        var out = execSync(cmd, { timeout: 30000, encoding: 'utf-8', shell: true, env: env });
        sendJson(res, { status: 'ok', output: out.trim() });
      } catch (e) {
        sendJson(res, { error: (e.stdout || '') + (e.stderr || e.message) }, 500);
      }
    });
    return;
  }

  // ─── POST /api/workflow/advance ───────────────────────────
  if (parsed.pathname === '/api/workflow/advance' && req.method === 'POST') {
    var body = '';
    req.on('data', function(chunk) { body += chunk; });
    req.on('end', function() {
      try {
        var data = JSON.parse(body);
        var scriptPath = path.join(BASE, 'scripts', 'workflow_state.py');
        var args = ['python', scriptPath, WORKSPACE, 'advance'];
        if (data.next_role) args.push('--next_role', data.next_role);
        if (data.output) args.push('--output', data.output);
        if (data.status) args.push('--status', data.status);
        var env = Object.assign({}, process.env, { PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' });
        var out = execSync(args.join(' '), { timeout: 30000, encoding: 'utf-8', shell: true, env: env });
        sendJson(res, { status: 'ok', output: out.trim() });
      } catch (e) {
        sendJson(res, { error: (e.stdout || '') + (e.stderr || e.message) }, 500);
      }
    });
    return;
  }

  // ─── POST /api/workflow/complete ─────────────────────────
  if (parsed.pathname === '/api/workflow/complete' && req.method === 'POST') {
    var scriptPath = path.join(BASE, 'scripts', 'workflow_state.py');
    var env = Object.assign({}, process.env, { PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' });
    try {
      var out = execSync('python "' + scriptPath + '" "' + WORKSPACE + '" complete', { timeout: 30000, encoding: 'utf-8', shell: true, env: env });
      sendJson(res, { status: 'ok', output: out.trim() });
    } catch (e) {
      sendJson(res, { error: (e.stdout || '') + (e.stderr || e.message) }, 500);
    }
    return;
  }

  // ─── GET /api/read ────────────────────────────────────────
  if (parsed.pathname.startsWith('/api/read')) {
    var filePath = qs.path;
    if (!filePath) { res.writeHead(400); res.end('Missing path'); return; }
    var normalized = path.normalize(filePath).replace(/^\\?/, '');
    var fullPath = path.join(WORKSPACE, normalized);
    if (fullPath.indexOf(WORKSPACE) !== 0) { res.writeHead(403); res.end('Forbidden'); return; }
    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isFile()) {
      sendText(res, readFileSafe(fullPath) || '', 'text/plain; charset=utf-8');
    } else { res.writeHead(404); res.end('Not found'); }
    return;
  }

  // ─── GET /api/run ─────────────────────────────────────────
  if (parsed.pathname.startsWith('/api/run')) {
    var ws = qs.workspace || WORKSPACE;
    sendText(res, runScript(qs.script, ws), 'text/plain; charset=utf-8'); return;
  }

  // ─── Static files ─────────────────────────────────────────
  var staticFile;
  if (parsed.pathname === '/' || parsed.pathname === '/index.html') {
    staticFile = path.join(BASE, 'web', 'index.html');
  } else {
    staticFile = path.join(BASE, 'web', parsed.pathname.replace(/^\//, ''));
  }
  if (fs.existsSync(staticFile) && fs.statSync(staticFile).isFile()) {
    var ext = path.extname(staticFile).toLowerCase();
    var mime = MIME[ext] || 'application/octet-stream';
    var buf = fs.readFileSync(staticFile);
    res.writeHead(200, { 'Content-Type': mime, 'Content-Length': buf.length, 'Access-Control-Allow-Origin': '*' });
    res.end(buf);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
}).listen(PORT, function() {
  console.log('novel-agent server running at http://localhost:' + PORT);
  console.log('Base directory: ' + BASE);
  console.log('Workspace: ' + WORKSPACE);
  console.log('Press Ctrl+C to stop');
});
