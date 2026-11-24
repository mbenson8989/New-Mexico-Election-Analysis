from kp_pages_common import *
import json, csv
B='/workspace/nm-election/'
R=Reg('resources'); v=R.v
Z=json.load(open(B+'out/zip_sizes.json')); EQ=json.load(open(B+'out/kp_equipment_summary_A.json'))
EQB=json.load(open(B+'verification/kp_equipment_check.json')); assert EQB.get('mismatches',0)==0
QC=json.load(open(B+'verification/kp_quote_check.json'))
clerks=list(csv.DictReader(open(B+'out/NM_County_Clerks.csv')))
assert len(clerks)==33 and all(c['clerk'].strip() for c in clerks)
eqrows=list(csv.DictReader(open(B+'out/NM_33_County_Voting_Equipment_VerifiedVoting.csv')))
assert len(eqrows)==33
order=R.raw('counties_pop_order'); cap=R.raw('ceiling5'); ten=R.use('ten.counties')
assert [r['County'] for r in eqrows]==order
dists=[k for k in Z if k!='all']
# ---- clerk letters
zl='\n'.join(f"- [Download District {k} ({Z[k]['label']}) county clerk letters (ZIP, {Z[k]['n']} counties, {Z[k]['mb']} MB)](downloads/{Z[k]['file']})" for k in dists)
dt='\n'.join(f"| {k}. {Z[k]['label']} | {Z[k]['n']} | {', '.join(Z[k]['counties'])} |" for k in dists)
assert sum(Z[k]['n'] for k in dists)==33
# ---- ten counties
n_cand=v('ten.n_candidates','int')
def trow(i,c):
    k=lambda x:f'c.{c}.{x}'
    f=c.replace(' ','_')
    return (f"| {i} | {c} | {v(k('population'),'int')} | {v(k('regdem22'),'int')} → {v(k('regdem26'),'int')} ({v(k('reg_change'),'sint')}) | "
            f"{v(k('dem22'),'int')} → {v(k('dem26'),'int')}{S} ({v(k('vote_change'),'sint')}{S}, {v(k('vote_pct'),'spct1')}{S}) | **{v(k('gap_votes'),'sint')}{S}** | {v(k('gap_share_ballots26'),'pct1')} | [PNG](resources/social-media/NM_Flip_{i:02d}_{f}.png) |")
ttab='\n'.join(trow(i,c) for i,c in enumerate(ten,1))
def tcard(i,c):
    k=lambda x:f'c.{c}.{x}'; f=c.replace(' ','_')
    return (f"**{i}. {c} County**: registered Democrats {v(k('regdem22'),'int')} → {v(k('regdem26'),'int')} ({v(k('reg_change'),'sint')}); Democratic governor votes {v(k('dem22'),'int')} → {v(k('dem26'),'int')}{S} ({v(k('vote_change'),'sint')}{S}); value {v(k('gap_votes'),'sint')}{S}.\n\n"
            f"[![{c} County](resources/social-media/NM_Flip_{i:02d}_{f}.png)](resources/social-media/NM_Flip_{i:02d}_{f}.png)")
tcards='\n\n'.join(tcard(i,c) for i,c in enumerate(ten,1))
# ---- equipment
tot=EQ['_total_pop']; vend=[(k,x) for k,x in EQ.items() if not k.startswith('_')]
assert tot==R.raw('sw.population') and len(vend)==1 and vend[0][1]['counties']==33 and vend[0][1]['population']==tot
swp=v('sw.population','int')
vs=f"- **{vend[0][0]}:** 33 counties (100.0% of counties); population {swp} (100.0% of the 33-county total of {swp})"
eh='| County | FIPS | Population | Marking method | Voting location | ED tabulator vendor | ED tabulator equipment | Mail tabulator equipment | Accessible device | Paper record / VVPAT | Software/firmware | Poll book | Status | Source | Notes |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |'
def erow(r):
    st='Confirmed' if r['Status'].startswith('Confirmed') else r['Status']
    return f"| {r['County']} | {r['FIPS']} | {cty(R,r['County'],'population','int')} | {r['Marking method']} | {r['Voting location']} | {r['ED tabulator vendor']} | {r['ED tabulator equipment']} | {r['Mail tabulator equipment']} | {r['Accessible device']} | {r['Paper record / VVPAT']} | {r['Software/firmware']} | {r['Poll book']} | {st} | [Verifier]({r['Source']}) | {r['Notes']} |"
etab='\n'.join(erow(r) for r in eqrows)
for r in eqrows: assert int(r['Population'])==R.raw(f"c.{r['County']}.population")
pb=EQ['_pollbook']; loc=EQ['_location']
VF=open(B+'scripts/kp/src/old_vote_flip_section.md').read().replace('### Vote-flip county graphics','### Earlier vote-flip and surge graphics (first New Mexico build)',1)
ld=EQ['_mail_changed']
body=f"""# Resources

> **\\*2026 figures are unofficial.** The New Mexico Secretary of State's 2026 general-election results are labeled "Unofficial Results" (last updated 11/12/2026 11:07 AM MT); the State Canvassing Board approves the canvass on the third Tuesday after the election, November 24, 2026 (NMSA 1978, § 1-13-15). 2022 figures are the SOS official results. New Mexico has party registration, so "registration" on this wiki means registered Democrats from the SOS "Statewide by County" registration reports.

This page collects the documents, data sources, laws, equipment records, and graphics behind the New Mexico Election Analysis in one place. Everything here is offered as analysis and as draft correspondence. Nothing on this page is an accusation against any county, official, or vendor.

## Letter to the New Mexico Attorney General

A draft letter to Attorney General Raúl Torrez (New Mexico Department of Justice) asking his office to say publicly, for example in an advisory letter or an update to its Inspection of Public Records Act Compliance Guide, whether a cast vote record is a "digitized equivalent" of ballots or one of the "records requisite to voting" under NMSA 1978, § 1-12-69(D), and whether it is open under the Inspection of Public Records Act (IPRA, NMSA 1978, §§ 14-2-1 to 14-2-12) once that section's sixty-day period ends; how IPRA applies to an existing cast vote record export (§ 14-2-9); and to help make sure 2026 election records are kept for the full twenty-two months (§ 1-12-69(A)(1); 52 U.S.C. § 20701). It cites the Guarantee Clause (U.S. Const. art. IV, § 4) and the Article II enforcement-duty language in Executive Order 14399, and it says plainly that New Mexico, through the Attorney General, is a plaintiff challenging Executive Order 14399 and, in *California v. Trump*, Executive Order 14248. It asks for public guidance rather than a formal opinion, because formal opinions under § 8-5-2(D) answer questions from the legislature, state officials and district attorneys. It is respectful and non-accusatory, and it presents the New Mexico analysis as a hypothesis, not proof. It is a draft for Morissa to review and send herself; it has not been sent.

- [Download the Attorney General letter (PDF)](New_Mexico_Attorney_General_Letter.pdf)
- [Download the Attorney General letter (Word)](New_Mexico_Attorney_General_Letter.docx)

Every quotation in the letters was checked word for word against the official text of the statute, order, judgment, or release it quotes ({QC['quotes']} quotations in {QC['files']} files, {QC['missing']} not found). The addressee and office address are from the [New Mexico Department of Justice](https://nmdoj.gov/).

## County clerk letters

One letter for each of New Mexico's 33 counties, addressed to that county's elected county clerk, who conducts elections in the county, in both PDF and Word. Each county also has a separate, formal **Inspection of Public Records Act request** for the same records, for anyone who prefers to send a plain records request. Each ZIP has a `PDF` folder and a `Word` folder with both documents for each county, plus a delivery tracker (Excel) for those counties. Pick your district, or download everything at once.

- **[Download all 33 New Mexico county clerk letters and IPRA requests (ZIP, 33 counties, {Z['all']['mb']} MB)](downloads/{Z['all']['file']})**

By district:

{zl}

Not sure which district your county is in? [Download the county-to-district lookup (CSV)](downloads/New_Mexico_County_to_District_Lookup.csv), or use the table below.

**Track delivery.** [Download the 33-county letter delivery tracker (Excel)](downloads/New_Mexico_33_County_Letter_Delivery_Tracker.xlsx): one row per county with the clerk's name and phone number, check boxes for emailed and hand delivered, and running totals. Each district ZIP has its own tracker for its counties.

**How the counties are grouped.** The New Mexico Secretary of State does not divide the state into election regions; each county clerk runs the county's elections. So these files use a standard official grouping that covers all 33 counties exactly once: the **seven planning and development districts listed in the Planning District Act, NMSA 1978, § 4-58-2** ([official text, Chapter 4](https://nmonesource.com/nmos/nmsa/en/item/4372/index.do)). The statute numbers the districts; the short names (Northwest, North Central and so on) are added here for convenience. The grouping has nothing to do with how the letters or the analysis were built.

**What each letter contains.** The letters follow Morissa's Nebraska 93-county cast-vote-record request letter and the Kansas clerk letters, in the same tone and structure, rewritten for New Mexico law: the county's own 2022 and 2026{S} figures for registered Democrats, Democratic governor votes and total ballots cast; federal litigation context (New Mexico is a plaintiff in *California v. Trump* and in the challenge to Executive Order 14399; no standing claimed); an IPRA request for existing records only (cast vote record export, with the limits of § 1-12-69(D) stated; canvass returns, which § 1-13-23(A) makes public documents; the § 1-14-13.2 voting system check records; the § 1-9-7.9(F) and (G) test printouts and audit-trail reports; hash-verification records; and confirmation that removable storage media were not cleared early, § 1-13-21(A)); a request, not a demand, for wider hand-count coverage; how a denial should be explained (§ 14-2-11(B)); and blank date, signature, and sender lines. Addressees and mailing addresses come from the [New Mexico Secretary of State's County Clerk Information page](https://www.sos.nm.gov/voting-and-elections/county-clerk-information/), retrieved November 24, 2026. All 33 counties had a clerk's name and address on that page, so no addressee is a placeholder. One email address is incomplete on that page (Mora County); the tracker flags it to confirm by phone. Please confirm each addressee against the county's own website before sending, because officials change. Nothing has been mailed or emailed.

| District | Counties | County list |
|---|---|---|
{dt}

## New Mexico Secretary of State data sources

Every election number on this wiki comes from the New Mexico Secretary of State (SOS):

- **2022 general election (official):** [SOS election results, 2022 General](https://electionresults.sos.nm.gov/resultsSW.aspx?type=SW&map=CTY&eid=2838): Governor and Lieutenant Governor, "County Level" export and county results pages (last updated 11/29/2022 4:39 PM MT)
- **2026 general election (unofficial{S}):** [SOS election results, 2026 General](https://electionresults.sos.nm.gov/resultsSW.aspx?type=SW&map=CTY), labeled "Unofficial Results", last updated 11/12/2026 11:07 AM MT; downloaded November 19, 2026
- **Ballots cast by county:** [SOS Voter Turnout page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx) and each county's turnout export (they agree in all 66 county-years)
- **Voter registration by county and party:** SOS "Statewide by County" reports as of [October 31, 2022](https://www.sos.nm.gov/sos-archive/voter-statistics-data-archive/2022-voter-statistics-data/) and [October 30, 2026](https://www.sos.nm.gov/voting-and-elections/data-and-maps/voter-registration-statistics/2026-voter-registration-data/)
- **County clerks:** [SOS County Clerk Information](https://www.sos.nm.gov/voting-and-elections/county-clerk-information/), used for the clerk-letter addressees
- **Post-election audit:** [SOS Election Audits page](https://www.sos.nm.gov/voting-and-elections/election-audits/) (the voting system check, NMSA 1978, § 1-14-13.2)
- **Voting system certification:** [SOS Voting System Certification page](https://www.sos.nm.gov/voting-and-elections/how-we-secure-your-vote/voting-system-certification-nformation/) (NMSA 1978, § 1-9-7.9)

County populations (used only to sort the tables) are [U.S. Census Bureau Vintage 2025 estimates](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv) (July 1, 2025).

## County-level results

- [New Mexico County PDF Information](New-Mexico-County-PDF-Information): what each column of the county PDF means
- [Download the 33-county PDF](New_Mexico_33_County_Democratic_Registration_and_Vote_Change.pdf): registered Democrats, Democratic governor votes, and total ballots cast for every county, 2022 vs 2026{S}, with changes and statewide totals
- [33-County Data (CSV)](NM_Governor_2022_2026_DeltaG_by_County.csv): the county figures as a spreadsheet
- Choose any county on the [SOS results site](https://electionresults.sos.nm.gov/resultsSW.aspx?type=SW&map=CTY) to see its 2026 returns

## Voting equipment by county

This table lists the in-person and mail-ballot equipment Verified Voting records for each of New Mexico's 33 counties. It is offered as background on how ballots are marked and counted. **Equipment information is context only. It is not evidence of wrongdoing, and a vendor name does not imply a problem with that county's results.**

**Why Verified Voting.** The New Mexico Secretary of State's Voting System Certification page describes how systems are certified but, in the SOS pages checked on November 24, 2026, gives no county-by-county equipment list. So, as on the Texas and Kansas wikis, equipment comes from [Verified Voting's Verifier](https://verifiedvoting.org/verifier/): the public CSV download for New Mexico (state FIPS 35), years 2026 and 2022, plus the public county API behind each Verifier county page, retrieved November 24, 2026, 4:47 PM CST (America/Chicago). Each county row links to its Verifier county page. Population figures are Census July 1, 2025 estimates, so the list reads in the same largest-to-smallest order as the other New Mexico tables.

**Confirmed vs. unconfirmed.** A county is marked *Confirmed* when Verified Voting's 2026 record lists an election-day tabulator for it. All 33 counties meet that test; **{33-EQ['_n_confirmed']} counties are unconfirmed**.

### Statewide vendor summary (2026 election-day tabulators)

Counts below use the election-day tabulator Verified Voting lists for each county. Poll books and the email and fax channels for military and overseas voters are not counted as the election-day tabulator.

{vs}

Every New Mexico county uses the same election-day tabulator: the Liberty Vote (Dominion) ImageCast Evolution, a hybrid optical scanner and ballot-marking device. Marking method: all {EQ['_marking']['Hand marked paper ballots and BMDs']} counties use hand-marked paper ballots with ballot-marking devices available. Voting location: {loc['Vote Center']} counties use vote centers and {loc['Assigned Polling Place']} use assigned polling places.

The downloadable CSV also records each county's poll book, 2022 election-day tabulator equipment, status, source link, and notes.

### Download the full table

- CSV (all 33 counties and all columns): [NM_33_County_Voting_Equipment_VerifiedVoting.csv](NM_33_County_Voting_Equipment_VerifiedVoting.csv) (raw download link)

### All 33 counties, largest to smallest

{eh}
{etab}

### Gaps and what Verified Voting does not list

- **New Mexico SOS county equipment list:** none found on the SOS pages checked November 24, 2026 (see above). If the SOS publishes one, this table should be cross-checked against it.
- **Software and firmware versions:** Verified Voting's county API has hardware, firmware and software version fields, but they are empty for every machine in all 33 counties. Every row shows "Not listed by Verified Voting." Versions were not inferred from anywhere else.
- **Post-election audit codes:** the county API's audit fields (comprehensiveness, binding, audit type) are blank for every New Mexico county in this retrieval. New Mexico's audit rule is the voting system check, NMSA 1978, § 1-14-13.2 (see the laws table below).
- **Missing election-day tabulator:** none. **Missing mail-ballot tabulator:** none. **No accessible device listed:** none.
- **Multiple tabulator vendors in one county:** none.
- **Absentee ballots counted on a central (batch-fed) scanner (ImageCast Central):** {len(EQ['_central_mail'])} counties ({', '.join(EQ['_central_mail'])}). The other {len(EQ['_mail_on_ed_unit'])} count absentee ballots on the ImageCast Evolution.
- **Election-day tabulator model changed from 2022 to 2026 in Verified Voting:** none. **Mail tabulator changed:** {', '.join(ld)} (the 2022 model is in the county's Notes).
- **Vendor renamed, same model:** in all {len(EQ['_renamed'])} counties the 2022 record lists "Dominion" and the 2026 record lists "Liberty Vote (Dominion)" for the same tabulator model. That is a change in how the vendor is named, not a change in equipment.
- **Poll books:** AES AutoVote in {pb['AES AutoVote']} counties, Robis AskED ePollbook in {pb['Robis AskED ePollbook']}, and a paper poll book in {pb['Paper Poll Book']} ({', '.join(EQ['_paper_pollbook'])}).
- Every county also lists email and fax options for military and overseas voters. Those are special-purpose channels, not the county's ordinary in-person or mail tabulator, and are omitted from the vendor counts above.

Please treat this as a snapshot of Verified Voting's records as of the retrieval date. County equipment can change, and official questions about a county's system should be confirmed with the county clerk or the New Mexico Secretary of State.

## Graphics

Charts and shareable graphics built from this wiki's data. Tap an image to open it full size. The full chart set, with captions, is on [Graphs](Graphs). The social-media graphics are kept together in their own folder, [`resources/social-media`]({REPO}/tree/main/resources/social-media).

### Vote-share change bars sorted by 2022 Democratic share

[![2022 Democratic share and 2026 change, sorted by 2022 share](NM_governor_2022_Dem_share_vs_gain_bar_chart.png)](NM_governor_2022_Dem_share_vs_gain_bar_chart.png)

*All 33 counties sorted by 2022 Democratic share of ballots cast. Blue is the 2022 share; orange is the 2022 to 2026{S} gain; red below zero is a decline. The Democratic share rose in {v('n_S_rose','int')} counties and fell in {v('n_S_fell','int')}{S}.*

### Ceiling counties

[![Ceiling counties Delta-G by population](NM_Ceiling_Counties_DeltaG_by_Population.png)](NM_Ceiling_Counties_DeltaG_by_Population.png)

*Ceiling counties (the five highest ΔG): {', '.join(f"{x} {cty(R,x,'dG','pt2')}{S}" for x in cap)}.*

### Charts from the Graphs page

- [County slope chart, G 2022 to G 2026{S}](NM_Slope_G2022_to_G2026_County_Slope_Chart.png)
- [Forward surplus fit, S against D](NM_Forward_Surplus_Fit_S_vs_D.png)
- [ΔG bars by population](NM_DeltaG_Bars_by_Population.png) and [ΔG scatter with county names](NM_DeltaG_by_Population_Scatter_Names.png)
- [Stacked share bars with registration loss, by population](NM_Stacked_Share_Reg_Loss_by_Population.png) and [sorted by 2022 Democratic share](NM_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png)
- [Expected-loss residual bars by population](NM_Expected_Loss_Residual_Bars_by_Population.png)

### Ten counties: fewer registered Democrats, more Democratic votes

In each of these ten New Mexico counties, the number of registered Democrats went **down** from 2022 to 2026, while Democratic votes for governor went **up**.

**How they are ranked.** The ranking value is the number of Democratic votes **beyond what the change in Democratic registration would predict**:

`Value = D votes 2026\\* − D votes 2022 × (Dem registration 2026 ÷ Dem registration 2022)`

In plain terms: if 2022 Democratic votes had risen or fallen by the same percentage as Democratic registration, how many votes would 2026 have? The value is how many more votes there actually were. It is the same measure used on the Nebraska and Kansas wikis' Resources pages, so the states compare directly. It is also the "Gap in votes" column on [Reverse-Math](Reverse-Math{EL_ANCHOR}). Counties are ranked from the biggest value down. Only counties where Democratic registration fell **and** Democratic votes rose are ranked: {n_cand} of New Mexico's 33 counties. Value is rounded to whole votes. The last column divides the value by the county's 2026{S} ballots cast, New Mexico's denominator.

[![Ten-county summary](resources/social-media/NM_Flip_00_Summary_Top10.png)](resources/social-media/NM_Flip_00_Summary_Top10.png)

| Rank | County | Population (2025) | Registered Dems 2022 → 2026 (change) | Dem governor votes 2022 → 2026\\* | Value (votes beyond registration)\\* | Share of 2026\\* ballots cast | Graphic |
|---|---|---|---|---|---|---|---|
{ttab}

Data file: [NM_Top10_Flip_Counties.csv]({REPO}/blob/main/resources/social-media/NM_Top10_Flip_Counties.csv). This is an observation about the numbers. Candidate choice, turnout, the change in the candidate field and voters crossing party lines can all move the value, and the arithmetic cannot separate those from other causes.

#### The ten graphics

{tcards}

<!-- vf-begin -->
{VF}<!-- vf-end -->

### Did you know? The Guarantee Clause

[![Guarantee Clause graphic](resources/social-media/NM_Guarantee_Clause.png)](resources/social-media/NM_Guarantee_Clause.png)

Downloads: [portrait 1080×1350 (PNG)](resources/social-media/NM_Guarantee_Clause.png) · [landscape 1600×900 (PNG)](resources/social-media/NM_Guarantee_Clause_Landscape.png)

**Sources**

- U.S. Constitution, Article IV, Section 4: "The United States shall guarantee to every State in this Union a Republican Form of Government, and shall protect each of them against Invasion; and on Application of the Legislature, or of the Executive (when the Legislature cannot be convened) against domestic Violence."
- [Executive Order 14399, "Ensuring Citizenship Verification and Integrity in Federal Elections"](https://www.federalregister.gov/documents/2026/04/03/2026-06601/ensuring-citizenship-verification-and-integrity-in-federal-elections), signed March 31, 2026, published April 3, 2026 at 91 FR 17125. Section 1: "The Federal Government has an unavoidable duty under Article II of the Constitution of the United States to enforce Federal law, which includes preventing violations of Federal criminal law and maintaining public confidence in election outcomes." The order separately cites "the Federal Government's constitutional obligation to guarantee a republican form of Government to every State in the Union, U.S. Const. Art. IV, Sec. 4." The words "unavoidable duty" belong to the Article II sentence, not to the Guarantee Clause itself.
- Morissa Benson's write-up: [A pattern you can't unsee]({SUBSTACK}).

## Where the method began: the Cedar County audit

The method was first worked out in Morissa Benson's [Cedar County Audit]({CEDAR}) in her Nebraska Election Analysis wiki. This New Mexico wiki applies the same approach using New Mexico's own numbers only.

## The reverse-factoring method in brief

1. **Two shares per county, per year.** For each of the 33 counties, in 2022 and in 2026{S}, take (a) the Democratic share of all ballots cast and (b) **D**, the Democratic share of all registered voters. New Mexico has party registration, so D is real registration, not a stand-in.
2. **The surplus.** The surplus is (a) − D, in percentage points: the Democratic share of ballots cast minus the Democratic share of registration. The wiki's other pages call this G.
3. **The New Mexico line.** Graph every county's surplus against its D and fit one straight line: **S = multiplier × (D/100) + offset**. New Mexico's own 33 counties, weighted equally, give:
   - **2022:** S = {v('fit.2022.m','f2')} × (D/100) {signed_term(R,'fit.2022.b')}, R² {v('fit.2022.r2','f3')}
   - **2026{S} (unofficial):** S = {v('fit.2026.m','f2')} × (D/100) {signed_term(R,'fit.2026.b')}, R² {v('fit.2026.r2','f3')}. The 2026 line uses unofficial figures and will be refit after certification.
4. **Residuals, floor and ceiling.** A county's residual is its actual surplus minus the surplus the line predicts. See [Floor and Ceiling Counties](Floor-and-Ceiling) and [Locked New Mexico Formula](Locked-New-Mexico-Formula).
5. **Checked against the source.** Two independent programs rebuilt every county figure from the raw SOS files and agreed, with 0 mismatches.

The [README](README) explains it all in plain language. This is an analytical model, with evidence for and against. It is not proof of anything.

## New Mexico laws cited in the letters

| Law | What it covers | Official text |
|---|---|---|
| NMSA 1978, § 14-2-1 | Inspection of Public Records Act: right to inspect, and the exceptions, including records withheld "as otherwise provided by law" (N) and the limits on the information-technology exception (J) | [Chapter 14](https://nmonesource.com/nmos/nmsa/en/item/4383/index.do) |
| § 14-2-5 | Purpose: all persons are entitled to the greatest possible information about the affairs of government | [Chapter 14](https://nmonesource.com/nmos/nmsa/en/item/4383/index.do) |
| § 14-2-6(H) | "Public records" include materials regardless of physical form or characteristics | [Chapter 14](https://nmonesource.com/nmos/nmsa/en/item/4383/index.do) |
| § 14-2-8(B), (D), (E) | No duty to create a record; inspection within fifteen days, with a written explanation if not within three business days; a request sent to the wrong person is forwarded to the custodian | [Chapter 14](https://nmonesource.com/nmos/nmsa/en/item/4383/index.do) |
| § 14-2-9(A), (B), (C) | Exempt and nonexempt information separated and the nonexempt part released; electronic records in the format in which they exist; fees | [Chapter 14](https://nmonesource.com/nmos/nmsa/en/item/4383/index.do) |
| § 14-2-11(B) | A written denial must explain the reason and name each person responsible | [Chapter 14](https://nmonesource.com/nmos/nmsa/en/item/4383/index.do) |
| § 14-2-12(A)(1) | An action to enforce the Act may be brought by the Attorney General or the district attorney | [Chapter 14](https://nmonesource.com/nmos/nmsa/en/item/4383/index.do) |
| § 1-12-69 | Ballots and records requisite to voting kept 22 months for federal elections; notice before destruction; ballots, their digitized equivalents and records requisite to voting exempt from third-party inspection for sixty days after the canvass, then by district court order | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 1-9-7.9(F), (G) | Voting systems print zero-results and results printouts for tests, and keep an audit trail in printed form | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 1-9-7.11 | Voting system source code placed in escrow | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 1-13-15 | State Canvassing Board meets the third Tuesday after the election | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 1-13-21(A) | Removable storage media not cleared until at least forty-five days after the canvassing board adjourns | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 1-13-23(A) | Returns and certificates of the county canvass are public documents | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 1-14-13.2 | Post-election voting system check: hand count of randomly selected precincts overseen by an independent auditor; results released to the public | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 1-14-22(B) | On petition by the Secretary of State or a county clerk, the district court may permit review of ballot images in place of paper ballots when returns are defective or missing | [Chapter 1](https://nmonesource.com/nmos/nmsa/en/item/4351/index.do) |
| § 8-5-2(D) | Attorney General opinions on questions submitted by the legislature, state officials and district attorneys | [Chapter 8](https://nmonesource.com/nmos/nmsa/en/item/4354/index.do) |
| § 4-58-2 | The seven planning and development districts (used only to group the letter downloads) | [Chapter 4](https://nmonesource.com/nmos/nmsa/en/item/4372/index.do) |
| Doña Ana County Clerk (May 29, 2026) | Public portal to view and verify ballot images and cast vote records for the November 4, 2025 local election | [County release](https://www.donaana.gov/news_detail_T7_R118.php) |

## Federal sources cited

- [U.S. Constitution](https://www.archives.gov/founding-docs/constitution-transcript): Article IV, § 4 (Guarantee Clause) and Article II, § 3 (Take Care)
- Executive Order 14399, "Ensuring Citizenship Verification and Integrity in Federal Elections," signed March 31, 2026, 91 Fed. Reg. 17125: [Federal Register](https://www.federalregister.gov/documents/2026/04/03/2026-06601/ensuring-citizenship-verification-and-integrity-in-federal-elections) · [official PDF](https://www.govinfo.gov/content/pkg/FR-2026-04-03/pdf/2026-06601.pdf)
- 52 U.S.C. § 20701 (22-month retention of federal election records): [Cornell LII](https://www.law.cornell.edu/uscode/text/52/20701)
- Litigation context: *California v. Trump*, No. 1:25-cv-10810 (D. Mass.), [judgment and permanent injunction, July 13, 2026 (PDF)](https://storage.courtlistener.com/recap/gov.uscourts.mad.282905/gov.uscourts.mad.282905.194.0.pdf); [New Mexico Department of Justice release on the Executive Order 14399 challenge (Apr. 24, 2026)](https://nmdoj.gov/press-release/attorney-general-raul-torrez-moves-to-permanently-block-president-trumps-executive-order-restricting-mail-voting-exerting-control-over-elections/); [California Attorney General release on the Supreme Court stay (Aug. 24, 2026)](https://oag.ca.gov/news/press-releases/attorney-general-bonta-responds-us-supreme-court-decision-allowing-president)

## Morissa Benson on Substack

- [Morissa Benson's Substack](https://moebenson.substack.com/)
- [A pattern you can't unsee]({SUBSTACK})

---
*2026 figures are unofficial until the New Mexico State Canvassing Board approves the canvass (scheduled for November 24, 2026).*
"""
write(R,'Resources.md',body); print('resources ok', len(body.splitlines()))
