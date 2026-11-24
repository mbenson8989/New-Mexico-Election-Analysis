"""Fetch NM SOS county-level governor results and county turnout for 2022 (eid 2838) and 2026 (current, unofficial)."""
import sys,re,json,hashlib,datetime,os
sys.path.insert(0,os.path.dirname(__file__))
from nmfetch import *
RAW='/workspace/nm-election/raw'
man=[]
def save(name,content,url,note=''):
    p=f'{RAW}/{name}'; open(p,'wb').write(content)
    man.append(dict(file=name,url=url,downloaded=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),note=note))
for year,eid in [('2022','2838'),('2026',None)]:
    s=sess()
    u='Default.aspx'+(f'?eid={eid}' if eid else '')
    r=s.get(BASE+u); save(f'{year}_default.html',r.content,BASE+u,'election landing page (sets session election)')
    swu='resultsSW.aspx?type=SW&map=CTY'+(f'&eid={eid}' if eid else '')
    r=s.get(BASE+swu); h=r.text; save(f'{year}_statewide_page.html',r.content,BASE+swu,'statewide races page')
    hdr=re.search(r'(Official|Unofficial) Results.{0,200}?Results last updated:[^<]*',re.sub(r'<[^>]+>',' ',h),re.S)
    print(year, hdr.group(0)[:200] if hdr else 'no header')
    # find governor race index
    idx=None
    for m in re.finditer(r'name="(ctl00\$MainContent\$rptRace\$ctl(\d+)\$CountyExport)"[^>]*raceid="(\d+)"',h):
        pass
    blocks=re.findall(r'__doPostBack\(\'(ctl00\$MainContent\$rptRace\$ctl\d+\$CountyExport)\',\'\'\)"[^>]*raceid="(\d+)"',h)
    # identify governor raceid from text order
    gov=None
    for tgt,rid in blocks:
        seg=h[h.find(f'raceid="{rid}"')-6000:h.find(f'raceid="{rid}"')]
        if 'Governor and Lieutenant Governor' in seg[-6000:] and gov is None:
            # ensure the nearest race title before is governor
            titles=re.findall(r'(Governor and Lieutenant Governor|United States Senator|United States Representative|Secretary of State|Attorney General)',seg)
            if titles and titles[-1]=='Governor and Lieutenant Governor': gov=(tgt,rid)
    print(year,'governor export',gov)
    r=postback(s,swu,gov[0],h)
    save(f'{year}_governor_county.xlsx',r.content,BASE+swu+f' [POST __EVENTTARGET={gov[0]} raceid={gov[1]} "County Level" export]','Governor county-level export')
    # turnout
    tu='VoterTurnoutDetails.aspx'+(f'?eid={eid}' if eid else '')
    r=s.get(BASE+tu); th=r.text; save(f'{year}_turnout_page.html',r.content,BASE+tu,'voter turnout page (county/precinct ballots cast & eligible voters)')
    tg=re.findall(r"__doPostBack\('([^']*CountyExport[^']*)'",th)
    print(year,'turnout export targets',tg[:4])
    if tg:
        r=postback(s,tu,tg[0],th)
        ext='xlsx' if 'spreadsheet' in r.headers.get('content-type','') else 'bin'
        save(f'{year}_turnout_county_export0.{ext}',r.content,BASE+tu+f' [POST __EVENTTARGET={tg[0]}]',r.headers.get('content-disposition',''))
json.dump(man,open(f'{RAW}/manifest_results.json','w'),indent=1)
