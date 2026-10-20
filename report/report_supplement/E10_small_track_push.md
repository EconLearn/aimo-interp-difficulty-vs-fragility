# Supplement to the technical report: Appendix E.10 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October (draft 28): a passage that speculated about another team's entry is replaced by one neutral sentence;
text moved out of the report in draft 28 is in the addendum of 20 October (draft 28) at the end of this file. Note added
20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29) at the end
of this file; the report keeps a summary or a pointer.*

### E.10 The small-track push: noise floor and nine readings (Section 3.1)

Run on 13-14 October after the nominees were chosen [411-420]; CPU analyses of logs and public data, plus one
pre-registered research read on the 28 public templates (Codabench 986037, every hidden case answered robust, board 0.48
by design) [417, 418]. Single reads; "post hoc" marks a reading looked at before its bar was written.

**The small board.** Under the original harness nothing we built beat 9 of 14. Own-run variants scored 9 [341], 9 [352],
8 [366] and 8 [369], with Olmo's pattern on the same three problems different in each distinct run (Appendix E.5),
against 8 for the stand-in [284] and 9 for Skywork run to the end [289]; the leaders were at 12 [352]. Under the
per-case harness the same rules (v96) scored 10, a single draw [471]. Most problem-level readings agree on about nine of
the 14 cases and behave like coin flips on the rest [341]. Our eleven scored small entries up to 9 October ranged from 5
to 9, mean 7.5, against 7.0 for coin flips [284]; we record an unsolved generalization problem. (1) *The labels sit
outside the original's solve rate.* On the 16 labelled public small-model rows whose problems have public full-length
runs, every row is solved 4 of 4 times, robust and non-robust alike (the 4 Qwen rows by Qwen3.5-4B itself, the other 12
by a 4B stand-in solver, Qwen3-4B-2507, a proxy) [416]. Full-length solution length (longer = non-robust) gives AUC
0.730 on the same 16 rows (`la3b_margin.out`; row permutation p about 0.07 before allowing for four rows sharing T13),
and on 9 templates a pooled AUC of 0.92, p 0.036 [412] (Qwen3.5-4B alone 0.83, p 0.083; `c1_cryptic.out`). Both separate
easy from hard rows: the 16 rows are 8 easy (all robust) and 8 hard (7 non-robust), and inside the hard rows the one
robust row (T16, Qwen3.5-4B median 22,332 tokens) is longer than 5 of the 7 non-robust rows (AUC 0.29). With Qwen3.5-4B
lengths the 0.73 also turns on a one-token median difference between T13 and T17. Post hoc, few rows and templates. Five
of the ten public small-model non-robust rows have drops at exact multiples of 0.1 (T13 for four models, and T20); the
label law that fits the public rows needs one variant family of about 10 predictions, i.e. a single text, and is
rejected without one: across all models, 7 of the 19 public non-robust rows sit on tenths, and without a single-text
family the chance of 7 or more is 0.0015 [416]. (2) *A solve-rate oracle reaches a range that includes our 8 to 9*: 7.4
to 11.0 of 14 across the current-recipe solve-rate and selection scenarios, 7.4 to 9.1 with full-length (MathArena)
solve rates; the other measured scenario, our capped own runs, reaches 11.0 [416]. (3) *The board's 12s are consistent
with selection.* One upload at true accuracy 0.70 reaches 12 of 14 with probability 0.16 (0.45 at 0.80); replaying every
team's uploads at its own median gives 8 (correlated draws) to 12 (independent draws) teams at 12 or more, and five did
[416]. This is a model-based estimate with wide intervals (ours 0.60, 90% interval 0.40 to 0.78), not a measurement of
any team's method. A per-case-era 14 of 14 is one other team's entry [467, 468]; we do not analyse other teams' entries. Route diversity, the only reading with a post hoc signal (AUC 0.83 on nine
templates with public full-length runs [412]), scored 0.39 on the hard public rows in a pre-registered server read [417,
420].

**Noise floor (computed, [416]).** Label law (five LLM families assumed, as in the proposal paper): base sampling plus five LLM-rewrite families (each ~100 predictions) plus
one hand-edited single-text family (~10 predictions). Sampling noise alone explains ~3% of public non-robust labels
(likelihood-ratio statistic 58.7 between the fitted law and the best noise-only fit); in the current-recipe fit
(`la2`) LLM-rewrite families show no effect beyond binomial noise and the single text breaks a model with probability
about 0.3 (keeping about 60% of its accuracy when it does); in the organisers' older per-family sample (`la1`), edited
texts broke a model with probability ~0.11 and no-solution texts ~0.36. The chance of a non-robust label is flat in the
solve rate between 0.5 and 1.0 (about 0.18 to 0.21 of all cases, 0.21 to 0.29 of labelled cases). Oracles on 20,000 class-balanced 14-case sets per scenario (solve rates
from public full-length runs, from our capped own runs, or uniform on 0.5-1; two label-selection rules consistent with
the public drops; break propensity flat or rising with difficulty): knows only the solve rate 7.4-11.0; knows the solve
rate and every family's break rate 11.1-13.7 (current-recipe scenarios; some scenarios simulated under the organisers'
older recipe fall outside these ranges, `la3_oracle.out`; the ledger's summary [416] gives 7.4 to 10.2 and 12 to 14,
which the output file supersedes). A third selection rule seen in the organisers' older sample
(robust only if perfect, non-robust only if the drop is at least 0.5) would let the solve-rate oracle reach 8.7-13.9,
but it is inconsistent with the public small-model drops (7 of 10 below 0.5), so we exclude it. Board: P(one upload
>= 12 of 14) = 0.04 / 0.16 / 0.28 / 0.45 at true accuracy 0.60 / 0.70 / 0.75 / 0.80 (binomial).

| Reading (lane) | Hypothesis | Bar (set before the data unless marked) | Measured | Verdict |
|---|---|---|---|---|
| Rescued wrong answers inside correct traces (transfer: canalization) | a model that recovers from wrong intermediate answers is fragile | AUC >= 0.85, permutation p <= 0.05, >= 4 of 5 length-matched pairs, >= 2 of 3 replication readers >= 0.70 | AUC 0.556, p 0.583, 2 of 5 pairs, 0 of 3 replications [412] | killed |
| Reading load (transfer: psychometrics, item bias) | long or dense statements break small models | none (exploratory) | AUC 0.11-0.44 [412] | no vector |
| Route diversity among correct attempts (transfer: flaky tests) | a model that reaches the answer by many routes is fragile | hard-row AUC >= 0.65; >= 0.60 length-residualised; template-rotated sabotage worse by > 0.10 (set after a post hoc 0.83 on 9 public full-length templates) | gpt-oss low K 16, 28 templates: 0.387; residualised 0.399; sabotage gap +0.018 [420] | killed |
| Arithmetic-slip share of wrong answers (literature) | slips mark fragile problems | hard AUC above the shuffle 95th percentile | 0.615 against 0.733 [415] | killed |
| Recitation of a famous parent problem (literature) | models answer the parent, not the edit | parent answers in a material share of attempts | 1 of 392, 0 of 303, 0 of 276 attempts [415] | killed |
| Early answer commitment (literature) | an early first answer marks a memorised, fragile solve | hard AUC above the shuffle 95th percentile | 0.709 / 0.662 against 0.747 / 0.756; equal to median length on small rows [415] | killed |
| Sampling loops in unfinished 7B attempts (literature) | unfinished work that is a loop is not fragility | >= 10% of not-ended Skywork / Olmo attempts degenerate (last-2,000-token loop share >= 0.20) | 1 of 67 (1.5%) [420] | killed |
| Answer size above 999 (cross-collision) | edited famous problems with large answers break | information only (2 templates) | 1 public template (T13) [420] | no rule |
| 62 observables in our own logs (error concentration, entropy, distinct answers, length spread, near misses, thinking minus no-thinking, ...) | some per-attempt statistic separates hard robust from hard non-robust | **post hoc** [413]: family-wise p <= 0.10 on 11 target templates and within-model AUC >= 0.65 on another team's public labelled generations | best cell exact p 0.039, family-wise p 0.82; within solved cells every observable <= 0.61 [413] | none passes |

**Main-track oracle (Section 3.1; computed, model-based, [432]).** `la6_main_oracle.py` reuses the small-track machinery
on the main shape, with four solve-rate scenarios for gpt-oss cases: the label-law fit, our gpt-oss low K 16 modal share
(a proxy: no keyed gpt-oss solve rates exist in our files), the organisers' May gpt-oss low sample, and uniform on 0.5
to 1; four allocations of the 10 robust cases over configurations; the excluded selection rule printed for information
only. Checks: the small subset reproduces the small-track oracle within 0.14; an oracle fed shuffled solve rates scores
10.0 to 11.0 of 21 (no information). Solve-rate oracle 10.7 to 17.0 (above 16 only for the May sample without
selection); solve-rate-and-family oracle 16.5 to 20.4; per configuration about 0.63 against 0.91 of cases right. Our
level against both oracles:

| Our level | Above the solve-rate oracle in | Below the family oracle by (mean over 96 scenarios) | Below it in |
|---|---|---|---|
| H1: the recipe's fitted level, about 17.3 of 21 (0.825, Appendix A.2) | 96 of 96 scenarios | about 1.9 cases (range −0.77 to +3.15) | 93 of 96 |
| H2: v95's one draw, 16 of 21 (Section 4.2) | 92 of 96 | about 3.2 cases | 96 of 96 |

At 17.3 the gap is spread evenly over small-model and gpt-oss cases (computed from `la6_main_oracle.out`, the 96
scenario rows). The H1 level is fitted to four draws on one fixed set of 21 cases, and the H2 level is one draw; neither
is measured on new cases.

**Pooling the 7B finish readings across configurations.** Pooling
the two 7B finish readings across configurations of the same problem (every problem is judged in all seven calls at the
final shape) passed its bars on held public reads (+4 of 71 rows) but shrank on a fresh server read to +2, and to +1 in
the form the call order allows (Skywork answers before Olmo runs), below the +2 bar set before the data; we did not
adopt it (H1) [435-440].

### Addendum of 20 October (draft 28)

*Text moved out of the report in draft 28 (verbatim, from draft 27).*

*From Section 3.1 (the oracle ranges are also in the report's Appendix E.10):*

So we simulated hidden-like sets from the fitted law
(model-based): a reader that knows each case's solve rate averages 7.4 to 11.0 of 14 small cases and 10.7 to 17.0 of 21
main cases; one that also knows how each variant family breaks reaches 11.1 to 13.7 and 16.5 to 20.4 [425, 432]. Our
readings, mostly the stand-in's agreement, exceed the solve-rate oracle in all 96 main scenarios at the H1 level (17.3)
and in 92 at v95's 16 [432].

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.10:*

**Main-track oracle** (Section 3.1; computed, model-based, [432]; `la6_main_oracle.py`): solve-rate oracle 10.7 to 17.0
of 21, solve-rate-and-family oracle 16.5 to 20.4. Our level against both:

| Our level | Above the solve-rate oracle in | Below the family oracle by (mean over 96 scenarios) | Below it in |
|---|---|---|---|
| H1: the recipe's fitted level, about 17.3 of 21 (0.825, Appendix A.2) | 96 of 96 scenarios | about 1.9 cases (range −0.77 to +3.15) | 93 of 96 |
| H2: v95's one draw, 16 of 21 (Section 4.2) | 92 of 96 | about 3.2 cases | 96 of 96 |

At 17.3 the gap is spread evenly over small-model and gpt-oss cases (computed from `la6_main_oracle.out`, the 96
scenario rows). The H1 level is fitted to four draws on one fixed set of 21 cases, and the H2 level is one draw; neither
is measured on new cases.
