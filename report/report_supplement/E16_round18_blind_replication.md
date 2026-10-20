# Supplement to the technical report: Appendix E.16 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 18 October: v102's gpt-oss probe, still open below, failed when v102 was read on 18 October [555] (Section 6.4 of
the report); no white-box route is open. Note added 20 October (draft 28): text moved out of the report in draft 28 is
in the addendum of 20 October (draft 28) at the end of this file. Note added 20 October (draft 29): text moved out of
the report in draft 29 is in the addendum of 20 October (draft 29) at the end of this file; the report keeps a summary
or a pointer.*

### E.16 Round 18: blind replication of STD, X6 read blind, a label-shift test and an input-gradient probe (Sections 2.4, 5.2, 6.5)

Run on 17 October locally (lane GRAD with MLX on a Mac, the rest on the CPU), with no uploads. Every number is computed
on the public rows against bars written before the data; the blind writers' labels were read only after scoring [521,
523, 525-528, 530, 532, 533]. Files: `work/miners18/` (`blindSTD/`, `blindSTD2/`, `blindSTD3/`, `pooledSTD/`, `laneS/`,
`laneGrad/`, `x6_on_blind.out`).

**Protocol of the blind writers** (`PREREG_blind.txt` with `PREREG_blind_addendum.txt`, `PREREG_blind2.txt`,
`PREREG_blind3.txt`, each written before any program). Each writer was a fresh Claude subagent, blind to the other
writers' folders and ledger rows, to lane L's programs, to the raters' ratings and notes, to `calib.json` and to every
LATENT value. It read the 28 public problems (id, text and answer only), lane L's prompt contract `prompt_std.txt`, the
harness `stdread.py` and the scorer's code. Per template it wrote `brute` (a direct check of the statement) and `path`
(a transcription of its own natural solution, with no added checks). Before the freeze, programs ran only at the public
numbers, where both were to give the public answer; every template met this except T28, where all three writers froze
programs that give 42, not 35 (writer 3: 54 of 56 programs gave the answer; footnote to Section 6.5). The programs were
then frozen by sha256 and re-verified after scoring. All three runs used the deployed harness path (`stdread.census`
with its defaults: 60 one-number draws, seed 1616 + T, 2 s per call, 20 s per reply, `min_support` 2) and the frozen
scorer `miners16/laneL/score_std_read.py` (md5 5e1757e4...) unchanged. Writer 1 wrote one program per template, supplied
twice to meet `min_support` (arm A), plus an independently written second brute for the brute-against-brute control S4a
(arm B); writers 2 and 3 wrote two independent drafts per template. Each writer knew the STD idea; none had labels.
Recorded deviations: before the freeze, writer 1 capped the size of its T14 brute (it took 19 s on one instance) and
writer 2 fixed one crash at the public numbers (T23, draft a) and, before any execution, one brute coefficient (T05),
rewrote four brutes for speed, renamed parameter keys in four drafts to pair them and set search bounds for T01, T03 and
T07; writer 3 made speed-only brute fixes in an amendment before the run and unit-tested one brute helper against direct
sums.

**Scorer lines, as printed** (arm A; S4a from arm B for writer 1; bars in brackets):

| Bar | Writer 1 [521] | Writer 2 [523] | Writer 3 [528] | Writers 1 + 2 pooled [527] |
|---|---|---|---|---|
| S1 covered (≥ 20 of 28); false validations (≤ 2) | 21; 1 (T28): PASS | 24; 1 (T28): PASS | 23; 1 (T28): PASS | 24; 1 (T28): PASS |
| S2 AUC on 36 weak + low rows (≥ 0.80); Spearman (≥ 0.40) | 0.724; +0.370: FAIL | 0.900; +0.303: FAIL | 0.789; +0.538: FAIL | 0.904; +0.313: FAIL |
| S3 7B rows (≥ 11 of 12); all rows (≥ 63 of 71); fresh (≥ 20 of 24) | 9; 61; 20: FAIL | 11; 63; 21: PASS | 10; 62; 20: FAIL | 11; 63; 21: PASS |
| S4a brute against brute (median ≤ 0.02; AUC ≤ 0.60) | 0.000; 0.500: PASS | 0.000; 0.500: PASS | 0.000; 0.500: PASS | 0.000; 0.500: PASS |
| S4b joint sampler (AUC ≤ single sampler + 0.05) | 0.815 against 0.724: FAIL | 0.809 against 0.900: PASS | 0.711 against 0.789: PASS | 0.827 against 0.904: PASS |
| S4c template rotation (mean AUC ≤ 0.60) | 0.491: PASS | 0.485: PASS | 0.489: PASS | 0.486: PASS |
| S5 cost (scorer bar 180 s; not informative, no model tokens) | 15 s | 15 s | 15 s | 16 s |
| Verdict line | FAIL (WEAKENED by the pre-registered rule: S1 passes and AUC ≥ 0.70) | FAIL | FAIL | FAIL (information only) |

The scorer's v95 line on the same rows: 9 of 12, 61 of 71, 19 of 24. Not covered: writer 1 T04, T20, T22, T23 and T27
(no valid draws) and T24 (the brute cannot search the instance); writer 2 T04, T20 and T22; writer 3 T04, T20, T22 and
T23; T28 is a false validation for every writer (see below).

**The 12 Skywork and Olmo rows** (1 = non-robust; the reading calls non-robust iff its share of disagreeing draws is at
least 0.05, and keeps v95's call where the template is not covered; wrong calls marked ×):

| Row | Label | v95 | Writer 1 | Writer 2 | Writer 3 | Pooled |
|---|---|---|---|---|---|---|
| T13 Skywork | 1 | 0 × | 1 | 1 | 1 | 1 |
| T15 Skywork | 0 | 0 | 0 | 0 | 0 | 0 |
| T16 Skywork | 0 | 1 × | 0 | 0 | 0 | 0 |
| T04 Olmo (not covered) | 0 | 0 | 0 | 0 | 0 | 0 |
| T06 Olmo | 0 | 0 | 1 × (0.500) | 0 | 0 | 0 |
| T07 Olmo | 0 | 0 | 1 × (0.115) | 1 × (0.115) | 1 × (0.113) | 1 × (0.115) |
| T08 Olmo | 0 | 1 × | 0 | 0 | 0 | 0 |
| T10 Olmo | 1 | 1 | 0 × (0.000) | 1 (0.067) | 0 × (0.000) | 1 (0.067) |
| T13, T15, T17, T18 Olmo | 1, 0, 0, 0 | right | right | right | right | right |
| Right of 12 | | 9 | 9 | 11 | 10 | 11 |

**Why the writers differ** (the writers' post hoc diagnostics on the frozen programs; information only):
- **T06.** Writer 1's path takes a leg as `S // 2`, assuming an even sum; every disagreement is a draw with an odd
  value (10 of 20 valid draws). This is a coding choice, not a way the models fail; writers 2 and 3 have none.
- **T07.** All three paths assume that 17 in base b equals b + 7; 6 of 52 valid draws (2 of 18 in one draft) change
  the problem's class (the leading digit of 17 becomes 2, or the lower bound on b falls below the largest digit), so a
  robust template reads 0.11.
- **T10.** Writers 1 and 3 solved the problem fully generally, so no draw separates path from brute; writer 2's path
  disagreed on 1 of 15 valid draws (0.067), just above the threshold.
- **True positives** (writer 1's diagnosis): T11 assumes the modulus is a power of 10 and the tail below 1; T12 that E
  is even and a + 1 a power of 2; T13 that 12 = 4 · 3 with X coprime to 6; T14 that the target's primes never interact;
  T25 and T26 (gpt-oss rows, outside the AUC rows) use a tangency and an added sum of 2.
- **Drafts disagree too.** Writer 3's two drafts read T11 at 0.733 and 0.067 and T13 at 0.73 and 0.43: a template's
  reading depends on how literally its solution is transcribed.
- **Writer 2's Spearman fail** comes from its T23 brutes, which accept fake rational answers (brute against brute 0.68;
  L 1.000 on a template with a mean rating of 0.2); without T23 its Spearman would be +0.477 (post hoc, not a result).
- **Lane L's "blind" transcriptions** (Appendix E.14: 11 of 12) were written by the same author after reading the
  notes, so they are not a blind replication.

**Pooled read** [527] (`PREREG_pooled.txt`, written before running): three replies per template (writer 1's program and
writer 2's two drafts, unchanged) through the deployed median over validated pairs. It was declared information only,
since both components' results were known. The median follows the majority, so pooling behaves like the better writer;
its gain over the v95 line sits on the Skywork rows (3 of 3 against 1 of 3), with Olmo 7 of 8 covered rows, as v95.

**What it means for the STD entries** [523, 527, 528]. The three writers give 9, 10 and 11 of the 12 7B rows against
the entry's 9: about +1 row of 12, or about +0.4 case per 21 main and +0.5 per 14 small cases if gpt-oss writes like an
average blind writer (guess; range 0 to 1 case). None is a robust pass of the 11-of-12 bar. Only v102 reads gpt-oss
itself as the writer (Section 6.4). All three writers are Claude subagents: independent in context, not in model.

**T28's public answer** (footnote to Section 6.5) [521, 523, 528]. Read literally (line DE meets line AB; Y lies on line
AD), equal powers of A give AX · AB = AE · AC, and Menelaus then gives a²b = (b − c)(b + c)²; the smallest acute integer
triangle with AB < AC is (a, b, c) = (7, 8, 6), unique at perimeter 21, and abc = 336 ≡ 42 (mod 49). The public 35 is
280 mod 49, from (7, 8, 5), the triangle with a 60° angle at A; writer 3 found that it fails the condition numerically
(a cross product of −1.97, in float and in 40-digit arithmetic). Writer 2's programs, one with a coordinate-geometry
brute, also give 42; that writer took the error to be its own. Against the literal reading: gpt-oss low answers 35 in
0.525 of its attempts pooled over six reads (`miners17/laneX/x2_drift.out`), and gpt-oss medium's one labelled row
(non-robust, drop 0.44) is scored against 35 [508]. We have not settled which reading the problem intends. In our
bundles the public answer enters only the STD read's logged `modal_ok` check; the calibration keeps 35 [523].

**Label-shift test (lane S2)** [525, 526] (`laneS/PREREG_labelshift.txt`, `ADDENDUM_S2.txt`, `r_shift.py` →
`r_shift.out`, `RESULT_S2.md`; lane G's machinery: leave-one-template-out on v95's dress read with `decision.json`
refitted per fold). Premise: the stand-in's logistic was fitted on 71 rows that are 73% robust while the boards are
about balanced, so one standard prior correction (−1.007 on the robust logit, log(0.5 / 0.5) − log(52 / 19)) should
raise accuracy at the board's mix. An addendum written before any shifted number found the premise false: the training
script (`release/training/pool_all.py`) weights the classes 0.5 / 0.5, so the shipped intercept already sits 0.733
higher on the non-robust logit than an unweighted refit, and the correction applies the prior a second time; for the
board's 10 robust / 11 non-robust mix the right correction is about −0.1, essentially zero. The candidate was still
evaluated as written:

| Bar | Need | Result |
|---|---|---|
| L1, leave-one-template-out accuracy reweighted to 50/50, in row-equivalents | ≥ +2 over v95 (57.56 at 50/50; 57.31 at the board's mix) | 56.52 (−1.04; −0.64 at the board's mix; template bootstrap 95% −7.56 to +6.37): FAIL |
| L2, fresh rows | ≥ 18 of 24 | 19: PASS |
| L3, the reversed sign lowers the reweighted accuracy | below 57.56 | 51.45: PASS |
| L4, v95's board calls the shift would flip | if local counts exist | none held: not reportable |

The base reproduced (60 of 71, fresh 18 of 24, 0.807 at the board's mix). The candidate makes 42 robust calls against
52 truly robust rows (v95 51) and gets 55 of 71 plain; 9 rows flip, 2 fixed (T19 DeepSeek, T10 low) and 7 broken (T01
Qwen, DeepSeek and low; T02 Qwen and DeepSeek; T09 and T21 medium). An information curve over shifts peaks, post hoc, at
−0.3 to −0.4 (60.6 row-equivalents, carried by three boundary rows); it is not a candidate. No v106 was built and v95
is unchanged. Lesson: check how a model was fitted before proposing to recalibrate it.

**X6 read blind** [530] (`miners18/x6_on_blind.out`). Lane X's frozen scorer `x6_na_share.py` (md5 02e6e223..., frozen
before any blind program existed; Appendix E.14) ran unchanged on the three writers' logs and the pooled log, on the
covered rows of DeepSeek, Qwen and gpt-oss medium and high (42 to 44 rows; 10 or 11 non-robust). Its primary statistic,
the share of valid one-number draws on which the solver's own path crashes (NA), gave AUC 0.474, 0.500, 0.437 and 0.472:
KILL on all four (bar 0.75, kill at 0.60). The secondary statistic D, a crash or a wrong integer, separated better (AUC
0.859, 0.669, 0.799, 0.697) but its AUC after removing difficulty was 0.654, 0.438, 0.632 and 0.427 against a bar of
0.70: FAIL on all four; template rotation passed on 2 of 4. The hand bench's 1.000 was contamination plus difficulty.
The planned override (D ≥ 0.5 → non-robust for gpt-oss high) is closed; no entry changed.

**Lane GRAD: an input-gradient probe** [532, 533] (`laneGrad/PREREG_grad.txt` and an addendum written before any
template gradient; `RESULT_grad.md`; local proxy: Qwen3.5-4B in 4-bit weights, gradient pass in float32). For each
template, the gradient of the summed log-probability of Qwen's own 768-token W-sol solution with respect to the input
embeddings of the problem's tokens; S is the log of the mean gradient norm over surface tokens (names, prose) divided by
that over math tokens (numbers, operators, variables, LaTeX commands), by a fixed regex. Prediction: higher S, more
fragile. Bars on Qwen's 12 labelled rows (4 non-robust): G1 AUC ≥ 0.75; G2 the same after regressing S on v95's
stand-in agreement ≥ 0.70; G3, token classes shuffled within each problem, mean AUC ≤ 0.60. Result: G1 0.250, the
opposite sign to the prediction (reading it as a reversed signal would be post hoc; it lies inside the shuffle band of
0.16 to 0.81, so 12 rows give these bars little power); G2 0.219; G3 0.499: FAIL. Information lines: DeepSeek 0.43,
Skywork 0.50, Olmo 0.79 (inside its own shuffle band) and all 34 weak rows 0.42. Surface tokens carry larger gradient
norms than math tokens on 26 of 28 templates, whatever the label. With W, W-sol and W-think, every local white-box route
is closed; v102's gpt-oss probe is the only open one.

**Group 8 of the negative results** (17 October; 4 rows):

| Lane | Reading or premise | Bar | Measured | Verdict |
|---|---|---|---|---|
| blind STD writers 1 to 3 | the STD bench rebuilt by three independent blind writers | the frozen scorer's S1 to S5 (S2 AUC ≥ 0.80 and Spearman ≥ 0.40; S3 11 / 63 / 20) | 9, 11, 10 of 12 7B rows; AUC 0.724, 0.900, 0.789; Spearman +0.370, +0.303, +0.538 [521, 523, 528] | failed (writer 1 WEAKENED); the contaminated 12 of 12 not reproduced |
| S2 | prior-shift correction of the stand-in | L1 ≥ +2 row-equivalents at 50/50 | −1.04 [526] | failed; premise wrong |
| X6, blind | crash share (NA) or deviation share (D) of the solver's own path over one-number draws, on the blind writers' logs | X6a AUC ≥ 0.75 (≤ 0.60 kills); X6b AUC after difficulty ≥ 0.70; X6c rotation P ≤ 0.05 | NA AUC 0.437 to 0.500 (KILL on four logs); D after difficulty 0.427 to 0.654 [530] | failed; the hand bench's 1.000 not reproduced |
| GRAD (local proxy) | surface-against-math input-gradient share of Qwen3.5-4B | G1 AUC ≥ 0.75; G2 after difficulty ≥ 0.70; G3 shuffle ≤ 0.60 | 0.250 (reversed); 0.219; 0.499 [533] | failed |

The pooled read [527], information only, is not counted.

### Addendum of 20 October (draft 28)

*Text moved out of the report in draft 28 (verbatim, from draft 27).*

*From Section 7 (lane X6's blind read is the report's Appendix E.16):*

Lane X6's one-number neighbourhood statistic borrows from certified robustness by randomized smoothing
(Cohen, Rosenfeld and Kolter, ICML 2019; *abstract*); it failed when read blind (Appendix E.16).

*From Section 6.5 (the AUCs are in the report's Section 6.5 table):*

Discrimination held for writer 2
and the pooled read (AUC 0.900 and 0.904 against 0.905); the 7B-row gain did not.

*From the caption of Section 6.5's table:*

Writer 1's own rule
reads WEAKENED; the pooled read is information only.

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Section 6.5:*

No blind writer reproduces 12 of 12: they gain 0, 2 and 1 rows over the entry, not 3. STD depends on how the writer
solves: true positives come from number-specific shortcuts in its solution (T11 to T14), false alarms from coding
choices (T06) or class-changing draws (T07, every writer), misses from fully general solutions (T10). The contaminated
programs got exactly these three Olmo rows right, consistent with guidance from the notes.

*From Appendix E.16:*

- **Blind writers** (`PREREG_blind.txt` and its successors, each written before any program): three fresh Claude
  subagents, blind to lane L's programs, to the raters' ratings and notes and to every label, read the 28 public
  problems (text and answer only) and wrote per template a `brute` (a direct check of the statement) and a `path` (a
  transcription of its own solution); the programs were frozen by sha256 and run through the deployed harness path and
  the frozen scorer unchanged. S1 coverage passed for every writer (21, 24 and 23 of 28; one false validation each,
  T28), S2 failed for every writer, and S3 passed for writer 2 only (Section 6.5) [521, 523, 528].
- **Label shift (lane S2)** [525, 526]: the premise was false, because the training script already weights the classes
  0.5 / 0.5; evaluated as written, L1 was −1.04 row-equivalents (bar +2), so no v106 was built. Lesson: check how a
  model was fitted before proposing to recalibrate it.
- **X6 read blind** [530]: the frozen scorer's crash share gave AUC 0.437 to 0.500 on the four logs (KILL; bar 0.75),
  and the deviation share after removing difficulty 0.427 to 0.654 (bar 0.70); the hand bench's 1.000 was contamination
  plus difficulty.
- **Lane GRAD** [532, 533]: G1 AUC 0.250 on Qwen's 12 rows (bar 0.75), G2 0.219, G3 0.499; surface tokens carry larger
  gradient norms than math tokens on 26 of 28 templates, whatever the label. With W, W-sol and W-think, every local
  white-box route is closed; v102's gpt-oss probe, the last open one, failed on the server (Section 6.4) [555].

*From Appendix E.16:*

**What it means for the STD entries** [523, 527, 528]. The three writers give 9, 10 and 11 of the 12 7B rows against the
entry's 9; none is a robust pass of the 11-of-12 bar. All three writers are Claude subagents: independent in context,
not in model. v102 then read gpt-oss as the writer; both arms were killed (Section 6.4) [555].

*From Section 6.5:*

| Writers 1, 2 pooled [527] | 11 | 63 | 21 | 0.904 | FAIL |

*From Section 6.5:*

[^t28]: All three blind writers' programs give 42 on T28, not the public answer 35; one found that the triangle giving
35 fails the stated condition. Yet gpt-oss low answers 35 about half the time [508]. We flag a possible public-key
issue, not an established error [521, 523, 528].
