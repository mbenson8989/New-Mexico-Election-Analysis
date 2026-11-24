from kp_pages_common import *
R=Reg('floor_ceiling'); v=R.v
order=R.raw('counties_pop_order'); cap=R.raw('ceiling5'); flo=R.raw('floor.counties'); bot=R.raw('bottom5'); nonloss=R.raw('nonloss.counties')
top=R.raw('dG.max_county'); low=R.raw('dG.min_county'); fl=R.raw('lowest_S22_county'); lg=R.raw('lowest_G22_county')
# share-based lists used on the (frozen) Locked page: five highest and five lowest 2022 Democratic shares of ballots
byS=sorted(order,key=lambda x:-R.use(f'c.{x}.S22'))
hi5=byS[:5]; lo5=byS[::-1][:5]
assert hi5==['Taos','Santa Fe','San Miguel','McKinley','Mora'] and lo5==['Lea','Eddy','De Baca','Union','Catron'], (hi5,lo5)  # as printed on the Locked page
capt=', '.join(f"{x} {cty(R,x,'dG','pt2')}{S}" for x in cap)
flot=', '.join(f"{x} {cty(R,x,'dG','pt2')}{S}" for x in sorted(flo,key=lambda x:R.raw(f'c.{x}.S22')))
bott=', '.join(f"{x} {cty(R,x,'dG','pt2')}{S}" for x in bot)
nl=', '.join(f"{x} ({arrow(R,x,'regdem22','regdem26','int')})" for x in nonloss)
both=[x for x in cap if x in flo]; botflo=[x for x in bot if x in flo]
def grp(x):
    g=[]
    if x in cap: g.append('Ceiling')
    if x in flo: g.append('Floor')
    if x in bot: g.append('Bottom-5 ΔG')
    return ' and '.join(g)
det='\n'.join(f"| {x} | {grp(x)} | {cty(R,x,'population','int')} | {cty(R,x,'S22','pct2')} | {cty(R,x,'G22','pt2')} | {cty(R,x,'G26','pt2')} | {cty(R,x,'dG','pt2')} | {arrow(R,x,'R22','R26','pct2')} | {arrow(R,x,'regdem22','regdem26','int')} ({cty(R,x,'reg_pct','spct1')}) | {arrow(R,x,'dem22','dem26','int')} |" for x in order if x in set(cap)|set(flo)|set(bot))
capfell=all(R.raw(f'c.{x}.reg_change')<0 for x in cap)
tight=R.use('tx.tightest')
trow='\n'.join(f"| {x} 20{y}{S if y=='26' else ''} | {cty(R,x,'ballots'+y,'int')} | {cty(R,x,'DR'+y,'int')} | {cty(R,x,'allgov'+y,'int')} | {cty(R,x,'regtot'+y,'int')} | {cty(R,x,'spare'+y,'int')} |" for x,y in tight)
none=lambda k:('none' if not R.raw(k) else ', '.join(R.raw(k)))
for k in ('tx.DR_gt_ballots22','tx.gov_gt_ballots22','tx.ballots_gt_reg22','tx.nogov_gt5_22','tx.DR_gt_ballots26','tx.gov_gt_ballots26','tx.ballots_gt_reg26','tx.nogov_gt5_26'): v(k,'list')
mx22=R.raw('tx.nogov_max_county22'); mx26=R.raw('tx.nogov_max_county26')
EQ=__import__('json').load(open('/workspace/nm-election/out/kp_equipment_summary_A.json'))
body=f"""# Floor and Ceiling Counties

{BANNER}

## How to read floor and ceiling counties

Look for the pattern at both ends. The ceiling counties are the ones with the highest ΔG. The floor counties are the most Republican baseline counties, where there were the fewest Democrats to move.

- **The ceiling** is the single county with the highest ΔG in the state. In New Mexico that is **{v('dG.max_county','raw')}, at {cty(R,top,'dG','pt2')}{S}**.
- **The floor county** (most Republican baseline) is **{v('lowest_S22_county','raw')}**: the lowest 2022 Democratic share of ballots cast ({cty(R,fl,'S22','pct2')}). Its 2022 surplus G was {cty(R,fl,'G22','pt2')}; the lowest 2022 G belongs to {v('lowest_G22_county','raw')} ({cty(R,lg,'G22','pt2')}). Lea's ΔG was {cty(R,fl,'dG','pt2')}{S}, the second largest in the state, so in New Mexico the floor county is also a ceiling county.
- **The lowest ΔG** is {v('dG.min_county','raw')}, at {cty(R,low,'dG','pt2')}{S}. No county's ΔG fell.

Every state has its own floor and ceiling. Those extremes set the range the rest of that state's counties fall within.

## Terminology

- **Ceiling counties** are the five largest ΔG: {capt}.
- **Floor counties** are the most Republican baseline. Rule (2022 data only, the Kansas rule): 2022 Democratic share of ballots at or below the 10th percentile ({v('floor.q10_S22','pct2')}) **and** 2022 G at or below the 25th percentile ({v('floor.q25_G22','pt2')}). {len(flo)} counties qualify, lowest 2022 Democratic share first: {flot} (ΔG shown). {' and '.join(both)} {'is' if len(both)==1 else 'are'} both floor and ceiling counties.
- **Bottom-5 ΔG** (the smallest rises; no county fell): {bott}. {'None of them is a floor county.' if not botflo else ''}
- **Non-loss counties** had no loss of registered Democrats. Raw numbers only: {nl}.
- **Share-based ceiling and floor (the definitions printed on the [Locked New Mexico Formula](Locked-New-Mexico-Formula) page).** That page, left unchanged, uses the earlier New Mexico rule: ceiling = the five highest 2022 Democratic shares of ballots ({', '.join(hi5)}), floor = the five lowest ({', '.join(lo5)}). Under it the ceiling county is Taos ({cty(R,'Taos','S22','pct2')}) and the floor county is Lea, the same floor county as the Kansas rule. The two rules answer different questions: the Kansas rule ranks counties by how much they moved (ΔG); the share-based rule ranks them by where they started.
- **Surplus (S), Residual:** as defined on the [Locked New Mexico Formula](Locked-New-Mexico-Formula) page: S is the Democratic share of ballots cast minus the Democratic registration share, in points (the same number as G); a residual is a county's distance from a fitted line and does not test a cause.

## Floor and ceiling constants

| Constant | Counties | Median ΔG\\* | Mean ΔG\\* |
|---|---|---|---|
| **Floor constant** | the {len(flo)} floor counties | **{v('floor.median','pt2')}** | {v('floor.mean','pt2')} |
| **Ceiling constant** (three largest counties) | {v('ceil3.counties','list')} | **{v('ceil3.median','pt2')}** | {v('ceil3.mean','pt2')} |
| Ceiling constant, six counties | + Santa Fe, San Juan, Valencia | **{v('ceil6.median','pt2')}** | {v('ceil6.mean','pt2')} |
| Statewide | all 33 counties | {v('dG.median','pt2')} | {v('dG.mean','pt2')} |

The constants are medians, which keeps one county from dominating a small group. Kansas took its ceiling constant from its largest metro counties; New Mexico has one metro county (Bernalillo), so the New Mexico ceiling constant uses the three largest counties by population, and the six largest for the wider version. **New Mexico runs the other way from Kansas:** the floor constant ({v('floor.median','pt2')}{S}) is above both ceiling constants and above the statewide median, and ΔG does not climb with county size ({v('size.slope','pt2')} points per tenfold population, r = {v('size.r','f2')}, p = {v('size.p','p')}).

## Ceiling and floor detail

Largest to smallest population.

| County | Group | Population | Dem share of ballots 2022 | G 2022 | G 2026\\* | ΔG\\* | Dem reg share 2022 → 2026 | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026\\* |
|---|---|---|---|---|---|---|---|---|---|
{det}

**Ceiling profile.** Two of the five ceiling counties (Luna and Hidalgo) are in the southwest along the Mexican border; Lea, Curry and De Baca are on the eastern plains. {'Registered Democrats fell in all five.' if capfell else ''} Lea and De Baca are also floor counties: they started among the most Republican baselines in the state and are among the five largest rises.

**Floor profile.** The {len(flo)} floor counties are all in eastern and southeastern New Mexico. Unlike Kansas, where the floor barely moved, the New Mexico floor moved more than the state: median ΔG {v('floor.median','pt2')}{S} against the statewide county median {v('dG.median','pt2')}{S}.

## Ballots-cast check (Texas style)

The Texas wiki checks for counties where Democratic plus Republican votes exceed ballots cast. New Mexico's SOS publishes ballots cast by county for both years (the turnout page and each county's turnout export, which agree in all 66 county-years), so both years can be checked. These would be anomalies in the data file, not findings about the election.

| Check | 2022 | 2026\\* |
|---|---|---|
| Democratic + Republican governor votes exceed ballots cast | {none('tx.DR_gt_ballots22')} | {none('tx.DR_gt_ballots26')} |
| Total governor votes (all candidates) exceed ballots cast | {none('tx.gov_gt_ballots22')} | {none('tx.gov_gt_ballots26')} |
| Ballots cast exceed registered voters | {none('tx.ballots_gt_reg22')} | {none('tx.ballots_gt_reg26')} |
| Ballots with no governor vote above 5% | {none('tx.nogov_gt5_22')} (county median {v('tx.nogov_median22','pct2')}; highest {v('tx.nogov_max_county22','raw')} {cty(R,mx22,'nogov22','pct2')}) | {none('tx.nogov_gt5_26')} (county median {v('tx.nogov_median26','pct2')}; highest {v('tx.nogov_max_county26','raw')} {cty(R,mx26,'nogov26','pct2')}) |

The closest county-years, fewest ballots to spare (ballots cast minus Democratic and Republican governor votes):

| County and year | Ballots cast | Dem + Rep gov votes | All gov votes | Registered | Ballots minus Dem + Rep |
|---|---|---|---|---|---|
{trow}

## Absentee and mail voting

- **By candidate:** the SOS county results pages and "County Level" exports used here report candidate totals per county. This rebuild did not find a county absentee-versus-election-day breakdown by candidate for 2022 or 2026{S} on the SOS pages checked (Nov 24, 2026), so no absentee share is computed.
- **Equipment:** Verified Voting lists a central batch-fed scanner (ImageCast Central) for absentee ballots in {len(EQ['_central_mail'])} counties ({', '.join(EQ['_central_mail'])}); the other {len(EQ['_mail_on_ed_unit'])} count mail ballots on the same ImageCast Evolution units used at the polls. See [Resources](Resources#voting-equipment-by-county).

![Delta-G by population, ceiling and floor counties marked](NM_DeltaG_Bars_by_Population.png)

*All 33 counties, ΔG\\* in population order. Orange: ceiling (5 largest ΔG). Blue: floor (most Republican baseline). Hatched: both. Dotted lines: floor and ceiling constants.*

![County slope chart, G 2022 to G 2026](NM_Slope_G2022_to_G2026_County_Slope_Chart.png)

*Each line is one county, G 2022 to G 2026\\*. Ceiling counties in orange, floor counties in blue (dashed where a county is both), labeled with ΔG.*

{related('Floor-and-Ceiling')}"""
write(R,'Floor-and-Ceiling.md',body); print('fc ok')
