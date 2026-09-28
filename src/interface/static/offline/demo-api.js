'use strict';
// Static GitHub Pages adapter: no Python execution, API credentials or model calls.
(() => {
  const storageKey='idl-public-offline-session-v1';
  let turns=[];
  try {const stored=JSON.parse(sessionStorage.getItem(storageKey)||'[]');if(Array.isArray(stored)&&stored.length<=20&&stored.every(t=>typeof t.question==='string'&&typeof t.answer==='string'&&Array.isArray(t.tools)))turns=stored;} catch(_) {}
  const persist=()=>{try{sessionStorage.setItem(storageKey,JSON.stringify(turns));}catch(_){/* Private browsing can deny storage; the current tab still works. */}};
  const clone=value=>JSON.parse(JSON.stringify(value));
  const cache=new Map();
  function data(name){
    if(!cache.has(name))cache.set(name,fetch(new URL('./data/'+name,document.baseURI)).then(r=>{if(!r.ok)throw new Error('Recorded data could not be loaded. Please retry.');return r.json();}).catch(e=>{cache.delete(name);throw e;}));
    return cache.get(name);
  }
  const normalize=text=>text.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
  window.demoApi=async(path,payload)=>{
    const url=new URL(path,'https://offline.invalid');
    if(url.pathname==='/api/dashboard'){
      const base=await data('snapshot.json');
      const day=url.searchParams.get('day')||base.selected_day;
      if(!/^\d{4}-\d{2}-\d{2}$/.test(day)||day<base.first_day||day>base.last_day)throw new Error('Choose a date within the recorded simulation window.');
      const daily=await data('days/'+day+'.json');
      return {...clone(base),...clone(daily)};
    }
    if(url.pathname==='/api/session')return {mode:'offline',turns:clone(turns)};
    if(url.pathname==='/api/reset'){turns=[];persist();return {ok:true};}
    if(url.pathname==='/api/export'){
      const source=await data('manifest.json');
      return {format_version:1,synthetic_data:true,public_offline_demo:true,
        evaluation_status:'Interactive replay of precomputed deterministic answers; not live execution or a scored experiment',
        source_run:source.source_run,telemetry_sha256:source.telemetry_sha256,
        exported_utc:new Date().toISOString(),turns:clone(turns)};
    }
    if(url.pathname==='/api/ask'){
      if(payload?.mode!=='offline')throw new Error('Claude requires a hosted backend and is unavailable in this GitHub-only demonstration.');
      if(typeof payload.question!=='string'||!payload.question.trim()||payload.question.length>2000)throw new Error('Enter a question between 1 and 2,000 characters.');
      if(turns.length>=20)throw new Error('Export this session and start a new conversation (20-turn limit).');
      const bank=await data('answers.json');
      const input=normalize(payload.question);
      const key=['status','show status','system status','what is the current system status','show current system status'].includes(input)?'current system status':input;
      const recorded=bank.answers.find(r=>normalize(r.question)===key);
      const turn=recorded?clone(recorded):{mode:'offline',status:'unsupported',tools:[],usage:[],model:null,synthetic_data:true,
        answer:'This GitHub demonstration contains precomputed answers for the suggested questions and current system status. Choose one of the topics above, or type "status". Other dates, new diagnoses and conversational follow-ups require the Python dashboard; Claude is not connected here.'};
      if(recorded)turn.recorded_at_utc=turn.timestamp_utc;
      turn.question=payload.question.trim();turn.presentation='precomputed_offline';turn.timestamp_utc=new Date().toISOString();turn.elapsed_seconds=0;
      turns.push(turn);persist();return clone(turn);
    }
    throw new Error('This action is unavailable in the static demonstration.');
  };
})();
