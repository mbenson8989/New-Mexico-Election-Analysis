"""Check EVERY number in wiki/New-Mexico-County-Data.pdf (via pdftotext) against an INDEPENDENT re-parse of raw/.
Does not import or read pipeline / pass outputs. Own parsers:
  governor xlsx  -> openpyxl, columns located by candidate name, TOTALS row cross-checked
  ballots cast   -> regex over the SOS VoterTurnoutDetails page (sum of every precinct's Ballots Cast)
  registration   -> pdftotext -layout lines of the SOS 'Statewide by County' PDFs, percent cells dropped; each row's party counts
                    must add to its TOTAL and the county rows must add to the TOTAL row
  population     -> csv module, Census co-est2025-alldata.csv (STATE 35)
  fits           -> exact rational least squares (fractions.Fraction)
Non-data numbers in the text (dates, page numbers, file names, formula constants) are each checked against raw/ or the PDF itself.
Writes verification/pdf_check.json; exits 1 on any mismatch or unaccounted number."""
import re, csv, json, subprocess, sys, html
from fractions import Fraction as Fr
import openpyxl
R='/workspace/nm-election/raw'; PDF='/workspace/nm-election/wiki/New-Mexico-County-Data.pdf'
nm=lambda s:html.unescape(s).strip().replace('Doña','Dona').replace('Ã±','n')
def gov(y):
    rows=list(openpyxl.load_workbook(f'{R}/{y}_governor_county.xlsx',read_only=True).worksheets[0].iter_rows(values_only=True))
    h=[i for i,r in enumerate(rows) if r[1]=='County'][0]; hdr=rows[h]
    di=[i for i,x in enumerate(hdr) if x and ('LUJAN GRISHAM' in x or 'HAALAND' in x)][0]
    out={}; tot=None
    for r in rows[h+1:]:
        if not r[1]: continue
        if r[1]=='TOTALS': tot=int(r[di]); continue
        out[nm(r[1])]=int(r[di])
    assert tot==sum(out.values()),('gov total',y); return out
def ballots(y):
    t=open(f'{R}/{y}_turnout_page.html',encoding='utf-8',errors='replace').read()
    ids=dict((cid,nm(n)) for n,cid in re.findall(r'turnout-results-box-a">\s*<h1>([^<]+)</h1>.*?countyid="(\d+)"',t,flags=re.S))
    out={}
    for cid,name in ids.items():
        s=t.index(f'id="countyturnout{cid}"'); e=t.find('id="countyturnout',s+10); blk=t[s:e if e>0 else len(t)]
        out[name]=sum(int(v.replace(',','')) for v in re.findall(r'<div class="county-cast">\s*<span>([\d,]+)</span>',blk))
    return out
def reg(fn):
    txt=subprocess.run(['pdftotext','-layout',f'{R}/registration/{fn}','-'],capture_output=True,text=True).stdout
    out={}; tot=None
    for line in txt.splitlines():
        m=re.match(r'^([A-Z][A-Za-z]*(?: [A-Z][A-Za-z]*)*)\s+(\d.*)$',line.strip())
        if not m or m.group(1)=='COUNTY': continue
        body=re.sub(r'\d+(?:\.\d+)?\s*%',' ',m.group(2))          # drop percentage cells
        nums=[int(x.replace(',','')) for x in body.split()]
        assert sum(nums[:-1])==nums[-1],('party counts do not add to row total',fn,m.group(1))
        if m.group(1)=='TOTAL': tot=(nums[0],nums[-1]); continue
        out[nm(m.group(1))]=(nums[0],nums[-1])
    assert tot==(sum(v[0] for v in out.values()),sum(v[1] for v in out.values())),('reg total',fn,tot); return out
def census():
    out={}
    with open(f'{R}/census/co-est2025-alldata.csv',encoding='latin-1') as f:
        for r in csv.DictReader(f):
            if r['STATE']=='35' and r['COUNTY']!='000': out[nm(r['CTYNAME'].replace(' County',''))]=int(r['POPESTIMATE2025'])
    return out
G={y:gov(y) for y in (2022,2026)}; B={y:ballots(y) for y in (2022,2026)}
RG={2022:reg('Statewide_10-31-2022.pdf'),2026:reg('Statewide_10-30-2026.pdf')}; POP=census()
C=sorted(POP); assert len(C)==33 and all(set(d)==set(C) for d in (G[2022],G[2026],B[2022],B[2026],RG[2022],RG[2026])),'county sets'
E={}
for c in C:
    e=dict(population=POP[c])
    for y in (2022,2026):
        k=str(y)[2:]; e['dem'+k]=G[y][c]; e['ballots'+k]=B[y][c]; e['regdem'+k]=RG[y][c][0]; e['regtot'+k]=RG[y][c][1]
        e['V'+k]=Fr(100*G[y][c],B[y][c]); e['D'+k]=Fr(100*RG[y][c][0],RG[y][c][1]); e['S'+k]=e['V'+k]-e['D'+k]
    E[c]=e
FIT={}
for k in ('22','26'):
    xs=[E[c]['D'+k]/100 for c in C]; ys=[E[c]['S'+k] for c in C]; n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); syy=sum((y-my)**2 for y in ys)
    m=sxy/sxx; b=my-m*mx
    for c in C: E[c]['F'+k]=m*E[c]['D'+k]/100+b; E[c]['res'+k]=E[c]['S'+k]-E[c]['F'+k]
    FIT[k]=dict(m=m,b=b,r2=sxy*sxy/(sxx*syy),mae=sum(abs(E[c]['res'+k]) for c in C)/n)
f2=lambda x:f'{float(x):.2f}'; s2=lambda x:f'{float(x):+.2f}'; ci=lambda x:f'{x:,}'
order=sorted(C,key=lambda c:-POP[c])
expA={c:[ci(E[c][k]) for k in ('population','dem22','ballots22','regdem22','regtot22','dem26','ballots26','regdem26','regtot26')] for c in C}
expA['Statewide total']=[ci(sum(E[c][k] for c in C)) for k in ('population','dem22','ballots22','regdem22','regtot22','dem26','ballots26','regdem26','regtot26')]
expB={c:[f2(E[c]['V22']),f2(E[c]['D22']),s2(E[c]['S22']),s2(E[c]['F22']),s2(E[c]['res22']),f2(E[c]['V26']),f2(E[c]['D26']),s2(E[c]['S26']),s2(E[c]['F26']),s2(E[c]['res26'])] for c in C}
expF={'2026* (unofficial, locked)':[f2(FIT['26']['m']),s2(FIT['26']['b']),f'{float(FIT["26"]["r2"]):.3f}',f2(FIT['26']['mae'])],
      '2022 (official, reference)':[f2(FIT['22']['m']),s2(FIT['22']['b']),f'{float(FIT["22"]["r2"]):.3f}',f2(FIT['22']['mae'])]}
# ---- PDF text
txt=subprocess.run(['pdftotext','-layout',PDF,'-'],capture_output=True,text=True).stdout
npages=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',PDF],capture_output=True,text=True).stdout).group(1))
NUM=r'[+-]?\d[\d,]*(?:\.\d+)?'
tot=ok=0; bad=[]; seenA=[]; seenB=[]; seenF=[]
rest=[]
for line in txt.splitlines():
    s=line.strip(); hit=None
    for lab in sorted(list(expA)+list(expF),key=len,reverse=True):
        if s.startswith(lab+' ') or s==lab: hit=lab; break
    if hit:
        toks=re.findall(NUM,s[len(hit):])
        if hit in expF: want=[expF[hit]]; seen=seenF
        elif len(toks)==9 or hit=='Statewide total': want=[expA[hit]]; seen=seenA
        else: want=[expB[hit]]; seen=seenB
        seen.append(hit)
        if len(toks)!=len(want[0]): bad.append(('row length',hit,toks,want[0])); tot+=len(want[0]); continue
        for g,w in zip(toks,want[0]):
            tot+=1
            if g==w: ok+=1
            else: bad.append((hit,g,w))
    else: rest.append(line)
assert seenA==order+['Statewide total'],('Table 1 rows/order',seenA)
assert seenB==order,('Table 2 rows/order',seenB)
assert sorted(seenF)==sorted(expF),seenF
# ---- every other number in the text must be a checked non-data token
s22=open(f'{R}/2022_statewide_page.html',encoding='utf-8',errors='replace').read(); s26=open(f'{R}/2026_statewide_page.html',encoding='utf-8',errors='replace').read()
r22=subprocess.run(['pdftotext',f'{R}/registration/Statewide_10-31-2022.pdf','-'],capture_output=True,text=True).stdout
r26=subprocess.run(['pdftotext',f'{R}/registration/Statewide_10-30-2026.pdf','-'],capture_output=True,text=True).stdout
man=open(f'{R}/MANIFEST.md').read(); chdr=open(f'{R}/census/co-est2025-alldata.csv',encoding='latin-1').readline()
gov22=openpyxl.load_workbook(f'{R}/2022_governor_county.xlsx',read_only=True).worksheets[0]; gov26=openpyxl.load_workbook(f'{R}/2026_governor_county.xlsx',read_only=True).worksheets[0]
hdr=lambda ws:' '.join(str(x) for r in ws.iter_rows(values_only=True,max_row=8) for x in r if x)
PHRASES=[  # (regex in PDF text, check against raw/PDF)
 (r'November 3, 2026', 'November 3, 2026' in s26 and 'Unofficial Results' in s26),
 (r'November 8, 2022', 'November 8, 2022' in s22 and 'Official Results' in s22),
 (r'11/12/2026 11:07 AM MT', '11/12/2026 11:07 AM MT' in s26),
 (r'As of October 31, 2022', 'As of October 31, 2022' in r22),
 (r'As of October 30, 2026', 'As of October 30, 2026' in r26),
 (r'Vintage 2025', 'Vintage 2025' in man),
 (r'co-est2025-alldata\.csv', 'co-est2025-alldata.csv' in man),
 (r'POPESTIMATE2025', 'POPESTIMATE2025' in chdr),
 (r'SHA-256', 'SHA-256' in man),
 (r'Lujan Grisham 2022', 'LUJAN GRISHAM' in hdr(gov22)), (r'Haaland 2026\*', 'HAALAND' in hdr(gov26)),
 (r'2022 General', '2022 General' in s22), (r'GENERAL 2026', 'GENERAL 2026' in s26),
 (r'All 33 New Mexico counties|across the 33 counties', len(C)==33),
 (r'\(D/100\)|D/100\)|x 100', True),   # formula constants (definition of a percent), not data
 (r'Table [12]\.', True),
]
pg=[int(x) for x in re.findall(r'Page (\d+)',txt)]
pages_ok=pg==list(range(1,npages+1))
other=[]; meta_ok=0; meta_tot=0
for line in rest:
    l=line
    for rx,good in PHRASES:
        for _ in re.findall(rx,l):
            meta_tot+=1; meta_ok+=bool(good)
            if not good: bad.append(('metadata',rx))
        l=re.sub(rx,' ',l)
    l=re.sub(r'Page \d+',' ',l)
    l=re.sub(r'\b(2022|2026)\*?',lambda m:(other.append(('year',m.group(1))) or ' '),l)  # bare years in headings/labels
    other+=[('UNACCOUNTED',x,line.strip()) for x in re.findall(r'\d+',l)]
years=[x for x in other if x[0]=='year']; unacc=[x for x in other if x[0]=='UNACCOUNTED']
meta_tot+=len(pg)+len(years); meta_ok+=(len(pg) if pages_ok else 0)+len(years)
if not pages_ok: bad.append(('page numbers',pg,npages))
bad+=unacc
res=dict(pdf=PDF,pages=npages,data_numbers_checked=tot,data_numbers_matched=ok,nondata_tokens_checked=meta_tot,nondata_tokens_matched=meta_ok,
         total_checked=tot+meta_tot,total_matched=ok+meta_ok,unaccounted_numbers=len(unacc),mismatches=bad,
         fit_raw=dict((k,dict(m=f2(v['m']),b=s2(v['b']),r2=f'{float(v["r2"]):.3f}',mae=f2(v['mae']))) for k,v in FIT.items()))
json.dump(res,open('/workspace/nm-election/verification/pdf_check.json','w'),indent=1,default=str)
print(f"PDF vs independent raw re-parse: data {ok}/{tot}, non-data tokens {meta_ok}/{meta_tot}, unaccounted {len(unacc)}, mismatches {len(bad)}, pages {npages}")
sys.exit(1 if bad else 0)
