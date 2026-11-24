import requests,re,sys,time
UA=open('/tmp/ua').read().strip()
BASE='https://electionresults.sos.nm.gov/'
def sess():
    s=requests.Session(); s.headers.update({'User-Agent':UA,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en-US,en;q=0.9'})
    _g=s.get; _p=s.post
    def g(*a,**k):
        for i in range(6):
            r=_g(*a,**k)
            if r.status_code!=403: return r
            print("403 retry",a[0][:80],flush=True); time.sleep(5*(i+1))
        raise SystemExit('403 persistent '+str(a))
    def p(*a,**k):
        for i in range(6):
            r=_p(*a,**k)
            if r.status_code!=403: return r
            print("403 retry",a[0][:80],flush=True); time.sleep(5*(i+1))
        raise SystemExit('403 persistent POST '+str(a))
    s.get=g; s.post=p
    return s
def fields(h):
    d={}
    for m in re.finditer(r'<input[^>]*type="hidden"[^>]*>',h):
        n=re.search(r'name="([^"]+)"',m.group(0)); v=re.search(r'value="([^"]*)"',m.group(0))
        if n: d[n.group(1)]=v.group(1) if v else ''
    return d
def postback(s,url,target,h=None):
    if h is None: h=s.get(BASE+url).text
    d=fields(h); d['__EVENTTARGET']=target; d['__EVENTARGUMENT']=''
    import html as H
    d={k:H.unescape(v) for k,v in d.items()}
    r=s.post(BASE+url,data=d)
    return r
