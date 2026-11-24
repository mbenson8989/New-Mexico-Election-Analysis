"""KANSAS-PARITY METRICS, PASS A (pandas / numpy / statsmodels / scipy).
Input: out/nm_county_table_fullprecision.csv, written by pipeline.py from the PASS-1 raw parse (SOS governor county export,
SOS turnout page precinct rows, SOS registration PDFs via pypdf, Census csv). Only the raw COUNTS are used; every share is recomputed here.
Output: verification/kp_passA.json (flat dict of named values, full precision) and out/kp_counties_A.csv.
Definitions follow the Kansas wiki (scripts/analysis.py, resid_pass_a.py, flip/build_flip.py) with New Mexico's ballots-cast denominator:
  S = 100*Dem gov votes/ballots cast; R (= D in the fit) = 100*Dem reg/total reg; G = S - R; dG = G26 - G22
  expected loss = R22 - R26; residual = dG - expected loss (= S26 - S22); offset votes = residual/100*ballots26
  gap in votes = D26 - D22*(RegDem26/RegDem22); NE residual votes = ballots26*dG/100
  floor counties: S22 <= 10th pct AND G22 <= 25th pct (linear interpolation); ceiling = 5 largest dG
  ceiling constant = median dG of the 3 largest counties by population; six-county version = 6 largest."""
import pandas as pd, numpy as np, json, statsmodels.api as sm
from scipy import stats
B='/workspace/nm-election/'
t=pd.read_csv(B+'out/nm_county_table_fullprecision.csv')
cnt=['population','dem22','rep22','ballots22','allgov22','dem26','rep26','ballots26','allgov26','regdem22','regtot22','regdem26','regtot26']
o=t[['county']+cnt].copy()
for c in cnt: o[c]=o[c].astype('int64')
o=o.sort_values('population',ascending=False).set_index('county')
assert len(o)==33
o['S22']=100*o.dem22/o.ballots22; o['S26']=100*o.dem26/o.ballots26
o['R22']=100*o.regdem22/o.regtot22; o['R26']=100*o.regdem26/o.regtot26
o['G22']=o.S22-o.R22; o['G26']=o.S26-o.R26; o['dG']=o.G26-o.G22; o['dS']=o.S26-o.S22; o['dR']=o.R26-o.R22
o['exp_loss']=o.R22-o.R26; o['residual']=o.dG-o.exp_loss
o['offset_votes']=o.residual/100*o.ballots26
assert np.allclose(o.offset_votes,o.dem26-o.S22/100*o.ballots26) and np.allclose(o.residual,o.dS)
o['gap_votes']=o.dem26-o.dem22*o.regdem26/o.regdem22
o['ne_resid_votes']=o.ballots26*o.dG/100
o['reg_change']=o.regdem26-o.regdem22; o['reg_pct']=100*o.reg_change/o.regdem22
o['vote_change']=o.dem26-o.dem22; o['vote_pct']=100*o.vote_change/o.dem22
o['ballot_change']=o.ballots26-o.ballots22; o['ballot_pct']=100*o.ballot_change/o.ballots22
o['nonloss']=o.regdem26>=o.regdem22
for y in ('22','26'):
    o['DR'+y]=o['dem'+y]+o['rep'+y]
    o['nogov'+y]=100*(o['ballots'+y]-o['allgov'+y])/o['ballots'+y]
    o['spare'+y]=o['ballots'+y]-o['DR'+y]
V={}
def put(k,v): V[k]=v
names=list(o.index)
put('counties_pop_order',names)
for c in names:
    r=o.loc[c]
    for k in ['population','dem22','rep22','ballots22','allgov22','dem26','rep26','ballots26','allgov26','regdem22','regtot22','regdem26','regtot26','reg_change','vote_change','ballot_change','DR22','DR26','spare22','spare26']:
        put(f'c.{c}.{k}',int(r[k]))
    for k in ['S22','S26','R22','R26','G22','G26','dG','dS','dR','exp_loss','residual','offset_votes','gap_votes','ne_resid_votes','reg_pct','vote_pct','ballot_pct','nogov22','nogov26']:
        put(f'c.{c}.{k}',float(r[k]))
    put(f'c.{c}.nonloss',bool(r.nonloss))
# ---- statewide
T={k:int(o[k].sum()) for k in cnt}
for k,v in T.items(): put('sw.'+k,v)
sw=dict(S22=100*T['dem22']/T['ballots22'],S26=100*T['dem26']/T['ballots26'],R22=100*T['regdem22']/T['regtot22'],R26=100*T['regdem26']/T['regtot26'])
sw['G22']=sw['S22']-sw['R22']; sw['G26']=sw['S26']-sw['R26']; sw['dG']=sw['G26']-sw['G22']; sw['dS']=sw['S26']-sw['S22']; sw['dR']=sw['R26']-sw['R22']
for k,v in sw.items(): put('sw.'+k,float(v))
for a,b_ in (('regdem','regdem'),('regtot','regtot'),('dem','dem'),('rep','rep'),('ballots','ballots'),('allgov','allgov')):
    put(f'sw.{a}_change',T[a+'26']-T[a+'22']); put(f'sw.{a}_pct',100*(T[a+'26']-T[a+'22'])/T[a+'22'])
# ---- county distribution of dG
put('dG.median',float(o.dG.median())); put('dG.mean',float(o.dG.mean())); put('dG.sd',float(o.dG.std()))
put('dG.n_pos',int((o.dG>0).sum())); put('dG.n_neg',int((o.dG<0).sum()))
put('dG.min_county',o.dG.idxmin()); put('dG.max_county',o.dG.idxmax())
put('n_S_rose',int((o.S26>o.S22).sum())); put('n_S_fell',int((o.S26<o.S22).sum()))
put('n_reg_fell',int((o.regdem26<o.regdem22).sum())); put('n_regshare_fell',int((o.R26<o.R22).sum()))
put('n_votes_rose',int((o.dem26>o.dem22).sum()))
top5=o.dG.sort_values(ascending=False).head(5); bot5=o.dG.sort_values().head(5)
put('ceiling5',list(top5.index)); put('bottom5',list(bot5.index))
q10=float(o.S22.quantile(.10)); q25=float(o.G22.quantile(.25))
FL=o[(o.S22<=q10)&(o.G22<=q25)].sort_values('S22')
put('floor.q10_S22',q10); put('floor.q25_G22',q25); put('floor.counties',list(FL.index))
put('floor.median',float(FL.dG.median())); put('floor.mean',float(FL.dG.mean()))
put('lowest_S22_county',o.S22.idxmin()); put('lowest_G22_county',o.G22.idxmin())
C3=names[:3]; C6=names[:6]
put('ceil3.counties',C3); put('ceil6.counties',C6)
put('ceil3.median',float(o.loc[C3].dG.median())); put('ceil3.mean',float(o.loc[C3].dG.mean()))
put('ceil6.median',float(o.loc[C6].dG.median())); put('ceil6.mean',float(o.loc[C6].dG.mean()))
put('nonloss.counties',[c for c in names if o.loc[c,'nonloss']])
put('regfell_votesfell',[c for c in names if o.loc[c,'regdem26']<o.loc[c,'regdem22'] and o.loc[c,'dem26']<o.loc[c,'dem22']])
lr=stats.linregress(np.log10(o.population),o.dG)
put('size.slope',float(lr.slope)); put('size.intercept',float(lr.intercept)); put('size.r',float(lr.rvalue)); put('size.r2',float(lr.rvalue**2)); put('size.p',float(lr.pvalue))
# ---- groups (Kansas Step 3)
def pooled(idx,pref):
    s=o.loc[idx]; S22=100*s.dem22.sum()/s.ballots22.sum(); S26=100*s.dem26.sum()/s.ballots26.sum(); R22=100*s.regdem22.sum()/s.regtot22.sum(); R26=100*s.regdem26.sum()/s.regtot26.sum()
    for k,v in dict(S22=S22,S26=S26,R22=R22,R26=R26,dS=S26-S22,dR=R26-R22,dG=(S26-R26)-(S22-R22),med=s.dG.median(),lo=s.dG.min(),hi=s.dG.max(),n=len(s)).items():
        put(f'grp.{pref}.{k}',float(v) if k!='n' else int(v))
pooled(C6,'six'); pooled([c for c in names if c not in C6],'other'); pooled(names,'all')
# ---- forward surplus fit S(=G) = m*(D/100)+b  (Kansas 'state-only constants')
def fit(y,x):
    X=sm.add_constant(np.asarray(x,float)/100); r=sm.OLS(np.asarray(y,float),X).fit(); res=np.asarray(y,float)-r.fittedvalues; ci=r.conf_int()
    return dict(n=int(len(y)),m=float(r.params[1]),m_se=float(r.bse[1]),m_lo=float(ci[1,0]),m_hi=float(ci[1,1]),b=float(r.params[0]),b_se=float(r.bse[0]),b_lo=float(ci[0,0]),b_hi=float(ci[0,1]),
        r2=float(r.rsquared),resid_sd=float(np.sqrt(np.sum(res**2)/(len(y)-2))),mae=float(np.mean(np.abs(res))),w2=int(np.sum(np.abs(res)<=2)),w5=int(np.sum(np.abs(res)<=5))),res
F22,res22=fit(o.G22,o.R22); F26,res26=fit(o.G26,o.R26); FP,_=fit(np.r_[o.G22,o.G26],np.r_[o.R22,o.R26])
for nm,F in (('2022',F22),('2026',F26),('pooled',FP)):
    for k,v in F.items(): put(f'fit.{nm}.{k}',v)
o['fit_res22']=res22; o['fit_res26']=res26
Xp=np.c_[np.ones(66),np.r_[o.R22,o.R26]/100,np.r_[np.zeros(33),np.ones(33)],np.r_[np.zeros(33),o.R26/100]]
rp=sm.OLS(np.r_[o.G22,o.G26],Xp).fit()
put('fit.int.d_b',float(rp.params[2])); put('fit.int.p_d_b',float(rp.pvalues[2])); put('fit.int.d_m',float(rp.params[3])); put('fit.int.p_d_m',float(rp.pvalues[3]))
put('fit.2022.at40',F22['m']*0.40+F22['b']); put('fit.2026.at40',F26['m']*0.40+F26['b'])
# ---- expected-loss layer
put('el.median_res',float(o.residual.median())); put('el.mean_res',float(o.residual.mean())); put('el.sd_res',float(o.residual.std()))
put('el.n_pos',int((o.residual>0).sum())); put('el.n_neg',int((o.residual<0).sum()))
put('el.sw_exp_loss',sw['R22']-sw['R26']); put('el.sw_residual',sw['S26']-sw['S22'])
N=T['ballots26']; p=sw['S26']/100; s0=(sw['R22']-sw['R26'])/100
put('el.pooled_votes',(sw['S26']-sw['S22'])/100*N)
put('el.county_sum',float(o.offset_votes.sum()))
put('el.sum_loss',float(o.offset_votes[~o.nonloss].sum())); put('el.sum_nonloss',float(o.offset_votes[o.nonloss].sum()))
put('el.raw_rise',T['dem26']-T['dem22']); put('el.turnout_part',(T['dem26']-T['dem22'])-(sw['S26']-sw['S22'])/100*N)
for k,a in (('0',0),('1',.01),('2',.02)):
    put(f'el.need{k}.switched',(s0+a)*N); put(f'el.need{k}.added',(s0+a)*N/(1-p+s0+a))
put('el.gap_sum',float(o.gap_votes.sum())); put('el.ne_resid_sum',float(o.ne_resid_votes.sum()))
above=o.S22>sw['S22']
put('el.above_share_ballots22',100*o.ballots22[above].sum()/T['ballots22']); put('el.above_share_ballots26',100*o.ballots26[above].sum()/T['ballots26']); put('el.n_above',int(above.sum()))
X=np.c_[np.ones(33),o.exp_loss]; beta,*_=np.linalg.lstsq(X,o.dG.values,rcond=None); e=o.dG.values-X@beta
se=np.sqrt(np.diag(e@e/31*np.linalg.inv(X.T@X))); r2=1-e@e/((o.dG-o.dG.mean())**2).sum()
put('el.regfit.a',float(beta[0])); put('el.regfit.b',float(beta[1])); put('el.regfit.b_se',float(se[1])); put('el.regfit.r2',float(r2))
put('el.top5',list(o.residual.sort_values(ascending=False).head(5).index)); put('el.bot5',list(o.residual.sort_values().head(5).index))
put('el.top5_votes',list(o.offset_votes.sort_values(ascending=False).head(5).index)); put('el.bot5_votes',list(o.offset_votes.sort_values().head(5).index))
# ---- ballots-cast check (Texas style), both years
for y in ('22','26'):
    put(f'tx.DR_gt_ballots{y}',[c for c in names if o.loc[c,'DR'+y]>o.loc[c,'ballots'+y]])
    put(f'tx.gov_gt_ballots{y}',[c for c in names if o.loc[c,'allgov'+y]>o.loc[c,'ballots'+y]])
    put(f'tx.ballots_gt_reg{y}',[c for c in names if o.loc[c,'ballots'+y]>o.loc[c,'regtot'+y]])
    put(f'tx.nogov_median{y}',float(o['nogov'+y].median())); put(f'tx.nogov_gt5_{y}',[c for c in names if o.loc[c,'nogov'+y]>5])
    put(f'tx.nogov_max_county{y}',o['nogov'+y].idxmax())
    put(f'sw.nogov{y}',100*(T['ballots'+y]-T['allgov'+y])/T['ballots'+y])
tight=sorted([(int(o.loc[c,'spare'+y]),c,y) for c in names for y in ('22','26')])[:8]
put('tx.tightest',[[c,y] for s,c,y in tight])
# ---- Kansas 'ten counties' (reg Dems fell AND Dem votes rose, ranked by gap in votes)
cand=o[(o.regdem26<o.regdem22)&(o.dem26>o.dem22)]
put('ten.n_candidates',int(len(cand))); ten=list(cand.gap_votes.sort_values(ascending=False).head(10).index); put('ten.counties',ten)
for c in ten: put(f'c.{c}.gap_share_ballots26',float(100*o.loc[c,'gap_votes']/o.loc[c,'ballots26']))
# ---- PDF order (Kansas: 2026 Dem reg share, highest first)
put('pdf.order',list(o.R26.sort_values(ascending=False).index))
put('sw.R26_1dp_check',sw['R26'])
json.dump(V,open(B+'verification/kp_passA.json','w'),indent=0)
o.to_csv(B+'out/kp_counties_A.csv',float_format='%.10f')
print('pass A keys',len(V)); print({k:V[k] for k in ['ceiling5','bottom5','floor.counties','ceil3.median','floor.median','size.slope','ten.counties','ten.n_candidates']})
