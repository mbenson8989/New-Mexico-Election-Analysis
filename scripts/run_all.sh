#!/bin/bash
# Kansas-parity rebuild of the New Mexico wiki from raw/ (no network). Fails on any verification mismatch.
# Does NOT run build_wiki.py / build_readme.py / build_resources.py / wiki_check.py (first-build page writers;
# build_wiki.py would rewrite the Locked page, which must stay byte for byte as it is).
set -e; cd "$(dirname "$0")"
LOCKED_SHA=0af726538da73c3e03cd1f8c00b8554583a72fd4221bfb3b2f8e17f31bc9ae27
locked(){ echo "$LOCKED_SHA  ../wiki/Locked-New-Mexico-Formula.md" | sha256sum -c --quiet || { echo "LOCKED PAGE CHANGED"; exit 1; }; }
locked
# first-build pipeline (both passes), charts, vote-flip and Guarantee Clause graphics, first-build PDF and its raw re-check
python3 pipeline.py
python3 verify_pass1.py
python3 verify_pass2.py
python3 compare.py
python3 -c "import json,sys;r=json.load(open('../verification/verification_report.json'));bad=[x for x in r['results'] if x['mismatched']];sys.exit('MISMATCH - does not ship' if bad else 0)"
python3 charts.py
python3 build_vote_flip.py
python3 build_guarantee_clause.py
python3 build_pdf.py
python3 verify_pdf.py
python3 -c "import json,sys;r=json.load(open('../verification/pdf_check.json'));sys.exit('PDF vs RAW MISMATCH' if r['mismatches'] or r['total_matched']!=r['total_checked'] else 0)"
# Kansas-parity build: two independent metric passes, then every output from pass A, re-checked against pass B
cd kp
python3 kp_metrics_a.py
python3 kp_metrics_b.py
python3 kp_compare.py
python3 -c "import json,sys;r=json.load(open('../../verification/kp_compare_report.json'));sys.exit(0 if r['CLEAN'] and r['keys_compared']>0 else 'KP PASS A/B MISMATCH')"
python3 kp_equipment.py
python3 kp_equipment_b.py
python3 -c "import json,sys;r=json.load(open('../../verification/kp_equipment_check.json'));sys.exit('EQUIPMENT MISMATCH' if r['mismatches'] or not r['checks'] else 0)"
python3 kp_extra.py
python3 kp_charts.py
python3 kp_cards.py
python3 kp_clerks.py
python3 kp_letters.py
python3 kp_ag_letter.py
python3 kp_verify_quotes.py
python3 -c "import json,sys;r=json.load(open('../../verification/kp_quote_check.json'));sys.exit('QUOTE NOT FOUND' if r['missing'] or not r['quotes'] else 0)"
python3 kp_docs.py
python3 kp_pdf.py
python3 kp_pdf_check.py
python3 -c "import json,sys;r=json.load(open('../../verification/kp_pdf_cell_check.json'));sys.exit('PDF CELL MISMATCH' if r['mismatches'] or not r['cells'] else 0)"
python3 kp_datacsv.py
python3 kp_page_home.py
python3 kp_page_readme.py
python3 kp_page_rm.py
python3 kp_page_fc.py
python3 kp_page_graphs.py
python3 kp_page_pdfinfo.py
python3 kp_page_resources.py
cp ../../out/NM_33_County_Voting_Equipment_VerifiedVoting.csv ../../wiki/
python3 kp_check_pages.py
python3 kp_check_links.py
cd ..
python3 verify_vote_flip.py
python3 -c "import json,sys;r=json.load(open('../verification/vote_flip_check.json'));sys.exit('VOTE-FLIP MISMATCH' if r['mismatches'] or r['matched']!=r['total_checks'] or r['total_checks']==0 or r['resources_md_cells_checked']==0 else 0)"
locked
echo ALL OK
