"""Word + PDF for the AG letter, 33 clerk letters and 33 IPRA requests (Kansas md2docx_ks converter, LibreOffice for PDF),
then ZIPs (all counties + the 7 NMSA 4-58-2 planning districts, each with PDF/ and Word/ folders), the district lookup CSV,
and the delivery trackers. Nothing is sent."""
import sys, os, glob, subprocess, csv, zipfile, json, shutil
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'vendor')); from md2docx_ks import convert
B='/workspace/nm-election/'; L=B+'letters/'; PKG=B+'wiki/downloads/'; os.makedirs(PKG,exist_ok=True)
jobs=[(L+'ag/New_Mexico_Attorney_General_Letter.md',L+'ag/',11.5)]
for kind in ('clerk','ipra'):
    os.makedirs(L+kind+'/Word',exist_ok=True); os.makedirs(L+kind+'/PDF',exist_ok=True)
    jobs+= [(m,L+kind+'/',10.5) for m in sorted(glob.glob(L+kind+'/md/*.md'))]
docx=[]
for src,outdir,size in jobs:
    base=os.path.basename(src)[:-3]; wd=outdir+('Word/' if outdir!=L+'ag/' else '')+base+'.docx'
    convert(src,wd,size); docx.append((wd,outdir+('PDF/' if outdir!=L+'ag/' else '')))
for outdir in sorted({d for _,d in docx}):
    files=[w for w,d in docx if d==outdir]
    subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',outdir]+files,check=True,capture_output=True)
n=lambda p:len(glob.glob(p))
print('docx',len(docx),'pdf ag',n(L+'ag/*.pdf'),'clerk',n(L+'clerk/PDF/*.pdf'),'ipra',n(L+'ipra/PDF/*.pdf'))
# AG letter into the published folder
for ext in ('pdf','docx'): shutil.copy2(L+f'ag/New_Mexico_Attorney_General_Letter.{ext}',B+f'wiki/New_Mexico_Attorney_General_Letter.{ext}')
# ZIPs
CL=list(csv.DictReader(open(B+'out/NM_County_Clerks.csv')))
fname=lambda r:r['county_display'].replace(' ','_').replace('ñ','n')
DN={'1':'Northwest','2':'North_Central','3':'Mid-Region','4':'Eastern_Plains','5':'Southwest','6':'Southeast','7':'South_Central'}
def mk(path,rows,tracker):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for r in sorted(rows,key=lambda r:r['county']):
            f=fname(r)
            z.write(L+f'clerk/PDF/{f}_County_Clerk_Letter.pdf',f'PDF/{f}_County_Clerk_Letter.pdf')
            z.write(L+f'clerk/Word/{f}_County_Clerk_Letter.docx',f'Word/{f}_County_Clerk_Letter.docx')
            z.write(L+f'ipra/PDF/{f}_County_IPRA_Request.pdf',f'PDF/{f}_County_IPRA_Request.pdf')
            z.write(L+f'ipra/Word/{f}_County_IPRA_Request.docx',f'Word/{f}_County_IPRA_Request.docx')
        z.write(tracker,os.path.basename(tracker))
import kp_tracker
sizes={}
allx=kp_tracker.build(CL,PKG+'New_Mexico_33_County_Letter_Delivery_Tracker.xlsx','New Mexico 33-County Letter Delivery Tracker')
mk(PKG+'New_Mexico_Clerk_Letters_All_33_Counties.zip',CL,allx); sizes['all']=dict(file='New_Mexico_Clerk_Letters_All_33_Counties.zip',n=33)
for d,lab in DN.items():
    rows=[r for r in CL if r['planning_district']==d]
    tx=kp_tracker.build(rows,L+f'District_{d}_{lab}_Letter_Delivery_Tracker.xlsx',f'New Mexico Planning District {d} ({lab.replace("_"," ")}) Letter Delivery Tracker')
    zp=f'New_Mexico_Clerk_Letters_District_{d}_{lab}.zip'; mk(PKG+zp,rows,tx); sizes[d]=dict(file=zp,n=len(rows),label=lab.replace('_',' '),counties=sorted(r['county_display'] for r in rows))
shutil.copy2(B+'out/NM_Planning_District_Lookup.csv',PKG+'New_Mexico_County_to_District_Lookup.csv')
for k,v in sizes.items(): v['mb']=round(os.path.getsize(PKG+v['file'])/1e6,1)
json.dump(sizes,open(B+'out/zip_sizes.json','w'),indent=1); print(json.dumps(sizes)[:600])
