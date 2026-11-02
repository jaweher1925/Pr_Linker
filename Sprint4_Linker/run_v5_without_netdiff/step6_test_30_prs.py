"""
step6_test_30_prs.py - the 30-PR test Mohamed asked for (30 Oct).

Takes 30 merged AI PRs that have at least one follow-up within 30 days (all_changes, code files),
spread over the agents, and lists up to 3 follow-ups each (the closest in time), with GitHub links.
You open each pair and fill the yellow columns -> precision of the linker + limitations.

Run (normal Python, needs pandas + openpyxl):   python step6_test_30_prs.py
Output: Test_30_PRs.xlsx (in this folder)
"""
import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from paths import HERE, RAW_V5, RESULTS

N_PRS, PER_PR, SEED = 30, 3, 42
NET = os.path.exists(os.path.join(RESULTS, "net_all_changes_30_60", "candidate_pairs.parquet"))
RUN = "net_all_changes_30_60" if NET else "all_changes_30_60"     # net diff (paper) when step4b was run
print(f"pairs from results/{RUN}")
pairs = pd.read_parquet(os.path.join(RESULTS, RUN, "candidate_pairs.parquet"))
pairs = pairs[pairs.within_30d]
pr = pd.read_parquet(os.path.join(RAW_V5, "pull_request.parquet"), columns=["id", "title", "html_url"]) \
       .drop_duplicates("id").set_index("id")

# 30 AI PRs spread over the agents (proportional, at least 2 per agent when possible)
ai = pairs.groupby(["original_pr_id", "original_agent"]).size().reset_index()[["original_pr_id", "original_agent"]]
share = ai.original_agent.value_counts(normalize=True)
quota = (share * N_PRS).round().clip(lower=2).astype(int)
while quota.sum() > N_PRS:
    quota[quota.idxmax()] -= 1
picked = pd.concat([g.sample(min(quota.get(a, 0), len(g)), random_state=SEED)
                    for a, g in ai.groupby("original_agent")])

rows = []
for k, (pid, agent) in enumerate(picked.itertuples(index=False), 1):
    fu = pairs[pairs.original_pr_id == pid].sort_values("days_after_merge").head(PER_PR)
    for j, f in enumerate(fu.itertuples(), 1):
        rows.append({
            "test_id": f"T{k:02d}.{j}", "ai_agent": agent,
            "ai_pr_url": pr.html_url.get(pid), "ai_pr_title": pr.title.get(pid),
            "followup_url": pr.html_url.get(f.followup_pr_id), "followup_title": pr.title.get(f.followup_pr_id),
            "followup_agent": f.followup_agent, "followup_type": f.followup_task_type,
            "days_after": round(f.days_after_merge, 1), "shared_files": "; ".join(f.shared_files),
            "1_same_code_changed? (yes/no)": "", "2_corrects_the_AI_code? (yes/no)": "",
            "3_what_was_wrong (Q2)": "", "4_how_it_was_fixed (Q3)": "", "notes": ""})
out = os.path.join(HERE, "Test_30_PRs_netdiff.xlsx" if NET else "Test_30_PRs.xlsx")
if os.path.exists(out):   # never overwrite the sheet you may have filled by hand
    out = out.replace(".xlsx", "_NEW.xlsx")
    print(f"sheet already exists -> keeping it, writing {os.path.basename(out)}")
df = pd.DataFrame(rows)
with pd.ExcelWriter(out) as xw:
    df.to_excel(xw, sheet_name="Test 30 PRs", index=False)
    pd.DataFrame({"How to check": [
        "Open the AI PR and the follow-up PR (Files changed tab).",
        "1 same code changed: does the follow-up change the lines / function the AI PR wrote? (not only the same file)",
        "2 corrects the AI code: yes = it fixes a bug, a missing check, error handling, performance or design problem in the AI code; no = new feature, docs, style, unrelated",
        "3 what was wrong: e.g. missing null check, wrong condition, wrong API call, crash, slow loop",
        "4 how it was fixed: e.g. added a check, changed a condition, replaced a call",
        "Precision = rows with 2 = yes / all rows"]}).to_excel(xw, sheet_name="How to check", index=False)

wb = load_workbook(out); ws = wb["Test 30 PRs"]
yellow = PatternFill("solid", fgColor="FFF2CC")
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3864")
    c.alignment = Alignment(wrap_text=True, vertical="center")
dv = DataValidation(type="list", formula1='"yes,no"', allow_blank=True); ws.add_data_validation(dv)
widths = [8, 12, 40, 40, 40, 40, 12, 10, 8, 40, 14, 14, 30, 30, 30]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[ws.cell(1, i).column_letter].width = w
for r in range(2, ws.max_row + 1):
    for col in range(11, 16):
        ws.cell(r, col).fill = yellow
    dv.add(f"K{r}:L{r}")
    for col in (3, 5):
        c = ws.cell(r, col)
        if c.value: c.hyperlink = c.value; c.font = Font(color="0563C1", underline="single")
wb["How to check"].column_dimensions["A"].width = 120
wb.save(out)
print(f"{len(picked)} AI PRs, {len(df)} pairs -> {out}")
print(picked.original_agent.value_counts().to_string())
