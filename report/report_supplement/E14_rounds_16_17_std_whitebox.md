# Supplement to the technical report: Appendix E.14 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 18 October: v102 was read on 18 October [555]; its results (both STD arms killed, the gpt-oss probe failed) are in
the report's Section 6.4 and Appendix E.14, which this file predates. Note added 20 October: text moved out of the
report in draft 27 is in the addendum of 20 October at the end of this file. Note added 20 October (draft 28): text
moved out of the report in draft 28 is in the addendum of 20 October (draft 28) at the end of this file. Note added 20
October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29) at the end of
this file; the report keeps a summary or a pointer.*

### E.14 Rounds 16 and 17: STD, white-box probes and eighteen more negative results (Sections 5, 6.3, 6.4)

Run on 16 October after the final files were chosen: round 16 (lanes S, L, P, Q, T) [478] and round 17 (lanes G, X, T,
F, W; frame `work/CRP_FRAME17.md`) [505]. Bars were written before computing unless marked post hoc. Labels: computed
(CPU bench or our logs), server (a research upload's log), local proxy (MLX 4-bit weights on a Mac standing in for the
judged bf16 model; single runs), post hoc.

**STD in detail** (lane L: `work/miners16/laneL/DESIGN.md`, `prompt_std.txt`; frozen scorer `score_std_read.py`, md5
5e1757e4...) [482, 489].

- **Why one number at a time.** The raters' notes showed that their dormant conditions are mostly coincidences in the
  solution path that change when one number moves (T13: an equal parity split at exponent 17; T26: the target is the
  extremal value; T16: an off-by-one on a prime square; `DESIGN.md`). A brute force with droppable conditions cannot see
  these; a transcription of the path compared with brute force can.
- **Harness.** Child processes with `-E -s`, an empty environment and memory, CPU and file-size limits; 2 s per call and
  20 s per reply; each function called twice at the given numbers (non-deterministic replies dropped); the modal answer
  is the most common `brute` value among replies whose two programs agree, with at least two such replies; a validated
  pair has both programs equal to it; a `path` that crashes counts as not applicable [482, 489].
- **Bench** (computed; hand-written programs for 15 templates). The pre-registered census of droppable constraints was
  killed (Spearman +0.236 against a bar of 0.30; 9 of 12 7B rows). The post hoc path-against-brute reading gave 12 of 12
  7B rows (64 of 71, fresh 21 of 24; AUC 1.000) with one sampler, and 11 of 12 (63 of 71) with digit-length-preserving
  draws and blind transcriptions (AUC 0.963 / 0.920); the transcriptions are contaminated by the raters' notes [482].
- **Through the deployed code.** v98's module reproduces the bench: 12 of 12, 64 of 71, AUC 1.000 (frozen scorer 0.905,
  because T04 has no valid draws) [489]. The entry candidates v100 / v101: per-case mocks with 0 invalid cases at 1.0x
  to 1.6x (main 3,420 s against v95's 3,339 at 1.0x; margin 88 s at 1.6x; v107 / v108, the same with v104's skip, give
  the same answers on 455 mock case runs with a margin of 753 s on main and 650 to 825 s on small [531]); every answer
  outside Skywork and Olmo cases identical to v95 / v96; 12 of 12 with v98's inputs and 11 of 12 with lane L's "blind"
  transcriptions, written by the same Claude agent (lane L) after reading the notes (a T07 false positive; independent blind writers in
  Appendix E.16) [495]. STD takes up to 220 s per case including the gpt-oss load, so when it finds no validated pair
  the main fallback is cut short (Qwen's quick finish or plain robust, not v95's own run): v100 can beat v95 only if STD
  covers the hidden problems [495].
- **Other lane L designs.** A ladder of retrieved rated anchors failed (Spearman −0.107 against a shuffled 95th
  percentile of 0.31); averaging many cheap gpt-oss medium ratings is predicted to reach Spearman 0.69 at K 32, passing
  its aggregation bar, yet the 7B policy stays at 9 of 12, because gpt-oss's errors are template-specific [482].

**The v102 read: bars in full** (Section 6.4). v102 runs two reads inside case 1,
with bars and scorers fixed before any data [482, 489, 501, 502]:

- **STD** on all 28 public templates (gpt-oss low, K 8, cap 4,000): S1, a validated program pair on at least 20
  templates with at most 2 false validations; S2, AUC at least 0.80 on weak and low rows and Spearman at least 0.40 with
  the five-rater mean; S3, the 7B policy at least 11 of 12, 63 of 71 and 20 of 24 fresh; S4, three sabotage controls;
  S5, at most 190 s per deployed case (`miners16/laneL/score_std_read.py`).
- **A white-box probe**: a ridge regression on gpt-oss-120b hidden states (one forward pass, three fixed layers, mean
  and last token), fitted in the run on the 325 rated pool problems and tested on the 28 templates with lane W's bars
  (Section 5.2; `miners17/laneW/score_woss.py`).

Outcome branches were written before any data (`miners17/laneT2/BRANCHES.md`; `classify_v102.py` prints the branch)
[511]: (a) STD passes S1 to S5: ship v100 / v101 (now v107 / v108 [531]) only if they then score at least 16 of 21 and
10 of 14; (b) S1 fails and the cap or format losses could close the gap (rule B1): research read v103 (two-stage STD);
(b0) S1 fails on the answer ceiling or on the programs: STD closed for entries; (c) S1 passes but S2, S3, S4b or S4c
fails: predicate flips (`score_m2.py`, same log) or v103; KILL: fewer than 14 templates covered or S4a fails; (d) the
probe passes W1 to W4: a probe entry whose ablation is the same entry with the probe switched off, the White-Box Award's
test; (e) everything fails: keep v95 / v96. Risk stated before data: S1's 20 of 28 sits near gpt-oss low's own answer
ceiling (21 to 23 of 28 modal answers right in v97) [511].

**Targeted siblings (v99)** [487, 488, 493]: the judged 7B model solves STD-flagged re-instantiations, and a case is
non-robust iff its accuracy there falls at least 0.25 below the original. Building it exposed two design problems before
any data: it costs more than v95's per-case targets (STD alone about 185 s, one Skywork batch at least 180 s), and its
coverage bar counts templates with at least two flagged siblings while the hand programs flag only 2 of the 10 Skywork
and Olmo templates, so that bar would measure the base rate of flags, not readability. Deprioritised, not uploaded
[493].

**Lane Q: a 4B program writer** (local proxy; `work/miners16/laneQ/RESULT.md`; Qwen3.5-4B, K 4, the organisers' label
sampling, lane L's prompt and frozen scorer) [485, 496]:

| Local proxy, 28 templates × K 4 | Thinking off, cap 2,500 | Thinking on, cap 6,000 |
|---|---|---|
| Replies ending before the cap | 5 of 112 | 10 of 112 (102 never closed their thinking) |
| Program block parsed / both programs run | 5 / 4 of 112 | 6 / 2 of 112 |
| Validated pairs; templates covered (bar 20) | 4; 2 (T06, T07) | 0; 0 |
| False validations | 0 | 0 |
| Small-track policy | 28 of 34, the v96 line unchanged | the same |

The writer does not terminate rather than writing wrong programs; a larger cap would cost more than the ~190 s per case
available [496].

**Lanes W, W-sol and W-think: white-box probes** (local proxy; `work/miners17/laneW/RESULT.md`, `RESULT_wsol.md`,
`RESULT_wthink.md`) [498-500, 506, 507, 516]. Features: the residual stream after layers 8, 16 and 24 of 32, each
mean-pooled and at the last token (15,360 features, z-scored on the pool); a hand-written forward pass reproduces the
model's logits (bare text: max difference 0); ridge with the regularisation chosen by 5-fold cross-validation (3.16e4,
inside the grid); the W2 threshold is the 0.529 quantile of the out-of-fold pool predictions (the pool's call rate is
0.471). Information lines, none promoted: single vectors on the templates reach 0.454 at most on the bare text (layer
16, last token) and 0.20 to 0.38 after the solution; one vector after the solution meets W2's counts (11 / 63 / 21) at
W1 0.195, a post hoc pick the pre-registration forbids. Only 15 of 353 solutions finished inside 768 tokens, so the
W-sol states mostly read a truncated first part of the work. W4 passed both times (median 0.26 s per problem on the bare
text; maximum 59.7 s after the solution, bar 60 s); W3, the shuffled-target sabotage, passed both times (0.019 and
−0.034). Pool-internal signal did not rise with the solution (nested out-of-fold Spearman 0.346 on the bare text, 0.302
after the solution). **W-think** (pre-registered [507]; `RESULT_wthink.md`) read the states after 2,048 tokens of the
model's own thinking (greedy, batched generation validated against unbatched passes, agreement at least 0.991 on all 353
items): W1 0.304 (95% interval −0.08 to 0.61), W2 9 / 61 / 18, W3 0.027, W4 108 s at most (batched); only 2 of 353
thinking blocks closed inside the cap, so the states read unfinished reasoning. The pre-stated dose-response direction
(W1 above 0.454) was refuted; pool-internal skill stayed flat (nested 0.346, 0.302, 0.317), and W-sol's post hoc
single-vector line did not replicate (7 / 59 / 17) [516].

**Lane X: mechanisms from other fields** for the 52 labelled rows of DeepSeek, Qwen and gpt-oss medium and high
(`work/miners17/laneX/`; `PREREG_laneX.txt` written before each test; 80 pooled gpt-oss low attempts per template from
six reads) [508]:

- X1, drift diffusion (fast against slow errors): AUC 0.692 (bar 0.75), and 0.288 on the residual after difficulty (bar
  0.70); failed.
- X2, item drift across our reads: 0 of 15 templates drift; premise not met, killed.
- X3, backward error: real 0.116 against a placebo of 0.032, void and killed; low's wrong answers are answers to
  sub-problems, not to neighbouring instances.
- X4, metamorphic target swap on medium: AUC 0.225, reversed, post hoc.
- X5, classification consistency (not a reading): v95's 6 errors on the 52 rows each have a label-flip probability of at
  most 0.03, and the plug-in ceiling is about 51 of 52 against v95's 46, so about 5 rows of headroom are real at the
  assumed label noise; at twice that noise the ceiling is 47.8 of 52 and P(flip) reaches 0.19, about 2 rows
  (`x5_consistency.out`).
- X6, compiler fuzzing crossed with certified robustness: the share of one-number neighbours where the solver's own path
  crashes or deviates (STD leaves crashes out of its denominator) separates high's non-robust T26 from robust T09 and
  T10, where the rating cannot; hand bench AUC 1.000 on 23 rows, post hoc and contaminated; its frozen scorer
  `x6_na_share.py` (md5 02e6e223...), frozen before any blind program existed, failed on the blind writers' logs
  (Appendix E.16) [530].
- A note (n = 1): the public T19 instance breaks an AIME-2025 coincidence, and DeepSeek is non-robust there (a
  memorised-shortcut hypothesis).

**Lane P: spare per-case time** [481]. Speed-gated K 48 to 64 for stand-in cases is worth an estimated +0.06 to +0.10
case on main (interval −0.04 to +0.29) and +0.05 on small (in-sample, template bootstrap); Skywork K 6 +0.01, Olmo K 6
0; no per-configuration switch clears a 2-row bar; the Qwen quick finish is worth +0.21 on main and stays. In the mock
v95's main job has 34 s to spare at 1.6x slower and times out at 2.0x [481]. No change.

**Group 6 of the negative results** (16 October; continues E.12's table; 13 rows):

| Lane | Reading or premise | Bar | Measured | Verdict |
|---|---|---|---|---|
| P | spare per-case time turned into accuracy | a per-configuration switch gains ≥ 2 rows | +0.06 to +0.10 case main, +0.05 small (in-sample) [481] | no change |
| v97 (A) | cheap in-hour rating: four structured arms of gpt-oss low and medium, with and without anchors | S2' Spearman ≥ 0.60; 7B policy ≥ 11 of 12, 63 of 71, 20 of 24 fresh | S2' −0.17, 0.13, −0.27, 0.24; 7B policy 1, 6, 2, 7 of 12 (the entry 9); R4 parsed 16 templates in time (server) [491] | failed; structured prompts worse than free-form (a reversal) |
| L | census of droppable constraints (pre-registered STD precursor) | Spearman ≥ 0.30 and ≥ 10 of 12 7B rows | +0.236; 9 of 12 [482] | killed |
| L | retrieval of similar rated anchors | above the shuffled-pool 95th percentile (0.31) | −0.107 [482] | failed |
| L | many cheap ratings averaged | predicted K-32 Spearman ≥ 0.65, then a policy gain | 0.69, but the 7B policy stays 9 of 12 [482] | no gain |
| Q | STD with a 4B writer (local proxy) | ≥ 20 templates covered | 2 and 0 of 28 [496] | killed |
| T | targeted siblings (v99) | coverage ≥ 6 of 10 templates; ≤ 200 s per Skywork case | design problems found in the build (cost, base-rate bar) [493] | deprioritised |
| W | probe on bare-text states (local proxy) | W1 ≥ 0.60; W2 11 / 63 / 20 | 0.277; 8 / 60 / 18 [499] | failed |
| W-sol | probe on states after the model's own solution (local proxy) | as W | 0.454; 10 / 62 / 19 [506] | failed |
| X1 | fast against slow errors | AUC ≥ 0.75 and residual AUC after difficulty ≥ 0.70 | 0.692; residual 0.288 [508] | failed |
| X2 | item drift across reads | ≥ 10% of templates drift (premise) | 0 of 15 [508] | killed |
| X3 | backward error | placebo ≤ real − 0.10 | 0.116 against 0.032 [508] | void, killed |
| X4 | metamorphic target swap (post hoc) | — | AUC 0.225 [508] | reversed |

**Group 7: pre-registered failures reported in the main text and not tabled above** (5 rows):

| Lane or read | Reading or premise | Bar | Measured | Verdict |
|---|---|---|---|---|
| W-think (local proxy) [507, 516] | probe on states after 2,048 thinking tokens | W1 ≥ 0.60; W2 11 / 63 / 20; W1 above W-sol's 0.454 (dose-response) | 0.304; 9 / 61 / 18 | failed; dose-response refuted |
| R [514, 515] | fresh-regime intercept shift for the stand-in | R1 fresh ≥ 20 of 24 (with R2 to R4) | 19 of 24 (base 18) | failed (R1) |
| v90 (server) [453, 454, 461] | in-hour rating by gpt-oss medium, with a high arm | S2' Spearman ≥ 0.50; S4' policy ≥ 63 of 71 and fresh ≥ 20 of 24 | medium 0.472, 48 of 71, fresh 15 of 24; high 0.637 on 20 parsed, 46 of 71 | failed |
| v94 (server) [462, 470] | the same with calibration anchors, gpt-oss high | S2' ≥ 0.60 | 0.49; 55 of 71; fresh 18 of 24 | failed |
| Probe baseline (server) [388, 394] | L2 logistic probe on prompt states, layer by inner CV | balanced ≥ 0.80, ≥ 0.15 above shuffled, ≥ 0.70 on hard rows | 0.669 (shuffled 0.525; hard 0.570) | not a lead |

### Addendum of 20 October

*Text moved out of the report in draft 27 to keep its main text within the limit (verbatim, from draft 26).*

*From Section 3.4 (still in the report's Key finding 7 and Section 5.1):*

The internal probes did not transfer: 4B hidden states carry
the dormant-condition rating inside a 325-problem pool (nested Spearman 0.346; surface text 0.033, post hoc) but not on
the 28 contest templates (0.277) [499].

*From Section 5.2:*

The organisers' kit probe stores validation balanced accuracies of 0.500 to 0.506 [333].

*From Section 6.3:*

A
rating would cost 300 to 700 s per case against about 190 s available [470].

### Addendum of 20 October (draft 28)

*Text moved out of the report in draft 28 (verbatim, from draft 27).*

*From Section 6.3 (the scores are in the report's Section 5.1 table):*

No model rated like this inside the hour in five pre-registered tries (Spearman with the five-rater mean; Section 5.1):
gpt-oss medium and, in the same read, high, which ranked better but parsed only 20 of 28 templates [461]; high with
calibration anchors [470]; four cheaper structured arms, worse than free-form prompts, the reverse of what we expected
[491]; a text-only rater [477]; and in-hour observables (best difficulty-controlled partial −0.18, bar 0.30) [479].

*From Section 5.2:*

W-sol's policy beat the entry by one row (10 / 62 / 19 against 9 / 61 / 19 on 7B rows / all rows / fresh rows) but
missed its bar (11 / 63 / 20); W (8 / 60 / 18) and W-think (9 / 61 / 18) did not beat it, and W-sol's post hoc best
layer did not replicate [516].

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.14:*

**The v102 result** (server; `miners17/v102_scores.out`) [555]. Case 1: probe 47 s, STD arms A and B 1,651 and 1,502 s;
case 2 re-ran and timed out; the board read 1 of 21, as designed. Arm A's compacting-loop check failed and an
out-of-memory error halved its batch to 52 rows; the default path ran, and the verdict is unaffected. Arm A: S1 (12 of
28; 11 templates lost to failing programs, 5 to the answer ceiling), S2 (0.381 / −0.272), S3 (8 / 60 / 20) and S4b
failed: KILL (under 14 covered). Arm B: S2 passed (0.955 / +0.587); S1 (16 of 28), S3 (10 / 62 / 21), S4a (0.845) and S5
(194 s) failed: KILL (S4a). Probe: W1 0.030 and W2 (fresh 17) failed, W3 (shuffled mean −0.009) and W4 (27.2 s) passed;
nested pool Spearman 0.254; the best single layer vector (post hoc) reaches W1 0.270.

*From Section 5.2:*

**White-box rating probes** (local proxy: Qwen3.5-4B in 4-bit weights on a Mac) [498-500, 506, 507, 516]: a ridge probe
on three fixed layers (mean-pooled and last token), trained on the 325-problem pool rated by two blinded raters each and
tested on the 28 templates, with bars set before any state was computed. It read the bare text (W), the text after the
model's own 768-token solution (W-sol) and after 2,048 thinking tokens (W-think; only 2 of 353 thinking blocks closed);
Section 5.1's table gives the scores: the pre-stated dose-response direction was refuted and all intervals overlap. No
probe's policy reached its bar, and W-sol's post hoc best layer did not replicate [516]. An input-gradient probe (lane
GRAD, local proxy) also failed: AUC 0.250 against a bar of 0.75 [532, 533] (Appendix E.16). **We make no White-Box
claim.** The last internal read, v102's gpt-oss-120b probe, also failed (Section 6.4) [555]; a claim would have needed
it to pass and a probe-off ablation shown on public rows and on at least two board draws per arm, given the board's
noise (Section 2.6).

*From Section 6.3:*

No model rated like this inside the hour in five pre-registered tries (Spearman with the five-rater mean; Section 5.1)
[461, 470, 477, 479, 491]. A computed version, the **solution-transcription differential (STD)** [482], has gpt-oss low
solve the problem and write two programs, a direct search (`brute`) and a transcription of its own steps (`path`), runs
both on 60 one-number re-instantiations (0.6 to 1.6 times each value), and calls a 7B case non-robust iff they disagree
on at least 5% of valid draws. Its pre-registered precursor was killed (Spearman +0.24); Section 6.5 gives its post hoc
bench and blind replication [482]. Entries using STD, v107 and v108, were built and gated on the server read, which
closed them (Section 6.4) [531, 555].

*From Section 6.4:*

v102 (Codabench 993976, main track, research; uploaded 16 October [503]) read STD on the 28 public templates and a ridge
probe on gpt-oss-120b hidden states inside case 1, against bars, frozen scorers and outcome branches written before any
data [501, 502, 511] (Appendix E.14). Frozen scorers' output (`miners17/v102_scores.out`; server, public rows):

- **STD arm A** (gpt-oss low writes): 12 of 28 templates covered (bar 20); AUC 0.381 (bar 0.80). KILL.
- **STD arm B** (medium writes; information arm): 16 of 28 covered and AUC 0.955, but disagreement between two `brute`
  programs reaches AUC 0.845 (sabotage S4a, bar ≤ 0.60): the signal is generic program disagreement (difficulty), not
  path against brute. KILL.
- **The probe**: W1 Spearman 0.030 (bar 0.60); its policy gets 7 of 12 7B rows and 59 of 71 (W2; entry 9 and 61). FAIL.

By the pre-set branches, STD and the white-box route through gpt-oss states are closed for entries (v107 and v108 are
not used). **No white-box component and no STD reading is in any entry.**
