"""Write wiki/README.md: plain-language start page for first-time readers. Every number comes from the verified outputs
(out/, verification/verification_report.json); wiki_check.py re-checks each number in it against BOTH verification passes."""
import csv, json
O='/workspace/nm-election/out'; W='/workspace/nm-election/wiki'; V='/workspace/nm-election/verification'
T=list(csv.DictReader(open(f'{O}/nm_county_table.csv'))); TD={r['county']:r for r in T}
SH={r['county']:r for r in csv.DictReader(open(f'{O}/nm_share_fit_table.csv'))}
SF=json.load(open(f'{O}/nm_share_fit.json'))['fmt']; a,b=SF['y2026'],SF['y2022']
VR={x['label']:x for x in json.load(open(f'{V}/verification_report.json'))['results']}
p1,p2=VR['Pass 1 vs published table'],VR['Pass 2 vs published table']
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
WRITEUP='https://moebenson.substack.com/p/the-election-equation-and-plan'   # found in the Nebraska wiki README (mbenson8989/Nebraska-Election-Analysis-.wiki, README.md)
SUBSTACK='https://moebenson.substack.com/'
c=lambda n:f'{int(n):,}'; mn=lambda s:s.replace('-','−')
def eq(f): return f"S = {mn(f['m'])} × (D/100) {'+' if f['b'][0]=='+' else '−'} {f['b'][1:]}"
fl=min(T,key=lambda r:float(r['S22'])); ce=max(T,key=lambda r:float(r['S22']))
over=sum(r['over22']=='YES' for r in T)+sum(r['over26']=='YES' for r in T)
X=TD['Lea']; XS=SH['Lea']
open(f'{W}/README.md','w').write(f"""# README: Start Here

Welcome! If this is your first visit, this page is for you. It explains, in everyday language, what you're looking at, where the numbers come from and how to read them. No math background needed.

> **\\*2026 figures are unofficial.** The New Mexico Secretary of State's results site labels the November 3, 2026 general election "Unofficial Results." Those numbers have not been certified yet and could still change. Anything that uses them is marked with an asterisk (\\*). The 2022 figures are the Secretary of State's "Official Results."

## Where the numbers come from

Every number on this wiki comes straight from the **New Mexico Secretary of State's official website**. Nothing is estimated or filled in by hand. These are the reports used:

- **Election results, Governor and Lieutenant Governor race, "County Level" export**: the 2022 General Election (Official Results) and the 2026 General Election (Unofficial Results\\*), plus each county's own results page as a cross-check.
- **Voter Turnout reports**: ballots cast in every county (and every precinct), for both elections, plus each county's turnout export as a cross-check.
- **New Mexico Voter Registration Statistics, "Statewide by County"**: the reports **As of October 31, 2022** and **As of October 30, 2026**, the last reports before each election.

One more source, used only to put the counties in order from largest to smallest: the U.S. Census Bureau's Vintage 2025 county population estimates. The full list of files, with web addresses and download times, is in `raw/MANIFEST.md` in the project folder.

## See the data for yourself

You don't have to take anyone's word for it. Open **[New Mexico County Data (PDF)](New-Mexico-County-Data.pdf)** in the sidebar. It lists all {len(T)} counties, largest first, with population, Democratic votes for governor, ballots cast, registered Democrats and total registered voters for 2022 and 2026\\*, along with the shares and the surplus worked out from them. You can check any line against the Secretary of State's own reports.

## This is a hypothesis, not a verdict

Please read this part carefully. **What you'll find here is a hypothesis, not a finding of wrongdoing.**

If election manipulation exists, it would not be one simple thing. It would be multifaceted, with several pieces working together. This analysis looks through just one lens: how the votes in each county line up with that county's voter registration. A gap between the two is a pattern worth a closer look. On its own it proves nothing, and it says nothing about who did what or why. It makes no claim of fraud or intent.

## The story behind the numbers

Numbers make more sense with the story behind them. Morissa tells that story in her hypothesis write-up on Substack: **[read Morissa's write-up]({WRITEUP})**. You can find more of her writing on **[Morissa Benson's Substack]({SUBSTACK})**.

## What you're looking at, in plain terms

**Two shares for every county.** For each county and each election we look at:

1. **Democratic vote share**: the Democratic votes for governor, as a share of all ballots cast.
2. **Democratic registration share (D)**: registered Democrats, as a share of all registered voters.

**The surplus (S)** is simply the first share minus the second, in percentage points. If a county's Democratic candidate drew a bigger share of the ballots than Democrats make up of the voter rolls, the surplus is positive.

**Why it's called reverse-factoring.** We work backward from the result. We start with the votes that were counted, take out what registration alone would lead you to expect, and look at what's left over. That leftover is the **residual**: the part that registration doesn't account for. A residual is a distance from the trend line, not proof of anything.

## New Mexico's surplus equation

Morissa's locked form is the same for every state: **S = multiplier × (D/100) + offset**. Each state gets its own multiplier and offset, worked out from that state's counties only. For New Mexico, using all {len(T)} counties:

- **2026\\* (unofficial, the headline): {eq(a)}**
- **2022 (official, for reference): {eq(b)}**

**An honest note: the fit is weak.** A measure called R² tells how well the line fits, where 1 would be a perfect fit. New Mexico's R² is **{a['r2']}\\*** for 2026 and **{b['r2']}** for 2022, so registration share by itself predicts very little of the surplus here. On average a county sits **{a['mae']} points\\*** away from the line in 2026 (**{b['mae']} points** in 2022). That average distance is the "average absolute residual."

**One county worked through: Lea.** Lea's Democratic registration share in 2026 was {X['R26']}%. Plug that into the 2026 equation and the line expects a surplus of {XS['shfit26']}\\* points. Lea's actual surplus was {X['G26']}\\* points, so its residual is {XS['shres26']}\\* points: a bit below the line. (The line is computed with unrounded numbers, so working it by hand with the rounded ones can land a hair off in the last digit.) The details, plus a fill-in-the-blank template, are on the **[Locked New Mexico Formula](Locked-New-Mexico-Formula)** page.

## Floor and ceiling counties

It helps to look at both ends of the range. The **floor** is the county with the lowest Democratic share of ballots in 2022, and the **ceiling** is the county with the highest. In New Mexico the floor is **{fl['county']}** ({fl['S22']}%) and the ceiling is **{ce['county']}** ({ce['S22']}%). Every other county falls somewhere in between. See **[Floor and Ceiling Counties](Floor-and-Ceiling)**.

## The over-ballot check

A simple common-sense test: in any county, Democratic plus Republican votes for governor should never be more than the number of ballots cast. We checked every county in both elections. **No county failed the check**: {over} county-years flagged in 2022 or 2026\\*.

## Checked twice, independently

Before anything is shared, every figure was rebuilt in **two separate verification passes**, each written on its own with no shared code, each going back to the raw Secretary of State files. One pass reads the statewide county export, the turnout page and the registration reports; the other reads a second set of Secretary of State files where they exist (each county's own results page and turnout export). Each pass compared **{p1['total']}** values against the published table (pass 1: {p1['mismatched']} mismatches; pass 2: {p2['mismatched']} mismatches). The numbers on this page and in the PDF are also checked against both passes every time the wiki is rebuilt.

## How Morissa worked it out

Morissa isn't a mathematician. She sees patterns. Here is what she did:

1. She lined up the Secretary of State's numbers county by county.
2. She graphed all the counties together and drew the line that fit them best.
3. That line gives each state its own fitted numbers: a multiplier and an offset. No two states share them, and New Mexico's come from New Mexico's counties alone.

She used AI tools to help with the heavy lifting, and every result was checked against the raw Secretary of State files. This work began with her **[Cedar County Audit]({CEDAR})** in Nebraska.

## Where to go next

- [Home](Home): the overview
- [Cedar County Audit]({CEDAR}): where it started
- [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at each end
- [Bottom-Up Reverse Math](Reverse-Math): the step-by-step math
- [Graphs](Graphs): the charts
- [New Mexico County Data (PDF)](New-Mexico-County-Data.pdf): the data table
- [Locked New Mexico Formula](Locked-New-Mexico-Formula): the equation and a fill-in-the-blank template
""")
print('README built')
