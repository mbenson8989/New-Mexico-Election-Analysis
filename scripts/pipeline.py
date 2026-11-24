"""New Mexico reverse-factoring pipeline (production build).
Inputs (all under raw/):
  2022_governor_county.xlsx, 2026_governor_county.xlsx  - SOS 'County Level' export of Governor & Lt Governor race
  2022_turnout_page.html, 2026_turnout_page.html        - SOS VoterTurnoutDetails page (precinct ballots cast / eligible voters)
  registration/Statewide_10-31-2022.pdf, Statewide_10-30-2026.pdf - SOS 'Statewide by County' registration reports
  census/co-est2025-alldata.csv                         - Census Vintage 2025 county population (sort order)
Output: out/nm_county_table.csv, out/nm_summary.json
"""
import openpyxl, subprocess, re, csv, json, numpy as np
from lxml import html as L
RAW='/workspace/nm-election/raw'; OUT='/workspace/nm-election/out'
def norm(n): return n.strip().replace('Doña','Dona').replace('Ã±','n')
def gov(year):
    ws=openpyxl.load_workbook(f'{RAW}/{year}_governor_county.xlsx').worksheets[0]  # 'Total' sheet
    rows=list(ws.iter_rows(values_only=True))
    hdr=rows[6]; cands=list(hdr[2:])
    dem_i=[i for i,c in enumerate(cands) if c.startswith(('MICHELLE LUJAN GRISHAM','DEB HAALAND'))][0]
    rep_i=[i for i,c in enumerate(cands) if c.startswith(('MARK V RONCHETTI','GREGGORY D HULL'))][0]
    out={}
    for r in rows[7:]:
        if not r[1] or r[1]=='TOTALS': continue
        v=[int(x) for x in r[2:2+len(cands)]]
        out[norm(r[1])]=dict(dem=v[dem_i],rep=v[rep_i],allcand=sum(v))
    return out,cands
def turnout(year):
    d=L.parse(f'{RAW}/{year}_turnout_page.html').getroot(); out={}
    for b in d.xpath('//div[contains(@class,"turnout-results-box-a")]'):
        name=norm(b.xpath('./h1/text()')[0]); cid=b.xpath('.//input[@countyid]/@countyid')[0]
        blk=d.xpath(f'//div[@id="countyturnout{cid}"]')[0]; bc=ev=0
        for r in blk.xpath('./div[@class="odd" or @class="even"]'):
            bc+=int(r.xpath('./div[@class="county-cast"]/span/text()')[0].replace(',',''))
            ev+=int(r.xpath('./div[@class="county-counted"]/span/text()')[0].replace(',',''))
        out[name]=dict(ballots=bc,eligible=ev)
    return out
def reg(pdf):
    t=subprocess.run(['pdftotext','-layout',f'{RAW}/registration/{pdf}','-'],capture_output=True,text=True).stdout
    out={}
    for line in t.splitlines():
        m=re.match(r'^([A-Z][a-zA-Z ]+?)\s{2,}([\d,]+)\s',line)
        if not m or m.group(1) in ('COUNTY','TOTAL'): continue
        nums=[int(x.replace(',','')) for x in re.findall(r'(?<![\d.])[\d,]*\d(?![\d.]*\s*%)',line[len(m.group(1)):])]
        out[norm(m.group(1))]=dict(dem=nums[0],total=nums[-1])
    return out
def pop():
    out={}
    with open(f'{RAW}/census/co-est2025-alldata.csv',encoding='latin-1') as f:
        for r in csv.DictReader(f):
            if r['STNAME']=='New Mexico' and r['SUMLEV']=='050':
                out[norm(r['CTYNAME'].replace(' County','').replace('Doña','Dona'))]=int(r['POPESTIMATE2025'])
    return out
g22,c22=gov(2022); g26,c26=gov(2026); t22=turnout(2022); t26=turnout(2026)
r22=reg('Statewide_10-31-2022.pdf'); r26=reg('Statewide_10-30-2026.pdf'); P=pop()
names=sorted(g22)
for d in (g26,t22,t26,r22,r26,P): assert set(d)==set(names),(set(d)^set(names))
assert len(names)==33
rows=[]
for n in names:
    a=dict(county=n,population=P[n],
      dem22=g22[n]['dem'],rep22=g22[n]['rep'],allgov22=g22[n]['allcand'],ballots22=t22[n]['ballots'],
      dem26=g26[n]['dem'],rep26=g26[n]['rep'],allgov26=g26[n]['allcand'],ballots26=t26[n]['ballots'],
      regdem22=r22[n]['dem'],regtot22=r22[n]['total'],regdem26=r26[n]['dem'],regtot26=r26[n]['total'])
    a['S22']=100*a['dem22']/a['ballots22']; a['S26']=100*a['dem26']/a['ballots26']
    a['R22']=100*a['regdem22']/a['regtot22']; a['R26']=100*a['regdem26']/a['regtot26']
    a['G22']=a['S22']-a['R22']; a['G26']=a['S26']-a['R26']
    a['dS']=a['S26']-a['S22']; a['dR']=a['R26']-a['R22']; a['drop']=a['R22']-a['R26']
    a['dG']=a['dS']-a['dR']
    a['over22']=a['dem22']+a['rep22']>a['ballots22']; a['over26']=a['dem26']+a['rep26']>a['ballots26']
    rows.append(a)
x=np.array([a['drop'] for a in rows]); y=np.array([a['dS'] for a in rows])
m,b=np.polyfit(x,y,1); yhat=b+m*x; r2=1-((y-yhat)**2).sum()/((y-y.mean())**2).sum()
for a in rows:
    a['expected']=b+m*a['drop']; a['residual']=a['dS']-a['expected']; a['implied']=a['residual']/100*a['ballots26']
rows.sort(key=lambda a:-a['population'])
FMT={'S22':2,'S26':2,'R22':2,'R26':2,'G22':2,'G26':2,'dS':2,'dR':2,'drop':2,'dG':2,'expected':2,'residual':2,'implied':0}
def fmt(k,v):
    if isinstance(v,bool): return 'YES' if v else 'no'
    if k in FMT: return f'{v:+.{FMT[k]}f}' if k not in('S22','S26','R22','R26','drop') else f'{v:.{FMT[k]}f}'
    return str(v)
cols=['county','population','dem22','rep22','ballots22','dem26','rep26','ballots26','regdem22','regtot22','regdem26','regtot26','S22','S26','R22','R26','G22','G26','dS','dR','drop','dG','expected','residual','implied','over22','over26']
with open(f'{OUT}/nm_county_table.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for a in rows: w.writerow([fmt(k,a[k]) for k in cols])
# full-precision copy for charts
with open(f'{OUT}/nm_county_table_fullprecision.csv','w',newline='') as f:
    fc=cols+['allgov22','allgov26']; w=csv.writer(f); w.writerow(fc)
    for a in rows: w.writerow([a[k] for k in fc])
st={k:sum(a[k] for a in rows) for k in ['dem22','rep22','allgov22','ballots22','dem26','rep26','allgov26','ballots26','regdem22','regtot22','regdem26','regtot26']}
summ=dict(n=len(rows),constant=b,multiplier=m,r2=r2,statewide=st,
  fmt=dict(constant=f'{b:+.2f}',multiplier=f'{m:.3f}',r2=f'{r2:.3f}'),
  floor=min(rows,key=lambda a:a['S22'])['county'],ceiling=max(rows,key=lambda a:a['S22'])['county'],
  over_ballot=[(a['county'],y) for a in rows for y in ('22','26') if a['over'+y]],
  candidates=dict(y2022=c22,y2026=c26))
json.dump(summ,open(f'{OUT}/nm_summary.json','w'),indent=1,default=str)
print(json.dumps(summ['fmt']),summ['floor'],summ['ceiling'],summ['over_ballot'])
print(st)

# ---------------- SHARE VERSION (Morissa): surplus S = G = DemShare - RegShare ; S = m*(D/100) + b, D = RegShare in percent
def share_fit(yr):
    xs=np.array([a['R'+yr]/100 for a in rows]); ys=np.array([a['G'+yr] for a in rows])
    mm,bb=np.polyfit(xs,ys,1); fit=bb+mm*xs; res=ys-fit
    r2s=1-(res**2).sum()/((ys-ys.mean())**2).sum()
    k=int(np.argmax(np.abs(res)))
    return dict(m=mm,b=bb,r2=r2s,mae=float(np.abs(res).mean()),max_county=rows[k]['county'],max_resid=float(res[k])),fit,res
SF={}
for yr in ('22','26'):
    st_,fit,res=share_fit(yr); SF['y20'+yr]=st_
    for a,fv,rv in zip(rows,fit,res): a['shfit'+yr]=fv; a['shres'+yr]=rv
# (Delta-G variant fit removed Nov 20 2026: the surplus form is the only locked equation)
def f2(v): return f'{v:+.2f}'
SFMT={}
for k,v in SF.items():
    SFMT[k]=dict(m=f"{v['m']:.2f}",b=f2(v['b']),r2=f"{v['r2']:.3f}",mae=f"{v['mae']:.2f}")
    if 'max_county' in v: SFMT[k].update(max_county=v['max_county'],max_resid=f2(v['max_resid']))
for a in rows: a['gapvotes']=a['dem26']-a['dem22']*a['regdem26']/a['regdem22']
scols=['county','R22','G22','shfit22','shres22','R26','G26','shfit26','shres26','gapvotes']
with open(f'{OUT}/nm_share_fit_table.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(scols)
    for a in rows: w.writerow([a['county'],f"{a['R22']:.2f}",f2(a['G22']),f2(a['shfit22']),f2(a['shres22']),f"{a['R26']:.2f}",f2(a['G26']),f2(a['shfit26']),f2(a['shres26']),f"{a['gapvotes']:+.0f}"])
with open(f'{OUT}/nm_share_fit_fullprecision.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(scols)
    for a in rows: w.writerow([a[k] for k in scols])
json.dump(dict(raw=SF,fmt=SFMT),open(f'{OUT}/nm_share_fit.json','w'),indent=1)
print('share fit',json.dumps(SFMT))
