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

- *What I asked for: Help with criteria writing after I wrote my own.*
- *What came back: Ideas for F1 acceptance in order to test my model.*
- *What I changed: I changed some of the F1 numbers to match what I wanted, and it worked well.*

**Pre-labelling disclosure:**
I labelled 20 of the 200 posts in `labels.csv` cold, on my own (`note` = `cold`). The other 180 were pre-labelled by Claude (Claude Code), given my four definitions and decision rules. I read them and accepted the labels (`note` = `pre-labelled, checked`). I labelled all 30 staff posts in `my_staff_labels.csv` myself, with no AI suggestions.

**Other AI use, so it's all disclosed.** I used Claude (Claude Code) throughout this project:
- **Data prep.** It wrote the script that stripped Reddit page clutter from my copy-pasted threads and turned them into `labels.csv`, and the labelling sheets I filled in.
- **Running things.** It ran the notebook (sections 1–7), `baseline.py` (with and without my definitions) and `test.py`, and made the commits.
- **Writing it drafted from my results, which I read:** the reasons under criteria 1, 2, 3 and 5 in `criteria.md`; this README's Dataset section (apart from my hard-case reasons), Training Run, Run Logs, Verdicts and Diagnoses, the Agreement Report disclaimers, The Improvement, and What's Still Broken.
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
| 3. Agreement with another labeller | ≥ 90% | not measured: staff labels unavailable (see Agreement Report) | — | — | NOT MEASURED |
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
| 3 | Agreement with another labeller | ≥ 90% | NOT MEASURED | Decided by the agreement check against the staff set, and I couldn't run it because I didn't have `data/staff_labels.csv`. No number, so no MET or MISSED. |
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
- **Not confirmed by the agreement report.** The agreement check is the only thing that could show whether Cause 2 is a labelling problem rather than only a data-size problem, and I couldn't run it (see Agreement Report). So Cause 2 rests on my own labelling notes (the 16 posts flagged "no label fits well" or "off-topic") and on the confusion matrix, not on outside evidence. Cause 1 doesn't depend on the agreement check.



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** not computed. I wasn't able to get `data/staff_labels.csv` from my TF, so there was nothing to compare my labels against.

**What I did do:** I read `data/staff_taxonomy.md` and labelled all 30 posts in `data/staff_posts.csv` under the staff definitions and decision rules, not my own. My labels are in `my_staff_labels.csv` (12 `reaction`, 12 `hot_take`, 6 `analysis`), committed before I had any answer key (commit `1c20bd0`).

**What's missing because of that:**
- No agreement rate, and no `agreement_results.json`. `agreement.py` needs the staff labels and stops without them. I didn't make up a staff file or a rate.
- No disagreements to adjudicate, so there are no pile (a)/(b)/(c) calls below.
- Criterion 3 (≥ 90% agreement) is NOT MEASURED, not MET or MISSED.
- My diagnosis of `hot_take` as a catch-all (Cause 2) can't be checked against an outside labeller.

If I get the staff labels later, running `python agreement.py` with my committed `my_staff_labels.csv` will produce the rate and the disagreement list without relabelling anything.

**What the pattern in my disagreements tells me:**
Nothing yet, since there were no disagreements to look at. The one thing my own 30 labels show is that I used all three staff labels, with `analysis` the least common (6 of 30). I can't tell whether that matches staff or means I was strict about rule 1 (the fact has to carry the argument).

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
| 3. Agreement with another labeller | ≥ 90% | not measured: staff labels unavailable | — | — | NOT MEASURED |
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
- **3. Agreement ≥ 90%** (not measured). **What I'd do:** get `data/staff_labels.csv` and run `python agreement.py` against my committed `my_staff_labels.csv`. **Why I stopped:** I couldn't get the staff file.
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
