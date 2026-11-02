"""
step0_data_analysis_v3_v5.py - quick data analysis of AIDev v3 and v5 (sizes, dates, agents).
Run:  uv run --project %EA% python step0_data_analysis_v3_v5.py
"""
import os
import duckdb
from paths import REPO
base = os.path.join(REPO, "data")
con = duckdb.connect()
def q(s): return con.sql(s).fetchall()
for name, d in [("AIDev v3 (AIDev-pop)", f"{base}/raw_linker"), ("AIDev v5 (AIDev-7.6M)", f"{base}/raw_v5")]:
    pr, rp = f"'{d}/pull_request.parquet'", f"'{d}/repository.parquet'"
    print("="*60); print(name); print("="*60)
    cols = [c[0] for c in con.sql(f"DESCRIBE SELECT * FROM {rp}").fetchall()]
    star = "stars" if "stars" in cols else [c for c in cols if "star" in c][0]
    t = q(f"""SELECT COUNT(*), COUNT(DISTINCT repo_id), COUNT(merged_at),
              MIN(CAST(created_at AS DATE)), MAX(CAST(created_at AS DATE)) FROM {pr}""")[0]
    print(f"PRs: {t[0]:,} | repos: {t[1]:,} | merged: {t[2]:,} ({t[2]/t[0]*100:.1f}%)")
    print(f"created from {t[3]} to {t[4]}")
    m5 = q(f"""SELECT COUNT(*) FROM {pr} p JOIN {rp} r ON r.id=p.repo_id
              WHERE p.merged_at IS NOT NULL AND r.{star} >= 500""")[0][0]
    print(f"merged PRs in repos >=500 stars: {m5:,}")
    print("per agent (PRs, merged %):")
    for a, n, mg in q(f"SELECT agent, COUNT(*), COUNT(merged_at) FROM {pr} GROUP BY 1 ORDER BY 2 DESC"):
        print(f"   {a:<14} {n:>10,}   {mg/n*100:5.1f}%")
    print("tables:", sorted(__import__('os').listdir(d)))
    if "v5" in name:
        print("merged PRs in repos >=500 stars, by language (top 5):")
        for lang, n in q(f"""SELECT r.language, COUNT(*) FROM {pr} p JOIN {rp} r ON r.id=p.repo_id
                            WHERE p.merged_at IS NOT NULL AND r.stars >= 500 GROUP BY 1 ORDER BY 2 DESC LIMIT 5"""):
            print(f"   {lang:<14} {n:>10,}")
