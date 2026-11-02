# run_v5 - everything to run linker_v5 on AIDev v5

## How to run
Double-click **RUN_ALL_v5.bat** (10-20 min). It runs steps 1 to 6.
Then open **step5_results_v5.html** (results) and **Test_30_PRs.xlsx** (manual check).

## The files (all in this folder)
| Step | File | What it does | Output |
|---|---|---|---|
| 1 | step1_download_v5.py | downloads AIDev v5 tables from Hugging Face (skips files already there) | 00_CODE/evolution-assurance/data/raw_v5/*.parquet |
| 2 | step2_task_type_v5.py | makes our own label (fix, feat...) from the PR title: prefix, else classifier trained on v3 | raw_v5/pr_task_type_v5.parquet |
| 3 | step3_build_lake_v5.py | builds the database: merged agent PRs + their CODE files | data/duckdb/aidev_v5.duckdb |
| 4 | step4_run_linker_v5.py | runs **linker_v5.py** twice (all_changes, fix_only; 30/60 days) | results/all_changes_30_60, results/fix_only_30_60 |
| 5 | step5_results_v5.ipynb | tables + charts per agent | step5_results_v5.html |
| 6 | step6_test_30_prs.py | picks 30 AI PRs for the manual check (never overwrites your filled sheet) | Test_30_PRs.xlsx (or Test_30_PRs_NEW.xlsx) |
| - | linker_v5.py | THE LINKER (one file). Called by step 4 | |
| - | paths.py | where the data and results are | |

## Is the linker one file?
linker_v5.py is one file, but it needs:
1. Mohamed's repo **00_CODE/evolution-assurance** (it imports `prfix.config`, and step 3 imports `prfix...boilerplate`). `uv run --project ...` uses it.
2. The data from steps 1-3 (the v5 tables + aidev_v5.duckdb).
So: always run it through RUN_ALL_v5.bat, not alone.
