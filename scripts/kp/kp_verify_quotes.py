"""Check every quotation (>= 8 chars, in straight double quotes) in the NM AG letter, a clerk letter and an IPRA request
against the saved official source texts, word for word (whitespace, quote style, soft and line-break hyphens normalized)."""
import re,html,glob,json,sys
B='/workspace/nm-election/'; R=B+'raw/resources/'
def norm(s):
    s=html.unescape(s).replace('\u00ad','')
    for a,b in [('’',"'"),('‘',"'"),('“','"'),('”','"'),('\xa0',' ')]: s=s.replace(a,b)
    return re.sub(r'\s+',' ',s).strip()
def strip_html(p):
    s=open(p,errors='ignore').read(); s=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',s,flags=re.S); return norm(re.sub(r'<[^>]+>',' ',s))
def statute(p):
    t=open(p).read(); t=re.sub(r'(\w)-\n\s*(\w)',lambda m:m.group(1)+'-'+m.group(2),t)  # keep "14-\n2-1" as 14-2-1
    return norm(t)
src={}
for f in glob.glob(R+'statutes/*.txt'): src['NMSA '+f.split('/')[-1][:-4]]=statute(f)
src['EO 14399']=norm(open(R+'federal/eo14399.txt').read()).replace('- ','')
src['U.S. Const.']=strip_html(R+'federal/constitution.html')
src['CA v Trump judgment']=norm(open(R+'federal/ca_v_trump_final_judgment_doc194.txt').read())
src['NMDOJ EO14399 release']=strip_html(R+'federal/nmdoj_eo14399_suit.html')
src['CA AG stay release']=strip_html(R+'federal/caoag_scotus_stay_eo14399_20260824.html')
src['Dona Ana release']=strip_html(R+'sos/donaana_ballot_verifier_20260529.html')
import subprocess
for f in glob.glob(B+'raw/registration/Statewide_*.pdf'): src['SOS reg '+f.split('/')[-1]]=norm(subprocess.run(['pdftotext',f,'-'],capture_output=True,text=True).stdout)
src['SOS 2026 county page']=strip_html(B+'raw/county_pages/2026_cty27_De_Baca.html')
src['SOS clerk page']=strip_html(R+'sos/county_clerk_information.html')
def check(path):
    t=norm(open(path).read()); res=[]
    for q in [q for q in re.findall(r'"([^"]*)"',t) if len(q)>=8]:
        qq=re.sub(r'\[(.)\]',r'\1',q).strip(' ,.')
        parts=[p.strip(' ,.') for p in re.split(r'\s*(?:…|\.\.\.)\s*',qq) if p.strip()]
        hits=[k for k,v in src.items() if all(p in v for p in parts)]
        if not hits:
            hits=[k+' (first letter case adjusted)' for k,v in src.items() if all(p[1:] in v for p in parts)]
        res.append(dict(quote=q,found_in=hits))
    return res
out={}; bad_total=0; n=0
files=sys.argv[1:] or [B+'letters/ag/New_Mexico_Attorney_General_Letter.md']+sorted(glob.glob(B+'letters/clerk/md/*.md'))+sorted(glob.glob(B+'letters/ipra/md/*.md'))
for p in files:
    r=check(p); out[p]=r; n+=len(r)
    bad=[x for x in r if not x['found_in']]; bad_total+=len(bad)
    for x in bad: print('MISSING in',p.split('/')[-1],':',x['quote'][:140])
json.dump(dict(files=len(files),quotes=n,missing=bad_total,detail=out),open(B+'verification/kp_quote_check.json','w'),indent=1)
print('files',len(files),'quotes',n,'missing',bad_total)
sys.exit(1 if bad_total else 0)
