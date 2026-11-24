"""Letter delivery tracker per TEMPLATE_SPEC (Nebraska structure): sheet 'Delivery Tracker', A-E County / Contact name / Phone number /
Emailed / Hand Delivered, navy header, freeze B2, ☐/☑ dropdown, green when ☑, COUNTIF/SUMPRODUCT totals in G-H; NM extensions after
a spacer, documented on a Sources sheet. Rows alphabetical (spec). Sender fields are not in the tracker."""
import openpyxl, json
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from kpfmt import Reg
SRC='https://www.sos.nm.gov/voting-and-elections/county-clerk-information/ (retrieved Nov 24, 2026, America/Chicago)'
def build(rows,path,title):
    V=Reg('trk').V; order=V['counties_pop_order']
    wb=openpyxl.Workbook(); ws=wb.active; ws.title='Delivery Tracker'
    ws.append(['County','Contact name','Phone number','Emailed','Hand Delivered'])
    rows=sorted(rows,key=lambda r:r['county_display'])
    for r in rows: ws.append([r['county_display'],r['clerk'],r['phone'],'☐','☐'])
    last=len(rows)+1; thin=Side(style='thin',color='999999')
    for cell in ws[1]:
        cell.font=Font(bold=True,color='FFFFFF'); cell.fill=PatternFill('solid',fgColor='1F4E78'); cell.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); cell.border=Border(top=thin,bottom=thin,left=thin,right=thin)
    for row in ws.iter_rows(min_row=2,max_row=last,min_col=4,max_col=5):
        for cell in row: cell.font=Font(size=14); cell.alignment=Alignment(horizontal='center')
    dv=DataValidation(type='list',formula1='"☐,☑"',allow_blank=True); ws.add_data_validation(dv); dv.add(f'D2:E{last}')
    ws.conditional_formatting.add(f'D2:E{last}',CellIsRule(operator='equal',formula=['"☑"'],fill=PatternFill('solid',fgColor='C6EFCE')))
    ws['G1']='Totals'; ws['G1'].font=Font(bold=True)
    ws['G2']='Emailed'; ws['H2']=f'=COUNTIF(D2:D{last},"☑")'
    ws['G3']='Hand delivered'; ws['H3']=f'=COUNTIF(E2:E{last},"☑")'
    ws['G4']='Not yet sent'; ws['H4']=f'=SUMPRODUCT((D2:D{last}<>"☑")*(E2:E{last}<>"☑"))'
    ws['G6']='Tap a box cell and pick ☑ to check it off.'
    EXT=['Official title','Mailing address','Email','Election email','FIPS','Planning district (NMSA 4-58-2)','Population 2025','Population rank (1 = largest)','Clerk letter file','IPRA request file','Notes','Source']
    for j,h in enumerate(EXT): 
        c=ws.cell(row=1,column=10+j,value=h); c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F4E78'); c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
    for i,r in enumerate(rows,2):
        f=r['county_display'].replace(' ','_').replace('ñ','n')
        vals=[r['title'],r['mailing_address'].replace(' | ',', '),r['email'] or '(none listed by SOS)',r['election_email'],r['fips'],f"District {r['planning_district']} ({r['district_label']})",
              V[f"c.{r['county']}.population"],order.index(r['county'])+1,f'{f}_County_Clerk_Letter.pdf / .docx',f'{f}_County_IPRA_Request.pdf / .docx',r.get('notes',''),SRC]
        for j,v in enumerate(vals): ws.cell(row=i,column=10+j,value=v)
        ws.cell(row=i,column=16).number_format='#,##0'
    for col,w in zip('ABCDEFGH',[16,30,18,12,16,3,16,10]): ws.column_dimensions[col].width=w
    for j,w in enumerate([14,44,36,32,8,30,12,12,40,40,50,60]): ws.column_dimensions[openpyxl.utils.get_column_letter(10+j)].width=w
    ws.freeze_panes='B2'
    s=wb.create_sheet('Sources')
    for line in [title,
      'Structure copied from the Nebraska 93-county CVR Letter Delivery Tracker (TEMPLATE_SPEC): one row per county, alphabetical; columns A-E County, Contact name, Phone number, Emailed, Hand Delivered; ☐/☑ dropdown, green when ☑; totals in G-H.',
      'New Mexico extensions (columns J-U, after the totals): official title, mailing address, email, election email, FIPS, NMSA 1978 § 4-58-2 planning district (the grouping used for the letter ZIPs; descriptive labels are added here, not statutory), population (Census Vintage 2025), population rank (the wiki sort order), letter and IPRA file names, notes, source.',
      'Contact names, phones, emails and mailing addresses: New Mexico Secretary of State, County Clerk Information, '+SRC+'. Party labels shown on the SOS page are omitted. Where the SOS lists a separate mailing address (Harding, Valencia), the mailing address is used.',
      'Mora County: the SOS page lists the clerk email as "vtrujillo@countyofmora" with no domain ending; it appears incomplete. Confirm by phone before emailing.',
      'Each county gets two documents: the clerk letter (Kansas format, with the hand-count request) and a formal Inspection of Public Records Act request (NMSA 1978, §§ 14-2-1 to 14-2-12).',
      'Drafts for Morissa Benson to review, sign and, only after approval, send. Date, signature, printed name, return address and phone are blank on purpose. Nothing in this workbook has been mailed, emailed, posted or pushed.']:
        s.append([line])
    s.column_dimensions['A'].width=160
    for row in s.iter_rows():
        for cell in row: cell.alignment=Alignment(wrap_text=True,vertical='top')
    s['A1'].font=Font(bold=True,size=14)
    wb.save(path); return path
