/* DetectAI frontend — talks to FastAPI backend at /api/cases/* */
const BACKEND_URL = window.location.origin;

const SCENARIO_MISSIONS = [
  { id: 'procedural', label: '🤖 Dynamic AI Mystery', desc: 'Procedurally generated case crafted by AI based on chosen crime & difficulty.' },
  { id: 'scenario_theft_easy', label: '💎 The Vanishing Ruby (Theft · Easy)', crime: 'Theft', diff: 'Easy', desc: 'A 50-carat ruby disappears from Lord Blackwood\'s secured vault during his birthday gala.' },
  { id: 'scenario_murder_medium', label: '☠ The Midnight Cyanide (Murder · Med)', crime: 'Murder', diff: 'Medium', desc: 'Dr. Alistair Vance is discovered poisoned with potassium cyanide in his espresso mug.' },
  { id: 'scenario_cyber_hard', label: '⚡ The Apex Grid Blackout (Cyber · Hard)', crime: 'Cybercrime', diff: 'Hard', desc: 'Cascading power grid failure triggered by DarkVolt ransomware demanding a 500 BTC payout.' },
];

const state = {
  playerName: 'Detective',
  crimeType: 'Murder',
  difficulty: 'Medium',
  scenarioId: 'procedural',
  case: null,
  caseId: null,
  visitedLocations: new Set(),
  discoveredEvidence: new Set(),
  activeSuspectId: null,
  chatHistories: {},
  hintsRevealed: [],
  accusedSuspectId: null,
  selectedEvidenceIds: new Set(),
  isGenerating: false,
};

const CRIME_TYPES = ['Murder','Theft','Kidnapping','Cybercrime','Fraud'];
const DIFFICULTIES = ['Easy','Medium','Hard'];

function renderTopbarActions(){
  document.getElementById('topbar-actions').innerHTML = `
    <button class="btn btn-ghost btn-sm" onclick="showScreen('how-to-play')">📖 How to Play</button>
    <button class="btn btn-ghost btn-sm" onclick="showCaseHistory()">📁 Case Files</button>
    <button class="btn btn-ghost btn-sm" onclick="showLeaderboard()">🏆 Leaderboard</button>
  `;
}

function initSetup(){
  const sBox = document.getElementById('scenario-choices');
  if(sBox){
    sBox.innerHTML = SCENARIO_MISSIONS.map(s =>
      `<button class="choice ${s.id===state.scenarioId?'active':''}" onclick="pickScenario('${s.id}')">${s.label}</button>`
    ).join('');
    const curScen = SCENARIO_MISSIONS.find(s => s.id === state.scenarioId) || SCENARIO_MISSIONS[0];
    const descEl = document.getElementById('scenario-desc');
    if(descEl) descEl.textContent = curScen.desc || '';
  }

  document.getElementById('crime-choices').innerHTML = CRIME_TYPES.map(c =>
    `<button class="choice ${c===state.crimeType?'active':''}" onclick="pickCrime('${c}')">${c}</button>`).join('');
  document.getElementById('diff-choices').innerHTML = DIFFICULTIES.map(d =>
    `<button class="choice ${d===state.difficulty?'active':''}" onclick="pickDiff('${d}')">${d}</button>`).join('');
}

function pickScenario(sId){
  state.scenarioId = sId;
  const s = SCENARIO_MISSIONS.find(x => x.id === sId);
  if(s && s.crime){
    state.crimeType = s.crime;
    state.difficulty = s.diff;
  }
  initSetup();
}

function pickCrime(c){
  state.crimeType = c;
  const cur = SCENARIO_MISSIONS.find(x => x.id === state.scenarioId);
  if(cur && cur.crime && cur.crime !== c) state.scenarioId = 'procedural';
  initSetup();
}

function pickDiff(d){
  state.difficulty = d;
  const cur = SCENARIO_MISSIONS.find(x => x.id === state.scenarioId);
  if(cur && cur.diff && cur.diff !== d) state.scenarioId = 'procedural';
  initSetup();
}

renderTopbarActions();
initSetup();

async function api(path, opts={}){
  const url = BACKEND_URL.replace(/\/$/,'') + path;
  try{
    const res = await fetch(url, {
      method: opts.method || 'GET',
      headers: {'Content-Type':'application/json'},
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    if(!res.ok){
      let detail = '';
      try{ detail = (await res.json()).detail || ''; }catch(e){}
      throw new Error(detail || `Request failed (${res.status})`);
    }
    return await res.json();
  }catch(err){
    if(err instanceof TypeError){
      toast(`Can't reach the backend at ${BACKEND_URL}. Check that the service is running.`, true);
    } else {
      toast(err.message, true);
    }
    throw err;
  }
}

function toast(msg, isError=false){
  const wrap = document.getElementById('toast-wrap');
  const el = document.createElement('div');
  el.className = 'toast' + (isError ? '' : ' info');
  el.textContent = msg;
  wrap.appendChild(el);
  setTimeout(()=>el.remove(), 5200);
}

const SCREENS = [
  'screen-home',
  'how-to-play',
  'screen-how-to-play',
  'screen-rules',
  'screen-setup',
  'screen-briefing',
  'screen-hub',
  'screen-verdict',
  'screen-leaderboard',
  'screen-history'
];

function normalizeScreenId(id) {
  if (!id) return 'screen-home';
  if (id === 'how-to-play' || id === 'screen-how-to-play') return 'how-to-play';
  if (id === 'rules' || id === 'screen-rules') return 'screen-rules';
  if (id === 'setup' || id === 'screen-setup') return 'screen-setup';
  if (id === 'home' || id === 'screen-home') return 'screen-home';
  return id;
}

const PRIMARY_SCREEN_IDS = [
  'screen-home',
  'how-to-play',
  'screen-rules',
  'screen-setup',
  'screen-briefing',
  'screen-hub',
  'screen-verdict',
  'screen-leaderboard',
  'screen-history'
];

function showScreen(id, pushState = true){
  const target = normalizeScreenId(id);

  PRIMARY_SCREEN_IDS.forEach(s => {
    const el = document.getElementById(s);
    if(el){
      if(s === target){
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    }
  });

  window.scrollTo({top: 0, behavior: 'instant'});

  if(pushState && window.history && window.history.pushState){
    const cleanHash = target.replace('screen-', '');
    try {
      history.pushState({ screen: target }, '', '#' + cleanHash);
    } catch(e){}
  }
}

function goHome(){ showScreen('screen-home'); }

// Safe event listener for How to Play button
function initHowToPlayListener(){
  const btn = document.getElementById('btn-how-to-play') || document.getElementById('btn-home-how-to-play');
  if(btn){
    btn.onclick = function(e){
      if(e) e.preventDefault();
      showScreen('how-to-play');
    };
    btn.addEventListener('click', function(e){
      e.preventDefault();
      showScreen('how-to-play');
    });
  }
}

// Make navigation functions globally accessible
window.showScreen = showScreen;
window.goHome = goHome;
window.initHowToPlayListener = initHowToPlayListener;

window.addEventListener('popstate', (e)=>{
  if(e.state && e.state.screen){
    showScreen(e.state.screen, false);
  } else {
    const hash = (window.location.hash || '').replace('#', '');
    if(hash && (hash === 'how-to-play' || hash === 'rules' || hash === 'setup')){
      showScreen(hash, false);
    } else {
      showScreen('screen-home', false);
    }
  }
});

if(document.readyState === 'loading'){
  document.addEventListener('DOMContentLoaded', initHowToPlayListener);
} else {
  initHowToPlayListener();
}

async function generateCase(){
  if(state.isGenerating) return;
  state.isGenerating = true;

  const btn = document.getElementById('btn-generate');
  if(btn){
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Generating Case...';
  }

  const loader = document.getElementById('case-loader-overlay');
  if(loader) loader.classList.remove('hidden');

  state.playerName = document.getElementById('player-name').value.trim() || 'Detective';

  try{
    const res = await api('/api/cases/generate', {method:'POST', body:{
      difficulty: state.difficulty,
      crime_type: state.crimeType,
      scenario_id: state.scenarioId !== 'procedural' ? state.scenarioId : undefined
    }});
    state.case = res.case;
    state.caseId = res.case_id;
    state.visitedLocations = new Set();
    state.discoveredEvidence = new Set();
    state.chatHistories = {};
    state.hintsRevealed = [];
    state.selectedEvidenceIds = new Set();
    state.accusedSuspectId = null;
    renderBriefing();
    showScreen('screen-briefing');
  }catch(e){
    toast('Unable to generate the case. Please try again.', true);
  }finally{
    state.isGenerating = false;
    if(loader) loader.classList.add('hidden');
    if(btn){
      btn.disabled = false;
      btn.innerHTML = 'Open a New Case File →';
    }
  }
}

function renderBriefing(){
  const c = state.case;
  document.getElementById('brief-crime').textContent = c.crime_type;
  document.getElementById('brief-diff').textContent = c.difficulty;
  document.getElementById('brief-title').textContent = c.title;
  document.getElementById('brief-nsuspects').textContent = (c.suspects||[]).length;
  document.getElementById('brief-nlocations').textContent = (c.locations||[]).length;
  document.getElementById('brief-nclues').textContent = (c.evidence||[]).length;
  document.getElementById('brief-summary').textContent = c.summary || '';
  const v = c.victim || {};
  document.getElementById('brief-victim-name').textContent = v.name || 'Unknown';
  document.getElementById('brief-victim-occ').textContent = v.occupation || '';
  document.getElementById('brief-victim-bg').textContent = v.background || '';
  const banner = document.getElementById('brief-fallback-banner');
  if(c.is_fallback || c.provider === 'offline'){
    if(banner) {
      banner.classList.remove('hidden');
      banner.innerHTML = '<strong>⚡ Offline Demo Mode</strong>: Case generated using pre-packaged forensic scenario without external API keys.';
    }
    toast('⚡ Offline Demo Mode — playing pre-packaged case.');
  } else if(c.provider === 'grok'){
    if(banner) {
      banner.classList.remove('hidden');
      banner.innerHTML = '<strong>🟣 Failover Active</strong>: Case generated by secondary provider (xAI Grok).';
    }
    toast('🟣 Secondary Provider: Grok AI generated this case.');
  } else {
    if(banner) banner.classList.add('hidden');
  }
}

function enterHub(){
  document.getElementById('hub-case-title').textContent = state.case.title;
  const provTag = state.case.provider === 'gemini' ? ' · 🟢 Gemini' : (state.case.provider === 'grok' ? ' · 🟣 Grok' : (state.case.is_fallback ? ' · ⚡ Offline' : ''));
  document.getElementById('hub-case-badge').textContent = state.case.difficulty + ' · ' + state.case.crime_type + provTag;
  updateTabCounts();
  switchTab('locations');
  showScreen('screen-hub');
}

function updateTabCounts(){
  const c = state.case;
  document.getElementById('tab-count-locations').textContent = `${state.visitedLocations.size}/${(c.locations||[]).length}`;
  document.getElementById('tab-count-evidence').textContent = `${state.discoveredEvidence.size}/${(c.evidence||[]).length}`;
  document.getElementById('tab-count-suspects').textContent = (c.suspects||[]).length;
}

function switchTab(tab){
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active', t.dataset.tab===tab));
  const content = document.getElementById('hub-content');
  if(tab==='locations') content.innerHTML = renderLocations();
  else if(tab==='evidence') content.innerHTML = renderEvidence();
  else if(tab==='suspects') content.innerHTML = renderSuspects();
  else if(tab==='hints') content.innerHTML = renderHints();
  else if(tab==='accuse') content.innerHTML = renderAccuse();
}

function renderLocations(){
  const locs = state.case.locations || [];
  return `
    <div class="section-head"><h2>📍 Locations</h2></div>
    <div class="section-desc">Investigate each location to uncover the evidence hidden there.</div>
    <div class="grid-cards">
      ${locs.map(l=>{
        const visited = state.visitedLocations.has(l.id);
        return `
        <div class="card loc-card ${visited?'visited':''}">
          <div class="loc-tag">${(l.image_type||'scene')}</div>
          <h3>${escapeHtml(l.name)}</h3>
          <p>${visited ? escapeHtml(l.description||'') : 'This location has not been searched yet.'}</p>
          ${visited
            ? `<span class="badge badge-green">Searched · ${(l.evidence_ids||[]).length} clue(s) found</span>`
            : `<button class="btn btn-sm btn-primary" onclick="visitLocation('${l.id}')">Investigate →</button>`}
        </div>`;
      }).join('')}
    </div>`;
}

function visitLocation(locId){
  state.visitedLocations.add(locId);
  const loc = (state.case.locations||[]).find(l=>l.id===locId);
  (loc.evidence_ids||[]).forEach(id=>state.discoveredEvidence.add(id));
  updateTabCounts();
  switchTab('locations');
  toast(`Searched ${loc.name} — ${(loc.evidence_ids||[]).length} clue(s) added to the evidence locker.`);
}

function openEvidenceInspect(evidenceId){
  const all = (state.case && state.case.evidence) || [];
  const ev = all.find(e => e.id === evidenceId);
  if(!ev) return;
  document.getElementById('inspect-name').textContent = ev.name || 'Unknown Evidence';
  document.getElementById('inspect-category').textContent = (ev.category || 'Physical Evidence') + ' · ' + (ev.importance || 'Important');
  document.getElementById('inspect-location').textContent = ev.location || 'Crime Scene';
  document.getElementById('inspect-desc').textContent = ev.description || 'No detailed forensic notes recorded.';
  document.getElementById('inspect-relevance').textContent = ev.relevance || 'Correlate this clue against suspect statements and timeline.';
  const stars = ev.stars || (ev.importance === 'Critical' ? 5 : (ev.importance === 'Low' ? 2 : 3));
  document.getElementById('inspect-stars').textContent = '★'.repeat(stars) + '☆'.repeat(Math.max(0, 5 - stars));
  const modal = document.getElementById('evidence-inspect-modal');
  if(modal) modal.classList.remove('hidden');
}

function closeEvidenceInspect(){
  const modal = document.getElementById('evidence-inspect-modal');
  if(modal) modal.classList.add('hidden');
}

window.openEvidenceInspect = openEvidenceInspect;
window.closeEvidenceInspect = closeEvidenceInspect;

function renderEvidence(){
  const all = state.case.evidence || [];
  const found = all.filter(e=>state.discoveredEvidence.has(e.id));
  return `
    <div class="section-head"><h2>🗂 Evidence Locker</h2></div>
    <div class="section-desc">Click any piece of evidence to inspect forensic observations, relevance, and details.</div>
    ${found.length===0 ? `<div class="locked-note">No evidence yet — go investigate a location first.</div>` : `
    <div class="grid-cards">
      ${found.map(e=>`
        <div class="card ev-card" data-imp="${e.importance||'Medium'}" onclick="openEvidenceInspect('${e.id}')" style="cursor:pointer;" title="Click to inspect this clue">
          <div class="meta">${escapeHtml(e.category||'')} · ${escapeHtml(e.location||'')}</div>
          <h3 style="margin:4px 0 6px;">${escapeHtml(e.name)}</h3>
          <p>${escapeHtml(e.description||'')}</p>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">
            <div class="stars">${'★'.repeat(e.stars||3)}${'☆'.repeat(5-(e.stars||3))}</div>
            <button class="btn btn-sm btn-ghost" onclick="event.stopPropagation(); openEvidenceInspect('${e.id}')" style="padding:4px 8px;font-size:11px;">🔍 Inspect Clue</button>
          </div>
        </div>`).join('')}
    </div>`}
  `;
}

function stressClass(s){
  const k = (s||'calm').toLowerCase();
  return 'stress-' + (['calm','defensive','nervous','cornered'].includes(k)?k:'calm');
}

function renderSuspects(){
  const suspects = state.case.suspects || [];
  return `
    <div class="section-head"><h2>🕵 Suspects</h2></div>
    <div class="section-desc">Select a suspect to open interrogation.</div>
    <div class="grid-cards">
      ${suspects.map(s=>{
        const hist = state.chatHistories[s.id];
        const latest = hist && hist.length ? hist[hist.length-1].stress_level : s.stress_level;
        return `
        <div class="card susp-card" onclick="openInterrogation('${s.id}')">
          <div class="susp-top">
            <div class="avatar">${(s.name||'?')[0]}</div>
            <div><h3 style="margin-bottom:2px;">${escapeHtml(s.name)}</h3><div class="meta">${escapeHtml(s.occupation||'')}</div></div>
          </div>
          <p>${escapeHtml(s.relationship||'')}</p>
          <span class="stress-pill ${stressClass(latest)}">${(latest||'Calm')}</span>
        </div>`;
      }).join('')}
    </div>`;
}

function openInterrogation(suspectId){
  state.activeSuspectId = suspectId;
  document.getElementById('hub-content').innerHTML = renderInterrogation();
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active', t.dataset.tab==='suspects'));
  scrollChatToBottom();
  if(!state.chatHistories[suspectId]) loadHistory(suspectId);
}

function renderInterrogation(){
  const suspects = state.case.suspects || [];
  const s = suspects.find(x=>x.id===state.activeSuspectId);
  const hist = state.chatHistories[s.id] || [];
  const latestStress = hist.length ? hist[hist.length-1].stress_level : s.stress_level;
  const evidenceOptions = (state.case.evidence||[]).filter(e=>state.discoveredEvidence.has(e.id));
  return `
    <div class="section-head"><h2>🕵 Interrogation</h2></div>
    <div class="interrogate-wrap">
      <div class="susp-list-mini">
        ${suspects.map(x=>`
          <div class="mini-susp ${x.id===s.id?'active':''}" onclick="openInterrogation('${x.id}')">
            <div class="avatar" style="width:26px;height:26px;font-size:12px;">${x.name[0]}</div>
            <span>${escapeHtml(x.name)}</span>
          </div>`).join('')}
      </div>
      <div class="chat-panel">
        <div class="chat-head">
          <h3>${escapeHtml(s.name)} <span class="stress-pill ${stressClass(latestStress)}" style="margin-left:8px;">${latestStress||'Calm'}</span></h3>
          <div class="chat-details"><b>Occupation:</b> ${escapeHtml(s.occupation||'')} · <b>Relation:</b> ${escapeHtml(s.relationship||'')}<br><b>Alibi:</b> ${escapeHtml(s.alibi||'')}</div>
        </div>
        <div class="chat-log" id="chat-log">
          ${hist.length===0 ? `<div class="empty-chat">No questions asked yet. Start the interrogation below.</div>` :
            hist.map(m=>`<div class="msg ${m.role==='player'?'player':'suspect'}">${escapeHtml(m.message || m.content || '')}</div>`).join('')}
        </div>
        <div class="chat-input-row">
          <select id="evidence-select"><option value="">No evidence</option>
            ${evidenceOptions.map(e=>`<option value="${e.id}">${escapeHtml(e.name)}</option>`).join('')}
          </select>
          <textarea id="question-input" placeholder="Ask a question…"></textarea>
          <button class="btn btn-primary" id="btn-ask" onclick="askQuestion()">Ask</button>
        </div>
      </div>
    </div>`;
}

async function loadHistory(suspectId){
  try{
    const res = await api(`/api/cases/${state.caseId}/interrogate/${suspectId}`);
    state.chatHistories[suspectId] = normalizeHistory(res.history || []);
    if(state.activeSuspectId===suspectId) refreshChatLog();
  }catch(e){}
}

function normalizeHistory(h){
  return h.map(item => ({
    role: item.role || item.speaker || (item.sender==='player'?'player':'suspect'),
    message: item.message || item.content || item.text || '',
    stress_level: item.stress_level,
  }));
}

function refreshChatLog(){
  const hist = state.chatHistories[state.activeSuspectId] || [];
  const log = document.getElementById('chat-log');
  if(!log) return;
  log.innerHTML = hist.length===0 ? `<div class="empty-chat">No questions asked yet. Start the interrogation below.</div>` :
    hist.map(m=>`<div class="msg ${m.role==='player'?'player':'suspect'}">${escapeHtml(m.message)}</div>`).join('');
  scrollChatToBottom();
}

function scrollChatToBottom(){
  const log = document.getElementById('chat-log');
  if(log) log.scrollTop = log.scrollHeight;
}

async function askQuestion(){
  const input = document.getElementById('question-input');
  const evSel = document.getElementById('evidence-select');
  const question = input.value.trim();
  if(!question) return;
  const suspectId = state.activeSuspectId;
  const evidenceId = evSel.value || undefined;

  if(!state.chatHistories[suspectId]) state.chatHistories[suspectId] = [];
  state.chatHistories[suspectId].push({role:'player', message: question});
  refreshChatLog();
  input.value = '';
  const btn = document.getElementById('btn-ask');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';

  try{
    const res = await api(`/api/cases/${state.caseId}/interrogate`, {method:'POST', body:{
      suspect_id: suspectId, question, evidence_id: evidenceId
    }});
    state.chatHistories[suspectId] = normalizeHistory(res.history && res.history.length ? res.history : [
      ...(state.chatHistories[suspectId]||[]),
      {role:'suspect', message: res.response, stress_level: res.stress_level}
    ]);
    refreshChatLog();
    updateSuspectStressBadgeLive(res.stress_level);
  }catch(e){
    state.chatHistories[suspectId].pop();
    refreshChatLog();
  }finally{
    btn.disabled = false; btn.innerHTML = 'Ask';
  }
}

function updateSuspectStressBadgeLive(stress){
  const head = document.querySelector('.chat-head h3 .stress-pill');
  if(head && stress){
    head.textContent = stress;
    head.className = 'stress-pill ' + stressClass(stress);
    head.style.marginLeft='8px';
  }
}

function renderHints(){
  const levels = [1,2,3];
  const labels = {1:'Directional Nudge',2:'Timeline Conflict',3:'Smoking Gun'};
  return `
    <div class="section-head"><h2>💡 Hint Desk</h2></div>
    <div class="section-desc">Stuck? Pull hints one level at a time — each gets more specific.</div>
    <div class="hint-levels">
      ${levels.map(l=>{
        const revealed = state.hintsRevealed.find(h=>h.level===l);
        const canRequest = l===1 || state.hintsRevealed.find(h=>h.level===l-1);
        return `
        <div class="hint-item">
          <div class="hh" style="display:flex;justify-content:space-between;align-items:center;">
            <h4 style="margin:0;">Level ${l} — ${labels[l]}</h4>
            ${revealed ? '' : `<button class="btn btn-sm ${canRequest?'btn-primary':''}" ${canRequest?'':'disabled'} onclick="requestHint(${l})">Reveal</button>`}
          </div>
          ${revealed ? `<div class="hint-text" style="font-family:'Courier Prime',monospace;font-size:13px;color:var(--paper-dim);margin-top:8px;">${escapeHtml(revealed.text)}</div>` :
            (canRequest ? '' : `<div class="hint-text" style="opacity:.5;">Unlock level ${l-1} first.</div>`)}
        </div>`;
      }).join('')}
    </div>`;
}

async function requestHint(level){
  try{
    const res = await api(`/api/cases/${state.caseId}/hint`, {method:'POST', body:{ hint_level: level }});
    state.hintsRevealed.push({level, text: res.hint});
    switchTab('hints');
  }catch(e){}
}

function renderAccuse(){
  const suspects = state.case.suspects || [];
  const evidence = (state.case.evidence||[]).filter(e=>state.discoveredEvidence.has(e.id));
  return `
    <div class="section-head"><h2>⚖ Make Your Accusation</h2></div>
    <div class="section-desc">Choose the culprit, explain the motive, and cite the evidence that proves it.</div>
    <div class="accuse-wrap">
      <div class="field"><label>Who did it?</label>
        ${suspects.map(s=>`
          <div class="radio-card ${state.accusedSuspectId===s.id?'selected':''}" onclick="selectAccused('${s.id}')">
            <div class="avatar" style="width:28px;height:28px;font-size:12px;">${s.name[0]}</div>
            <div><b>${escapeHtml(s.name)}</b> — ${escapeHtml(s.occupation||'')}</div>
          </div>`).join('')}
      </div>
      <div class="field"><label>Motive</label><textarea class="accuse-motive" id="motive-input" placeholder="Explain why they did it…"></textarea></div>
      <div class="field"><label>Supporting Evidence (${evidence.length} discovered)</label>
        ${evidence.length===0 ? `<div class="locked-note">No evidence discovered yet — investigate locations first.</div>` :
          evidence.map(e=>`
            <label class="checkline">
              <input type="checkbox" ${state.selectedEvidenceIds.has(e.id)?'checked':''} onchange="toggleEvidenceSelect('${e.id}', this.checked)">
              <span><b>${escapeHtml(e.name)}</b> — ${escapeHtml(e.description||'')}</span>
            </label>`).join('')}
      </div>
      <button class="btn btn-danger" style="width:100%;padding:13px;margin-top:10px;" onclick="submitAccusation()">Present Case to the Judge →</button>
    </div>`;
}

function selectAccused(id){ state.accusedSuspectId = id; switchTab('accuse'); }
function toggleEvidenceSelect(id, checked){
  if(checked) state.selectedEvidenceIds.add(id); else state.selectedEvidenceIds.delete(id);
}

async function submitAccusation(){
  if(!state.accusedSuspectId){ toast('Select a suspect to accuse first.', true); return; }
  const motive = document.getElementById('motive-input').value.trim();
  if(!motive){ toast('Explain the motive before presenting your case.', true); return; }
  try{
    const res = await api(`/api/cases/${state.caseId}/judge`, {method:'POST', body:{
      accused_suspect_id: state.accusedSuspectId,
      motive_provided: motive,
      evidence_ids: Array.from(state.selectedEvidenceIds),
      player_name: state.playerName,
      hints_used: state.hintsRevealed.length,
    }});
    renderVerdict(res.verdict);
    showScreen('screen-verdict');
  }catch(e){}
}

function renderVerdict(v){
  const correct = !!v.is_correct;
  const score = v.score ?? 0;
  const truth = v.ground_truth || {};
  document.getElementById('verdict-content').innerHTML = `
    <div class="verdict-stamp ${correct?'':'wrong'}">${correct ? 'Case Closed' : 'Wrong Suspect'}</div>
    <h1 style="margin:0 0 4px;">Detective Score: ${score}/100</h1>
    <p style="color:var(--muted);">${state.playerName}, here's how the Judge evaluated your case.</p>
    <div class="verdict-explain">${escapeHtml(v.judge_explanation || v.explanation || '')}</div>
    <div class="clue-cols">
      <div class="clue-col"><h4 style="color:var(--green);">Supported by evidence</h4>
        <ul>${(v.supported_clues||[]).map(c=>`<li>${escapeHtml(c)}</li>`).join('') || '<li>None cited</li>'}</ul></div>
      <div class="clue-col"><h4 style="color:var(--red-bright);">Ignored / missed</h4>
        <ul>${(v.ignored_clues||[]).map(c=>`<li>${escapeHtml(c)}</li>`).join('') || '<li>None</li>'}</ul></div>
    </div>
    <div class="truth-box">
      <div><b>The truth:</b> ${escapeHtml(truth.criminal_name||'')} was behind it.</div>
      <div style="margin-top:8px;"><b>Motive:</b> ${escapeHtml(truth.motive||'')}</div>
      <div style="margin-top:8px;"><b>How it happened:</b> ${escapeHtml(truth.how_it_was_done||'')}</div>
    </div>
    <div style="display:flex; gap:12px; justify-content:center; margin-top:26px; flex-wrap:wrap;">
      <button class="btn" onclick="showLeaderboard()">View Leaderboard</button>
      <button class="btn btn-primary" onclick="replayCase(state.caseId)">🔄 Replay This Case</button>
      <button class="btn btn-ghost" onclick="showScreen('screen-setup')">Start Another Case →</button>
      <button class="btn btn-ghost" onclick="goHome()">Home</button>
    </div>`;
}

async function showLeaderboard(){
  showScreen('screen-leaderboard');
  const body = document.getElementById('lb-body');
  body.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);"><span class="spinner"></span>Loading…</td></tr>`;
  try{
    const res = await api('/api/cases/leaderboard');
    const rows = res.leaderboard || [];
    body.innerHTML = rows.length ? rows.map((r,i)=>`
      <tr>
        <td>${i+1}</td>
        <td>${escapeHtml(r.player_name||'Detective')}</td>
        <td>${escapeHtml(r.case_title || r.case_id || '')}</td>
        <td>${r.score ?? '-'}</td>
        <td>${r.is_correct ? '✅ Solved' : '❌ Missed'}</td>
      </tr>`).join('') : `<tr><td colspan="5" style="text-align:center;color:var(--muted);">No cases solved yet — be the first.</td></tr>`;
  }catch(e){
    body.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);">Couldn't load the leaderboard.</td></tr>`;
  }
}

function escapeHtml(str){
  return String(str ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

async function showCaseHistory(){
  showScreen('screen-history');
  const container = document.getElementById('history-cases-list');
  container.innerHTML = `<div style="text-align:center;padding:30px;color:var(--muted);"><span class="spinner"></span> Accessing central archives…</div>`;
  try{
    const res = await api('/api/cases');
    const cases = res.cases || [];
    if(!cases.length){
      container.innerHTML = `<div class="locked-note">No cases archived yet. Start a new investigation!</div>`;
      return;
    }
    container.innerHTML = cases.map(c => {
      let badgeClass = 'badge-amber';
      let statusLabel = c.status || 'In Progress';
      if(statusLabel === 'Solved') badgeClass = 'badge-green';
      else if(statusLabel === 'Failed') badgeClass = 'badge-red';

      return `
      <div class="card" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px;">
            <span class="badge ${badgeClass}">${statusLabel}</span>
            <span class="badge">${escapeHtml(c.crime_type)} · ${escapeHtml(c.difficulty)}</span>
            <span style="font-family:'Courier Prime',monospace;font-size:11px;color:var(--muted);">${escapeHtml(c.case_id)}</span>
          </div>
          <h3 style="margin:0 0 4px;font-size:17px;">${escapeHtml(c.title)}</h3>
          <div style="font-size:12px;color:var(--muted);">Victim: <b>${escapeHtml(c.victim_name)}</b> · ${c.log_count || 0} interrogation records</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
          <button class="btn btn-sm btn-ghost" onclick="replayCase('${c.case_id}')" title="Replay this case from the beginning">
            🔄 Replay
          </button>
          <button class="btn btn-sm btn-primary" onclick="resumeCase('${c.case_id}')">
            ${c.is_completed ? 'Review Verdict →' : 'Resume Investigation →'}
          </button>
        </div>
      </div>`;
    }).join('');
  }catch(e){
    container.innerHTML = `<div class="locked-note" style="color:var(--red-bright);">Failed to load case history. Check backend connection.</div>`;
  }
}

function lookupCaseById(){
  const input = document.getElementById('hist-case-id-input');
  const id = input ? input.value.trim() : '';
  if(!id){
    toast('Please enter a Case ID to search.', true);
    return;
  }
  resumeCase(id);
}

async function replayCase(caseId){
  if(!caseId) return;
  try{
    toast(`Replaying case ${caseId}…`);
    const res = await api(`/api/cases/${caseId}/replay`, {method: 'POST'});
    if(!res || !res.case){
      throw new Error(res?.detail || 'Failed to replay case');
    }
    state.case = res.case;
    state.caseId = res.case.case_id || caseId;
    state.visitedLocations = new Set();
    state.discoveredEvidence = new Set();
    state.chatHistories = {};
    state.hintsRevealed = [];
    state.selectedEvidenceIds = new Set();
    state.accusedSuspectId = null;

    renderBriefing();
    showScreen('screen-briefing');
    toast(`Case ${state.case.title} reset and ready for investigation!`);
  }catch(err){
    toast(`Could not replay case: ${err.message}`, true);
  }
}

async function resumeCase(caseId){
  try{
    toast(`Loading case file ${caseId}…`);
    const res = await api(`/api/cases/${caseId}`);
    state.case = res.case;
    state.caseId = caseId;
    state.visitedLocations = new Set();
    state.discoveredEvidence = new Set();
    state.chatHistories = {};
    state.hintsRevealed = [];
    state.selectedEvidenceIds = new Set();
    state.accusedSuspectId = null;

    // Fetch all interrogation logs
    try{
      const logsRes = await api(`/api/cases/${caseId}/logs`);
      if(logsRes.interrogations){
        for(const [sId, logs] of Object.entries(logsRes.interrogations)){
          state.chatHistories[sId] = normalizeHistory(logs);
        }
      }
    }catch(e){}

    // Check if verdict exists
    let verdict = null;
    try{
      const vRes = await api(`/api/cases/${caseId}/verdict`);
      verdict = vRes.verdict;
    }catch(e){}

    // If completed, show verdict
    if(verdict){
      (state.case.locations || []).forEach(l => state.visitedLocations.add(l.id));
      (state.case.evidence || []).forEach(e => state.discoveredEvidence.add(e.id));
      renderVerdict(verdict);
      showScreen('screen-verdict');
      toast(`Loaded completed case: ${state.case.title}`);
    }else{
      // Recover evidence mentioned in logs
      const allEv = state.case.evidence || [];
      for(const logs of Object.values(state.chatHistories)){
        for(const entry of logs){
          for(const ev of allEv){
            if((entry.message || '').includes(ev.name)){
              state.discoveredEvidence.add(ev.id);
            }
          }
        }
      }
      // Recover visited locations
      for(const loc of (state.case.locations || [])){
        if((loc.evidence_ids || []).some(id => state.discoveredEvidence.has(id))){
          state.visitedLocations.add(loc.id);
        }
      }
      enterHub();
      toast(`Resumed investigation: ${state.case.title}`);
    }
  }catch(err){
    toast(`Could not load case ${caseId}: ${err.message}`, true);
  }
}

window.showLeaderboard = showLeaderboard;
window.showCaseHistory = showCaseHistory;
window.lookupCaseById = lookupCaseById;
window.resumeCase = resumeCase;
window.replayCase = replayCase;

