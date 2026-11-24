from kp_pages_common import *
R=Reg('graphs'); v=R.v
cap=R.raw('ceiling5'); flo=R.raw('floor.counties'); bot=R.raw('bottom5'); top=R.raw('dG.max_county')
assert R.raw('dG.n_neg')==0
rosetxt=f"G rose in all {v('dG.n_pos','int')} counties; it fell in none."
capt=', '.join(f"{x} {cty(R,x,'dG','pt2')}{S}" for x in cap)
def eq(y): 
    k=f'fit.{y}.'; return f"S = {v(k+'m','f2')}·(D/100) {signed_term(R,k+'b')}, R² {v(k+'r2','f3')}, residual SD {v(k+'resid_sd','f2')}"
body=f"""# Graphs

{BANNER}

All charts use the ballots-cast denominator in both years and list counties largest to smallest population (Census, July 1, 2025) unless the title says otherwise. Images are stored in the [New-Mexico-Election-Analysis repo]({REPO}).

## 1. County slope chart

![County slope chart, G 2022 to G 2026](NM_Slope_G2022_to_G2026_County_Slope_Chart.png)

*Each gray line is one county, from its 2022 surplus G to its 2026{S} surplus G. {rosetxt} Orange: the five ceiling counties, the largest upward shifts ({capt}). Blue: the {len(flo)} floor counties (most Republican baseline); Lea and De Baca are both and are drawn dashed. Each highlighted line is labeled with its ΔG.*

## 2. Forward surplus fit: S against D

![Forward surplus fit, S = m(D/100) + b, 2022 and 2026](NM_Forward_Surplus_Fit_S_vs_D.png)

*New Mexico-only least-squares lines. 2022: {eq('2022')}. 2026{S}: {eq('2026')}. Shaded band: ±1 residual SD. These are the same fits as the [Locked New Mexico Formula](Locked-New-Mexico-Formula) page.*

## 3. ΔG by population

![Delta-G for all 33 counties in population order, floor and ceiling marked](NM_DeltaG_Bars_by_Population.png)

*All 33 counties in population order. Ceiling: {v('dG.max_county','raw')} is the highest ΔG{S}. Hatched: Lea and De Baca, both ceiling and floor. Lines: county median {v('dG.median','pt2')}, floor constant {v('floor.median','pt2')} and ceiling constant {v('ceil3.median','pt2')} (three largest counties).*

![Delta-G by county with names, trend against log population](NM_DeltaG_by_Population_Scatter_Names.png)

*ΔG{S} by county with the trend against log population ({v('size.slope','pt2')} points per tenfold population, r = {v('size.r','f2')}). Red: {top}, the ceiling. Orange: the five lowest ΔG ({v('bottom5','list')}).*

## 4. Stacked share bars with registration loss

![Democratic vote share with gain stacked, registered-Democrat loss below, by population](NM_Stacked_Share_Reg_Loss_by_Population.png)

*Blue: 2022 Democratic share of ballots cast. Amber stacked on top: the 2022 to 2026{S} gain. Dotted outline: where the share fell. Navy below zero (right axis, head count): the drop in registered Democrats. Democratic share rose in {v('n_S_rose','int')} counties; registered Democrats fell in {v('n_reg_fell','int')}.*

![The same bars sorted by 2022 Democratic share](NM_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png)

*The same bars sorted by 2022 Democratic share, highest to lowest. Floor: {v('lowest_S22_county','raw')} (lowest 2022 share). Ceiling: {top} (highest ΔG).*

## Earlier New Mexico charts

Charts from the first New Mexico build, kept for reference. They use the same verified 33-county table and the same ballots-cast denominator.

- [G by county, 2022 vs 2026{S}](nm_gap_2022_vs_2026.png)
- [ΔG by county](nm_delta_g_bars.png)
- [Slope chart, first version](nm_slope_G2022_to_G2026.png)
- [Registration-share drop against vote-share change](nm_scatter_regdrop_vs_sharechange.png), with its [residual bars](nm_residual_bars.png) and [implied extra votes](nm_implied_extra_votes.png) (a separate change-against-drop model, not the expected-loss layer on [Reverse Math](Reverse-Math))
- [Surplus S against D/100 with the Locked fit lines](nm_share_scatter_S_vs_D.png) and [the 2026{S} fit residuals by county](nm_share_residual_bars_2026.png)

{related('Graphs')}"""
write(R,'Graphs.md',body); print('graphs ok')
