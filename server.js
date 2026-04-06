/**
 * server.js — novel-agent Web UI API Server (Node.js version)
 * Run: node server.js
 * Serves on http://localhost:8765
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT = 8765;
const BASE = __dirname;

// ─── Helpers ──────────────────────────────────────────────────────────────

function sendJson(res, data) {
  const body = Buffer.from(JSON.stringify(data, null, 2));
  res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(body);
}

function sendText(res, text, contentType) {
  const buf = Buffer.from(text, 'utf8');
  res.writeHead(200, { 'Content-Type': contentType, 'Content-Length': buf.length, 'Access-Control-Allow-Origin': '*' });
  res.end(buf);
}

function readFileSafe(filePath) {
  try { return fs.readFileSync(filePath, 'utf8'); } catch (e) { return null; }
}

function getChapters() {
  const dir = path.join(BASE, 'chapters');
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir).filter(function(f) { return f.endsWith('.md'); }).sort();
  return files.map(function(f) {
    const num = parseInt(f.match(/ch[_\s]*(\d+)/i)?.[1] || '0');
    const content = readFileSafe(path.join(dir, f)) || '';
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return { file: f, num: num, title: titleMatch ? titleMatch[1].trim() : '无标题', words: content.length };
  }).sort(function(a, b) { return a.num - b.num; });
}

function getBeats(currentCh) {
  var beats = [];
  var trackingPath = path.join(BASE, 'beats', 'TRACKING.md');
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
  var graphPath = path.join(BASE, 'memory', 'ontology', 'graph.jsonl');
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
      } catch (err) { /* skip invalid JSON lines */ }
    }
  }
  return beats;
}

function getCharacters() {
  var dir = path.join(BASE, 'characters');
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

function getOntology() {
  var p = path.join(BASE, 'memory', 'ontology', 'graph.jsonl');
  if (!fs.existsSync(p)) return [];
  var content = readFileSafe(p) || '';
  return content.split('\n').filter(Boolean).map(function(line) { try { return JSON.parse(line); } catch (e) { return null; } }).filter(Boolean);
}

function runScript(name) {
  var scripts = { beats: 'beat_tracker.py', consistency: 'consistency_check.py', context: 'context_compressor.py', outline: 'outline_generator.py' };
  var file = scripts[name];
  if (!file) return '[ERROR] Unknown script: ' + name;
  var scriptPath = path.join(BASE, 'scripts', file);
  if (!fs.existsSync(scriptPath)) return '[ERROR] Script not found: ' + file;
  try {
    var out = execSync('python "' + scriptPath + '" "' + BASE + '"', { timeout: 60, encoding: 'utf8', shell: true });
    return out || '(脚本执行完成，无输出)';
  } catch (e) {
    var errMsg = (e.stdout || '') + (e.stderr || '') || '[ERROR] ' + (e.message || 'unknown error');
    return errMsg;
  }
}

// ─── MIME types ──────────────────────────────────────────────────────────
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

// ─── HTTP Server ──────────────────────────────────────────────────────
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

  // API
  if (parsed.pathname === '/api/stats') { sendJson(res, getStats()); return; }
  if (parsed.pathname === '/api/chapters') { sendJson(res, getChapters()); return; }
  if (parsed.pathname === '/api/beats') {
    var ch = qs.chapter ? parseInt(qs.chapter) : null;
    var chapters = getChapters();
    var currentCh = ch || (chapters.length ? Math.max.apply(null, chapters.map(function(c) { return c.num; })) : 0);
    sendJson(res, getBeats(currentCh)); return;
  }
  if (parsed.pathname === '/api/characters') { sendJson(res, getCharacters()); return; }
  if (parsed.pathname === '/api/ontology') { sendJson(res, getOntology()); return; }
  if (parsed.pathname === '/api/health') { sendJson(res, { status: 'ok' }); return; }

  if (parsed.pathname.startsWith('/api/read')) {
    var filePath = qs.path;
    if (!filePath) { res.writeHead(400); res.end('Missing path'); return; }
    var normalized = path.normalize(filePath).replace(/^\\?/, '');
    var fullPath = path.join(BASE, normalized);
    if (fullPath.indexOf(BASE) !== 0) { res.writeHead(403); res.end('Forbidden'); return; }
    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isFile()) {
      sendText(res, readFileSafe(fullPath) || '', 'text/plain; charset=utf-8');
    } else { res.writeHead(404); res.end('Not found'); }
    return;
  }

  if (parsed.pathname.startsWith('/api/run')) {
    sendText(res, runScript(qs.script), 'text/plain; charset=utf-8'); return;
  }

  // Static files
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
  console.log('Press Ctrl+C to stop');
});
