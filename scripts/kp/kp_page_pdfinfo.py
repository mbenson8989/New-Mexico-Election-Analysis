from kp_pages_common import *
import json
R=Reg('pdfinfo'); v=R.v
M=json.load(open('/workspace/nm-election/verification/kp_pdf_meta.json'))
CK=json.load(open('/workspace/nm-election/verification/kp_pdf_cell_check.json'))
assert CK['mismatches']==0
assert R.raw('pdf.order')[0]==M['first']
PDF='New_Mexico_33_County_Democratic_Registration_and_Vote_Change.pdf'
body=f"""# New Mexico County PDF Information

{BANNER}

This {M['pages']}-page PDF covers all 33 New Mexico counties, 2022 vs 2026{S}, in the same layout as the Nebraska 93-county and Kansas 105-county PDFs. For each county it lists Democratic registration, Democratic governor votes and total ballots cast, each with the change as a number and a percent. Counties are sorted by 2026 Democratic share of registration, highest first ({M['first']} first; {M['bigreg']} has the most registered Democrats). The statewide total is the last row.

**[Download the New Mexico 33-County PDF]({PDF})** · [view it on GitHub]({REPO}/blob/main/{PDF})

## Columns

| Column | What it shows |
|---|---|
| County | New Mexico county |
| Population (Jul 1, 2025) | U.S. Census Bureau Vintage 2025 estimate, shown for size only |
| Dem Reg Share 2026 % | Democratic registered voters ÷ all registered voters, SOS "Statewide by County" report of Oct 30, 2026. This is the sort order |
| Dem Reg 2022 (Oct 31) / Dem Reg 2026 (Oct 30) | Democratic registered voters from the SOS "Statewide by County" registration reports |
| Reg Change # / % | Dem Reg 2026 − Dem Reg 2022, and that change ÷ Dem Reg 2022 × 100 |
| Dem Gov Votes 2022 / 2026{S} | Votes for the Democratic governor and lieutenant governor ticket (Lujan Grisham 2022, Haaland 2026{S}) |
| Vote Change # / % | Dem Gov Votes 2026{S} − 2022, and that change ÷ 2022 votes × 100 |
| Total Ballots† 2022 / 2026{S} | Total ballots cast in the county, SOS turnout figures |
| Total Ballot Change # / % | Total Ballots 2026{S} − 2022, and that change ÷ 2022 ballots × 100 |

Shading: rows shaded blue are counties where Democratic registration rose ({', '.join(M['up'])}). Red vote-change figures mark counties where Democratic governor votes fell ({', '.join(M['down'])}).

**†Why "total ballots".** New Mexico uses total ballots cast, the same basis as the Nebraska PDF. The SOS publishes ballots cast by county for both years, so New Mexico does not need the Kansas governor-votes workaround.

## Statewide totals row

| Measure | 2022 | 2026{S} | Change # | Change % |
|---|---|---|---|---|
| Dem Reg Share 2026 % | | {v('sw.R26','pct1')} | | |
| Democratic registration | {v('sw.regdem22','int')} | {v('sw.regdem26','int')} | {v('sw.regdem_change','sint')} | {v('sw.regdem_pct','spct1')} |
| Democratic governor votes | {v('sw.dem22','int')} | {v('sw.dem26','int')}{S} | {v('sw.dem_change','sint')}{S} | {v('sw.dem_pct','spct1')} |
| Total ballots cast | {v('sw.ballots22','int')} | {v('sw.ballots26','int')}{S} | {v('sw.ballots_change','sint')}{S} | {v('sw.ballots_pct','spct1')} |

## Verification

Every cell was computed twice by independent programs (pass A and pass B, which must produce identical strings before the PDF is written), and then checked cell by cell against the raw SOS files: the 2022 and 2026 SOS county-level result exports, the SOS turnout figures, the Oct 31, 2022 and Oct 30, 2026 "Statewide by County" registration reports and the Census population file. The check extracts the text from the PDF and compares each displayed figure with the value recomputed at its displayed rounding: {CK['cells']:,} cells, {CK['mismatches']} mismatches. Scripts and reports are in the [repo]({REPO}) (`scripts/kp/kp_pdf_check.py`, `verification/kp_pdf_cell_check.json`).

The earlier New Mexico county table, from the first build, is still available: [New-Mexico-County-Data.pdf](New-Mexico-County-Data.pdf).

{related('New-Mexico-County-PDF-Information')}"""
write(R,'New-Mexico-County-PDF-Information.md',body); print('pdfinfo ok')
