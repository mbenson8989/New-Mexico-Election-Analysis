#!/bin/bash
# Rebuild everything from raw/ (no network). Fails on any verification mismatch.
# Covers: change-vs-drop model (861 cells/comparison) + share version S = m*(D/100)+b + gap in votes (309 cells/comparison) + wiki table check
# + README.md and New-Mexico-County-Data.pdf: every number vs BOTH passes (wiki_check.py) and vs an independent raw/ re-parse (verify_pdf.py).
# + Resources: vote-flip graphics and Resources.md tables vs BOTH passes (verify_vote_flip.py); Guarantee Clause post/graphic (build_guarantee_clause.py).
set -e; cd "$(dirname "$0")"
python3 pipeline.py
python3 verify_pass1.py
python3 verify_pass2.py
python3 compare.py
python3 -c "import json,sys;r=json.load(open('../verification/verification_report.json'));bad=[x for x in r['results'] if x['mismatched']];sys.exit('MISMATCH - does not ship' if bad else ('SHARE-VERSION CELLS NOT COMPARED' if any(x.get('share_version_cells',0)!=309 for x in r['results']) else 0))"
python3 charts.py
python3 build_vote_flip.py
python3 build_guarantee_clause.py
python3 build_wiki.py
python3 verify_vote_flip.py
python3 build_readme.py
python3 build_pdf.py
python3 verify_pdf.py
python3 wiki_check.py
python3 -c "import json,sys;r=json.load(open('../verification/wiki_table_check.json'));sys.exit('WIKI MISMATCH' if r['mismatched'] or not r['reverse_math_tables_in_population_order'] else ('README/PDF MISMATCH' if r['readme_pdf_mismatches'] or any(r[b][k]['numbers_checked']==0 for b in ('readme_vs_pass','pdf_vs_pass') for k in ('1','2')) else 0))"
python3 -c "import json,sys;r=json.load(open('../verification/pdf_check.json'));sys.exit('PDF vs RAW MISMATCH' if r['mismatches'] or r['total_matched']!=r['total_checked'] else 0)"
python3 -c "import json,sys;r=json.load(open('../verification/vote_flip_check.json'));sys.exit('VOTE-FLIP MISMATCH' if r['mismatches'] or r['matched']!=r['total_checks'] or r['total_checks']==0 or r['resources_md_cells_checked']==0 else 0)"
echo ALL OK
