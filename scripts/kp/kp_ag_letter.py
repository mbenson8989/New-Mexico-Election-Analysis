"""Letter to New Mexico Attorney General Raul Torrez, Kansas AG-letter structure (sections 1-6 + Sources), New Mexico law.
Quotes are checked word for word by kp_verify_quotes.py; numbers come from the verified registry."""
from kpfmt import Reg
R=Reg('ag_letter'); B='/workspace/nm-election/'
n_votes_rose=R.v('n_votes_rose','int'); n_reg_fell=R.v('n_reg_fell','int')
md=f"""[Date]

The Honorable Raúl Torrez
Attorney General of New Mexico
New Mexico Department of Justice
408 Galisteo Street, Villagra Building
Santa Fe, NM 87501

Re: Request for public guidance on whether New Mexico cast vote records are public records under the Inspection of Public Records Act, how NMSA 1978, § 1-12-69(D) applies to them, and for help preserving 2026 election records

Dear Attorney General Torrez:

## 1. Who I am and why I am writing

"The United States shall guarantee to every State in this Union a Republican Form of Government." U.S. Const. art. IV, § 4. A republican form of government rests on elections the public can check for itself. I write to respectfully ask your office to help New Mexico's county clerks and the public do exactly that with the records New Mexico law already creates.

I am Morissa Benson, and I write regarding public access to New Mexico election records. I have studied the official 2022 and the unofficial 2026 New Mexico governor results, county by county, using only data from the New Mexico Secretary of State. I am not alleging that any county clerk, the Secretary of State, any vendor, or any employee did anything improper, and I am not alleging that any New Mexico result is wrong. I am asking for two things: (1) a clear public statement of how the Inspection of Public Records Act and the Election Code apply to cast vote records, and (2) your office's help in making sure the records needed to answer questions about the November 3, 2026 general election are preserved and made available as the law provides.

## 2. The federal framing: Executive Order 14399, and your office's position on it

On March 31, 2026, the President signed Executive Order 14399, "Ensuring Citizenship Verification and Integrity in Federal Elections," 91 Fed. Reg. 17125 (Apr. 3, 2026). Its authority clause rests in part on "the Federal Government's constitutional obligation to guarantee a republican form of Government to every State in the Union, U.S. Const. Art. IV, Sec. 4." Section 1 adds that "[t]he Federal Government has an unavoidable duty under Article II of the Constitution of the United States to enforce Federal law, which includes preventing violations of Federal criminal law and maintaining public confidence in election outcomes." That duty traces to the President's charge to "take Care that the Laws be faithfully executed." U.S. Const. art. II, § 3.

Section 5 of the Order states that "States and localities should preserve, for a 5-year period, all records and materials—excluding ballots cast—evidencing voter participation in any Federal election (e.g., ballot envelopes, regardless of carrier)."

I want to be candid about where your office stands. New Mexico, through your office, is one of the states challenging Executive Order 14399 in federal court; on April 24, 2026 your office announced that you had joined a coalition of 23 attorneys general seeking to permanently block its key provisions, and on August 24, 2026 the U.S. Supreme Court stayed the district court's injunction without deciding whether the Order is lawful. Your office is also a plaintiff in *California v. Trump*, No. 1:25-cv-10810 (D. Mass.), over Executive Order 14248. I do not ask you to change that position, and nothing in this letter depends on the Order being valid. The Order directs federal officers, not your office; Section 5's preservation language is phrased as "should"; and Section 7(c) says the Order creates no enforceable right. I cite it only because it states, at the federal level, a public interest the New Mexico Legislature declared long ago in the Inspection of Public Records Act: "all persons are entitled to the greatest possible information regarding the affairs of government and the official acts of public officers and employees." NMSA 1978, § 14-2-5.

## 3. What New Mexico law already provides

Electronic records are public records. The Act defines "public records" to include "all documents, papers, letters, books, maps, tapes, photographs, recordings and other materials, regardless of physical form or characteristics, that are used, created, received, maintained or held by or on behalf of any public body and relate to public business, whether or not the records are required by law to be created or maintained." NMSA 1978, § 14-2-6(H). A custodian must permit inspection "not later than fifteen days after receiving a written request." § 14-2-8(D). Where a record holds both kinds of information, "[r]equested public records containing information that is exempt and nonexempt from disclosure shall be separated by the custodian prior to inspection, and the nonexempt information shall be made available for inspection." § 14-2-9(A). A custodian "is only required to provide the electronic record in the file format in which it exists at the time of the request." § 14-2-9(B). A denial must be explained in writing, naming "the names and titles or positions of each person responsible for the denial." § 14-2-11(B).

The Election Code limits inspection of ballots for a time. Section 1-12-69(D) provides: "Paper ballots marked by voters, their digitized equivalents and records requisite to voting are exempt from third-party inspection except as otherwise provided in the Election Code until the later of sixty days following adjournment of the state or county canvassing board for that election or sixty days following any recount, contest or other judicial inquiry". After that, "a third-party inspection not otherwise provided for in the Election Code shall be conducted for good cause shown and upon order of the district court." Under § 14-2-1(N), records may be withheld "as otherwise provided by law," so § 1-12-69(D) is the provision that matters.

Preservation rules. Ballots and records requisite to voting must be kept for "twenty-two months from the date of the election for any election in which a federal office appears on the ballot." § 1-12-69(A)(1). Before destruction the clerk must give public notice at least seven days ahead. § 1-12-69(B). "The county clerk shall not clear the votes recorded on the removable storage media devices until at least forty-five days after adjournment of the county or state canvassing board, whichever is later." § 1-13-21(A). Federal law separately requires that records of elections for federal office be kept for 22 months. 52 U.S.C. § 20701.

Tabulation, testing, and audit records. Certified voting systems must be "capable of printing a zero-results printout prior to these tests and a results printout after the test," and must keep an internal audit trail so that "all pre-election, election day and post-election events shall be stored, recorded and recovered in an easy-to-read printed form." § 1-9-7.9(F), (G). "The returns and certificates of the result of the county canvass are public documents." § 1-13-23(A). After each general election, an independent auditor oversees a voting system check in which county clerks hand count the paper ballots of randomly selected precincts, and "[t]he auditor shall report the results of the voting system check to the secretary of state upon completion of the voting system check and release the results to the public." § 1-14-13.2(G). As a condition of certification, a voting system's source code is placed in escrow. § 1-9-7.11.

Where New Mexico has no exact parallel. Two points deserve candor. First, I did not find a New Mexico statute that names cast vote records. The Election Code speaks of "digitized equivalents" of ballots (§ 1-12-69(D)) and lets a district court permit "a review of ballot images in place of paper ballots" in a contest or recount (§ 1-14-22(B)), but it does not say whether a cast vote record, which records the choices on each ballot without the voter's name, is a "digitized equivalent," one of the "records requisite to voting," or neither. Second, I did not find a statute that, in so many words, requires a county to record hash-validation results for its voting system; the Act's exception for information technology systems expressly "shall not be used to restrict requests for" records "stored or transmitted using information technology systems" or "information to authenticate or validate records received pursuant to a request." § 14-2-1(J)(1), (3). How these provisions fit together for a cast vote record is where guidance from your office would help most.

Practice already varies. In May 2026 the Doña Ana County Clerk's Office launched a portal that "allows the public to view, compare, and independently verify ballot images and Cast Vote Records (CVRs) from the November 4, 2025 Regular Local Election," so that the public can see them "without submitting a formal public records request." Other counties may read § 1-12-69(D) differently. A public statement would help all 33 county clerks apply the same rule.

## 4. Why this matters for New Mexico now

My county-level comparison of the 2022 and 2026 governor races covers all 33 New Mexico counties and was checked cell by cell against the Secretary of State's own files. New Mexico has party registration, so I compare each county's Democratic share of ballots cast with its Democratic share of registered voters. Registered Democrats fell in {n_reg_fell} of 33 counties between the October 2022 and October 2026 registration reports, while Democratic votes for governor rose in {n_votes_rose}. The 2026 figures are unofficial until the State Canvassing Board approves the canvass on the third Tuesday after the election (NMSA 1978, § 1-13-15). What I have is an analytical model and a hypothesis, not proof. The only way to test a hypothesis like mine fairly is with the underlying records: cast vote records, ballot images where kept, and the testing and voting-system-check records described above. If those records show nothing unusual, that is a result worth having too.

## 5. Specific requests

I respectfully ask your office to:

1. State publicly, in whatever form your office considers appropriate (for example an advisory letter or an update to your office's Inspection of Public Records Act Compliance Guide), whether a cast vote record from the November 3, 2026 general election is a "digitized equivalent" of ballots or one of the "records requisite to voting" under § 1-12-69(D), and, if it is, whether it becomes open to inspection under the Inspection of Public Records Act once the sixty-day period ends, or only by district court order. I understand that formal opinions under § 8-5-2(D) are given on questions submitted by the legislature, state officials, and district attorneys, so I ask for public guidance rather than a formal opinion.
2. State your office's view on whether a custodian whose tabulation system can export cast vote records must provide an existing export in response to a request, in the file format in which it exists (§ 14-2-9(B)), and how § 14-2-9(A) applies if part of a record is exempt.
3. Remind county clerks, in coordination with the Secretary of State, that ballots, cast vote records, ballot images, removable storage media, testing printouts, audit-trail reports, and voting-system-check records for the 2026 general election should be kept for at least the full twenty-two-month period under § 1-12-69(A)(1) and 52 U.S.C. § 20701, and consider encouraging the five-year retention of participation records described in Section 5 of Executive Order 14399, whatever its legal force.
4. If your office finds it warranted, use its authority to enforce the Inspection of Public Records Act (§ 14-2-12(A)(1)) to review whether counties are responding to requests for 2026 election records as the Act requires, and share the results with the public.

I would be grateful for a written response within 30 days of the date of this letter. I am glad to provide my county-level data and methods to your staff.

## 6. Closing

New Mexicans, and the county clerks who run their elections, deserve records that let anyone check the count. New Mexico law already declares that the public is entitled to "the greatest possible information" about the affairs of government. A clear statement from your office would help county clerks apply the law the same way in all 33 counties, and it would help the public trust the result, whatever it shows.

Thank you for your attention to this request.

Respectfully,

Morissa Benson

## Sources

1. U.S. Const. art. IV, § 4; art. II, § 3. National Archives transcript: https://www.archives.gov/founding-docs/constitution-transcript
2. Executive Order 14399, "Ensuring Citizenship Verification and Integrity in Federal Elections," 91 Fed. Reg. 17125 (Apr. 3, 2026), FR Doc. 2026-06601. https://www.govinfo.gov/content/pkg/FR-2026-04-03/pdf/2026-06601.pdf
3. NMSA 1978, §§ 14-2-1, 14-2-5, 14-2-6, 14-2-8, 14-2-9, 14-2-11, 14-2-12 (Inspection of Public Records Act), official NMOneSource compilation, Chapter 14. https://nmonesource.com/nmos/nmsa/en/item/4383/index.do
4. NMSA 1978, §§ 1-9-7.9, 1-9-7.11, 1-12-69, 1-13-15, 1-13-21, 1-13-23, 1-14-13.2, 1-14-22 (Election Code), official NMOneSource compilation, Chapter 1. https://nmonesource.com/nmos/nmsa/en/item/4351/index.do
5. NMSA 1978, § 8-5-2 (duties of the attorney general), official NMOneSource compilation, Chapter 8. https://nmonesource.com/nmos/nmsa/en/item/4354/index.do
6. New Mexico Department of Justice, "Attorney General Raúl Torrez Moves to Permanently Block President Trump's Executive Order Restricting Mail Voting, Exerting Control over Elections" (Apr. 24, 2026). https://nmdoj.gov/press-release/attorney-general-raul-torrez-moves-to-permanently-block-president-trumps-executive-order-restricting-mail-voting-exerting-control-over-elections/
7. California Attorney General, press release on the U.S. Supreme Court's stay in the Executive Order 14399 case (Aug. 24, 2026). https://oag.ca.gov/news/press-releases/attorney-general-bonta-responds-us-supreme-court-decision-allowing-president
8. *California v. Trump*, No. 1:25-cv-10810 (D. Mass.), judgment and permanent injunction (July 13, 2026). https://storage.courtlistener.com/recap/gov.uscourts.mad.282905/gov.uscourts.mad.282905.194.0.pdf
9. Doña Ana County, "Clerk's Office Launches New Ballot Verification and Election Transparency Tool" (May 29, 2026). https://www.donaana.gov/news_detail_T7_R118.php
10. 52 U.S.C. § 20701. https://www.law.cornell.edu/uscode/text/52/20701
"""
open(B+'letters/ag/New_Mexico_Attorney_General_Letter.md','w').write(md)
R.save('letters/ag/New_Mexico_Attorney_General_Letter.md'); print('ok', n_reg_fell, n_votes_rose)
