#!/usr/bin/env python3
"""Check which PMIDs were already used in recent medical-digest posts.

Usage (run from /root/medical-digest):
    python3 scripts/find_used_pmids.py [lookback_days]
Default lookback: 7 days. Prints each used PMID with the post file that
contained it and the post's date (from the filename), newest first.

Purpose: daily digest cron should not re-publish an article already covered
within ~5-7 days. Feed the used-PMID set into the eutils selection step and
skip any candidate whose PMID appears here.
"""
import re, sys, os
from datetime import date, timedelta

LOOKBACK = int(sys.argv[1]) if len(sys.argv) > 1 else 7

posts_dir = "public/posts"
if not os.path.isdir(posts_dir):
    sys.exit(f"error: no {posts_dir} dir — run from /root/medical-digest")

cutoff = date.today() - timedelta(days=LOOKBACK)
used = {}  # pmid -> sorted list of post-date strings

for fname in sorted(os.listdir(posts_dir)):
    if not fname.endswith(".html"):
        continue
    m = re.match(r"(\d{4}-\d{2}-\d{2})\.html$", fname)
    if not m:
        continue
    post_date = m.group(1)
    try:
        d = date.fromisoformat(post_date)
    except ValueError:
        continue
    if d < cutoff:
        continue
    path = os.path.join(posts_dir, fname)
    pmids = set(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/",
                           open(path, encoding="utf-8").read()))
    for pmid in pmids:
        used.setdefault(pmid, []).append(post_date)

print(f"PMIDs used in posts within the last {LOOKBACK} days ({cutoff} … today):")
print("PMID\tposts")
for pmid in sorted(used, key=lambda p: used[p][-1], reverse=True):
    print(f"{pmid}\t{','.join(sorted(used[pmid]))}")