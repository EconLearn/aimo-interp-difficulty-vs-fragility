# Difficulty is not fragility: an audited robustness predictor and 88 negative results

Jude Wallis (Independent researcher)

*Technical report, AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180), 22 October 2026 (UTC); four-page
version (draft 33). The full report (draft 29, revised 22 October; `report/REPORT_full.pdf` in the repository) is the
supplementary material: "Supplement X" refers to its section or appendix X. Hidden cases appear as counts only.
Appendix A gives the source of every number (ledger entries and scripts) and defines the number labels.*

## Abstract

We predict, inside a fixed GPU budget, whether a configuration's accuracy on a math problem survives the organisers'
perturbations, and find that difficulty is not fragility. On the 63 labelled public rows matching the text we read (all
71 in brackets), a stronger model's answer agreement ranks rows at within-configuration AUC 0.914 [0.929], mostly
because 30 of 31 easy-template rows are robust; on hard templates it is 0.821 [0.875], and 2.5 times more attempts or a
perfect answer key raise it to at most 0.897. What it misses is mostly fragility of the problem itself: 15 of 16
problems labelled for several configurations carry one label. No in-budget reading of that from the original passed all
its pre-set bars: of 88 negative results, 70 failed and 2 were unclear. Leave-one-template-out our entry gets 55 of 63
[60 of 71] public and 17 of 22 [18 of 24] fresh rows, a selection null cannot tell its board-chosen layer's gain from
coin flips, and a 21-case validation board total varies by about 1.3 cases across server states.

## 1. Introduction

The AIMO Interpretability Challenge (Štefánik et al., 2026) asks, for each *case*, a (problem, configuration) pair,
whether the configuration's accuracy survives perturbation of the problem. The configurations are Qwen3.5-4B,
Skywork-OR1-Math-7B, Olmo-3-7B-Think and DeepSeek-R1-0528-Qwen3-8B (the small track), and gpt-oss-120b at low, medium
and high effort. A case is robust iff the largest accuracy drop over the organisers' families of perturbed texts is at
most 0.10, non-robust iff at least 0.25, and exists only if the configuration solves the original robustly [2]. An entry
sees only the original text, runs each case in its own process on one GPU [178, 464] and faces 30 to 50 new problems in
the final at about 170 s each [513, 537].

We find that **difficulty is not fragility**: a stronger model's reading of difficulty carries most of the public
ranking, but what it misses on hard problems is mostly fragility of the problem itself, and no in-budget reading of that
from the original passed all its pre-set bars (Sections 3 and 6). Edited or re-instantiated problems are known to cut
accuracy (Mirzadeh et al., 2025; Huang et al., 2025a; Mondorf et al., 2026); whether probes and interpretations predict
unseen behaviour is asked by Belinkov (2022), Li et al. (2025) and Huang et al. (2025b). We ask it of a whole entry,
with a selection null from adaptive data analysis (Dwork et al., 2015; Blum and Hardt, 2015; Roelofs et al., 2019).

## 2. Data and the entry

**Data.** 82 public rows over 28 templates, 71 labelled (52 robust) [3, 278, 382, 618]; *fresh rows* are the 24 labelled
rows on 12 AIME-2026 templates [446, 509]; 9 of 12 Skywork rows added on 15 October are labelled [617]. **8 of the 71
labelled rows (9 of 80) carry other numbers than the text all our readings used** [661, 664]; we report the 63 *matched*
rows, with all rows in square brackets. The validation boards hold 21 main cases (10 robust) [99] and 14 small cases (7
robust) [270]. As the site invites, we iterated on them with public-row-motivated method variants, never constant
answers per configuration or per-case probes, though early ones tested guesses about the hidden sets' structure
(Supplement E.6.2) [266, 282, 290]. Board counts per configuration carry hidden-label information [329b], which we used
while choosing three routes (Supplement A.2); Section 4 audits that use.

**The entry reads behaviour only.** *Stand-in* (Qwen, DeepSeek, gpt-oss low and medium cases): gpt-oss-120b at low
effort makes 4 to 32 attempts. Their *agreement* (the chance that two random attempts both end on their own with the
same answer), a *quick finish* (whether any of 4 non-thinking Qwen3.5-4B attempts ends within 2,000 tokens) and an
effort code enter a logistic rule with 10 coefficients (`decision.json`; Supplement F.4) [272b]. *Own runs* (Skywork,
Olmo): robust iff at least 1 (Skywork) or 2 (Olmo) of 3 attempts of the judged model end on their own inside a 9,000- or
10,000-token cap [269, 339]. *Prior* (gpt-oss high): robust, as 13 of 15 public rows are [336]. *The entry* is v95
(main) and v96 (small), rebuilt for the final as v111 and v112 [540]; this paper's evaluated entries are their
per-case-safe variants v115 and v116 (Codabench 1003729, 1003727; Section 7) [575, 576], which cut Olmo's cap to 7,200
tokens [573] (Appendix A).

## 3. Difficulty is not fragility

**Two meanings of difficulty.** The judged model's solve rate carries almost none of the label: in our fit of the label
recipe the chance of a non-robust label is flat, 0.18 to 0.21, for solve rates from 0.5 to 1.0 (computed) [416]; on T13
every small model solves the problem yet is labelled non-robust [197, 266]. Difficulty read by a stronger model carries
far more: the stand-in's agreement at K 32 ranks matched rows at within-configuration AUC 0.914 [0.929] [611].

**That reading saturates on hard templates** (Figure 1; computed, post hoc, one server read [440]). Its AUC comes mostly
from the 10 easy templates, where 30 of 31 rows are robust. On the 17 *hard* templates, which a 2,000-token reader never
finishes (32 rows, 13 non-robust) [267b, 278], it is 0.821 [0.875]: 7 of 39 [7 of 56] same-configuration pairs are
misordered (four on gpt-oss high, two on low, one on Skywork). 80 pooled attempts give 0.897 [0.929] and their accuracy
against the answer key 0.872 [0.911], inside the 0.821 to 0.936 of single held reads; leave-one-template-out (LOTO), the
key fixes 1 of 32 hard rows [2 of 37] [611].

**What it misses is mostly the problem's own fragility** (computed, post hoc) [664]. By exact problem text (all 80
labelled rows), 15 of the 16 problems labelled for several configurations carry one label, and 4 of the 5 with a
non-robust label are non-robust for every configuration (T10 is the exception). An oracle calling a row non-robust when
the other configurations' mean drop on the same text is at least 0.175 would fix 6.4 of our calls per read and break 0.4
(matched rows, 8 reads). These are few problems; the oracle uses labels.

![Figure 1: agreement by label on easy and hard templates](agreement_by_label_v32.png)

*Figure 1. The stand-in's agreement on each labelled public row, by label, on easy and hard templates. Hollow: rows
labelled on other numbers. Diamonds: T13. Script `report/figures/make_agreement_by_label_v32.py`.*

**What fragility can look like.** On two harsher expert-style rewrites of T10, gpt-oss low's wrong answers are exactly
those of the correct method without one check, a lower triangle bound; at the original numbers the check removes nothing
(both give 850), so the original cannot show the slip (an equivalent mutant; Papadakis et al., 2015) [446]. gpt-oss
medium makes the same slip yet is labelled robust, so our rewrites are harsher than the organisers' [318].

## 4. A generalisation audit

**What was fitted, and when.** The only label-fitted part, `decision.json`, was fitted on the 71 public rows on 5
October [113], after board uploads began (2 October) [20] but before the board-tested changes of 5 to 11 October; a LOTO
refit changes 1 of 71 answers [509], and a refit without the 8 mismatched rows changes no call on the Figure 1 read (0
or 1 on seven others; computed). Three choices of 10 to 11 October (the high prior, both own runs) decide 8 of 21 main
and 6 of 14 small cases; about ten hand-set values (caps, K, thresholds) cannot be cross-validated. Table 1 gives
out-of-sample accuracy.

*Table 1. The entry's rules on public rows (one server read), LOTO with `decision.json` refitted per held-out template;
template-bootstrap 95% intervals; boards predicted from matched rows (model-based) and observed (OFFICIAL, one draw
each) [471, 560, 564, 664].*

| Rows | Matched rows | All rows | Predicted board (90% range) | Board |
|---|---|---|---|---|
| All labelled [509] | 55/63 = 0.873 (0.78 to 0.94) | 60/71 = 0.845 | main 17.0 (13 to 20) | 16 (v95), 17 (v111) |
| Fresh AIME-2026 [509] | 17/22 = 0.773 (0.64 to 0.90) | 18/24 = 0.750 | main 16.0 (11 to 20) | 16, 17 |
| Small-model rows, board class mix [509] | 0.872 | 0.817 | small 12.2 (10 to 14) | 10 (v96), 9 (v112) |
| 80 rows, 8 reads, pre-registered [618] | 62.5/71 = 0.880 (60 to 64 per read; balanced 0.817; always-robust 0.789) | 68.75/80 = 0.859 | — | — |

**The board-chosen layer against a selection null.** Keeping a change only when the board rises gains +3.9 in
expectation (90% range 1 to 8) if every changed answer is a coin flip and +7.3 (3 to 12) if each is right 70% of the
time (model-based). The three routes kept +3, inferred from board counts (Supplement A.2) [509], inside both ranges: the
test cannot separate them, and **the board-chosen layer adds no demonstrable accuracy**.

**A frozen prediction.** We expect v111 to get **about 16 of 21 main cases right on new problems** (90% range 11 to 20),
not our best draw's 19 [393, 509]. Guess ranges for final accuracy, frozen on 17 October [543] (assumptions, hash and
their rule for the evaluated v115 and v116: Appendix A), are 0.72 to 0.82 for v111 and 0.62 to 0.76 for v112;
Section 5's noise alone would put the final inside them only about 40 to 50% (v111) and 55 to 70% (v112) of the time
(computed).

## 5. How much a board score moves

From our own logs, without hidden labels (computed) [585]: a reading repeats exactly within one server state (23 of 23
same-problem groups), but across states a stand-in call flips with probability about 0.26 (90% interval 0.14 to 0.45).
One board total thus varies by about 1.3 cases on main and 1.0 on small. **A 21-case board cannot order entries whose
readings resample and that differ by two cases or fewer**: 17 against 15 arises with probability 0.41 with no real
difference. On 30 to 50 new problems, reading noise and problem sampling give about 0.07 to 0.09 accuracy per run.

## 6. Negative results

Of 88 negative results from work to 20 October (Supplement D), **70 failed a bar written before their data** in our
dated, author-controlled ledger (no external timestamp), 2 were unclear, 13 had no bar or a post hoc one, and 3 were not
built or run. In Table 2, a probe of the judged model's difficulty adds nothing over agreement, and no fragility reading
passed all its bars.

*Table 2. Six informative readings (server: contest server; local proxy: 4-bit weights on a Mac). Ledger by row: [652],
[499, 506, 516, 555], [447, 457, 461, 470, 477, 479, 491, 664], [521, 523, 528], [619], [302, 309].*

| Reading | Measures | Bar, set first | Result | Verdict |
|---|---|---|---|---|
| Qwen3.5-4B prompt-state probe of Qwen's solve rate (local proxy; 80 rows) | difficulty (internal state) | Spearman ≥ 0.40; at most 0.5 rows lost; ablation gain ≥ 2 rows | Spearman 0.803; each use loses 0.25 to 3.25 rows; a perfect probe (post hoc) 1.5 to 5.5 | failed |
| Probes for the rating below: Qwen3.5-4B states on text, solution, thinking (local proxy); gpt-oss-120b (server) | internal state | Spearman ≥ 0.60, 28 templates | 0.277, 0.454, 0.304; 0.030 | failed |
| Five blinded Claude raters: would new numbers make a dormant condition bind? Five in-hour versions | fragility | AUC ≥ 0.70, 37 hard rows; one bar per version | 0.646; 32 matched rows (post hoc): 0.674, five-rater mean 0.711; none of five passed | failed |
| STD: own steps against own brute force on new numbers; three blind writers | fragility | 11 of 12 7B rows; AUC ≥ 0.80; Spearman ≥ 0.40 | 9, 11, 10 of 12; AUC 0.724, 0.900, 0.789; writer 3 passes on matched rows (post hoc) | each failed a bar |
| Premise reliance; instance-binding depth (local proxy) | fragility | Spearman with the rating ≤ −0.30; sabotage loses | +0.150 (11 of 34 problems defined); −0.038 (27); sabotage did not lose | failed |
| Answer-keeping organiser-style rewrites, gpt-oss low (server, 7 rows) | fragility | drop ≥ 0.20 on non-robust rows | +0.03, +0.10; AUC 0.30 | unclear (0.10 is the boundary) |

*At these sizes 80% power needs a true Spearman of about 0.51 (28 templates) or an AUC of about 0.77 (19 against 18
rows) (Supplement D): "failed" means not shown, not absent.*

**The prompt-state probe** reads difficulty, and even Qwen's measured solve rate in its place loses rows [652]: **we
make no White-Box claim**. **STD** programs a Claude agent wrote after reading the raters' notes scored 12 of 12 7B
rows, blind ones 9 to 11 [482, 489]: **a reading computed through a solver's own steps needs a blind replication.**

## 7. Efficiency under a 170 s per-case budget

Our decode paths share K/V reads across a KV head's query heads and write K and V in place [360, 186]; in
pre-registered server benches a decode run takes 0.42x (Skywork) and 0.48x (Olmo) of the default wall time [365]. v115
and v116 answered every board case in at most 148 s, under the final's 170 s [575, 576].

## 8. Limitations and lessons

**Limitations.** Reading noise rests on 3 server states [585]; fresh rows were seen while hand-set values were chosen;
the own runs rest on thin, post hoc support (3 Skywork and 9 Olmo rows when chosen) [339, 387]; a Claude agent wrote the
rating rubric after seeing the labels [447, 480]; raters and blind writers are Claude subagents; the final is mocked,
not run [538]. **Lessons.** Check that each labelled row's text is the text you read; split a reading's score by where
the label varies; refit label-fitted parts LOTO and compare board gains with a selection null (`audit.py`); set bars
above read-to-read noise.

## AI Use Statement

**Generative AI was used for most of this work.** We used Anthropic's Claude through Claude Code, a tool in which Claude
writes and runs code, reads and edits files and starts further Claude instances (subagents). The Claude models used were Claude Opus 5.5, Claude Opus 5 and Claude Fable 5.1. Claude was used for:

- **ideation**: research directions, hypotheses and the design of each pre-registered test (bars, controls, outcome
  branches);
- **coding**: the entries, decode paths, mocks, fault injection, the analysis and audit scripts, the release folders and
  the figure scripts; Claude also created and updated the public GitHub repository under the author's account, with the
  author's permission [632, 634];
- **research data**: Claude agents wrote the perturbed problem texts (1,976 texts) [302], the LATENT rating rubric
  [447, 480] and the solution programs of Section 6 [482];
- **experiments and analysis**: local runs, the statistics and the research ledger; Claude also operated the
  competition site in the author's logged-in browser session, to read server logs and, from 5 October, to upload
  entries and research runs, among them v95 and v96 [469] and the evaluated v115 and v116 [574], under permissions the
  author gave in chat (at first for one night [125], later for a session or a named file [239, 503], and standing from
  18 October [556, 601]). One upload went up under a standing go-ahead before the author had answered a question about
  it [288], and one file was uploaded twice by mistake [295];
- **literature**: search and reading (statuses in the References);
- **writing**: this report, its supplement and its consistency checks; Claude instances also reviewed drafts and code.

Claude instances were also the five blinded raters and the three blind program writers of Section 6 (a limitation;
Section 8). No Claude model runs inside the entries, which use only the open models of Section 1.

**Tasks done without generative AI.** The author set the goals and limits of the work; gave the permissions for uploads and compute in chat, mostly as standing permissions; provided the competition, GitHub and other accounts; sent this project's messages to the organisers (Claude drafted some and sent none); made the final decisions, including which entries are evaluated with this paper (Claude recommended them); and submits this report.

**Review and responsibility.** The author reviewed all AI-assisted work and takes full responsibility for the final content of this paper, including AI-assisted text, claims, code and other artefacts.

## References

Status: *read* (we read the paper), *abstract* (abstract page only), *listed* (details from the organisers' proposal's
bibliography; we did not open the work), *record* (authors and venue checked in the publisher's record; abstract not
seen).

- Belinkov (2022). Probing classifiers: promises, shortcomings, and advances. Computational Linguistics 48(1). *Listed*.
- Blum and Hardt (2015). The Ladder: a reliable leaderboard for machine learning competitions. ICML 2015. *Abstract*.
- Dwork et al. (2015). The reusable holdout: preserving validity in adaptive data analysis. Science. *Abstract*.
- Huang et al. (2025a). MATH-Perturb: benchmarking LLMs' math reasoning abilities against hard perturbations. ICML 2025;
  arXiv 2502.06453. *Abstract*.
- Huang, Tao, Icard, Yang and Potts (2025b). Internal causal mechanisms robustly predict language model
  out-of-distribution behaviors. ICML 2025. *Listed*.
- Li, Kaufmann, Wattenberg, Alvarez-Melis and Saphra (2025). Can interpretation predict behavior on unseen data? arXiv
  2507.06445. *Listed*.
- Mirzadeh et al. (2025). GSM-Symbolic: understanding the limitations of mathematical reasoning in large language
  models. ICLR 2025. *Listed*.
- Mondorf, Bell, Dodge and Hupkes (2026). LPDS: evaluating LLM robustness through logic-preserving difficulty scaling.
  arXiv 2605.15393. *Read*.
- Papadakis et al. (2015). Trivial compiler equivalence: a large scale empirical study of a simple, fast and effective
  equivalent mutant detection technique. ICSE 2015. *Record*.
- Roelofs et al. (2019). A meta-analysis of overfitting in machine learning. NeurIPS 2019. *Abstract*.
- Štefánik, Mondorf, Waldis et al. (2026). AIMO Interpretability Challenge (the organisers' proposal). arXiv 2607.13899.
  *Read*.

## Appendix A. Supplementary material and reproducibility details

**Reproducibility.** v111, v112, v115, v116, v121 and v122 rebuild byte for byte from the repository's root folder (v115
/ v116 and v121 / v122 from its folders `v115_v116/` and `v121_v122/`; md5s below; every command in its README) [549,
589, 627]. **Training data**: `training/build_calib.py` rebuilds `calib.json` from the organisers' public parquet
(Hugging Face `aimo-interp/train-main-v2`, revision `23791d9b`), and `training/refit_low16.py` refits `decision.json`
from it and our four public-template server logs (`training/runs/`). **Board scores**: each zip runs unchanged in the
organisers' per-case harness; a rerun in another server state varies by about 1.3 cases on main and 1.0 on small
(Section 5) [585]. **Licence**: code under the MIT License; report text under CC BY 4.0. **Repository**:
https://github.com/EconLearn/aimo-interp-difficulty-vs-fragility.

**Matched rows.** A labelled row is matched when its own problem text is the template text all our readings used;
`calib.json` flags this per row (`own_text`, from `build_calib.py`), and a hash of the texts in the organisers' file
gives the same 8 of 71 and 9 of 80 unmatched rows [661, 664]. Figure 1's script and
`report/figures/recompute_matched_v32.py` compute
every matched-row number from the same held logs.

**Evaluated entries.** The entries evaluated with this paper are Codabench 1003729 (v115, main) and 1003727 (v116,
small) [574]; by the rule fixed before any final result [568], the frozen ranges apply to them if they alone are scored.
Their 7,200-token Olmo cap costs about 0.6 to 0.9 main and 1.3 to 2.1 small cases per 40 new problems against v111 and
v112 (model-based) [654]. These ids may still change after the organisers' answers (v111 and v112 if 170 s is an
average) or a pending server timing test of an Olmo variant [657, 663]. The other rows are listed for reproducibility
(md5 of each zip; board OFFICIAL, one draw each, with its Codabench submission id):

| Role | File | md5 | Board |
|---|---|---|---|
| The entry rebuilt for the final, main; small | `aimo_v111_main.zip`; `aimo_v112_small.zip` | 9686c9cec06ec4dc40f9b728f7ef17db; 8b404890d71bc5483ccce18f88887636 [540] | 17 of 21 (1000991); 9 of 14 (1000212) [560, 564] |
| Per-case-safe variants (own runs stop at 160 s; Olmo cap 7,200 tokens) | `aimo_v115_main.zip`; `aimo_v116_small.zip` | ad191e2e2262b0a918ec1aaf83bcf9c7; d3ada3a4b8ff05b5876582246008bbf9 [573] | 15 of 21 (1003729); 9 of 14 (1003727) [575, 576] |
| The same with every reading's seed shifted | `aimo_v121_main.zip`; `aimo_v122_small.zip` | 22ced3169a4d73b5cfe9b7ceb0d815b6; 4de6852eee8d4c3e6ccb07576c422a31 [588] | 15 of 21 (1004377); 9 of 14 (1004381) [608] |

**Frozen prediction** (Section 4). Assumed: a roughly balanced class mix, a validation-like configuration mix and a
server at most 1.2x slower than our mock, with 170 s as an average (a per-case limit leaves v111 15 of 21 answered
[573]). By a rule fixed before any final result [568], the forecast holds on a track if the final accuracy of v111
(main) or v112 (small), or of another nominee if only that one is scored, lies in its range, so the ranges apply to v115
and v116 if they alone are scored. The prediction's ledger row (`work/miners18/FROZEN_PREDICTION_ledger543.txt`) has
sha256 `ffd7c3fcc370631dbc7501bd713444df47f067ede871a672c15ead8aa91a2ec6`, computed on 18 October after the board runs
of that day, with no external timestamp [566]. **Outcome.** The final had not been scored when this report was
submitted; we will report the evaluated entries' accuracy against the frozen ranges, whichever way it falls.

**Supplementary material.** The full report (draft 29, revised 22 October, 39 pages; `report/REPORT_full.pdf` and `report/REPORT_full.md` in
the repository) holds every detail this version omits; its supplement folder `report/report_supplement/` holds the full text of
its longer appendix parts. Where to look: the audit in full, Supplement E.13, and the board draws against it, the
supplement's Figure 1; every board upload, Supplement A; board-feedback use, Supplement A.2; the 88 negative results
with their bars, Supplement D and E.6; the worked T10 example, Supplement E.12; decode paths, Supplement E.3; the
final-shape mocks and the pre-mortem, Supplement E.15 and E.17; token confidence, the 80-row rescore, the key-headroom
check and the fragility vectors, Supplement E.18; the decision rule's coefficients, Supplement F.4; scripts, including
`audit.py`, Supplement F.7. Figure 1 is made by `report/figures/make_agreement_by_label_v32.py` from held logs (lane G's
loader and the server read of 15 October); it writes its numbers to `report/figures/make_agreement_by_label_v32.out`.

**Number labels.** *Board*: the OFFICIAL hidden validation score, counts only, one draw each. *Public rows*: the
labelled public rows (in-sample where our rule was fitted on them). *Server*: a research run on the contest server.
*Computed*: offline, from logs or outputs we hold. *Mock*: a rehearsal on a virtual clock (time, coverage and validity,
not accuracy). *Model-based*: a simulation. *Local proxy*: a run on a Mac with 4-bit weights standing in for a judged
model. *Guess*: a judgement, given as a range.

**Ledger entries.** Every bracketed whole number is an entry of our dated research ledger (other brackets hold all-row
values; Section 2); the full report cites the same entries, except 589 and 627 (release rebuild checks). The ledger holds internal notes and is not published as it stands; a redacted extract of the cited
entries is available on request.
