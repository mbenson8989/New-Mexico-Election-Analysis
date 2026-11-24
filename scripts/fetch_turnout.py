"""Fetch the SOS 'County' turnout export (Eligible Voters, Votes Cast) for every county, 2022 (eid 2838) and 2026 (current, unofficial)."""
import sys,re,json,hashlib,datetime,os,time
sys.path.insert(0,os.path.dirname(__file__))
from nmfetch import *
RAW='/workspace/nm-election/raw'; os.makedirs(RAW+'/turnout',exist_ok=True)
man=json.load(open(RAW+'/manifest_results.json'))
for year,eid in [('2022','2838'),('2026',None)]:
    s=sess(); s.get(BASE+'Default.aspx'+(f'?eid={eid}' if eid else ''))
    tu='VoterTurnoutDetails.aspx'+(f'?eid={eid}' if eid else '')
    th=s.get(BASE+tu).text
    tg=[t for t in re.findall(r"__doPostBack\('([^']*\$CountyExport)'",th)]
    tg=list(dict.fromkeys(tg)); print(year,len(tg))
    for i,t in enumerate(tg):
        r=postback(s,tu,t,th)
        name=f'turnout/{year}_turnout_county_{i:02d}.xlsx'
        open(f'{RAW}/{name}','wb').write(r.content)
        man.append(dict(file=name,url=BASE+tu+f' [POST __EVENTTARGET={t}]',downloaded=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest(),note='county turnout export: '+r.headers.get('content-disposition','')))
        time.sleep(0.5)
json.dump(man,open(RAW+'/manifest_results.json','w'),indent=1)
