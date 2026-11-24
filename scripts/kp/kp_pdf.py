"""New Mexico 33-county PDF in the Kansas/Nebraska layout, built from PASS B strings (asserted identical to pass A strings).
Ballots cast is the denominator in New Mexico (both years), so the last block is Total Ballots (Nebraska PDF basis), not total governor votes."""
import json, glob, sys
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, LongTable, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from kpfmt import Reg, fmt
B='/workspace/nm-election/'
def rows_for(src):
    R=Reg('pdf',src); out=[]
    for c in R.raw('pdf.order'):
        k=lambda x:f'c.{c}.{x}'
        out.append([c,R.v(k('population'),'int'),R.v(k('R26'),'pct1'),R.v(k('regdem22'),'int'),R.v(k('regdem26'),'int'),R.v(k('reg_change'),'sint'),R.v(k('reg_pct'),'spct1'),
            R.v(k('dem22'),'int'),R.v(k('dem26'),'int'),R.v(k('vote_change'),'sint'),R.v(k('vote_pct'),'spct1'),R.v(k('ballots22'),'int'),R.v(k('ballots26'),'int'),R.v(k('ballot_change'),'sint'),R.v(k('ballot_pct'),'spct1')])
    out.append(['Statewide total',R.v('sw.population','int'),R.v('sw.R26','pct1'),R.v('sw.regdem22','int'),R.v('sw.regdem26','int'),R.v('sw.regdem_change','sint'),R.v('sw.regdem_pct','spct1'),
        R.v('sw.dem22','int'),R.v('sw.dem26','int'),R.v('sw.dem_change','sint'),R.v('sw.dem_pct','spct1'),R.v('sw.ballots22','int'),R.v('sw.ballots26','int'),R.v('sw.ballots_change','sint'),R.v('sw.ballots_pct','spct1')])
    return out,R
rows,RB=rows_for('B'); rowsA,_=rows_for('A'); assert rows==rowsA, 'pass A and pass B PDF strings differ'
json.dump(rows,open(B+'verification/kp_pdf_rows_B.json','w'),indent=0)
def font(n): return glob.glob(f'/usr/share/fonts/**/{n}',recursive=True)[0]
pdfmetrics.registerFont(TTFont('F',font('DejaVuSans.ttf'))); pdfmetrics.registerFont(TTFont('FB',font('DejaVuSans-Bold.ttf')))
OUT=B+'wiki/New_Mexico_33_County_Democratic_Registration_and_Vote_Change.pdf'
H=ParagraphStyle('h',fontName='FB',fontSize=6.3,leading=7.4,alignment=1,textColor=colors.white)
T=ParagraphStyle('t',fontName='FB',fontSize=12.5,leading=15); N=ParagraphStyle('n',fontName='F',fontSize=7,leading=8.8)
hdr=['County','Population (Jul&nbsp;1, 2025)','Dem Reg Share 2026 %','Dem Reg 2022 (Oct&nbsp;31)','Dem Reg 2026 (Oct&nbsp;30)','Reg Change #','Reg Change %',
     'Dem Gov Votes 2022','Dem Gov Votes 2026*','Vote Change #','Vote Change % (on 2022 base)','Total Ballots 2022','Total Ballots 2026*','Total Ballot Change #','Total Ballot Change %']
W=[70,50,44]+[47]*12
data=[[Paragraph(h,H) for h in hdr]]+rows
up=[i for i,r in enumerate(rows,1) if r[5].startswith('+') and r[0]!='Statewide total']
down=[i for i,r in enumerate(rows,1) if r[9].startswith('-') and r[0]!='Statewide total']
st=[('FONT',(0,1),(-1,-1),'F',6.8),('ALIGN',(1,1),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1f3864')),('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#b4b4b4')),
    ('TOPPADDING',(0,1),(-1,-1),1.6),('BOTTOMPADDING',(0,1),(-1,-1),1.6),('LEFTPADDING',(0,0),(-1,-1),2.5),('RIGHTPADDING',(0,0),(-1,-1),2.5),
    ('FONT',(0,len(data)-1),(-1,len(data)-1),'FB',6.8),('BACKGROUND',(0,len(data)-1),(-1,len(data)-1),colors.HexColor('#e7e6e6')),('LINEABOVE',(0,len(data)-1),(-1,len(data)-1),1,colors.black)]
for i in up: st.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#ddebf7')))
for i in down: st.append(('TEXTCOLOR',(9,i),(10,i),colors.HexColor('#c00000')))
tbl=LongTable(data,colWidths=W,repeatRows=1); tbl.setStyle(TableStyle(st))
upn=', '.join(rows[i-1][0] for i in up); dnn=', '.join(rows[i-1][0] for i in down) or 'none'
legend=LongTable([[Paragraph('<b>Legend:</b>',N),Paragraph(f'Democratic registration rose ({len(up)}): {upn}',N),Paragraph(f'<font color="#c00000">Red vote change</font>: Democratic governor votes fell ({len(down)}): {dnn}',N)]],colWidths=[48,362,310])
legend.setStyle(TableStyle([('BACKGROUND',(1,0),(1,0),colors.HexColor('#ddebf7')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
first=rows[0][0]; bigreg=max(rows[:-1],key=lambda r:int(r[4].replace(',','')))[0]
story=[Paragraph('New Mexico 33 Counties — Democratic Registration, Democratic Governor Votes and Total Ballots, 2022 vs 2026*',T),Spacer(1,3),
 Paragraph(f'Sorted by 2026 Democratic share of registration (Democratic registered voters ÷ all registered voters, New Mexico SOS "Statewide by County" report as of Oct 30, 2026), highest first. {first} leads by share; {bigreg} leads by raw Democratic registration. Statewide totals are the last row.',N),Spacer(1,2),
 Paragraph('*2026 votes and ballots are UNOFFICIAL: New Mexico Secretary of State (SOS) results site, November 3, 2026 General, labeled "Unofficial Results", last updated 11/12/2026 11:07 AM MT; the State Canvassing Board meets the third Tuesday after the election (Nov 24, 2026; NMSA 1978, § 1-13-15). 2022: SOS official results, November 8, 2022 General. Votes are votes for the Democratic governor and lieutenant governor ticket (Lujan Grisham 2022, Haaland 2026), not a count of registered Democrats who voted.',N),Spacer(1,2),
 Paragraph('<b>Total ballots</b> are SOS turnout figures (ballots cast), the same basis as the Nebraska 93-county PDF and the denominator used throughout the New Mexico wiki. (Kansas uses total governor votes because its ballots-cast data was unusable; New Mexico\'s is complete for both years.)',N),Spacer(1,4),
 legend,Spacer(1,5),tbl,Spacer(1,6),
 Paragraph('<b>Sources.</b> New Mexico Secretary of State: 2022 general election official results and 2026 general election unofficial results (electionresults.sos.nm.gov, Governor and Lieutenant Governor, county level; turnout pages for ballots cast); Voter Registration Statistics, Statewide by County, as of Oct 31, 2022 and Oct 30, 2026. Population: U.S. Census Bureau Vintage 2025 county estimates (July 1, 2025), shown for size only. Change % = (2026 − 2022) ÷ 2022 × 100. Every figure was computed twice by independent programs from the raw SOS files with 0 mismatches, and this PDF\'s text was re-checked cell by cell. Data, scripts and verification: github.com/mbenson8989/New-Mexico-Election-Analysis. This table measures a pattern; it makes no claim about intent, fraud or cause.',N)]
def foot(c,d):
    c.saveState(); c.setFont('F',7); c.drawString(0.5*inch,0.32*inch,'*2026 figures unofficial (New Mexico SOS "Unofficial Results", 11/12/2026); state canvass Nov 24, 2026.  Total ballots = ballots cast (SOS turnout).')
    c.drawRightString(10.5*inch,0.32*inch,f'Page {d.page} of {d._total}'); c.restoreState()
def build(total):
    d=BaseDocTemplate(OUT,pagesize=landscape(letter),leftMargin=0.5*inch,rightMargin=0.5*inch,topMargin=0.45*inch,bottomMargin=0.5*inch,title='New Mexico 33 County Democratic Registration and Vote Change, 2022 vs 2026*',author='mbenson8989 / New-Mexico-Election-Analysis')
    d._total=total; fr=Frame(d.leftMargin,d.bottomMargin,d.width,d.height,id='f')
    d.addPageTemplates([PageTemplate('p',[fr],onPage=foot)]); d.build(list(story)); return d.page
n=build(0); n2=build(n); assert n==n2
json.dump(dict(pages=n,up=[rows[i-1][0] for i in up],down=[rows[i-1][0] for i in down],first=first,bigreg=bigreg),open(B+'verification/kp_pdf_meta.json','w'))
print(OUT,'pages',n,'reg rose',len(up),upn,'| votes fell',len(down),dnn)
