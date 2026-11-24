import csv, json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
O='/workspace/nm-election/out'; W='/workspace/nm-election/wiki'
rows=list(csv.DictReader(open(f'{O}/nm_county_table_fullprecision.csv')))
S=json.load(open(f'{O}/nm_summary.json')); b,m,r2=S['constant'],S['multiplier'],S['r2']
f=lambda k:np.array([float(r[k]) for r in rows]); names=[r['county'] for r in rows]
note='*2026 = UNOFFICIAL NM SOS results (not certified). Governor race. Source: NM Secretary of State; Census V2025 population.'
# 1 scatter
x,y=f('drop'),f('dS'); fig,ax=plt.subplots(figsize=(11,7.5))
sz=np.sqrt(f('population'))/4
ax.scatter(x,y,s=sz,alpha=.6,color='#2b6cb0',edgecolor='k',linewidth=.4)
xx=np.linspace(x.min()-.3,x.max()+.3,50); ax.plot(xx,b+m*xx,color='#c53030',lw=2,label=f'Fit: change = {b:+.2f} + ({m:.3f}) x drop   R² = {r2:.3f}')
for xi,yi,n in zip(x,y,names): ax.annotate(n,(xi,yi),fontsize=7,xytext=(3,3),textcoords='offset points')
ax.axhline(0,color='gray',lw=.6); ax.set_xlabel('Democratic registration-share drop, 2022 to 2026 (points)  [R2022 - R2026]')
ax.set_ylabel('Change in Democratic share of ballots cast, 2022 to 2026* (points)')
ax.set_title('New Mexico, 33 counties: Dem vote-share change vs Dem registration-share drop (2026* unofficial)'); ax.legend(loc='upper right')
fig.text(.01,.01,note,fontsize=7.5); fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(f'{W}/nm_scatter_regdrop_vs_sharechange.png',dpi=130); plt.close(fig)
# 2 residual bars by population
res=f('residual'); fig,ax=plt.subplots(figsize=(12,7))
ax.bar(range(33),res,color=['#c53030' if v>0 else '#2b6cb0' for v in res]); ax.set_xticks(range(33)); ax.set_xticklabels(names,rotation=70,fontsize=8)
ax.axhline(0,color='k',lw=.6); ax.set_ylabel('Residual = actual share change - fitted expectation (points)')
ax.set_title('Residual after subtracting the fitted registration-decline expectation, by county (largest to smallest population), 2026*')
fig.text(.01,.01,note,fontsize=7.5); fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(f'{W}/nm_residual_bars.png',dpi=130); plt.close(fig)
# 3 implied extra votes
iv=f('implied'); fig,ax=plt.subplots(figsize=(12,7))
ax.bar(range(33),iv,color=['#c53030' if v>0 else '#2b6cb0' for v in iv]); ax.set_xticks(range(33)); ax.set_xticklabels(names,rotation=70,fontsize=8)
ax.axhline(0,color='k',lw=.6); ax.set_ylabel('Implied extra Democratic votes, 2026* (residual x ballots cast 2026)')
ax.set_title('Implied extra votes solved backward from the residual (signed), by county, largest to smallest population, 2026*')
fig.text(.01,.01,note,fontsize=7.5); fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(f'{W}/nm_implied_extra_votes.png',dpi=130); plt.close(fig)
# 4 gap G 2022 vs 2026
g22,g26=f('G22'),f('G26'); fig,ax=plt.subplots(figsize=(12,7)); i=np.arange(33)
ax.bar(i-.2,g22,.4,label='G 2022 (official)',color='#a0aec0'); ax.bar(i+.2,g26,.4,label='G 2026* (unofficial)',color='#dd6b20')
ax.set_xticks(i); ax.set_xticklabels(names,rotation=70,fontsize=8); ax.axhline(0,color='k',lw=.6); ax.legend()
ax.set_ylabel('Gap G = Dem share of ballots - Dem share of registration (points)'); ax.set_title('Gap G by county, 2022 vs 2026* (largest to smallest population)')
fig.text(.01,.01,note,fontsize=7.5); fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(f'{W}/nm_gap_2022_vs_2026.png',dpi=130); plt.close(fig)
# 5 delta-G bars
dg=f('dG'); fig,ax=plt.subplots(figsize=(12,7))
ax.bar(range(33),dg,color='#805ad5'); ax.set_xticks(range(33)); ax.set_xticklabels(names,rotation=70,fontsize=8)
ax.set_ylabel('Delta-G = share change - registration-share change (points)'); ax.set_title('Delta-G by county, 2022 to 2026* (largest to smallest population)')
fig.text(.01,.01,note,fontsize=7.5); fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(f'{W}/nm_delta_g_bars.png',dpi=130); plt.close(fig)
print('charts ok')
# ---- share version charts: surplus S (=G) vs D/100, and share-version residuals
SH=json.load(open(f'{O}/nm_share_fit.json')); s26=SH['raw']['y2026']; s22=SH['raw']['y2022']
srows=list(csv.DictReader(open(f'{O}/nm_share_fit_fullprecision.csv')))
g=lambda k:np.array([float(r[k]) for r in srows]); sn=[r['county'] for r in srows]
fig,ax=plt.subplots(figsize=(11,7.5))
d26,S26=g('R26')/100,g('G26'); d22,S22=g('R22')/100,g('G22')
ax.scatter(d22,S22,s=18,color='#a0aec0',alpha=.8,label='2022 counties (official)')
ax.scatter(d26,S26,s=np.sqrt(f('population'))/4,color='#dd6b20',edgecolor='k',linewidth=.4,alpha=.75,label='2026* counties (unofficial)')
xx=np.linspace(min(d22.min(),d26.min())-.02,max(d22.max(),d26.max())+.02,50)
ax.plot(xx,s26['b']+s26['m']*xx,color='#c05621',lw=2.2,label=f"2026* fit: S = {s26['m']:.2f} x (D/100) {s26['b']:+.2f}   R² = {s26['r2']:.3f}")
ax.plot(xx,s22['b']+s22['m']*xx,color='#718096',lw=1.4,ls='--',label=f"2022 fit: S = {s22['m']:.2f} x (D/100) {s22['b']:+.2f}   R² = {s22['r2']:.3f}")
for xi,yi,n in zip(d26,S26,sn): ax.annotate(n,(xi,yi),fontsize=7,xytext=(3,3),textcoords='offset points')
ax.axhline(0,color='gray',lw=.6); ax.set_xlabel('D/100 = Democratic registration share (fraction, SOS pre-election report)')
ax.set_ylabel('S = surplus = Dem share of ballots cast - Dem registration share (points)')
ax.set_title('Share version of the Locked NM formula: S = m x (D/100) + b, 33 counties (2026* unofficial)'); ax.legend(loc='lower left',fontsize=8.5)
fig.text(.01,.01,note,fontsize=7.5); fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(f'{W}/nm_share_scatter_S_vs_D.png',dpi=130); plt.close(fig)
r26=g('shres26'); fig,ax=plt.subplots(figsize=(12,7))
ax.bar(range(33),r26,color=['#c53030' if v>0 else '#2b6cb0' for v in r26]); ax.set_xticks(range(33)); ax.set_xticklabels(sn,rotation=70,fontsize=8)
ax.axhline(0,color='k',lw=.6); ax.set_ylabel('Share-version residual 2026* = S - (m x D/100 + b) (points)')
ax.set_title(f"Share-version residuals, 2026* (m = {s26['m']:.2f}, b = {s26['b']:+.2f}; mean |residual| = {s26['mae']:.2f}), largest to smallest population")
fig.text(.01,.01,note,fontsize=7.5); fig.tight_layout(rect=(0,.03,1,1)); fig.savefig(f'{W}/nm_share_residual_bars_2026.png',dpi=130); plt.close(fig)
print('share charts ok')
# ---- Nebraska-style chart 1: county slope chart G 2022 -> G 2026*
fig,ax=plt.subplots(figsize=(8,10))
_o=np.argsort(f('dG')); _bot=set(_o[:5]); _top=set(_o[-5:])
for i,(n,a,b2) in enumerate(zip(names,f('G22'),f('G26'))):
    col='#c53030' if i in _top else ('#2b6cb0' if i in _bot else '#a0aec0')
    ax.plot([0,1],[a,b2],color=col,lw=1.6 if col!='#a0aec0' else .9,alpha=.9)
    ax.annotate(n,(1,b2),xytext=(4,0),textcoords='offset points',fontsize=6.5,va='center')
ax.set_xticks([0,1]); ax.set_xticklabels(['G 2022 (official)','G 2026* (unofficial)']); ax.set_xlim(-.1,1.35)
ax.axhline(0,color='k',lw=.5); ax.set_ylabel('G = Dem share of ballots - Dem registration share (points)')
ax.set_title('County slope chart, G 2022 to G 2026*\n(red = top-5 Delta-G, blue = bottom-5 Delta-G)')
fig.text(.01,.005,note,fontsize=6.5); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(f'{W}/nm_slope_G2022_to_G2026.png',dpi=130); plt.close(fig)
print('slope chart ok')
