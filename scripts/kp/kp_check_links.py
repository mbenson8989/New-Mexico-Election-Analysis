"""Every relative link in the wiki pages must resolve: a wiki page (and its #anchor, using GitHub's heading slugs) or a file in wiki/."""
import re, os, glob, sys, json, unicodedata
W='/workspace/nm-election/wiki/'
WIKI='https://github.com/mbenson8989/New-Mexico-Election-Analysis/wiki/'
def slug(h):
    h=h.strip().lower()
    h=re.sub(r'[*_`\\]','',h)
    h=''.join(ch for ch in h if ch in ' -' or unicodedata.category(ch)[0] in 'LN')
    return h.replace(' ','-')
pages={os.path.basename(p)[:-3]:open(p,encoding='utf-8').read() for p in glob.glob(W+'*.md')}
anchors={}
for n,t in pages.items():
    t2=re.sub(r'```.*?```','',t,flags=re.S); seen={}; A=set()
    for h in re.findall(r'^#{1,6} (.+)$',t2,flags=re.M):
        s=slug(h); k=seen.get(s,0); A.add(s if k==0 else f'{s}-{k}'); seen[s]=k+1
    anchors[n]=A
bad=[]; n=0
for name,t in pages.items():
    for m in re.finditer(r'\]\(([^)\s]+)\)',t):
        u=m.group(1); n+=1
        if u.startswith(WIKI): u=u[len(WIKI):] or 'Home'
        elif u==WIKI[:-1]: u='Home'
        elif u.startswith('http') or u.startswith('mailto:'): continue
        path,_,anc=u.partition('#')
        if path=='' : path=name
        if path in pages:
            if anc and anc not in anchors[path]: bad.append((name,u,'anchor'))
        elif not os.path.exists(W+path): bad.append((name,u,'missing file'))
print('links checked',n,'bad',len(bad)); [print(b) for b in bad]
json.dump(dict(checked=n,bad=bad),open('/workspace/nm-election/verification/kp_link_check.json','w'),indent=1)
sys.exit(1 if bad else 0)
