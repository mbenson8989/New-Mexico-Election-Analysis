"""Build wiki/New-Mexico-County-Data.pdf from the VERIFIED tables (out/nm_county_table.csv, out/nm_share_fit_table.csv,
out/nm_share_fit.json). All 33 counties, largest to smallest population. Checked afterwards by verify_pdf.py (independent
re-parse of raw/) and wiki_check.py (both verification passes)."""
import csv, json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
O='/workspace/nm-election/out'; W='/workspace/nm-election/wiki'
T=list(csv.DictReader(open(f'{O}/nm_county_table.csv')))            # already in population order
SH={r['county']:r for r in csv.DictReader(open(f'{O}/nm_share_fit_table.csv'))}
SF=json.load(open(f'{O}/nm_share_fit.json'))['fmt']
assert len(T)==33 and [r['county'] for r in T]==sorted([r['county'] for r in T],key=lambda c:-int(next(x for x in T if x['county']==c)['population']))
c=lambda n:f'{int(n):,}'
ss=getSampleStyleSheet(); body=ParagraphStyle('b',parent=ss['BodyText'],fontSize=9,leading=12)
h1=ParagraphStyle('h1',parent=ss['Title'],fontSize=16); h2=ParagraphStyle('h2',parent=ss['Heading2'],fontSize=12)
note=ParagraphStyle('n',parent=body,backColor=colors.HexColor('#fff3cd'),borderColor=colors.HexColor('#e0b000'),borderWidth=0.8,borderPadding=5)
def tbl(rows,widths):
    t=Table(rows,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'Helvetica',7.5),('FONT',(0,0),(-1,0),'Helvetica-Bold',7),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dde6f0')),('ALIGN',(1,0),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID',(0,0),(-1,-1),0.25,colors.grey),('TOPPADDING',(0,1),(-1,-1),1.6),('BOTTOMPADDING',(0,1),(-1,-1),1.6),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f5f5')])]))
    return t
P=lambda s:Paragraph(s,ParagraphStyle('th',fontName='Helvetica-Bold',fontSize=7,leading=8.5,alignment=1))
UNOFF=('<b>* 2026 figures are UNOFFICIAL.</b> The New Mexico Secretary of State (SOS) results site labels the November 3, 2026 general '
       'election "Unofficial Results" (results last updated 11/12/2026 11:07 AM MT). They have not been certified and may change. Every column '
       'marked * uses 2026 unofficial votes or ballots. 2022 figures are the SOS "Official Results" for the November 8, 2022 general election. '
       'Registration counts for both years are from the SOS registration reports listed under Sources.')
st=[Paragraph('New Mexico County Data: Governor Race 2022 and 2026*',h1),Paragraph(UNOFF,note),Spacer(1,8),
 Paragraph('All 33 New Mexico counties, largest to smallest population. Democratic governor votes are votes for the Democratic ticket '
  '(Lujan Grisham 2022, Haaland 2026*). Ballots cast are from the SOS voter turnout reports. Every figure here was taken from the verified '
  'county table and re-checked against the raw SOS and Census files.',body),Spacer(1,6),
 Paragraph('Surplus Equation fits (S = multiplier x (D/100) + offset)',h2),
 Paragraph('D = Democratic registered voters / total registered voters x 100. Dem vote share = Democratic governor votes / ballots cast x 100. '
  'S (surplus, percentage points) = Dem vote share - D. Fitted S = multiplier x (D/100) + offset, fitted across the 33 counties, each county '
  'weighted equally, each year on its own. Residual = S - fitted S (the surplus/residual used by the pipeline).',body),Spacer(1,4)]
fit=[['Fit','Multiplier','Offset','R-squared','Mean abs. residual'],
     ['2026* (unofficial, locked)',SF['y2026']['m'],SF['y2026']['b'],SF['y2026']['r2'],SF['y2026']['mae']],
     ['2022 (official, reference)',SF['y2022']['m'],SF['y2022']['b'],SF['y2022']['r2'],SF['y2022']['mae']]]
st+=[tbl(fit,[150,70,70,70,90]),PageBreak()]
hdrA=['County','Population','Dem gov votes 2022','Ballots cast 2022','Dem reg 2022','Total reg 2022','Dem gov votes 2026*','Ballots cast 2026*','Dem reg 2026','Total reg 2026']
rowsA=[[P(h) for h in hdrA]]+[[r['county'],c(r['population']),c(r['dem22']),c(r['ballots22']),c(r['regdem22']),c(r['regtot22']),c(r['dem26']),c(r['ballots26']),c(r['regdem26']),c(r['regtot26'])] for r in T]
sm=lambda k:sum(int(r[k]) for r in T)
rowsA.append(['Statewide total',c(sm('population')),c(sm('dem22')),c(sm('ballots22')),c(sm('regdem22')),c(sm('regtot22')),c(sm('dem26')),c(sm('ballots26')),c(sm('regdem26')),c(sm('regtot26'))])
tA=tbl(rowsA,[80]+[71]*9); tA.setStyle(TableStyle([('FONT',(0,-1),(-1,-1),'Helvetica-Bold',7.5)]))
st+=[Paragraph('Table 1. County inputs (counts), largest to smallest population',h2),tA,PageBreak()]
hdrB=['County','Dem vote share % 2022','D % 2022','S 2022','Fitted S 2022','Residual 2022','Dem vote share % 2026*','D % 2026','S 2026*','Fitted S 2026*','Residual 2026*']
rowsB=[[P(h) for h in hdrB]]+[[r['county'],r['S22'],r['R22'],SH[r['county']]['G22'],SH[r['county']]['shfit22'],SH[r['county']]['shres22'],
        r['S26'],r['R26'],SH[r['county']]['G26'],SH[r['county']]['shfit26'],SH[r['county']]['shres26']] for r in T]
st+=[Paragraph('Table 2. Shares, surplus S and Surplus Equation residuals (percent / percentage points), largest to smallest population',h2),
     tbl(rowsB,[80]+[64]*10),PageBreak()]
SRC=['<b>2022 governor votes by county:</b> New Mexico Secretary of State election results site (electionresults.sos.nm.gov), 2022 General, '
     'November 8, 2022, "Official Results", Governor and Lieutenant Governor race, "County Level" export; cross-checked against the SOS county results pages.',
     '<b>2026* governor votes by county:</b> SOS election results site, GENERAL 2026, November 3, 2026, "Unofficial Results" (last updated 11/12/2026 11:07 AM MT), '
     'Governor and Lieutenant Governor race, "County Level" export; cross-checked against the SOS county results pages.',
     '<b>Ballots cast by county:</b> SOS "Voter Turnout" details page (VoterTurnoutDetails.aspx; Ballots Cast summed over every precinct) for each election, '
     'cross-checked against the SOS per-county turnout exports ("Votes Cast"). 2026 ballots are unofficial*.',
     '<b>Party registration by county:</b> SOS "New Mexico Voter Registration Statistics - Statewide by County, As of October 31, 2022" and '
     '"Statewide by County, As of October 30, 2026" (linked from the SOS Voter Registration Statistics data pages).',
     '<b>Population (sort order only):</b> U.S. Census Bureau Vintage 2025 county population estimates (co-est2025-alldata.csv, POPESTIMATE2025).',
     'Source URLs, download times and SHA-256 hashes of every raw file are listed in raw/MANIFEST.md of the project.']
st+=[Paragraph('Sources',h2)]+[Paragraph(s,body) for s in SRC]+[Spacer(1,8),Paragraph(UNOFF,note),Spacer(1,8),
     Paragraph('This table measures a pattern. It makes no claim about intent, fraud or cause.',body)]
def foot(cv,doc):
    cv.saveState(); cv.setFont('Helvetica',7); cv.drawString(36,20,'New Mexico County Data. * 2026 figures are unofficial (SOS "Unofficial Results").')
    cv.drawRightString(756,20,f'Page {doc.page}'); cv.restoreState()
SimpleDocTemplate(f'{W}/New-Mexico-County-Data.pdf',pagesize=landscape(letter),leftMargin=36,rightMargin=36,topMargin=36,bottomMargin=36,
  title='New Mexico County Data 2022 and 2026 (2026 unofficial)',author='Morissa Benson').build(st,onFirstPage=foot,onLaterPages=foot)
print('pdf built')
