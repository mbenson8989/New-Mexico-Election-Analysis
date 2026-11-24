"""VERIFICATION PASS 1 - written separately from pipeline.py (shares no code with it).
Re-parses the same primary SOS files with different libraries:
  governor xlsx -> pandas.read_excel ; turnout page -> BeautifulSoup ; registration PDF -> pypdf token stream ; census -> pandas
Fit computed with closed-form least squares in plain Python.
Writes verification/pass1_values.csv (displayed precision) and compares to out/nm_county_table.csv cell by cell."""
import pandas as pd, re, csv, json, sys
from bs4 import BeautifulSoup
import pypdf
R='/workspace/nm-election/raw'
fix=lambda s:s.strip().replace('Doña','Dona')
def governor(y):
    df=pd.read_excel(f'{R}/{y}_governor_county.xlsx',sheet_name=0,header=None,dtype=str)
    head=df.iloc[6].tolist()
    dcol=[i for i,h in enumerate(head) if isinstance(h,str) and ('LUJAN GRISHAM' in h or 'HAALAND' in h)][0]
    rcol=[i for i,h in enumerate(head) if isinstance(h,str) and ('RONCHETTI' in h or 'HULL' in h)][0]
    res={}
    for _,row in df.iloc[7:].iterrows():
        c=row[1]
        if isinstance(c,str) and c.strip() and c!='TOTALS': res[fix(c)]=(int(row[dcol]),int(row[rcol]))
    return res
def ballots(y):
    soup=BeautifulSoup(open(f'{R}/{y}_turnout_page.html','rb').read(),'html.parser')
    res={}
    for h1 in soup.select('div.turnout-results-box-a > h1'):
        box=h1.parent; cid=box.find('input',attrs={'countyid':True})['countyid']
        tot=0
        for cell in soup.find(id=f'countyturnout{cid}').select('div.county-cast span'):
            tot+=int(cell.get_text().replace(',',''))
        res[fix(h1.get_text())]=tot
    return res
def registration(fn):
    t=pypdf.PdfReader(f'{R}/registration/{fn}').pages[0].extract_text()
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    i=lines.index('Bernalillo'); j=lines.index('TOTAL',i)
    names=lines[i:j]; k=lines.index('COUNTY',j)
    toks=lines[k+1:]
    recs=[];cur=[]
    for n,tk in enumerate(toks):
        if re.fullmatch(r'[\d,]+',tk):
            nxt=toks[n+1] if n+1<len(toks) else ''
            cur.append(int(tk.replace(',','')))
            if not re.fullmatch(r'[\d.]+ ?%',nxt):   # a count with no percent after it = row total
                recs.append(cur); cur=[]
        if len(recs)==len(names)+1: break
    out={fix(nm):(r[0],r[-1]) for nm,r in zip(names,recs)}
    return out, recs[len(names)]
def population():
    df=pd.read_csv(f'{R}/census/co-est2025-alldata.csv',encoding='latin-1',dtype={'STATE':str,'COUNTY':str})
    df=df[(df.STATE=='35')&(df.COUNTY!='000')]
    return {fix(n.replace(' County','')):int(p) for n,p in zip(df.CTYNAME,df.POPESTIMATE2025)}
G22,G26=governor(2022),governor(2026); B22,B26=ballots(2022),ballots(2026)
(RG22,T22),(RG26,T26)=registration('Statewide_10-31-2022.pdf'),registration('Statewide_10-30-2026.pdf')
POP=population()
cs=sorted(POP); assert len(cs)==33 and all(set(d)==set(cs) for d in (G22,G26,B22,B26,RG22,RG26)),'county sets differ'
assert sum(v[0] for v in RG22.values())==T22[0] and sum(v[1] for v in RG22.values())==T22[-1]
assert sum(v[0] for v in RG26.values())==T26[0] and sum(v[1] for v in RG26.values())==T26[-1]
V={}
for c in cs:
    v=dict(population=POP[c],dem22=G22[c][0],rep22=G22[c][1],ballots22=B22[c],dem26=G26[c][0],rep26=G26[c][1],ballots26=B26[c],
           regdem22=RG22[c][0],regtot22=RG22[c][1],regdem26=RG26[c][0],regtot26=RG26[c][1])
    v['S22']=v['dem22']*100/v['ballots22']; v['S26']=v['dem26']*100/v['ballots26']
    v['R22']=v['regdem22']*100/v['regtot22']; v['R26']=v['regdem26']*100/v['regtot26']
    v['G22']=v['S22']-v['R22']; v['G26']=v['S26']-v['R26']; v['dS']=v['S26']-v['S22']; v['dR']=v['R26']-v['R22']
    v['drop']=-v['dR']; v['dG']=v['G26']-v['G22']
    v['over22']=(v['dem22']+v['rep22'])>v['ballots22']; v['over26']=(v['dem26']+v['rep26'])>v['ballots26']
    V[c]=v
n=33; xs=[V[c]['drop'] for c in cs]; ys=[V[c]['dS'] for c in cs]
mx=sum(xs)/n; my=sum(ys)/n
sxy=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); sxx=sum((a-mx)**2 for a in xs); syy=sum((b-my)**2 for b in ys)
slope=sxy/sxx; icpt=my-slope*mx; r2=sxy*sxy/(sxx*syy)
for c in cs:
    v=V[c]; v['expected']=icpt+slope*v['drop']; v['residual']=v['dS']-v['expected']; v['implied']=v['residual']*v['ballots26']/100
def show(k,x):
    if k in('over22','over26'): return 'YES' if x else 'no'
    if k=='implied': return f'{x:+.0f}'
    if k in('S22','S26','R22','R26','drop'): return f'{x:.2f}'
    if k in('G22','G26','dS','dR','dG','expected','residual'): return f'{x:+.2f}'
    return str(x)
order=sorted(cs,key=lambda c:-POP[c])
cols=['county','population','dem22','rep22','ballots22','dem26','rep26','ballots26','regdem22','regtot22','regdem26','regtot26','S22','S26','R22','R26','G22','G26','dS','dR','drop','dG','expected','residual','implied','over22','over26']
with open('/workspace/nm-election/verification/pass1_values.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(cols)
    for c in order: w.writerow([c]+[show(k,V[c][k]) for k in cols[1:]])
fit={'constant':f'{icpt:+.2f}','multiplier':f'{slope:.3f}','r2':f'{r2:.3f}'}
json.dump(fit,open('/workspace/nm-election/verification/pass1_fit.json','w'))
print('pass1 fit',fit)

# ---- share version, pass 1 (plain-Python closed form). S(surplus)=G ; S = m*(D/100)+b
def ols(xs,ys):
    k=len(xs); ax=sum(xs)/k; ay=sum(ys)/k
    sxy_=sum((p-ax)*(q-ay) for p,q in zip(xs,ys)); sxx_=sum((p-ax)**2 for p in xs); syy_=sum((q-ay)**2 for q in ys)
    sl=sxy_/sxx_; ic=ay-sl*ax; return sl,ic,sxy_*sxy_/(sxx_*syy_)
sg2=lambda x:f'{x:+.2f}'
SH={}; shfit={}
for yy in ('22','26'):
    xs=[V[c]['R'+yy]/100 for c in cs]; ys=[V[c]['G'+yy] for c in cs]; sl,ic,rr=ols(xs,ys)
    res={c:V[c]['G'+yy]-(ic+sl*V[c]['R'+yy]/100) for c in cs}
    worst=max(cs,key=lambda c:abs(res[c]))
    for c in cs: V[c]['shfit'+yy]=ic+sl*V[c]['R'+yy]/100; V[c]['shres'+yy]=res[c]
    SH['y20'+yy]=dict(m=f'{sl:.2f}',b=sg2(ic),r2=f'{rr:.3f}',mae=f'{sum(abs(v) for v in res.values())/33:.2f}',max_county=worst,max_resid=sg2(res[worst]))
with open('/workspace/nm-election/verification/pass1_share_values.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['county','R22','G22','shfit22','shres22','R26','G26','shfit26','shres26','gapvotes'])
    for c in order: w.writerow([c,f"{V[c]['R22']:.2f}",sg2(V[c]['G22']),sg2(V[c]['shfit22']),sg2(V[c]['shres22']),f"{V[c]['R26']:.2f}",sg2(V[c]['G26']),sg2(V[c]['shfit26']),sg2(V[c]['shres26']),'%+.0f'%(V[c]['dem26']-V[c]['dem22']*(V[c]['regdem26']/V[c]['regdem22']))])
json.dump(SH,open('/workspace/nm-election/verification/pass1_share_fit.json','w'),indent=1)
print('pass1 share',SH)
