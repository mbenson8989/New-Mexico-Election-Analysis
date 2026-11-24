"""Compare Kansas-parity pass A and pass B, key by key: identical key sets; lists/strings/bools/ints exactly equal;
floats equal to 1e-9 relative (exact-fraction pass B vs float pass A) and, for statistical p-values and CIs from the t distribution, 1e-6."""
import json,math,sys
B='/workspace/nm-election/verification/'
a=json.load(open(B+'kp_passA.json')); b=json.load(open(B+'kp_passB.json'))
bad=[]; n=0
for k in sorted(set(a)|set(b)):
    n+=1
    if k not in a or k not in b: bad.append((k,'missing')); continue
    x,y=a[k],b[k]
    if isinstance(x,float) or isinstance(y,float):
        tol=1e-6 if any(s in k for s in ('.p','_lo','_hi','_se','resid_sd','size.r','.sd')) else 1e-9
        if not math.isclose(float(x),float(y),rel_tol=tol,abs_tol=1e-9): bad.append((k,x,y))
    elif x!=y: bad.append((k,x,y))
rep=dict(keys_compared=n,mismatches=bad,CLEAN=not bad)
json.dump(rep,open(B+'kp_compare_report.json','w'),indent=1)
print('kp compare: keys',n,'mismatches',len(bad)); [print('  ',x) for x in bad[:20]]
sys.exit(1 if bad else 0)
