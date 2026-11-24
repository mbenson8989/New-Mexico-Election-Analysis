"""Cell-by-cell comparison: published table vs pass 1, published vs pass 2, pass 1 vs pass 2 (displayed precision)."""
import csv, json, datetime
V='/workspace/nm-election/verification'; O='/workspace/nm-election/out'
def load(p): r=list(csv.reader(open(p))); return r[0],{row[0]:row for row in r[1:]},[row[0] for row in r[1:]]
hp,P,op=load(f'{O}/nm_county_table.csv'); h1,A,o1=load(f'{V}/pass1_values.csv'); h2,B,o2=load(f'{V}/pass2_values.csv')
assert hp==h1==h2
s=json.load(open(f'{O}/nm_summary.json'))['fmt']; f1=json.load(open(f'{V}/pass1_fit.json')); f2=json.load(open(f'{V}/pass2_fit.json'))
def cmp(X,Y,fx,fy,label):
    tot=ok=0; bad=[]
    for c in X:
        for j,k in enumerate(hp[1:],1):
            tot+=1
            if Y.get(c) and X[c][j]==Y[c][j]: ok+=1
            else: bad.append((c,k,X[c][j],Y.get(c,[None]*99)[j]))
    for k in ('constant','multiplier','r2'):
        tot+=1
        if fx[k]==fy[k]: ok+=1
        else: bad.append(('STATEWIDE FIT',k,fx[k],fy[k]))
    return dict(label=label,total=tot,matched=ok,mismatched=len(bad),mismatches=bad)
def scmp(X,Y,fx,fy,label):
    tot=ok=0; bad=[]
    for c in X:
        for j,k in enumerate(sh[1:],1):
            tot+=1
            if Y.get(c) and X[c][j]==Y[c][j]: ok+=1
            else: bad.append(('share',c,k,X[c][j],Y.get(c,[None]*99)[j]))
    for blk in fx:
        for k in fx[blk]:
            tot+=1
            if str(fx[blk][k])==str(fy.get(blk,{}).get(k)): ok+=1
            else: bad.append(('share fit',blk,k,fx[blk][k],fy.get(blk,{}).get(k)))
    return dict(label=label,total=tot,matched=ok,mismatched=len(bad),mismatches=bad)
sh,SP,_=load(f'{O}/nm_share_fit_table.csv'); _,SA,_=load(f'{V}/pass1_share_values.csv'); _,SB,_=load(f'{V}/pass2_share_values.csv')
ss=json.load(open(f'{O}/nm_share_fit.json'))['fmt']; sf1=json.load(open(f'{V}/pass1_share_fit.json')); sf2=json.load(open(f'{V}/pass2_share_fit.json'))
def merge(a,b):
    return dict(label=a['label'],total=a['total']+b['total'],matched=a['matched']+b['matched'],mismatched=a['mismatched']+b['mismatched'],mismatches=a['mismatches']+b['mismatches'],share_version_cells=b['total'],share_version_matched=b['matched'])
res=[merge(cmp(P,A,s,f1,'Pass 1 vs published table'),scmp(SP,SA,ss,sf1,'')),merge(cmp(P,B,s,f2,'Pass 2 vs published table'),scmp(SP,SB,ss,sf2,'')),merge(cmp(A,B,f1,f2,'Pass 1 vs Pass 2 (cross-comparison)'),scmp(SA,SB,sf1,sf2,''))]
_unused=[cmp(P,A,s,f1,'Pass 1 vs published table'),cmp(P,B,s,f2,'Pass 2 vs published table'),cmp(A,B,f1,f2,'Pass 1 vs Pass 2 (cross-comparison)')]
order_ok = op==o1==o2
rep=dict(run_at=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),counties=len(P),cells_per_county=len(hp)-1,sort_order_identical=order_ok,results=res)
json.dump(rep,open(f'{V}/verification_report.json','w'),indent=1)
with open(f'{V}/VERIFICATION.md','w') as f:
    f.write(f"# New Mexico double verification\n\nRun {rep['run_at']} (box clock, America/Chicago). 33 counties x {len(hp)-1} displayed cells + 3 change-vs-drop fit values + share-version cells (33 counties x 9 cells (incl. Nebraska-style gap in votes) + 12 surplus-equation fit values: m, b, R2, mean abs residual, max county, max residual for 2026 and 2022) per comparison. Population sort order identical in all three tables: {order_ok}.\n\n| Comparison | Cells | Matched | Mismatched | of which share-version cells (matched) |\n|---|---|---|---|---|\n")
    for r in res: f.write(f"| {r['label']} | {r['total']} | {r['matched']} | {r['mismatched']} | {r['share_version_cells']} ({r['share_version_matched']}) |\n")
    for r in res:
        if r['mismatches']: f.write(f"\n## Mismatches: {r['label']}\n\n"+'\n'.join(f'- {m}' for m in r['mismatches'])+'\n')
for r in res: print(r['label'],r['matched'],'/',r['total'],'mismatched',r['mismatched'],r['mismatches'][:5])
print('order identical',order_ok)
