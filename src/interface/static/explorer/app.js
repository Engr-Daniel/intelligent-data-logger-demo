"use strict";

const ORDER = ["customer_overload","cloudy_day_generation_drop","gradual_efficiency_decline","battery_degradation_signature","sensor_dropout","grid_outage_islanding"];
const META = {
  customer_overload:{
    short:"Overload spike",date:"08 Aug · 19:30–20:05",injection:"A sustained load above the 5 kW inverter rating is introduced before the overload alarm and derating. The alarm is recorded at 19:55.",
    channels:["load_power_w","battery_discharge_w","inverter_alarm_code","inverter_operating_state","grid_available"],
    metrics:[["Peak load",6403.9,"6,403.9 W",7000,"amber"],["Inverter rating",5000,"5,000 W",7000,"secondary"]],
    metricNote:"Same power scale. The evidence window starts five minutes before the injected interval.",
    reasoning:["Check the load against the configured inverter rating before the alarm.","Cross-reference the inverter alarm and battery discharge with the load window.","Report overload as the leading technical explanation; do not assign customer responsibility or warranty liability."],
    m5:"PASS",m5note:"The frozen M5 baseline already detected and explained the overload."
  },
  cloudy_day_generation_drop:{
    short:"Cloudy-day PV drop",date:"05 Aug · 09:00–15:55",injection:"Cloud cover reduces irradiance during daytime, lowering PV output without an inverter fault.",
    channels:["irradiance_wm2","cloud_cover_pct","pv_ac_power_w","inverter_alarm_code","inverter_operating_state"],
    metrics:[["PV · surrounding days",4327.9,"4,327.9 W",5000,"secondary"],["PV · cloudy window",1685.9,"1,685.9 W",5000,""],["Irradiance · surrounding days",719.4,"719.4 W/m²",800,"secondary"],["Irradiance · cloudy window",272.5,"272.5 W/m²",800,""]],
    metricNote:"The paired bars use separate scales for PV power and irradiance; each target is compared with the same daytime hours on surrounding days.",
    reasoning:["Compare PV output with the same daytime hours on surrounding days.","Check whether irradiance falls in parallel, then inspect inverter alarms and state.","Prefer weather-related low irradiance over an inverter fault when the two drops track closely and no alarm appears."],
    m5:"PASS",m5note:"The frozen M5 baseline distinguished weather from fault."
  },
  gradual_efficiency_decline:{
    short:"Gradual PV decline",date:"20 Aug – 15 Nov",injection:"A smooth PV performance-factor loss is injected, reaching an 8% final loss. The record is examined over the 120-day observation window.",
    channels:["irradiance_wm2","ambient_temp_c","pv_ac_power_w","performance_ratio"],
    metrics:[["Early median normalized ratio",0.965,"0.9650",1,"secondary"],["Late median normalized ratio",0.8878,"0.8878",1,""]],
    metricNote:"Ratios are normalized for measured irradiance and adjusted for temperature; clipping samples are excluded.",
    reasoning:["Calculate expected PV output using measured irradiance and temperature.","Exclude clipping and compare daily normalized performance through the observation period.","Identify a sustained decline; do not treat this signature alone as proof of a particular physical mechanism."],
    m5:"PASS",m5note:"The frozen M5 baseline found the longitudinal normalized trend."
  },
  battery_degradation_signature:{
    short:"Battery degradation",date:"15 Aug – 28 Nov",injection:"The simulator gradually reduces usable battery capacity by 6%. This latent injected state is withheld from the operational diagnostic.",
    channels:["battery_soc_pct","battery_charge_w","battery_discharge_w","timestamp","configured_efficiencies"],
    metrics:[["Early estimated usable capacity",9000,"9.000 kWh",10000,"secondary"],["Late estimated usable capacity",8490.7,"8.491 kWh",10000,""]],
    metricNote:"The 5.66% estimate uses observed SOC changes and energy flows. It is a controlled-demo estimate, not field battery state of health.",
    reasoning:["Estimate capacity from observed SOC movement and charge/discharge power using configured efficiencies.","Filter implausible intervals, aggregate daily medians, and compare early with late estimates.","Report a capacity-decline signature with its assumptions; never read the simulator's latent capacity field."],
    m5:"CAPABILITY GAP",m5note:"M5 had no observed-flow capacity diagnostic. M6 added one without changing the scoring rubric."
  },
  sensor_dropout:{
    short:"Telemetry dropout",date:"18 Sep · 12:00–12:45",injection:"Fifteen sensor and telemetry fields are intentionally blank for nine consecutive five-minute readings.",
    channels:["irradiance_wm2","pv_ac_power_w","battery_soc_pct","grid_import_w","inverter_temp_c"],
    metrics:[["Rows with missing telemetry",9,"9 rows",9,"amber"],["Missing cells",135,"135 cells",135,""]],
    metricNote:"A single contiguous 45-minute gap. Missing readings are absence of evidence, not zero device output.",
    reasoning:["Detect contiguous missing rows from observed values and the expected five-minute cadence.","Localize the gap to 12:00–12:45 rather than only naming the affected day.","Abstain from causal diagnosis inside the gap because the necessary operational evidence is missing."],
    m5:"PARTIAL",m5note:"M5 detected missingness but localized it only to a day. M6 found the exact interval."
  },
  grid_outage_islanding:{
    short:"Grid outage / islanding",date:"10 Oct · 21:35–22:35",injection:"Utility availability is switched off for 60 minutes before dispatch. The inverter enters islanded backup operation; a configured 30% battery reserve supports backup use.",
    channels:["grid_available","grid_import_w","grid_export_w","inverter_operating_state","battery_discharge_w","battery_soc_pct","load_requested_power_w","load_power_w","unmet_load_w"],
    metrics:[["Mean grid import · before",66.6,"66.6 W",100,"secondary"],["Mean grid import · outage",0,"0 W",100,""],["Immediate battery discharge increase",377.1,"377.1 W",500,"amber"],["Battery SOC drop",12.76,"12.76 points",20,""]],
    metricNote:"Aggregates are not a five-minute trace. The event maintained all requested load, with 0 Wh unmet load and restoration afterward.",
    reasoning:["Require explicit grid unavailability and the islanded inverter state; zero import by itself is insufficient.","Check grid exchange, immediate battery response, SOC change and requested-versus-served load.","Explain backup operation and restoration; verify local energy balance and disclose any modeled unmet load."],
    m5:"NOT EVALUATED",m5note:"This sixth required scenario was added in M6; the frozen M5 report covered five scenarios."
  }
};
const MILESTONES=[
  ["M1","Generate","120 days of five-minute synthetic telemetry with scripted events and a separate oracle."],
  ["M2","Validate","Schema, missingness, SOC bounds and explicit interval energy balance in the operational store."],
  ["M3","Analyze","Deterministic tools compare weather, load, PV trend, battery, data quality and grid behavior."],
  ["M4","Reason","Approved tools form evidence objects and support offline answers or a configured tool-use loop."],
  ["M5","Evaluate","Freeze the baseline and score detection, localization, diagnosis, evidence, calibration and abstention."],
  ["M6","Resolve","Add observed-flow battery estimation, precise gap localization and required islanding; rerun the unchanged rubric."]
];
let dataset, selected, activeMilestone=0;
const esc = v => String(v ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const nice = v => String(v).replaceAll("_"," ").replace(/\b\w/g,c=>c.toUpperCase());
const fmtTime = iso => {
  const d=new Date(iso);
  return new Intl.DateTimeFormat("en-GB",{timeZone:"Africa/Lagos",day:"2-digit",month:"short",year:"numeric",hour:"2-digit",minute:"2-digit",hour12:false}).format(d)+" WAT";
};
const dayNumber = iso => (Date.parse(iso.slice(0,10)+"T00:00:00Z")-Date.parse("2026-08-01T00:00:00Z"))/86400000;

function selectScenario(key,{focus=false}={}){
  if(!dataset || !META[key]) throw new Error("Unknown scenario");
  selected=key;
  history.replaceState(null,"",location.pathname+"?scenario="+encodeURIComponent(key));
  renderSelection();
  if(focus) document.querySelector("#detail-title")?.focus();
  return {scenario:key,result:dataset.scenarios.find(s=>s.event_type===key).overall};
}
function renderSelection(){
  const s=dataset.scenarios.find(x=>x.event_type===selected);
  document.querySelectorAll("[data-scenario]").forEach(el=>{
    const on=el.dataset.scenario===selected;
    el.classList.toggle("selected",on);
    if(el.classList.contains("scenario-button")) el.setAttribute("aria-pressed",String(on));
    if(el.classList.contains("timeline-row")) el.setAttribute("aria-current",on?"true":"false");
  });
  document.querySelector("#detail-content").innerHTML=detailHTML(s);
  if(selected==='grid_outage_islanding')renderOutage();
}
function renderControls(){
  const list=document.querySelector("#scenario-list");
  list.innerHTML=ORDER.map((key,i)=>'<button type="button" class="scenario-button" data-scenario="'+key+'" aria-pressed="false"><span class="number">'+String(i+1).padStart(2,"0")+'</span><span>'+esc(META[key].short)+'</span></button>').join("");
  list.addEventListener("click",e=>{const button=e.target.closest("[data-scenario]");if(button)selectScenario(button.dataset.scenario)});
  const timeline=document.querySelector("#timeline");
  timeline.innerHTML=[...ORDER].sort((a,b)=>dayNumber(dataset.scenarios.find(s=>s.event_type===a).ground_truth.start)-dayNumber(dataset.scenarios.find(s=>s.event_type===b).ground_truth.start)).map(key=>{
    const gt=dataset.scenarios.find(s=>s.event_type===key).ground_truth;
    const left=Math.max(0,dayNumber(gt.start)/120*100),width=Math.max(.75,(dayNumber(gt.end)-dayNumber(gt.start)+1)/120*100);
    return '<button type="button" class="timeline-row" data-scenario="'+key+'" aria-label="Select '+esc(META[key].short)+'"><span class="timeline-label">'+esc(META[key].short)+'</span><span class="track"><svg class="event-svg" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true"><rect x="'+left.toFixed(2)+'" y="1" width="'+Math.min(width,100-left).toFixed(2)+'" height="8" rx="1"/></svg></span></button>';
  }).join("");
  timeline.addEventListener("click",e=>{const button=e.target.closest("[data-scenario]");if(button)selectScenario(button.dataset.scenario,{focus:true})});
  renderWorkflow();
}
function renderWorkflow(){
  const el=document.querySelector("#workflow");
  el.innerHTML=MILESTONES.map(([code,title,desc],i)=>'<button class="workflow-step '+(i===activeMilestone?"active":"")+'" type="button" data-milestone="'+i+'" aria-pressed="'+(i===activeMilestone)+'"><span>'+code+'</span><strong>'+title+'</strong><small>'+esc(desc.split(".")[0])+'</small></button>').join("")+'<div class="workflow-note" role="status"><strong>'+MILESTONES[activeMilestone][0]+' · '+MILESTONES[activeMilestone][1]+':</strong> '+esc(MILESTONES[activeMilestone][2])+'</div>';
  el.onclick=e=>{const button=e.target.closest("[data-milestone]");if(button){activeMilestone=Number(button.dataset.milestone);renderWorkflow()}};
}
function metricsHTML(s){
  const m=META[s.event_type];
  return m.metrics.map(([label,num,value,scale,tone])=>'<div class="metric-row '+tone+'"><div class="metric-head"><span>'+esc(label)+'</span><strong>'+esc(value)+'</strong></div><span class="scale-label">Scale: 0–'+esc(scale)+' (units as labelled)</span><div class="meter" role="img" aria-label="'+esc(label+': '+value)+'"><svg viewBox="0 0 100 6" preserveAspectRatio="none" aria-hidden="true"><rect width="'+Math.max(0,Math.min(100,num/scale*100)).toFixed(1)+'" height="6" rx="2"/></svg></div></div>').join("");
}
function measuresHTML(items){
  return items.map(x=>{
    const value=Array.isArray(x.value)?x.value.join(", "):typeof x.value==="boolean"?String(x.value):String(x.value);
    return '<div class="measurement"><span class="label">'+esc(nice(x.name))+'</span><span class="value '+(value.length>35?"long":"")+'">'+esc(value)+' '+(x.unit&&x.unit!=="categorical"&&x.unit!=="timestamp"&&x.unit!=="fields"&&x.unit!=="boolean"?esc(x.unit):"")+'</span></div>';
  }).join("");
}
function detailHTML(s){
  const m=META[s.event_type],e=s.evidence,gt=s.ground_truth;
  const prominent=e.measurements.filter(x=>!Array.isArray(x.value)&&String(x.value).length<34).slice(0,6);
  const fields=gt.fields_affected?'<div class="truth-fields">'+gt.fields_affected.map(x=>'<span>'+esc(x)+'</span>').join("")+'</div>':"";
  const alternatives=e.alternatives_checked?.length?'<details><summary>Alternatives checked ('+e.alternatives_checked.length+')</summary><ul>'+e.alternatives_checked.map(a=>'<li><strong>'+esc(nice(a.cause||a.alternative))+'</strong> — '+esc(a.result|| (a.supported?"supported":"not supported"))+'</li>').join("")+'</ul></details>':"";
  const assumptions=e.assumptions?.length?'<details><summary>Assumptions and thresholds ('+e.assumptions.length+')</summary><ul>'+e.assumptions.map(a=>'<li><code>'+esc(a.name)+'</code>: '+esc(a.value)+'</li>').join("")+'</ul></details>':"";
  const warnings=e.data_quality?.warnings?.length?'<p class="caution">'+e.data_quality.warnings.map(esc).join(" ")+'</p>':"";
  return '<div class="detail-header"><div class="detail-topline"><span class="eyebrow">SCENARIO '+String(ORDER.indexOf(s.event_type)+1).padStart(2,"0")+' / 06</span><span class="pill">M6 '+esc(s.overall)+'</span></div><h2 id="detail-title" tabindex="-1">'+esc(m.short)+'</h2><p>'+esc(e.finding)+'</p><div class="detail-window"><span>Injected · '+esc(m.date)+' WAT</span><span>Evidence · '+esc(fmtTime(e.data_window.start))+' → '+esc(fmtTime(e.data_window.end))+'</span></div></div>'+
  '<div class="detail-grid">'+
    '<section class="panel oracle"><span class="eyebrow">01 / INJECTED CONDITION · EVALUATION ORACLE</span><h3>What was programmed</h3><p>'+esc(m.injection)+'</p><div class="receipt"><p><strong>Ground-truth cause:</strong> '+esc(gt.true_cause)+'.</p><p class="caution">This event log is withheld from operational analytics and used only to score the result.</p>'+fields+'</div></section>'+
    '<section class="panel"><span class="eyebrow">02 / RELEVANT TELEMETRY</span><h3>Signals to inspect</h3><div class="metric-list">'+metricsHTML(s)+'</div><p class="metric-caption">'+esc(m.metricNote)+'</p><div class="signal-tags">'+m.channels.map(x=>'<span>'+esc(x)+'</span>').join("")+'</div></section>'+
    '<section class="panel"><span class="eyebrow">03 / DIAGNOSTIC EVIDENCE</span><h3>Recorded measurements</h3><div class="measurement-grid">'+measuresHTML(prominent)+'</div><details><summary>All '+e.measurements.length+' recorded measurements</summary><div class="measurement-grid spaced">'+measuresHTML(e.measurements)+'</div></details>'+alternatives+assumptions+'<div class="receipt"><p><strong>Approved tool:</strong> '+e.supporting_tools.map(x=>'<code>'+esc(x)+'()</code>').join(", ")+'</p><p><strong>Evidence quality:</strong> '+(e.data_quality.sufficient?"sufficient for the stated finding":"insufficient for causal diagnosis")+' · confidence '+esc(e.confidence)+'</p>'+warnings+'</div></section>'+
    '<section class="panel"><span class="eyebrow">04 / EXPECTED REASONING</span><h3>Question → evidence → answer</h3><p class="finding">“'+esc(e.question)+'”</p><ol class="reasoning-list spaced">'+m.reasoning.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ol><div class="receipt"><p><strong>Leading supported label:</strong> <code>'+esc(e.candidate_cause)+'</code></p><p class="metric-caption">This is a reading guide to the deterministic evidence and offline answer path, not a live model transcript.</p></div></section>'+
    '<section class="panel wide"><span class="eyebrow">05 / RESULT · FROZEN M5 VS FINAL M6</span><h3>What the evaluation recorded</h3><div class="comparison"><div class="'+(m.m5==="PASS"?"":"m5-gap")+'"><span>M5 historical baseline</span><strong>'+esc(m.m5)+'</strong></div><div class="m6-pass"><span>M6 dry run</span><strong>'+esc(s.overall)+'</strong></div></div><p class="spaced">'+esc(m.m5note)+'</p><div class="result-grid">'+Object.entries(s.dimensions).map(([name,d])=>'<div class="dimension '+(d.status==="N/A"?"na":"")+'" title="'+esc(d.rationale)+'"><span>'+esc(nice(name))+'</span><strong>'+esc(d.status)+'</strong></div>').join("")+'</div><p class="metric-caption">Six separate rubric dimensions. N/A means abstention is not required for a scenario with adequate evidence. These passes are controlled functional checks.</p><details><summary>Scoring rationales</summary><ul>'+Object.entries(s.dimensions).map(([name,d])=>'<li><strong>'+esc(nice(name))+' · '+esc(d.status)+':</strong> '+esc(d.rationale)+'</li>').join("")+'</ul></details></section>'+
  '</div>'+(s.event_type==='grid_outage_islanding'?'<section class="panel trace-panel"><span class="eyebrow">FIVE-MINUTE OBSERVATIONS</span><h3>Before, during and after the outage</h3><div id="outage-trace">Loading archived telemetry…</div></section>':'');
}
function registerWebMCP(){
  const ctx=document.modelContext;
  if(!ctx?.registerTool)return;
  const lifecycle=new AbortController();
  try{Promise.resolve(ctx.registerTool({
    name:"select_experiment_scenario",title:"Select experiment scenario",
    description:"Show the recorded injected condition, operational evidence, reasoning and M5/M6 result for one of the six solar scenarios.",
    inputSchema:{type:"object",properties:{scenario:{type:"string",enum:ORDER}},required:["scenario"],additionalProperties:false},
    annotations:{readOnlyHint:false,untrustedContentHint:false},
    execute(input){if(!input||typeof input!=="object"||!ORDER.includes(input.scenario))throw new Error("Choose one of the six listed scenario keys.");return selectScenario(input.scenario)}
  },{signal:lifecycle.signal})).catch(()=>{});}catch(_){}
}
async function init(){
  try{
    const response=await fetch("./data/experiment.json");
    if(!response.ok)throw new Error("The recorded data could not be loaded.");
    dataset=await response.json();
    if(dataset.scenarios.length!==6||ORDER.some(k=>!dataset.scenarios.some(s=>s.event_type===k)))throw new Error("The scenario record is incomplete.");
    renderControls();
    const requested=new URLSearchParams(location.search).get("scenario");
    selectScenario(META[requested]?requested:ORDER[0]);
    registerWebMCP();
  }catch(error){
    document.querySelector("#detail-content").innerHTML='<div class="error" role="alert">The experiment record could not be loaded. Refresh this page to try again.</div>';
  }
}
init();

async function renderOutage(){
 try{
  const response=await fetch('./data/outage.json'); if(!response.ok)throw new Error();
  const data=await response.json(), host=document.querySelector('#outage-trace'); if(!host)return;
  const rows=data.rows, colors=['#47c5e5','#ffbd66','#a2d6a5'];
  const tracks=[['Power (W)',[['grid_import_w','Grid import'],['battery_discharge_w','Battery discharge'],['load_power_w','Served load']]],['Battery SOC (%)',[['battery_soc_pct','SOC']]],['Grid availability (0 = outage, 1 = available)',[['grid_available','Grid available']]]];
  host.innerHTML=tracks.map(([title,series])=>{
   const ceiling=title.startsWith('Power')?Math.ceil(Math.max(...rows.flatMap(r=>series.map(([k])=>r[k])))/500)*500:title.startsWith('Battery')?100:1;
   const x=i=>55+i/(rows.length-1)*615,y=v=>135-v/ceiling*110;
   let svg='<svg viewBox="0 0 700 165" role="img" aria-label="'+esc(title)+'"><title>'+esc(title)+'</title>';
   for(let i=0;i<=2;i++){const value=ceiling*i/2;svg+='<line x1="55" x2="670" y1="'+y(value)+'" y2="'+y(value)+'" stroke="#294758"/><text x="45" y="'+(y(value)+4)+'" text-anchor="end">'+value+'</text>';}
   series.forEach(([key,label],j)=>{svg+='<path fill="none" stroke="'+colors[j]+'" stroke-width="2.5" d="'+rows.map((r,i)=>(i?'L':'M')+x(i)+','+y(r[key])).join(' ')+'"/>';});
   [0,Math.floor(rows.length/2),rows.length-1].forEach(i=>svg+='<text x="'+x(i)+'" y="158" text-anchor="middle">'+esc(rows[i].timestamp.slice(11,16))+'</text>');
   return '<h4>'+esc(title)+'</h4>'+svg+'</svg><p class="metric-caption">'+series.map(([key,label],j)=>esc(label)+' ('+['cyan','amber','green'][j]+')').join(' · ')+' · WAT</p>';
  }).join('')+'<p class="metric-caption">Actual stored synthetic samples, verified against the original run’s telemetry hash. Outage: 21:35–22:35 WAT. Each panel has its own labelled units. <a href="./data/outage.json">Download observations and provenance</a>.</p>';
 }catch(_){const host=document.querySelector('#outage-trace');if(host)host.textContent='Telemetry unavailable. See the archived evidence above.';}
}
