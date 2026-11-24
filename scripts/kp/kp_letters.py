"""New Mexico correspondence package, Kansas format adapted to New Mexico law:
- 33 county clerk letters (Kansas clerk-letter structure; IPRA instead of KORA; NM election code)
- 33 formal IPRA requests (NMSA 1978, 14-2-1 to 14-2-12), one per county clerk
- the Attorney General letter (Raul Torrez)
Every county number comes from the verified pass-A registry (logged per file; re-checked against pass B by kp_check_pages.py).
Names/addresses: SOS County Clerk Information page (out/NM_County_Clerks.csv). Nothing is sent."""
import csv, json, os
from kpfmt import Reg
B='/workspace/nm-election/'; L=B+'letters/'
for d in ('clerk/md','ipra/md','ag'): os.makedirs(L+d,exist_ok=True)
CL={r['county']:r for r in csv.DictReader(open(B+'out/NM_County_Clerks.csv'))}
EQ={r['County']:r for r in csv.DictReader(open(B+'out/NM_33_County_Voting_Equipment_VerifiedVoting.csv'))}
LOG=[]
def newreg(): return Reg('tmp')
def ch(R,c,a,b,chg,pct,star=''):
    return f"{R.v(f'c.{c}.{a}','int')} → {R.v(f'c.{c}.{b}','int')}{star} ({R.v(f'c.{c}.{chg}','sint')}{star}, {R.v(f'c.{c}.{pct}','spct1')}{star})"
def swch(R,a,b,chg,pct,star=''):
    return f"{R.v('sw.'+a,'int')} → {R.v('sw.'+b,'int')}{star} ({R.v('sw.'+chg,'sint')}{star}, {R.v('sw.'+pct,'spct1')}{star})"
UNOFF=("2022 figures are the Secretary of State's official results. *2026 figures are the Secretary of State's \"Unofficial Results\" "
       "(last updated Nov. 12, 2026, 11:07 AM MT) and are not final until the State Canvassing Board approves the canvass; the board meets on the third Tuesday "
       "after the election (Nov. 24, 2026), NMSA 1978, § 1-13-15. Registration counts are the Secretary of State's \"Statewide by County\" voter registration "
       "reports of Oct. 31, 2022 and Oct. 30, 2026. Total ballots are the Secretary of State's turnout figures. These are votes for the Democratic candidate "
       "for governor, not a count of registered Democrats who voted; that would require the voter-history file.")
LIT=("**Federal litigation context.** Executive Order 14248 (Mar. 25, 2025) was challenged in *California v. Trump*, No. 1:25-cv-10810 (D. Mass.), "
     "in which New Mexico, through Attorney General Raúl Torrez, is a plaintiff (judgment and permanent injunction July 13, 2026; New Mexico is one of the "
     "\"Ballot Receipt States\" protected by the injunction against Sections 7(a) and 7(b)), and in *LULAC v. Executive Office of the President*, No. 1:25-cv-0946 "
     "(D.D.C.) (permanent injunction as to Section 2(a), Oct. 31, 2025). New Mexico is also part of the 23-state coalition challenging Executive Order 14399 "
     "(Mar. 31, 2026) in the District of Massachusetts; on Aug. 24, 2026 the U.S. Supreme Court stayed that court's injunction without ruling on whether the "
     "Order is lawful. This letter takes no side in that litigation, does not rely on it for standing or for any new right to records, and mentions it only "
     "as context: the county's duties under the Inspection of Public Records Act and the Election Code stand independently, however the litigation resolves.")
order=Reg('x').raw('counties_pop_order')
SWR=newreg(); SW=(f"Statewide, registered Democrats changed {swch(SWR,'regdem22','regdem26','regdem_change','regdem_pct')} and Democratic votes for governor "
    f"changed {swch(SWR,'dem22','dem26','dem_change','dem_pct','*')}.")
merge=[]
for c in order:
    k=CL[c]; e=EQ[c]; R=newreg(); R.log=list(SWR.log)
    disp=k['county_display']; addr='\n'.join(k['mailing_address'].split(' | '))
    rd=R.raw(f'c.{c}.reg_change'); vd=R.raw(f'c.{c}.vote_change')
    if rd<0 and vd>0: pat='In this county, Democratic registration declined while Democratic votes for governor rose.'
    elif rd<0 and vd<0: pat='In this county, Democratic registration and Democratic votes for governor both declined.'
    elif rd>0 and vd>0: pat='In this county, Democratic registration and Democratic votes for governor both rose.'
    elif rd>0 and vd<0: pat='In this county, Democratic registration rose while Democratic votes for governor declined.'
    else: pat='In this county, at least one of these figures did not change.'
    eq=e['ED tabulator equipment']; mail=e['Mail tabulator equipment']
    eqs=(f"Verified Voting lists the county's election-day tabulator as {eq}" + (f" and its absentee (mail) tabulator as {mail}" if mail and mail!=eq else '') + "; please tell me if that has changed.")
    figs=(f"- Registered Democrats, Oct. 31, 2022 to Oct. 30, 2026: {ch(R,c,'regdem22','regdem26','reg_change','reg_pct')}\n"
          f"- Democratic votes for governor, 2022 to 2026: {ch(R,c,'dem22','dem26','vote_change','vote_pct','*')}\n"
          f"- Total ballots cast, 2022 to 2026: {ch(R,c,'ballots22','ballots26','ballot_change','ballot_pct','*')}")
    md=f"""# {disp.upper()} COUNTY — Clerk letter (records and audit request)

Date: ______________________

{k['clerk']}
County Clerk, {disp} County
{addr}

Re: November 3, 2026 general election — Inspection of Public Records Act request for existing election records, and request for additional post-election hand-count coverage, {disp} County

Dear County Clerk {k['salutation_surname']}:

I am writing as a member of the public concerning election records and post-election review for the November 3, 2026 general election in {disp} County, where you serve as the county clerk and conduct elections. Using New Mexico Secretary of State figures for the governor race, I compared the 2022 and 2026 general elections in {disp} County:

{figs}

{UNOFF}

{pat} {SW} I offer these figures as an observation, not an allegation. Candidate choice, turnout, and voters crossing party lines can all move them, and county totals alone cannot tell those causes apart. The cast vote record, which shows the ballots in their batches, is the record that could.

{LIT}

**Records request.** Under the Inspection of Public Records Act, NMSA 1978, §§ 14-2-1 to 14-2-12 ("public records" include materials "regardless of physical form or characteristics," § 14-2-6(H)), and in light of the retention requirements of NMSA 1978, § 1-12-69(A) and 52 U.S.C. § 20701, I request copies of the following existing records for the November 3, 2026 general election. A separate formal request listing the same records is enclosed.

- **Cast vote record export:** the full cast vote record (CVR) export for the election, if the county has generated or retained one, including batch identifiers, ballot sequence or position numbers, and all contests, in the electronic file format in which it exists (§ 14-2-9(B)), with any information that could identify a voter removed. {eqs} I understand that § 1-12-69(D) makes "paper ballots marked by voters, their digitized equivalents and records requisite to voting" exempt from third-party inspection until sixty days after the canvassing board adjourns, and after that allows inspection only "for good cause shown and upon order of the district court." If the county treats the CVR as a digitized equivalent or a record requisite to voting, please say so in writing, preserve it, and tell me the date from which it could be released or whether the county believes a court order is required.
- **Canvass returns and results printouts:** the county canvass report and certificate of results, which § 1-13-23(A) makes "public documents," and the precinct and tabulator results printouts (results tapes) used in the county canvass.
- **Voting system check records:** for any precinct in the county selected for the post-election voting system check under § 1-14-13.2, the auditor's notice of selection, the hand-count tally sheets, the comparison with the machine count, and the results the county reported to the auditor under § 1-14-13.2(E).
- **Equipment test and audit-trail records:** the zero-results and results printouts from pre-election testing under § 1-9-7.9(F), and the printed audit-trail reports of pre-election, election-day and post-election events under § 1-9-7.9(G).
- **Hash verification:** the hash values for the certified voting system version the county used, and any record of hash verification performed on that system, so they can be compared with the trusted build for the certified version. If no such record exists, please say so.
- **Removable storage media:** confirmation that the removable storage media devices were not cleared before the date allowed by § 1-13-21(A), forty-five days after the canvassing board adjourns, and that they will be preserved with the other records requisite to voting.

**Audit request (a request, not a records demand).** Under § 1-14-13.2 the auditor retained by the Secretary of State selects the precincts for the voting system check, and the county clerk hand counts the paper ballots from those precincts. I ask that the county consider a further hand count covering ballots from precincts representing at least thirty to forty percent of the county's total ballots, prioritizing the precincts with the highest ballot volume, so the sample reflects where most voters actually cast ballots, and that the counted ballots be compared with the cast vote record. This is a request, not a claim of statutory entitlement. Because § 1-12-69(D) restricts third-party inspection of ballots, I ask the county to perform or arrange any such count itself, in public and open to observers, and not to let me inspect ballots. If the county concludes it has no authority to do so, I ask that it say so in writing.

This request is limited to records that already exist; I understand that IPRA does not require a public body to create a record (§ 14-2-8(B)). If any record is withheld in whole or in part, I ask for the written explanation described in § 14-2-11(B), including the names and titles of each person responsible for the denial, that you tell me whether the record exists, and that you release any nonexempt part, separated as § 14-2-9(A) requires. If a record is held by another office, please forward this request and tell me where, as § 14-2-8(E) provides. I will pay reasonable copying costs under § 14-2-9(C); please tell me the estimated cost before proceeding.

Please confirm the addressee and mailing address if your office's information has changed since the Secretary of State's County Clerk Information page was retrieved on November 24, 2026.

Thank you for your time and for the work your office does to conduct elections.

Signature: _______________________________________________

Printed name: _______________________________________________

Address: _______________________________________________

Phone / email: _______________________________________________
"""
    fn=f"{disp.replace(' ','_').replace('ñ','n')}_County_Clerk_Letter.md"; open(L+'clerk/md/'+fn,'w').write(md)
    LOG.append(dict(file='letters/clerk/md/'+fn,entries=R.log))
    # formal IPRA request
    R2=newreg()
    ipra=f"""# {disp.upper()} COUNTY — Inspection of Public Records Act request

Date: ______________________

To: Records Custodian, Office of the County Clerk, {disp} County
Attn: {k['clerk']}, County Clerk
{addr}{(chr(10)+'Email: '+k['email']) if k['email'] else ''}

Re: Request to inspect and copy public records — November 3, 2026 general election, {disp} County

This is a written request under the Inspection of Public Records Act, NMSA 1978, §§ 14-2-1 to 14-2-12. As § 14-2-8(C) requires, my name, address and telephone number are given below, and the records are identified with as much particularity as I can. No reason is required for this request (§ 14-2-8(C)), but it relates to a county-level comparison of the 2022 and 2026 governor results.

**Records requested** (November 3, 2026 general election, {disp} County; existing records only):

1. The cast vote record (CVR) export for the election, if the county has generated or retained one, in the electronic file format in which it exists, with any information that could identify a voter removed. If the county considers the CVR a "digitized equivalent" or one of the "records requisite to voting" under NMSA 1978, § 1-12-69(D), please say so in writing, preserve it, and state when it may be inspected or whether a district court order is required.
2. The county canvass report and the certificate of results of the county canvass (§ 1-13-23(A)), and the tabulator results printouts used in the county canvass.
3. Records of the post-election voting system check under § 1-14-13.2 for any precinct in the county that was selected: the auditor's notice, the hand-count tally sheets, the comparison with machine counts, and the results reported to the auditor.
4. The zero-results and results printouts from pre-election testing (§ 1-9-7.9(F)) and the printed audit-trail reports (§ 1-9-7.9(G)) for the county's tabulators.
5. Any record of hash values or hash verification for the certified voting system software and firmware the county used.
6. Any record showing when the removable storage media devices used in the election were cleared or are scheduled to be cleared (§ 1-13-21).

**Format.** Please provide electronic copies where the records exist in electronic form (§ 14-2-9(B)), by email if possible (§ 14-2-8(F)).

**Timing.** Section 14-2-8(D) asks the custodian to permit inspection as soon as practicable and not later than fifteen days after receiving a written request, and to explain in writing within three business days if the records will not be available by then.

**Exempt material.** If any part of a record is exempt, please separate it and provide the rest (§ 14-2-9(A)). If any record is withheld, please provide the written explanation described in § 14-2-11(B). If a record is held by another custodian, please forward this request and tell me (§ 14-2-8(E)).

**Fees.** I agree to pay reasonable copying and media costs allowed by § 14-2-9(C). Please tell me the estimated cost before copying.

Requester name: _______________________________________________

Mailing address: _______________________________________________

Telephone: _______________________________________________

Email (optional): _______________________________________________

Signature: _______________________________________________
"""
    fn2=f"{disp.replace(' ','_').replace('ñ','n')}_County_IPRA_Request.md"; open(L+'ipra/md/'+fn2,'w').write(ipra)
    merge.append(dict(county=c,county_display=disp,clerk=k['clerk'],salutation=k['salutation_surname'],pattern=pat,ed_equipment=eq,mail_equipment=mail,letter=fn,ipra=fn2))
json.dump(dict(files=LOG),open(B+'verification/kp_log_letters.json','w'),indent=0)
with open(B+'out/clerk_letter_merge_fields.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(merge[0])); w.writeheader(); w.writerows(merge)
print('clerk letters',len(LOG),'ipra',len(merge)); print(SW)
