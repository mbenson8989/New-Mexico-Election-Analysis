"""Clerk contact CSV from the official NM SOS County Clerk Information page (parsed lines saved in clerks_parsed_raw.json),
plus the NMSA 4-58-2 planning-district lookup. Party labels stripped; mailing address used where the SOS lists one."""
import json, csv, re
B='/workspace/nm-election/'
raw=json.load(open(B+'raw/resources/sos/clerks_parsed_raw.json'))
SURN={'Amanda López Askin':'López Askin','Robert Serrano III':'Serrano','Veronica Olguin Manley':'Manley'}
DIST={1:('Northwest',['San Juan','McKinley','Cibola']),2:('North Central',['Rio Arriba','Santa Fe','Taos','Los Alamos','Colfax','Mora','San Miguel']),
3:('Mid-Region',['Sandoval','Bernalillo','Valencia','Torrance']),4:('Eastern Plains',['Union','Harding','Quay','Curry','Roosevelt','Guadalupe','De Baca']),
5:('Southwest',['Catron','Hidalgo','Luna','Grant']),6:('Southeast',['Lincoln','Otero','Chaves','Eddy','Lea']),7:('South Central',['Socorro','Sierra','Dona Ana'])}
fips={}
for r in csv.DictReader(open(B+'out/NM_33_County_Voting_Equipment_VerifiedVoting.csv')):
    k=[x for x in r if 'fips' in x.lower()]; fips[r[[x for x in r if x.lower().startswith('county')][0]]]=r[k[0]] if k else ''
rows=[]
for county,lines in raw:
    name=re.sub(r'\s*\((D|R|DTS|L)\)\s*$','',lines[0].split(':',1)[1].strip())
    rest=[l for l in lines[1:]]
    ph=next(l.split(':',1)[1].strip() for l in rest if l.startswith('Phone'))
    em=[l.split(':',1)[1].strip() for l in rest if l.startswith('Email') or l.startswith('General Inquiries')]
    elec=[l.split(':',1)[1].strip() for l in rest if l.startswith('Election')]
    web=next((l.split(':',1)[1].strip() for l in rest if l.startswith('Website')),'')
    addr=[l for l in rest[:next(i for i,l in enumerate(rest) if l.startswith('Phone'))]]
    if 'Mailing Address' in addr: addr=addr[addr.index('Mailing Address')+1:]
    if county=='Valencia': addr=['P. O. Box 969','Los Lunas, NM 87031']
    sur=SURN.get(name,name.split()[-1])
    key='Dona Ana' if county.startswith('Do') else county
    d=[n for n,(lab,cs) in DIST.items() if key in cs]; assert len(d)==1,county
    rows.append(dict(county=key,county_display=county,clerk=name,salutation_surname=sur,title='County Clerk',mailing_address=' | '.join(addr),
        phone=ph,email=em[0] if em else '',election_email=elec[0] if elec else '',website=web,fips=fips.get(key,fips.get(county,'')),
        planning_district=d[0],district_label=DIST[d[0]][0],notes=('SOS page lists this email as "vtrujillo@countyofmora" with no domain ending; it appears incomplete. Confirm with the clerk office by phone before emailing.' if county=='Mora' else ''),source='https://www.sos.nm.gov/voting-and-elections/county-clerk-information/'))
assert len(rows)==33 and len({r['county'] for r in rows})==33 and sum(len(v[1]) for v in DIST.values())==33
w=csv.DictWriter(open(B+'out/NM_County_Clerks.csv','w',newline=''),fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open(B+'out/NM_Planning_District_Lookup.csv','w',newline='') as f:
    x=csv.writer(f); x.writerow(['County','Planning district (NMSA 1978, § 4-58-2)','Descriptive label (added here, not statutory)'])
    for r in sorted(rows,key=lambda r:r['county']): x.writerow([r['county_display'],r['planning_district'],r['district_label']])
for r in rows: print(r['county'],'|',r['clerk'],'|',r['salutation_surname'],'|',r['mailing_address'],'|',r['email'],'|',r['fips'],'|',r['planning_district'])
