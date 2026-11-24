"""Page-only derived values for both passes: comparison with the other states' published county fits (read from the Kansas
wiki's KS_results_summary.json, ballots-cast basis = New Mexico's basis). Writes verification/kp_extra{A,B}.json; Reg merges them."""
import json
B='/workspace/nm-election/verification/'
# saved copy of mbenson8989/Kansas-Election-Analysis KS_results_summary.json (published neighbor fits)
K=json.load(open('/workspace/nm-election/raw/resources/KS_results_summary_neighbors_source.json'))['neighbors']
for src in 'AB':
    V=json.load(open(B+f'kp_pass{src}.json')); X={}
    for st in ('NE','IA','SD'):
        for y in ('2022','2026'):
            for basis in ('ballots','govvotes'):
                d=K[f'{st}_{y}_{basis}']; X[f'ext.{st}.{y}.{basis}.m']=d['m']; X[f'ext.{st}.{y}.{basis}.b']=d['b']; X[f'ext.{st}.{y}.{basis}.n']=d['n']
    for y in ('2022','2026'):
        for p in ('m','b'):
            band=[X[f'ext.{s}.{y}.ballots.{p}'] for s in ('NE','IA','SD')]; lo,hi=min(band),max(band); v=V[f'fit.{y}.{p}']
            X[f'band.{y}.{p}.lo']=lo; X[f'band.{y}.{p}.hi']=hi
            X[f'band.{y}.{p}.inside']=lo<=v<=hi
            dist=(lo-v) if v<lo else ((v-hi) if v>hi else 0.0); X[f'band.{y}.{p}.dist']=dist; X[f'band.{y}.{p}.dist_se']=dist/V[f'fit.{y}.{p}_se']
            X[f'band.{y}.{p}.side']='below' if v<lo else ('above' if v>hi else 'inside')
            X[f'band.{y}.{p}.ci_overlap']=not (V[f'fit.{y}.{p}_hi']<lo or V[f'fit.{y}.{p}_lo']>hi)
    X['meta.kp_keys']=len(V)
    X['sw.other22']=V['sw.allgov22']-V['sw.dem22']-V['sw.rep22']; X['sw.other26']=V['sw.allgov26']-V['sw.dem26']-V['sw.rep26']
    json.dump(X,open(B+f'kp_extra{src}.json','w'),indent=0)
print(json.dumps({k:v for k,v in X.items() if k.startswith('band')},indent=0))
