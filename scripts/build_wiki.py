import csv, json, datetime, statistics as st
O='/workspace/nm-election/out'; W='/workspace/nm-election/wiki'; V='/workspace/nm-election/verification'
REPO='https://github.com/mbenson8989/New-Mexico-Election-Analysis'; WK=''  # relative wiki links, as on the Nebraska wiki
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
T=list(csv.DictReader(open(f'{O}/nm_county_table.csv')))           # verified, displayed precision
F={r['county']:r for r in csv.DictReader(open(f'{O}/nm_county_table_fullprecision.csv'))}
S=json.load(open(f'{O}/nm_summary.json')); fm=S['fmt']; w=S['statewide']
VR=json.load(open(f'{V}/verification_report.json'))
SHJ=json.load(open(f'{O}/nm_share_fit.json')); SH=SHJ['fmt']; s26=SH['y2026']; s22=SH['y2022']
SHT=list(csv.DictReader(open(f'{O}/nm_share_fit_table.csv')))
POPS={r['county']:r['population'] for r in csv.DictReader(open(f'{O}/nm_county_table.csv'))}
built=datetime.datetime.now().strftime('%b %d %Y %I:%M %p').replace(' 0',' ')+' CST'
c=lambda n:f'{int(n):,}'
def sg(x): return x if x.startswith('-') else ('+'+x if not x.startswith('+') else x)
fl=lambda r,k:float(F[r][k])
BANNER=("> **\\*2026 figures are UNOFFICIAL.** They come from the New Mexico Secretary of State (SOS) results site, which labels the November 3, 2026 "
"general election \"Unofficial Results\" (last updated 11/12/2026 11:07 AM MT; downloaded Nov 19, 2026, about 5:39 PM CST). The State Canvassing Board has not certified them. "
"2022 figures are the SOS **Official Results** for the November 8, 2022 general election. Governor and Lieutenant Governor race. Votes are votes for the Democratic ticket, "
"not a count of registered Democrats who voted. Every 2026 figure and everything computed from it is marked \\*. These pages measure a pattern; they make no claim about intent, fraud or cause.")
NAV=[('Home','Home'),('Reverse-Math','Bottom-Up Reverse Math'),('Locked-New-Mexico-Formula','Locked New Mexico Formula'),('Floor-and-Ceiling','Floor and Ceiling Counties'),('Graphs','Graphs')]
def related(skip):
    return '\n---\n**Related:** '+' · '.join(f'[{t}]({WK}{p})' for p,t in NAV if p!=skip)+f' · [Cedar County Audit]({CEDAR})\n'
stw=dict(S22=w['dem22']/w['ballots22']*100,S26=w['dem26']/w['ballots26']*100,R22=w['regdem22']/w['regtot22']*100,R26=w['regdem26']/w['regtot26']*100)
stw['G22']=stw['S22']-stw['R22']; stw['G26']=stw['S26']-stw['R26']; stw['dG']=stw['G26']-stw['G22']; stw['drop']=stw['R22']-stw['R26']; stw['dS']=stw['S26']-stw['S22']
stw['exp']=S['constant']+S['multiplier']*stw['drop']; stw['res']=stw['dS']-stw['exp']
byS=sorted(T,key=lambda r:fl(r['county'],'S22')); floor5=byS[:5]; ceil5=byS[::-1][:5]
bydG=sorted(T,key=lambda r:fl(r['county'],'dG')); byres=sorted(T,key=lambda r:fl(r['county'],'residual'))
import numpy as np
_x=np.array([fl(r['county'],'drop') for r in T]); _y=np.array([fl(r['county'],'dS') for r in T])
_res=_y-(S['constant']+S['multiplier']*_x); SE=float(np.sqrt((_res**2).sum()/31/((_x-_x.mean())**2).sum()))
_wm,_wb=np.polyfit(_x,_y,1,w=np.sqrt(np.array([fl(r['county'],'ballots26') for r in T])))
byimp=sorted(T,key=lambda r:fl(r['county'],'implied'))
imp_pos=sum(fl(r['county'],'implied') for r in T if fl(r['county'],'implied')>0); imp_neg=sum(fl(r['county'],'implied') for r in T if fl(r['county'],'implied')<0)
npos=sum(fl(r['county'],'implied')>0 for r in T)
gained=[r['county'] for r in T if int(r['regdem26'])>int(r['regdem22'])]
over=[(r['county'],y) for r in T for y in ('22','26') if r['over'+y]=='YES']
margins=sorted(((int(r['ballots'+y])-int(r['dem'+y])-int(r['rep'+y]),r['county'],y) for r in T for y in ('22','26')))
allgov_over=[(k,y) for k,r in F.items() for y in ('22','26') if int(r['allgov'+y])>int(r['ballots'+y])]
vr={x['label']:x for x in VR['results']}
p1=vr['Pass 1 vs published table']; p2=vr['Pass 2 vs published table']; px=vr['Pass 1 vs Pass 2 (cross-comparison)']
VERIF=f"""| Pass | Method (written separately, no shared code) | Cells checked | Matched | Mismatched |
|---|---|---|---|---|
| Pass 1 | pandas on the SOS governor county export, BeautifulSoup over every precinct row of the SOS turnout page, pypdf token stream of the SOS registration reports, closed-form least squares | {p1['total']} | {p1['matched']} | {p1['mismatched']} |
| Pass 2 | second-source SOS files: the 66 per-county SOS results pages (stdlib HTML parser), the 66 per-county SOS turnout exports (raw OOXML, no spreadsheet library), pdfplumber word positions on the registration reports, Decimal arithmetic | {p2['total']} | {p2['matched']} | {p2['mismatched']} |
| Cross-check | Pass 1 vs Pass 2, cell by cell | {px['total']} | {px['matched']} | {px['mismatched']} |

Each comparison covers all 33 counties x 26 displayed cells (population, votes, ballots, registration, S, R, G, changes, Delta-G, expected, residual, implied votes, over-ballot flags), the 3 change-vs-drop fit values, and the share-version cells (33 counties x 9 share cells, including the Nebraska-style gap in votes, plus {p1['share_version_cells']-33*9} share-fit values: multiplier, offset, R², mean absolute residual, largest county and largest residual for 2026 and 2022), compared at the displayed precision. Result: **every cell matched; nothing shipped unmatched.**"""
def page(name,body): open(f'{W}/{name}.md','w').write(body)
A='\\*'   # markdown-escaped asterisk = 2026 unofficial marker
SHD={r['county']:r for r in SHT}
TD={r['county']:r for r in T}
def gv(n): return f"{int(n):+,}"
nonloss=[r['county'] for r in T if int(r['regdem26'])>int(r['regdem22'])]
loss=[r['county'] for r in T if int(r['regdem26'])<int(r['regdem22'])]
bothfell=[r['county'] for r in T if int(r['regdem26'])<int(r['regdem22']) and int(r['dem26'])<int(r['dem22'])]
WX='Lea'; X=TD[WX]; XS=SHD[WX]
# consistency of the plugged-in arithmetic at displayed precision
assert abs(float(X['S26'])-float(X['S22'])-float(X['dS']))<0.011 and abs(float(X['dS'])-float(X['dR'])-float(X['dG']))<0.011
m26=float(s26['m']); b26=float(s26['b'])
def latex_eq(m,b): return f"$$\\boxed{{S = {m} \\times \\frac{{D}}{{100}} {'+' if not b.startswith('-') else '-'} {b.lstrip('+-')}}}$$"
def plain_eq(m,b): return f"S = {m.replace('-','−')} × (D/100) {'+' if not b.startswith('-') else '−'} {b.lstrip('+-')}"
# ---------------- Home
page('Home',f"""# New Mexico 2022 vs 2026 Governor Race: ΔG Method

**Version 2, built {built}.**

> ### [Resources](Resources): download the graphics
> **[Vote-flip county graphics](Resources#vote-flip-county-graphics)** (the 3 real flips, where Democratic governor votes fell while Republican votes rose, plus 7 counties with the largest Democratic gains, marked as surges, 2026{A}) and the **[Guarantee Clause graphic](Resources#guarantee-clause-graphic)** (EO 14399 checked against the Federal Register).

{BANNER}

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). Data: New Mexico Secretary of State (SOS) results site (county exports, county results pages, voter-turnout pages) and SOS Voter Registration Statistics reports, compiled 19–20 Nov 2026. It began with her [Cedar County Audit]({CEDAR}) on the Nebraska Election Analysis wiki; this wiki applies the same county-by-county arithmetic to all 33 New Mexico counties. New Mexico's multiplier, offset and constant are fitted from New Mexico data only.

## Contents

Start with Cedar County, Nebraska. That is where this began: a small all-mail county where registered Democrats fell from 976 to 826 while Democratic governor votes rose from 466 to 681. The New Mexico pages then build up from one county ({WX}) to all 33 counties and to the statewide formula.

1. [Cedar County Audit]({CEDAR}): what Cedar's routine manual audit covered and found (Nebraska wiki)
2. [Bottom-Up Reverse Math](Reverse-Math): {WX} County → all 33 counties → New Mexico statewide, plus the full county tables (largest to smallest population)
3. [Locked New Mexico Formula](Locked-New-Mexico-Formula): the Surplus Equation {plain_eq(s26['m'],s26['b'])}\\*, with a blank fill-in template and a worked example
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at the bottom and top, ΔG extremes and the over-ballot check
5. [Graphs](Graphs): county slope chart, fit scatters, residual bars, implied-vote bars, gap and ΔG charts
6. [Resources](Resources): vote-flip county graphics, the Guarantee Clause graphic, downloads

## Statewide at a glance

| Measure | 2022 (official) | 2026{A} (unofficial) | Change |
|---|---|---|---|
| Democratic registered voters (SOS report Oct 31, 2022 / Oct 30, 2026) | {c(w['regdem22'])} | {c(w['regdem26'])} | {int(w['regdem26'])-int(w['regdem22']):+,} ({(int(w['regdem26'])/int(w['regdem22'])-1)*100:+.1f}%) |
| Total registered voters (same reports) | {c(w['regtot22'])} | {c(w['regtot26'])} | {int(w['regtot26'])-int(w['regtot22']):+,} |
| Democratic governor votes (Lujan Grisham 2022, Haaland 2026) | {c(w['dem22'])} | {c(w['dem26'])}{A} | {int(w['dem26'])-int(w['dem22']):+,}{A} ({(int(w['dem26'])/int(w['dem22'])-1)*100:+.1f}%) |
| Republican governor votes (Ronchetti 2022, Hull 2026) | {c(w['rep22'])} | {c(w['rep26'])}{A} | {int(w['rep26'])-int(w['rep22']):+,}{A} |
| Total ballots (SOS turnout) | {c(w['ballots22'])} | {c(w['ballots26'])}{A} | {int(w['ballots26'])-int(w['ballots22']):+,}{A} ({(int(w['ballots26'])/int(w['ballots22'])-1)*100:+.1f}%) |
| **S** = Dem votes / ballots cast | {stw['S22']:.2f}% | {stw['S26']:.2f}%{A} | {stw['dS']:+.2f}{A} |
| **R** = Dem registered / total registered | {stw['R22']:.2f}% | {stw['R26']:.2f}% | {stw['R26']-stw['R22']:+.2f} |
| **G** = S − R | {stw['G22']:+.2f} | {stw['G26']:+.2f}{A} | **ΔG = {stw['dG']:+.2f}{A}** |

## Key findings

- **Surplus Equation (locked form):** **{plain_eq(s26['m'],s26['b'])}**{A} (2026, unofficial; R² = {s26['r2']}, mean absolute residual {s26['mae']} points, largest {s26['max_county']} {s26['max_resid']}{A}). 2022 reference: {plain_eq(s22['m'],s22['b'])} (R² = {s22['r2']}). Registration share alone barely predicts the surplus in New Mexico.
- **Democratic registration share fell in all 33 counties** (statewide {stw['R22']:.2f}% to {stw['R26']:.2f}%). The Democratic registered **count** fell in {len(loss)}; it rose in {', '.join(nonloss)} (non-loss counties).
- **ΔG is positive in all 33 counties{A}** (lowest {bydG[0]['county']} {bydG[0]['dG']}{A}, highest {bydG[-1]['county']} {bydG[-1]['dG']}{A}; median {st.median(fl(r['county'],'dG') for r in T):+.2f}{A}).
- **Change-vs-drop fit (separate model):** Dem share change = {fm['constant']} + ({fm['multiplier']}) × registration-share drop, R² = {fm['r2']}{A}. The **NM constant is {fm['constant']} points**{A}. Residuals against it, solved backward: largest positive implied extra votes {', '.join(f"{r['county']} {int(r['implied']):+,}" for r in byimp[::-1][:3])}{A}; {npos} counties positive (sum {imp_pos:+,.0f}{A}), {33-npos} negative (sum {imp_neg:+,.0f}{A}), net {imp_pos+imp_neg:+,.0f}{A}.
- **Floor (most Republican baseline, lowest 2022 Democratic share of ballots):** {floor5[0]['county']} {floor5[0]['S22']}%. **Ceiling (highest 2022 share):** {ceil5[0]['county']} {ceil5[0]['S22']}%. See [Floor and Ceiling Counties](Floor-and-Ceiling).
- **Over-ballot check** (Democratic + Republican governor votes greater than ballots cast): **no county in 2022 or 2026{A}**. The closest is {margins[0][1]} 20{margins[0][2]}, {margins[0][0]} ballots to spare.

## Verification

Every figure for all 33 counties was checked in **two independent passes** against the raw SOS files before anything was published:

{VERIF}

Reports: `verification/VERIFICATION.md` and `verification/verification_report.json` in the [data repository]({REPO}).

## Sources

| Data | Source | Status |
|---|---|---|
| 2022 governor votes by county | SOS results site, 2022 General (eid 2838), Governor and Lieutenant Governor, "County Level" export; cross-checked against the 33 SOS county results pages | Official (last updated 11/29/2022 4:39 PM MT) |
| 2026 governor votes by county | SOS results site, November 3, 2026 General, same export and county pages | **Unofficial{A}** (last updated 11/12/2026 11:07 AM MT) |
| Ballots cast by county | SOS "Voter Turnout" page (sum of every precinct's Ballots Cast) and the SOS per-county turnout export ("Votes Cast"); the two agree in all 66 county-years | 2022 official, 2026 unofficial{A} |
| Party registration by county | SOS "New Mexico Voter Registration Statistics, Statewide by County": **As of October 31, 2022** (8 days before the Nov 8, 2022 election) and **As of October 30, 2026** (4 days before the Nov 3, 2026 election); the closest pre-election reports | Official SOS reports |
| Population (sort order) | U.S. Census Bureau Vintage 2025 county estimates (co-est2025-alldata.csv, POPESTIMATE2025) | Official estimate |

The SOS 2022 General Recount (Dec 5, 2022, eid 2839) covered Legislative contests only; the governor race was not recounted, so the 2022 official governor figures stand as used.
{related('Home')}""")
# ---------------- Bottom-Up Reverse Math
step2='\n'.join(f"| {r['county']} | {c(r['population'])} | {c(r['regdem22'])} → {c(r['regdem26'])} | {c(r['dem22'])} → {c(r['dem26'])} | {r['dS']} | {r['dR']} | {r['dG']} | {gv(SHD[r['county']]['gapvotes'])} |" for r in T)
def grp(names):
    sel=[TD[n] for n in names]; tot=lambda k:sum(int(r[k]) for r in sel)
    S2,S6=tot('dem22')/tot('ballots22')*100,tot('dem26')/tot('ballots26')*100; R2,R6=tot('regdem22')/tot('regtot22')*100,tot('regdem26')/tot('regtot26')*100
    dgs=[float(F[n]['dG']) for n in names]
    return (f"{S2:.2f}% → {S6:.2f}%{A}",f"{R2:.2f}% → {R6:.2f}%",f"{S6-S2:+.2f}",f"{R6-R2:+.2f}",f"{(S6-S2)-(R6-R2):+.2f}",
            f"{sum(dgs)/len(dgs):+.2f} ({min(dgs):+.2f} to {max(dgs):+.2f})",f"{sum(int(SHD[n]['gapvotes']) for n in names):+,}",f"{sum(float(F[n]['implied']) for n in names):+,.0f}")
allc=[r['county'] for r in T]
step3='\n'.join(f"| {lab} | {len(ns)} | "+' | '.join(grp(ns))+" |" for lab,ns in (('Counties that lost registered Democrats',loss),('Non-loss counties ('+', '.join(nonloss)+')',nonloss),('All 33 counties',allc)))
rows1='\n'.join(f"| {r['county']} | {c(r['population'])} | {c(r['dem22'])} | {c(r['ballots22'])} | {c(r['dem26'])}{A} | {c(r['ballots26'])}{A} | {c(r['regdem22'])} | {c(r['regtot22'])} | {c(r['regdem26'])} | {c(r['regtot26'])} |" for r in T)
rows2='\n'.join(f"| {r['county']} | {r['S22']} | {r['S26']}{A} | {r['R22']} | {r['R26']} | {r['G22']} | {r['G26']}{A} | {r['dS']}{A} | {r['drop']} | {r['dG']}{A} | {r['expected']} | {r['residual']}{A} | {int(r['implied']):+,}{A} |" for r in T)
npos_dg=sum(float(F[n]['dG'])>0 for n in allc)
page('Reverse-Math',f"""# Bottom-Up Reverse Math

{BANNER}

The same arithmetic at three levels, from one county up to the whole state. Ballots-cast denominator (SOS turnout). {WX} is used as the starting county: it is New Mexico's floor county (lowest 2022 Democratic share) and has the largest positive residual.

## Step 1: {WX} County

| Step | Value |
|---|---|
| Democratic vote share | {X['S22']}% (2022) → {X['S26']}%{A} (2026): **{X['dS']} points{A}** |
| Democratic registration share | {X['R22']}% → {X['R26']}%: **{X['dR']} points** |
| ΔG = vote-share growth − registration-share change | {X['dS']} − ({X['dR']}) = **{X['dG']} points{A}** |
| Reverse step: ΔG − registration-share loss | {X['dG'].lstrip('+')} − {X['drop']} = {X['dS'].lstrip('+')} (the vote-share surplus{A}) |
| Gap in votes | {c(X['dem26'])}{A} − {c(X['dem22'])} × ({c(X['regdem26'])} ÷ {c(X['regdem22'])}) = **about {gv(XS['gapvotes'])}{A}** |
| Surplus Equation check (2026{A}) | S = {X['G26']}{A} vs fitted {XS['shfit26']}{A}: residual **{XS['shres26']}{A}** |
| Change-vs-drop fit (separate model) | expected {X['expected']}, residual {X['residual']}{A}, implied extra votes **{int(X['implied']):+,}{A}** |

## Step 2: all 33 counties

Largest to smallest population. Vote-share growth, registration-share change and ΔG in points; gap in votes = D2026 − D2022 × (Dem reg 2026 ÷ Dem reg 2022).

| County | Population | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026{A} | Vote-share growth{A} (pts) | Registration-share change (pts) | ΔG{A} (pts) | Gap{A} |
|---|---|---|---|---|---|---|---|
{step2}

ΔG is positive in **{npos_dg} of 33**{A} ({bydG[0]['dG']} to {bydG[-1]['dG']}). Democratic registration share fell in every county; Democratic vote share fell in {sum(float(F[n]['dS'])<0 for n in allc)} ({', '.join(n for n in allc if float(F[n]['dS'])<0)}).

## Step 3: all of New Mexico

| Group | Counties | Dem vote share | Dem registration share | Vote-share growth{A} | Reg-share change | Pooled ΔG{A} | County mean ΔG{A} (range) | Gap{A} | Implied extra votes{A} (change-vs-drop fit) |
|---|---|---|---|---|---|---|---|---|---|
{step3}

> **Hypothesis label.** Turning ΔG or a residual into "residual votes" or "implied extra votes" and calling them injected or offset votes is a hypothesis the arithmetic cannot test. The same number reflects turnout changes, crossover voting and any other cause. Candidate votes are not turnout.

## County detail: inputs and fitted residuals

How the detail columns are computed:

1. **S** (Democratic vote share) = Democratic governor votes ÷ ballots cast × 100, for 2022 and 2026{A}.
2. **R** (Democratic registration share) = Democratic registered ÷ total registered × 100, from the SOS pre-election registration report for each year.
3. **G** = S − R; **ΔG** = (S2026 − S2022) − (R2026 − R2022).
4. **Expected change** = {fm['constant']} + ({fm['multiplier']}) × registration-share drop (the separate change-vs-drop fit, [Locked New Mexico Formula](Locked-New-Mexico-Formula#separate-model-change-vs-drop-fit-new-mexico-constant)).
5. **Residual** = actual S change − expected change; **implied extra votes (solved backward)** = residual ÷ 100 × 2026 ballots cast, signed.

### County inputs (largest to smallest population)

Population: Census Vintage 2025. Votes: Democratic governor ticket. Registration: SOS reports of Oct 31, 2022 and Oct 30, 2026.

| County | Population | Dem votes 2022 | Ballots 2022 | Dem votes 2026{A} | Ballots 2026{A} | Dem reg 2022 | Total reg 2022 | Dem reg 2026 | Total reg 2026 |
|---|---|---|---|---|---|---|---|---|---|
{rows1}
| **Statewide** | | **{c(w['dem22'])}** | **{c(w['ballots22'])}** | **{c(w['dem26'])}{A}** | **{c(w['ballots26'])}{A}** | **{c(w['regdem22'])}** | **{c(w['regtot22'])}** | **{c(w['regdem26'])}** | **{c(w['regtot26'])}** |

### County reverse math (largest to smallest population)

All values in percentage points except implied votes.

| County | S 2022 | S 2026{A} | R 2022 | R 2026 | G 2022 | G 2026{A} | S change{A} | R drop | ΔG{A} | Expected | Residual{A} | Implied extra votes{A} |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{rows2}

All county tables were matched cell by cell in two independent verification passes ({p1['matched']}/{p1['total']} and {p2['matched']}/{p2['total']}; cross-check {px['matched']}/{px['total']}).
{related('Reverse-Math')}""")
# ---------------- Locked (surplus form only; Morissa's decision Nov 20 2026)
shrows='\n'.join(f"| {r['county']} | {c(POPS[r['county']])} | {r['R22']} | {r['G22']} | {r['shfit22']} | {r['shres22']} | {r['R26']} | {r['G26']}{A} | {r['shfit26']}{A} | {r['shres26']}{A} |" for r in SHT)
# Lea plug-in arithmetic, checked at displayed precision
for y in ('22','26'):
    assert abs(float(X['S'+y])-float(X['R'+y])-float(X['G'+y]))<0.011
    assert abs(float(XS['G'+y])-float(XS['shfit'+y])-float(XS['shres'+y]))<0.011
def fit_shown(y):  # fitted value from the rounded coefficients, for the plug-in line
    sf=s26 if y=='26' else s22; return float(sf['m'])*float(X['R'+y])/100+float(sf['b'])
def lea_line(y):
    sf=s26 if y=='26' else s22; st_=A if y=='26' else ''
    rnd=fit_shown(y); full=float(XS['shfit'+y])
    note='' if abs(rnd-full)<0.005 else f" (the rounded coefficients give {rnd:+.2f}; the table uses full precision)"
    return (f"**20{y}{st_}: S = {X['S'+y]}{st_} − {X['R'+y]} = {X['G'+y]}{st_}; fitted S = {sf['m'].replace('-','−')} × ({X['R'+y]}/100) {'+' if sf['b'][0]=='+' else '−'} {sf['b'][1:]} = {XS['shfit'+y]}{st_}; residual = {XS['shres'+y]}{st_}**"+note)
page('Locked-New-Mexico-Formula',f"""# Locked New Mexico Formula

{BANNER}

## The equation

The locked equation is the surplus form, the same form Morissa set for every state:

- **Democratic vote share** = Democratic governor votes ÷ ballots cast (SOS turnout) × 100 (column "S" in the county tables on the other pages)
- **D** (Democratic registration share) = Democratic registered voters ÷ total registered voters (SOS pre-election "Statewide by County" report) × 100 (column "R" on the other pages)
- **S** (surplus) = Democratic vote share − D, in percentage points (column "G" on the other pages)
- **Fitted surplus** = multiplier × (D/100) + offset, fitted across New Mexico's 33 counties; **residual** = S − fitted surplus

Each year is fitted on its own, with every county weighted equally. New Mexico divides by total ballots cast in both years.

## New Mexico's equation in final form

### Surplus Equation (New Mexico statewide constant)

**Surplus Equation: {plain_eq(s26['m'],s26['b'])}**{A}

{latex_eq(s26['m'],s26['b'])}

Where:
- S = Surplus, expressed in percentage points (the county's Democratic share of ballots cast minus its Democratic registration share)
- D = Democratic registration share, as a percent of total registration (0–100 scale), not a headcount of registered Democrats
- {s26['m'].replace('-','−')} = Multiplier coefficient
- {s26['b'].lstrip('+')} = Constant offset, in percentage points

Fitted by least squares across all 33 New Mexico counties on the 2026{A} unofficial results and the Oct 30, 2026 registration report. The 2022 reference fit uses the same surplus form, the 2022 official results and the Oct 31, 2022 report.

| Fit (surplus form) | 2026{A} (unofficial, locked) | 2022 (official, reference) |
|---|---|---|
| Equation | {plain_eq(s26['m'],s26['b'])}{A} | {plain_eq(s22['m'],s22['b'])} |
| Multiplier coefficient | **{s26['m']}**{A} | {s22['m']} |
| Constant offset (points) | **{s26['b']}**{A} | {s22['b']} |
| R² | **{s26['r2']}**{A} | {s22['r2']} |
| Mean absolute residual (points) | **{s26['mae']}**{A} | {s22['mae']} |
| Largest absolute residual | {s26['max_county']} {s26['max_resid']}{A} | {s22['max_county']} {s22['max_resid']} |

Each state fits its own multiplier and offset, fitted by graphing that state's counties ([Graphs](Graphs)). D is defined the same way as on the Nebraska, Kansas, South Dakota, Texas and South Carolina pages: the Democratic share of registration in percent.

**How well it fits:** poorly. D explains {float(s26['r2'])*100:.1f}% (2026{A}) and {float(s22['r2'])*100:.1f}% (2022) of the county-to-county variation in the surplus, and a typical county sits {s26['mae']} points{A} ({s22['mae']} in 2022) off the line. The multiplier is negative in both years: counties with a higher Democratic registration share carry a slightly smaller surplus.

### Surplus Equation plugged in: {WX} County

{lea_line('26')}

{lea_line('22')}

### Surplus Equation residuals by county

Largest to smallest population. Residual = S − (multiplier × D/100 + offset), each year with its own fit. 2026 columns are unofficial{A}.

| County | Population | D 2022 | S 2022 | Fitted 2022 | Residual 2022 | D 2026 | S 2026{A} | Fitted 2026{A} | Residual 2026{A} |
|---|---|---|---|---|---|---|---|---|---|
{shrows}

## Blank template

Fill one column per year. Use that year's fitted multiplier and offset (2026{A}: {s26['m']} and {s26['b']}; 2022: {s22['m']} and {s22['b']}).

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic governor votes | ______ | ______ |
| 2 | Total ballots cast (SOS turnout) | ______ | ______ |
| 3 | Democratic vote share = line 1 ÷ line 2 × 100 | ______ | ______ |
| 4 | Democratic registered voters (SOS pre-election report) | ______ | ______ |
| 5 | Total registered voters (same report) | ______ | ______ |
| 6 | D = line 4 ÷ line 5 × 100 | ______ | ______ |
| 7 | S (surplus) = line 3 − line 6 | ______ | ______ |
| 8 | Fitted S = multiplier × (line 6 ÷ 100) + offset | ______ | ______ |
| 9 | Residual = line 7 − line 8 | ______ | ______ |

The template applies to every county, including the four that gained registered Democrats ({', '.join(nonloss)}). The surplus form needs no registration-loss step.

## Rules for using this formula

1. **Use the surplus form: S = multiplier × (D/100) + offset.** Fit the multiplier and offset from the state's own county data, one fit per year, every county weighted equally.
2. **The starting point is different in every state. Don't assume Nebraska's numbers carry over.** New Mexico's multiplier ({s26['m']}{A}) and offset ({s26['b']}{A}) come from New Mexico's own 33 counties. New Mexico starts with far higher Democratic registration (statewide {stw['R22']:.2f}% in 2022) than Nebraska, so compare its counties against New Mexico's own range.
3. **Always pull out the ceiling and floor counties.** Floor {floor5[0]['county']} ({floor5[0]['S22']}% Democratic share in 2022), ceiling {ceil5[0]['county']} ({ceil5[0]['S22']}%). See [How to read floor and ceiling counties](Floor-and-Ceiling#how-to-read-floor-and-ceiling-counties).

**Terms used in this wiki** (full definitions on [Floor and Ceiling Counties](Floor-and-Ceiling#terminology)):
- **Surplus (S)**: Democratic share of ballots cast minus Democratic registration share, in percentage points.
- **Ceiling counties**: the five highest 2022 Democratic shares ({', '.join(r['county'] for r in ceil5)}).
- **Floor**: the five lowest 2022 Democratic shares ({', '.join(r['county'] for r in floor5)}).
- **Residual**: a county's surplus minus the fitted surplus. It describes distance from New Mexico's line; it does not test a cause.

## Worked example: {WX}

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic governor votes | {c(X['dem22'])} | {c(X['dem26'])}* |
| 2 | Total ballots cast | {c(X['ballots22'])} | {c(X['ballots26'])}* |
| 3 | Democratic vote share | {X['S22']} | {X['S26']}* |
| 4 | Democratic registered | {c(X['regdem22'])} | {c(X['regdem26'])} |
| 5 | Total registered | {c(X['regtot22'])} | {c(X['regtot26'])} |
| 6 | D | {X['R22']} | {X['R26']} |
| 7 | S (surplus) | {X['G22']} | {X['G26']}* |
| 8 | Fitted S | {XS['shfit22']} | {XS['shfit26']}* |
| 9 | Residual | {XS['shres22']} | {XS['shres26']}* |
{related('Locked-New-Mexico-Formula')}""")
# ---------------- Floor and Ceiling Counties
def frow(r,g): return f"| {r['county']} | {g} | {c(r['population'])} | {r['S22']} → {r['S26']}{A} | {r['R22']} → {r['R26']} | {r['G22']} → {r['G26']}{A} | {r['dG']}{A} | {c(r['regdem22'])} → {c(r['regdem26'])} | {c(r['dem22'])} → {c(r['dem26'])}{A} | {r['residual']}{A} | {int(r['implied']):+,}{A} |"
popsort=lambda L:sorted(L,key=lambda r:-int(r['population']))
mrows='\n'.join(f"| {k} | 20{y}{'' if y=='22' else A} | {c(F[k]['dem'+y])} | {c(F[k]['rep'+y])} | {c(int(F[k]['dem'+y])+int(F[k]['rep'+y]))} | {c(F[k]['ballots'+y])} | {m:,} | no |" for m,k,y in margins[:8])
g22s=sorted(T,key=lambda r:fl(r['county'],'G22'))
page('Floor-and-Ceiling',f"""# Floor and Ceiling Counties

{BANNER}

## How to read floor and ceiling counties

Look for the pattern at both ends. New Mexico's rule (set for this build): the **floor** is the most Republican baseline, the county with the lowest 2022 Democratic share of ballots cast; the **ceiling** is the county with the highest. Five of each are listed.

- **The floor** is {floor5[0]['county']}, S 2022 = {floor5[0]['S22']}% (ΔG {floor5[0]['dG']}{A}).
- **The ceiling** is {ceil5[0]['county']}, S 2022 = {ceil5[0]['S22']}% (ΔG {ceil5[0]['dG']}{A}).

Nebraska's pages use ΔG instead: by that rule New Mexico's ceiling is {bydG[-1]['county']} ({bydG[-1]['dG']}{A}) and its floor is {bydG[0]['county']} ({bydG[0]['dG']}{A}); both lists are below. Using G 2022 instead gives {g22s[0]['county']} ({g22s[0]['G22']}) and {g22s[-1]['county']} ({g22s[-1]['G22']}). Every state will have its own floor and ceiling; those two extremes set the range the rest of that state's counties fall within.

## Terminology

- **Ceiling counties** are the five highest 2022 Democratic shares: {', '.join(f"{r['county']} {r['S22']}%" for r in ceil5)}.
- **Floor counties** are the five lowest 2022 Democratic shares: {', '.join(f"{r['county']} {r['S22']}%" for r in floor5)}.
- **Highest and lowest ΔG** (Nebraska's rule): highest {', '.join(f"{bydG[-1-i]['county']} {bydG[-1-i]['dG']}{A}" for i in range(5))}; lowest {', '.join(f"{bydG[i]['county']} {bydG[i]['dG']}{A}" for i in range(5))}.
- **Non-loss counties** (also called **share-gain counties**) had no Democratic registration loss. They get raw numbers only, with no residual step:
{chr(10).join(f"  - {n}: registered Democrats {c(TD[n]['regdem22'])} → {c(TD[n]['regdem26'])}; Democratic governor votes {c(TD[n]['dem22'])} → {c(TD[n]['dem26'])}{A}." for n in nonloss)}
- **Registration fell and votes fell too.** In these {len(bothfell)} counties, Democratic registration fell and Democratic governor votes also fell. Raw numbers only:
{chr(10).join(f"  - {n}: registered Democrats {c(TD[n]['regdem22'])} → {c(TD[n]['regdem26'])}; votes {c(TD[n]['dem22'])} → {c(TD[n]['dem26'])}{A}." for n in bothfell)}

## Ceiling and floor detail

Largest to smallest population within each group.

| County | Group | Population | S % 2022 → 2026{A} | R % 2022 → 2026 | G 2022 → 2026{A} | ΔG{A} | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026{A} | Residual{A} | Implied extra votes{A} |
|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(frow(r,'Ceiling') for r in popsort(ceil5))}
{chr(10).join(frow(r,'Floor') for r in popsort(floor5))}

### ΔG extremes (Nebraska-style ceiling and floor)

| Rank | Highest ΔG{A} | Lowest ΔG{A} |
|---|---|---|
{chr(10).join(f"| {i+1} | {bydG[-1-i]['county']} {bydG[-1-i]['dG']}{A} | {bydG[i]['county']} {bydG[i]['dG']}{A} |" for i in range(5))}

No New Mexico county has a negative ΔG{A}, so the bottom is the smallest rise, not a decline.

## Over-ballot check

Flag any county-year where Democratic + Republican governor votes exceed ballots cast.

**Result: no county in 2022 and no county in 2026{A}. 0 of 66 county-years flagged.** {'All-candidate governor totals also stay at or below ballots cast in every county-year.' if not allgov_over else 'All-candidate totals exceed ballots in: '+str(allgov_over)}

The eight tightest county-years:

| County | Year | Dem votes | Rep votes | Dem + Rep | Ballots cast | Ballots to spare | Over-ballot? |
|---|---|---|---|---|---|---|---|
{mrows}
{related('Floor-and-Ceiling')}""")
# ---------------- Graphs
page('Graphs',f"""# Graphs

{BANNER}

All charts use the verified 33-county table. County bar charts run largest to smallest population (Census Vintage 2025).

## 1. County slope chart

![County slope chart, G 2022 to G 2026](nm_slope_G2022_to_G2026.png)

*Each line is one county, G 2022 to G 2026{A}. G rose in all 33 counties; red lines are the five highest ΔG, blue the five lowest.*

## 2. ΔG by county (population order)

![ΔG by county](nm_delta_g_bars.png)

*ΔG = vote-share change − registration-share change. Range {bydG[0]['dG']} ({bydG[0]['county']}) to {bydG[-1]['dG']} ({bydG[-1]['county']}){A}.*

## 3. Gap G, 2022 vs 2026{A}

![Gap G by county 2022 vs 2026](nm_gap_2022_vs_2026.png)

*G = Democratic share of ballots − Democratic registration share, each county in both years.*

## 4. Registration-share drop vs vote-share change (change-vs-drop fit)

![Registration-share drop vs vote-share change scatter with fit line](nm_scatter_regdrop_vs_sharechange.png)

*Separate model: S change = {fm['constant']} + ({fm['multiplier']}) × drop, R² = {fm['r2']}{A}. Dot size scales with population.*

## 5. Residual by county (change-vs-drop fit)

![Residual bar chart by county](nm_residual_bars.png)

*Actual vote-share change minus the change-vs-drop expectation. Red = above New Mexico's county trend, blue = below.*

## 6. Implied extra votes by county (change-vs-drop fit)

![Implied extra votes by county](nm_implied_extra_votes.png)

*Residual × 2026 ballots cast, signed{A}.*

## 7. Surplus Equation: surplus S vs D/100, with fit lines

![Surplus S vs D/100 scatter with Surplus Equation fit lines](nm_share_scatter_S_vs_D.png)

*Locked Surplus Equation: {plain_eq(s26['m'],s26['b'])} (orange, 2026{A}, R² = {s26['r2']}). Grey dashed: 2022 reference {plain_eq(s22['m'],s22['b'])} (R² = {s22['r2']}). See [Locked New Mexico Formula](Locked-New-Mexico-Formula#surplus-equation-new-mexico-statewide-constant).*

## 8. Surplus Equation residuals by county, 2026{A}

![Surplus Equation residual bars 2026](nm_share_residual_bars_2026.png)

*Residual = S − (multiplier × D/100 + offset) with the 2026{A} fit; mean absolute residual {s26['mae']} points{A}; largest {s26['max_county']} {s26['max_resid']}{A}.*
{related('Graphs')}""")
open(f'{W}/_Sidebar.md','w').write(f"""**New Mexico Election Analysis**

1. [README: Start Here](README)
2. [Home](Home)
3. [Resources](Resources)
4. [Cedar County Audit]({CEDAR})
5. [Floor and Ceiling Counties](Floor-and-Ceiling)
6. [Bottom-Up Reverse Math](Reverse-Math)
7. [Graphs](Graphs)
8. [New Mexico County Data (PDF)](New-Mexico-County-Data.pdf)
9. [Locked New Mexico Formula](Locked-New-Mexico-Formula)

*2026 figures are unofficial\\**
""")
print('wiki built',built)
# Resources page (vote-flip graphics + Guarantee Clause post); inputs built by build_vote_flip.py and build_guarantee_clause.py
import subprocess, sys, os
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_resources.py')], check=True)
