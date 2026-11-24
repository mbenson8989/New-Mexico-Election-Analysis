"""VERIFICATION PASS 2 - written separately from pipeline.py and verify_pass1.py (no shared code).
Uses SECOND-SOURCE SOS files where they exist:
  governor votes  -> 66 per-county SOS results pages (raw/county_pages/*.html), stdlib html.parser
  ballots cast    -> 66 per-county SOS 'County Level' turnout exports (raw/turnout/*.xlsx), raw OOXML via zipfile + ElementTree
  registration    -> SOS Statewide-by-County PDFs via pdfplumber word coordinates (only SOS county-party source)
  population      -> Census csv via csv.reader by column index
Fit via Decimal arithmetic normal equations."""
import os, re, csv, json, zipfile, glob
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from decimal import Decimal as D, getcontext
import pdfplumber
getcontext().prec=50
RAW='/workspace/nm-election/raw'
def cname(s): return s.replace('_',' ').strip()
class Seq(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.items=[]
    def handle_starttag(s,t,a):
        s.stack.append((t,dict(a).get('class','')))
    def handle_endtag(s,t):
        if s.stack: s.stack.pop()
    def handle_data(s,d):
        d=d.strip()
        if d and s.stack and s.stack[-1][0] in('h1','h2'): s.items.append((s.stack[-1][0],d))
def gov_from_page(path):
    p=Seq(); p.feed(open(path,encoding='utf-8',errors='replace').read())
    it=p.items
    k=[i for i,(t,d) in enumerate(it) if t=='h1' and d=='Governor and Lieutenant Governor'][0]
    dem=rep=None; tot=0; i=k+1
    while i+2<len(it):
        if it[i][0]=='h1' and it[i+1][0]=='h2' and it[i+2][0]=='h1' and re.fullmatch(r'[\d,]+',it[i+2][1]):
            party=it[i+1][1]; v=int(it[i+2][1].replace(',','')); tot+=v
            if party=='Democrat': dem=v
            elif party=='Republican': rep=v
            i+=3
        else: break
    gov_from_page.last_total=tot
    return dem,rep
def xlsx_cells(path):
    z=zipfile.ZipFile(path); ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    ss=[si.find('x:t',ns).text or '' for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('x:si',ns)]
    cells={}
    for c in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter('{%s}c'%ns['x']):
        v=c.find('x:v',ns)
        if v is None: continue
        cells[c.get('r')]=ss[int(v.text)] if c.get('t')=='s' else v.text
    return cells
def reg_pdf(fn):
    out={}
    with pdfplumber.open(f'{RAW}/registration/{fn}') as pdf:
        words=pdf.pages[0].extract_words()
    lines={}
    for w in words: lines.setdefault(round(w['top']),[]).append(w)
    for top in sorted(lines):
        ws=sorted(lines[top],key=lambda w:w['x0'])
        name=[];j=0
        while j<len(ws) and re.fullmatch(r'[A-Za-z]+',ws[j]['text']): name.append(ws[j]['text']); j+=1
        nm=' '.join(name)
        if not nm or nm in('COUNTY','TOTAL') or j==len(ws): continue
        toks=[w['text'] for w in ws[j:]]
        counts=[int(t.replace(',','')) for n,t in enumerate(toks) if re.fullmatch(r'[\d,]+',t) and not (n+1<len(toks) and toks[n+1].startswith('%')) and not t.endswith('%')]
        if counts: out[nm]=(counts[0],counts[-1])
    return out
data={}
for y in ('2022','2026'):
    for f in glob.glob(f'{RAW}/county_pages/{y}_cty*.html'):
        nm=cname(re.match(r'.*_cty\d\d_(.+)\.html',f).group(1)); d,r=gov_from_page(f)
        data.setdefault(nm,{})[f'dem{y[2:]}']=d; data[nm][f'rep{y[2:]}']=r; data[nm][f'allgov{y[2:]}']=gov_from_page.last_total
    for f in glob.glob(f'{RAW}/turnout/{y}_turnout_export_cty*.xlsx'):
        nm=cname(re.match(r'.*_cty\d\d_(.+)\.xlsx',f).group(1)); c=xlsx_cells(f)
        assert c['A7']=='County' and c['C7']=='Votes Cast' and cname(c['A8'])==nm
        data[nm][f'ballots{y[2:]}']=int(c['C8'])
for y,fn in (('22','Statewide_10-31-2022.pdf'),('26','Statewide_10-30-2026.pdf')):
    got=reg_pdf(fn); used=0
    for nm,(dm,tt) in got.items():
        if nm not in data: print('  pdf line skipped (not a county):',nm); continue
        data[nm][f'regdem{y}']=dm; data[nm][f'regtot{y}']=tt; used+=1
    assert used==33,(fn,used)
with open(f'{RAW}/census/co-est2025-alldata.csv',encoding='latin-1') as f:
    rd=csv.reader(f); h=next(rd); iS,iC,iN,iP=h.index('STATE'),h.index('COUNTY'),h.index('CTYNAME'),h.index('POPESTIMATE2025')
    for r in rd:
        if r[iS]=='35' and r[iC]!='000': data[r[iN].replace(' County','').replace('Doña','Dona')]['population']=int(r[iP])
assert len(data)==33, len(data)
need=['population','dem22','rep22','ballots22','dem26','rep26','ballots26','regdem22','regtot22','regdem26','regtot26']
for nm,v in data.items():
    miss=[k for k in need if v.get(k) is None]
    assert not miss,(nm,miss)
H=D(100)
for v in data.values():
    v['S22']=D(v['dem22'])*H/D(v['ballots22']); v['S26']=D(v['dem26'])*H/D(v['ballots26'])
    v['R22']=D(v['regdem22'])*H/D(v['regtot22']); v['R26']=D(v['regdem26'])*H/D(v['regtot26'])
    v['G22']=v['S22']-v['R22']; v['G26']=v['S26']-v['R26']
    v['dS']=v['S26']-v['S22']; v['dR']=v['R26']-v['R22']; v['drop']=v['R22']-v['R26']
    v['dG']=(v['S26']-v['S22'])-(v['R26']-v['R22'])
    v['over22']=v['dem22']+v['rep22']>v['ballots22']; v['over26']=v['dem26']+v['rep26']>v['ballots26']
vals=list(data.values()); n=D(len(vals))
Sx=sum(v['drop'] for v in vals); Sy=sum(v['dS'] for v in vals)
Sxx=sum(v['drop']**2 for v in vals); Sxy=sum(v['drop']*v['dS'] for v in vals); Syy=sum(v['dS']**2 for v in vals)
m=(n*Sxy-Sx*Sy)/(n*Sxx-Sx*Sx); b=(Sy-m*Sx)/n
ssr=sum((v['dS']-(b+m*v['drop']))**2 for v in vals); sst=Syy-Sy*Sy/n; r2=1-ssr/sst
for v in vals:
    v['expected']=b+m*v['drop']; v['residual']=v['dS']-v['expected']; v['implied']=v['residual']*D(v['ballots26'])/H
def q(x,nd): return format(float(x),f'.{nd}f')  # displayed precision
def disp(k,x):
    if isinstance(x,bool): return 'YES' if x else 'no'
    if k=='implied': return ('+' if x>=0 else '')+q(x,0) if q(x,0)!='-0' else '-0'
    if k in('S22','S26','R22','R26','drop'): return q(x,2)
    if k in('G22','G26','dS','dR','dG','expected','residual'): s=q(x,2); return s if s.startswith('-') else '+'+s
    return str(x)
cols=['county','population','dem22','rep22','ballots22','dem26','rep26','ballots26','regdem22','regtot22','regdem26','regtot26','S22','S26','R22','R26','G22','G26','dS','dR','drop','dG','expected','residual','implied','over22','over26']
with open('/workspace/nm-election/verification/pass2_values.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for nm in sorted(data,key=lambda k:-data[k]['population']): w.writerow([nm]+[disp(k,data[nm][k]) for k in cols[1:]])
fit={'constant':('+' if b>=0 else '')+q(b,2),'multiplier':q(m,3),'r2':q(r2,3)}
json.dump(fit,open('/workspace/nm-election/verification/pass2_fit.json','w'))
print('pass2 fit',fit)

# ---- share version, pass 2 (Decimal normal equations, own code). surplus S = G ; S = m*(D/100) + b
def fit_dec(pairs):
    N=D(len(pairs)); a=sum(p for p,_ in pairs); bq=sum(q for _,q in pairs)
    aa=sum(p*p for p,_ in pairs); ab=sum(p*q for p,q in pairs); bb_=sum(q*q for _,q in pairs)
    sl=(N*ab-a*bq)/(N*aa-a*a); ic=(bq-sl*a)/N
    sse=sum((q-(ic+sl*p))**2 for p,q in pairs); r2_=1-sse/(bb_-bq*bq/N)
    return sl,ic,r2_
def sgn(x,nd=2): s=q(x,nd); return s if s.startswith('-') else '+'+s
share={}
for yy in ('22','26'):
    names=list(data); pr=[(data[k]['R'+yy]/H,data[k]['G'+yy]) for k in names]
    sl,ic,r2_=fit_dec(pr)
    for k in names:
        data[k]['shfit'+yy]=ic+sl*data[k]['R'+yy]/H; data[k]['shres'+yy]=data[k]['G'+yy]-data[k]['shfit'+yy]
    absr={k:abs(data[k]['shres'+yy]) for k in names}; wk=max(absr,key=absr.get)
    share['y20'+yy]=dict(m=q(sl,2),b=sgn(ic),r2=q(r2_,3),mae=q(sum(absr.values())/D(33),2),max_county=wk,max_resid=sgn(data[wk]['shres'+yy]))
with open('/workspace/nm-election/verification/pass2_share_values.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['county','R22','G22','shfit22','shres22','R26','G26','shfit26','shres26','gapvotes'])
    for nm in sorted(data,key=lambda k:-data[k]['population']):
        d_=data[nm]; w.writerow([nm,q(d_['R22'],2),sgn(d_['G22']),sgn(d_['shfit22']),sgn(d_['shres22']),q(d_['R26'],2),sgn(d_['G26']),sgn(d_['shfit26']),sgn(d_['shres26']),sgn(D(d_['dem26'])-D(d_['dem22'])*D(d_['regdem26'])/D(d_['regdem22']),0)])
json.dump(share,open('/workspace/nm-election/verification/pass2_share_fit.json','w'),indent=1)
print('pass2 share',share)

# ---- raw second-source counts for the Kansas-parity pass B (kp_metrics_b.py); integers only, no derived values
json.dump({nm:{k:int(data[nm][k]) for k in need+['allgov22','allgov26']} for nm in data},open('/workspace/nm-election/verification/pass2_counts.json','w'),indent=1,sort_keys=True)
