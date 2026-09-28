const fs=require("fs");
const path=require("path");
const vm=require("vm");
const assert=require("assert");
const root=path.resolve(__dirname,"../src/interface/static/explorer");
const record=JSON.parse(fs.readFileSync(root+"/data/experiment.json","utf8"));
const nodes=new Map();
let registered;
function node(selector){
  if(!nodes.has(selector))nodes.set(selector,{innerHTML:"",listeners:{},addEventListener(kind,fn){this.listeners[kind]=fn},focus(){this.focused=true}});
  return nodes.get(selector);
}
function control(key,type){
  const classes=new Set([type]);
  return {dataset:{scenario:key},classList:{contains:c=>classes.has(c),toggle(c,on){if(on)classes.add(c);else classes.delete(c)}},setAttribute(name,value){this[name]=value}};
}
const controls=record.scenarios.flatMap(s=>[control(s.event_type,"scenario-button"),control(s.event_type,"timeline-row")]);
const context={
  document:{querySelector:node,querySelectorAll:()=>controls,modelContext:{registerTool(tool){registered=tool}}},
  fetch:async()=>({ok:true,json:async()=>record}),
  history:{replaceState(_a,_b,url){context.location.lastUrl=url}},
  location:{pathname:"/",search:""},
  URLSearchParams,Date,Intl,console,AbortController,Promise,Error
};
vm.runInNewContext(fs.readFileSync(root+"/app.js","utf8"),context);
setImmediate(async()=>{
  assert(registered,"WebMCP action should register");
  assert.strictEqual(registered.name,"select_experiment_scenario");
  assert.strictEqual(registered.inputSchema.properties.scenario.enum.length,6);
  for(const scenario of record.scenarios){
    const outcome=registered.execute({scenario:scenario.event_type});
    const html=node("#detail-content").innerHTML;
    assert.strictEqual(outcome.result,"PASS");
    assert(html.includes(scenario.evidence.finding));
    assert(html.includes("Ground-truth cause"));
    assert(html.includes("What the evaluation recorded"));
    assert(html.includes(scenario.evidence.supporting_tools[0]+"()"));
    assert(html.includes("All "+scenario.evidence.measurements.length+" recorded measurements"));
    assert(controls.find(c=>c.dataset.scenario===scenario.event_type&&c.classList.contains("scenario-button")).classList.contains("selected"));
  }
  const before=context.location.lastUrl;
  assert.throws(()=>registered.execute({scenario:"unknown"}),/Choose one/);
  assert.strictEqual(context.location.lastUrl,before,"invalid scenario must not change state");
  node("#timeline").listeners.click({target:{closest:()=>({dataset:{scenario:"sensor_dropout"}})}});
  assert(node("#detail-content").innerHTML.includes("9 rows"));
  assert(node("#detail-title").focused);
  node("#workflow").onclick({target:{closest:()=>({dataset:{milestone:"5"}})}});
  assert(node("#workflow").innerHTML.includes("M6 · Resolve"));
  console.log("PASS: six scenario selections, telemetry, ground truth, evidence, results, timeline, workflow, invalid input and WebMCP action");
});
