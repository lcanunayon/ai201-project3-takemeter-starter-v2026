#!/usr/bin/env python
"""
TakeMeter classify CLI — the capstone extension (Shape C).

Before this, TakeMeter could only train and score itself inside the notebook.
This adds one capability: label NEW r/Boxing posts from the command line, with
every post logged as a structured record.

    python classify.py train                      # once: train + save the model
    python classify.py classify "Canelo is washed"
    python classify.py classify --file posts.txt  # one post per line
    echo "some post" | python classify.py classify

Every classified post appends one JSON line to logs/classify_log.jsonl:
timestamp, run id, input, output label + confidence + all scores, and how long
it took (inference ms, plus the model-load ms for that run).

Training uses the notebook's settings and split exactly (same LABELS, seed 42,
10 epochs, lr 2e-5, batch 16, max_length 128, 70/15/15 stratified), so the
saved model is the one the README's results describe.
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
MODEL_DIR = REPO_DIR / "models" / "takemeter"
DEFAULT_LOG = REPO_DIR / "logs" / "classify_log.jsonl"

# ── Same settings as takemeter.ipynb section 2 ───────────────────────────────
LABELS = ["hot_take", "informative", "humorous", "offensive"]
BASE_MODEL = "distilbert-base-uncased"
EPOCHS = 10
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
MAX_LENGTH = 128
SEED = 42
CSV = REPO_DIR / "labels.csv"


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def pick_device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def append_log(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ── train ────────────────────────────────────────────────────────────────────

def split_dataset(df, seed, test_size=0.15, val_size=0.15):
    """Identical to the notebook's split, so the test set matches test_split.csv."""
    from sklearn.model_selection import train_test_split

    def _stratify_on(frame):
        counts = frame["label"].value_counts()
        return frame["label"] if counts.min() >= 2 else None

    rest, test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=_stratify_on(df)
    )
    val_share = val_size / (1 - test_size)
    train, val = train_test_split(
        rest, test_size=val_share, random_state=seed, stratify=_stratify_on(rest)
    )
    return (train.reset_index(drop=True), val.reset_index(drop=True),
            test.reset_index(drop=True))


def cmd_train(args):
    import numpy as np
    import pandas as pd
    from datasets import Dataset
    from sklearn.metrics import accuracy_score, f1_score
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                              Trainer, TrainingArguments, set_seed)

    started = time.perf_counter()
    df = pd.read_csv(CSV)
    train_df, val_df, test_df = split_dataset(df, args.seed)

    lookup = {l: i for i, l in enumerate(LABELS)}

    def to_ds(frame):
        out = frame.copy()
        out["labels"] = out["label"].astype(str).str.strip().map(lookup)
        ds = Dataset.from_pandas(out[["text", "labels"]])
        return ds.map(lambda b: tokenizer(b["text"], truncation=True,
                                          padding="max_length", max_length=MAX_LENGTH),
                      batched=True)

    set_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=len(LABELS),
        id2label=dict(enumerate(LABELS)), label2id=lookup,
    )
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(REPO_DIR / "takemeter_out"),
            num_train_epochs=args.epochs, learning_rate=LEARNING_RATE,
            per_device_train_batch_size=BATCH_SIZE, per_device_eval_batch_size=BATCH_SIZE,
            # eval every epoch like the notebook does: it changes the RNG
            # sequence, and skipping it gives a different model than the README's.
            eval_strategy="epoch", save_strategy="no", logging_steps=10,
            seed=args.seed, report_to="none",
        ),
        train_dataset=to_ds(train_df),
        eval_dataset=to_ds(val_df),
        compute_metrics=lambda p: {"accuracy": float(accuracy_score(
            p.label_ids, np.argmax(p.predictions, axis=-1)))},
    )
    trainer.train()

    pred = trainer.predict(to_ds(test_df))
    guessed = np.argmax(pred.predictions, axis=-1)
    gold = pred.label_ids
    acc = float(accuracy_score(gold, guessed))
    f1 = float(f1_score(gold, guessed, average="macro", zero_division=0))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(MODEL_DIR))
    tokenizer.save_pretrained(str(MODEL_DIR))
    seconds = round(time.perf_counter() - started, 1)
    meta = {
        "trained_at": now_iso(), "seed": args.seed, "epochs": args.epochs,
        "labels": LABELS, "base_model": BASE_MODEL, "max_length": MAX_LENGTH,
        "n_train": len(train_df), "n_val": len(val_df), "n_test": len(test_df),
        "test_accuracy": acc, "test_f1_macro": f1,
        "train_seconds": seconds, "device": pick_device(),
    }
    (MODEL_DIR / "takemeter_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nSaved model to {MODEL_DIR}")
    print(f"test accuracy {acc:.3f}  macro F1 {f1:.3f}  ({seconds}s on {meta['device']})")


# ── classify ─────────────────────────────────────────────────────────────────

def read_posts(args):
    if args.text:
        return [" ".join(args.text)]
    if args.file:
        lines = Path(args.file).read_text(encoding="utf-8").splitlines()
        return [l.strip() for l in lines if l.strip()]
    if not sys.stdin.isatty():
        return [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]
    return []


def cmd_classify(args):
    posts = read_posts(args)
    if not posts:
        sys.exit("Nothing to classify. Pass text, --file posts.txt, or pipe posts in.")
    if not (MODEL_DIR / "config.json").exists():
        # A clean checkout has no model (it's gitignored), so build it once.
        print(f"No trained model at {MODEL_DIR}. Training one first (~2 min on CPU)...",
              file=sys.stderr)
        cmd_train(argparse.Namespace(seed=SEED, epochs=EPOCHS))

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    run_id = uuid.uuid4().hex[:8]
    device = pick_device()

    t0 = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR)).to(device)
    model.eval()
    load_ms = round((time.perf_counter() - t0) * 1000, 1)
    labels = [model.config.id2label[i] for i in range(model.config.num_labels)]

    log_path = Path(args.log) if args.log else DEFAULT_LOG
    results = []
    for text in posts:
        t = time.perf_counter()
        enc = tokenizer(text, truncation=True, max_length=MAX_LENGTH,
                        return_tensors="pt").to(device)
        with torch.no_grad():
            probs = torch.softmax(model(**enc).logits[0], dim=-1).tolist()
        duration_ms = round((time.perf_counter() - t) * 1000, 1)

        best = max(range(len(labels)), key=lambda i: probs[i])
        record = {
            "timestamp": now_iso(),
            "run_id": run_id,
            "input": text,
            "input_tokens": int(enc["input_ids"].shape[1]),
            "truncated": len(tokenizer(text)["input_ids"]) > MAX_LENGTH,
            "output": labels[best],
            "confidence": round(probs[best], 4),
            "scores": {l: round(p, 4) for l, p in zip(labels, probs)},
            "duration_ms": duration_ms,
            "model_load_ms": load_ms,
            "device": device,
            "model": str(MODEL_DIR.relative_to(REPO_DIR)),
        }
        append_log(log_path, record)
        results.append(record)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            preview = r["input"] if len(r["input"]) <= 70 else r["input"][:67] + "..."
            print(f"{r['output']:<12} {r['confidence']:.2f}  {r['duration_ms']:>7.1f} ms  {preview}")
        total = sum(r["duration_ms"] for r in results)
        print(f"\n{len(results)} post(s) · load {load_ms:.0f} ms · inference {total:.0f} ms "
              f"({total / len(results):.1f} ms/post) · {device} · run {run_id}")
        print(f"Logged to {log_path}")


def main():
    p = argparse.ArgumentParser(description="Classify r/Boxing posts with TakeMeter.")
    sub = p.add_subparsers(dest="command", required=True)

    t = sub.add_parser("train", help="train on labels.csv and save the model")
    t.add_argument("--seed", type=int, default=SEED)
    t.add_argument("--epochs", type=int, default=EPOCHS)
    t.set_defaults(func=cmd_train)

    c = sub.add_parser("classify", help="label new posts")
    c.add_argument("text", nargs="*", help="the post to classify")
    c.add_argument("--file", help="a text file, one post per line")
    c.add_argument("--json", action="store_true", help="print full records as JSON")
    c.add_argument("--log", help=f"log file (default {DEFAULT_LOG.relative_to(REPO_DIR)})")
    c.set_defaults(func=cmd_classify)

    args = p.parse_args()
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    args.func(args)


if __name__ == "__main__":
    main()
