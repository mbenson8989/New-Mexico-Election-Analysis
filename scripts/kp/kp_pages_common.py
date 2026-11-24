"""Shared text and helpers for the Kansas-parity New Mexico wiki pages."""
from kpfmt import Reg, fmt
W='/workspace/nm-election/wiki/'
WIKI='https://github.com/mbenson8989/New-Mexico-Election-Analysis/wiki/'
REPO='https://github.com/mbenson8989/New-Mexico-Election-Analysis'
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
NEWIKI='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki'
SUBSTACK='https://moebenson.substack.com/p/a-pattern-you-cant-unsee'
EL_ANCHOR='#expected-loss-residual-and-backward-solved-offset-votes-neiasd-method'
S='\\*'
BANNER=('> **\\*2026 figures are UNOFFICIAL.** They come from the New Mexico Secretary of State (SOS) results site ([electionresults.sos.nm.gov](https://electionresults.sos.nm.gov/)), '
 'which labels the November 3, 2026 general election "Unofficial Results" (last updated 11/12/2026 11:07 AM MT; downloaded Nov 19, 2026). The State Canvassing Board '
 'approves the canvass on the third Tuesday after the election, Nov 24, 2026 (NMSA 1978, § 1-13-15); these pages will be re-run after certification. 2022 figures are SOS '
 'official results. Governor and Lieutenant Governor race. Denominator: total ballots cast (SOS turnout), in both years. Registration: all registered voters, SOS '
 '"Statewide by County" reports as of Oct 31, 2022 and Oct 30, 2026. These pages measure a pattern; they make no claim about intent, fraud or cause.')
def related(skip):
    items=[('Home','Home'),('Bottom-Up Reverse Math','Reverse-Math'),('Locked New Mexico Formula','Locked-New-Mexico-Formula'),('Floor and Ceiling Counties','Floor-and-Ceiling'),('Graphs','Graphs')]
    out=[f'[{a}]({b})' for a,b in items if b!=skip]+[f'[Cedar County Audit (Nebraska)]({CEDAR})']
    return '---\n**Related:** '+' · '.join(out)+'\n'
def cty(R,c,k,f): return R.v(f'c.{c}.{k}',f)
def arrow(R,c,a,b,f,star=''):
    return f"{cty(R,c,a,f)} → {cty(R,c,b,f)}{star}"
def signed_term(R,key):
    """'+ 0.25' / '− 0.25' for writing an equation term"""
    v=R.raw(key); return ('− ' if v<0 else '+ ')+R.v(key,'abs2')
def write(R,name,body):
    open(W+name,'w').write(body); R.save(f'wiki/{name}')
