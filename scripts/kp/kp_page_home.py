from kp_pages_common import *
# ---------------- Sidebar (Kansas item for item)
side=f"""**New Mexico ΔG wiki, reading order**

1. [Home]({WIKI[:-1]})
   - [README: start here]({WIKI}README)
2. [Cedar County Audit (Nebraska)]({CEDAR})
3. [Floor and Ceiling Counties]({WIKI}Floor-and-Ceiling)
4. [Bottom-Up Reverse Math]({WIKI}Reverse-Math)
   - [Expected-loss residual layer]({WIKI}Reverse-Math{EL_ANCHOR})
5. [Locked New Mexico Formula]({WIKI}Locked-New-Mexico-Formula)
6. [Graphs]({WIKI}Graphs)
7. [New Mexico County PDF Information]({WIKI}New-Mexico-County-PDF-Information)
8. [Resources]({WIKI}Resources)

\\*2026 figures are unofficial until the New Mexico State Canvassing Board approves the canvass (third Tuesday after the election, Nov 24, 2026; NMSA 1978, § 1-13-15).
"""
R=Reg('sidebar'); write(R,'_Sidebar.md',side)
# ---------------- Home
R=Reg('home'); v=R.v
cap=R.raw('ceiling5'); flo=R.raw('floor.counties'); R.use('ceiling5'); v('floor.counties','list')
capt=', '.join(f"{c} {cty(R,c,'dG','pt2')}{S}" for c in cap)
flot=', '.join(R.raw('floor.counties'))
slope=v('size.slope','pt2')
body=f"""# New Mexico 2022 vs 2026 Governor Race: ΔG Method

{BANNER}

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit]({CEDAR}) on the [Nebraska Election Analysis wiki]({NEWIKI}), the origin of the ΔG method. This wiki applies the same county-by-county arithmetic to all 33 New Mexico counties, using New Mexico SOS numbers only. New Mexico has party registration, so D is real Democratic registration, and New Mexico publishes ballots cast by county for both years, so the denominator is total ballots cast (the Nebraska basis; Kansas had to use governor votes). Rebuilt in the Kansas wiki's structure Nov 24, 2026.

**New here? Start with the [README](README).** &nbsp;|&nbsp; **[Resources](Resources): ten shareable county graphics, the Guarantee Clause graphic, the Attorney General letter and the 33 county clerk letters.**

## Contents

Start with the Cedar County audit in Nebraska. That is where the method began. The New Mexico pages then build up from one county (Luna, the ceiling county) to the six largest counties, to all 33 counties, and to the formula.

1. [Cedar County Audit]({CEDAR}) (Nebraska wiki): where the method started
2. [Bottom-Up Reverse Math](Reverse-Math): Luna → the six largest counties → all 33 counties, the New Mexico-only constants fitted from New Mexico data, and the expected-loss residual layer
3. [Locked New Mexico Formula](Locked-New-Mexico-Formula): the Surplus Equation, a blank fill-in template and a worked example (Lea)
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at the top and bottom, the floor and ceiling constants, and the ballots-cast (over-ballot) check
5. [Graphs](Graphs): county slope chart, forward-fit scatter, ΔG by population, stacked share bars with registration loss
6. [New Mexico County PDF Information](New-Mexico-County-PDF-Information): downloadable 33-county PDF of Democratic registration, Democratic governor votes and total ballots, 2022 vs 2026{S}

## Statewide at a glance

| Measure | 2022 (official) | 2026{S} (unofficial) | Change |
|---|---|---|---|
| Democratic registration (SOS reports Oct 31, 2022 / Oct 30, 2026) | {v('sw.regdem22','int')} | {v('sw.regdem26','int')} | {v('sw.regdem_change','sint')} |
| Total registration (same reports) | {v('sw.regtot22','int')} | {v('sw.regtot26','int')} | {v('sw.regtot_change','sint')} |
| Democratic governor votes | {v('sw.dem22','int')} (Lujan Grisham) | {v('sw.dem26','int')}{S} (Haaland) | {v('sw.dem_change','sint')}{S} |
| Total ballots cast (SOS turnout) | {v('sw.ballots22','int')} | {v('sw.ballots26','int')}{S} | {v('sw.ballots_change','sint')}{S} |
| Democratic share of ballots cast | {v('sw.S22','pct2')} | {v('sw.S26','pct2')}{S} | {v('sw.dS','pt2')} pts{S} |
| Democratic registration share | {v('sw.R22','pct2')} | {v('sw.R26','pct2')} | {v('sw.dR','pt2')} pts |
| G = vote share − registration share | {v('sw.G22','pt2')} | {v('sw.G26','pt2')}{S} | ΔG {v('sw.dG','pt2')}{S} |

## County results in brief

- **ΔG rose in {v('dG.n_pos','int')} counties and fell in {v('dG.n_neg','int')}.** County median ΔG is {v('dG.median','pt2')}{S} (mean {v('dG.mean','pt2')}{S}), ranging from {cty(R,R.raw('dG.min_county'),'dG','pt2')}{S} ({v('dG.min_county','raw')}) to {cty(R,R.raw('dG.max_county'),'dG','pt2')}{S} ({v('dG.max_county','raw')}). Democratic vote share rose in {v('n_S_rose','int')} counties; registered Democrats fell in {v('n_reg_fell','int')} of 33, and the Democratic share of registration fell in all {v('n_regshare_fell','int')}.
- **Ceiling counties** (five largest ΔG): {capt}.
- **Floor counties** (most Republican baseline): {v('lowest_S22_county','raw')} has the lowest 2022 Democratic share of ballots cast in the state ({cty(R,'Lea','S22','pct2')}). The floor cluster is {flot}; its median ΔG, the **floor constant**, is {v('floor.median','pt2')}{S}. In New Mexico the floor counties moved more than the state as a whole, the opposite of Kansas.
- **Size slope:** ΔG changes {slope} points for every tenfold increase in population (r = {v('size.r','f2')}, p = {v('size.p','p')}): county size explains almost none of the spread. The **ceiling constant** (median ΔG of the three largest counties, {', '.join(R.raw('ceil3.counties'))}) is {v('ceil3.median','pt2')}{S}; with Santa Fe, San Juan and Valencia added it is {v('ceil6.median','pt2')}{S}.
- **New Mexico-only constants** (least squares, S = m·(D/100) + b, New Mexico data only): 2022 m = {v('fit.2022.m','f2')}, b = {v('fit.2022.b','f2')} (R² {v('fit.2022.r2','f3')}, residual SD {v('fit.2022.resid_sd','f2')} pts); 2026{S} m = {v('fit.2026.m','f2')}, b = {v('fit.2026.b','f2')} (R² {v('fit.2026.r2','f3')}, residual SD {v('fit.2026.resid_sd','f2')} pts). Registration share barely predicts the surplus in either year. See [Bottom-Up Reverse Math](Reverse-Math#new-mexico-only-constants-forward-surplus-fit).

## Read this before using the numbers

- **New Mexico moved a lot, and everywhere.** Statewide ΔG is {v('sw.dG','pt2')}{S}, and ΔG is positive in every county. About half of it is the drop in the Democratic share of registration ({v('sw.R22','pct2')} → {v('sw.R26','pct2')}); the rest is the rise in the Democratic share of ballots ({v('sw.S22','pct2')} → {v('sw.S26','pct2')}{S}).
- **The field changed.** In 2022, {v('sw.other22','int')} governor votes went to candidates other than the Democratic and Republican tickets; in 2026{S}, {v('sw.other26','int')} did. Because the denominator is ballots cast, that shift is part of the change in Democratic share.
- **A large ΔG is not evidence of altered votes.** Candidate choice, crossover voting by Republicans and voters who decline to state a party, turnout differences, and registration-list maintenance all move these numbers. The arithmetic cannot separate them.
- **2026 is unofficial.** Every 2026 figure is marked {S} and will be re-run after the State Canvassing Board approves the canvass.

## Verification

Every county figure on these pages was computed twice, by two independently written programs reading the raw SOS files: the original pass 1 / pass 2 pipeline (33 counties x 13 count fields, the second pass re-reading the 66 SOS county results pages and 66 county turnout exports), and then, for this rebuild, Kansas-parity pass A (pandas/statsmodels) and pass B (standard library with exact fractions). The two Kansas-parity passes compared {v('meta.kp_keys','int')} values key by key with **0 mismatches**. County sums equal the SOS statewide totals in both years. Every number written into these pages, the graphics, the letters and the PDF was then checked against pass B by script. Reports are in the repo's `verification/` folder.

## Sources

All election and registration numbers come from the New Mexico Secretary of State. Population (used only for sort order and the size slope) is from the U.S. Census Bureau. Retrieved Nov 19, 2026 (America/Chicago); clerk and equipment sources Nov 24, 2026.

| Data | Status | URL |
|---|---|---|
| 2022 general, Governor and Lieutenant Governor, "County Level" export and county results pages | OFFICIAL (last updated 11/29/2022 4:39 PM MT) | https://electionresults.sos.nm.gov/resultsSW.aspx?type=SW&map=CTY&eid=2838 |
| 2026 general, Governor and Lieutenant Governor (Haaland D, Hull R), same export and pages | **UNOFFICIAL{S}** (last updated 11/12/2026 11:07 AM MT) | https://electionresults.sos.nm.gov/resultsSW.aspx?type=SW&map=CTY |
| Ballots cast by county (Voter Turnout page and county turnout exports; the two agree in all 66 county-years) | 2022 official, 2026 unofficial{S} | https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx |
| Voter registration by county and party, as of Oct 31, 2022 ("Statewide by County") | SOS report | https://www.sos.nm.gov/sos-archive/voter-statistics-data-archive/2022-voter-statistics-data/ |
| Voter registration by county and party, as of Oct 30, 2026 ("Statewide by County") | SOS report | https://www.sos.nm.gov/voting-and-elections/data-and-maps/voter-registration-statistics/2026-voter-registration-data/ |
| County population, July 1, 2025 | U.S. Census Bureau Vintage 2025 | https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv |

The SOS 2022 General Recount (Dec 5, 2022) covered legislative contests only; the governor race was not recounted. Data files, charts and scripts: [mbenson8989/New-Mexico-Election-Analysis]({REPO}).

**Other state wikis:** [Nebraska]({NEWIKI}) · [Iowa](https://github.com/mbenson8989/Iowa-Election-Analysis/wiki) · [South Dakota](https://github.com/mbenson8989/South-Dakota-Election-Analysis/wiki) · [Texas](https://github.com/mbenson8989/Texas-Election-Analysis/wiki) · [Michigan](https://github.com/mbenson8989/Michigan-Election-Analysis/wiki) · [Kansas](https://github.com/mbenson8989/Kansas-Election-Analysis/wiki)

## Added Nov 24, 2026: expected-loss residual layer

As on the Kansas wiki, [Bottom-Up Reverse Math](Reverse-Math{EL_ANCHOR}) has a separate, labelled section that applies the Nebraska / Iowa / South Dakota reverse step: residual = ΔG − expected loss from the registration-share decline, then solved backward for offset votes, on the ballots-cast denominator. The [Locked New Mexico Formula](Locked-New-Mexico-Formula) page is unchanged. Statewide, the residual is {v('el.sw_residual','pt2')}{S} points ({v('el.pooled_votes','sint')}{S} votes pooled); the county median is {v('el.median_res','pt2')}{S}, and the residual is positive in {v('el.n_pos','int')} of 33 counties. 2026 figures are unofficial.

{related('Home')}"""
write(R,'Home.md',body)
print('home ok')
