'use strict';
const $ = id => document.getElementById(id);
let snapshot, running = false, refreshSequence = 0;
const number = (n, digits=1) => n == null ? 'Unavailable' : Number(n).toLocaleString('en-US', {maximumFractionDigits: digits});
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, payload) {
  const response = await fetch(path, payload ? {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)} : {});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed. Please retry.');
  return data;
}
function notice(message='') { $('notice').textContent=message; $('notice').hidden=!message; }
function metric(id, value, unit) { $(id).innerHTML = `${number(value)} <small>${escapeHTML(unit)}</small>`; }
function plot(rows) {
  if (!rows.length) { $('chart').textContent='No observations available for this date.'; $('chart-table').replaceChildren(); return; }
  const keys=['pv_ac_power_w','load_power_w','grid_import_w'];
  const palette=getComputedStyle(document.documentElement);
  const colors=['--green','--orange','--blue'].map(token=>palette.getPropertyValue(token).trim());
  const max=Math.max(1000,...rows.flatMap(r=>keys.map(k=>r[k]??0)));
  const ceiling=Math.ceil(max/1000)*1000;
  const x=i=>46+(i/Math.max(1,rows.length-1))*510, y=v=>215-v/ceiling*180;
  let svg='<svg viewBox="0 0 580 250" xmlns="http://www.w3.org/2000/svg"><title>Daily power in kilowatts, Africa/Lagos time</title>';
  for(let i=0;i<=4;i++) { const v=ceiling*i/4; svg+=`<line x1="46" y1="${y(v)}" x2="556" y2="${y(v)}" stroke="#edf0e9"/><text x="33" y="${y(v)+3}" text-anchor="end" fill="#8d9b8a" font-size="9">${number(v/1000)}</text>`; }
  keys.forEach((key,k)=>{let d='',connected=false; rows.forEach((r,i)=>{if(r[key]==null){connected=false;return;} d+=`${connected?'L':'M'}${x(i).toFixed(2)},${y(r[key]).toFixed(2)} `;connected=true;});svg+=`<path d="${d}" fill="none" stroke="${colors[k]}" stroke-width="${k===2?2.6:2}" stroke-linejoin="round" stroke-linecap="round"/>`;});
  [0,6,12,18,23].forEach(hour=>{const i=rows.findIndex(r=>Number(r.timestamp.slice(11,13))===hour);if(i>=0)svg+=`<text x="${x(i)}" y="239" text-anchor="middle" fill="#8d9b8a" font-size="9">${String(hour).padStart(2,'0')}:00</text>`;});
  $('chart').innerHTML=svg+'</svg>';
  $('chart-table').innerHTML='<table><thead><tr><th>Time</th><th>Solar W</th><th>Load W</th><th>Grid W</th></tr></thead><tbody>'+rows.map(r=>`<tr><td>${escapeHTML(r.timestamp.slice(11,16))}</td>${keys.map(k=>`<td>${number(r[k])}</td>`).join('')}</tr>`).join('')+'</tbody></table>';
}
async function refresh(day) {
  const sequence=++refreshSequence;
  $('refresh').disabled=true;
  try {
    const d=await api('/api/dashboard'+(day?'?day='+encodeURIComponent(day):''));
    if(sequence!==refreshSequence)return;
    snapshot=d;
    $('installation').textContent=d.installation+` · ${d.equipment.pv_kwp} kWp PV / ${d.equipment.inverter_rating_w/1000} kW inverter / ${d.equipment.battery_nominal_kwh} kWh battery`;
    $('snapshot-time').textContent=d.timestamp+' · Africa/Lagos';
    $('system-state').textContent='Inverter · '+d.inverter_state.replaceAll('_',' ');
    $('alarm').textContent=d.values.active_alarm?'Active alarm · '+d.values.active_alarm:'No active alarm at snapshot';
    metric('pv',d.values.pv_generation_w/1000,'kW');metric('load',d.values.load_w/1000,'kW');metric('soc',d.values.battery_soc_pct,'%');metric('grid',d.values.grid_import_w/1000,'kW');
    const charge=d.values.battery_soc_pct;
    $('battery-level').value=Number.isFinite(charge)?Math.max(0,Math.min(100,charge)):0;
    $('battery-level').setAttribute('aria-valuetext',Number.isFinite(charge)?number(charge)+' percent':'Unavailable');
    $('runway').textContent=d.values.estimated_battery_runway_hours==null?'Runway unavailable':number(d.values.estimated_battery_runway_hours,2)+' h estimated runway';
    $('export').textContent=number(d.grid_export_w/1000)+' kW exported to grid';
    $('day').min=d.first_day;$('day').max=d.last_day;$('day').value=d.selected_day;
    plot(d.chart);$('chart-note').textContent=`Five-minute observations · ${d.missing_rows} incomplete rows on this day. Gaps remain visible.`;
    $('suggestions').replaceChildren();
    d.suggestions.forEach(([label,question])=>{const b=document.createElement('button');b.textContent=label;b.title=question;b.disabled=running;b.onclick=()=>{$('question').value=question;$('question').focus();};$('suggestions').append(b);});
    $('mode').querySelector('[value="live"]').disabled=!d.live_configured;
    $('snapshot-json').textContent=JSON.stringify(d.status_evidence,null,2);
    notice(d.snapshot_is_latest?'':`The latest received row is incomplete. Status shows the last complete snapshot: ${d.timestamp}.`);
    updateMode();
  } catch(e) {if(sequence===refreshSequence)notice(e.message);} finally {if(sequence===refreshSequence)$('refresh').disabled=false;}
}
function updateMode() {
  $('mode-note').textContent=$('mode').value==='live'
    ? `Claude · ${snapshot?.model||'configured model'} · follow-up context retained · API charges apply.`
    : 'Offline questions are independent. '+(snapshot?.live_configured?'Choose Claude for follow-up conversation.':'Configure .env and refresh to enable Claude.');
}
function renderTurn(turn) {
  const welcome=$('messages').querySelector('.welcome');if(welcome)welcome.remove();
  const article=document.createElement('article');article.className='turn';
  const q=document.createElement('div');q.className='question';q.textContent=turn.question;article.append(q);
  const answer=document.createElement('div');answer.className='answer';answer.textContent=turn.answer;article.append(answer);
  const meta=document.createElement('div');meta.className='turn-meta';meta.textContent=`${turn.mode==='live'?'Claude':'Deterministic'} · ${turn.status} · ${number(turn.elapsed_seconds,2)}s`;article.append(meta);
  turn.tools.forEach(tool=>{
    const details=document.createElement('details');details.className='receipt';
    const summary=document.createElement('summary');summary.textContent='Evidence · '+tool.name.replaceAll('_',' ');details.append(summary);
    const e=tool.evidence;
    if(e) {
      const finding=document.createElement('p');finding.className='evidence-title';finding.textContent=e.finding;details.append(finding);
      const quality=document.createElement('p');quality.textContent=`Confidence: ${e.confidence||'not stated'} · Data: ${e.data_quality?.sufficient===false?'insufficient':'sufficient'}`;details.append(quality);
      if(e.data_window){const window=document.createElement('p');window.textContent=`Window: ${e.data_window.start} → ${e.data_window.end}`;details.append(window);}
      const table=document.createElement('div');table.className='table-scroll';table.innerHTML='<table><thead><tr><th>Measurement</th><th>Value</th><th>Unit</th></tr></thead><tbody>'+(e.measurements||[]).map(m=>`<tr><td>${escapeHTML(m.name.replaceAll('_',' '))}</td><td>${escapeHTML(typeof m.value==='object'?JSON.stringify(m.value):m.value)}</td><td>${escapeHTML(m.unit)}</td></tr>`).join('')+'</tbody></table>';details.append(table);
    }
    const raw=document.createElement('details');const title=document.createElement('summary');title.textContent='Full receipt, assumptions & alternatives';raw.append(title);const pre=document.createElement('pre');pre.textContent=JSON.stringify(tool,null,2);raw.append(pre);details.append(raw);article.append(details);
  });
  $('messages').append(article);$('messages').scrollTop=$('messages').scrollHeight;
}
function setBusy(value){running=value;$('send').disabled=value;$('reset').disabled=value;$('download').disabled=value;$('question').disabled=value;$('mode').disabled=value||$('messages').querySelector('.turn')!==null;$('suggestions').querySelectorAll('button').forEach(b=>b.disabled=value);$('busy').textContent=value?'Reading telemetry and preparing evidence…':'Answers grounded in analytical evidence';}
$('ask-form').onsubmit=async e=>{e.preventDefault();if(running)return;const question=$('question').value.trim();if(!question)return;setBusy(true);notice();try{const turn=await api('/api/ask',{question,mode:$('mode').value});renderTurn(turn);$('question').value='';}catch(err){notice(err.message);}finally{setBusy(false);$('question').focus();}};
$('question').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('ask-form').requestSubmit();}};
$('mode').onchange=updateMode;
$('day').onchange=()=>refresh($('day').value);
$('refresh').onclick=()=>refresh($('day').value);
$('reset').onclick=async()=>{if(!confirm('Start a new conversation? Export first if you want to keep this session.'))return;try{await api('/api/reset',{});$('messages').replaceChildren();$('mode').disabled=false;$('question').value='';notice();}catch(e){notice(e.message);}};
$('download').onclick=async()=>{try{const data=await api('/api/export');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='intelligent-logger-session-'+new Date().toISOString().replaceAll(':','-')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){notice(e.message);}};
$('snapshot-evidence').onclick=()=>$('evidence-dialog').showModal();$('close-dialog').onclick=()=>$('evidence-dialog').close();
async function init(){await refresh();try{const session=await api('/api/session');session.turns.forEach(renderTurn);if(session.mode)$('mode').value=session.mode;setBusy(false);updateMode();}catch(e){notice(e.message);}}
init();
