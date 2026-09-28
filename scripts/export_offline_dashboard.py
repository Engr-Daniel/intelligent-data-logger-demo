"""Export verified synthetic dashboard observations and offline answers; no model calls."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'.venv/Lib/site-packages'))
import pandas as pd
from src.interface.web_service import dashboard,Conversation,SUGGESTIONS
from src.storage.local_store import load_telemetry
OUT=ROOT/'src/interface/static/offline/data'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=json.loads((ROOT/'reports/runs/20260921T055826825005Z/run_manifest.json').read_text())
 csv=ROOT/'data/processed/telemetry.csv'
 expected=next(v for k,v in manifest['sha256'].items() if k.replace('\\','/')=='data/processed/telemetry.csv')
 if digest(csv)!=expected:raise ValueError('Refusing to export telemetry that differs from the original synthetic run')
 df=load_telemetry();raw=pd.read_csv(csv,low_memory=False,dtype={"inverter_alarm_code":str});raw['timestamp']=pd.to_datetime(raw.timestamp,utc=True).dt.tz_convert('Africa/Lagos')
 for column in df.select_dtypes(include="object").columns:
  raw[column]=raw[column].fillna("");df[column]=df[column].fillna("")
 pd.testing.assert_frame_equal(df,raw,check_dtype=False,check_exact=False,rtol=1e-10,atol=1e-10)
 OUT.mkdir(parents=True,exist_ok=True)
 files=[]
 def write(name,value):
  path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n',encoding='utf-8');files.append(name)
 base=dashboard();base.pop('chart');base.update(live_configured=False,model=None,public_offline=True)
 write('snapshot.json',base)
 required=['pv_ac_power_w','load_power_w','battery_soc_pct','grid_import_w','grid_export_w']
 for day,group in df.groupby(df.timestamp.dt.strftime('%Y-%m-%d')):
  chart=group[['timestamp',*required,'battery_charge_w','battery_discharge_w']].copy();chart['timestamp']=chart.timestamp.astype(str)
  write('days/'+day+'.json',{'selected_day':day,'missing_rows':int(group[required].isna().any(axis=1).sum()),'chart':json.loads(chart.to_json(orient='records'))})
 answers=[]
 for label,question in [('Current status','Current system status'),*SUGGESTIONS]:
  record=Conversation().ask(question,'offline')
  if record['status']!='complete' or not record['tools']:raise ValueError('Offline answer failed: '+label)
  record['presentation']='precomputed_offline';record['recorded_question']=question
  answers.append(record)
 write('answers.json',{'kind':'Precomputed deterministic answers; not live execution or research evaluation','answers':answers})
 write('manifest.json',{'source_run':'20260921T055826825005Z','telemetry_sha256':expected,'rows':len(df),'days':df.timestamp.dt.date.nunique(),
       'source_sha256':{name:digest(ROOT/name) for name in ['config/installation.yaml','src/interface/web_service.py','src/reasoning/agent.py','src/reasoning/tools.py']},
       'sha256':{name:digest(OUT/name) for name in files}})
 print(f'Exported {len(df)} verified synthetic observations, 120 daily charts and {len(answers)} offline answers; no API calls.')
if __name__=='__main__':main()
