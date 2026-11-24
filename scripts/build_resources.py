#!/usr/bin/env python3
"""Write wiki/Resources.md: New Mexico vote-flip graphics + Guarantee Clause graphic.
Called at the end of build_wiki.py. Reads wiki/resources/vote-flip/manifest.json (from
build_vote_flip.py).
Numbers in the table are re-checked against both passes by verify_vote_flip.py."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / 'wiki'
VF = W / 'resources' / 'vote-flip'; GC = W / 'resources' / 'guarantee-clause'
CEDAR = 'https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
m = json.loads((VF / 'manifest.json').read_text())
rows, exc = m['rows'], m['excluded']; N = len(rows)
surges = m.get('surges', []); NS = len(surges)
c = lambda n: f'{n:,}'
A = '\\*'


L = []
L.append('# Resources\n')
L.append('> **\\*2026 figures are UNOFFICIAL** (New Mexico SOS \u201cUnofficial Results\u201d, not yet canvassed). 2022 figures are official. Everything on this page is a hypothesis drawn from public numbers, not a finding of fraud, intent or cause.\n')
L.append('Downloadable graphics built from this wiki\u2019s verified New Mexico data. Contents: [Vote-flip county graphics](#vote-flip-county-graphics) \u00b7 [Guarantee Clause graphic](#guarantee-clause-graphic).\n')
L.append('## Vote-flip county graphics\n')
L.append(f'**Only {N} of New Mexico\u2019s 33 counties show a vote flip from 2022 to 2026{A}.** A county counts as a vote flip only when its Democratic governor votes actually **fell** and its Republican governor votes **rose**. '
         f'Statewide, Democratic governor votes **rose {m["statewide_dem_change"]:+,}{A}**, and Democratic votes rose in {m["dem_rose_count"]} of 33 counties. No drop was invented; only real drops are shown as flips.\n')
if surges:
    L.append(f'**Flips vs. surges.** A **flip** is a county where Democratic votes fell while Republican votes rose. A **surge** is the opposite kind of change: Democratic votes rose. To fill out a top ten, the other {NS} cards show the {NS} counties with the largest raw Democratic governor-vote gains from 2022 to 2026{A} (not counting the flip counties or Guadalupe and Harding). Each surge card is marked **SURGE, NOT A FLIP** and uses a teal accent instead of the flip cards\u2019 red and gold.\n')
L.append(f'**Flip magnitude** = Democratic vote drop + Republican vote gain (2022 \u2192 2026{A}), in votes. That is the change in the Republican-minus-Democratic margin. Counties are ranked by it. '
         '(The Texas vote-flip cards used a different test, Democratic primary voters down while Democratic votes rose, so only their visual style is reused here.)\n')
L.append(f'| Rank | County | Dem votes 2022 | Dem votes 2026{A} | Dem drop{A} | Rep votes 2022 | Rep votes 2026{A} | Rep gain{A} | Flip magnitude{A} |')
L.append('|---|---|---|---|---|---|---|---|---|')
for r in rows:
    L.append(f'| {r["rank"]} | {r["county"]} | {c(r["dem22"])} | {c(r["dem26"])} | -{c(r["dem_drop"])} | {c(r["rep22"])} | {c(r["rep26"])} | +{c(r["rep_gain"])} | {c(r["flip_magnitude"])} |')
L.append('')
if surges:
    L.append(f'**Surges (not flips): largest Democratic vote gains**\n')
    L.append(f'| Rank | County | Dem votes 2022 | Dem votes 2026{A} | Dem gain{A} | Rep votes 2022 | Rep votes 2026{A} | Rep change{A} |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in surges:
        L.append(f'| {r["rank"]} | {r["county"]} | {c(r["dem22"])} | {c(r["dem26"])} | +{c(r["dem_gain"])} | {c(r["rep22"])} | {c(r["rep26"])} | {r["rep_change"]:+,} |')
    L.append('')
if exc:
    L.append(f'**Democratic votes fell, but not a flip** (Republican votes fell too, so there is no gain to pair):\n')
    L.append(f'| County | Dem votes 2022 | Dem votes 2026{A} | Rep votes 2022 | Rep votes 2026{A} |')
    L.append('|---|---|---|---|---|')
    for e in exc:
        L.append(f'| {e["county"]} | {c(e["dem22"])} | {c(e["dem26"])} | {c(e["rep22"])} | {c(e["rep26"])} |')
    L.append('')
L.append(f'Every number on every graphic is checked against both independent verification passes (`verification/vote_flip_check.json`) by `scripts/verify_vote_flip.py`.\n')
L.append('### Summary\n')
L.append((f'![Summary: top {N + NS}, {N} vote flips and {NS} surges, New Mexico 2022 vs 2026*]' if surges else f'![Summary: only {N} of 33 New Mexico counties show a vote flip, 2022 vs 2026*]') + f'(resources/vote-flip/00-summary.png)\n')
L.append('[Download the summary graphic (PNG)](resources/vote-flip/00-summary.png)\n')
for r in rows:
    f = next(i['file'] for i in m['images'] if i.get('county') == r['county'])
    L.append(f'### {r["rank"]}. {r["county"]} County\n')
    L.append(f'![{r["county"]} County vote-flip graphic, 1080 by 1350: Democratic governor votes {c(r["dem22"])} \u2192 {c(r["dem26"])}* (down {c(r["dem_drop"])}), Republican governor votes {c(r["rep22"])} \u2192 {c(r["rep26"])}* (up {c(r["rep_gain"])}), flip magnitude {c(r["flip_magnitude"])}* votes.](resources/vote-flip/{f})\n')
    L.append(f'[Download the {r["county"]} County graphic (PNG)](resources/vote-flip/{f})\n')
for r in surges:
    f = next(i['file'] for i in m['images'] if i.get('county') == r['county'])
    rc = r['rep_change']
    L.append(f'### {r["rank"]}. {r["county"]} County (surge, not a flip)\n')
    L.append(f'![{r["county"]} County surge graphic, 1080 by 1350, marked SURGE, NOT A FLIP: Democratic governor votes {c(r["dem22"])} \u2192 {c(r["dem26"])}* (up {c(r["dem_gain"])}), Republican governor votes {c(r["rep22"])} \u2192 {c(r["rep26"])}* ({"up" if rc > 0 else "down"} {c(abs(rc))}).](resources/vote-flip/{f})\n')
    L.append(f'[Download the {r["county"]} County graphic (PNG)](resources/vote-flip/{f})\n')
L.append('Footer on every graphic: *Source: NM Secretary of State. 2026 unofficial. Hypothesis, not a finding.*\n')

L.append('## Guarantee Clause graphic\n')
L.append('![New Mexico Guarantee Clause graphic: Article IV, Section 4 text, \u201cDid you know? It\u2019s NOT your job to prove our elections are free and fair. The Guarantee Clause puts that on the government.\u201d, and the EO 14399 \u201cunavoidable duty\u201d quote over the Sangre de Cristo range and the Roundhouse.](resources/guarantee-clause/nm-guarantee-clause.png)\n')
L.append('Downloads: [portrait 1080\u00d71350 (PNG)](resources/guarantee-clause/nm-guarantee-clause.png) \u00b7 [landscape 1600\u00d7900 (PNG)](resources/guarantee-clause/nm-guarantee-clause-landscape.png)\n')
L.append('### Citation check\n')
L.append('- **Executive Order 14399**, \u201cEnsuring Citizenship Verification and Integrity in Federal Elections\u201d: signed March 31, 2026; published at **91 FR 17125** (April 3, 2026, FR Doc. 2026-06601). [Federal Register](https://www.federalregister.gov/documents/2026/04/03/2026-06601/ensuring-citizenship-verification-and-integrity-in-federal-elections)')
L.append('- Exact quote, Sec. 1: \u201cThe Federal Government has an unavoidable duty under Article II of the Constitution of the United States to enforce Federal law, which includes preventing violations of Federal criminal law and maintaining public confidence in election outcomes.\u201d')
L.append('- The order separately cites \u201cthe Federal Government\u2019s constitutional obligation to guarantee a republican form of Government to every State in the Union, U.S. Const. Art. IV, Sec. 4\u201d (the Guarantee Clause). The words \u201cunavoidable duty\u201d belong to the Article II sentence, not to the Guarantee Clause itself.')
L.append('- Guarantee Clause text: [U.S. Constitution, Art. IV, Sec. 4](https://www.archives.gov/founding-docs/constitution-transcript).\n')
L.append('---\n**Related:** [Home](Home) \u00b7 [Bottom-Up Reverse Math](Reverse-Math) \u00b7 [Locked New Mexico Formula](Locked-New-Mexico-Formula) \u00b7 [Floor and Ceiling Counties](Floor-and-Ceiling) \u00b7 [Graphs](Graphs) \u00b7 [Cedar County Audit](' + CEDAR + ')\n')
(W / 'Resources.md').write_text('\n'.join(L))
print(f'Resources.md built: {N} vote-flip cards')
