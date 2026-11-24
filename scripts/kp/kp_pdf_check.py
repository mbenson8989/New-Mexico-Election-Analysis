"""Cell-by-cell check of the New Mexico 33-county PDF: pdftotext -layout text, one line per county, compared with
cells recomputed from pass2_counts.json (the independent stdlib pass over the second-source SOS files) with exact fractions."""
import json, subprocess, re
from fractions import Fraction as Fr
B='/workspace/nm-election/'
P=json.load(open(B+'verification/pass2_counts.json'))
cnt=P
def half(x,nd):  # exact half-up (away from zero) at nd decimals
    q=Fr(10)**nd; v=abs(x)*q; n=int(v); n+= 1 if v-n>=Fr(1,2) else 0; return (n if x>=0 else -n), nd
def s_int(x): return f"{int(x):,}"
def s_sint(x): return ('+' if x>0 else ('-' if x<0 else ''))+f"{abs(int(x)):,}"
def s_pct(x,signed):
    n,nd=half(x,1); s=f"{abs(n)//10}.{abs(n)%10}%"
    if not signed: return s
    return ('-' if n<0 else '+')+s
txt=subprocess.run(['pdftotext','-layout',B+'wiki/New_Mexico_33_County_Democratic_Registration_and_Vote_Change.pdf','-'],capture_output=True,text=True).stdout
lines=[l.strip() for l in txt.split('\n')]
rowsB=json.load(open(B+'verification/kp_pdf_rows_B.json'))
def expect(name,d):
    rd=d['regdem26']-d['regdem22']; vd=d['dem26']-d['dem22']; bd=d['ballots26']-d['ballots22']
    return [name,s_int(d['population']),s_pct(Fr(100*d['regdem26'],d['regtot26']),False),s_int(d['regdem22']),s_int(d['regdem26']),s_sint(rd),s_pct(Fr(100*rd,d['regdem22']),True),
            s_int(d['dem22']),s_int(d['dem26']),s_sint(vd),s_pct(Fr(100*vd,d['dem22']),True),s_int(d['ballots22']),s_int(d['ballots26']),s_sint(bd),s_pct(Fr(100*bd,d['ballots22']),True)]
checked=0; bad=[]
keys=['population','regdem22','regdem26','regtot26','dem22','dem26','ballots22','ballots26']
sw={k:0 for k in keys}
for r in rowsB[:-1]:
    c=r[0]; d=cnt[c]; e=expect(c,d)
    for k in keys: sw[k]+=d[k]
    line=[l for l in lines if re.match(re.escape(c)+r'\s+[\d,]+\s',l)]
    assert len(line)==1,(c,line)
    toks=re.split(r'\s{1,}',line[0][len(c):].strip())
    got=[c]+toks
    for a,b in zip(e,got): checked+=1; (a==b) or bad.append((c,a,b))
    if len(got)!=len(e): bad.append((c,'len',len(got)))
e=expect('Statewide total',sw); line=[l for l in lines if l.startswith('Statewide total')]; assert len(line)==1
got=['Statewide total']+re.split(r'\s+',line[0][len('Statewide total'):].strip())
for a,b in zip(e,got): checked+=1; (a==b) or bad.append(('Statewide',a,b))
json.dump(dict(cells=checked,mismatches=len(bad),detail=bad),open(B+'verification/kp_pdf_cell_check.json','w'),indent=1)
print('PDF cells checked',checked,'mismatches',len(bad),bad[:5]); assert not bad
