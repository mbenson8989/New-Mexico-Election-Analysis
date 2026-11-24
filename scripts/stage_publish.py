#!/usr/bin/env python3
"""Stage the Kansas-parity New Mexico wiki for GitHub (LOCAL ONLY: this script never commits or pushes).
- main repo (publish/repo): README.md, every non-page file the wiki links (charts, PDFs, Word files, CSVs, downloads/, resources/),
  plus scripts/ and verification/ reports, as the Kansas repo does. No post text (Morissa: no X/social posts).
- wiki repo (publish/wiki): the .md pages + _Sidebar.md. Every file link is pointed at raw.githubusercontent.com/.../main/...;
  Home's internal page links are made absolute. Only link targets change (checked).
- Locked-New-Mexico-Formula.md is copied BYTE FOR BYTE and its sha256 asserted (Morissa: leave the Locked page exactly as it is)."""
import re, shutil, hashlib
from pathlib import Path
ROOT=Path('/workspace/nm-election'); W=ROOT/'wiki'; P=ROOT/'publish'
OWNER_REPO='mbenson8989/New-Mexico-Election-Analysis'
RAW=f'https://raw.githubusercontent.com/{OWNER_REPO}/main/'; WIKI=f'https://github.com/{OWNER_REPO}/wiki/'
LOCKED='Locked-New-Mexico-Formula.md'; LOCKED_SHA='0af726538da73c3e03cd1f8c00b8554583a72fd4221bfb3b2f8e17f31bc9ae27'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(W/LOCKED)==LOCKED_SHA, 'local Locked page changed'
R=P/'repo'; WK=P/'wiki'
for d in (R,WK):   # clear staged files but keep each folder's .git (the published history)
    d.mkdir(parents=True, exist_ok=True)
    for x in d.iterdir():
        if x.name == '.git': continue
        shutil.rmtree(x) if x.is_dir() else x.unlink()
SKIP={'post.txt','manifest.json'}
files=[f.relative_to(W) for f in sorted(W.rglob('*')) if f.is_file() and f.suffix!='.md' and f.name not in SKIP]
for rel in files:
    (R/rel).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(W/rel,R/rel)
shutil.copy2(ROOT/'out/nm_county_table.csv',R/'NM_33_County_Governor_Table.csv')   # first-build CSV, kept at its published path
# scripts and verification reports (Kansas repo layout)
for f in sorted((ROOT/'scripts').rglob('*')):
    if f.is_file() and '__pycache__' not in f.parts and f.suffix in ('.py','.sh','.md'):
        rel=f.relative_to(ROOT); (R/rel).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,R/rel)
for f in sorted((ROOT/'verification').glob('*')):
    if f.is_file() and f.suffix in ('.json','.md','.csv'):
        rel=f.relative_to(ROOT); (R/rel).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,R/rel)
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
n=0
for f in sorted(W.glob('*.md')):
    if f.name==LOCKED:
        shutil.copyfile(f,WK/f.name); n+=1; continue
    src=f.read_text(); out=fix(src,f.name)
    assert strip(src)==strip(out), f.name
    (WK/f.name).write_text(out); n+=1
    for t in link.findall(out):
        u=t[1].split('#')[0]
        if u.startswith(RAW): assert (R/u[len(RAW):]).exists(), u
        elif not u.startswith('http'): assert not any(u.endswith(e) for e in ('.png','.pdf','.csv','.txt','.zip','.xlsx','.docx')), (f.name,u)
assert sha(WK/LOCKED)==LOCKED_SHA, 'staged Locked page differs'
(R/'README.md').write_text(f"""# New-Mexico-Election-Analysis
New Mexico 2022 vs 2026 Governor race, built the same way as the Kansas Election Analysis: G and ΔG (Democratic share of ballots cast minus Democratic share of registration), the New Mexico-only forward surplus fit S = m × (D/100) + b, floor and ceiling counties, the expected-loss residual and backward-solved offset votes (Nebraska / Iowa / South Dakota method), gap in votes, and a ballots-cast check. All 33 counties, largest to smallest population, double-verified against the raw New Mexico Secretary of State files. 2026 figures are UNOFFICIAL (SOS "Unofficial Results"; state canvass Nov 24, 2026). Analytical model and hypothesis, not a claim of fraud.

- Wiki: https://github.com/{OWNER_REPO}/wiki
- Method origin: https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit
- Data: New Mexico Secretary of State results site (electionresults.sos.nm.gov: 2022 General official, 2026 General unofficial), SOS voter-turnout pages, and SOS Voter Registration Statistics "Statewide by County" reports (Oct 31, 2022 and Oct 30, 2026); population from U.S. Census Vintage 2025.

Contents:
- `NM_Governor_2022_2026_DeltaG_by_County.csv`: all 33 counties with G, ΔG, expected loss, residual, offset votes and gap in votes.
- `New_Mexico_33_County_Democratic_Registration_and_Vote_Change.pdf`: the 33-county PDF (Kansas / Nebraska layout).
- `NM_*.png`: the charts on the wiki's Graphs, Floor-and-Ceiling, Reverse-Math and Resources pages (`nm_*.png`: charts from the first build).
- `New_Mexico_Attorney_General_Letter.pdf` / `.docx`: draft letter to the New Mexico Attorney General (not sent).
- `downloads/`: county clerk letters and Inspection of Public Records Act requests for all 33 counties (PDF and Word), by planning district, the county-to-district lookup and the Excel delivery trackers.
- `NM_33_County_Voting_Equipment_VerifiedVoting.csv`: voting equipment by county (Verified Voting, retrieved Nov 24, 2026).
- `resources/social-media/`: the ten-county graphics and the Guarantee Clause graphic. `resources/vote-flip/` and `resources/guarantee-clause/`: graphics from the first build.
- `NM_33_County_Governor_Table.csv`, `New-Mexico-County-Data.pdf`: tables from the first build.
- `scripts/`, `verification/`: the build and verification scripts and their reports.
""")
print('staged', len(list(p for p in R.rglob('*') if p.is_file() and '.git' not in p.parts)), 'repo files;', n, 'wiki pages; Locked sha', sha(WK/LOCKED))
