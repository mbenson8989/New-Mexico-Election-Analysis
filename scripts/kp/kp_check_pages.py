"""Second verification for every Kansas-parity page, letter, chart and card.
1) Every logged (key, fmt) is recomputed from PASS B (+ extras B) and must give the identical string, and that string must occur in its file.
2) 'use' entries (chart data) must equal pass B numerically.
3) Coverage scan: every data-looking number in each built wiki page must be a logged output for that page or on a short allowlist
   (the old vote-flip section between vf markers is excluded; it is checked by verify_vote_flip.py)."""
import json, glob, re, math, sys, os
from kpfmt import fmt
B='/workspace/nm-election/'
V=json.load(open(B+'verification/kp_passB.json'))
if os.path.exists(B+'verification/kp_extraB.json'): V.update(json.load(open(B+'verification/kp_extraB.json')))
err=[]; n_str=n_use=n_presence=0; per_file={}
def eq(a,b):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)): return math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9)
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
    return a==b
def check(file,entries):
    global n_str,n_use,n_presence
    text=None
    if file not in ('charts',) and not file.endswith('.png'):
        text=open(B+file,encoding='utf-8').read()
    outs=per_file.setdefault(file,set())
    for k,f,out in entries:
        if k not in V: err.append(f'{file}: key {k} missing in pass B'); continue
        if f=='use':
            n_use+=1
            if not eq(V[k],out): err.append(f'{file}: use {k} A={out} B={V[k]}')
            continue
        n_str+=1; b=fmt(V[k],f)
        if b!=out: err.append(f'{file}: {k} {f} A={out!r} B={b!r}')
        outs.add(out)
        if text is not None:
            n_presence+=1
            if out not in text: err.append(f'{file}: {k} {f} {out!r} not found in file')
for p in sorted(glob.glob(B+'verification/kp_log_*.json')):
    d=json.load(open(p))
    if 'files' in d:
        for x in d['files']: check(x['file'],x['entries'])
    else: check(d['file'],d['entries'])
# ---- coverage scan
NUM=re.compile(r'(?<![\w.#/\-§])[+\-−]?\d[\d,]*\.\d+%?|(?<![\w.#/\-§])[+\-−]?\d{1,3}(?:,\d{3})+(?![\d])|(?<![\w.#/§(])[+\-]\d+(?![\d.,%\w])')
ALLOW={'wiki/Reverse-Math.md':{'2.0','1.0'},'wiki/Floor-and-Ceiling.md':set(),'wiki/Graphs.md':set(),'wiki/Resources.md':{'1.0','14-2-1','1080','1600'},
 'wiki/Home.md':set(),'wiki/README.md':set(),'wiki/New-Mexico-County-PDF-Information.md':{'510'}}
# ZIP sizes shown on Resources: recomputed from the files themselves
Z=json.load(open(B+'out/zip_sizes.json'))
for k,z in Z.items():
    real=round(os.path.getsize(B+'wiki/downloads/'+z['file'])/1e6,1)
    if real!=z['mb']: err.append(f"zip size {z['file']}: listed {z['mb']} real {real}")
    ALLOW['wiki/Resources.md'].add(f"{z['mb']}")
ALLOW['wiki/Resources.md'].add('100.0%')
cov_fail=[]; cov_n=0
for f,allow in ALLOW.items():
    t=open(B+f,encoding='utf-8').read()
    t=re.sub(r'<!-- vf-begin -->.*?<!-- vf-end -->','',t,flags=re.S)
    t=re.sub(r'\(https?://[^)]*\)|\]\([^)]*\)','',t)          # link targets
    t=re.sub(r'`[^`]*`','',t)
    t=re.sub(r'§+ ?[\d\-.]+(\([A-Za-z0-9]+\))*','',t)         # statute cites
    outs=per_file.get(f,set())
    blob='\n'.join(outs)
    for m in NUM.finditer(t):
        s=m.group(0).replace('−','-'); cov_n+=1
        if s in allow: continue
        if any(s==o or s in o for o in outs): continue
        cov_fail.append((f,s,t[max(0,m.start()-60):m.end()+20].replace('\n',' ')))
print(f'string checks {n_str}, presence checks {n_presence}, use checks {n_use}, errors {len(err)}')
print(f'coverage numbers scanned {cov_n}, unlogged {len(cov_fail)}')
for e in err[:40]: print('ERR',e)
for c in cov_fail[:80]: print('COV',c)
json.dump(dict(string_checks=n_str,presence_checks=n_presence,use_checks=n_use,errors=err,coverage_scanned=cov_n,coverage_unlogged=cov_fail),open(B+'verification/kp_page_check.json','w'),indent=1,ensure_ascii=False)
sys.exit(1 if err or cov_fail else 0)
