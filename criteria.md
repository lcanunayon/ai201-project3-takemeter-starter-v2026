# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1.

<!-- Your criterion. It must name a number. -->
The model must have an overall accuracy of at least .80 on the held-out test set, on all three seeds.



**Why this target:**
With four labels, random guessing gets about 25%, so 0.80 has to come from the model actually learning the labels. I think it can because most boundaries have a clear marker: `informative` needs a fact you could check publicly, `humorous` posts are usually just a joke or "LMAO", and `offensive` needs an insult aimed at someone. Most of the misses should come from the anecdote posts between `hot_take` and `informative`, which is why I didn't go higher than 0.80.



---

## 2.

<!-- Your criterion. -->
The biggest label is at most 50% of posts.




**Why this target:**
Most r/boxing comments are opinions about fighters, so `hot_take` will probably be my biggest label. Capping it at 50% keeps the other half of the posts for `informative`, `humorous` and `offensive`, so they each get enough training examples. It also means a model that always guesses `hot_take` could score at most 0.50, well below my 0.80 target in #1.


---

## 3.

<!-- Your criterion. -->
The labeller should be consistent and if someone else labeled the same posts, you should agree 90% of the time.


**Why this target:**
I wrote decision rules for my two hardest boundaries (personal stories with numbers are `hot_take`, and swearing alone isn't `offensive`), so someone using my definitions should land on the same label for most posts. The disagreements I expect are jokes that also mock a fighter, which sit between `humorous` and `hot_take` and don't have a rule yet. That's why I set it at 90% and not higher.



---

## 4.

<!-- Your criterion. -->
On the held-out test set, predictions with confidence > 0.90 are right at least 90% of the time.

For unsure confidence predictions, labelling should be right 70% of the time still.


**Why this target:**
Confidence should have a high cutoff such as .90 if confident. Unsure should be right 70% of the time because it is well above random guessing 25% accuracy rate with four labels.



---

## 5.

<!-- Your criterion. -->
On the held-out test set, `hot_take` F1 >= 0.50, and `informative`, `humorous` and `offensive` each have F1 >= 0.80, on all three seeds.


**Why this target:**
`hot_take` shares a boundary with all three other labels: anecdote posts with numbers look `informative`, opinions with swearing look `offensive` even though swearing alone doesn't count, and jokes that mock a fighter look `humorous`. Since it's the label the model is most likely to confuse with the others, I'm allowing it a lower F1 than the rest.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
