#!/usr/bin/env python
"""
Measure what one TakeMeter CLI run costs, by running it ten times.

One "run" = one `python classify.py classify "<post>"` command, start to
finish, as a user would type it. Each run is a fresh process, so the timing
includes Python startup, importing torch/transformers, loading the saved
model and classifying the post.

Two clocks, so they can check each other:
  wall_ms     timed out here with time.perf_counter() around subprocess.run
  process_ms  timed inside classify.py from its first line (in the log record)

    python measure_cost.py            # 10 posts from data/unlabelled_posts.csv

Writes logs/cost_runs.csv and prints the averages. The posts are real r/Boxing
comments that were scraped but never labelled or trained on.
"""

import csv
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
LOG = REPO / "logs" / "classify_log.jsonl"
OUT = REPO / "logs" / "cost_runs.csv"
N = 10


def main():
    import pandas as pd
    posts = pd.read_csv(REPO / "data" / "unlabelled_posts.csv")["text"].head(N).tolist()
    if not (REPO / "models" / "takemeter" / "config.json").exists():
        sys.exit("Train first (python classify.py train) so training isn't timed as a run.")

    rows = []
    for i, post in enumerate(posts, 1):
        before = LOG.read_text(encoding="utf-8").count("\n") if LOG.exists() else 0
        t = time.perf_counter()
        proc = subprocess.run([sys.executable, str(REPO / "classify.py"), "classify", post],
                              capture_output=True, text=True, encoding="utf-8")
        wall_ms = round((time.perf_counter() - t) * 1000, 1)
        lines = LOG.read_text(encoding="utf-8").splitlines()[before:]
        rec = json.loads(lines[-1]) if lines else {}
        rows.append({
            "run": i, "run_id": rec.get("run_id"), "status": rec.get("status"),
            "exit_code": proc.returncode, "wall_ms": wall_ms,
            "process_ms": rec.get("process_ms"), "model_load_ms": rec.get("model_load_ms"),
            "duration_ms": rec.get("duration_ms"), "output": rec.get("output"),
        })
        print(f"run {i:>2}  {wall_ms:>8.0f} ms wall  {rec.get('process_ms', 0):>8.0f} ms process  "
              f"{rec.get('duration_ms', 0):>6.1f} ms inference  {rec.get('output')}")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def stats(key):
        xs = [r[key] for r in rows if r[key] is not None]
        return statistics.mean(xs), statistics.stdev(xs), min(xs), max(xs)

    print(f"\n{len(rows)} runs, all ok: {all(r['status'] == 'ok' for r in rows)}")
    for key in ("wall_ms", "process_ms", "model_load_ms", "duration_ms"):
        m, sd, lo, hi = stats(key)
        print(f"{key:<14} mean {m:>8.1f}  sd {sd:>7.1f}  min {lo:>8.1f}  max {hi:>8.1f}")
    print(f"\nWrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
