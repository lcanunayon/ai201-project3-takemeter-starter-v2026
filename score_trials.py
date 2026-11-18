#!/usr/bin/env python
"""
Score the Milestone 5 trials against the README's pass rules, mechanically.

    python score_trials.py                    # before: logs/trials
    python score_trials.py logs/trials_after  # after the fix

Reads logs/trials/*, prints one line per criterion per trial and the run-log
table to paste into the README. It applies the rules as written, including
where a rule turns out to be stricter than what it meant. Diagnosis is the
README's job, not this script's.
"""

import csv
import json
import statistics
from pathlib import Path

import pandas as pd

import sys
T = Path(__file__).resolve().parent / (sys.argv[1] if len(sys.argv) > 1 else "logs/trials")
TRIALS = ["t1", "t2", "t3"]
C5_SETS = {"t1": "data/c5_multiline_test.csv", "t2": "data/c5_multiline_labels.csv",
           "t3": "data/c5_multiline_unlabelled.csv"}


def read_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def c1(k):
    recs = read_jsonl(T / f"c1_{k}.jsonl")
    hits = sum(r.get("correct") is True for r in recs)
    acc = hits / len(recs) if recs else 0.0
    ok = len(recs) == 30 and 0.6665 <= acc <= 0.7335
    return ok, f"{hits}/{len(recs)} = {acc:.3f}"


C2_EXPECT = ["ok", "ok", "ok", "ok", "rejected", "rejected", "error"]


def c2(k):
    recs = read_jsonl(T / f"c2_{k}.jsonl")
    statuses = [r.get("status") for r in recs]
    good = 0
    for r, want in zip(recs, C2_EXPECT):
        fields = all(f in r for f in ("timestamp", "run_id", "status", "input", "output"))
        dur = "duration_ms" in r if want == "ok" else "process_ms" in r
        good += fields and dur and r.get("status") == want
    ok = len(recs) == 7 and statuses == C2_EXPECT and good == 7
    # Score in runs (a-e): run b is 3 records.
    runs = [recs[0:1], recs[1:4], recs[4:5], recs[5:6], recs[6:7]]
    wants = [["ok"], ["ok"] * 3, ["rejected"], ["rejected"], ["error"]]
    runs_ok = sum([r.get("status") for r in run] == w for run, w in zip(runs, wants))
    return ok, f"{runs_ok}/5 runs ({len(recs)}/7 records)"


def c3(k):
    rows = list(csv.DictReader(open(T / f"c3_{k}.csv", encoding="utf-8")))
    wall = statistics.mean(float(r["wall_ms"]) for r in rows)
    inf = statistics.mean(float(r["duration_ms"]) for r in rows)
    all_ok = len(rows) == 10 and all(r["status"] == "ok" for r in rows)
    ok = all_ok and wall <= 10_000 and inf <= 200
    return ok, f"{wall / 1000:.2f} s / {inf:.0f} ms"


def c4(k):
    out = T / f"c4_{k}_out.txt"
    if not out.exists():
        return False, "not run"
    text = out.read_text(encoding="utf-8", errors="replace").replace(chr(13), chr(10))
    get = lambda key: next((l.split(":", 1)[1].strip() for l in text.splitlines()
                            if l.startswith(key)), "")
    code, lines, status, acc = (get("exit code of last line"), get("log lines in clone"),
                                get("last log line status"), get("test_accuracy"))
    acc = acc.rstrip(chr(0xFFFD) + " " + chr(10))
    ok = code == "0" and lines == "1" and status == "ok" and acc in ("0.7", "0.70")
    return ok, f"exit {code}, {lines} log lines, last {status}, acc {acc}"


def c5(k):
    posts = pd.read_csv(C5_SETS[k])["text"].astype(str).str.strip().tolist()
    recs = read_jsonl(T / f"c5_{k}.jsonl")
    same = sum(r.get("input") == p for r, p in zip(recs, posts))
    newlines = sum("\n" in r.get("input", "") for r in recs)
    ok = len(recs) == len(posts) and same == len(posts)
    return ok, f"{len(recs)} rec / {len(posts)} posts, {same} exact, {newlines} keep newlines"


CRITERIA = [
    ("C1. Agrees with the notebook", "0.667–0.733 on 30 posts", c1),
    ("C2. Always leaves a record", "5 of 5 runs, 7 records", c2),
    ("C3. Cost per run", "≤ 10 s wall / ≤ 200 ms inference", c3),
    ("C4. Clean checkout", "exit 0, 1 log line `ok`, acc 0.7", c4),
    ("C5. Multi-line posts stay whole", "records = posts, inputs exact", c5),
]


def main():
    print("| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |")
    print("|---|---|---|---|---|---|")
    for name, target, fn in CRITERIA:
        cells, verdict = [], True
        for k in TRIALS:
            try:
                ok, desc = fn(k)
            except FileNotFoundError:
                ok, desc = False, "missing"
            verdict &= ok
            cells.append(f"{desc} {'✅' if ok else '❌'}")
        print(f"| {name} | {target} | " + " | ".join(cells) + f" | **{'MET' if verdict else 'MISSED'}** |")


if __name__ == "__main__":
    main()
