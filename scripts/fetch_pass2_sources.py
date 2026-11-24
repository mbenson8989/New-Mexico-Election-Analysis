"""Second-source SOS files for verification pass 2:
 - per-county results pages (resultsSW.aspx?type=CTYALL&cty=NN) for 2022 (eid 2838) and 2026 (current)
 - per-county 'County Level' turnout exports (Eligible Voters / Votes Cast)
Slow, with backoff, because the SOS F5 firewall rate-limits bursts."""
import sys,re,json,hashlib,datetime,os,time
sys.path.insert(0,os.path.dirname(__file__))
from nmfetch import *
RAW='/workspace/nm-election/raw'
os.makedirs(RAW+'/county_pages',exist_ok=True); os.makedirs(RAW+'/turnout',exist_ok=True)
mf=RAW+'/manifest_pass2.json'
man=json.load(open(mf)) if os.path.exists(mf) else []
done={m['file'] for m in man}
def rec(name,content,url,note=''):
    open(f'{RAW}/{name}','wb').write(content)
    man.append(dict(file=name,url=url,downloaded=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),note=note))
    json.dump(man,open(mf,'w'),indent=1)
from lxml import html as L
for year,eid in [('2022','2838'),('2026',None)]:
    d=L.parse(f'{RAW}/{year}_turnout_page.html').getroot()
    ctys=[(b.xpath('./h1/text()')[0].strip(),b.xpath('.//input[@countyid]/@countyid')[0]) for b in d.xpath('//div[contains(@class,"turnout-results-box-a")]')]
    s=sess(); s.get(BASE+'Default.aspx'+(f'?eid={eid}' if eid else '')); time.sleep(2)
    for name,cid in ctys:
        fn=f'county_pages/{year}_cty{cid}_{name.replace(" ","_")}.html'
        if fn in done: continue
        u=f'resultsSW.aspx?type=CTYALL&map=CTY&cty={cid}'+(f'&eid={eid}' if eid else '')
        r=s.get(BASE+u)
        if 'Governor and Lieutenant Governor' not in r.text: print('WARN no governor',fn,flush=True)
        rec(fn,r.content,BASE+u,f'county results page {name}'); print('ok',fn,flush=True); time.sleep(2.5)
    tu='VoterTurnoutDetails.aspx'+(f'?eid={eid}' if eid else '')
    for i,(name,cid) in enumerate(ctys):
        fn=f'turnout/{year}_turnout_export_cty{cid}_{name.replace(" ","_")}.xlsx'
        if fn in done: continue
        th=s.get(BASE+tu).text; time.sleep(1.5)
        r=postback(s,tu,f'ctl00$MainContent$rptVoterTurnoutCTY$ctl{i:02d}$CountyExport',th)
        rec(fn,r.content,BASE+tu+f' [POST __EVENTTARGET=ctl00$MainContent$rptVoterTurnoutCTY$ctl{i:02d}$CountyExport]',f'county turnout export {name}; '+r.headers.get('content-disposition',''))
        print('ok',fn,flush=True); time.sleep(2.5)
