# Supplement to the technical report: Appendix E.6 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix
part and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references
point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's
folder. Note added 20 October: text moved out of the report in draft 27 is in the addendum of 20 October at the end of
this file.*

### E.6 Negative results in full (Section 5)

The 24 rows below are ideas that did not enter the entry. 22 had a bar written in the ledger before the data came back.
Two did not and are marked "post hoc" or "no bar". One is marked "not refuted": it held on a second read but could not
be built. The small-track push of 13-14 October is listed separately in Appendix E.10. "Server read" means one
evaluation-hour research run on public problems. The adoption decisions for the entry's own stages, with their bars, are
in Appendix C.

#### E.6.1 Changing the problem: perturbations and sibling problems

| Idea | Hypothesis | Bar | Measured | Why it failed |
|---|---|---|---|---|
| Answer-keeping rewrites (5 organiser-style families), gpt-oss low [302, 309] | Worst-family accuracy drop D separates non-robust rows | D ≥ 0.20 on both non-robust rows and on ≤ 1 of 5 robust rows | non-robust +0.03, +0.10; robust up to +0.15; AUC 0.30; formal verdict "unclear by one hundredth", failed in substance | For models that solve the original reliably, LLM-written families add only binomial noise in the organisers' own data (2 of 35 cells against a 0.051 no-effect rate, p 0.57) [183] |
| gpt-oss writes its own rewrites [309] | Same, inside the hour | as above | "drops" 0.40, 0.27 and 0.51 on a robust control | Whole rewrites come out wrong: defective texts, not fragility |
| Re-numbered siblings with known answers, gpt-oss low [100] | Response to new numbers tracks the label | Spearman ≥ +0.43 | −0.04 (own re-numberings −0.16) | The reader is stronger than many examinees; siblings measure the reader |
| Answer-changing "expert-style" texts, gpt-oss medium [310, 318, 319] | Base minus expert-text accuracy X separates medium rows | AUC ≥ 0.85; ≥ 3 non-robust and ≤ 2 robust rows with X ≥ 0.25 | AUC 0.55; 1 non-robust and 3 robust rows at X ≥ 0.25 | Our harder versions are harsher than the organisers' variants: X measures distance to the model's limit, i.e. difficulty |
| Same texts, Skywork [303, 312] | Breaks T13 (official drop 1.00) and not robust T15 / T16 | T13 ≤ 1 of 8 on some kind; T15 / T16 ≥ 5 of 8 on every kind | T13 0 of 24; T15 23 of 24; robust T16 also ≤ 1 of 8 | Skywork rarely ends T16 inside 9,000 tokens: "breaks" and "needs more tokens" cannot be told apart |
| Expert texts on gpt-oss low, offline [309, 321] (**post hoc; not refuted**) | As above, low rows | none, then a second read | AUC 1.00 on 2 × 5 rows; held on a second read (0.22, 0.31 against 0.75 to 1.00) | Not buildable: see the next two rows |
| In-run siblings: medium writes, high keys, low is judged [311, 314] | The offline effect can be made inside the hour | keys right on ≥ 7 of 8 originals; ≥ 6 of 8 rows with ≥ 3 keyed siblings | 13 of 36 siblings keyed; 1 of 8 rows usable | Writing a valid harder sibling needs someone to solve it, and high runs past 8,000 tokens exactly where it matters |
| Program-aided siblings: high writes a solver, random valid instances [316, 321] | Program keys replace model keys | programs right for ≥ 5 of 8 problems | 4 of 8; X the wrong way round (T10 non-robust +0.04, T09 robust +0.46) | Low breaks only on adversarially chosen instances, which random valid instances rarely hit |
| Surface twins and number variants of T13, Skywork and Olmo [260, 263, 266] (**no bar**) | Some variant family reproduces the official drop | none (one decisive cell) | Skywork 12 of 12 renamed or typo'd, 13 of 14 number variants, 18 of 18 rephrased, distractor or story; Olmo 6 of 6 number variants and 8 of 8 answered attempts on the rest | The label on this cell is made by variant texts that are not public |

#### E.6.2 Priors, thresholds, recalibration and bets on the test's structure

| Idea | Hypothesis | Bar | Measured (board) | Why it failed |
|---|---|---|---|---|
| Threshold shifted to the stated base rate [137, 140] | The stand-in calls too few cases robust | paired gain ≥ +2 supports, ≤ 0 refutes | 13 against 16; 5 calls flipped to robust, 4 of them wrong | False alarms are confident (spectrum effect, Section 3.4) |
| Recalibration under a hidden-like reweighting [192] | Some rank-preserving fix gains | +0.03 with P ≥ 0.90 | none passes (public rows, reweighted) | The hidden-like false alarms score above truly non-robust rows |
| Rank within each call, top half robust [279, 282] | The set is balanced within each configuration | ≥ 17 | 16 | No gain over the fixed threshold |
| Opposite labels on shared problems [286, 290] | Shared problems carry opposite labels | ≥ 17 | 15 (predicted 17 if true, 14 if not) | Premise not supported on main |
| Low-effort cases re-read at a longer cap [325, 330] | Low's own modal share ≥ 0.83 at 4,500 tokens means robust | ≥ 17 | 14 | The public margin (0.81 against 0.85) was noise |
| Two readers combined by AND / OR [322, 324, 327, 329] | Errors of the two readers do not overlap | ≥ 10 (small), ≥ 17 (main) | 9 and 15 | Each reader adds robust calls at about one right in two [330] |

#### E.6.3 Probing the model's internals and its reasoning

| Idea | Hypothesis | Bar | Measured | Why it failed |
|---|---|---|---|---|
| Embedding noise on problem tokens, gpt-oss low [164, 173] | Fragile problems scatter more under input noise | AUC ≥ 0.75 on hard rows | 0.49 on 26 rows of an earlier hard-row list, 0.62 on its gpt-oss rows; tracks agreement (Spearman 0.54) | Noise on the prompt template (placebo) disrupted the model more than noise on the problem |
| Probes on Qwen3.5-4B prefill states, distilled from gpt-oss behaviour or from human difficulty ratings [211, 213, 217] | A small model's internal state carries the reader's signal | small-row AUC ≥ 0.86 | distilled probe (layer 16) 0.742; human-difficulty probe (layer 8) 0.562 | The state tracks gpt-oss (Spearman +0.66 over templates) but too weakly to replace it |
| Oral exam: follow-up questions on the model's own solution [296, 308] | A robust solver answers "the next question" consistently | AUC ≥ 0.80 | 0.557 | Robust and non-robust templates both answer follow-ups consistently |
| Response-state distance from solved cases [296b, 308] | Mid-depth states of fragile solves lie far from solved cases | AUC ≥ 0.80; sabotage column ≥ 0.10 lower | 0.735; plain Euclidean sabotage 0.774 | A noisier copy of difficulty |
| Own-prefix ease (log-probabilities of the first 1,000 thinking tokens) [237, 244] | Model-specific ease tracks the label | small board ≥ 10 of 14 | 5 and 7 of 14 | Repeatable (r 0.60 between reads) but unrelated to the label |
| Text familiarity [247] | Memorised problems are fragile | ≥ 10 of 14 | 6 of 14 | Barely sees exposure (about 0.1 SD) |
| Recognition premium on renamed text [249, 257] | Ease drops when a known problem is renamed | replication AUC ≥ 0.70 | 0.746 on one read, 0.441 on the replication | Only the first 250 tokens repeat: the model restating the text |
| Paired-scoring divergence, original against typo twin [255, 261] | A noise-free divergence tracks the label | AUC ≥ 0.70 with p < 0.05 (permutation by template) on 31 public small labels | reliability 0.89; AUC 0.40 | A clean instrument that measures something else |
| Forced answers as a robustness certificate [189, 190, 197] | Unanimous forced answers certify robustness | no wrong flip | 0 right, 5 wrong (post hoc it had looked like 2 right, 0 wrong) | T13: the small models solve it and are non-robust anyway |

**The probe baseline in full** (Section 5.2; pre-registered [388], read in [394]): for five readers, an L2 logistic
probe on the last prompt-token hidden state at every layer, plus strength, scored leave-one-template-out on the 71 rows,
with layer and regularisation chosen by an inner leave-one-template-out; controls: template states shuffled across
templates, and the 37 hard rows.

| Reading (71 labelled public rows) | Selection | Accuracy / balanced / AUC | 37 hard rows | Main board (H1) | Basis |
|---|---|---|---|---|---|
| Always robust | none | 0.732 / 0.500 / — | 0.514 / 0.500 | 10 [99] | computed [387] |
| Probe, Qwen3.5-4B, layer by inner CV (17) | nested | — / 0.669 / 0.743; shuffled 0.525 | balanced 0.570 | not run | server [394] |
| Stand-in, shipped fit | features chosen on these rows; leave-one-template-out fit | 0.845 / 0.844 / — | 0.743 (refit inside; six reads) | 13 to 16 | public rows [272b, 278] |
| Skywork own-run rule as a reader | threshold chosen on these rows | 0.859 / 0.804 / 0.89 | 0.784 / 0.78 / 0.83 | 12, every case [299] | computed [272b, 387] |
| Olmo own-run rule as a reader (39 read rows) | threshold chosen on these rows | 0.641 / 0.708 / 0.71 | AUC 0.63 | — | computed (`xread.out`) |

No probe met the bar, even post hoc [394]; the best honest one sits between always-robust and the stand-in, compared
like for like [397], and a reading without signal can score below chance here (strength-only AUC 0.342 [391]). The
probe is our re-implementation; we did not run the organisers' kit probe. The other four readers' probes
(inner CV chose layer 0) score balanced 0.31 to 0.43, and all five at the best layer chosen after seeing scores 0.64 to
0.73 [394]; the stand-in's shipped coefficients at K 8 score 0.850 / 0.868, hard rows 0.807 / 0.809 (computed,
`standin_k.out`).

### Addendum of 20 October

*Text moved out of the report in draft 27 to keep its main text within the limit (verbatim, from draft 26).*

*From Section 5.1 (still in the report's Appendix D):*

At 80% power detectable effects are larger (Spearman 0.51, not 0.37,
at 28 templates).
