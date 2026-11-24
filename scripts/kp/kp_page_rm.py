from kp_pages_common import *
R=Reg('reverse_math'); v=R.v
order=R.raw('counties_pop_order'); six=R.raw('ceil6.counties'); cap=R.raw('ceiling5'); nonloss=R.raw('nonloss.counties')
L='Luna'; c=lambda k,f:cty(R,L,k,f)
assert R.raw('dG.max_county')==L
step1=f"""| Step | Value |
|---|---|
| Democratic share of ballots cast | {c('S22','pct2')} (2022: {c('dem22','int')} of {c('ballots22','int')}) → {c('S26','pct2')}{S} (2026: {c('dem26','int')} of {c('ballots26','int')}{S}): **{c('dS','pt2')} points{S}** |
| Democratic registration share | {c('R22','pct2')} ({c('regdem22','int')} of {c('regtot22','int')}) → {c('R26','pct2')} ({c('regdem26','int')} of {c('regtot26','int')}): **{c('dR','pt2')} points** |
| G 2022 = vote share − registration share | {c('S22','f2')} − {c('R22','f2')} = **{c('G22','pt2')}** |
| G 2026{S} | {c('S26','f2')} − {c('R26','f2')} = **{c('G26','pt2')}{S}** |
| ΔG = G 2026 − G 2022 | **{c('dG','pt2')} points{S}**, the largest in New Mexico |
| Registered Democrats | {c('regdem22','int')} → {c('regdem26','int')} ({c('reg_change','sint')}): Luna lost registered Democrats while its Democratic governor vote rose {c('dem22','int')} → {c('dem26','int')}{S} |"""
rows6='\n'.join(f"| {x} | {cty(R,x,'population','int')} | {arrow(R,x,'regdem22','regdem26','int')} | {arrow(R,x,'dem22','dem26','int')} | {arrow(R,x,'ballots22','ballots26','int')} | {cty(R,x,'G22','pt2')} | {cty(R,x,'G26','pt2')} | {cty(R,x,'dG','pt2')} |" for x in six)
in_cap=[x for x in six if x in cap]
fell6=[x for x in six if R.raw(f'c.{x}.dG')<0]
six_note=(f"None of the six is among the five ceiling counties." if not in_cap else f"{', '.join(in_cap)} {'is' if len(in_cap)==1 else 'are'} among the five ceiling counties.")
def grp(g,lab):
    p=f'grp.{g}.'
    return f"| {lab} | {v(p+'n','int')} | {v(p+'S22','pct2')} → {v(p+'S26','pct2')}{S} | {v(p+'R22','pct2')} → {v(p+'R26','pct2')} | {v(p+'dS','pt2')} | {v(p+'dR','pt2')} | {v(p+'dG','pt2')} | {v(p+'med','pt2')} ({v(p+'lo','pt2')} to {v(p+'hi','pt2')}) |"
def fitrow(y,lab):
    p=f'fit.{y}.'
    return f"| {lab} | {v(p+'n','int')} | {v(p+'m','f2')} (95% CI {v(p+'m_lo','f2')} to {v(p+'m_hi','f2')}) | {v(p+'b','f2')} ({v(p+'b_lo','f2')} to {v(p+'b_hi','f2')}) | {v(p+'r2','f3')} | {v(p+'resid_sd','f2')} | {v(p+'w2','int')} / {v(p+'w5','int')} |"
def nb(st,name):
    q=lambda y,k:v(f'ext.{st}.{y}.ballots.{k}','f2')
    return f"| {name} ({v(f'ext.{st}.2022.ballots.n','int')}) | {q('2022','m')} / {q('2022','b')} | {q('2026','m')} / {q('2026','b')} |"
side26=R.raw('band.2026.m.side')
flag=(f"**New Mexico's 2022 line sits inside the band of the other three states; its 2026{S} multiplier does not.** On the ballots-cast basis the 2026{S} band for m is "
      f"{v('band.2026.m.lo','f2')} to {v('band.2026.m.hi','f2')}, and New Mexico's m ({v('fit.2026.m','f2')}) is {v('band.2026.m.dist','f2')} {side26} it "
      f"({v('band.2026.m.dist_se','f2')} New Mexico standard errors). New Mexico's 95% confidence interval for m {'does' if R.raw('band.2026.m.ci_overlap') else 'does not'} overlap the band, because the New Mexico slope is so loosely determined (R² {v('fit.2026.r2','f3')}). "
      f"The offset b is inside the band in both years (2022: {v('fit.2022.b','f2')} vs {v('band.2022.b.lo','f2')} to {v('band.2022.b.hi','f2')}; 2026{S}: {v('fit.2026.b','f2')} vs {v('band.2026.b.lo','f2')} to {v('band.2026.b.hi','f2')}). "
      f"Registration definitions differ by state and several states' 2026 figures are also unofficial, so the comparison is descriptive.")
assert R.raw('band.2022.m.inside') and R.raw('band.2022.b.inside') and R.raw('band.2026.b.inside') and side26=='below'
pa='\n'.join(f"| {x} | {cty(R,x,'population','int')} | {cty(R,x,'dem22','int')} | {cty(R,x,'ballots22','int')} | {cty(R,x,'regdem22','int')} | {cty(R,x,'regtot22','int')} | {cty(R,x,'G22','pt2')} |" for x in order)
pb='\n'.join(f"| {x} | {cty(R,x,'population','int')} | {cty(R,x,'dem26','int')} | {cty(R,x,'ballots26','int')} | {cty(R,x,'regdem26','int')} | {cty(R,x,'regtot26','int')} | {cty(R,x,'G26','pt2')} | {cty(R,x,'dG','pt2')} |" for x in order)
dag=lambda x:' †' if x in nonloss else ''
ea='\n'.join(f"| {x}{dag(x)} | {cty(R,x,'population','int')} | {arrow(R,x,'regdem22','regdem26','int')} | {arrow(R,x,'R22','R26','pct2')} | {cty(R,x,'exp_loss','pt2')} |" for x in order)
eb='\n'.join(f"| {x}{dag(x)} | {cty(R,x,'population','int')} | {cty(R,x,'dG','pt2')} | {cty(R,x,'residual','pt2')} | {cty(R,x,'ballots26','int')} | {cty(R,x,'offset_votes','sint')} | {cty(R,x,'gap_votes','sint')} |" for x in order)
def tb(lst):
    lst=[x for x in order if x in lst]
    return '\n'.join(f"| {x}{dag(x)} | {cty(R,x,'population','int')} | {arrow(R,x,'R22','R26','pct2')} | {cty(R,x,'exp_loss','pt2')} | {cty(R,x,'dG','pt2')} | {cty(R,x,'residual','pt2')} | {cty(R,x,'ballots26','int')} | {cty(R,x,'offset_votes','sint')} |" for x in lst)
TH="| County | Population | Dem reg share 2022 → 2026 | Expected loss (pts) | ΔG\\* | Residual\\* (pts) | Total ballots 2026\\* | Backward-solved offset votes\\* |\n|---|---|---|---|---|---|---|---|"
W_='Bernalillo'; w=lambda k,f:cty(R,W_,k,f)
pos_v=', '.join(f"{x}{dag(x)} {cty(R,x,'offset_votes','sint')}{S}" for x in R.raw('el.top5_votes'))
bv=R.raw('el.bot5_votes'); bneg=[x for x in bv if R.raw(f'c.{x}.offset_votes')<0]; bpos=[x for x in bv if x not in bneg]
fmtv=lambda xs:', '.join(f"{x}{dag(x)} {cty(R,x,'offset_votes','sint')}{S}" for x in xs)
neg_v=(f"{fmtv(bneg)} (the only {len(bneg)} negative figures), followed by {fmtv(bpos)}" if bpos else fmtv(bneg))
R.use('el.top5_votes'); R.use('el.bot5_votes'); R.use('el.top5'); R.use('el.bot5')
neg_res=[x for x in order if R.raw(f'c.{x}.residual')<0]
body=f"""# Bottom-Up Reverse Math

{BANNER}

The same arithmetic at three levels, from one county up to the whole state, then the New Mexico-only constants fitted across all 33 counties. Denominator: total ballots cast, both years. The method comes from the [Cedar County Audit]({CEDAR}) in Nebraska.

## Step 1: Luna County (the ceiling county)

{step1}

## Step 2: the six largest counties

Largest to smallest population.

| County | Population | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026\\* | Total ballots 2022 → 2026\\* | G 2022 | G 2026\\* | ΔG\\* |
|---|---|---|---|---|---|---|---|
{rows6}

{six_note} {'None of the six had ΔG fall.' if not fell6 else ''} The six largest counties' median ΔG ({v('grp.six.med','pt2')}{S}) is below the state median ({v('dG.median','pt2')}{S}): in New Mexico the larger counties moved less, not more, which is the opposite of Kansas (see the size slope below).

## Step 3: all 33 counties

| Group | Counties | Dem vote share | Dem registration share | Vote-share change\\* | Reg-share change | Pooled ΔG\\* | County median ΔG\\* (range) |
|---|---|---|---|---|---|---|---|
{grp('six','Six largest counties')}
{grp('other','Other counties')}
{grp('all','All New Mexico counties')}

- ΔG rose in {v('dG.n_pos','int')} of 33 counties and fell in {v('dG.n_neg','int')}. County-level SD of ΔG: {v('dG.sd','f2')} points.
- **Size slope:** ΔG = {v('size.intercept','f2')} {signed_term(R,'size.slope')} × log10(population). That is {v('size.slope','pt2')} points per tenfold population (r = {v('size.r','f2')}, R² = {v('size.r2','f3')}, p = {v('size.p','p')}). County size explains essentially none of the spread in New Mexico.

## New Mexico-only constants (forward surplus fit)

New Mexico's own constants are fitted from New Mexico data only; no other state's constant is reused. For each county, S = G (Democratic share of ballots cast − Democratic registration share, in points) and D = Democratic registration share (%). Ordinary least squares across the 33 counties fits **S = m × (D/100) + b**. These are the same 2022 and 2026{S} values shown on the [Locked New Mexico Formula](Locked-New-Mexico-Formula) page.

| Fit | n | m (multiplier) | b (offset, pts) | R² | Residual SD (pts) | Counties within ±2 / ±5 pts of the line |
|---|---|---|---|---|---|---|
{fitrow('2022','2022 (official)')}
{fitrow('2026','2026\\* (unofficial)')}
{fitrow('pooled','Pooled, both years')}

**How to read it.** A county with D = 40% registered Democrats is expected to have S = m × 0.40 + b: in 2022 about {v('fit.2022.at40','f2')} points, in 2026{S} about {v('fit.2026.at40','f2')} points. In both years the slope is slightly negative and not distinguishable from zero: the Democratic candidate's lead over registration did not grow with the share of registered Democrats.

**Tightness.** The residual SD (the typical distance of a county from the fitted line) went from {v('fit.2022.resid_sd','f2')} points in 2022 to {v('fit.2026.resid_sd','f2')} in 2026{S}, and R² from {v('fit.2022.r2','f3')} to {v('fit.2026.r2','f3')}. Testing both years in one model, the 2026 slope differs by {v('fit.int.d_m','pt2')} (p = {v('fit.int.p_d_m','p')}, not significant), and the 2026 offset is higher by {v('fit.int.d_b','f2')} points (p = {v('fit.int.p_d_b','p')}). In New Mexico the whole line moved up in 2026{S}; it did not get steeper.

### Compared with other states

Same fit, as published on the Kansas wiki for Nebraska, Iowa and South Dakota (each from its own county files), on the ballots-cast basis that New Mexico uses. Shown as m / b. Kansas is not in this table: it divides by governor votes, not ballots. None of New Mexico's neighbors has a comparable fit on these wikis: Texas, the only one with a wiki, has no party registration.

| State | 2022, ballots | 2026\\*, ballots |
|---|---|---|
{nb('NE','Nebraska')}
{nb('IA','Iowa')}
{nb('SD','South Dakota')}
| **New Mexico (33)** | **{v('fit.2022.m','f2')} / {v('fit.2022.b','f2')}** | **{v('fit.2026.m','f2')} / {v('fit.2026.b','f2')}** |

{flag}

## Not computed here

The [Locked New Mexico Formula](Locked-New-Mexico-Formula) is the surplus form only; it has no expected-loss step and no backward-solved votes. That page is left exactly as it was. The expected-loss step is added below as a separate, labelled layer.

## What the arithmetic cannot tell you

- **The field changed.** In 2022, {v('sw.other22','int')} governor votes went to candidates other than the two major tickets; in 2026{S}, {v('sw.other26','int')}. With ballots cast as the denominator, a county where those voters went Democratic in 2026 shows a larger ΔG for that reason alone.
- **Registered Democrats are not the only people who vote for Democrats.** Registration fell for Democrats ({v('sw.regdem_change','sint')}) while total registration rose ({v('sw.regtot_change','sint')}), so the registration share drops even where the same people vote the same way.
- **2026 is unofficial.** These totals come from the SOS "Unofficial Results" site. They will be re-run after the state canvass.

## All 33 counties

Largest to smallest population. G = 100 × Dem governor votes ÷ total ballots cast − 100 × Dem registered ÷ total registered.

**Part A: 2022 (official).** Votes, ballots, registration and G.

| County | Population | Dem gov votes 2022 | Total ballots 2022 | Dem reg 2022 | Total reg 2022 | G 2022 |
|---|---|---|---|---|---|---|
{pa}

**Part B: 2026\\* (unofficial) and the change.** Votes, ballots, registration, G and ΔG = G 2026 − G 2022 (Part A). Same 33 counties, same order.

| County | Population | Dem gov votes 2026\\* | Total ballots 2026\\* | Dem reg 2026 | Total reg 2026 | G 2026\\* | ΔG\\* |
|---|---|---|---|---|---|---|---|
{pb}

## Expected-Loss Residual and Backward-Solved Offset Votes (NE/IA/SD method)

> **Separate layer, added Nov 24, 2026, in the same form as the Kansas wiki.** This section applies the reverse-factoring step used on the Nebraska, Iowa and South Dakota wikis. It is a separate layer. **Everything above this section is unchanged**, including G, ΔG, the New Mexico-only forward fit and the 33-county table, and the Locked New Mexico Formula page is untouched. \\*2026 figures are UNOFFICIAL (SOS "Unofficial Results", last updated 11/12/2026 11:07 AM MT; state canvass Nov 24, 2026).

### The formulas, exactly as the other states define them

- **Nebraska** (`nebraska-elections/statewide/scripts/analyze.py`): `regdrop = RD_2022 − RD_2026`; `resid = dG − regdrop` ("= change in D share of ballots"); `unexpl_votes = resid / 100 × ballots_2026`.
- **Iowa** (`iowa-wiki/repo/scripts/resolve.py`): `reg_share_loss = R22 − R26`; `residual = dG − reg_share_loss`; `residual_votes = D26 − S22 / 100 × ballots26`. The statewide offset need is "switched votes = s × N; added votes = s × N ÷ (1 − p + s)", where s is the registration-share decline (plus any cushion), N is 2026 ballots and p is the 2026 Democratic share.
- **South Dakota** (`south-dakota-elections/github_wiki_build_sd.py`): "Residual = ΔG − registration-share drop, where registration-share drop = Dem reg share 2022 − Dem reg share 2026"; "Implied extra (offset) votes = residual × 2026 ballots cast ÷ 100".

All three are the same arithmetic. Applied to New Mexico:

- **Expected loss** (points) = Dem registration share 2022 − Dem registration share 2026
- **Residual** (points) = ΔG − expected loss = Dem share of ballots cast 2026 − Dem share of ballots cast 2022
- **Backward-solved offset votes** = residual ÷ 100 × 2026 ballots cast = 2026 Dem votes − (2022 Dem share × 2026 ballots cast)

### Where New Mexico differs

1. **Denominator.** New Mexico uses ballots cast, exactly as the Nebraska script, Iowa and South Dakota do (Kansas had to use governor votes). N in every formula here is the 2026 ballots cast, {v('sw.ballots26','int')}{S} statewide.
2. **Candidate field.** {v('sw.other22','int')} governor votes in 2022 went to candidates other than the two major tickets; {v('sw.other26','int')} in 2026{S}. The residual includes wherever those voters went.
3. **Registration snapshot.** Registration is the SOS "Statewide by County" report as of Oct 30, 2026, four days before the election, and Oct 31, 2022, eight days before.
4. **Non-loss counties.** South Dakota and Iowa run the residual step only for counties that lost registered Democrats. New Mexico has {len(nonloss)} non-loss counties ({v('nonloss.counties','list')}). They are marked † below and shown for completeness, and statewide totals are given with and without them.
5. **Sign.** In New Mexico the residual is positive in {v('el.n_pos','int')} of 33 counties and negative in {v('el.n_neg','int')} ({', '.join(neg_res)}). Negative values are reported as computed, not set to zero.

### New Mexico-only constants for this layer

Computed from New Mexico data only; no other state's constant is used.

- **Statewide pooled:** expected loss {v('el.sw_exp_loss','pt2')} points (registration share {v('sw.R22','pct2')} → {v('sw.R26','pct2')}), ΔG {v('sw.dG','pt2')}{S}, residual {v('el.sw_residual','pt2')}{S}.
- **County residual:** median {v('el.median_res','pt2')}{S}, mean {v('el.mean_res','pt2')}{S}, SD {v('el.sd_res','f2')}. Positive in {v('el.n_pos','int')} counties, negative in {v('el.n_neg','int')}.
- **Registration constant** (South Dakota's check, fitted on New Mexico): ΔG = {v('el.regfit.a','f2')} {signed_term(R,'el.regfit.b')} × expected loss across 33 counties (slope SE {v('el.regfit.b_se','f2')}, R² {v('el.regfit.r2','f3')}). In New Mexico the registration-share decline explains almost none of the county-to-county spread in ΔG; South Dakota's own fit had a slope near 1.

### Statewide backward solve

| Measure | Votes\\* |
|---|---|
| Statewide, pooled: residual {v('el.sw_residual','pt2')} pts × {v('sw.ballots26','int')} 2026 ballots ÷ 100 | {v('el.pooled_votes','sint')} |
| Sum of the 33 county figures (net) | {v('el.county_sum','sint')} |
| … the {33-len(nonloss)} counties that lost registered Democrats | {v('el.sum_loss','sint')} |
| … the {len(nonloss)} non-loss counties † | {v('el.sum_nonloss','sint')} |
| Raw rise in Democratic governor votes | {v('el.raw_rise','sint')} = {v('el.pooled_votes','int')} share gain + {v('el.turnout_part','int')} from more ballots at the 2022 share |
| Offset need for the {v('el.sw_exp_loss','f2')}-point registration-share decline: switched / added votes | {v('el.need0.switched','int')} / {v('el.need0.added','int')} |
| Same, with a 1-point cushion | {v('el.need1.switched','int')} / {v('el.need1.added','int')} |
| Same, with a 2-point cushion | {v('el.need2.switched','int')} / {v('el.need2.added','int')} |
| Comparison, Nebraska wiki "gap in votes" (2026 Dem votes − 2022 Dem votes × registration ratio), county sum | {v('el.gap_sum','sint')} |
| Comparison, Nebraska wiki "residual votes" (ballots × ΔG ÷ 100), county sum | {v('el.ne_resid_sum','sint')} |

The pooled figure and the county sum differ because pooling also counts where the ballots were cast: the {v('el.n_above','int')} counties above the 2022 statewide Democratic share cast {v('el.above_share_ballots22','pct2')} of ballots in 2022 and {v('el.above_share_ballots26','pct2')}{S} in 2026. The offset need uses Iowa's formula with s = the statewide registration-share decline and p = the 2026 Democratic share ({v('sw.S26','pct2')}{S}).

### Worked example: Bernalillo

Registration share {w('R22','pct2')} → {w('R26','pct2')}: expected loss {w('exp_loss','f2')} points. ΔG {w('dG','pt2')}{S}. Residual {w('dG','f2')} − {w('exp_loss','f2')} = **{w('residual','pt2')}{S}** (Democratic share of ballots cast {w('S22','pct2')} → {w('S26','pct2')}{S}; computed from unrounded shares). Backward-solved offset votes {w('residual','pt2')} × {w('ballots26','int')} ÷ 100 = **{w('offset_votes','sint')}{S}**, the same as {w('dem26','int')} − {w('S22','pct2')} × {w('ballots26','int')}.

### Top and bottom counties

Five highest residuals (population order):

{TH}
{tb(R.raw('el.top5'))}

Five lowest residuals (population order):

{TH}
{tb(R.raw('el.bot5'))}

By backward-solved votes, the largest positive figures are {pos_v}. The lowest are {neg_v}. Large counties dominate the vote figures because the residual is multiplied by each county's ballots.

![Residual after the expected loss, by population](NM_Expected_Loss_Residual_Bars_by_Population.png)

*Residual (ΔG minus expected loss) for all 33 counties, largest to smallest population. Orange: ceiling counties. Blue: floor counties. Hatched: non-loss counties.*

> **Hypothesis label.** Turning the residual into "backward-solved offset votes" and calling them injected, switched or offset votes is Morissa Benson's hypothesis, which the arithmetic cannot test. The same number reflects candidate choice, the change in the candidate field, crossover voting, turnout changes and any other cause. Candidate votes are not turnout, and registered Democrats are not the only people who vote for Democrats.

### All 33 counties, expected-loss layer

Largest to smallest population. † = non-loss county (registered Democrats did not fall). "Gap in votes" is the Nebraska wiki's comparison line: 2026 Dem votes − 2022 Dem votes × (Dem reg 2026 ÷ Dem reg 2022).

**Part A: registration and the expected loss.** Same 33 counties, same order.

| County | Population | Dem reg 2022 → 2026 | Dem reg share 2022 → 2026 | Expected loss (pts) |
|---|---|---|---|---|
{ea}

**Part B: residual and backward-solved votes.** Residual = ΔG − expected loss (Part A). Same 33 counties, same order.

| County | Population | ΔG\\* | Residual\\* (pts) | Total ballots 2026\\* | Backward-solved offset votes\\* | Gap in votes\\* (NE comparison) |
|---|---|---|---|---|---|---|
{eb}

{related('Reverse-Math')}"""
write(R,'Reverse-Math.md',body); print('rm ok', len(body.splitlines()))
