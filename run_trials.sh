#!/usr/bin/env bash
# Milestone 5: run C1, C2, C3 and C5 exactly as README "Acceptance criteria"
# defines them, for one trial. C4 (clean checkout) is run_c4.ps1.
#
#   bash run_trials.sh t1      # then t2, t3. Change nothing in between.
#
# Every command's real output is saved to logs/trials/<criterion>_<trial>_out.txt;
# the log records go to logs/trials/<criterion>_<trial>.jsonl via --log.

set -u
K="${1:?usage: bash run_trials.sh t1|t2|t3}"
cd "$(dirname "$0")"
PY=".venv/Scripts/python.exe"; [ -x "$PY" ] || PY=".venv/bin/python"
export PYTHONIOENCODING=utf-8
T="${TRIALS_DIR:-logs/trials}"   # after the fix: TRIALS_DIR=logs/trials_after
mkdir -p "$T"
noise='it/s|s/it|pin_memory|super\(\).__init__|Map: '

echo "### $K started $(date -Iseconds)"

# ── C1: fresh train, then the 30 held-out posts ──────────────────────────────
rm -f "$T/c1_$K.jsonl"
{ echo "\$ python classify.py train"
  $PY classify.py train 2>&1 | grep -vE "$noise" | tail -3
  cp models/takemeter/takemeter_meta.json "$T/c1_${K}_meta.json"
  echo "model.safetensors sha256: $(sha256sum models/takemeter/model.safetensors | cut -c1-16)"
  echo "\$ python classify.py classify --csv test_split.csv --log $T/c1_$K.jsonl"
  $PY classify.py classify --csv test_split.csv --log "$T/c1_$K.jsonl" 2>&1 | grep -vE "$noise"
} > "$T/c1_${K}_out.txt"

# ── C2: the five runs, one log file ──────────────────────────────────────────
L="$T/c2_$K.jsonl"; rm -f "$L"
{ echo "\$ (a) one post";    $PY classify.py classify --log "$L" "Ryan destroyed buddy" 2>&1 | tail -3; echo "exit ${PIPESTATUS[0]}"
  echo "\$ (b) 3-post CSV";  $PY classify.py classify --log "$L" --csv data/c2_three_posts.csv 2>&1 | tail -6; echo "exit ${PIPESTATUS[0]}"
  echo "\$ (c) blank";       $PY classify.py classify --log "$L" "   " 2>&1 | tail -1; echo "exit ${PIPESTATUS[0]}"
  echo "\$ (d) missing file";$PY classify.py classify --log "$L" --csv no_such_file.csv 2>&1 | tail -1; echo "exit ${PIPESTATUS[0]}"
  echo "\$ (e) model hidden"
  mv models/takemeter/model.safetensors models/takemeter/model.safetensors.bak
  $PY classify.py classify --log "$L" "test" 2>&1 | tail -1; echo "exit ${PIPESTATUS[0]}"
  mv models/takemeter/model.safetensors.bak models/takemeter/model.safetensors
} > "$T/c2_${K}_out.txt"

# ── C3: ten timed single-post runs ───────────────────────────────────────────
{ echo "\$ python measure_cost.py"; $PY measure_cost.py 2>&1; } > "$T/c3_${K}_out.txt"
cp logs/cost_runs.csv "$T/c3_$K.csv"

# ── C5: the multi-line set for this trial ────────────────────────────────────
case "$K" in t1) SET=data/c5_multiline_test.csv;; t2) SET=data/c5_multiline_labels.csv;; t3) SET=data/c5_multiline_unlabelled.csv;; esac
rm -f "$T/c5_$K.jsonl"
{ echo "\$ python classify.py classify --csv $SET --log $T/c5_$K.jsonl"
  $PY classify.py classify --csv "$SET" --log "$T/c5_$K.jsonl" 2>&1 | grep -vE "$noise"
} > "$T/c5_${K}_out.txt"

echo "### $K finished $(date -Iseconds)"
