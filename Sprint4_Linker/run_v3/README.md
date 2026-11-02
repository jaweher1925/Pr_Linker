# run_v3 – ORIGINAL linker.py on AIDev v3 (the paper's data)

**Goal:** check that we reproduce the paper (Who Finishes the Job): ~2,510 candidate pairs, 22.9% of agent PRs with a candidate fix in 30 days.

**Run:** double-click `RUN_ALL_v3.bat` (or run the steps one by one), then open `step5_results.ipynb` → Run All.

| Step | File | What | Status |
|---|---|---|---|
| 1 | step1_download_data.py | 5 AIDev v3 tables → evolution-assurance/data/raw_linker | ✅ done |
| 2 | step2_load_tables.py | load them in the linker database (6,774 agent PRs, 5,044 human PRs) | ✅ done – rerun once (folder moved) |
| 3 | step3_fetch_changed_files.py | changed files of 5,781 PRs from GitHub | ✅ done |
| 4 | step4_run_linker.py | runs the original linker.py → results/ | ⬜ to do |
| 5 | step5_results.ipynb | per agent, who fixes, days, comparison with the paper, 50 pairs to annotate | ⬜ to do |

Code of the linker: 00_CODE/evolution-assurance (branch main).


Linker code: 00_CODE/evolution-assurance/src/prfix/rq1_fix_rates/linker.py (branch main)
