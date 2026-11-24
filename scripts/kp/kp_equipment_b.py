"""Pass B for the equipment table: re-derive every county's equipment fields from the raw Verified Voting CSVs with the csv module
(no pandas) and the Census file, and compare with the pass-A CSV and summary. Writes verification/kp_equipment_check.json."""
import csv, json, io, collections
RAW='/workspace/nm-election/raw/resources/vv/'; B='/workspace/nm-election/'
TAB={'Hand-Fed Optical Scanner','Batch-Fed Optical Scanner','Hybrid BMD/Tabulator','Hybrid Optical Scan/BMD'}
ACC={'Ballot Marking Device','Hybrid BMD/Tabulator','Hybrid Optical Scan/BMD','DRE-Touchscreen'}
def rd(p):
    t=open(p,encoding='utf-8-sig').read().split('\n',1)[1]; return list(csv.DictReader(io.StringIO(t)))
def eq(r): return f"{r['Manufacturer']} {r['Model']} ({r['Equipment Type']})"
M26=rd(RAW+'vv2026/verifier-machines.csv'); J26=rd(RAW+'vv2026/verifier-jurisdictions.csv'); M22=rd(RAW+'vv2022/verifier-machines.csv')
pop={}
for r in csv.DictReader(open(B+'raw/census/co-est2025-alldata.csv',encoding='latin-1')):
    if r['STATE']=='35' and r['COUNTY']!='000': pop[r['STATE']+r['COUNTY']]=int(r['POPESTIMATE2025'])
A={r['FIPS']:r for r in csv.DictReader(open(B+'out/NM_33_County_Voting_Equipment_VerifiedVoting.csv'))}
SA=json.load(open(B+'out/kp_equipment_summary_A.json'))
bad=[]; n=0
def chk(a,b,what):
    global n; n+=1
    if a!=b: bad.append((what,a,b))
by=collections.defaultdict(list); by22=collections.defaultdict(list)
for r in M26: by[r['FIPS code'][:5]].append(r)
for r in M22: by22[r['FIPS code'][:5]].append(r)
jur={r['FIPS code'][:5]:r for r in J26}
assert set(by)==set(A)==set(pop), (len(by),len(A),len(pop))
central=[];mailed=[];pbk=collections.Counter();loc=collections.Counter();mark=collections.Counter();vend=collections.Counter()
for f in by:
    g=by[f]; a=A[f]
    ed=sorted({eq(r) for r in g if r['Election Day Standard']=='Yes' and r['Equipment Type'] in TAB})
    ml=sorted({eq(r) for r in g if r['Mail Ballot/Absentee Equipment']=='Yes' and r['Equipment Type'] in TAB})
    ac=sorted({eq(r) for r in g if r['Election Day Accessible']=='Yes' and r['Equipment Type'] in ACC})
    pb=sorted({(f"{r['Manufacturer']} {r['Model']}".strip() if r['Manufacturer'] not in ('','Not Applicable') else r['Equipment Type']) for r in g if 'Poll Book' in r['Equipment Type']})
    ed22=sorted({eq(r) for r in by22[f] if r['Election Day Standard']=='Yes' and r['Equipment Type'] in TAB})
    for x,y,w in [('; '.join(ed),a['ED tabulator equipment'],'ed'),('; '.join(ml),a['Mail tabulator equipment'],'mail'),('; '.join(ac),a['Accessible device'],'acc'),
                  ('; '.join(pb),a['Poll book'],'pollbook'),('; '.join(ed22),a['ED tabulator equipment 2022'],'ed22'),(str(pop[f]),a['Population'],'pop'),
                  (jur[f]['Election Day Marking Method'],a['Marking method'],'mark'),(jur[f]['Voting Location'],a['Voting location'],'loc'),
                  ('Confirmed (Verified Voting 2026 record)' if ed else 'Unconfirmed',a['Status'],'status')]:
        chk(x,y,(a['County'],w))
    if any('Batch-Fed' in m for m in ml): central.append(a['County'])
    else: mailed.append(a['County'])
    pbk['; '.join(pb)]+=1; loc[jur[f]['Voting Location']]+=1; mark[jur[f]['Election Day Marking Method']]+=1
    vend['; '.join(sorted({r['Manufacturer'] for r in g if r['Election Day Standard']=='Yes' and r['Equipment Type'] in TAB}))]+=1
chk(sorted(central),sorted(SA['_central_mail']),'central'); chk(sorted(mailed),sorted(SA['_mail_on_ed_unit']),'mail_on_ed')
chk(dict(pbk),SA['_pollbook'],'pollbook counts'); chk(dict(loc),SA['_location'],'location'); chk(dict(mark),SA['_marking'],'marking')
chk(sum(pop.values()),SA['_total_pop'],'total pop'); chk({k:v for k,v in vend.items()},{k:v['counties'] for k,v in SA.items() if not k.startswith('_')},'vendors')
json.dump(dict(checks=n,mismatches=len(bad),detail=bad),open(B+'verification/kp_equipment_check.json','w'),indent=1)
print('equipment pass B checks',n,'mismatches',len(bad),bad[:3]); assert not bad
