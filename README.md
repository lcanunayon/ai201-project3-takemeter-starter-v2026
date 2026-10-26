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
| 3. Agreement with another labeller | ≥ 90% | not measured by training; see Agreement Report | — | — | Pending agreement check |
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



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy on the held-out test set | ≥ 0.80 on all three seeds | MISSED | 0.600 on all three seeds (42, 7, 2024), below 0.80 on every one. |
| 2 | Biggest label share | ≤ 50% of posts | MISSED | `hot_take` is 120 of 200 posts (60%), and 18 of 30 in every test split. |
| 3 | Agreement with another labeller | ≥ 90% | Pending | Not a training number. Decided by the agreement check against the staff set. |
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
- **Still to check with the agreement report.** If my agreement with staff is low on the `hot_take` boundaries, Cause 2 is confirmed as a labelling problem, not only a data-size problem. I'll update this once the agreement check is done.



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

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
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



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
