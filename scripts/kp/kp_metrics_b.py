"""KANSAS-PARITY METRICS, PASS B. Written separately from kp_metrics_a.py: no pandas, numpy, scipy or statsmodels, no shared code.
Input: verification/pass2_counts.json, the integer counts written by verify_pass2.py from the SECOND-SOURCE SOS files
(66 per-county SOS results pages via html.parser, including the all-candidate governor total; 66 per-county turnout exports via raw
OOXML; registration PDFs via pdfplumber word positions; Census csv by column index).
Arithmetic: exact fractions.Fraction for every share, difference, sum, median and least-squares solve; floats only for log10,
square roots and the Student-t distribution (own continued-fraction incomplete beta)."""
import json, math
from fractions import Fraction as Fr
B='/workspace/nm-election/'
raw=json.load(open(B+'verification/pass2_counts.json'))
names=sorted(raw,key=lambda c:-raw[c]['population'])
assert len(names)==33
H=Fr(100)
c={}
for n in names:
    r=raw[n]; d=dict(r)
    d['S22']=H*r['dem22']/r['ballots22']; d['S26']=H*r['dem26']/r['ballots26']
    d['R22']=H*r['regdem22']/r['regtot22']; d['R26']=H*r['regdem26']/r['regtot26']
    d['G22']=d['S22']-d['R22']; d['G26']=d['S26']-d['R26']; d['dG']=d['G26']-d['G22']; d['dS']=d['S26']-d['S22']; d['dR']=d['R26']-d['R22']
    d['exp_loss']=d['R22']-d['R26']; d['residual']=d['dG']-d['exp_loss']; d['offset_votes']=d['residual']/H*r['ballots26']
    assert d['offset_votes']==r['dem26']-d['S22']/H*r['ballots26']
    d['gap_votes']=r['dem26']-Fr(r['dem22']*r['regdem26'],r['regdem22']); d['ne_resid_votes']=r['ballots26']*d['dG']/H
    d['reg_change']=r['regdem26']-r['regdem22']; d['reg_pct']=H*d['reg_change']/r['regdem22']
    d['vote_change']=r['dem26']-r['dem22']; d['vote_pct']=H*d['vote_change']/r['dem22']
    d['ballot_change']=r['ballots26']-r['ballots22']; d['ballot_pct']=H*d['ballot_change']/r['ballots22']
    d['nonloss']=r['regdem26']>=r['regdem22']
    for y in ('22','26'):
        d['DR'+y]=r['dem'+y]+r['rep'+y]; d['nogov'+y]=H*(r['ballots'+y]-r['allgov'+y])/r['ballots'+y]; d['spare'+y]=r['ballots'+y]-d['DR'+y]
    c[n]=d
V={}
def put(k,v): V[k]=float(v) if isinstance(v,Fr) else v
put('counties_pop_order',names)
INTK=['population','dem22','rep22','ballots22','allgov22','dem26','rep26','ballots26','allgov26','regdem22','regtot22','regdem26','regtot26','reg_change','vote_change','ballot_change','DR22','DR26','spare22','spare26']
FRK=['S22','S26','R22','R26','G22','G26','dG','dS','dR','exp_loss','residual','offset_votes','gap_votes','ne_resid_votes','reg_pct','vote_pct','ballot_pct','nogov22','nogov26']
for n in names:
    for k in INTK: put(f'c.{n}.{k}',int(c[n][k]))
    for k in FRK: put(f'c.{n}.{k}',c[n][k])
    put(f'c.{n}.nonloss',bool(c[n]['nonloss']))
def med(xs):
    s=sorted(xs); m=len(s)
    return s[m//2] if m%2 else (s[m//2-1]+s[m//2])/2
def mean(xs): return sum(xs,Fr(0))/len(xs)
def sd(xs):
    mu=mean(xs); return math.sqrt(sum((x-mu)**2 for x in xs)/(len(xs)-1))
def quant(xs,q):
    s=sorted(xs); pos=(len(s)-1)*Fr(q).limit_denominator(1000); lo=int(pos); fr=pos-lo
    return s[lo] if lo+1>=len(s) else s[lo]+(s[lo+1]-s[lo])*fr
def argmin(key): return min(names,key=lambda n:c[n][key])
def argmax(key): return max(names,key=lambda n:c[n][key])
CK=['population','dem22','rep22','ballots22','allgov22','dem26','rep26','ballots26','allgov26','regdem22','regtot22','regdem26','regtot26']
T={k:sum(raw[n][k] for n in names) for k in CK}
for k in CK: put('sw.'+k,T[k])
sw=dict(S22=H*T['dem22']/T['ballots22'],S26=H*T['dem26']/T['ballots26'],R22=H*T['regdem22']/T['regtot22'],R26=H*T['regdem26']/T['regtot26'])
sw['G22']=sw['S22']-sw['R22']; sw['G26']=sw['S26']-sw['R26']; sw['dG']=sw['G26']-sw['G22']; sw['dS']=sw['S26']-sw['S22']; sw['dR']=sw['R26']-sw['R22']
for k,v in sw.items(): put('sw.'+k,v)
for a in ('regdem','regtot','dem','rep','ballots','allgov'):
    put(f'sw.{a}_change',T[a+'26']-T[a+'22']); put(f'sw.{a}_pct',H*(T[a+'26']-T[a+'22'])/T[a+'22'])
dG=[c[n]['dG'] for n in names]
put('dG.median',med(dG)); put('dG.mean',mean(dG)); put('dG.sd',sd(dG))
put('dG.n_pos',sum(1 for x in dG if x>0)); put('dG.n_neg',sum(1 for x in dG if x<0))
put('dG.min_county',argmin('dG')); put('dG.max_county',argmax('dG'))
put('n_S_rose',sum(1 for n in names if c[n]['S26']>c[n]['S22'])); put('n_S_fell',sum(1 for n in names if c[n]['S26']<c[n]['S22']))
put('n_reg_fell',sum(1 for n in names if raw[n]['regdem26']<raw[n]['regdem22'])); put('n_regshare_fell',sum(1 for n in names if c[n]['R26']<c[n]['R22']))
put('n_votes_rose',sum(1 for n in names if raw[n]['dem26']>raw[n]['dem22']))
put('ceiling5',sorted(names,key=lambda n:-c[n]['dG'])[:5]); put('bottom5',sorted(names,key=lambda n:c[n]['dG'])[:5])
q10=quant([c[n]['S22'] for n in names],Fr(1,10)); q25=quant([c[n]['G22'] for n in names],Fr(1,4))
fl=sorted([n for n in names if c[n]['S22']<=q10 and c[n]['G22']<=q25],key=lambda n:c[n]['S22'])
put('floor.q10_S22',q10); put('floor.q25_G22',q25); put('floor.counties',fl)
put('floor.median',med([c[n]['dG'] for n in fl])); put('floor.mean',mean([c[n]['dG'] for n in fl]))
put('lowest_S22_county',argmin('S22')); put('lowest_G22_county',argmin('G22'))
C3=names[:3]; C6=names[:6]; put('ceil3.counties',C3); put('ceil6.counties',C6)
for nm,L in (('ceil3',C3),('ceil6',C6)):
    put(nm+'.median',med([c[n]['dG'] for n in L])); put(nm+'.mean',mean([c[n]['dG'] for n in L]))
put('nonloss.counties',[n for n in names if c[n]['nonloss']])
put('regfell_votesfell',[n for n in names if raw[n]['regdem26']<raw[n]['regdem22'] and raw[n]['dem26']<raw[n]['dem22']])
# ---- Student t via regularized incomplete beta (Numerical Recipes betacf), own code
def betacf(a,b,x):
    qab=a+b; qap=a+1; qam=a-1; C=1.0; Dd=1-qab*x/qap; Dd=1/(Dd if abs(Dd)>1e-300 else 1e-300); h=Dd
    for m in range(1,500):
        m2=2*m; aa=m*(b-m)*x/((qam+m2)*(a+m2)); Dd=1+aa*Dd; Dd=1/(Dd if abs(Dd)>1e-300 else 1e-300); C=1+aa/C; C=C if abs(C)>1e-300 else 1e-300; h*=Dd*C
        aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2)); Dd=1+aa*Dd; Dd=1/(Dd if abs(Dd)>1e-300 else 1e-300); C=1+aa/C; C=C if abs(C)>1e-300 else 1e-300; de=Dd*C; h*=de
        if abs(de-1)<1e-15: break
    return h
def ibeta(a,b,x):
    if x<=0: return 0.0
    if x>=1: return 1.0
    lb=math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log(1-x)
    return math.exp(lb)*betacf(a,b,x)/a if x<(a+1)/(a+b+2) else 1-math.exp(lb)*betacf(b,a,1-x)/b
def t_two_sided_p(t,df): return ibeta(df/2,0.5,df/(df+t*t))
def t_crit(df,alpha=0.05):
    lo,hi=0.0,50.0
    for _ in range(200):
        mid=(lo+hi)/2
        if t_two_sided_p(mid,df)>alpha: lo=mid
        else: hi=mid
    return (lo+hi)/2
def ols1(x,y):
    n=len(x); mx=mean(x); my=mean(y); sxx=sum((a-mx)**2 for a in x); sxy=sum((a-mx)*(b-my) for a,b in zip(x,y))
    m=sxy/sxx; b=my-m*mx; res=[yy-(b+m*xx) for xx,yy in zip(x,y)]; sse=sum(r*r for r in res); syy=sum((b_-my)**2 for b_ in y)
    s2=sse/(n-2); m_se=math.sqrt(s2/sxx); b_se=math.sqrt(s2*(Fr(1,n)+mx*mx/sxx))
    return dict(m=m,b=b,m_se=m_se,b_se=b_se,r2=1-sse/syy,sse=sse,res=res,n=n,sxy=sxy,sxx=sxx,syy=syy)
lx=[math.log10(raw[n]['population']) for n in names]
from fractions import Fraction
o1=ols1([Fraction(v) for v in lx],dG)
r=float(o1['sxy'])/math.sqrt(float(o1['sxx'])*float(o1['syy']))
put('size.slope',o1['m']); put('size.intercept',o1['b']); put('size.r',r); put('size.r2',r*r); put('size.p',t_two_sided_p(float(o1['m'])/o1['m_se'],31))
def pooled(L,pref):
    s=lambda k:sum(raw[n][k] for n in L)
    S22=H*s('dem22')/s('ballots22'); S26=H*s('dem26')/s('ballots26'); R22=H*s('regdem22')/s('regtot22'); R26=H*s('regdem26')/s('regtot26'); g=[c[n]['dG'] for n in L]
    for k,v in dict(S22=S22,S26=S26,R22=R22,R26=R26,dS=S26-S22,dR=R26-R22,dG=(S26-R26)-(S22-R22),med=med(g),lo=min(g),hi=max(g)).items(): put(f'grp.{pref}.{k}',v)
    put(f'grp.{pref}.n',len(L))
pooled(C6,'six'); pooled([n for n in names if n not in C6],'other'); pooled(names,'all')
def fwd(xs,ys):
    o=ols1([x/H for x in xs],ys); tc=t_crit(o['n']-2); rsd=math.sqrt(o['sse']/(o['n']-2))
    return dict(n=o['n'],m=o['m'],m_se=o['m_se'],m_lo=float(o['m'])-tc*o['m_se'],m_hi=float(o['m'])+tc*o['m_se'],b=o['b'],b_se=o['b_se'],b_lo=float(o['b'])-tc*o['b_se'],b_hi=float(o['b'])+tc*o['b_se'],
        r2=o['r2'],resid_sd=rsd,mae=mean([abs(e) for e in o['res']]),w2=sum(1 for e in o['res'] if abs(e)<=2),w5=sum(1 for e in o['res'] if abs(e)<=5))
G22=[c[n]['G22'] for n in names]; G26=[c[n]['G26'] for n in names]; R22=[c[n]['R22'] for n in names]; R26=[c[n]['R26'] for n in names]
F22=fwd(R22,G22); F26=fwd(R26,G26); FP=fwd(R22+R26,G22+G26)
for nm,F in (('2022',F22),('2026',F26),('pooled',FP)):
    for k,v in F.items(): put(f'fit.{nm}.{k}',v)
# 4-parameter interaction model by exact normal equations (Gauss-Jordan on Fractions)
rows=[[Fr(1),x/H,Fr(0),Fr(0)] for x in R22]+[[Fr(1),x/H,Fr(1),x/H] for x in R26]; yv=G22+G26
XtX=[[sum(rw[i]*rw[j] for rw in rows) for j in range(4)] for i in range(4)]; Xty=[sum(rw[i]*y for rw,y in zip(rows,yv)) for i in range(4)]
def inv(M):
    n=len(M); A=[list(M[i])+[Fr(int(i==j)) for j in range(n)] for i in range(n)]
    for i in range(n):
        p=next(k for k in range(i,n) if A[k][i]!=0); A[i],A[p]=A[p],A[i]; pv=A[i][i]; A[i]=[v/pv for v in A[i]]
        for k in range(n):
            if k!=i and A[k][i]!=0: f=A[k][i]; A[k]=[a-f*b for a,b in zip(A[k],A[i])]
    return [r[n:] for r in A]
Xi=inv(XtX); beta=[sum(Xi[i][j]*Xty[j] for j in range(4)) for i in range(4)]
sse=sum((y-sum(b*x for b,x in zip(beta,rw)))**2 for rw,y in zip(rows,yv)); s2=sse/(66-4)
se=[math.sqrt(s2*Xi[i][i]) for i in range(4)]
put('fit.int.d_b',beta[2]); put('fit.int.p_d_b',t_two_sided_p(float(beta[2])/se[2],62)); put('fit.int.d_m',beta[3]); put('fit.int.p_d_m',t_two_sided_p(float(beta[3])/se[3],62))
put('fit.2022.at40',F22['m']*Fr(40,100)+F22['b']); put('fit.2026.at40',F26['m']*Fr(40,100)+F26['b'])
res=[c[n]['residual'] for n in names]
put('el.median_res',med(res)); put('el.mean_res',mean(res)); put('el.sd_res',sd(res)); put('el.n_pos',sum(1 for x in res if x>0)); put('el.n_neg',sum(1 for x in res if x<0))
put('el.sw_exp_loss',sw['R22']-sw['R26']); put('el.sw_residual',sw['S26']-sw['S22'])
N=T['ballots26']; p=sw['S26']/H; s0=(sw['R22']-sw['R26'])/H
put('el.pooled_votes',(sw['S26']-sw['S22'])/H*N)
put('el.county_sum',sum(c[n]['offset_votes'] for n in names))
put('el.sum_loss',sum((c[n]['offset_votes'] for n in names if not c[n]['nonloss']),Fr(0))); put('el.sum_nonloss',sum((c[n]['offset_votes'] for n in names if c[n]['nonloss']),Fr(0)))
put('el.raw_rise',T['dem26']-T['dem22']); put('el.turnout_part',(T['dem26']-T['dem22'])-(sw['S26']-sw['S22'])/H*N)
for k,a in (('0',Fr(0)),('1',Fr(1,100)),('2',Fr(2,100))):
    put(f'el.need{k}.switched',(s0+a)*N); put(f'el.need{k}.added',(s0+a)*N/(1-p+s0+a))
put('el.gap_sum',sum(c[n]['gap_votes'] for n in names)); put('el.ne_resid_sum',sum(c[n]['ne_resid_votes'] for n in names))
ab=[n for n in names if c[n]['S22']>sw['S22']]
put('el.above_share_ballots22',H*sum(raw[n]['ballots22'] for n in ab)/T['ballots22']); put('el.above_share_ballots26',H*sum(raw[n]['ballots26'] for n in ab)/T['ballots26']); put('el.n_above',len(ab))
o2=ols1([c[n]['exp_loss'] for n in names],dG)
put('el.regfit.a',o2['b']); put('el.regfit.b',o2['m']); put('el.regfit.b_se',o2['m_se']); put('el.regfit.r2',o2['r2'])
put('el.top5',sorted(names,key=lambda n:-c[n]['residual'])[:5]); put('el.bot5',sorted(names,key=lambda n:c[n]['residual'])[:5])
put('el.top5_votes',sorted(names,key=lambda n:-c[n]['offset_votes'])[:5]); put('el.bot5_votes',sorted(names,key=lambda n:c[n]['offset_votes'])[:5])
for y in ('22','26'):
    put(f'tx.DR_gt_ballots{y}',[n for n in names if c[n]['DR'+y]>raw[n]['ballots'+y]])
    put(f'tx.gov_gt_ballots{y}',[n for n in names if raw[n]['allgov'+y]>raw[n]['ballots'+y]])
    put(f'tx.ballots_gt_reg{y}',[n for n in names if raw[n]['ballots'+y]>raw[n]['regtot'+y]])
    put(f'tx.nogov_median{y}',med([c[n]['nogov'+y] for n in names])); put(f'tx.nogov_gt5_{y}',[n for n in names if c[n]['nogov'+y]>5])
    put(f'tx.nogov_max_county{y}',argmax('nogov'+y))
    put(f'sw.nogov{y}',H*(T['ballots'+y]-T['allgov'+y])/T['ballots'+y])
put('tx.tightest',[[n,y] for s,n,y in sorted((c[n]['spare'+y],n,y) for n in names for y in ('22','26'))[:8]])
cand=[n for n in names if raw[n]['regdem26']<raw[n]['regdem22'] and raw[n]['dem26']>raw[n]['dem22']]
put('ten.n_candidates',len(cand)); ten=sorted(cand,key=lambda n:-c[n]['gap_votes'])[:10]; put('ten.counties',ten)
for n in ten: put(f'c.{n}.gap_share_ballots26',H*c[n]['gap_votes']/raw[n]['ballots26'])
put('pdf.order',sorted(names,key=lambda n:-c[n]['R26'])); put('sw.R26_1dp_check',sw['R26'])
json.dump(V,open(B+'verification/kp_passB.json','w'),indent=0)
print('pass B keys',len(V))
