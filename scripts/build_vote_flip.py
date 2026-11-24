#!/usr/bin/env python3
"""New Mexico vote-flip county graphics (2022 official vs 2026* unofficial governor race).

FLIP DEFINITION (New Mexico, own definition; see note below):
  A county is a vote-flip county when, from 2022 to 2026*,
    Democratic governor votes FELL  (dem26 < dem22)  AND
    Republican governor votes ROSE  (rep26 > rep22).
  dem_drop  = dem22 - dem26        (> 0)
  rep_gain  = rep26 - rep22        (> 0)
  flip magnitude = dem_drop + rep_gain
                 = change in the Republican-minus-Democratic vote margin, in votes.
  Ranked by flip magnitude (desc), ties broken by dem_drop.

Why not the Texas definition: the Texas bot's vote-flip work
(/workspace/texas-wiki/repo/graphics/vote-flip/build_vote_flip_graphics.py) defines a
"flip" as Democratic primary voters FALLING while Democratic governor votes ROSE, ranked by
the surplus change dS (= dG). That is the opposite direction (a Democratic gain, not a drop)
and cannot be used for "Democratic drop -> Republican gain" cards. Only Texas's visual style
(navy / red / white / gold, Barlow Condensed Black numbers, 1080x1350) is reused here.

NEVER invents a drop: only counties whose verified Dem governor votes actually fell are eligible;
a county whose Dem votes fell but whose Rep votes ALSO fell has no gain to pair, so it is not a flip
(listed as excluded). If fewer than ten counties qualify, only that many cards are made.

Inputs: verification/pass1_values.csv and verification/pass2_values.csv (independent passes,
all 33 counties). Every integer used must be identical in both or the script stops.
Writes wiki/resources/vote-flip/NN-<county>.png, 00-summary.png, vote_flip_table.csv and
manifest.json (every text string drawn on every image, for verify_vote_flip.py).
Local only. Does not push anything.
"""
import csv, json, hashlib, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
VER = ROOT / 'verification'
OUT = ROOT / 'wiki' / 'resources' / 'vote-flip'
OUT.mkdir(parents=True, exist_ok=True)
FOOTER = "Source: NM Secretary of State. 2026 unofficial. Hypothesis, not a finding."
INT = ['dem22', 'rep22', 'ballots22', 'dem26', 'rep26', 'ballots26']

def load(p):
    return {r['county']: {k: int(r[k]) for k in INT} for r in csv.DictReader(open(p))}

P1, P2 = load(VER / 'pass1_values.csv'), load(VER / 'pass2_values.csv')
assert len(P1) == 33 and set(P1) == set(P2), 'need all 33 counties in both passes'
for c in P1:
    if P1[c] != P2[c]:
        raise SystemExit(f'PASS MISMATCH {c}: {P1[c]} vs {P2[c]}')
D = P1

rows, excluded = [], []
for c, v in D.items():
    if v['dem26'] < v['dem22']:
        drop, gain = v['dem22'] - v['dem26'], v['rep26'] - v['rep22']
        rec = dict(county=c, **v, dem_drop=drop, rep_change=gain)
        if gain > 0:
            rows.append(dict(rec, rep_gain=gain, flip_magnitude=drop + gain))
        else:
            excluded.append(dict(rec, reason='Dem votes fell but Rep votes also fell (no gain to pair) - not a flip'))
rows.sort(key=lambda r: (-r['flip_magnitude'], -r['dem_drop'], r['county']))
rows = rows[:10]
for i, r in enumerate(rows, 1):
    r['rank'] = i
excluded.sort(key=lambda r: -r['dem_drop'])
# SURGE fill-ins (Morissa approved, Nov 23 2026): the 3 real flips are kept; the rest of the ten are the
# counties with the largest RAW Democratic governor-vote gain (dem26 - dem22), 2022 -> 2026*. Flip counties and
# the Dem-drop non-flips (Guadalupe, Harding) are excluded. Labelled "SURGE, NOT A FLIP" everywhere.
# (Texas ranked its own cards by the surplus change dS; it had no fill-ins, so the raw-gain default is used here.)
_skip = {r['county'] for r in rows} | {e['county'] for e in excluded}
surges = [dict(county=c, **v, dem_gain=v['dem26'] - v['dem22'], rep_change=v['rep26'] - v['rep22'])
          for c, v in D.items() if c not in _skip and v['dem26'] > v['dem22']]
surges.sort(key=lambda r: (-r['dem_gain'], r['county']))
surges = surges[:max(0, 10 - len(rows))]
for i, r in enumerate(surges, len(rows) + 1):
    r['rank'] = i
dem_rose = sorted(c for c, v in D.items() if v['dem26'] > v['dem22'])
dem_same = sorted(c for c, v in D.items() if v['dem26'] == v['dem22'])
SW = {k: sum(v[k] for v in D.values()) for k in INT}
sw_dem_change = SW['dem26'] - SW['dem22']
N = len(rows)
NT = N + len(surges)

# ---------- style (from Texas / Nebraska cards) ----------
BG = (8, 14, 28); RED = (200, 16, 46); WHITE = (255, 255, 255); GOLD = (212, 175, 90)
GREY = (160, 170, 190); LINE = (40, 52, 78); BLUE = (70, 130, 220)
TEAL = (0, 196, 170)   # surge accent (flip cards use red/gold)
G = '/usr/share/fonts/truetype/sand-box/google/'
BC = G + 'Barlow Condensed/BarlowCondensed-Black.ttf'
BCB = G + 'Barlow Condensed/BarlowCondensed-Bold.ttf'
SS = G + 'Source Sans 3/SourceSans3-VariableFont_wght.ttf'
W, H = 1080, 1350
def bc(s): return ImageFont.truetype(BC, s)
def bcb(s): return ImageFont.truetype(BCB, s)
def ss(s, w=600):
    f = ImageFont.truetype(SS, s); f.set_variation_by_axes([w]); return f
c = lambda n: f'{n:,}'

class Card:
    def __init__(self, w=W, h=H):
        self.im = Image.new('RGB', (w, h), BG); self.d = ImageDraw.Draw(self.im); self.texts = []
    def t(self, xy, s, font, fill, anchor='la'):
        self.d.text(xy, s, font=font, fill=fill, anchor=anchor); self.texts.append(s)
        return self.d.textbbox(xy, s, font=font, anchor=anchor)
    def fit(self, s, path, start, maxw, minsize=40):
        size = start
        while size > minsize and self.d.textlength(s, font=ImageFont.truetype(path, size)) > maxw:
            size -= 2
        return ImageFont.truetype(path, size)

def footer(k, y=None):
    y = y or H - 62
    k.d.line([(70, y - 22), (W - 70, y - 22)], fill=LINE, width=2)
    k.t((70, y), FOOTER, ss(29, 500), GREY)

def spaced(name):
    return '   '.join(' '.join(p) for p in (name.upper() + ' COUNTY').split())

def county_card(r):
    k = Card(); M = 70
    k.t((M, 58), f'NEW MEXICO VOTE FLIP  #{r["rank"]} OF {NT}', bcb(36), GOLD)
    k.t((M, 100), spaced(r['county']) if len(r['county']) < 12 else (r['county'].upper() + ' COUNTY'), bcb(40), WHITE)
    f = k.fit(r['county'].upper(), BC, 150, W - 2 * M)
    k.t((M - 4, 150), r['county'].upper(), f, WHITE)
    k.d.rectangle([M, 330, M + 150, 336], fill=GOLD)

    def block(y, label, big, col, y22, y26):
        k.t((M, y), label, bcb(44), WHITE)
        fb = bc(150)
        bb = k.t((M - 4, y + 44), big, fb, col)
        x = bb[2] + 40
        k.t((x, y + 82), f'2022: {c(y22)}', ss(46, 700), GREY)
        k.t((x, y + 140), f'2026*: {c(y26)}', ss(46, 700), WHITE)

    block(360, 'DEMOCRATIC GOVERNOR VOTES', f'DOWN {c(r["dem_drop"])}*', RED, r['dem22'], r['dem26'])
    block(590, 'REPUBLICAN GOVERNOR VOTES', f'UP {c(r["rep_gain"])}*', BLUE, r['rep22'], r['rep26'])

    # before / after bars
    y0 = 830; mx = max(r['dem22'], r['dem26'], r['rep22'], r['rep26']); BW = 560; x0 = M + 150
    k.t((M, y0), 'BEFORE / AFTER', bcb(34), GOLD)
    yy = y0 + 50
    for lab, dv, rv in (('2022', r['dem22'], r['rep22']), ('2026*', r['dem26'], r['rep26'])):
        k.t((M, yy + 8), lab, bcb(44), WHITE)
        for j, (val, col, tag) in enumerate(((dv, RED, 'D'), (rv, BLUE, 'R'))):
            by = yy + j * 34
            k.d.rectangle([x0, by, x0 + int(BW * val / mx), by + 26], fill=col)
            k.t((x0 + int(BW * val / mx) + 12, by - 4), f'{tag} {c(val)}', ss(28, 700), WHITE)
        yy += 92

    k.t((M, 1080), 'FLIP MAGNITUDE', bcb(40), GOLD)
    bb = k.t((M - 4, 1118), f'{c(r["flip_magnitude"])} VOTES*', bc(96), WHITE)
    k.t((bb[2] + 30, 1140), f'= {c(r["dem_drop"])} Dem drop', ss(34, 600), GREY)
    k.t((bb[2] + 30, 1182), f'+ {c(r["rep_gain"])} Rep gain', ss(34, 600), GREY)
    footer(k)
    return k

def surge_card(r):
    k = Card(); M = 70
    k.d.rectangle([0, 0, W, 14], fill=TEAL)
    k.t((M, 58), f'NEW MEXICO VOTE SURGE  #{r["rank"]} OF {NT}', bcb(36), TEAL)
    k.t((M, 100), spaced(r['county']) if len(r['county']) < 12 else (r['county'].upper() + ' COUNTY'), bcb(40), WHITE)
    f = k.fit(r['county'].upper(), BC, 150, W - 2 * M)
    k.t((M - 4, 150), r['county'].upper(), f, WHITE)
    lab = 'SURGE, NOT A FLIP'
    lw = k.d.textlength(lab, font=bcb(40))
    k.d.rounded_rectangle([M, 318, M + lw + 40, 372], radius=10, outline=TEAL, width=4)
    k.t((M + 20, 322), lab, bcb(40), TEAL)

    def block(y, label, big, col, y22, y26):
        k.t((M, y), label, bcb(44), WHITE)
        side = max(k.d.textlength(f'2022: {c(y22)}', font=ss(46, 700)), k.d.textlength(f'2026*: {c(y26)}', font=ss(46, 700)))
        fb = k.fit(big, BC, 150, W - 2 * M - 40 - side, 70)
        bb = k.t((M - 4, y + 44 + (150 - fb.size) // 2), big, fb, col)
        x = bb[2] + 40
        k.t((x, y + 82), f'2022: {c(y22)}', ss(46, 700), GREY)
        k.t((x, y + 140), f'2026*: {c(y26)}', ss(46, 700), WHITE)
    rc = r['rep_change']
    block(400, 'DEMOCRATIC GOVERNOR VOTES', f'UP {c(r["dem_gain"])}*', TEAL, r['dem22'], r['dem26'])
    block(630, 'REPUBLICAN GOVERNOR VOTES', ('UP ' if rc > 0 else 'DOWN ' if rc < 0 else 'NO CHANGE ') + (f'{c(abs(rc))}*' if rc else '*'), BLUE, r['rep22'], r['rep26'])
    y0 = 870; mx = max(r['dem22'], r['dem26'], r['rep22'], r['rep26']); BW = 560; x0 = M + 150
    k.t((M, y0), 'BEFORE / AFTER', bcb(34), TEAL)
    yy = y0 + 50
    for lab_, dv, rv in (('2022', r['dem22'], r['rep22']), ('2026*', r['dem26'], r['rep26'])):
        k.t((M, yy + 8), lab_, bcb(44), WHITE)
        for j_, (val, col, tag) in enumerate(((dv, TEAL, 'D'), (rv, BLUE, 'R'))):
            by = yy + j_ * 34
            k.d.rectangle([x0, by, x0 + int(BW * val / mx), by + 26], fill=col)
            k.t((x0 + int(BW * val / mx) + 12, by - 4), f'{tag} {c(val)}', ss(28, 700), WHITE)
        yy += 92
    k.t((M, 1110), 'A surge: Democratic votes ROSE. Not a flip.', ss(38, 700), TEAL)
    k.t((M, 1160), 'Flip = Dem votes fell AND Rep votes rose.', ss(34, 600), GREY)
    footer(k)
    return k

def summary():
    k = Card(); M = 70
    k.t((M, 58), 'NEW MEXICO GOVERNOR  2022 vs 2026*', bcb(38), GOLD)
    title = f'TOP {NT}: {N} FLIPS + {len(surges)} SURGES' if surges else f'ONLY {N} OF 33 COUNTIES SHOW A FLIP'
    f = k.fit(title, BC, 110, W - 2 * M)
    k.t((M - 2, 100), title, f, WHITE)
    k.t((M, 232), 'FLIP: Democratic votes fell AND Republican votes rose.', ss(34, 700), RED)
    k.t((M, 274), 'SURGE: largest Democratic vote gains. Not a flip.', ss(34, 700), TEAL)
    y = 340
    for s_, x in [('#', M), ('COUNTY', M + 60), ('DEM', M + 410), ('REP', M + 610), ('TYPE', M + 810)]:
        k.t((x, y), s_, bcb(36), GREY)
    y += 50; k.d.line([(M, y), (W - M, y)], fill=LINE, width=2); y += 14
    fs, rh = 52, 64
    for r in rows:
        k.t((M, y), str(r['rank']), bc(fs), GOLD); k.t((M + 60, y), r['county'].upper(), bc(fs), WHITE)
        k.t((M + 410, y), f'-{c(r["dem_drop"])}', bc(fs), RED); k.t((M + 610, y), f'+{c(r["rep_gain"])}', bc(fs), BLUE)
        k.t((M + 810, y), 'FLIP', bc(fs), RED); y += rh
    if surges:
        k.d.line([(M, y + 2), (W - M, y + 2)], fill=LINE, width=2); y += 12
    for r in surges:
        rc = r['rep_change']
        k.t((M, y), str(r['rank']), bc(fs), TEAL); k.t((M + 60, y), r['county'].upper(), bc(fs), WHITE)
        k.t((M + 410, y), f'+{c(r["dem_gain"])}', bc(fs), TEAL); k.t((M + 610, y), f'{rc:+,}' if rc else '0', bc(fs), BLUE)
        k.t((M + 810, y), 'SURGE', bc(fs), TEAL); y += rh
    y += 10; k.d.line([(M, y), (W - M, y)], fill=LINE, width=2); y += 22
    k.t((M, y), 'Votes, 2022 to 2026*. Flips ranked by Dem drop + Rep gain;', ss(30, 600), GREY); y += 40
    k.t((M, y), 'surges ranked by raw Democratic vote gain.', ss(30, 600), GREY); y += 50
    k.t((M, y), f'Statewide, Democratic votes ROSE {sw_dem_change:+,}*.', ss(32, 700), GOLD)
    k.t((M, H - 120), '*2026 figures are unofficial.', ss(30, 600), GREY)
    footer(k)
    return k

def slug(s): return re.sub(r'[^a-z]+', '-', s.lower()).strip('-')

manifest = dict(footer=FOOTER, flip_definition='Dem governor votes fell (dem26<dem22) AND Rep governor votes rose (rep26>rep22); magnitude = dem_drop + rep_gain',
                n_flip_counties=N, n_surge_counties=len(surges), surge_definition='Not a flip. Remaining ten slots: counties with the largest raw Democratic governor-vote gain dem26-dem22 (2022 -> 2026*), excluding flip counties and Dem-drop non-flips', n_dem_drop_counties=N + len(excluded), excluded=excluded, dem_rose_count=len(dem_rose),
                dem_same=dem_same, statewide_dem_change=sw_dem_change, images=[])
for old in OUT.glob('[0-9][0-9]-*.png'):
    old.unlink()   # only our own generated cards (NN-*.png) are replaced
for r in rows:
    k = county_card(r); p = OUT / f'{r["rank"]:02d}-{slug(r["county"])}.png'; k.im.save(p)
    manifest['images'].append(dict(file=p.name, kind='county', county=r['county'], rank=r['rank'], texts=k.texts,
                                   sha256=hashlib.sha256(p.read_bytes()).hexdigest(), size=list(k.im.size)))
for r in surges:
    k = surge_card(r); p = OUT / f'{r["rank"]:02d}-{slug(r["county"])}.png'; k.im.save(p)
    manifest['images'].append(dict(file=p.name, kind='surge', county=r['county'], rank=r['rank'], texts=k.texts,
                                   sha256=hashlib.sha256(p.read_bytes()).hexdigest(), size=list(k.im.size)))
k = summary(); p = OUT / '00-summary.png'; k.im.save(p)
manifest['images'].append(dict(file=p.name, kind='summary', texts=k.texts, sha256=hashlib.sha256(p.read_bytes()).hexdigest(), size=list(k.im.size)))
manifest['rows'] = rows
manifest['surges'] = surges
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
with open(OUT / 'vote_flip_table.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, ['rank', 'type', 'county', 'dem22', 'dem26', 'dem_change', 'rep22', 'rep26', 'rep_change', 'flip_magnitude'], extrasaction='ignore')
    w.writeheader()
    for r in rows: w.writerow(dict(r, type='flip', dem_change=-r['dem_drop'], rep_change=r['rep_gain']))
    for r in surges: w.writerow(dict(r, type='surge', dem_change=r['dem_gain'], flip_magnitude=''))
print(f'vote-flip: {N} flip counties, {len(excluded)} Dem-drop non-flips, {len(dem_rose)} Dem-rose; statewide Dem {sw_dem_change:+,}')
for r in rows:
    print(f'  {r["rank"]}. {r["county"]}: Dem {r["dem22"]:,}->{r["dem26"]:,} (-{r["dem_drop"]:,}), Rep {r["rep22"]:,}->{r["rep26"]:,} (+{r["rep_gain"]:,}), flip {r["flip_magnitude"]:,}')
for r in surges:
    print(f'  {r["rank"]}. {r["county"]} SURGE: Dem {r["dem22"]:,}->{r["dem26"]:,} (+{r["dem_gain"]:,}), Rep {r["rep22"]:,}->{r["rep26"]:,} ({r["rep_change"]:+,})')
for e in excluded:
    print(f'  excluded {e["county"]}: Dem -{e["dem_drop"]:,}, Rep {e["rep_change"]:+,}')
