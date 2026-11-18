# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ═══════════════════════ CAPSTONE — THE EXTENSION ═══════════════════════ -->

## Capstone Extension: Classify CLI

### What I extended

**System:** TakeMeter, the r/Boxing post classifier (project 3). It fine-tunes
DistilBERT to sort posts into `hot_take`, `informative`, `humorous` or
`offensive`.

**What's new:** TakeMeter could only train and score itself inside the
notebook, and there was no way to label a post it hadn't seen. The extension is
`classify.py`, a command-line classifier. It loads the trained model, labels new
posts (from an argument, a CSV, a text file or stdin) with a confidence score, and logs
every post as a structured record.

### The Shape

**Shape C: extend one capability.** I'm adding one capability to a classifier
that already trains and scores: labelling **new** r/Boxing posts from the
command line. `python classify.py classify "<post>"` returns a label and a
confidence score, and writes a structured log record for every post. When I'm
finished, I'll claim that the CLI labels new posts outside the notebook, gives
the same answers the notebook's model would, and leaves a log record for every
post with what came in, what came out and how long it took.

**Out of scope:** <!-- Your call. A draft from the options weighed while planning: -->
- **No fifth label.** I considered adding something like `analysis`, but it
  means relabelling much of `labels.csv` and retraining. That's a second project.
- **No HTTP endpoint or web interface.** A local server would do the same job
  as the CLI with more moving parts.
- **No "unsure" / abstain output, and no fixing the model.** The classifier's
  known weaknesses (0 F1 on `informative` and `offensive`, leaning toward
  `hot_take`) carry over unchanged. The extension exposes the model, it doesn't
  retrain it to be better.

**Size check:** the CLI is one file of about 250 lines, reusing the notebook's
split and settings. It was well under the ninety-minute limit.

### Run path

**Path B: local with logs.** One documented command starts it, and it works from
a clean checkout:
`python classify.py classify "<post>"`. The command, the environment it needs
(Python version, pinned dependencies, model files and their size) and the log
format are in [RUNNING.md](RUNNING.md#the-capstone-extension-classifypy-path-b-local-with-logs).
The committed run record is `logs/classify_log.jsonl`, pasted below.

### The original system still works

The extension adds files and doesn't edit any of the original ones.
`git diff d08863a HEAD` (the last commit before the capstone) shows no changes
to the notebook, `baseline.py`, `agreement.py`, `test.py`, `labels.csv` or
`test_split.csv`. I also re-ran the whole original pipeline from a fresh export
of the repo on 2026-11-14. Full output is in
[logs/regression_2026-11-14.txt](logs/regression_2026-11-14.txt).

| Check | Result |
|---|---|
| `python test.py` | 10 passed, 0 failed |
| `python agreement.py` | `agreement_results.json` byte-identical to the committed one |
| `python baseline.py --trained results.json` | Same 30 predictions and metrics as committed (accuracy 0.233, macro F1 0.128) |
| Notebook, all cells | Ran clean. Three seeds identical to `results_three_seeds_after.json` (0.700 / 0.767 / 0.633) |
| `classify.py train` | Reproduces the notebook's seed 42 model exactly: accuracy 0.700, macro F1 0.379 |

The only byte-level differences were Windows line endings (`\r\n` vs `\n`)
inside multi-line posts in `test_split.csv` and `baseline_results.json`. The
content is the same.

### Acceptance criteria

Written 2026-11-17, before any trial was run. All five are about the extension,
the CLI. None of them re-tests how accurate the classifier is: that was project
3's job. Each criterion gets **three trials** and is **met only if all three
trials hit the target**.

**Self-checked before any trial.** I asked of each one: could a person who can't
ask me what I meant run it and score it? The first draft (`62de4d1`) failed that
test in every criterion: unclear record counting, an unnamed CSV, an undefined
"hide the model", and so on. This version spells out exactly what to run, what to
count and what passes. The targets didn't change.

**Rules for every trial:**
- Run from the repo root with the `.venv` active.
- Never pass `--epochs` or `--seed`, so the defaults (seed 42, 10 epochs) apply.
- Every command logs to its own file under `logs/trials/` with `--log`, so the
  records for a trial are exactly the lines in that file.
- Trial *k* is `t1`, `t2` or `t3`.

#### C1 — Agrees with the notebook

The CLI gives the same answers as the notebook's model it claims to reproduce.

- **Run:** `python classify.py train`, then
  `python classify.py classify --csv test_split.csv --log logs/trials/c1_tk.jsonl`
- **Count:** lines in `c1_tk.jsonl` where `"correct": true`, divided by the
  number of lines (it must be 30).
- **Pass:** 30 lines, and an accuracy **from 0.667 to 0.733 inclusive**. That's
  the notebook's seed 42 result of 0.700 (21/30), plus or minus one post.
- **Why ±1:** the CLI tokenizes without padding to 128, so one borderline post
  could flip on floating-point rounding. Two or more flips would mean it isn't the
  same model.

#### C2 — Always leaves a record

Every run, including a failed one, writes a log record. Run these 5 commands,
each with `--log logs/trials/c2_tk.jsonl`:

| Run | Command | Expected records |
|---|---|---|
| a | `python classify.py classify "Ryan destroyed buddy"` | 1, `status: ok` |
| b | `python classify.py classify --csv data/c2_three_posts.csv` (the first 3 rows of `test_split.csv`, committed) | 3, `status: ok` |
| c | `python classify.py classify "   "` | 1, `status: rejected` |
| d | `python classify.py classify --csv no_such_file.csv` | 1, `status: rejected` |
| e | Rename `models/takemeter/model.safetensors` to `model.safetensors.bak`, run `python classify.py classify "test"`, then rename it back. **Rename only that one file:** without `config.json` the CLI would retrain instead of failing | 1, `status: error` |

- **Count:** `c2_tk.jsonl` must have exactly **7 lines**, in the order above,
  with the statuses above.
- **Every line must have** `timestamp`, `run_id`, `status`, `input`, and
  `output` (a label, or `null` on a failure).
- **Durations:** `ok` lines have `duration_ms`; failed lines have `process_ms`.
- **Pass:** all of the above in every one of the 3 trials, 100%. A log that
  misses some runs is the failure Milestone 3 warns about.

#### C3 — Cost

One run is cheap enough to use by hand.

- **Run:** `python measure_cost.py`, then copy `logs/cost_runs.csv` to
  `logs/trials/c3_tk.csv` *before* the next trial, because the script overwrites
  it. The model must already be trained, or the script refuses to run.
- **Read:** the `mean` column of the `wall_ms` and `duration_ms` lines it prints,
  or average those columns in the CSV.
- **Pass:** all 10 runs `status: ok`, **mean `wall_ms` ≤ 10,000**, and **mean
  `duration_ms` ≤ 200**.
- **Why these numbers:** I measured about 6.4 s once while building. Ten seconds
  is my line for "I'd still use this by hand". The 200 ms cap means a slowdown in
  the model itself can't hide inside the 5.5 s of import time.
- **Same machine every trial:** this laptop, CPU only.

#### C4 — Clean checkout

Someone with only RUNNING.md can get a labelled post.

- **Run:** make a new, empty folder (`clonetest_tk`). In a new PowerShell
  window, type the six lines in RUNNING.md's **Clean-checkout setup** block,
  exactly as written and in order.
- **Pass:**
  - the last line exits with code **0**
  - `logs/classify_log.jsonl` in the clone contains **exactly one line**, with
    `status: ok`
  - `models/takemeter/takemeter_meta.json` in the clone has `test_accuracy`
    **0.7**
  - nothing was typed that isn't in that block
- **What counts as a miss:** any extra command, such as an execution-policy fix,
  a different `python`, or re-running a line. RUNNING.md listing a workaround
  doesn't make it part of the six lines.
- **Limit, stated up front:** this machine already has `distilbert-base-uncased`
  in `~/.cache/huggingface/`, so C4 does **not** test the 257 MB first download.
  Passing C4 means "works from a clean checkout on a machine with the base model
  cached", nothing more.

#### C5 — Multi-line posts stay whole

A post that spans several lines comes back as one label.

- **The three trials use three sets of posts.** Each is built by keeping the
  rows whose `text` contains a newline:

| Trial | Source | Posts | Committed as |
|---|---|---|---|
| t1 | `test_split.csv` | 9 | `data/c5_multiline_test.csv` |
| t2 | `labels.csv` | 38 | `data/c5_multiline_labels.csv` |
| t3 | `data/unlabelled_posts.csv` | 4 | `data/c5_multiline_unlabelled.csv` |

- **Run:** `python classify.py classify --csv <that file> --log logs/trials/c5_tk.jsonl`
- **Count:** the lines in `c5_tk.jsonl`, and for each line *i*, compare its
  `input` with row *i*'s `text` after `.strip()`. The CLI trims surrounding
  whitespace, and that isn't a split.
- **Pass:** **line count = post count exactly** (9, 38, 4), and **every `input`
  equals its post** with its inner newlines still there. One fragment means a
  post got cut and labelled as two half-posts.

### Trials, verdicts and diagnoses

<!-- TODO: three trials per criterion, then Met/Missed and, for each miss,
     which part of the system failed and how. -->

### Instrumentation

Every `classify.py classify` command appends to `logs/classify_log.jsonl`, one
JSON object per line. It's a file you can read back, not `print()` output.
Successful posts get `status: "ok"`. A run that fails still leaves a record:
`status` is `"rejected"` for bad input, `"error"` for a crash such as a missing
or corrupt model, or `"interrupted"` for Ctrl-C, along with the input, the error
and how long it ran. The field meanings are in
[RUNNING.md](RUNNING.md#the-capstone-extension-classifypy-path-b-local-with-logs).

Beyond the minimum (timestamp, input, output, duration), the log records the
things I'll want in Milestone 5: `confidence` and all four `scores` (to tell a
confident miss from a coin flip), `truncated` (posts past 128 tokens lose their
end), `model_load_ms` vs `duration_ms` vs `process_ms` (where the time goes),
and `expected` / `correct` when the input CSV has labels.

**The run record.** This is the whole of `logs/classify_log.jsonl` from a real
session on 2026-11-14:
- Entries 1–10 are the ten cost-measurement runs, one command each, on real
  r/Boxing comments from `data/unlabelled_posts.csv`. These were scraped but
  never labelled or trained on.
- Entries 11–12 are failed runs: a blank post, and a mistyped file name
  (`unlabeled` for `unlabelled`). Both were rejected and logged.

```jsonl
{"timestamp": "2026-11-14T15:37:16.700-06:00", "run_id": "30631e3a", "status": "ok", "input": "I think Benn being aggressive and throwing in tight the way he was was the right call.\nBut being that heavy on his front foot leaning forward at centre ring was a recipe for disaster, I don’t think that was well thought out lol", "input_tokens": 52, "truncated": false, "output": "hot_take", "confidence": 0.6892, "scores": {"hot_take": 0.6892, "informative": 0.132, "humorous": 0.1187, "offensive": 0.0601}, "duration_ms": 63.0, "model_load_ms": 136.5, "process_ms": 5835.6, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:37:23.194-06:00", "run_id": "dfeeef91", "status": "ok", "input": "Realistically that was Benn’s only real chance to win with fighting like that. He was never going to win a technical boxing match cos he simply doesn’t have that style let alone at this level.\nThe Benn you seen tonight is him and nothing really changes. It’s been pretty much accepted for a long time that he just isn’t world level and in reality he hasn’t even won a title at British level.\nI thought Garcia would win a decision but I never saw him doing what he did. Eubank couldn’t even finish Benn in their first fight when he had him hurt.\nI’m not a Benn fan but I do kinda feel bad for him now as he’s been outted for what will be a highlight reel.", "input_tokens": 128, "truncated": true, "output": "hot_take", "confidence": 0.5286, "scores": {"hot_take": 0.5286, "informative": 0.2955, "humorous": 0.0958, "offensive": 0.0802}, "duration_ms": 61.9, "model_load_ms": 134.1, "process_ms": 5767.9, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:37:29.660-06:00", "run_id": "0ca64040", "status": "ok", "input": "Eubank was boiled down to death the fact he even won is laughable", "input_tokens": 17, "truncated": false, "output": "hot_take", "confidence": 0.7162, "scores": {"hot_take": 0.7162, "informative": 0.1081, "humorous": 0.1258, "offensive": 0.0499}, "duration_ms": 33.4, "model_load_ms": 131.7, "process_ms": 5760.4, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:37:36.067-06:00", "run_id": "1a2f3aed", "status": "ok", "input": "If Benn was really 180+ that night, they sure don't have any plans for the later rounds.", "input_tokens": 25, "truncated": false, "output": "hot_take", "confidence": 0.7448, "scores": {"hot_take": 0.7448, "informative": 0.1192, "humorous": 0.0918, "offensive": 0.0443}, "duration_ms": 35.3, "model_load_ms": 132.9, "process_ms": 5710.4, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:37:42.486-06:00", "run_id": "a4832362", "status": "ok", "input": "That right hand was so Fkn beautiful. Nobody has faster hands in boxing than Ryan.", "input_tokens": 20, "truncated": false, "output": "hot_take", "confidence": 0.7673, "scores": {"hot_take": 0.7673, "informative": 0.0833, "humorous": 0.1084, "offensive": 0.041}, "duration_ms": 47.0, "model_load_ms": 131.9, "process_ms": 5718.6, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:37:48.932-06:00", "run_id": "9032e727", "status": "ok", "input": "In the slow motion you can see him use his left hand to block Benns view of his right and frame it, Benn barely saw it coming, class.", "input_tokens": 35, "truncated": false, "output": "hot_take", "confidence": 0.7663, "scores": {"hot_take": 0.7663, "informative": 0.0871, "humorous": 0.0924, "offensive": 0.0542}, "duration_ms": 38.4, "model_load_ms": 132.1, "process_ms": 5737.5, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:37:55.368-06:00", "run_id": "09ead8d6", "status": "ok", "input": "Benn the fat snake got what he deserved. Not a world class fighter, should go back to fighting old bums.", "input_tokens": 27, "truncated": false, "output": "hot_take", "confidence": 0.825, "scores": {"hot_take": 0.825, "informative": 0.0702, "humorous": 0.0691, "offensive": 0.0357}, "duration_ms": 46.6, "model_load_ms": 133.2, "process_ms": 5743.3, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:38:01.804-06:00", "run_id": "4453c57e", "status": "ok", "input": "Great fight, awful commentary. Dear God, Garcia was landing at will in the 1st and the commentary just talking about how they aren't 'all' landing and Benn is doing a good job, Gracias going to get tires he's moving too much. 2nd round Garcia stops him, 'i think it was premature, Garcia was robbed of a decisive finish' like my fucking god what are they watching?", "input_tokens": 87, "truncated": false, "output": "hot_take", "confidence": 0.4801, "scores": {"hot_take": 0.4801, "informative": 0.2949, "humorous": 0.1267, "offensive": 0.0983}, "duration_ms": 45.7, "model_load_ms": 137.4, "process_ms": 5728.0, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:38:08.236-06:00", "run_id": "b27fc2ba", "status": "ok", "input": "The commentary was embarrassing. Kellerman has gone full Stephen A Smith. He literally said “Benn is trying to show Garcia he can take the left hook” nah Max, Garcia is piecing Benn up, he has no choice in this.", "input_tokens": 52, "truncated": false, "output": "hot_take", "confidence": 0.4753, "scores": {"hot_take": 0.4753, "informative": 0.2133, "humorous": 0.1982, "offensive": 0.1131}, "duration_ms": 42.2, "model_load_ms": 135.0, "process_ms": 5712.3, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:38:14.658-06:00", "run_id": "79021d2c", "status": "ok", "input": "Someone finally explained to Benn that there are levels to this.", "input_tokens": 15, "truncated": false, "output": "hot_take", "confidence": 0.78, "scores": {"hot_take": 0.78, "informative": 0.074, "humorous": 0.103, "offensive": 0.043}, "duration_ms": 33.0, "model_load_ms": 135.4, "process_ms": 5721.7, "device": "cpu", "model": "models\\takemeter"}
{"timestamp": "2026-11-14T15:38:21.802-06:00", "run_id": "3e55720e", "status": "rejected", "input": "   ", "output": null, "error": "Rejected: Nothing to classify. Pass text, --csv posts.csv, --file posts.txt, or pipe posts in.", "process_ms": 7.8}
{"timestamp": "2026-11-14T15:38:21.904-06:00", "run_id": "4dafad7c", "status": "rejected", "input": "--csv data/unlabeled_posts.csv", "output": null, "error": "Rejected: No such file: data/unlabeled_posts.csv", "process_ms": 6.3}
```

All ten real posts came out `hot_take`, with confidence from 0.48 to 0.83. That matches the model's known lean toward `hot_take` from the confusion
matrix below, and the criteria should test it.

Failure path, tested on purpose before this session, logged to a scratch file
so it stayed out of the record above. I renamed `model.safetensors` away and
ran one post. The run failed and logged
`"status": "error", "error": "OSError: Error no file named ... model.safetensors ..."`
with `process_ms` 5686.7, then exited non-zero. The model was restored
afterwards.

### What It Costs

**About 6.4 seconds of local CPU per run. $0 in API spend, and no tokens are
billed.** It's measured, not estimated.

**Method:** [measure_cost.py](measure_cost.py) runs the real command,
`python classify.py classify "<post>"`, **ten times as ten separate processes**,
one real post each. Each run is timed on two clocks that check each other:
- `wall_ms`: `time.perf_counter()` around `subprocess.run` in the measuring
  script. That's start to finish as a user would type it, including Python
  startup.
- `process_ms`: `time.perf_counter()` from the first line of `classify.py`,
  written into the log record.

The model was already trained, so training isn't counted here. Raw numbers are
in [logs/cost_runs.csv](logs/cost_runs.csv).

| Measure (10 runs) | Mean | SD | Min | Max |
|---|---|---|---|---|
| Wall-clock per run | **6442.8 ms** | 42.2 | 6400.2 | 6545.4 |
| `process_ms` (from script start) | 5743.6 ms | 37.7 | 5710.4 | 5835.6 |
| `model_load_ms` | 134.0 ms | 2.0 | 131.7 | 137.4 |
| `duration_ms` (inference, one post) | 44.6 ms | 10.7 | 33.0 | 63.0 |

**Where the time goes:** classifying the post is under 1% of a run (45 ms).
Loading the model is about 2% (134 ms). Roughly 5.5 s is importing torch and
transformers, and about 0.7 s is starting Python. So a batch is far cheaper per
post than single runs: `--csv` pays the 6 s once and then about 45 ms per post.

**One-time costs, not per run:** training the model takes about 120 s of CPU on
the first run of a clean checkout (117.4 s in the clone test). `pip install`
took 160 s with a warm pip cache.

Hardware: CPU only (`device: cpu`), Windows 11, Python 3.13.7, torch 2.14.1+cpu,
31.7 GB RAM.

### The improvement

<!-- TODO: one change, re-run, before and after side by side. -->

### What's left

<!-- TODO: what you'd do next, and why you stopped. -->

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Your community, and what your classifier sorts posts into. Three or four
     sentences. -->

r/Boxing (reddit forum on boxing)

My classifier will sort comments/posts by what they bring to the discussion. Some posts are opinions about fighters, some are informative, some are just jokes, and some are offensive. It sorts each post into one of four labels: `hot_take`, `informative`, `humorous`, or `offensive`. The offensive will win if there is an offensive word/idea insulting a fighter, even if it is for example informative as well.

---

## Label Taxonomy

<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.

     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### `hot_take`

**Definition:**
A confident opinion about a fighter, fight or matchup with no checkable fact backing it up.

**Example 1:**
> Witnessed it. And i was a hater back then. But dudes legit

**Example 2:**
> Straight dawg too. Fought everyone and their mama. Didn't matter if they were right in their prime and he was aging. Absolute dawg. If you wanted smoke, he was happy to oblige

### `informative`

**Definition:**
Has a checkable fact in the post (something you could verify from a public source like a record, a broadcast or an article) which can inform the viewer.

**Example 1:**
>It was before my time but Oscar in his prime is elite. "Oscar De La Hoya won 11 world titles across six weight classes during his professional boxing career, along with 3 lineal championships."

**Example 2:**
> His serious left punch was recorded by a tv show before and according to them the force is just as great as a shot from a shotgun

### `humorous`

**Definition:**
No other purpose than to be funny.

**Example 1:**
> Jake Paul really thought he was a boxer LMAOO

**Example 2:**
> LMAO

### `offensive`

**Definition:**
A post that insults or attacks a person or group. Swearing just for emphasis doesn't count.

**Example 1:**
> I fucking hate ryan garcia

**Example 2:**
> Hrgovic is fuckin hilarious man. I love his heart and mentality. But let’s be honest. He’s a fuckin shit boxer.
> Telegraphed and slow as fuck.
>
> Dubois runs through him.
>
> Fuck it, even old fury would give Hrgovic a hammering.
>
> I just wish fury would have the balls to fight Dubois but we know that won’t happen.
>
> Fury gonna beat Joshua and retire.
>
> Then it’s King Daniel

### The hardest boundary

**Which two labels:** `hot_take` vs `informative`

Borderline post:
>I'm 5'10" 140lbs Filipino and got ~800 by getting a running start and Superman punching the machine. My glasses flew off when I made contact. This dude just stands there

It has specific numbers in it, but we cannot check the facts of this random poster. What he is really saying is a hot_take: that the fighter he is talking about is extraordinary.

**The decision rule I used every time:**
<!-- e.g. "If the post names a specific checkable fact, it's `analysis`, even
     if the tone is heated." -->

If the post names a specific fact that can be checked from a public source, it is `informative`, even if the post may not be professional. A personal story or numbers about the poster themselves don't count as checkable. If it is simply an opinion, it is a `hot_take`.

**Other rule:** Swearing alone doesn't make a post `offensive`. "Bivol fucking destroyed Canelo, and we think Canelo is a GOAT?" is a `hot_take`, because the swear is emphasis, not an insult. A post is only `offensive` if it attacks someone. If a post insults someone, it's `offensive` even if it also makes a hot take.

---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:**
Public comments copied by hand from three r/boxing threads in October 2026: one about Ricky Hatton's estate and his family, one about a Deontay Wilder knockout (which turned into a Wilder vs Zhang debate), and one about Ryan Garcia stopping Conor Benn. I pasted the whole threads into text files and used a small script to strip the Reddit page clutter (usernames, timestamps, vote counts, buttons, badges and two ads), then checked for duplicates. That gave 229 comments; I kept the first 200 and dropped the last 29. Posts are kept whole, including some off-topic replies (a gym story, posts about wrestler Chris Benoît), because that's what the threads actually contained.

**How I labelled them:** <!-- Cold first? Pre-labelled with AI and corrected?
Say so plainly — the disclosure is required, not penalised. -->
I labelled the first 20 posts cold, on my own with no tools, using only my definitions (`note` = `cold`). The other 180 were pre-labelled by an AI tool (Claude) given my four definitions and decision rules. I then read every one of those 180 and checked the label (`note` = `pre-labelled, checked`). Close calls are flagged with `hard:` in the note.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| `hot_take` | 120 | 60% |
| `humorous` | 40 | 20% |
| `informative` | 32 | 16% |
| `offensive` | 8 | 4% |
| **Total** | 200 | 100% |

`hot_take` is above the 50% cap in my criterion #2, and `offensive` has only 8 examples, so expect about one in the test split. Part of the reason `hot_take` is so big is that questions, bare reactions ("Depressing stuff") and off-topic replies don't fit any of my four labels, and they all ended up as `hot_take`.

**Three hard cases**

<!-- Any post that made you pause: what it was, which two labels it could have
     been, and what you chose. These are worth more than the easy 190. -->

**1.**
> *The post:* I don't buy that tbh, that always seemed like a 'save face' explanation. The fact he was training for some shocker of a fight in Dubai makes a more compelling case for money issues imo.
>
> *Could have been:* `hot_take` or `informative`
>
> *I chose, because:* `informative`, because the Dubai fight Hatton was training for is a checkable public fact, and it's the reason the poster gives for money trouble.

**2.**
> *The post:* Yeah bro he was so special, knocking out every can fighter he stepped in the ring with. What a legend, I will never forget when he knocked out Herndon...
>
> *Could have been:* `humorous` or `hot_take`
>
> *I chose, because:* `humorous`, because it is a sarcastic post about knocking out "cans", a fighter than is unworthy of any praise. Humorous.

**3.**
> *The post:* Stomp that ho
>
> *Could have been:* `humorous` or `offensive`
>
> *I chose, because:* `humorous`, because it is a humorous statement and is not meant to be taken seriously. Humourous.

---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:** `distilbert-base-uncased`

**Settings:** <!-- epochs, learning rate, batch size, seed -->
3 epochs, learning rate 2e-5, batch size 16, max length 128 tokens, seed 42. Trained on **`cpu`** (Intel Core i9-12900K, PyTorch 2.14.1+cpu), which is also what `results.json` recorded. Training took about a minute.

**Anything I changed from the defaults, and why:**
Nothing. I used the notebook defaults.

**Split sizes:** <!-- train / val / test, and per-label counts in the test
split. If a label had fewer than about 8 in test, say so — it explains a lot
of next unit's variance. -->
train 139 / val 31 / test 30.

| Label | Train | Val | Test |
|---|---|---|---|
| `hot_take` | 83 | 19 | 18 |
| `informative` | 22 | 5 | 5 |
| `humorous` | 28 | 6 | 6 |
| `offensive` | 6 | 1 | 1 |

Three labels have fewer than 8 examples in the test split: `informative` (5), `humorous` (6) and `offensive` (1). Their F1 scores rest on very few posts and will move a lot between seeds. `offensive` with a single test post can only score 0 or 1.

---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- *What I asked for: A labeller for reddit boxing comments/posts.*
- *What came back: A labeller using the labels I chose that worked for all the posts we copy and pasted into the csv.*
- *What I changed: Not much, the labels worked well.*

**Moment 2**

- *What I asked for:* Feedback on my five acceptance criteria after I wrote them: could someone else check each one without asking me what I meant?
- *What came back:* Criteria 2, 4 and 5 couldn't be checked. #2 said ".50 lopsided" without saying what that meant, #4 mixed up confidence and accuracy, and #5 had no number. It also said most of my reasons ("the labels are differentiated") could fit any project. Later I asked it to rewrite my reasons for criteria 1–3 and fix #5, and it did.
- *What I changed:* I rewrote #2, #4 and #5 myself until each named a number someone could check, and I kept all my own target numbers. When it pointed out that my #4 required unsure predictions to be right 10% of the time or less while also needing them right 70% of the time, I removed the contradiction. The reasons under #1–3 and #5 are its wording.

**Pre-labelling disclosure:**
I labelled 20 of the 200 posts in `labels.csv` cold, on my own (`note` = `cold`). The other 180 were pre-labelled by Claude (Claude Code), given my four definitions and decision rules. I read them and accepted the labels (`note` = `pre-labelled, checked`). I labelled all 30 staff posts in `my_staff_labels.csv` myself, with no AI suggestions.

**Other AI use, so it's all disclosed.** I used Claude (Claude Code) throughout this project:
- **Data prep.** It wrote the script that stripped Reddit page clutter from my copy-pasted threads and turned them into `labels.csv`, and the labelling sheets I filled in.
- **Running things.** It ran the notebook (sections 1–7), `baseline.py` (with and without my definitions), `agreement.py` and `test.py`, and made the commits.
- **Writing it drafted from my results, which I read:** the reasons under criteria 1, 2, 3 and 5 in `criteria.md`; this README's Dataset section (apart from my hard-case reasons), Training Run, Run Logs, Verdicts and Diagnoses, the Agreement Report's rate, table, post blocks and pattern paragraph. I chose every pile myself and wrote first drafts of the calls arguing my own label each time; Claude then reworded the calls so each one says who is right, matching my pile, and cites the staff rule, The Improvement, and What's Still Broken.
- **Its suggestions I took:** tightening my label definitions and decision rules in unit 5, and the improvement (10 epochs). I chose 10 epochs out of three options it laid out.
- **Spotting error patterns.** It pointed out that the before run's zero spread across seeds wasn't stability: the model was guessing `hot_take` for every post. It also noticed that bare label names beat my definitions as a baseline prompt.
- **What I wrote myself:** my label taxonomy and examples, the decision rules' choices (anecdotes are `hot_take`, swearing alone isn't `offensive`, insults beat hot takes), the criteria themselves and their numbers, the 20 cold labels, the 30 staff labels, my hard-case reasons, my baseline prediction, and the biggest-confusion sentence.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.233 | 0.600 | +0.367 |
| Macro F1 | 0.128 | 0.188 | +0.059 |
| F1 — `hot_take` | 0.190 | 0.750 | +0.560 |
| F1 — `humorous` | 0.000 | 0.000 | +0.000 |
| F1 — `informative` | 0.323 | 0.000 | -0.323 |
| F1 — `offensive` | 0.000 | 0.000 | +0.000 |

Baseline is `facebook/bart-large-mnli` zero-shot, prompted with my definitions from `label_definitions.txt`, scored on the same 30 posts in `test_split.csv` as the trained model (seed 42, cpu).

**Same baseline with bare label names instead of my definitions** (`baseline_bare_names.json`):

| Measure | Bare names | With my definitions |
|---|---|---|
| Overall accuracy | 0.467 | 0.233 |
| Macro F1 | 0.356 | 0.128 |
| F1 — `hot_take` | 0.600 | 0.190 |
| F1 — `humorous` | 0.600 | 0.000 |
| F1 — `informative` | 0.222 | 0.323 |
| F1 — `offensive` | 0.000 | 0.000 |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->
I had already seen the trained runs numbers, but I predict the trained model will beat the baseline on hot_take and overall accuracy, and loses to it on informative.

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->
Bare label names beat my definitions as a prompt.


---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

Trained on **`cpu`** (Intel Core i9-12900K, PyTorch 2.14.1+cpu), all three seeds. Defaults: 3 epochs, lr 2e-5, batch 16, max length 128.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.80 | 0.600 | 0.600 | 0.600 | MISSED |
| 2. Biggest label share | ≤ 50% of posts | `hot_take` 60% (120/200; 18/30 in test) | 60% (18/30 in test) | 60% (18/30 in test) | MISSED |
| 3. Agreement with another labeller | ≥ 90% | 67% (20/30) vs staff; one measurement, not per seed | — | — | MISSED |
| 4. Confident > 0.90 right ≥ 90%; unsure right ≥ 70% | 90% / 70% | most-sure third 0.80, least-sure third 0.30; mean confidence 0.48 | 1.00 / 0.30; mean 0.47 | 0.50 / 0.50; mean 0.46 | MISSED |
| 5. F1 `hot_take` ≥ 0.50; others ≥ 0.80 | 0.50 / 0.80 | `hot_take` 0.750; `informative`, `humorous`, `offensive` 0.000 | same | same | MISSED |

`results.json` reports confidence by thirds (10 posts each) and mean confidence, not a 0.90 cutoff, so criterion 4 can't be read exactly as written. With four labels, a mean confidence under 0.5 means the model was rarely, if ever, above 0.90.

**Spread across seeds** (notebook section 6):

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.600 | 0.600 | 0.600 | 0.000 |
| Macro F1 | 0.188 | 0.188 | 0.188 | 0.000 |
| F1 — `hot_take` | 0.750 | 0.750 | 0.750 | 0.000 |
| F1 — `informative` | 0.000 | 0.000 | 0.000 | 0.000 |
| F1 — `humorous` | 0.000 | 0.000 | 0.000 | 0.000 |
| F1 — `offensive` | 0.000 | 0.000 | 0.000 | 0.000 |

The spread is zero, but that isn't stability. On every seed the model predicted `hot_take` for all 30 test posts, and the stratified split always puts 18 `hot_take` posts in a 30-post test set, so every seed gets the same 0.600.

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

Seed 42 (seeds 7 and 2024 are identical):

| true \ predicted | hot_take | informative | humorous | offensive |
|---|---|---|---|---|
| **hot_take** | 18 | 0 | 0 | 0 |
| **informative** | 5 | 0 | 0 | 0 |
| **humorous** | 6 | 0 | 0 | 0 |
| **offensive** | 1 | 0 | 0 | 0 |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->
6 real `humorous` posts were called `hot_take`, and 0 real `hot_take` posts were called `humorous`. The model never learned the `humorous` vs `hot_take` boundary, so it always resolved toward `hot_take`.




---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy on the held-out test set | ≥ 0.80 on all three seeds | MISSED | 0.600 on all three seeds (42, 7, 2024), below 0.80 on every one. |
| 2 | Biggest label share | ≤ 50% of posts | MISSED | `hot_take` is 120 of 200 posts (60%), and 18 of 30 in every test split. |
| 3 | Agreement with another labeller | ≥ 90% | MISSED | I agreed with staff on 20 of 30 posts (67%) in the agreement check, below 90%. It's one measurement, since it doesn't depend on the seed. |
| 4 | Confident (> 0.90) right ≥ 90%; unsure right ≥ 70% | 90% / 70% | MISSED | The least-sure third was right 0.30, 0.30 and 0.50 of the time, below 70% on every seed. The 0.90 cutoff itself can't be read from `results.json`, which reports thirds. |
| 5 | F1 `hot_take` ≥ 0.50; `informative`, `humorous`, `offensive` ≥ 0.80 | 0.50 / 0.80 | MISSED | `hot_take` 0.750 passes, but the other three are 0.000 on all three seeds. |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->

**The model never learned anything except "guess `hot_take`".** Criteria 1, 4 and 5 all miss for this reason, and 2 is the cause of it.

- **What happened.** On all three seeds the model called all 30 test posts `hot_take`. The confusion matrix has every prediction in the `hot_take` column. Validation accuracy was 0.613 after every one of the three epochs, which is exactly the `hot_take` share of the validation split (19 of 31). The model reached that by guessing the majority label in epoch 1 and never moved off it. Training loss only fell from about 1.32 to 1.16.
- **Cause 1: too few examples of the thin labels (criteria 1, 5).** The training split has 83 `hot_take` posts but only 28 `humorous`, 22 `informative` and 6 `offensive`. With 3 epochs at learning rate 2e-5 on 139 posts, always guessing `hot_take` already scores 60%, and the model didn't train long enough to find anything better. `offensive` has 1 post in each test split, so its F1 can only ever be 0 or 1.
- **Cause 2: `hot_take` is a catch-all, a labelling problem (criteria 2, 5).** At least 16 posts are `hot_take` only because no other label fit: questions, bare reactions ("Depressing stuff"), off-topic replies about families and wrestling. My notes flag them as "no label fits well" or "off-topic". That makes `hot_take` both the biggest label and the vaguest one, so it has no single pattern for the model to learn and it absorbs everything else.
- **This isn't a task the model can't reach.** The zero-shot baseline, given only bare label names, got `humorous` F1 0.600 on the same posts. So the humour in these posts can be detected from the text. My trained model's 0.000 comes from the data and the short training, not from humour being invisible.
- **Criterion 4 (confidence).** Mean confidence was 0.46 to 0.48 on every seed, which is barely above a four-way coin flip (0.25) and nowhere near 0.90. A model that always gives the same answer isn't confident about any post, so the confident and unsure groups don't mean much here. The criterion is also partly unmeasurable as written, because the notebook reports thirds rather than a 0.90 cutoff.
- **What the agreement report shows (criterion 3, and evidence for criterion 5).** I agreed with staff on 20 of 30 posts (67%). 6 of my 10 disagreements are posts staff called `analysis` that I didn't: I called 3 `reaction` and 3 `hot_take`, and matched staff on only 4 of their 10 `analysis` posts. Staff `analysis` is the same idea as my `informative`: a checkable fact that carries the argument. So the boundary where I disagree with an outside labeller most is the boundary of the label my model never learned (`informative` F1 0.000 on every seed). That points at my labelling as part of the cause of the `informative` miss, not only the model. If I under-credit checkable facts on 30 staff posts, I probably did the same across my 200, which gives the model an inconsistent signal for `informative` on top of having only 22 training examples.



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** 20 / 30 = 67%

I labelled the 30 staff posts under the staff taxonomy in `data/staff_taxonomy.md` and committed them in `my_staff_labels.csv` (commit `1c20bd0`) before I had the answer key. I got `data/staff_labels.csv` afterwards and ran `python agreement.py`, which wrote `agreement_results.json`. My labels weren't changed after seeing the key.

| staff \ me | analysis | hot_take | reaction |
|---|---|---|---|
| **analysis** | 4 | 3 | 3 |
| **hot_take** | 1 | 8 | 1 |
| **reaction** | 1 | 1 | 8 |

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:* Pulled the splits from the last five editions. The winning time has moved by 40 seconds total in ten years, but the 100th-place time is four minutes faster. The depth changed, the front didn't.
>
> *Staff said / I said:* Staff said `analysis` / I said `reaction`
>
> *My call, and why:* Staff is right. I read it as a `reaction` to how much the times moved, but nothing here is about the writer's own race or feelings, and rule 3 says recency doesn't outrank evidence. The two checkable numbers (40 seconds at the front, four minutes at 100th place) are the whole argument, so under rule 1 it's `analysis`. I applied rule 1 loosely.
>
> *Which pile:* (a)

**2.**
> *The post:* The club championship scoring changed in 2019 from top-6 to top-10. Since then our B team has finished above the A team twice. That's not depth improving, it's the scoring rewarding turnout.
>
> *Staff said / I said:* Staff said `analysis` / I said `reaction`
>
> *My call, and why:* Staff is right. I called it a `reaction` because it's about the writer's own club, but rule 2 says a reaction reports what just happened to the writer and how it felt, and this argues a general point instead. A named date (2019), a named rule change (top-6 to top-10) and a result (B team above A team twice) are what the conclusion rests on, so rule 1 makes it `analysis`.
>
> *Which pile:* (a)

**3.**
> *The post:* Ran the same loop in 4C and in 24C within a fortnight, same effort by heart rate. 90 seconds slower in the heat over six miles. People keep saying heat costs you 'a bit' and it's more than that.
>
> *Staff said / I said:* Staff said `analysis` / I said `hot_take`
>
> *My call, and why:* Staff is right. I focused on the confident last sentence and called it a `hot_take`, but the post gives its support: the same loop at 4C and 24C, same effort, 90 seconds slower. Rule 1 asks whether the fact carries the argument, and here it does. The conclusion ("it's more than a bit") comes from the number, not before it.
>
> *Which pile:* (a)

**4.**
> *The post:* Went back through the club results going back to 2012. Every single year the number of people who enter the spring marathon and don't start it sits between 18 and 23 percent. It's not a bad-luck year, it's the base rate.
>
> *Staff said / I said:* Staff said `analysis` / I said `reaction`
>
> *My call, and why:* Staff is right. Nothing in the post just happened to the writer, so rule 2's test for `reaction` fails. The 18–23% range across every year since 2012 is used to reject the "bad-luck year" explanation, which is exactly a fact doing work in the argument under rule 1, so it's `analysis`.
>
> *Which pile:* (a)

**5.**
> *The post:* The 10K route was remeasured in 2021 and came out 60 metres long. Everyone comparing PBs from before and after that is comparing two different races, which is about 12 seconds at club pace.
>
> *Staff said / I said:* Staff said `analysis` / I said `hot_take`
>
> *My call, and why:* Staff is right. I took "everyone comparing PBs is comparing two different races" as an unsupported claim, but it is supported. The 2021 remeasurement and the 60 metres (about 12 seconds) are the reason the claim holds. Under rule 1 that's `analysis`, not a `hot_take`.
>
> *Which pile:* (a)

**6.**
> *The post:* Three of us ran the same session on the same day, different shoes, within 10 seconds of each other over 5 miles. I'm not saying shoes do nothing, but whatever they do was smaller than the noise between three people.
>
> *Staff said / I said:* Staff said `analysis` / I said `hot_take`
>
> *My call, and why:* Staff is right. I saw an opinion about shoes and called it a `hot_take`, but the writer ran a comparison (three runners, same session, within 10 seconds over 5 miles) and draws a hedged conclusion from it. Rule 1: the fact carries the argument, so it's `analysis`. The hedging ("I'm not saying shoes do nothing") makes it more like analysis, not less.
>
> *Which pile:* (a)

**7.**
> *The post:* Times are down about 3% since the shoe rules changed, so obviously the shoes are the whole story and the sport has a problem.
>
> *Staff said / I said:* Staff said `hot_take` / I said `analysis`
>
> *My call, and why:* I'd defend `analysis`. "Times are down about 3% since the shoe rules changed" is a checkable fact, and it's the only reason the post gives, joined to the conclusion by "so". Rule 1 says a fact is decoration when the writer had already reached the conclusion, but nothing in the post shows which came first. The staff reading leans on tone ("so obviously", "whole story") to decide that. I accept the conclusion overreaches what 3% can show, which is why this is ambiguous rather than a clear win, but the rule doesn't give a way to tell decoration from a thin reason when the fact is the only support offered.
>
> *Which pile:* (c)

**8.**
> *The post:* Every injury thread on this forum is the same injury and the same three replies.
>
> *Staff said / I said:* Staff said `hot_take` / I said `reaction`
>
> *My call, and why:* The rules don't settle this one. Rule 2 splits posts into a report of what just happened to the writer (`reaction`) and a general claim about the world (`hot_take`). This post is a general claim ("every injury thread"), but it's about the writer's own repeated experience of reading this forum, not about running or the world outside it, and not about something in the last few hours. I read it as frustration (`reaction`); staff read the "every" as a general claim (`hot_take`). The definitions don't cover an ongoing personal irritation phrased as a generalisation, so I'd call this a gap rather than say either of us applied a rule wrong.
>
> *Which pile:* (b)

**9.**
> *The post:* First run back after eight weeks out. Two miles, slower than my warm-up used to be, and I don't care even slightly.
>
> *Staff said / I said:* Staff said `reaction` / I said `analysis`
>
> *My call, and why:* Staff is right. I saw numbers (eight weeks, two miles, slower than a warm-up) and called it `analysis`, but nothing is argued from them. They're the news, and "I don't care even slightly" is the feeling. It's the writer's own run, just done, so rule 2 makes it a `reaction`, and rule 3 doesn't turn it into analysis because no fact is load-bearing.
>
> *Which pile:* (a)

**10.**
> *The post:* Wind was so bad on the out section I was leaning at about 20 degrees. Coming back felt like cheating.
>
> *Staff said / I said:* Staff said `reaction` / I said `hot_take`
>
> *My call, and why:* I'd defend `hot_take`, though it's close. "Leaning at about 20 degrees" isn't a real measurement, it's an exaggerated claim about how strong the wind was, and "felt like cheating" is a judgment about the course rather than a report of what the writer did. Staff read both as the writer describing their own run (rule 2, `reaction`). Rule 2 separates claims about the world from reports about the writer, and here the writer's experience is the evidence for a claim about the conditions, so both readings are defensible.
>
> *Which pile:* (c)

**What the pattern in my disagreements tells me:**
My disagreements cluster on one boundary. 6 of the 10 are posts staff called `analysis` that I called `reaction` (3) or `hot_take` (3), so I was much stricter than staff about when a fact "carries the argument" (rule 1). Staff had 10 `analysis` posts and I had only 6, and only 4 of those matched. The other two staff labels I mostly agreed on: 8 of 10 for both `hot_take` and `reaction`. This is the same boundary as my own `informative` label, which my model never learned. That suggests my own labelling of checkable facts is part of why: I didn't apply that boundary consistently.

---

## The Improvement

**What I changed:**
One training setting: `EPOCHS` from 3 to 10. Everything else is the same: same `labels.csv`, same three seeds (42, 7, 2024), learning rate 2e-5, batch size 16, max length 128, `distilbert-base-uncased`, trained on `cpu`. Results are in `results_three_seeds_after.json`.

**Which diagnosis pointed at it:**
Cause 1. In the before run, validation accuracy was 0.613 after every epoch, exactly the `hot_take` share of the validation split, and training loss only fell from about 1.32 to 1.16. Three epochs on 139 posts is only 27 training steps, and the model settled on "always `hot_take`" in epoch 1 and never moved. That pointed at training length rather than at the labels. I didn't pick a data fix because I couldn't run the agreement check to show a boundary was labelled inconsistently.

### Run Log — After

Trained on **`cpu`** (Intel Core i9-12900K, PyTorch 2.14.1+cpu), all three seeds. 10 epochs, everything else unchanged.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.80 | 0.700 | 0.767 | 0.633 | MISSED |
| 2. Biggest label share | ≤ 50% of posts | `hot_take` 60% (120/200; 18/30 in test) | 60% | 60% | MISSED |
| 3. Agreement with another labeller | ≥ 90% | 67% (20/30), unchanged: training doesn't affect it | — | — | MISSED |
| 4. Confident > 0.90 right ≥ 90%; unsure right ≥ 70% | 90% / 70% | most-sure third 0.80, least-sure third 0.60 | 1.00 / 0.70 | 0.70 / 0.50 | MISSED |
| 5. F1 `hot_take` ≥ 0.50; others ≥ 0.80 | 0.50 / 0.80 | `hot_take` 0.791, `humorous` 0.727, `informative` 0.000, `offensive` 0.000 | 0.837 / 0.909 / 0.000 / 0.000 | 0.766 / 0.286 / 0.000 / 0.000 | MISSED |

**Spread across seeds** (notebook section 6):

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.700 | 0.767 | 0.633 | 0.133 |
| Macro F1 | 0.379 | 0.437 | 0.263 | 0.174 |
| F1 — `hot_take` | 0.791 | 0.837 | 0.766 | 0.071 |
| F1 — `informative` | 0.000 | 0.000 | 0.000 | 0.000 |
| F1 — `humorous` | 0.727 | 0.909 | 0.286 | 0.623 |
| F1 — `offensive` | 0.000 | 0.000 | 0.000 | 0.000 |

**Confusion matrix, after** (seed 42):

| true \ predicted | hot_take | informative | humorous | offensive |
|---|---|---|---|---|
| **hot_take** | 17 | 0 | 1 | 0 |
| **informative** | 5 | 0 | 0 | 0 |
| **humorous** | 2 | 0 | 4 | 0 |
| **offensive** | 1 | 0 | 0 | 0 |

**Before and after, side by side:**

| Measure | Before (3 epochs), seeds 42 / 7 / 2024 | After (10 epochs), seeds 42 / 7 / 2024 |
|---|---|---|
| Overall accuracy | 0.600 / 0.600 / 0.600 | 0.700 / 0.767 / 0.633 |
| Macro F1 | 0.188 / 0.188 / 0.188 | 0.379 / 0.437 / 0.263 |
| F1 — `hot_take` | 0.750 / 0.750 / 0.750 | 0.791 / 0.837 / 0.766 |
| F1 — `humorous` | 0.000 / 0.000 / 0.000 | 0.727 / 0.909 / 0.286 |
| F1 — `informative` | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 |
| F1 — `offensive` | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->

Yes, partly. Accuracy went up on every seed (+0.100, +0.167, +0.033) and macro F1 roughly doubled. The model stopped guessing `hot_take` for everything: it learned `humorous`, with F1 0.727 and 0.909 on two seeds where before it was 0.000 on all three. But it didn't move any criterion from MISSED to MET. Accuracy still tops out at 0.767, against a target of 0.80.

Two labels didn't move at all. Every real `informative` post was still called `hot_take` on all three seeds (5 of 5 each time), and the single `offensive` test post was missed every time. So the extra training let the model learn the one thin label with the most training examples and clear surface cues ("LMAO", emojis), but not the two that need more than that.

The numbers are also no longer stable. Accuracy now moves 0.133 across seeds and `humorous` F1 swings from 0.286 to 0.909. With only 6 `humorous` posts in each test split, one or two posts landing differently changes the score a lot, which is the small-dataset problem from Cause 1 showing up now that the model predicts more than one label.

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->

Every criterion that was measured is still MISSED after the improvement.

- **1. Overall accuracy ≥ 0.80** (after: 0.700 / 0.767 / 0.633). **What I'd do:** collect about 30 more `informative` and `offensive` posts. Those two labels are still 0.000 F1 and are where the remaining errors are, since every `informative` test post goes to `hot_take`. **Why I stopped:** the milestone allows one change per run, and I used it on training length because that's what my diagnosis pointed at. Collecting more posts means copying another batch from Reddit and labelling it, which I didn't do.
- **2. Biggest label ≤ 50%** (`hot_take` 60%). **What I'd do:** two things. Collect posts from threads that produce insults and fact-based posts, like "most overrated" threads and stats or records threads. And stop using `hot_take` as the default for questions, bare reactions and off-topic replies, either by leaving those posts out or by giving them their own label. **Why I stopped:** both mean changing the dataset, and my one change went to training.
- **3. Agreement ≥ 90%** (67%). **What I'd do:** reread rule 1 and go back over the 6 `analysis` posts I missed until I can say why the fact carries each one. Then relabel the `informative` boundary in my own 200 posts the same way and retrain. That's the relabelling improvement this evidence points at. **Why I stopped:** I only got the staff labels after I'd already used my one change on training length.
- **4. Confidence** (after: least-sure third 0.60 / 0.70 / 0.50). **What I'd do:** first, revise the criterion so it matches what the notebook measures (thirds, not a 0.90 cutoff). Then add data, because a model this unsure about most posts won't separate confident from unsure guesses well. **Why I stopped:** I only got as far as noting the measurement problem.
- **5. Per-label F1** (`informative` and `offensive` 0.000 on every seed). **What I'd do:** add examples of both. `offensive` has 6 training posts and 1 test post, so its F1 can only be 0 or 1. `informative` may also be a task the model can't reach from this data, for the reason below. **Why I stopped:** same as criterion 1.

**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->

I meant `informative` to capture whether a post contains a fact you could check from a public source. But the model called all 5 `informative` test posts `hot_take` on every seed, before and after the improvement, so it never learned that checkability isn't visible in the wording of a post. What it did learn, at 10 epochs, is surface style: posts with "LMAO", emojis and joke phrasing become `humorous`, and everything else becomes `hot_take`, which is why `humorous` is the only thin label it ever gets right.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
