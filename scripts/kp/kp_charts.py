"""Kansas-parity chart set for New Mexico (ballots-cast denominator), drawn only from verified pass-A keys through the registry
(every plotted value and every label is logged and re-checked against pass B by kp_check_pages.py)."""
import numpy as np, matplotlib, json
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from kpfmt import Reg
R=Reg('charts'); W='/workspace/nm-election/wiki/'
names=R.raw('counties_pop_order'); cap=R.raw('ceiling5'); flo=R.raw('floor.counties'); bot=R.raw('bottom5'); nonloss=R.raw('nonloss.counties')
for k in ('ceiling5','floor.counties','bottom5','nonloss.counties','counties_pop_order'): R.v(k,'list')
g=lambda c,k:R.use(f'c.{c}.{k}')
NOTE='*2026 UNOFFICIAL: New Mexico SOS "Unofficial Results" (last updated 11/12/2026 11:07 AM MT); State Canvassing Board certification pending. 2022 SOS official.'
OR='#e8590c'; BL='#1f5fbf'; GR='#bbbbbb'
# 1 slope
fig,ax=plt.subplots(figsize=(10,12))
for c in names:
    if c in cap or c in flo: continue
    ax.plot([0,1],[g(c,'G22'),g(c,'G26')],color=GR,lw=0.9,zorder=1)
for c in flo:
    ax.plot([0,1],[g(c,'G22'),g(c,'G26')],color=BL,lw=2.4,marker='o',ms=4,zorder=2)
for c in cap:
    ax.plot([0,1],[g(c,'G22'),g(c,'G26')],color=OR,lw=3,marker='o',zorder=3,ls='-' if c not in flo else (0,(4,2)))
def stack(items,gap):
    items=sorted(items,key=lambda t:t[1]); ys=[t[1] for t in items]
    for k in range(1,len(ys)): ys[k]=max(ys[k],ys[k-1]+gap)
    return [(t[0],y) for t,y in zip(items,ys)]
for c,y in stack([(c,g(c,'G26')) for c in cap],1.3):
    ax.text(1.03,y,f"{c} {R.v(f'c.{c}.dG','pt2')} pts"+(' (also floor)' if c in flo else ''),va='center',color='#b02a00',fontweight='bold',fontsize=10)
for c,y in stack([(c,g(c,'G22')) for c in flo],1.3):
    ax.text(-0.03,y,f"{c} {R.v(f'c.{c}.dG','pt2')} pts",va='center',ha='right',color='#1f4e9a',fontweight='bold',fontsize=10)
ax.set_xticks([0,1]); ax.set_xticklabels(['2022 (official)','2026* (unofficial)'],fontsize=12); ax.set_xlim(-0.55,1.6)
ax.set_ylabel('G = Dem share of ballots cast − Dem registration share (points)')
ax.set_title('New Mexico G 2022 to G 2026* — County Slope Chart\nGovernor race; 33 counties. Orange: 5 ceiling counties (largest ΔG). Blue: floor counties\n(most Republican baseline; Lea and De Baca are both, dashed). Labels show ΔG = G2026* − G2022.',fontsize=12)
ax.grid(axis='y',alpha=0.3); fig.text(0.01,0.01,NOTE,fontsize=7.5)
plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(W+'NM_Slope_G2022_to_G2026_County_Slope_Chart.png',dpi=150); plt.close()
# 2 forward fit
fig,axs=plt.subplots(1,2,figsize=(14,6.5),sharey=True)
for ax,y,lab in ((axs[0],'22','2022 (official)'),(axs[1],'26','2026* (unofficial)')):
    fk='fit.20'+y; m=R.use(fk+'.m'); b=R.use(fk+'.b'); sd=R.use(fk+'.resid_sd')
    x=np.array([g(c,'R'+y) for c in names]); s=np.array([g(c,'G'+y) for c in names])
    ax.scatter(x,s,s=20,color='#888',zorder=2)
    ax.scatter([g(c,'R'+y) for c in cap],[g(c,'G'+y) for c in cap],s=44,color=OR,zorder=3,label='ceiling (top-5 ΔG)')
    ax.scatter([g(c,'R'+y) for c in flo],[g(c,'G'+y) for c in flo],s=30,color=BL,zorder=4,label='floor (most Republican baseline)')
    xx=np.linspace(x.min(),x.max(),50); ax.plot(xx,m*xx/100+b,color='black',lw=1.6,label=f"fit: S = {R.v(fk+'.m','f2')}·(D/100) {R.v(fk+'.b','pt2')}".replace('+','+ ').replace('·(D/100) -','·(D/100) − '))
    ax.fill_between(xx,m*xx/100+b-sd,m*xx/100+b+sd,color='#999',alpha=0.15,label=f"±1 residual SD ({R.v(fk+'.resid_sd','f2')} pts)")
    for c in cap: ax.annotate(c,(g(c,'R'+y),g(c,'G'+y)),xytext=(4,3),textcoords='offset points',fontsize=8,color='#b02a00')
    ax.set_title(f"{lab}: R² = {R.v(fk+'.r2','f3')}, n = 33",fontsize=11); ax.set_xlabel('D = Democratic registration share (%)'); ax.grid(alpha=0.3); ax.legend(fontsize=8,loc='upper right')
axs[0].set_ylabel('S = Dem share of ballots − Dem registration share (points)')
fig.suptitle('New Mexico forward surplus fit, least squares across 33 counties (ballots-cast denominator, both years)',fontsize=12)
fig.text(0.01,0.01,NOTE,fontsize=8); plt.tight_layout(rect=(0,0.03,1,0.96)); plt.savefig(W+'NM_Forward_Surplus_Fit_S_vs_D.png',dpi=140); plt.close()
# 3a dG bars by population with constants
fig,ax=plt.subplots(figsize=(16,6.5))
cols=[OR if c in cap else (BL if c in flo else '#999') for c in names]
hat=['//' if (c in cap and c in flo) else '' for c in names]
dg=[g(c,'dG') for c in names]
bars=ax.bar(range(33),dg,color=cols,edgecolor=['#1f4e9a' if h else 'none' for h in hat],hatch=None)
for bb,h in zip(bars,hat):
    if h: bb.set_hatch(h)
for i,c in enumerate(names):
    if c in cap: ax.text(i,dg[i]+0.25,R.v(f'c.{c}.dG','pt2'),ha='center',fontsize=8,color='#b02a00',fontweight='bold')
med=R.use('dG.median'); fc=R.use('floor.median'); cc=R.use('ceil3.median')
ax.axhline(med,color='#555',ls='--',lw=1,label=f"County median ΔG {R.v('dG.median','pt2')} (mean {R.v('dG.mean','pt2')})")
ax.axhline(fc,color=BL,ls=':',lw=1.4,label=f"Floor constant (median ΔG of {len(flo)} floor counties) {R.v('floor.median','pt2')}")
ax.axhline(cc,color='#b02a00',ls=':',lw=1.4,label=f"Ceiling constant (median ΔG of {', '.join(R.raw('ceil3.counties'))}) {R.v('ceil3.median','pt2')}")
ax.set_xticks(range(33)); ax.set_xticklabels([f"{c} {R.v(f'c.{c}.population','int')}" for c in names],rotation=90,fontsize=8)
ax.set_ylabel('ΔG = G2026* − G2022 (points)'); ax.set_title('New Mexico governor ΔG by county, largest to smallest population (ballots-cast denominator both years)',fontweight='bold')
h,l=ax.get_legend_handles_labels(); h+= [Patch(color=OR,label='Ceiling counties: 5 largest ΔG'),Patch(color=BL,label='Floor counties: most Republican baseline'),Patch(facecolor=OR,edgecolor=BL,hatch='//',label='Both ceiling and floor (Lea, De Baca)')]
ax.legend(handles=h,fontsize=8,loc='upper right'); ax.margins(x=0.01); ax.set_ylim(0,max(dg)+3)
fig.text(0.01,0.01,NOTE,fontsize=7.5); plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig(W+'NM_DeltaG_Bars_by_Population.png',dpi=130); plt.close()
# 3b scatter with names vs log population
fig,ax=plt.subplots(figsize=(12,7.5))
lp=np.log10([g(c,'population') for c in names]); sl=R.use('size.slope'); ic=R.use('size.intercept'); top=R.raw('dG.max_county'); R.v('dG.max_county','raw')
for i,c in enumerate(names):
    col='#c00000' if c==top else (OR if c in bot else '#555')
    ax.scatter(lp[i],dg[i],color=col,s=40 if col!='#555' else 22,zorder=3)
    ax.annotate(c,(lp[i],dg[i]),xytext=(4,3),textcoords='offset points',fontsize=8,color=col)
xx=np.linspace(lp.min(),lp.max(),20); ax.plot(xx,ic+sl*xx,color='black',lw=1.4,label=f"trend: {R.v('size.slope','pt2')} points per tenfold population (r = {R.v('size.r','f2')}, p = {R.v('size.p','p')})")
ax.set_xlabel('County population (log scale, Census July 1, 2025)'); ax.set_ylabel('ΔG* (points)')
ax.set_xticks([3,4,5,6]); ax.set_xticklabels(['1,000','10,000','100,000','1,000,000'])
ax.legend(handles=ax.get_legend_handles_labels()[0]+[Line2D([],[],marker='o',ls='',color='#c00000',label=f'{top}: highest ΔG (ceiling)'),Line2D([],[],marker='o',ls='',color=OR,label='five lowest ΔG')],fontsize=9,loc='lower left')
ax.set_title('New Mexico ΔG* by county against population',fontweight='bold'); ax.grid(alpha=0.3)
fig.text(0.01,0.01,NOTE,fontsize=7.5); plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig(W+'NM_DeltaG_by_Population_Scatter_Names.png',dpi=130); plt.close()
# 4 stacked share bars with registration loss (two sorts)
def stacked(order,fname,title,sub):
    fig,ax=plt.subplots(figsize=(18,8)); ax2=ax.twinx()
    for i,c in enumerate(order):
        s22=g(c,'S22'); s26=g(c,'S26')
        if s26>=s22:
            ax.bar(i,s22,color='#3a6fd8'); ax.bar(i,s26-s22,bottom=s22,color='#f2a516')
        else:
            ax.bar(i,s26,color='#3a6fd8'); ax.bar(i,s22-s26,bottom=s26,color='none',edgecolor='#3a6fd8',ls=':',lw=1)
        rc=g(c,'reg_change')
        if rc<0: ax2.bar(i,rc,color='#0b1f4d',width=0.55)
    ax.set_ylim(-60,100); ax.axhline(0,color='black',lw=0.8)
    mn=min(R.use(f'c.{c}.reg_change') for c in order); lo=mn*1.08; ax2.set_ylim(lo,-lo*100/60)   # zero aligned with the left axis (-60..100)
    ax2.set_yticks([t for t in ax2.get_yticks() if t<=0])
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order,rotation=90,fontsize=8)
    ax.set_ylabel('Democratic share of ballots cast (%); bar above 0 = 2026* share'); ax2.set_ylabel('Change in registered Democrats, 2022→2026 (count, below 0)')
    ax.set_title(title,fontweight='bold')
    ax.legend(handles=[Patch(color='#3a6fd8',label='2022 Democratic share (2026 share where it fell)'),Patch(color='#f2a516',label='Gain in Democratic share 2022→2026*'),Patch(facecolor='none',edgecolor='#3a6fd8',ls=':',label='Drop in Democratic share (dotted, top = 2022)'),Patch(color='#0b1f4d',label='Loss of registered Democrats 2022→2026 (count, right axis)')],fontsize=8,loc='upper right')
    fig.text(0.01,0.01,sub+' '+NOTE,fontsize=7.5); plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig(W+fname,dpi=120); plt.close()
stacked(names,'NM_Stacked_Share_Reg_Loss_by_Population.png','New Mexico governor race: Democratic share gain (above 0) vs. loss of registered Democrats (below 0), 2022→2026* (largest to smallest population)','Share = Dem governor votes ÷ ballots cast × 100. Navy bars only where registered Democrats fell.')
o2=sorted(names,key=lambda c:-R.use(f'c.{c}.S22'))
stacked(o2,'NM_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png','New Mexico governor race: the same bars sorted by 2022 Democratic share, highest to lowest','Share = Dem governor votes ÷ ballots cast × 100. Navy bars only where registered Democrats fell.')
# 5 expected-loss residual bars
fig,ax=plt.subplots(figsize=(16,6.5))
rs=[g(c,'residual') for c in names]
bars=ax.bar(range(33),rs,color=[OR if c in cap else (BL if c in flo else '#999') for c in names])
for bb,c in zip(bars,names):
    if c in nonloss: bb.set_hatch('xx'); bb.set_edgecolor('black')
ax.axhline(0,color='black',lw=0.8)
ax.set_xticks(range(33)); ax.set_xticklabels(names,rotation=90,fontsize=8)
ax.set_ylabel('Residual = ΔG − expected loss (points)\n= change in Dem share of ballots cast')
ax.set_title('New Mexico residual after the expected registration loss, by county (largest to smallest population)',fontweight='bold')
ax.legend(handles=[Patch(color=OR,label='Ceiling counties (5 largest ΔG)'),Patch(color=BL,label='Floor counties'),Patch(facecolor='white',edgecolor='black',hatch='xx',label='Non-loss counties (registered Democrats did not fall)')],fontsize=8)
fig.text(0.01,0.01,NOTE,fontsize=7.5); plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig(W+'NM_Expected_Loss_Residual_Bars_by_Population.png',dpi=130); plt.close()
# Resources chart A: 2022 share vs gain, sorted by 2022 share
fig,ax=plt.subplots(figsize=(18,7))
for i,c in enumerate(o2):
    s22=g(c,'S22'); d=g(c,'dS')
    ax.bar(i,s22,color='#4472C4')
    ax.bar(i,d,bottom=s22 if d>=0 else 0,color='#ED7D31' if d>=0 else '#C00000')
ax.axhline(0,color='black',lw=0.8); ax.set_xticks(range(33)); ax.set_xticklabels(o2,rotation=90,fontsize=8)
ax.set_ylabel('Democratic share of ballots cast (%) / change (points)')
ax.set_title(f"New Mexico: 2022 Democratic share and the 2022→2026* change, sorted by 2022 share (share rose in {R.v('n_S_rose','int')} counties, fell in {R.v('n_S_fell','int')})",fontweight='bold')
ax.legend(handles=[Patch(color='#4472C4',label='2022 Democratic share'),Patch(color='#ED7D31',label='Gain 2022→2026*'),Patch(color='#C00000',label='Decline (below zero)')],fontsize=9)
fig.text(0.01,0.01,NOTE,fontsize=7.5); plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig(W+'NM_governor_2022_Dem_share_vs_gain_bar_chart.png',dpi=130); plt.close()
# Resources chart B: ceiling counties highlighted, by population
fig,ax=plt.subplots(figsize=(18,7))
ax.bar(range(33),dg,color=['#C55A11' if c in cap else '#9DC3E6' for c in names])
for i,c in enumerate(names):
    if c in cap: ax.annotate(f"{c} {R.v(f'c.{c}.dG','pt2')}*",(i,dg[i]),xytext=(0,6),textcoords='offset points',ha='center',fontsize=9,color='#C00000',fontweight='bold',bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='#C00000'))
ax.set_xticks(range(33)); ax.set_xticklabels(names,rotation=90,fontsize=8); ax.set_ylabel('ΔG (percentage points)'); ax.set_ylim(0,max(dg)+3)
ax.set_title('New Mexico 2026* ΔG by population: ceiling counties highlighted\nGovernor race, 2022 vs 2026, all 33 counties, largest to smallest population',fontweight='bold')
fig.text(0.01,0.01,'G = (Dem governor votes ÷ ballots cast × 100) − (Dem registered ÷ total registered × 100). ΔG = G2026 − G2022. '+NOTE,fontsize=7.5)
plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig(W+'NM_Ceiling_Counties_DeltaG_by_Population.png',dpi=130); plt.close()
R.save('charts'); print('charts built; logged',len(R.log))
