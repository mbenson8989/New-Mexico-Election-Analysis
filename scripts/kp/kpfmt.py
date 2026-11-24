"""Display formatting + a registry of every computed number written into a Kansas-parity page, letter or graphic.
Builders call R.v(key, fmt) with a pass-A key; kp_check_pages.py recomputes each logged (key, fmt) from PASS B and requires
the identical string, and that the string occurs in the output file."""
import json, math
B='/workspace/nm-election/'
def fmt(x,f):
    if f=='raw': return str(x)
    if f=='list': return ', '.join(x)
    if f=='int': return f"{int(round(x)):,}"
    if f=='sint':
        n=int(round(x)); return ('+' if n>0 else ('-' if n<0 else '')) + f"{abs(n):,}"
    if f=='pct2': return f"{x:.2f}%"
    if f=='pct1': return f"{x:.1f}%"
    if f=='spct1':
        s=f"{x:.1f}"; return s+'%' if s.startswith('-') else '+'+s+'%'
    if f=='spct0':
        s=f"{x:.0f}"; return s+'%' if s.startswith('-') else '+'+s+'%'
    if f=='f1': return f"{x:.1f}"
    if f=='f2': return f"{x:.2f}"
    if f=='f3': return f"{x:.3f}"
    if f=='pt2':
        s=f"{x:.2f}"; return s if s.startswith('-') else '+'+s
    if f=='pt1':
        s=f"{x:.1f}"; return s if s.startswith('-') else '+'+s
    if f=='abs2': return f"{abs(x):.2f}"
    if f=='p': return f"{x:.1e}" if x<0.001 else f"{x:.2f}"
    raise ValueError(f)
class Reg:
    def __init__(s,name,src='A'):
        s.name=name; s.V=json.load(open(B+f'verification/kp_pass{src}.json')); s.log=[]
        import os
        if os.path.exists(B+f'verification/kp_extra{src}.json'): s.V.update(json.load(open(B+f'verification/kp_extra{src}.json')))
    def raw(s,k): return s.V[k]
    def v(s,k,f):
        out=fmt(s.V[k],f); s.log.append([k,f,out]); return out
    def use(s,k):
        s.log.append([k,'use',s.V[k]]); return s.V[k]
    def save(s,path):
        json.dump(dict(file=path,entries=s.log),open(B+f'verification/kp_log_{s.name}.json','w'),indent=0)
