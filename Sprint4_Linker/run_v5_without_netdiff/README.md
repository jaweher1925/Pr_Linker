# run_v5_without_netdiff – linker_v5 with COMMIT FILES (first version)

This folder keeps the **first version** of the results, where rule 3 (shared file) uses the files of
**every commit** of a PR (v5 `pr_commit_details`). It is kept to compare with the net-diff version.

| Result | Value |
|---|---|
| Candidate pairs (all_changes, 60 days) | 152,697 |
| Claude Code follow-up rate, 30 days | 59.2% all_changes · 43.5% fix_only |
| Manual check (68 random pairs, seed 42) | 3 real fixes → precision 4.4% |
| False links caused by merged-in commit files | 26 of 68 (38%) |

Files: results/ (linker output), step5_results_v5.html + charts/ + tables/ (step 5),
Test_30_PRs.xlsx (sample) and Test_30_PRs_checked.xlsx (manual check, tab "Result").
Note: results/all_changes_30_60 keeps candidate_pairs.parquet (the .csv copy was too big and is not needed).

Run again: RUN_ALL_without_netdiff.bat (steps 1–6, no step 4b).
The net-diff version (like the paper) is in ../run_v5_with_netdiff.
