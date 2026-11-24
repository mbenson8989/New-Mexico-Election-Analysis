#!/usr/bin/env python3
"""Stage the verified local wiki for GitHub, mirroring the Texas layout:
- main repo (publish/repo): README.md, 33-county CSV, chart PNGs, county PDF, resources/ images (no post text, no scripts)
- wiki repo (publish/wiki): the .md pages + _Sidebar.md, with every file link pointed at raw.githubusercontent.com/.../main/...
  and Home's internal page links made absolute (Texas fix: relative links break when Home is opened at /wiki).
Only link targets change; a check strips links and confirms the text is otherwise identical."""
import re, shutil, csv
from pathlib import Path
ROOT=Path('/workspace/nm-election'); W=ROOT/'wiki'; P=ROOT/'publish'
OWNER_REPO='mbenson8989/New-Mexico-Election-Analysis'
RAW=f'https://raw.githubusercontent.com/{OWNER_REPO}/main/'; WIKI=f'https://github.com/{OWNER_REPO}/wiki/'
R=P/'repo'; WK=P/'wiki'
for d in (R,WK):   # clear staged files but keep each folder's .git (the published history)
    d.mkdir(parents=True, exist_ok=True)
    for x in d.iterdir():
        if x.name == '.git': continue
        shutil.rmtree(x) if x.is_dir() else x.unlink()
files=[]
for f in sorted(W.glob('*.png'))+[W/'New-Mexico-County-Data.pdf']: files.append(f.relative_to(W))
for sub in ('resources/vote-flip','resources/guarantee-clause'):
    for f in sorted((W/sub).iterdir()):
        if f.suffix in ('.png','.csv'): files.append(f.relative_to(W))
for rel in files:
    (R/rel).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(W/rel,R/rel)
shutil.copy2(ROOT/'out/nm_county_table.csv',R/'NM_33_County_Governor_Table.csv')
fileset={str(x) for x in files}
link=re.compile(r'(\]\()([^)\s]+)(\))')
def fix(md,name):
    def rep(m):
        t=m.group(2); base=t.split('#')[0]
        if base in fileset: return m.group(1)+RAW+t+m.group(3)
        if name=='Home.md' and not re.match(r'[a-z]+:',t) and not t.startswith('#'): return m.group(1)+WIKI+t+m.group(3)
        return m.group(0)
    return link.sub(rep,md)
strip=lambda s:link.sub(lambda m:'](L)',s)
for f in sorted(W.glob('*.md')):
    src=f.read_text(); out=fix(src,f.name)
    if f.name=='_Sidebar.md':
        out=out.replace('\n*2026 figures', f'\n[33-County Data (CSV)]({RAW}NM_33_County_Governor_Table.csv)\n\n*2026 figures',1)
    else: assert strip(src)==strip(out), f.name
    (WK/f.name).write_text(out)
    for t in link.findall(out):
        u=t[1].split('#')[0]
        if u.startswith(RAW): assert (R/u[len(RAW):]).exists(), u
        else: assert not any(u.endswith(e) for e in ('.png','.pdf','.csv','.txt')), (f.name,u)
(R/'README.md').write_text(f"""# New-Mexico-Election-Analysis
New Mexico 22-26 Governor race, surplus form of Morissa Benson's locked formula (S = multiplier × (D/100) + offset, from the Nebraska Cedar County audit), ΔG and residual math, floor and ceiling counties, over-ballot check. All 33 counties, double-verified cell by cell against the raw New Mexico Secretary of State files. 2026 figures are unofficial (SOS "Unofficial Results"; state canvass pending). Analytical model and hypothesis, not a claim of fraud.

- Wiki: https://github.com/{OWNER_REPO}/wiki
- Method origin: https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit
- Data: New Mexico Secretary of State results site (electionresults.sos.nm.gov: 2022 General official, 2026 General unofficial), SOS voter-turnout pages, and SOS Voter Registration Statistics "Statewide by County" reports (Oct 31, 2022 and Oct 30, 2026); population from U.S. Census Vintage 2025.
- `NM_33_County_Governor_Table.csv`: all 33 counties, largest to smallest population.
- `New-Mexico-County-Data.pdf`: the 33-county data table with sources.
- `resources/`: vote-flip county graphics and the Guarantee Clause graphic shown on the wiki's Resources page.
""")
print('staged', len(files)+2, 'repo files;', len(list(WK.glob('*.md'))), 'wiki pages')
