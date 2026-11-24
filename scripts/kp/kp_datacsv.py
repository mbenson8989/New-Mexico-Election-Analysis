"""33-county data CSV for the wiki (population order). Written from pass A, then every cell re-derived from pass B and compared."""
import json, csv
B='/workspace/nm-election/'
OUT=B+'wiki/NM_Governor_2022_2026_DeltaG_by_County.csv'
cols=[('county','County',None),('population','Population (Census Jul 1, 2025)','i'),('regdem22','Dem registered 2022 (Oct 31)','i'),('regtot22','Total registered 2022','i'),
('regdem26','Dem registered 2026 (Oct 30)','i'),('regtot26','Total registered 2026','i'),('dem22','Dem governor votes 2022','i'),('ballots22','Total ballots cast 2022','i'),
('dem26','Dem governor votes 2026 (unofficial)','i'),('ballots26','Total ballots cast 2026 (unofficial)','i'),('S22','Dem share of ballots 2022 (%)','f'),('S26','Dem share of ballots 2026 (%, unofficial)','f'),
('R22','Dem registration share 2022 (%)','f'),('R26','Dem registration share 2026 (%)','f'),('G22','G 2022 (pts)','f'),('G26','G 2026 (pts, unofficial)','f'),('dG','Delta-G (pts, unofficial)','f'),
('exp_loss','Expected loss (pts)','f'),('residual','Residual (pts, unofficial)','f'),('offset_votes','Backward-solved offset votes (unofficial)','i'),('gap_votes','Gap in votes (unofficial)','i')]
def rows(src):
    V=json.load(open(B+f'verification/kp_pass{src}.json')); out=[]
    for c in V['counties_pop_order']:
        r=[]
        for k,h,t in cols:
            if k=='county': r.append(c); continue
            x=V[f'c.{c}.{k}']; r.append(str(int(round(x))) if t=='i' else f"{x:.4f}")
        out.append(r)
    return out
A=rows('A'); Bb=rows('B'); assert A==Bb, 'pass A/B differ'
with open(OUT,'w',newline='') as f:
    w=csv.writer(f); w.writerow([h for _,h,_ in cols]); w.writerows(A)
print('csv ok', len(A), 'rows; pass A == pass B')
