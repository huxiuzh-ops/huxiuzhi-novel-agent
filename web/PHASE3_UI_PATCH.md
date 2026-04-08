# Phase 3 UI 落地指南

## 概述
Phase 3 需要将现有的单页 web UI 扩展为多页应用，新增：
- 决策中心页面 (`pg-decisions`)
- 章节工作室页面 (`pg-studio`) 含工作流步骤可视化
- 设置页面 (`pg-settings`)

## 需要修改的文件
1. `server.js` — 新增 API 端点（已完成，见 server_v2.js）
2. `web/index.html` — 新增 3 个页面 + 新增导航项

---

## 一、server.js 新增端点（已在 server_v2.js 中实现）

需要添加到 `/api/health` 之后：

```javascript
// GET /api/decisions
if (parsed.pathname === '/api/decisions') {
  sendJson(res, getDecisions()); return;
}

// GET /api/decisions/:id
var decisionsMatch = parsed.pathname.match(/^\/api\/decisions\/(.+)$/);
if (decisionsMatch && req.method === 'GET') {
  var id = decisionsMatch[1];
  var all = getDecisions().all;
  var found = all.find(function(d){ return d.id === id; });
  sendJson(res, found || {error:'Not found'}, found ? 200 : 404); return;
}

// POST /api/decisions/:id/resolve
if (parsed.pathname.match(/^\/api\/decisions\/(.+)\/resolve$/) && req.method === 'POST') {
  var id = parsed.pathname.match(/^\/api\/decisions\/(.+)\/resolve$/)[1];
  var body = ''; req.on('data', function(c){ body+=c; });
  req.on('end', function(){
    var data = JSON.parse(body);
    var all = getDecisions().all;
    var entry = all.find(function(d){ return d.id===id; });
    if(!entry){ sendJson(res,{error:'Not found'},404); return; }
    entry.status='decided'; entry.decided_at=new Date().toISOString();
    entry.chosen_option=data.option||''; entry.notes=data.notes||'';
    fs.appendFileSync(path.join(WORKSPACE,'index','decisions.jsonl'), JSON.stringify(entry)+'\n');
    sendJson(res,{status:'ok',decision:entry});
  });
  return;
}

// GET /api/workflow
if (parsed.pathname === '/api/workflow') {
  sendJson(res, getWorkflowState()||{current_workflow:null}); return;
}

// POST /api/workflow/start
if (parsed.pathname === '/api/workflow/start' && req.method === 'POST') {
  var body=''; req.on('data',function(c){body+=c;});
  req.on('end',function(){
    var data=JSON.parse(body);
    var scriptPath=path.join(BASE,'scripts','workflow_state.py');
    var env=Object.assign({},process.env,{PYTHONIOENCODING:'utf-8',PYTHONUTF8:'1'});
    var cmd='python "'+scriptPath+'" "'+WORKSPACE+'" start '+(data.workflow||'write_chapter')+' '+(data.task_id||'task_'+(Date.now()))+' --workflow '+(data.workflow||'write_chapter')+' --start_role Supervisor';
    if(data.chapter) cmd+=' --chapter '+data.chapter;
    var out=execSync(cmd,{timeout:30000,encoding:'utf-8',shell:true,env:env});
    sendJson(res,{status:'ok',output:out.trim()});
  });
  return;
}

// POST /api/workflow/advance
if (parsed.pathname === '/api/workflow/advance' && req.method === 'POST') {
  var body=''; req.on('data',function(c){body+=c;});
  req.on('end',function(){
    var data=JSON.parse(body);
    var scriptPath=path.join(BASE,'scripts','workflow_state.py');
    var args=['python',scriptPath,WORKSPACE,'advance'];
    if(data.next_role) args.push('--next_role',data.next_role);
    if(data.output) args.push('--output',data.output);
    if(data.status) args.push('--status',data.status);
    var env=Object.assign({},process.env,{PYTHONIOENCODING:'utf-8',PYTHONUTF8:'1'});
    var out=execSync(args.join(' '),{timeout:30000,encoding:'utf-8',shell:true,env:env});
    sendJson(res,{status:'ok',output:out.trim()});
  });
  return;
}

// POST /api/workflow/complete
if (parsed.pathname === '/api/workflow/complete' && req.method === 'POST') {
  var scriptPath=path.join(BASE,'scripts','workflow_state.py');
  var env=Object.assign({},process.env,{PYTHONIOENCODING:'utf-8',PYTHONUTF8:'1'});
  var out=execSync('python "'+scriptPath+'" "'+WORKSPACE+'" complete',{timeout:30000,encoding:'utf-8',shell:true,env:env});
  sendJson(res,{status:'ok',output:out.trim()}); return;
}

// GET /api/config
if (parsed.pathname === '/api/config') {
  sendJson(res, getProjectConfig()); return;
}
```

同时在文件顶部添加辅助函数：

```javascript
// Decisions 辅助
function getDecisions() {
  var p = path.join(WORKSPACE, 'index', 'decisions.jsonl');
  if (!fs.existsSync(p)) return { pending:[], all:[] };
  var content = readFileSafe(p) || '';
  var all = {};
  content.split('\n').forEach(function(line){
    if(!line.trim()) return;
    try { var e = JSON.parse(line); if(e&&e.id) all[e.id]=e; } catch(e){}
  });
  var pending = Object.values(all).filter(function(d){ return d.status==='waiting_human'; });
  return {
    pending: pending,
    all: Object.values(all).sort(function(a,b){ return (b.created_at||'').localeCompare(a.created_at||''); })
  };
}

// Workflow State 辅助
function getWorkflowState() {
  var p = path.join(WORKSPACE, '.workflow', 'state.json');
  if (!fs.existsSync(p)) return null;
  try { return JSON.parse(readFileSafe(p)||'{}'); } catch(e){ return null; }
}

// Project Config 辅助
function getProjectConfig() {
  var p = path.join(WORKSPACE, 'novel-agent.yaml');
  if(!fs.existsSync(p)) p = path.join(BASE,'config','project.yaml');
  if(!fs.existsSync(p)) return {};
  try { var yaml = require('js-yaml'); return yaml.load(readFileSafe(p))||{}; } catch(e){ return {}; }
}
```

---

## 二、web/index.html 修改

### 2.1 新增导航项

在侧边栏 `<nav class="sidebar-nav">` 中添加：

```html
<div class="nav-item" data-p="studio"><span class="ni">&#9998;</span> 章节工作室</div>
<div class="nav-item" data-p="decisions"><span class="ni">&#9872;</span> 决策中心</div>
<div class="nav-item" data-p="settings"><span class="ni">&#9874;</span> 设置</div>
```

### 2.2 新增页面 HTML（放在 `</div><!-- /content -->` 之前）

```html
<!-- Studio Page -->
<div class="page" id="pg-studio">
<div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap">
  <button class="btn btn-p btn-sm" onclick="startWriteChapter()">&#9998; 写新章节</button>
  <button class="btn btn-g btn-sm" onclick="loadWorkflow()">&#8635; 刷新</button>
  <select id="ch-select" onchange="loadWorkflow()" style="margin-left:4px"><option value="">— 选择章节审稿 —</option></select>
  <button class="btn btn-g btn-sm" onclick="startReviewChapter()">&#128269; 审稿</button>
</div>
<div class="card" style="margin-bottom:12px">
  <div class="card-head"><div class="ctitle"><span class="ctitle-ic">&#9654;</span> 当前工作流</div><span id="wf-status-badge"></span></div>
  <div id="wf-steps"><div class="msg msg-c">暂无运行中的工作流</div></div>
  <div class="wf-controls" id="wf-controls" style="display:none">
    <button class="btn btn-p btn-sm" onclick="wfAdvance()">&#8594; 推进下一步</button>
    <button class="btn btn-g btn-sm" onclick="wfWaiting()">&#9208; 暂停等决策</button>
    <button class="btn btn-danger btn-sm" onclick="wfComplete()">&#10003; 完成</button>
  </div>
</div>
<div class="card">
  <div class="card-head"><div class="ctitle"><span class="ctitle-ic">&#128203;</span> 写作配置</div></div>
  <div id="cfg-display" style="padding:12px 16px;font-size:13px;color:var(--text-dim)">加载中...</div>
</div>
</div>

<!-- Decisions Page -->
<div class="page" id="pg-decisions">
<div style="display:flex;gap:8px;margin-bottom:14px">
  <button class="btn btn-g btn-sm" onclick="loadDecisions()">&#8635; 刷新</button>
  <span style="font-size:12.5px;color:var(--text-dim);margin-left:8px" id="dec-count"></span>
</div>
<div id="dec-list"><div class="msg msg-c">加载中...</div></div>
</div>

<!-- Settings Page -->
<div class="page" id="pg-settings">
<div class="settings-section">
  <div class="settings-title">工作区</div>
  <div class="settings-row">
    <div><div class="settings-label">当前工作区</div><div class="settings-desc" id="cfg-workspace">server.js 同目录（默认）</div></div>
    <div style="display:flex;gap:8px;align-items:center">
      <input type="text" id="ws-input" placeholder="./my-novel">
      <button class="btn btn-p btn-sm" onclick="setWorkspace()">切换</button>
    </div>
  </div>
  <div class="settings-row">
    <div class="settings-label">重置工作区</div>
    <div><button class="btn btn-g btn-sm" onclick="resetWorkspace()">&#8596; 恢复默认</button></div>
  </div>
</div>
<div class="settings-section">
  <div class="settings-title">项目配置</div>
  <div id="cfg-full"><div class="msg msg-c">加载中...</div></div>
</div>
</div>
```

### 2.3 新增 JavaScript 函数（在 `</script>` 之前添加）

```javascript
// ─── Chapter Studio ──────────────────────────────────────────────
function loadStudio() {
  loadWorkflow();
  loadCfgDisplay();
  loadChapterSelect();
}

function loadWorkflow() {
  api('/api/workflow').then(function(state) {
    var wf = state && state.current_workflow;
    var badge = document.getElementById('wf-status-badge');
    var stepsEl = document.getElementById('wf-steps');
    var controlsEl = document.getElementById('wf-controls');
    if (!wf || wf.status !== 'running') {
      badge.textContent = ''; badge.className = 'wf-status-badge';
      stepsEl.innerHTML = '<div class="msg msg-c">暂无运行中的工作流</div>';
      controlsEl.style.display = 'none';
      return;
    }
    var statusClass = wf.status === 'waiting_human' ? 'wf-waiting' : 'wf-running';
    badge.textContent = wf.status === 'waiting_human' ? '⏸ 等待决策' : '▶ 运行中';
    badge.className = 'wf-status-badge ' + statusClass;
    var html = '';
    (wf.steps||[]).forEach(function(s) {
      var isActive = s.step === wf.current_step;
      var isDone = s.step < wf.current_step;
      var cls = isActive ? 'wf-step active' : (isDone ? 'wf-step done' : 'wf-step');
      html += '<div class="'+cls+'"><div class="wf-step-num">'+(isDone?'✓':s.step)+'</div><div class="wf-step-role">'+s.role+'</div><div class="wf-step-action">'+s.action+'</div></div>';
    });
    stepsEl.innerHTML = html;
    controlsEl.style.display = 'flex';
  });
}

function loadCfgDisplay() {
  api('/api/config').then(function(cfg) {
    var p = (cfg&&cfg.project)||{};
    var w = (cfg&&cfg.writing)||{};
    var lines = [
      '标题: '+(p.title||'未设置'),
      '框架: '+(p.narrative_framework||'three_act'),
      '自主级别: '+(p.default_autonomy||'L2'),
      '最低字数: '+(w.min_words_per_chapter||3000)+' 字/章',
      '要求结尾钩子: '+(w.require_chapter_hook?'是':'否')
    ];
    document.getElementById('cfg-display').innerHTML = '<div style="color:var(--text-dim);line-height:2">'+lines.join('<br>')+'</div>';
  });
}

function loadChapterSelect() {
  api('/api/chapters').then(function(chs) {
    var sel = document.getElementById('ch-select');
    if(!chs) return;
    var opts = '<option value="">— 选择章节审稿 —</option>';
    (chs||[]).forEach(function(c){ opts += '<option value="'+c.file+'">'+c.num+' '+c.title+'</option>'; });
    sel.innerHTML = opts;
  });
}

function startWriteChapter() {
  var ch = prompt('输入章节号（如 ch009）：');
  if(!ch) return;
  apiPost('/api/workflow/start',{workflow:'write_chapter',chapter:ch,task_id:'task_'+ch}).then(function(r){
    if(r.error) { alert('错误: '+r.error); }
    else { loadWorkflow(); }
  });
}

function startReviewChapter() {
  var sel = document.getElementById('ch-select');
  var file = sel.value;
  if(!file) { alert('请先在章节工作室选择一个章节'); return; }
  var ch = file.replace('.md','');
  apiPost('/api/workflow/start',{workflow:'review_chapter',chapter:ch,task_id:'review_'+ch}).then(function(r){
    if(r.error) { alert('错误: '+r.error); }
    else { loadWorkflow(); }
  });
}

function wfAdvance() {
  apiPost('/api/workflow/advance',{next_role:null}).then(function(r){
    if(r.error) alert('错误: '+r.error);
    else loadWorkflow();
  });
}

function wfWaiting() {
  apiPost('/api/workflow/advance',{status:'waiting_human'}).then(function(r){
    if(r.error) alert('错误: '+r.error);
    else loadWorkflow();
  });
}

function wfComplete() {
  if(!confirm('确认完成当前工作流？')) return;
  apiPost('/api/workflow/complete',{}).then(function(r){
    if(r.error) alert('错误: '+r.error);
    else loadWorkflow();
  });
}

// ─── Decisions ────────────────────────────────────────────────────
function loadDecisions() {
  api('/api/decisions').then(function(r) {
    var pending = r && r.pending || [];
    var all = r && r.all || [];
    document.getElementById('dec-count').textContent = pending.length + ' 项待决 / ' + all.length + ' 总计';
    var el = document.getElementById('dec-list');
    if(!all.length) { el.innerHTML='<div class="msg msg-k">暂无决策记录 ✓</div>'; return; }
    el.innerHTML = all.map(function(d) {
      var cls = d.status === 'waiting_human' ? 'waiting' : 'decided';
      var statusLabel = d.status === 'waiting_human' ? '待决' : '已决';
      var optsHtml = '';
      if(d.options && d.status==='waiting_human') {
        optsHtml = '<div class="d-opts">'+d.options.map(function(o){
          return '<div class="d-opt" id="opt-'+d.id+'-'+o.id+'" onclick="selectOpt(\''+d.id+'\',\''+o.id+'\')">'
            +'<div class="d-opt-id">'+o.id+'</div>'
            +'<div><div class="d-opt-label">'+o.label+'</div>'
            +(o.pros&&o.pros.length?'<div class="d-opt-pros">+ '+o.pros.join(', ')+'</div>':'')
            +(o.cons&&o.cons.length?'<div class="d-opt-cons">- '+o.cons.join(', ')+'</div>':'')
            +'</div></div>';
        }).join('')+'</div>';
        if(d.recommended) optsHtml += '<div class="d-recommended">&#9733; 推荐: '+d.recommended+'</div>';
        optsHtml += '<textarea class="d-notes" id="notes-'+d.id+'" placeholder="备注（可选）"></textarea>';
        optsHtml += '<div class="d-actions"><button class="btn btn-p btn-sm" onclick="resolveDecision(\''+d.id+'\')">&#10003; 确认决策</button></div>';
      } else if(d.status==='decided') {
        optsHtml += '<div class="d-actions"><span class="d-status decided">&#10003; 已决定: '+d.chosen_option+'</span>'+(d.notes?' <span style="color:var(--text-dim);font-size:12px">'+d.notes+'</span>':'')+'</div>';
      }
      return '<div class="decision-card '+cls+'">'
        +'<div class="d-header">'
        +'<span class="d-id">'+d.id+'</span>'
        +'<span class="d-type">'+d.type+'</span>'
        +'<span class="d-status '+cls+'">'+statusLabel+'</span>'
        +'</div>'
        +'<div class="d-summary">'+(d.summary||'')+'</div>'
        +(d.why_it_matters?'<div class="d-why">&#9888; '+d.why_it_matters+'</div>':'')
        +optsHtml
        +(d.chapter?'<div style="margin-top:8px;font-size:11.5px;color:var(--text-dim)">章节: '+d.chapter+' | 创建: '+(d.created_at||'').slice(0,10)+'</div>':'')
        +'</div>';
    }).join('');
  });
}

var selectedOpts = {};
function selectOpt(decisionId, optId) {
  selectedOpts[decisionId] = optId;
  document.querySelectorAll('#opt-'+decisionId+'-'+optId+' ~ div[id^="opt-"], #opt-'+decisionId+'-'+optId+', #opt-'+decisionId+'-'+optId+' ~ *').forEach(function(el){ el.classList.remove('selected'); });
  document.querySelectorAll('#opt-'+decisionId+'-'+optId).forEach(function(el){ el.classList.add('selected'); });
}

function resolveDecision(decisionId) {
  var option = selectedOpts[decisionId] || prompt('输入选项ID（A/B/C...）:');
  if(!option) return;
  var notes = document.getElementById('notes-'+decisionId);
  notes = notes ? notes.value : '';
  apiPost('/api/decisions/'+decisionId+'/resolve',{option:option,notes:notes}).then(function(r){
    if(r.error) alert('错误: '+r.error);
    else loadDecisions();
  });
}

// ─── Settings ─────────────────────────────────────────────────────
function loadSettings() {
  var badge = document.getElementById('ws-badge');
  badge.textContent = WORKSPACE || '默认';
  badge.style.display = 'inline';
  document.getElementById('cfg-workspace').textContent = WORKSPACE || 'server.js 同目录';
  document.getElementById('ws-input').value = WORKSPACE || '';
  api('/api/config').then(function(cfg) {
    var p = (cfg&&cfg.project)||{};
    var html = '<div class="settings-row"><div class="settings-label">书名</div><div class="settings-value">'+(p.title||'未设置')+'</div></div>'
      +'<div class="settings-row"><div class="settings-label">叙事框架</div><div class="settings-value">'+(p.narrative_framework||'three_act')+'</div></div>'
      +'<div class="settings-row"><div class="settings-label">默认自主级别</div><div class="settings-value">'+(p.default_autonomy||'L2')+'</div></div>'
      +'<div class="settings-row"><div class="settings-label">语言</div><div class="settings-value">'+(p.language||'zh-CN')+'</div></div>';
    document.getElementById('cfg-full').innerHTML = html;
  });
}

function setWorkspace() {
  var ws = document.getElementById('ws-input').value.trim();
  if(!ws) return;
  fetch(API+'/api/workspace',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({workspace:ws})}).then(function(r){ return r.json(); }).then(function(data){
    if(data.status==='ok') { WORKSPACE=ws; alert('已切换到: '+ws); loadSettings(); }
    else { alert('切换失败: '+JSON.stringify(data)); }
  }).catch(function(e){ alert('错误: '+e.message); });
}

function resetWorkspace() {
  WORKSPACE = null;
  document.getElementById('ws-input').value = '';
  document.getElementById('cfg-workspace').textContent = 'server.js 同目录（默认）';
  document.getElementById('ws-badge').style.display = 'none';
  alert('已重置为默认工作区');
}

// ─── Dashboard ────────────────────────────────────────────────────
function loadDash() {
  api('/api/stats').then(function(d){
    if(!d){updateStatus(false);return;}
    updateStatus(true);
    document.getElementById('sv-ch').textContent=d.chapterCount||0;
    document.getElementById('sv-words').textContent=((d.totalWords||0)/10000).toFixed(1)+'万字';
    document.getElementById('sv-beats').textContent=d.beatCount||0;
    document.getElementById('sv-resolved').textContent=(d.resolvedBeats||0)+' 已回收';
    document.getElementById('sv-chars').textContent=d.charCount||0;
    document.getElementById('sv-alive').textContent=(d.activeChars||0)+' 在世';
    document.getElementById('sv-decisions').textContent='-';
  });
  api('/api/decisions').then(function(r){
    var pending=(r&&r.pending)?r.pending.length:0;
    document.getElementById('sv-decisions').textContent=pending;
    var rdEl=document.getElementById('rd');
    if(pending>0){
      rdEl.innerHTML=r.pending.slice(0,3).map(function(x){
        return '<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:13px">'
          +'<span class="d-status pending" style="margin-right:8px">待决</span>'
          +'<span>'+(x.summary||'').slice(0,40)+'</span></div>';
      }).join('');
    } else { rdEl.innerHTML='<div class="msg msg-k">暂无待确认决策 ✓</div>'; }
  });
  api('/api/beats').then(function(b){
    var ov=document.getElementById('ov');
    if(!b){ov.innerHTML='<div class=msg>加载失败</div>';return;}
    var list=b.filter(function(x){return x.status==='overdue';});
    if(!list.length){ov.innerHTML='<div class="msg msg-k">✓ 暂无逾期</div>';return;}
    ov.innerHTML=list.slice(0,5).map(function(x){
      return '<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:13px">'
        +'<span style="background:rgba(248,81,73,.15);color:var(--danger);padding:2px 7px;border-radius:8px;font-size:11px">逾期</span>'
        +'<span class=bid>'+x.id+'</span>'
        +'<span style="flex:1;color:var(--text-dim)">'+((x.description||'').slice(0,40))+'</span>'
        +'<span style="font-size:11.5px;color:var(--text-dim)">ch'+(x.plannedChapter||'-')+'</span></div>';
    }).join('');
  });
  api('/api/chapters').then(function(c){
    var rc=document.getElementById('rc');
    if(!c){rc.innerHTML='<div class=msg>加载失败</div>';return;}
    var r=(c||[]).slice(-5).reverse();
    if(!r.length){rc.innerHTML='<div class="msg msg-c">暂无章节</div>';return;}
    rc.innerHTML=r.map(function(ch){
      return '<div class=chitem onclick="openChapter(\''+ch.file+'\')">'
        +'<span class=chn>'+ch.num+'</span>'
        +'<span class=cht>'+(ch.title||'无标题')+'</span>'
        +'<span class=chw>'+ch.words+'字</span>'
        +'<span class=charrow>&#8594;</span></div>';
    }).join('');
  });
}
```

### 2.4 知识图谱中文化（已有，需确认 web/index.html 中存在）

在 `loadTools()` 函数的 `og.innerHTML` 处确认有以下代码：

```javascript
var typeMap={'Character':'角色','Faction':'势力','Location':'地点','Scene':'场景','PlotBeat':'伏笔','Item':'道具'};
og.innerHTML='<div class=ogrid>'
  +Object.keys(types).map(function(t){
    return '<div class=oitem><div class=ocount>'+types[t]+'</div><div class=olabel>'+(typeMap[t]||t)+'</div></div>';
  }).join('')
  +'</div><div class=msg style="margin-top:12px;font-size:12px">共 '+d.length+' 条实体</div>';
```

---

## 三、快速应用步骤

### 步骤 1：更新 server.js
```bash
copy C:\Users\Administrator\Desktop\server_v2.js C:\Users\Administrator\.openclaw\workspace\novel-agent\server.js
```

### 步骤 2：更新 web/index.html
将本目录下的 `index_phase3_patch.md` 中的 "新增页面 HTML" 和 "新增 JavaScript 函数" 插入到 `web/index.html` 对应位置。

### 步骤 3：重启服务
```bash
cd C:\Users\Administrator\.openclaw\workspace\novel-agent
node server.js
```

### 步骤 4：访问新功能
- http://localhost:8765/#studio — 章节工作室
- http://localhost:8765/#decisions — 决策中心
- http://localhost:8765/#settings — 设置
