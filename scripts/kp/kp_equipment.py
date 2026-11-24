"""New Mexico 33-county voting-equipment table from Verified Voting raw exports (state FIPS 35; retrieval time in raw/resources/vv/RETRIEVED.txt).
Population, FIPS and county names from Census Vintage 2025 (raw/census/co-est2025-alldata.csv). Pandas builder (pass A); checked by kp_verify_resources.py (csv module, pass B)."""
import pandas as pd, json, glob, re
RAW='/workspace/nm-election/raw/resources/vv/'; CEN='/workspace/nm-election/raw/census/co-est2025-alldata.csv'; OUT='/workspace/nm-election/out/'
TAB=['Hand-Fed Optical Scanner','Batch-Fed Optical Scanner','Hybrid BMD/Tabulator','Hybrid Optical Scan/BMD']
ACC=['Ballot Marking Device','Hybrid BMD/Tabulator','Hybrid Optical Scan/BMD','DRE-Touchscreen']
def load(y):
    m=pd.read_csv(RAW+f'vv{y}/verifier-machines.csv',skiprows=1,dtype=str,index_col=False,keep_default_na=False)
    j=pd.read_csv(RAW+f'vv{y}/verifier-jurisdictions.csv',skiprows=1,dtype=str,index_col=False,keep_default_na=False)
    for d in (m,j): d['fips']=d['FIPS code'].str[:5]
    return m,j
m26,j26=load(2026); m22,j22=load(2022)
eq=lambda r:f"{r.Manufacturer} {r.Model} ({r['Equipment Type']})"
p=pd.read_csv(CEN,encoding='latin-1',dtype={'STATE':str,'COUNTY':str}); p=p[(p.STATE=='35')&(p.COUNTY!='000')]
p['fips']=p.STATE+p.COUNTY; pop=p.set_index('fips').POPESTIMATE2025.astype(int)
cname=p.set_index('fips').CTYNAME.str.replace(' County','',regex=False).str.replace('Doña','Dona',regex=False).str.replace('\xf1','n',regex=False)
api={re.search(r'(\d{5})\.json',f).group(1):json.load(open(f)) for f in glob.glob(RAW+'county_api_2026/*.json')}
rows=[]
for fips,g in m26.groupby('fips'):
    jr=j26[j26.fips==fips].iloc[0]; c=cname[fips]
    vvname=jr.Jurisdiction.replace(' County','').replace('DeBaca','De Baca')
    assert vvname==c,(fips,vvname,c)
    ed=g[(g['Election Day Standard']=='Yes')&g['Equipment Type'].isin(TAB)]
    mail=g[(g['Mail Ballot/Absentee Equipment']=='Yes')&g['Equipment Type'].isin(TAB)]
    acc=g[(g['Election Day Accessible']=='Yes')&g['Equipment Type'].isin(ACC)]
    pb=g[g['Equipment Type'].str.contains('Poll Book')]
    g22=m22[m22.fips==fips]; ed22=g22[(g22['Election Day Standard']=='Yes')&g22['Equipment Type'].isin(TAB)]
    vend=sorted(set(ed.Manufacturer)); vv=sorted(set(g[g['Equipment Type'].isin(TAB+['Ballot Marking Device'])].VVPAT))
    ms=[x for x in (api.get(fips,{}).get('machines') or []) if x.get('equip_type') in TAB+['Ballot Marking Device']]
    vers=sorted({x['model']+': '+', '.join(f"{lab} {x[k]}" for lab,k in [('hardware','hardware_version'),('firmware','firmware_version'),('software','software_version')] if x.get(k)) for x in ms if (x.get('hardware_version') or x.get('firmware_version') or x.get('software_version'))})
    s26=sorted(set(eq(r) for _,r in ed.iterrows())); s22=sorted(set(eq(r) for _,r in ed22.iterrows()))
    k26=sorted(set((r.Model,r['Equipment Type']) for _,r in ed.iterrows())); k22=sorted(set((r.Model,r['Equipment Type']) for _,r in ed22.iterrows()))
    notes=[]
    if k26!=k22: notes.append('Election-day tabulator equipment changed from 2022: '+('; '.join(s22) if s22 else '(none listed)')+'.')
    elif s26!=s22: notes.append('Same election-day tabulator model as 2022; Verified Voting renamed the manufacturer from '+'/'.join(sorted(set(ed22.Manufacturer)))+' to '+'/'.join(sorted(set(ed.Manufacturer)))+'.')
    mail22=g22[(g22['Mail Ballot/Absentee Equipment']=='Yes')&g22['Equipment Type'].isin(TAB)]
    mk26=sorted(set((r.Model,r['Equipment Type']) for _,r in mail.iterrows())); mk22=sorted(set((r.Model,r['Equipment Type']) for _,r in mail22.iterrows()))
    if mk26!=mk22: notes.append('Absentee tabulator equipment changed from 2022: '+('; '.join(sorted(set(eq(r) for _,r in mail22.iterrows()))) or '(none listed)')+'.')
    if len(mail) and (mail['Equipment Type']=='Batch-Fed Optical Scanner').all(): notes.append('Absentee ballots are tabulated on a central batch-fed scanner.')
    rows.append({'County':c,'FIPS':fips,'Population':int(pop[fips]),'Marking method':jr['Election Day Marking Method'],'Voting location':jr['Voting Location'],
        'ED tabulator vendor':'; '.join(vend) if vend else 'Not listed','ED tabulator equipment':'; '.join(s26) if s26 else 'Not listed',
        'Mail tabulator equipment':'; '.join(sorted(set(eq(r) for _,r in mail.iterrows()))) or 'Not listed',
        'Accessible device':'; '.join(sorted(set(eq(r) for _,r in acc.iterrows()))) or 'Not listed',
        'Paper record / VVPAT':'VVPAT: '+('/'.join(vv) if vv else 'not listed')+(' (Verified Voting does not list a VVPAT for these systems)' if vv==['N/A'] else ''),
        'Software/firmware':'; '.join(vers) if vers else 'Not listed by Verified Voting',
        'Poll book':'; '.join(sorted(set(f"{r.Manufacturer} {r.Model}".strip() if r.Manufacturer not in ('','Not Applicable') else r['Equipment Type'] for _,r in pb.iterrows()))) or 'Not listed',
        'ED tabulator equipment 2022':'; '.join(s22) if s22 else 'Not listed',
        'Status':'Confirmed (Verified Voting 2026 record)' if len(ed) else 'Unconfirmed',
        'Source':f"https://verifiedvoting.org/verifier/#mode/navigate/map/ppEquip/mapType/normal/year/2026/state/35/county/{fips[2:]}",
        'Notes':' '.join(notes)})
o=pd.DataFrame(rows).sort_values('Population',ascending=False).reset_index(drop=True)
assert len(o)==33 and o.FIPS.is_unique
o.to_csv(OUT+'NM_33_County_Voting_Equipment_VerifiedVoting.csv',index=False)
summ={v:dict(counties=len(g),population=int(g.Population.sum())) for v,g in o.groupby('ED tabulator vendor')}
summ['_total_pop']=int(o.Population.sum()); summ['_n_confirmed']=int(o.Status.str.startswith('Confirmed').sum())
summ['_marking']=o['Marking method'].value_counts().to_dict(); summ['_location']=o['Voting location'].value_counts().to_dict()
summ['_central_mail']=list(o.County[o['Mail tabulator equipment'].str.contains('Batch-Fed')])
summ['_mail_on_ed_unit']=list(o.County[~o['Mail tabulator equipment'].str.contains('Batch-Fed')])
summ['_renamed']=list(o.County[o.Notes.str.contains('renamed')]); summ['_changed']=list(o.County[o.Notes.str.contains('Election-day tabulator equipment changed')]); summ['_mail_changed']=list(o.County[o.Notes.str.contains('Absentee tabulator equipment changed')])
summ['_paper_pollbook']=list(o.County[o['Poll book'].str.contains('Paper')])
summ['_pollbook']=o['Poll book'].value_counts().to_dict()
summ['_api_version_fields_nonempty']=sum(1 for d in api.values() for x in (d.get('machines') or []) if x.get('hardware_version') or x.get('firmware_version') or x.get('software_version'))
summ['_api_audit']=sorted({json.dumps(d['official_audit']) for d in api.values()})
summ['_api_n']=len(api)
json.dump(summ,open(OUT+'kp_equipment_summary_A.json','w'),indent=1); print(json.dumps(summ,indent=1))
