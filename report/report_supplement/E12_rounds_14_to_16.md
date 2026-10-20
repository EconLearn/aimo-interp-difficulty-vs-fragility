# Supplement to the technical report: Appendix E.12 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October (draft 28): two related-work sentences moved out of the report in draft 28 are in the addendum of 20
October (draft 28) at the end of this file. Note added 20 October (draft 29): text moved out of the report in draft 29
is in the addendum of 20 October (draft 29) at the end of this file; the report keeps a summary or a pointer.*

### E.12 Rounds 14 to 16: what the organisers' expert edits look like, and five more groups of negative results (Sections 3.4 and 6)

Run on 15 October after the nominees were chosen [442]: a creative research push (frame `work/CRP_FRAME14.md`) with four
lanes working on CPU from public rows, held logs and the organisers' older per-family sample, with bars written before
computing unless marked post hoc; reports in `work/miners14/lane{A,B,C,D}/REPORT.md`. Literature the lanes cite is
unverified unless Section 7 marks it otherwise. Apart from the server reads under "What followed" and in the
kick-and-return row [461, 463, 470], nothing here comes from a server read or the board. The frame asked two questions:
Q1, is there an in-hour measurement of what the single hand-edited text exploits (lane B: no; lane D: derivable, not
measured [445, 446]); Q2, what reading beats chance on gpt-oss low's hard rows (lane A: the rating of Section 6, a bench
result [447]). Rounds 15 and 16 (16 October) then tested two cheap offline versions of the rating, with bars and frozen
scorers set before their data (group 5 of the table at the end) [474, 475, 477-479].

**The organisers' expert edits** (lane B, `b1_taxonomy.py`, [446]). The older per-family sample has one text per problem
and family, shared by all models; strong cell = base accuracy at least 0.7; break = decay of at least 0.25. Edit kinds
are the lane's reading of each visible text; whether an edit keeps the answer was computed (organisers' data):

| Family | Edit (problems) | Keeps the answer? | Strong cells broken |
|---|---|---|---|
| Expert perturbation (EP) | adds a true redundant fact or bound (2 problems, one of them T04) | yes | 1 of 7 (0.14) |
| EP | target swap: the same figure, asks for the square of an area (T25) | no (17,802,399,091 against 751) | 1 of 5 |
| EP | nesting: the problem's own map iterated at a pushed scale (1 problem) | no (18 against 891) | 2 of 6 |
| EP | text not published (T02, T09, T21; no model decayed) | unknown | 0 of 21 |
| Expert no-solution (ENS) | re-numbered to an infeasible case, or an added false, contradictory or unattainable condition, or an unsatisfiable target (7 problems) | no solution | 14 of 39 (0.36) |
| Five LLM-rewrite families | rephrase, rename, typos, distractor, domain (10 texts pooled per cell) | — | 0.06 to 0.12 per family |

The two answer-changing EP texts together break 3 of 11 strong cells (0.27).

**Which family the current single text is** (post hoc, n = 5 [446]). On the five public templates that are AIMO-2
reference problems (T02, T04, T09, T21, T25), "some strong old cell decays by 0.35 or more under the old EP text"
matches "the current template has a non-robust row" on 5 of 5 (4 of 5 at 0.25); the ENS text matches 1 of 5, the LLM
families 1 or 2 of 5. The per-template pattern was seen before the script was written, so this is a description, not a
test. It is consistent with the current single text being the old EP text, but only T25 (the target swap) is a positive
match; on the other four the old EP text broke no strong cell and the current template is robust, so they mainly rule
out the old no-solution text, which broke strong cells by 0.6 to 1.0 on T02, T04, T09 and T21 (`b1_taxonomy.out`) [446].
The fitted current break (about 0.3 [416]) sits nearest the answer-changing EP texts (0.27), which a reader cannot key
without solving the edited problem.

**The no-solution hypothesis, contradicted** [444]. Because the fitted single-text break (about 0.3 [416]) is close to
the old no-solution break (0.36), we asked whether the current single text adds a contradiction, which a reader could
inject and key by construction. Data we already held say no [12]: on templates shared with the old sample, Fibonacci
(T02) had an old mean drop of 0.54 (5 of 7 old models non-robust, driven by its no-solution text) and a current one of
0.00 (all 4 current configurations robust); on "Alice writes" the mean drop went from 0.31 to 0.03; and the
broken-premise control on gpt-oss low showed no signal [100]. Lane D adds two cells: an old no-solution text moved one
old model by 1.0 on T02 (current high 0.01, medium −0.09), and old gpt-oss low by 0.30 on T04 (current low −0.05); on
the old sample, strong models' rewrite-family breaks match noise (3 against 3.14 expected), and their real breaks come
from no-solution texts (12 of 31) and expert edits (3 of 31) [445]. The current labels most likely lack the old
no-solution texts; the organisers' site says the perturbations "leave the deductive chain unchanged" (quoted by lane D
[445]).

**T10: an equivalent mutant** (lane B, `b2_equivalent_mutants.py`, [446]). On our two harsher expert-style T10 texts
(Appendix E.6.1), gpt-oss low's wrong answers are exactly those of one mutant of the correct method, the one that skips
the lower triangle bound: 1,530 in 6 of 8 attempts and 27,744 in 5 of 8. Wherever that mutant gives the right answer,
low is right 47 of 56 times (original 21 of 24, a same-numbers quantity text 6 of 8, four random program siblings 20 of
24). At the original numbers the mutant is equivalent (850 = 850), so no reading of the original's answers can tell the
model from it. Medium shares the slip (1,530 in 3 of 8, 27,744 in 4 of 8) yet is officially robust on T10 (drop 0.10):
our breaking instances are harsher than the organisers' text, as in [318]. In the terms of Section 6 the bound is a
dormant condition; T10's mean rating is 1.8, called non-robust. Lane B's taxonomy of the organisers' expert edits and
the rating describe the same failure from two sides: on an answer-changing edit, a weaker solver re-applies a step that
no longer applies [448].

**Exposure audit** (Section 3.4; lane B, `b3_exposure.py`, [446]). Provenance from MathArena matches: exposed = AIMO-2
reference problems (T02, T04, T09, T21, T25) and AIME 2025 (T06, T07, T08, T19, T22, T27); fresh = AIME 2026 (T03, T05,
T10, T11, T13, T15, T16, T17, T18, T20, T23, T26); T01, T12, T14, T24 and T28 are unmatched and left out. Model release
dates are public knowledge, not re-checked (Qwen3.5-4B's may fall days after AIME 2026 I; it is treated as fresh). Bars:
D = non-robust share of exposed rows minus that of fresh rows, against provenance permuted over templates (20,000
draws); "supports the memorised-path premise" iff D ≥ +0.15 with p ≤ 0.10, "opposite" iff D ≤ −0.15 with p ≤ 0.10. Hard
rows: D −0.50 (p 0.048), opposite; all labelled rows: 3 of 35 against 11 of 24, D −0.37 (p 0.018). Descriptively, fresh
rows are non-robust more often in each of the six configurations that have both kinds of row. The lane disclosed that it
guessed the direction while reading the templates, before the script ran.

**The dormant-condition rating in detail** (lane A, `work/miners14/laneA/`; ratings `a6_analyst_ratings.json`,
`a6r_analyst2_ratings.json`, `blind3/rater3.json` to `rater5.json`; `blind_problems.json` is exactly what the raters
saw). Lane A's first five tests (A1 to A5, below) failed or were bounds; A6, the rating, was added before the first
rater's output existed, as a transfer from software testing (condition coverage) and reliability (dormant failure
modes). Each rater also scored COINC (how much the derivation rests on a numerical coincidence) and PLACEBO (amount of
non-mathematical story wording, the sabotage scale).

- **Disclosure: the rubric was written with the labels seen.** `PREREG_laneA.txt` line 2 records that lane A's analyst
  had seen "the 71 public labels and max_drops" before writing; line 46 adds that the analyst had read about 12 of the
  28 texts. The A6 rubric (LATENT, COINC, PLACEBO) was written by that analyst; the five raters who applied it saw only
  the problems and answers (`blind_problems.json`). So the raters were blind and the rubric was not; whether its target
  was shaped by what was known about non-robust templates such as T10 [318] cannot be told from our files. The split by
  configuration (small models + low) was found post hoc on raters 1 and 2 [449]; raters 3 to 5 re-measured it on the
  same 41 rows, which replicates the measurement, not the selection [453]. The frozen scorer and thresholds [451, 452]
  still count.
- **Raters 1 and 2** (each alone, call at LATENT ≥ 2) [447]: gpt-oss low 7 of 7 each (the entry 6 of 7; chance of 7 of 7
  under template rotation about 0.01 per rater); agreement Spearman 0.661 (75% exact, 96% within one); Spearman with the
  stand-in's reading +0.08 and +0.07; hard-row AUC 0.646 and 0.570; all 71 rows 0.735 and 0.729; PLACEBO hard-row AUC
  0.310 for both. Rater 1 only: hard-row AUC of the residual on the stand-in's reading 0.750; added to the entry's
  margin by a leave-one-template-out logistic, −3 rows (bar +2). Pre-set verdicts: A6 failed, not killed; its
  replication A6r passed R1, R2 and R4 and failed R3 (`a6_score.out`, `a10_replication.out`).
- **Policies with two raters** [449]: low only 62 of 71 for each rater; Qwen + DeepSeek + low 62 and 60; all small
  models + low 64 and 61. We first read the larger gain as rater-1 noise and pre-registered the low-only rule.
- **Five raters** [451-453, 457]. Mean LATENT by template (computed, `score_five_raters.py`): T01 1.2, T02 1.2, T03 1.6,
  T04 0.0, T05 1.2, T06 0.8, T07 0.4, T08 0.0, T09 1.6, T10 1.8, T11 2.0, T12 2.0, T13 1.6, T14 2.4, T15 1.0, T16 1.4,
  T17 1.0, T18 0.8, T19 1.2, T20 1.0, T21 1.8, T22 0.2, T23 0.2, T24 0.8, T25 1.2, T26 2.2, T27 1.8, T28 0.2. Bars [451]
  and results [453]: M1 (low 7 of 7 and low hard 4 of 4) failed, 6 of 7 and 3 of 4 (T09 1.6); M2 (small models + low ≥
  36 of 41) passed, 37; M3 (the rating on those 41 rows, the entry elsewhere: ≥ 63 of 71 and fresh rows ≥ 20 of 24)
  passed, 64 and 21; M4 (raters 3 to 5 against the mean of raters 1 and 2, Spearman ≥ 0.5) passed, 0.661; PLACEBO
  sabotage (≤ 30 of 41) passed, 25. The low-only rule is undermined too: three of five raters rate T09 at 2 [453].
- **What failed, in full.** Lane A's pre-set bar, hard-row AUC ≥ 0.70: rater 1 0.646 [447], the five-rater mean also
  0.646 [457]; the replication's R3 (rater 2, 0.570) [447]; and the five-rater M1 (low 7 of 7): 6 of 7, as three raters
  rate T09, a robust low row, at 2 [453]. By its pre-set rule the test did not pass.
- **The 7B cases only** [455]: Skywork and Olmo decided by the rating alone, 12 of 12 rows (the entry 9 of 12), all 71
  rows 64, fresh rows 21 of 24; combined with the own runs by OR, 62 and 20, by AND, 63 and 20. Thin: 12 rows on 10
  templates, and it would replace the readings behind our main-board gain (Section 4.1). Baseline: the stand-in's
  decision alone scores about 11 of these 12 rows (Olmo 9 of 9, lane C's `REPORT.md`; Skywork 2 of 3, Appendix E.11) and
  64 of 71 in the same dress (in-sample; `a1_vectors.out`).
- **What followed** [450, 453-456, 461, 462, 470, 472-479]. A server read with gpt-oss medium as the rater (v90; K 4,
  cap 8,000), with bars set before any gpt-oss rating: parsing (S1), Spearman with the five-rater mean ≥ 0.50 (S2'), and
  the small-models + low policy with gpt-oss's median ≥ 63 of 71 with fresh rows ≥ 20 of 24 (S4'); for the candidate
  also ≥ 11 of 12 Skywork and Olmo rows [455]. S1 passed (27 templates parsed); S2' failed (0.472) and S4' failed (48 of
  71 against the entry's 61; fresh 15 of 24): gpt-oss's median rating was 2 on 18 of 27 templates [461]. The same read's
  high-effort arm (K 2, cap 8,000) parsed only 20 of 28 templates, ranked them better (Spearman 0.637) with the same
  inflation, and gave a policy of 46 of 71; as information, the medium mean rating's AUC on the 40 weak and low rows was
  0.729 [461] and v94's on the 41 such rows 0.826 [470] (five raters: 0.935). A second read with five calibration
  anchors at high effort (v94; S2' raised to ≥ 0.60 before its data [462]) gave 0.49 on the non-anchor templates and 55
  of 71, a failure [470]. Candidates v91 (main) and v92 (small), built from v83 without the 7B own runs, rate problems
  after the stand-in reading; their mock was clean (0 invalid, longest 3,200 s; at final main shape 28 to 30 of 30
  problems rated at measured speed, 13 to 17 at 1.4x slower) [456], but by the pre-set plan neither was uploaded [455,
  461]; under the per-case harness a rating would cost about 300 to 700 s per case against about 190 s available on main
  [470]. A cheaper in-hour read (v97: gpt-oss low and medium, structured prompt with and without the anchors, four arms,
  about 1,200 s inside case 1; bars include S2' ≥ 0.60 and a 7B-only policy ≥ 11 of 12) was pre-registered and uploaded
  on 16 October; all four arms failed (Appendix E.14) [472, 473, 478, 491]. Two offline routes to a cheap rater then
  failed their pre-set bars (group 5 of the table below): a text-only distilled rater [474, 475, 477] and in-hour
  observables of the models' own attempts [478, 479]. The distillation pool is 325 public olympiad problems with answers
  (none of our 28 templates), each rated by two blinded Claude raters with the A6 rubric; the raters agree well
  (Spearman 0.713, exact 0.658, within one 0.975), so the target is consistent [474, 477].
- **Caveats and per-configuration results.** Medium rows are at chance (0.55); high's 0.788 rests on 2 non-robust rows
  [457]. Rows cluster by template (effective sample about 15 templates) [457]; the gain is all on the 7B cases (Skywork
  T13, T16; Olmo T08), whose own runs carry our board gain [453, 455]; and the raters are a strong model (lane A's
  report: about 14 minutes and 150,000 tokens per rater), unlike anything inside the hour.
- **Other notes.** Another team's public self-labelled generations cannot validate the rating, since their families are
  renames, typos and distractors, not new numbers [457]. The raters were shown 35 for T28 (gpt-oss's pooled modal
  answer) and each who checked found 42 [453] (and lane A's report); raters 3 and 5 noted that T19 is a re-numbered AIME
  2025 problem whose parallel-lines shortcut no longer holds [453].

**Five more groups of negative results, 19 results in all** (groups 1 to 4 from round 14, group 5 from rounds 15 and 16;
bars set before computing unless marked post hoc; computed on public rows, held logs and, for group 5, a rated pool of
other public problems; single computations):

| Group (lane) | Reading or premise | Bar | Measured | Verdict |
|---|---|---|---|---|
| 1. Affordable small-model own runs (C) | Olmo K 3 against K 1 on Olmo's 9 own rows | expected gain ≥ +0.5 row, bootstrap interval excluding 0, above the 95th percentile of 36 relabellings | +0.00 row on held reads, +0.01 with dress inferences [443] | failed: K 3 = K 1 |
| | Qwen3.5-4B thinking own run (robust iff ≥ 1 of K ends inside a cap chosen leave-one-template-out) | more own rows right than the entry | leave-one-template-out on a MathArena proxy 0.25 of 4 expected rows (K 1) against 3 of 4; our own run at 17,761 tokens 7 of 12 against 11 of 12; as a reader of the 8 hard small-model rows, AUC 0.29 (inverted) [443] | failed |
| | DeepSeek own run | more of its 6 rows right than the entry | 4 of 6 against 5 of 6 at 16,000 tokens; at 32,000 a length proxy predicts a loss at every cap from 20,000 to 64,000 (proxy, not measured) [443] | failed; a 32,000-token server read kept in reserve |
| | Engineering at the final shape | none (arithmetic on logged step times) | 7B fast paths at the KV-bandwidth floor (ms per row per step: Olmo 1.06 against 1.13, Skywork 0.14 against 0.15); Olmo's sliding-window cache already honoured; a fixed ~24 ms per step (weights ~8 ms) is the one large lever, CUDA graphs an estimated −435 s at the final shape; KV quantisation, paged KV, speculative decoding and two models per GPU closed [443] | build only if a measurement needs the time |
| 2. gpt-oss high and transfer fields (D) | an in-hour reading separating high's non-robust T25 / T26 from robust T22 / T23 | — | none found; the stand-in certifies robust (0 of 12 certified medium and high rows non-robust); uncertified high rows non-robust 2 of 9 [445] | keep the public prior |
| | anchor linking (psychometrics, common-item equating; post hoc) | — | 11 of 11 against always-robust 10 of 11, p 0.20; n = 5 cannot pass [445] | failed |
| | low-to-medium attractor persistence (ecology; post hoc) | AUC above the 95th percentile of template rotations | 0.583 against 0.667 [445] | killed |
| | kick-and-return: continuations resampled from 15% into a trace return to its answer less often when the failure is decided while reading the problem (ecology, structural reliability) | the scorer passes a planted effect in ≥ 14 of 20 synthetic replicates | 0.40 (null 0.00, confound 0.02) [445] | the scorer failed its own power bar; the server read (v89) then failed its bar: AUC 0.667 against 0.75, below plain modal share (0.730) [450, 463]; closed |
| 3. gpt-oss low's other readings (A) | weaker readers predict better [118], on the current labels | mean weak-reader AUC on 23 gpt-oss hard rows ≥ low's own + 0.05 | 0.686 against 0.837 [447] | premise rejected |
| | low's own solve rate (a bound) | hard rows separated by ≥ 0.05 with bootstrap P ≥ 0.90 | +0.050, P 0.857; ordering low's 4 hard rows right has probability 0.73 at K 64, 0.86 at K 128, 0.95 at K 256 [447] | fails narrowly; needs K ≥ 128, far above the entry's median of 16 for low cases [404] |
| | ICC flatness across 9 readers (psychometrics) | hard AUC ≥ 0.65 and ≥ +2 rows added to the entry's margin | hard AUC 0.835 but +0 rows, and reversed on low rows (0.200) (`a1_vectors.out`) | failed, not killed |
| | case-set answer ("how many", "sum of all", ...) | hard balanced accuracy ≥ 0.60 | 0.538 (`a1_vectors.out`) | killed |
| | the older per-family sample as a bench for low | labels agree on 2 of 2 shared rows | 0 of 2 [447] | not usable |
| 4. Edit-side readings (B; [444]) | the current single text is an added contradiction, keyable by construction | none (checked against held data) | contradicted by [12] (above) [444] | not pursued |
| | lossy final map (answers reduced mod m, m + n, prime-factor count) | hard AUC above the shuffle 95th percentile (0.727) | 0.430 [446] | killed |
| | boundary-pushed siblings kill the T10 mutant | ≥ 3x the random rate (kill below 1.5x) | 1.77x (0.207 against 0.117) [446] | unclear |
| | differential-program read (medium writes a brute-force and an analytic program; low reads instances where they disagree) | instrument and result bars written, not run | prior 5 to 10%; medium shares the T10 slip, so its specificity bar likely fails [446] | not built |
| 5. A cheap dormant-condition rater (rounds 15 and 16) | text-only distilled rater: word and character tf-idf plus handcrafted counts, ridge regression fitted on the 325-problem pool rated by two blinded raters each, applied to the 28 public templates (scorer frozen before any pool rating, `miners15/distill/text_rater.py`, md5 65a7a7d5...) | T1 Spearman with the five-rater mean ≥ 0.60; T2 7B-only policy ≥ 11 of 12, ≥ 63 of 71 and fresh ≥ 20 of 24; T3 shuffled-label sabotage ≤ 0.30 | ridge strength at the top of its grid (the text carries almost no signal); predictions 1.04 to 1.41; T1 0.279; T2 9 of 12, 61 of 71, fresh 18 of 24 (the entry 9 of 12, 61, 19 of 24); T3 0.013 [474, 475, 477] | failed: surface text does not carry the rating |
| | in-hour observables of the models' own attempts (finish rate, length, agreement, distinct answers, entropy, modal share, answer size) on 142 pool problems matched to another team's public generations (Qwen3.5-4B, Skywork, DeepSeek; 8 attempts at 8,192 tokens) | a lead needs a difficulty-controlled partial Spearman of at least 0.30 in size with permutation p ≤ 0.01; the ridge combination, 5-fold Spearman ≥ 0.45 (`miners16/laneS/PREREG_laneS.txt`) | the rating tracks difficulty somewhat (Spearman with solve rate −0.31); best partial −0.18 (DeepSeek finish rate, p 0.03); ridge +0.21 (solve rate alone +0.25), difficulty-controlled −0.11; Qwen and DeepSeek hit the cap on 95 to 97% of attempts [478, 479] | failed: own-attempt behaviour does not see the dormant condition; no server read proposed |

### Addendum of 20 October (draft 28)

*Text moved out of the report in draft 28 (verbatim, from draft 27).*

*From Section 7 (anchor linking: the report's Appendix E.12, groups 1 to 5):*

**Psychometrics.** Anchor linking follows test equating (Kolen and Brennan, *Test Equating, Scaling, and Linking*,
Springer, 2014; *record*).

*From Section 7:*

predictive mutation testing (Zhang et al., ISSTA 2016; *read* by that lane) motivated reading mutants without running
every test.

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.12:*

Mean LATENT by template: T01 1.2, T02 1.2, T03 1.6, T04 0.0,
  T05 1.2, T06 0.8, T07 0.4, T08 0.0, T09 1.6, T10 1.8, T11 2.0, T12 2.0, T13 1.6, T14 2.4, T15 1.0, T16 1.4, T17 1.0,
  T18 0.8, T19 1.2, T20 1.0, T21 1.8, T22 0.2, T23 0.2, T24 0.8, T25 1.2, T26 2.2, T27 1.8, T28 0.2.

*From Section 6.2:*

On our two harsher expert-style T10 texts, gpt-oss low's wrong answers are exactly those of one mutant of the correct
method, the one that skips the lower triangle bound: 1,530 in 6 of 8 attempts and 27,744 in 5 of 8. Wherever that
mutant gives the right answer, low is right 47 of 56 times. At the original numbers the mutant is equivalent (850 =
850), so no reading of the original's answers can tell the model from it [446]. The bound is a dormant condition (T10's
mean rating 1.8). For benchmark builders: an answer key at the given numbers cannot separate a method from its
equivalent mutant; only instances where the dormant condition binds can. gpt-oss medium shares the slip yet is
officially robust on T10 (drop 0.10), so our instances are harsher than the organisers' text [318, 446].

*From Section 2.4:*

Fresh problems are also non-robust more often: on
hard rows, AIME-2026 problems are non-robust 11 of 15 times, problems published before the judged models 3 of 13
(one-sided p 0.048, two-sided 0.10; direction guessed while reading) [446].
