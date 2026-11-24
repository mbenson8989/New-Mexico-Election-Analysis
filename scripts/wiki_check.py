"""Check that every county cell printed in the wiki tables equals the verified table (out/nm_county_table.csv),
and that every number in wiki/README.md and wiki/New-Mexico-County-Data.pdf (via pdftotext) equals BOTH verification passes."""
import csv,re,json
T={r['county']:r for r in csv.DictReader(open('/workspace/nm-election/out/nm_county_table.csv'))}
W='/workspace/nm-election/wiki'
def tables(md):
    out=[];cur=[]
    for l in open(md).read().splitlines():
        if l.startswith('|'): cur.append([x.strip() for x in l.strip('|').split('|')])
        elif cur: out.append(cur); cur=[]
    if cur: out.append(cur)
    return out
clean=lambda s:s.replace('\\*','').replace(',','').replace('*','').strip()
tot=ok=0; bad=[]
t=tables(f'{W}/Reverse-Math.md')
inp=[x for x in t if x[0][0]=='County' and 'Dem votes 2022' in x[0]][0]
kin=['county','population','dem22','ballots22','dem26','ballots26','regdem22','regtot22','regdem26','regtot26']
der=[x for x in t if x[0][0]=='County' and 'S 2022' in x[0]][0]
kde=['county','S22','S26','R22','R26','G22','G26','dS','drop','dG','expected','residual','implied']
order=[]
for tbl,keys in ((inp,kin),(der,kde)):
    rows=[r for r in tbl[2:] if r[0] in T]
    order.append([r[0] for r in rows]); assert len(rows)==33
    for r in rows:
        for k,v in zip(keys[1:],r[1:]):
            tot+=1; want=T[r[0]][k]
            if clean(v)==want.replace('+','') or clean(v)==want: ok+=1
            elif k=='implied' and clean(v).replace('+','')==want.replace('+',''): ok+=1
            else: bad.append((r[0],k,v,want))
fc=[x for x in tables(f'{W}/Floor-and-Ceiling.md') if x[0][1]=='Group'][0]
assert len(fc)-2==10
for r in fc[2:]:
    cty=r[0]; S=clean(r[3]).split(' → '); R=clean(r[4]).split(' → '); G=clean(r[5]).split(' → ')
    for v,k in [(r[2],'population'),(S[0],'S22'),(S[1],'S26'),(R[0],'R22'),(R[1],'R26'),(G[0],'G22'),(G[1],'G26'),(r[6],'dG'),(r[9],'residual'),(r[10],'implied')]:
        tot+=1; want=T[cty][k]
        if clean(v).replace('+','')==want.replace('+',''): ok+=1
        else: bad.append((cty,k,v,want))
# share-version residual table on the Locked page + share fit values printed on Locked/Graphs/Home
SHT={r['county']:r for r in csv.DictReader(open('/workspace/nm-election/out/nm_share_fit_table.csv'))}
SF=json.load(open('/workspace/nm-election/out/nm_share_fit.json'))['fmt']
lt=[x for x in tables(f'{W}/Locked-New-Mexico-Formula.md') if x[0][0]=='County' and 'Residual 2026*' in [clean(h)+'*' if False else h.replace('\\','') for h in x[0]]][0]
share_order=[]
for r in lt[2:]:
    share_order.append(r[0])
    for k,v in zip(['population','R22','G22','shfit22','shres22','R26','G26','shfit26','shres26'],r[1:]):
        tot+=1; want=T[r[0]]['population'] if k=='population' else SHT[r[0]][k]
        if clean(v)==want: ok+=1
        else: bad.append(('share',r[0],k,v,want))
assert len(share_order)==33
lock=open(f'{W}/Locked-New-Mexico-Formula.md').read(); gr=open(f'{W}/Graphs.md').read()
for y in ('y2026','y2022'):
    for k in ('m','b','r2','mae'):
        tot+=1
        pv=SF[y][k]; alt=pv.replace('-','−') if k=='m' else ('+ '+pv[1:] if pv[0]=='+' else '− '+pv[1:]) if k=='b' else pv
        if pv in lock and (y!='y2026' or pv in gr or alt in gr): ok+=1
        else: bad.append(('share fit text',y,k,SF[y][k]))
# Nebraska-style Step 2 table (Reverse-Math) incl. gap in votes
s2=[x for x in t if x[0][0]=='County' and x[0][-1].replace('\\','')=='Gap*'][0]
s2_order=[]
for r in s2[2:]:
    c=r[0]; s2_order.append(c); rg=clean(r[2]).split(' → '); dv=clean(r[3]).split(' → ')
    for v,want in [(r[1],T[c]['population']),(rg[0],T[c]['regdem22']),(rg[1],T[c]['regdem26']),(dv[0],T[c]['dem22']),(dv[1],T[c]['dem26']),(r[4],T[c]['dS']),(r[5],T[c]['dR']),(r[6],T[c]['dG']),(r[7],SHT[c]['gapvotes'])]:
        tot+=1
        if clean(v).replace('+','')==want.replace('+',''): ok+=1
        else: bad.append(('step2',c,v,want))
assert len(s2_order)==33
# Step 3 pooled rows recomputed here from the verified integer columns
s3=[x for x in t if x[0][0]=='Group'][0]
nonloss=[c for c in T if int(T[c]['regdem26'])>int(T[c]['regdem22'])]; loss=[c for c in T if c not in nonloss]
for row,names in zip(s3[2:],(loss,nonloss,list(T))):
    sm=lambda k:sum(int(T[c][k]) for c in names)
    S2,S6=sm('dem22')/sm('ballots22')*100,sm('dem26')/sm('ballots26')*100; R2,R6=sm('regdem22')/sm('regtot22')*100,sm('regdem26')/sm('regtot26')*100
    exp=[str(len(names)),f"{S2:.2f}% → {S6:.2f}%",f"{R2:.2f}% → {R6:.2f}%",f"{S6-S2:+.2f}",f"{R6-R2:+.2f}",f"{(S6-S2)-(R6-R2):+.2f}"]
    gsum=sum(int(SHT[c]['gapvotes']) for c in names)
    for v,want in list(zip(row[1:7],exp))+[(row[8],f"{gsum:+}")]:
        tot+=1
        if clean(v)==want.replace(',',''): ok+=1
        else: bad.append(('step3',row[0],v,want))
# Surplus Equation headline: bold line + boxed LaTeX use the verified 2026 fit
m,b=SF['y2026']['m'],SF['y2026']['b']
for frag in (f"**Surplus Equation: S = {m.replace('-','−')} × (D/100) {'+' if b[0]=='+' else '−'} {b.lstrip('+-')}**", f"\\boxed{{S = {m} \\times \\frac{{D}}{{100}} {'+' if b[0]=='+' else '-'} {b.lstrip('+-')}}}"):
    tot+=1
    if frag in lock: ok+=1
    else: bad.append(('headline',frag))
pop_sorted=[c for c in sorted(T,key=lambda c:-int(T[c]['population']))]
# ---------------- README.md and the county-data PDF, each checked against BOTH independent verification passes
import subprocess
VD='/workspace/nm-election/verification'
def load_pass(k):
    v={r['county']:r for r in csv.DictReader(open(f'{VD}/pass{k}_values.csv'))}
    sv={r['county']:r for r in csv.DictReader(open(f'{VD}/pass{k}_share_values.csv'))}
    return v,sv,json.load(open(f'{VD}/pass{k}_share_fit.json'))
VR={x['label']:x for x in json.load(open(f'{VD}/verification_report.json'))['results']}
def U(x): return x.replace('−','-')
def readme_check(k):
    v,sv,sf=load_pass(k); txt=open(f'{W}/README.md').read(); n=e=0; badr=[]
    fl_=min(v,key=lambda c:float(v[c]['S22'])); ce_=max(v,key=lambda c:float(v[c]['S22']))
    nyes=sum(r['over22']=='YES' for r in v.values())+sum(r['over26']=='YES' for r in v.values())
    def bsign(sg,num): return ('+' if sg=='+' else '-')+num
    SLOTS=[  # (regex, [expected values for each group]) - expected values come from pass k (or the compare report where marked)
     (r'2026\\\* \(unofficial, the headline\): S = (−?[0-9.]+) × \(D/100\) ([+−]) ([0-9.]+)', None, lambda g:[U(g[0])==sf['y2026']['m'], bsign(g[1],g[2])==sf['y2026']['b']]),
     (r'2022 \(official, for reference\): S = (−?[0-9.]+) × \(D/100\) ([+−]) ([0-9.]+)', None, lambda g:[U(g[0])==sf['y2022']['m'], bsign(g[1],g[2])==sf['y2022']['b']]),
     (r'R² is \*\*([0-9.]+)\\\*\*\* for 2026', None, lambda g:[g[0]==sf['y2026']['r2']]),
     (r'and \*\*([0-9.]+)\*\* for 2022', None, lambda g:[g[0]==sf['y2022']['r2']]),
     (r'sits \*\*([0-9.]+) points\\\*\*\* away', None, lambda g:[g[0]==sf['y2026']['mae']]),
     (r'\(\*\*([0-9.]+) points\*\* in 2022\)', None, lambda g:[g[0]==sf['y2022']['mae']]),
     (r"Lea's Democratic registration share in 2026 was ([0-9.]+)%", None, lambda g:[g[0]==v['Lea']['R26']]),
     (r'expects a surplus of ([+-][0-9.]+)\\\* points', None, lambda g:[g[0]==sv['Lea']['shfit26']]),
     (r'actual surplus was ([+-][0-9.]+)\\\* points', None, lambda g:[g[0]==sv['Lea']['G26']]),
     (r'its residual is ([+-][0-9.]+)\\\* points', None, lambda g:[g[0]==sv['Lea']['shres26']]),
     (r'the floor is \*\*([A-Za-z ]+)\*\* \(([0-9.]+)%\) and the ceiling is \*\*([A-Za-z ]+)\*\* \(([0-9.]+)%\)', None, lambda g:[g[0]==fl_, g[1]==v[fl_]['S22'], g[2]==ce_, g[3]==v[ce_]['S22']]),
     (r'No county failed the check\*\*: ([0-9]+) county-years', None, lambda g:[int(g[0])==nyes]),
     (r'It lists all ([0-9]+) counties', None, lambda g:[int(g[0])==len(v)]),
     (r'using all ([0-9]+) counties', None, lambda g:[int(g[0])==len(v)]),
     (r'Each pass compared \*\*([0-9]+)\*\* values', 'report', lambda g:[int(g[0])==VR[f'Pass {k} vs published table']['total']]),
     (r'pass 1: ([0-9]+) mismatches', 'report', lambda g:[int(g[0])==VR['Pass 1 vs published table']['mismatched']]),
     (r'pass 2: ([0-9]+) mismatches', 'report', lambda g:[int(g[0])==VR['Pass 2 vs published table']['mismatched']]),
    ]
    rest=re.sub(r'\]\([^)]*\)',']',txt)   # link targets (URLs/page names) are not numbers to check
    for rx,_src,test in SLOTS:
        ms=list(re.finditer(rx,rest))
        if len(ms)!=1: badr.append(('README slot not found exactly once',rx,len(ms))); continue
        res_=test(ms[0].groups()); n+=len(res_); e+=sum(res_)
        if not all(res_): badr.append(('README',rx,ms[0].groups()))
        rest=rest[:ms[0].start()]+' '*(ms[0].end()-ms[0].start())+rest[ms[0].end():]
    # anything numeric left must be a structural token: years, the SOS dates/labels, D/100, the "1 = perfect fit" scale, list numbering
    STRUCT=[r'November 3, 2026',r'October 31, 2022',r'October 30, 2026',r'Vintage 2025',r'D/100',r'where 1 would be',r'^[0-9]\. ',r'\b20(22|26)\b']
    ns=0
    for rx in STRUCT:
        ns+=len(re.findall(rx,rest,flags=re.M)); rest=re.sub(rx,' ',rest,flags=re.M)
    left=re.findall(r'[0-9]+',rest)
    for x in left: badr.append(('README number not checked',x))
    return dict(pass_=k,numbers_checked=n,matched=e,structural_tokens=ns,unchecked_numbers=len(left),mismatches=badr)
def pdf_check(k):
    v,sv,sf=load_pass(k); txt=subprocess.run(['pdftotext','-layout',f'{W}/New-Mexico-County-Data.pdf','-'],capture_output=True,text=True).stdout
    cm=lambda x:f'{int(x):,}'
    KA=['population','dem22','ballots22','regdem22','regtot22','dem26','ballots26','regdem26','regtot26']
    exA={c:[cm(v[c][q]) for q in KA] for c in v}; exA['Statewide total']=[cm(sum(int(v[c][q]) for c in v)) for q in KA]
    exB={c:[v[c]['S22'],v[c]['R22'],sv[c]['G22'],sv[c]['shfit22'],sv[c]['shres22'],v[c]['S26'],v[c]['R26'],sv[c]['G26'],sv[c]['shfit26'],sv[c]['shres26']] for c in v}
    exF={'2026* (unofficial, locked)':[sf['y2026'][q] for q in ('m','b','r2','mae')],'2022 (official, reference)':[sf['y2022'][q] for q in ('m','b','r2','mae')]}
    n=e=0; badp=[]; rowsA=[]; rowsB=[]
    for line in txt.splitlines():
        s_=line.strip(); hit=next((lab for lab in sorted(list(exA)+list(exF),key=len,reverse=True) if s_.startswith(lab+' ')),None)
        if not hit: continue
        toks=re.findall(r'[+-]?[0-9][0-9,]*(?:\.[0-9]+)?',s_[len(hit):])
        if hit in exF: want=exF[hit]
        elif len(toks)==9 or hit=='Statewide total': want=exA[hit]; rowsA.append(hit)
        else: want=exB[hit]; rowsB.append(hit)
        for g,w in zip(toks,want):
            n+=1; e+=g==w
            if g!=w: badp.append(('PDF',hit,g,w))
        if len(toks)!=len(want): badp.append(('PDF row length',hit,len(toks),len(want)))
    if rowsA!=pop_sorted+['Statewide total'] or rowsB!=pop_sorted: badp.append(('PDF rows missing or out of population order',))
    return dict(pass_=k,numbers_checked=n,matched=e,mismatches=badp)
RM={k:readme_check(k) for k in (1,2)}; PD={k:pdf_check(k) for k in (1,2)}
res=dict(wiki_cells_checked=tot,matched=ok,mismatched=bad,reverse_math_tables_in_population_order=all(o==pop_sorted for o in order) and share_order==pop_sorted and s2_order==pop_sorted,
         readme_vs_pass={str(k):v for k,v in RM.items()},pdf_vs_pass={str(k):v for k,v in PD.items()},
         readme_pdf_mismatches=sum(len(x['mismatches']) for x in list(RM.values())+list(PD.values())))
for k in (1,2): print(f"pass {k}: README {RM[k]['matched']}/{RM[k]['numbers_checked']} (+{RM[k]['structural_tokens']} structural, {RM[k]['unchecked_numbers']} unchecked); PDF {PD[k]['matched']}/{PD[k]['numbers_checked']}; mismatches {len(RM[k]['mismatches'])+len(PD[k]['mismatches'])}")
json.dump(res,open('/workspace/nm-election/verification/wiki_table_check.json','w'),indent=1)
print(res)
