import re,sys
def get(txt,sec):
    lines=txt.split('\n')
    pat=re.compile(r'^\s*'+re.escape(sec)+r'\.\s')
    for i,l in enumerate(lines):
        if pat.match(l):
            out=[]
            for l2 in lines[i:]:
                if l2.strip().startswith('History:'): out.append(l2); break
                out.append(l2)
            return '\n'.join(out)
    return None
if __name__=='__main__':
    f=sys.argv[1]; txt=open(f).read()
    for s in sys.argv[2:]:
        print('=====',s); print(get(txt,s))
