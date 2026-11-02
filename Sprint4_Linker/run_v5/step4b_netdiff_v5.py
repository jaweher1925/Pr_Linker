"""
step4b_netdiff_v5.py - use the NET DIFF (like the original paper), not the per-commit files.

Why: v5 only gives the files of every commit (pr_commit_details). A branch that merged
"main" then carries files written by other people -> false links (26 of 68 pairs in the
manual check). The paper (Who Finishes the Job?, H3) uses the net base->merge diff =
the GitHub "Files changed" tab. This step brings that back, exactly like Mohamed's repo
(prfix.common.loaders.fetch_netdiff + build_net_files), for v5:

  A. fetch the net-diff file list from the GitHub API for every PR that appears in a
     candidate pair of step 4 (P or Q)   -> data/interim/netdiff_cache_v5.jsonl
     (resumable: re-run skips PRs already fetched; ~14.7k PRs, ~3 h with a token)
  B. build table pr_net_files(pr_id, filename, is_boilerplate, is_code) in aidev_v5.duckdb
  C. run linker_v5 again with --file-match-mode net_sub (paper: H3 net diff + H4 not boilerplate)
     -> results/net_all_changes_30_60 and results/net_fix_only_30_60

Needs GITHUB_TOKEN in evolution-assurance/.env (already there).
Run:  uv run --project %EA% python step4b_netdiff_v5.py            (A + B + C)
      uv run --project %EA% python step4b_netdiff_v5.py --skip-fetch   (B + C only)
"""
import argparse, json, os, re, subprocess, sys, time, threading
import urllib.request, urllib.error
import concurrent.futures as cf
import duckdb
import pandas as pd
from prfix.rq1_fix_rates.boilerplate import is_boilerplate
from paths import DB, HERE, REPO, RESULTS

ap = argparse.ArgumentParser()
ap.add_argument("--skip-fetch", action="store_true", help="only rebuild the table and re-run the linker")
ap.add_argument("--workers", type=int, default=4)
args = ap.parse_args()

CACHE = os.path.join(REPO, "data", "interim", "netdiff_cache_v5.jsonl")
os.makedirs(os.path.dirname(CACHE), exist_ok=True)
CODE_EXT = (".py", ".pyx", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".c", ".cc", ".cpp",
            ".h", ".hpp", ".cs", ".rb", ".php", ".kt", ".swift", ".scala", ".sh", ".sql", ".r", ".jl", ".lua")


def token():
    t = os.environ.get("GITHUB_TOKEN")
    env = os.path.join(REPO, ".env")
    if not t and os.path.exists(env):
        for ln in open(env, encoding="utf-8"):
            if ln.strip().startswith("GITHUB_TOKEN="):
                t = ln.split("=", 1)[1].strip().strip('"').strip("'")
    if not t:
        sys.exit("No GITHUB_TOKEN (set it in evolution-assurance/.env)")
    return t


# ---------------------------------------------------------------- A. fetch
def pr_list():
    """Every PR (P or Q) in the step-4 candidate pairs (all_changes 60 d = the widest set)."""
    p = pd.read_parquet(os.path.join(RESULTS, "all_changes_30_60", "candidate_pairs.parquet"),
                        columns=["original_pr_id", "followup_pr_id"])
    ids = set(p.original_pr_id) | set(p.followup_pr_id)
    con = duckdb.connect(DB, read_only=True)
    urls = con.execute("SELECT id, html_url FROM pull_request").df().drop_duplicates("id").set_index("id").html_url
    con.close()
    return [(int(i), urls.get(i)) for i in sorted(ids) if isinstance(urls.get(i), str)]


URL = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")
lock = threading.Lock()


def get(url, tok, tries=6):
    for k in range(tries):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}",
                                                   "Accept": "application/vnd.github+json",
                                                   "User-Agent": "thesis-linker-v5"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                rem = int(r.headers.get("X-RateLimit-Remaining", "100"))
                if rem < 20:                                   # wait for the hourly reset
                    wait = max(int(r.headers.get("X-RateLimit-Reset", "0")) - time.time(), 0) + 5
                    print(f"  rate limit almost used - waiting {wait/60:.0f} min", flush=True)
                    time.sleep(wait)
                return json.loads(r.read()), "ok"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, "not_found"
            if e.code in (403, 429):                          # rate limited -> back off
                reset = e.headers.get("X-RateLimit-Reset")
                wait = max(int(reset) - time.time(), 60) if reset else 60 * (k + 1)
                time.sleep(min(wait, 3700))
                continue
            time.sleep(5 * (k + 1))
        except Exception:
            time.sleep(5 * (k + 1))
    return None, "error"


def fetch_files(url, tok):
    m = URL.search(url or "")
    if not m:
        return None, "bad_url"
    owner, repo, num = m.groups()
    files = []
    for page in range(1, 31):                                  # GitHub returns at most 3000 files
        data, st = get(f"https://api.github.com/repos/{owner}/{repo}/pulls/{num}/files?per_page=100&page={page}", tok)
        if st != "ok":
            return None, st
        files += [f["filename"] for f in data]
        if len(data) < 100:
            break
    return files, "ok"


if not args.skip_fetch:
    tok = token()
    done = set()
    if os.path.exists(CACHE):
        for ln in open(CACHE, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["pr_id"])
            except Exception:
                pass
    prs = pr_list()
    todo = [(i, u) for i, u in prs if i not in done]
    print(f"A. net diff: {len(prs):,} PRs in candidate pairs | already fetched {len(done):,} | to fetch {len(todo):,}", flush=True)
    t0 = time.time()
    with open(CACHE, "a", encoding="utf-8") as fh, cf.ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(fetch_files, u, tok): (i, u) for i, u in todo}
        for k, fu in enumerate(cf.as_completed(futs), 1):
            i, u = futs[fu]
            files, st = fu.result()
            with lock:
                fh.write(json.dumps({"pr_id": i, "url": u, "status": st, "files": files or []}) + "\n"); fh.flush()
            if k % 200 == 0 or k == len(todo):
                rate = k / max(time.time() - t0, 1)
                print(f"   {k:,}/{len(todo):,}  ETA {(len(todo)-k)/rate/60:.0f} min", flush=True)

# ---------------------------------------------------------------- B. table
rows, bad = [], 0
for ln in open(CACHE, encoding="utf-8"):
    d = json.loads(ln)
    if d["status"] == "ok":
        rows += [(int(d["pr_id"]), f) for f in d["files"]]
    else:
        bad += 1
net = pd.DataFrame(rows, columns=["pr_id", "filename"]).drop_duplicates()
names = pd.Series(net.filename.unique())
bp = dict(zip(names, names.map(is_boilerplate)))
net["is_boilerplate"] = net.filename.map(bp).astype(bool)
net["is_code"] = net.filename.str.lower().str.endswith(CODE_EXT)
con = duckdb.connect(DB)
con.register("net_df", net)
con.execute("DROP TABLE IF EXISTS pr_net_files")
con.execute("CREATE TABLE pr_net_files AS SELECT * FROM net_df")
con.close()
print(f"B. pr_net_files: {len(net):,} rows, {net.pr_id.nunique():,} PRs ({bad} PRs unavailable), "
      f"{net.is_boilerplate.mean():.1%} boilerplate", flush=True)

# ---------------------------------------------------------------- C. linker with net diff (paper H3 + H4)
env = dict(os.environ, AIDEV_V5_DB=DB)
for mode in ("all_changes", "fix_only"):
    out = os.path.join(RESULTS, f"net_{mode}_30_60")
    print(f"\nC. === net diff, {mode} ===", flush=True)
    subprocess.check_call([sys.executable, os.path.join(HERE, "linker_v5.py"), "--candidate-mode", mode,
                           "--windows", "30", "60", "--window-rule", "elapsed", "--file-match-mode", "net_sub",
                           "--pairs-format", "both", "--output-dir", out], env=env)
print(f"\nDone. Net-diff results in {RESULTS}\\net_*_30_60")
