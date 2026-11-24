# New-Mexico-Election-Analysis
New Mexico 2022 vs 2026 Governor race, built the same way as the Kansas Election Analysis: G and ΔG (Democratic share of ballots cast minus Democratic share of registration), the New Mexico-only forward surplus fit S = m × (D/100) + b, floor and ceiling counties, the expected-loss residual and backward-solved offset votes (Nebraska / Iowa / South Dakota method), gap in votes, and a ballots-cast check. All 33 counties, largest to smallest population, double-verified against the raw New Mexico Secretary of State files. 2026 figures are UNOFFICIAL (SOS "Unofficial Results"; state canvass Nov 24, 2026). Analytical model and hypothesis, not a claim of fraud.

- Wiki: https://github.com/mbenson8989/New-Mexico-Election-Analysis/wiki
- Method origin: https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit
- Data: New Mexico Secretary of State results site (electionresults.sos.nm.gov: 2022 General official, 2026 General unofficial), SOS voter-turnout pages, and SOS Voter Registration Statistics "Statewide by County" reports (Oct 31, 2022 and Oct 30, 2026); population from U.S. Census Vintage 2025.

Contents:
- `NM_Governor_2022_2026_DeltaG_by_County.csv`: all 33 counties with G, ΔG, expected loss, residual, offset votes and gap in votes.
- `New_Mexico_33_County_Democratic_Registration_and_Vote_Change.pdf`: the 33-county PDF (Kansas / Nebraska layout).
- `NM_*.png`: the charts on the wiki's Graphs, Floor-and-Ceiling, Reverse-Math and Resources pages (`nm_*.png`: charts from the first build).
- `New_Mexico_Attorney_General_Letter.pdf` / `.docx`: draft letter to the New Mexico Attorney General (not sent).
- `downloads/`: county clerk letters and Inspection of Public Records Act requests for all 33 counties (PDF and Word), by planning district, the county-to-district lookup and the Excel delivery trackers.
- `NM_33_County_Voting_Equipment_VerifiedVoting.csv`: voting equipment by county (Verified Voting, retrieved Nov 24, 2026).
- `resources/social-media/`: the ten-county graphics and the Guarantee Clause graphic. `resources/vote-flip/` and `resources/guarantee-clause/`: graphics from the first build.
- `NM_33_County_Governor_Table.csv`, `New-Mexico-County-Data.pdf`: tables from the first build.
- `scripts/`, `verification/`: the build and verification scripts and their reports.
