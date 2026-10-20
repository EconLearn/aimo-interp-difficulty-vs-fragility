# Supplement to the technical report: Appendix E.13 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October: text moved out of the report in draft 27 is in the addendum of 20 October at the end of this file.
Note added 20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29)
at the end of this file; the report keeps a summary or a pointer.*

### E.13 The generalisation audit in full (Section 2)

Lane G of round 17 (`work/miners17/laneG/AUDIT.md`; scripts `g1_policy_loto.py` to `g5_selection.py` in that folder,
each with its `.out`; CPU only, existing files, no model runs) [505, 509]. Labels: board (OFFICIAL), public rows
(measured on the 71 labelled rows; single reads unless stated), validation inference (deduced from board counts, as in
Appendix A.2), model-based (a simulation) and guess (a judgement, given as a range). Fresh rows are the 24 AIME-2026
rows on 12 templates; here every other row (47, including the five templates lane B left unmatched) counts as exposed,
so these splits differ from lane B's, under which the entry (in-sample) gets 19 of 24 fresh rows right against 31 of
35 exposed ones [440, 446].

**What decides v95's cases, and how each part was chosen** (main board: Qwen 2, Skywork 3, Olmo 2, DeepSeek 3, high 3,
low 5, medium 3; small: Qwen 5, Skywork 3, Olmo 3, DeepSeek 3 [432, 327]):

| Component | How chosen | Board feedback | Cases it decides (main / small) |
|---|---|---|---|
| Stand-in reading and `decision.json` (fitted 5 October on the 71 public rows; the same md5 from v7 to v95) | public; the statistic chosen leave-one-template-out among five [61] | no | 13 / 8 |
| Qwen quick finish at K 4, not K 8 | public; K 8 withdrawn after one hidden case on each board flipped the wrong way [153-156] | touched | feeds every stand-in case |
| Decision cut at 0; low cases read by the stand-in | public defaults kept after board tests (v11, v58) [140, 330] | tested, rejected | no answers changed |
| gpt-oss high answered "robust" | public: robust on 13 of 15 rows; board level at 16 [336, 338] | tested, neutral | 3 / 0 |
| Olmo's own run on Olmo cases | public: 9 of 9 attempts end on easy robust rows, 0 of 8 on hard non-robust ones; adopted when the board went 16 → 17 [339-345] | adopted | 2 / 3 |
| Skywork's own run on Skywork cases | thin public support; adopted when the board went 17 → 19 [348-350] | chosen | 3 / 3 |
| Per-case targets and decode paths | measured costs; engineering [465, 466] | no | — |

Seven decisions were made or kept with board feedback (the quick finish's K, the cut, low's re-read, the high prior, the
two own runs and the combine rule); only the high prior and the two own runs make v95's answers differ from the
pre-iteration nominee v22. On the main board those three changed 5 answers (2 high, 2 Skywork, 1 Olmo), net +3
(validation inference). One choice, the stand-in's K, was kept against the board [204, 509].

**Capacity.** `decision.json` holds 4 + 3 + 3 = 10 fitted coefficients, one model active per case, fitted on 71 rows (19
non-robust) in 27 template clusters, about 6 non-robust rows per slope in the full model; the fit reproduces from
`release/training` to 2e-4. Leave-one-template-out is nearly in-sample: −1 row on the dress read, 62 → 60 on the
fit-time reads [509].

**Out-of-sample accuracy** (public rows; template-cluster bootstrap, 10,000 resamples):

| Estimate (v95 rules) | Rows | Accuracy | At the board's class mix |
|---|---|---|---|
| Dress read, in-sample | 71 | 61/71 = 0.859 [0.759, 0.935] | 0.835 |
| Dress read, leave-one-template-out | 71 | 60/71 = 0.845 [0.746, 0.922] | 0.807 [0.699, 0.898] |
| the same, hard region | 37 | 30/37 = 0.811 | 0.804 |
| the same, fresh AIME-2026 rows | 24 | 18/24 = 0.750 [0.591, 0.905] | 0.747 |
| the same, the other 47 rows | 47 | 42/47 = 0.894 | 0.832 |
| Fitted on the other 47 only, tested on the fresh 24 | 24 | 18/24 = 0.750 | 0.747 |
| Four older reads, leave-one-template-out | 71 | 61 to 62 of 71 (fresh 17 to 19 of 24) | 0.80 to 0.86 |
| Stand-in alone, fit-time reads: fresh / other | 24 / 47 | 0.708 / 0.915 | — |
| Always robust | 71 | 0.732 | 0.476 |

The 11 leave-one-template-out errors are T05 Qwen and DeepSeek, T19 DeepSeek, T16 and T13 Skywork, T08 Olmo, T25 and T26
high, T09 and T10 low, and T12 medium; six fall on fresh rows, three of those (T16 and T13 Skywork, T26 high) on
board-chosen routes [509].

**Board against public** (model-based: each hidden case right with probability p, p from the bootstrap; binomial over 21
or 14 cases):

| Board | p | Expected | 90% predictive | Observed (board, H2) | P(score ≤ observed) |
|---|---|---|---|---|---|
| Main, from all 71 rows | 0.807 | 17.0 | 13 to 20 | 16 | 0.39 |
| Main, from the fresh rows | 0.747 | 15.7 | 11 to 20 | 16 | 0.58 |
| Small, from the 34 small-model rows | 0.817 | 11.4 | 8 to 14 | 10 | 0.27 |
| Small, from the 16 fresh small-model rows | 0.762 | 10.7 | 7 to 14 | 10 | 0.39 |

The four H1 draws on the same 21 cases (19, 17, 18 and 16; mean 17.5, SD 1.29) measure reading noise only; a new 21-case
set adds case sampling, a binomial SD of about 1.8 cases at p = 0.81. On small the public rows over-predict (11.4
expected against 8 to 10 observed over four draws), the spectrum effect of Section 3.4. For scale, 14 of 14 has
probability 0.044 at a true p of 0.80 [509].

**Selection** (`g5_selection.py`, model-based). The seven main-board candidate changes with recorded counts (5 to 11
October) changed 14 hidden answers, 6 of them right. Keeping a change only when the board rises yields an expected kept
gain of +3.9 (90% range 1 to 8; P(≥ 3) = 0.72) if every changed answer is a coin flip, and +7.3 if they are right 70% of
the time; the observed +3 sits inside the coin-flip range [509].

**Public-only counterfactuals** (leave-one-template-out; rows right of 71, then summed over five reads, of 355):

| Variant | Dress read | Five reads | Fresh rows, five reads (of 120) |
|---|---|---|---|
| v95 as shipped | 60 | 307 | 92 |
| Skywork and Olmo cases to the stand-in, high prior kept | 62 | 309 | 93 |
| Skywork cases to the stand-in only | 62 | 312 | 97 |
| Olmo cases to the stand-in only | 60 | 304 | 88 |
| High cases to the stand-in only | 59 | 300 | 87 |
| Stand-in on every case (as v22) | 61 | 302 | 88 |

Sending Skywork's cases to the stand-in never loses on public rows (+2, +1, +1, +1 and 0 over the five reads) but rests
on two templates (T13, T16), and the board said the opposite (−0.67 per Skywork case, validation inference); both
effects are about one case per 21. As readers of all 34 small-model rows, both 7B own-run rules trail the stand-in
(Skywork 26 against 30, Olmo 24 against 30; Skywork 6 against 12 on the 14 hard small-model rows). Combined estimate of
swapping every board-chosen part for its public default: about 0 per 21 main cases, range −1 to +1.5, and about 0 per 14
small cases, range −1.5 to +2 (guesses) [509]. A board run cannot settle it, because the board chose the rule, and the
swap would also slow Skywork cases (the stand-in takes about 150 to 200 s per case against 46 to 138 s for the own run)
[509].

**Caveats.** Single reads on 71 rows in 27 templates; about ten hand-set values (strength codes, caps, K, the own-run
thresholds, the high prior) cannot be cross-validated; the
per-configuration hidden mix is unknown; most Olmo rows in the dress were read at K 1 while v95 runs K 3 (K 3 = K 1 on
Olmo's own rows [443]); board answer counts come from same-run or previous-run arithmetic [329b].

**Lane R, a fresh-regime recalibration** (pre-registered `work/miners17/laneR/PREREG_laneR.txt` and an addendum written
before computing; `r_fresh.py` → `.out`, `RESULT_R.md`) [514, 515]: `decision.json`'s model plus one intercept shift for
fresh templates, deployed with fresh = 1 for every final case. It reproduced lane G's base exactly (60 of 71; fresh 18
of 24; exposed 42 of 47). R1, fresh rows at least 20 of 24: 19, fail. R2, exposed rows lose at most 1: 42 of 47, pass.
R3, random-template draws reaching 20 of 24 at most 0.05: 0.0035, pass. R4, the shift's sign: +0.90 logits (template
bootstrap −1.23 to +2.44; positive in all 27 folds), pass. One row changed (T10 low), and 22% of random-template draws
also reach 19 of 24, so the +1 is not fresh-specific. Three of the six fresh errors sit on routes the shift cannot touch
(Skywork's own run, the high prior). No change to v95.

### Addendum of 20 October

*Text moved out of the report in draft 27 to keep its main text within the limit (verbatim, from draft 26).*

*From Section 2.4 (still in the report's Appendix C, lane S2, and Appendix D):*

A pre-registered prior-shift correction
for balanced classes also failed (−1.04 row-equivalents, bar +2) on a wrong premise: `decision.json` was already
class-balanced [525, 526].

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.13:*

**Public-only counterfactuals** (leave-one-template-out; rows right of 71, then summed over five reads, of 355):

| Variant | Dress read | Five reads | Fresh rows, five reads (of 120) |
|---|---|---|---|
| v95 as shipped | 60 | 307 | 92 |
| Skywork and Olmo cases to the stand-in, high prior kept | 62 | 309 | 93 |
| Skywork cases to the stand-in only | 62 | 312 | 97 |
| Olmo cases to the stand-in only | 60 | 304 | 88 |
| High cases to the stand-in only | 59 | 300 | 87 |
| Stand-in on every case (as v22) | 61 | 302 | 88 |
