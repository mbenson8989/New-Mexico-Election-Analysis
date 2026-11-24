#!/usr/bin/env python3
"""Verify every number on every New Mexico vote-flip graphic against BOTH verification passes.

Independent of build_vote_flip.py: re-reads verification/pass1_values.csv and pass2_values.csv
separately, recomputes the flip set (Dem governor votes fell AND Rep governor votes rose),
ranking (flip magnitude = Dem drop + Rep gain, desc) and all values, then checks:
  - every image listed in manifest.json exists, is the image that was drawn (sha256), and is 1080x1350;
  - every numeric token in every text string drawn on every image equals a value computed from pass1
    AND from pass2 for that image (structural tokens - years 2022/2026, rank, count of flips, 33 - allowed);
  - every required value (2022/2026 Dem & Rep votes, drop, gain, magnitude) appears on each county card;
  - the exact footer is on every image; no county with a Dem rise appears anywhere as a flip.
Writes verification/vote_flip_check.json; exits non-zero on any failure.
"""
import csv, json, hashlib, re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'wiki' / 'resources' / 'vote-flip'
FOOTER = "Source: NM Secretary of State. 2026 unofficial. Hypothesis, not a finding."
man = json.loads((OUT / 'manifest.json').read_text())

def expected(path):
    rows = list(csv.DictReader(open(path)))
    v = {r['county']: {k: int(r[k]) for k in ('dem22', 'dem26', 'rep22', 'rep26')} for r in rows}
    flips = []
    excl = []
    for c, x in v.items():
        if x['dem26'] < x['dem22']:
            if x['rep26'] > x['rep22']:
                flips.append((c, x['dem22'] - x['dem26'], x['rep26'] - x['rep22']))
            else:
                excl.append(c)
    flips.sort(key=lambda t: (-(t[1] + t[2]), -t[1], t[0]))
    flips = flips[:10]
    sw = sum(x['dem26'] for x in v.values()) - sum(x['dem22'] for x in v.values())
    rose = sum(x['dem26'] > x['dem22'] for x in v.values())
    # surges: fill the ten with the largest raw Dem governor-vote gains; flips and Dem-drop non-flips excluded
    skip = {f[0] for f in flips} | set(excl)
    surg = sorted(((c, x['dem26'] - x['dem22'], x['rep26'] - x['rep22']) for c, x in v.items()
                   if c not in skip and x['dem26'] > x['dem22']), key=lambda t: (-t[1], t[0]))[:max(0, 10 - len(flips))]
    return dict(v=v, flips=flips, surges=surg, excl=sorted(excl), sw=sw, rose=rose, n=len(rows))

E = {1: expected(ROOT / 'verification' / 'pass1_values.csv'), 2: expected(ROOT / 'verification' / 'pass2_values.csv')}
fails = []
def need(cond, msg):
    if not cond: fails.append(msg)

for p in (1, 2):
    need(E[p]['n'] == 33, f'pass{p}: expected 33 counties, got {E[p]["n"]}')
    need([f[0] for f in E[p]['flips']] == [r['county'] for r in man['rows']], f'pass{p}: flip set/order differs from graphics')
    need([t[0] for t in E[p]['surges']] == [r['county'] for r in man.get('surges', [])], f'pass{p}: surge set/order differs from graphics')
    need(all(E[p]['v'][t[0]]['dem26'] > E[p]['v'][t[0]]['dem22'] for t in E[p]['surges']), f'pass{p}: a surge county did not gain Dem votes')
    need(not ({t[0] for t in E[p]['surges']} & ({f[0] for f in E[p]['flips']} | set(E[p]['excl']))), f'pass{p}: surge overlaps flip/excluded')
    need(E[p]['excl'] == sorted(e['county'] for e in man['excluded']), f'pass{p}: excluded set differs')

NUM = re.compile(r'(?<![\w#])[-+]?\d[\d,]*')
def tok(s): return [int(t.replace(',', '')) for t in NUM.findall(s.replace('#', ' # '))]
STRUCT = {2022, 2026, 33}
checked = matched = 0
per_image = []
for im in man['images']:
    f = OUT / im['file']
    need(f.exists(), f'{im["file"]} missing')
    if not f.exists(): continue
    need(hashlib.sha256(f.read_bytes()).hexdigest() == im['sha256'], f'{im["file"]}: image differs from manifest (stale)')
    need(Image.open(f).size == (1080, 1350), f'{im["file"]}: size {Image.open(f).size}')
    need(FOOTER in im['texts'], f'{im["file"]}: exact footer missing')
    n_img = 0
    for p in (1, 2):
        e = E[p]; v = e['v']
        allowed = set(STRUCT) | {len(e['flips']), len(e['flips']) + len(e['surges']), len(e['surges'])}
        if im['kind'] == 'county':
            c = im['county']; x = v[c]; rank = [f[0] for f in e['flips']].index(c) + 1
            drop, gain = x['dem22'] - x['dem26'], x['rep26'] - x['rep22']
            req = {x['dem22'], x['dem26'], x['rep22'], x['rep26'], drop, gain, drop + gain}
            allowed |= req | {rank}
            got = {abs(t) for s in im['texts'] for t in tok(s)}
            for r_ in req: need(r_ in got, f'pass{p} {im["file"]}: required value {r_} not on graphic')
            need(im['rank'] == rank, f'pass{p} {im["file"]}: rank {im["rank"]} != {rank}')
        elif im['kind'] == 'surge':
            c = im['county']; x = v[c]; rank = len(e['flips']) + 1 + [t[0] for t in e['surges']].index(c)
            gain, rc = x['dem26'] - x['dem22'], x['rep26'] - x['rep22']
            req = {x['dem22'], x['dem26'], x['rep22'], x['rep26'], gain, abs(rc)} - {0}
            allowed |= req | {rank}
            got = {abs(t) for s in im['texts'] for t in tok(s)}
            for r_ in req: need(r_ in got, f'pass{p} {im["file"]}: required value {r_} not on graphic')
            need(im['rank'] == rank, f'pass{p} {im["file"]}: rank {im["rank"]} != {rank}')
            need('SURGE, NOT A FLIP' in im['texts'], f'{im["file"]}: SURGE label missing')
        else:
            allowed |= {e['sw'], e['rose']} | set(range(1, len(e['flips']) + len(e['surges']) + 1))
            for c, g, rc in e['surges']:
                allowed |= {g, abs(rc)}
                got = {abs(t) for s in im['texts'] for t in tok(s)}
                need(g in got and (rc == 0 or abs(rc) in got), f'pass{p} summary: surge {c} values missing')
            for c, d, g in e['flips']:
                allowed |= {d, g, d + g}
            for c in e['excl']:
                allowed |= {v[c][k] for k in ('dem22', 'dem26', 'rep22', 'rep26')}
        for s in im['texts']:
            if s == FOOTER: continue
            for t in tok(s):
                checked += 1; n_img += (p == 1)
                if abs(t) in allowed: matched += 1
                else: fails.append(f'pass{p} {im["file"]}: number {t} in "{s}" not supported by pass{p}')
    per_image.append(dict(file=im['file'], numbers_on_image=n_img))

# Resources.md tables vs both passes
res_md = (ROOT / 'wiki' / 'Resources.md')
md_checked = 0
if res_md.exists():
    md = res_md.read_text()
    # Kansas-parity Resources page: the old vote-flip section sits between vf markers; check only that section
    if '<!-- vf-begin -->' in md:
        md = md.split('<!-- vf-begin -->', 1)[1].split('<!-- vf-end -->', 1)[0]
    allr = [[x.strip() for x in ln.strip('|').split('|')] for ln in md.splitlines() if re.match(r'^\| \d+ \| ', ln)]
    trows = [r for r in allr if len(r) == 9]; srows = [r for r in allr if len(r) == 8]
    xrows = [[x.strip() for x in ln.strip('|').split('|')] for ln in md.splitlines()
             if ln.startswith('| ') and len(ln.strip('|').split('|')) == 5 and not ln.startswith('| County')]
    for p in (1, 2):
        e = E[p]
        need(len(trows) == len(e['flips']), f'pass{p}: Resources.md has {len(trows)} flip rows, expected {len(e["flips"])}')
        for i, (cty, d, g) in enumerate(e['flips']):
            if i >= len(trows): break
            x = e['v'][cty]
            want = [str(i + 1), cty, f"{x['dem22']:,}", f"{x['dem26']:,}", f"-{d:,}", f"{x['rep22']:,}", f"{x['rep26']:,}", f"+{g:,}", f"{d + g:,}"]
            for a, b in zip(trows[i], want):
                md_checked += 1
                need(a == b, f'pass{p} Resources.md row {i + 1}: "{a}" != "{b}"')
        need(len(srows) == len(e['surges']), f'pass{p}: Resources.md has {len(srows)} surge rows, expected {len(e["surges"])}')
        for i, (cty, g, rc) in enumerate(e['surges']):
            if i >= len(srows): break
            x = e['v'][cty]
            want = [str(len(e['flips']) + i + 1), cty, f"{x['dem22']:,}", f"{x['dem26']:,}", f"+{g:,}", f"{x['rep22']:,}", f"{x['rep26']:,}", f"{rc:+,}"]
            for a, b in zip(srows[i], want):
                md_checked += 1
                need(a == b, f'pass{p} Resources.md surge row {i + 1}: "{a}" != "{b}"')
        need(sorted(r[0] for r in xrows) == e['excl'], f'pass{p}: Resources.md excluded list differs')
        for r in xrows:
            if r[0] in e['v']:
                x = e['v'][r[0]]
                for a, b in zip(r[1:], [f"{x[k]:,}" for k in ('dem22', 'dem26', 'rep22', 'rep26')]):
                    md_checked += 1; need(a == b, f'pass{p} Resources.md excluded {r[0]}: "{a}" != "{b}"')
else:
    fails.append('wiki/Resources.md missing')

for c, *_ in E[1]['flips']:
    need(E[1]['v'][c]['dem26'] < E[1]['v'][c]['dem22'], f'{c}: shown as flip but Dem votes did not fall')

res = dict(images=len(man['images']), county_cards=sum(i['kind'] == 'county' for i in man['images']), surge_cards=sum(i['kind'] == 'surge' for i in man['images']),
           surges=[dict(rank=len(E[1]['flips']) + i + 1, county=c, dem_gain=g, rep_change=rc) for i, (c, g, rc) in enumerate(E[1]['surges'])],
           flip_counties=len(E[1]['flips']), dem_drop_counties=len(E[1]['flips']) + len(E[1]['excl']),
           excluded_dem_drop_not_flip=E[1]['excl'], dem_rose_counties=E[1]['rose'], statewide_dem_change=E[1]['sw'],
           numbers_checked_pass1=checked // 2, numbers_checked_pass2=checked // 2, total_checks=checked, matched=matched, resources_md_cells_checked=md_checked,
           mismatches=fails, per_image=per_image,
           ranking=[dict(rank=i + 1, county=c, dem_drop=d, rep_gain=g, flip_magnitude=d + g) for i, (c, d, g) in enumerate(E[1]['flips'])])
(ROOT / 'verification' / 'vote_flip_check.json').write_text(json.dumps(res, indent=1))
print(f'vote-flip check: {res["images"]} images, {checked} number checks ({checked//2} per pass), matched {matched}; Resources.md cells {md_checked}; failures {len(fails)}')
if fails or checked == 0 or matched != checked or md_checked == 0:
    print('\n'.join(fails)); sys.exit('VOTE-FLIP MISMATCH')
