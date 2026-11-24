from kp_pages_common import *
R=Reg('readme'); v=R.v
PDFURL='New_Mexico_33_County_Democratic_Registration_and_Vote_Change.pdf'
body=f"""# README: Start Here

> **\\*2026 numbers are UNOFFICIAL.** They come from the New Mexico Secretary of State's results site, which labels them "Unofficial Results" (last updated 11/12/2026 11:07 AM MT). The State Canvassing Board approves the canvass on November 24, 2026. Numbers may change a little.

Welcome. If you have never seen this wiki before, this page is for you. It explains what we did, where the numbers came from, and what they do and do not mean.

## 1. Where every number comes from

Every vote count and every voter-registration count on these pages comes straight from the **New Mexico Secretary of State's official website**. We did not use polls. We did not use news reports. We did not use anyone's estimate. Population numbers come from the U.S. Census Bureau.

The exact pages and files we used:

| What | Where it came from |
|---|---|
| 2022 governor votes, every county | [New Mexico SOS results site: 2022 General, Governor and Lieutenant Governor, "County Level" export](https://electionresults.sos.nm.gov/resultsSW.aspx?type=SW&map=CTY&eid=2838) (listed on the [SOS 2022 election results page](https://www.sos.nm.gov/sos-archive/election-results-archive/2022-election-results/)) |
| 2026 governor votes, every county (unofficial) | [New Mexico SOS results site: 2026 General](https://electionresults.sos.nm.gov/resultsSW.aspx?type=SW&map=CTY), last updated 11/12/2026 11:07 AM MT |
| Ballots cast, every county, both years | [New Mexico SOS Voter Turnout page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx) and each county's turnout export |
| Registered voters by party, as of Oct 31, 2022 | [New Mexico SOS: 2022 Voter Statistics Data, "Statewide by County"](https://www.sos.nm.gov/sos-archive/voter-statistics-data-archive/2022-voter-statistics-data/) |
| Registered voters by party, as of Oct 30, 2026 | [New Mexico SOS: 2026 Voter Registration Data, "Statewide by County"](https://www.sos.nm.gov/voting-and-elections/data-and-maps/voter-registration-statistics/2026-voter-registration-data/) |
| County population | [U.S. Census Bureau, 2025 county estimates](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv) |

We checked every number twice, in two separate ways, against these original files.

## 2. See the data yourself

You do not have to take our word for anything. The sidebar has a page called **[New Mexico County PDF Information](New-Mexico-County-PDF-Information)**. It links to a PDF with all 33 counties: Democratic registrations, Democratic votes for governor, and total ballots cast, 2022 next to 2026\\*.

**[Open the New Mexico 33-County PDF]({PDFURL})**

Pick your own county. Check the numbers against the Secretary of State's website.

## 3. This is a hypothesis, not a settled fact

Please read this part carefully.

We are **not** saying we have proven anything. We are asking a question.

The idea is this. If election manipulation exists, it is probably not one trick. It would likely be many methods working together. Each one leaves its own kind of trace. This analysis looks at only one of them: the link between **who is registered** and **how people voted**. It is one lens, not the whole picture.

A pattern in the numbers is not proof of why the pattern is there. Other things can explain it: the candidates, who showed up to vote, voters switching sides, and more. We show the pattern so that people can look closer.

## 4. Morissa's write-up

Morissa Benson explains the full hypothesis, in her own words, on her Substack. Start with this post:

**[A pattern you can't unsee: What the paper trail shows]({SUBSTACK})**

More of her writing is at [moebenson.substack.com](https://moebenson.substack.com/).

## 5. What "reverse-factoring" means

Think of a recipe. A recipe tells you how much of each ingredient goes in. "Reverse-factoring" works the other way. You look at the finished dish and ask what the recipe must have been.

Here is how it works for one county.

1. **Look at who is registered.** Take the share of all registered voters who are Democrats. Call this **D**. If 30 out of 100 registered voters are Democrats, D is 30%.
2. **Look at the vote.** Take the Democratic governor candidate's votes as a share of all ballots cast. Call this the vote share.
3. **Find the surplus.** Subtract: vote share minus D. The leftover is the **surplus**, called **S**. It is measured in percentage points. If Democrats are 30% of registered voters but get 40% of the ballots, S is +10.
4. **Find the usual pattern.** We draw the best straight line through all 33 New Mexico counties, with S on one side and D on the other. That line is the "usual" recipe. (In New Mexico the line is nearly flat: registration share tells you very little about the surplus.)
5. **Run it backward.** For any county, we can ask: given its D, what S does the usual line expect? How far is the county's real S from that?

The line is written like this:

> **S = multiplier × (D ÷ 100) + offset**

- **S** is the surplus, in percentage points (Democratic vote share minus Democratic registration share).
- **D** is the Democratic share of registered voters, in percent.
- **multiplier** says how fast S climbs as D goes up.
- **offset** is where the line starts when D is zero.

The multiplier and offset are not borrowed from any other state. We worked them out from New Mexico data only, for all 33 counties, once for 2022 and once for 2026\\*. They are listed on the [Locked New Mexico Formula](Locked-New-Mexico-Formula) page. The step-by-step build, starting with one county, is on [Bottom-Up Reverse Math](Reverse-Math).

**How we count:**
- The vote share is the Democratic governor candidate's votes divided by **all ballots cast** in that county (the Secretary of State's turnout figure).
- Registered voters means everyone on the Secretary of State's "Statewide by County" report for that date. New Mexico publishes registration by party, so D is the real share of registered Democrats.
- Governor race only.

## 6. How Morissa found these numbers

The method began in Nebraska. Morissa Benson built it while checking one small rural county, Cedar County, by hand ([Cedar County Audit]({CEDAR})). She then carried the same arithmetic county by county across other states. For New Mexico she used only New Mexico numbers and followed the same steps for every one of the 33 counties. Nothing was skipped and no county was left out.

## 7. Where to go next

- [Home](Home): the full list of pages.
- [Resources](Resources): ten shareable county graphics, a Guarantee Clause graphic, the Attorney General letter and the county clerk letters.
- [Bottom-Up Reverse Math](Reverse-Math): the step-by-step build.
- [Locked New Mexico Formula](Locked-New-Mexico-Formula): the equation.
- [Floor and Ceiling Counties](Floor-and-Ceiling) and [Graphs](Graphs).

*These pages measure a pattern. They make no claim about anyone's intent.*
"""
write(R,'README.md',body); print('readme ok')
