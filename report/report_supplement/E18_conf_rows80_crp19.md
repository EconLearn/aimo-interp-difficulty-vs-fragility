# Supplement to the technical report: Appendix E.18 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). New in draft 29 of the report (20 October 2026,
UTC). The report keeps a summary of this appendix part; this file holds the part's complete text. Labels: board
(OFFICIAL), public rows (measured on the labelled public rows; single reads unless pooled), server, computed, local
proxy. Section, Appendix and Figure references point to the report; numbers in brackets are entries of our research
ledger; file paths are relative to the report's folder.*

### E.18 20 October: token confidence, the 80-row rescore and six fragility vectors (Sections 2.2, 2.3, 5.1, 5.3)

#### Lane CONF: DeepConf-style token confidence on the stand-in reading [583, 593-607, 614]

**Pre-registration** (`work/miners19/laneConf/PREREG_conf.txt`, written before any confidence value existed [583];
addenda 1, 3 and 4 written before any server data [599, 600]). Token confidence c_t = minus the mean log-probability of
the 20 most probable tokens of the raw next-token distribution (before top-k and top-p); group confidence = mean c_t
over sliding windows of 256 generated tokens; LGC = a trace's lowest group confidence; TAIL = mean c_t over its last
256 tokens. Candidates, each replacing agreement (pair_nat) in `decision.json`'s stand-in models with a
leave-one-template-out refit: A1 pair_nat over the 50% most confident traces by LGC; A2 LGC-weighted pair agreement;
A3 the problem's mean LGC; A4 the problem's mean TAIL. Bars: C1 at least +2 rows over the same read's own pair_nat on
all 71 rows and on the 44 stand-in rows; C2 fresh rows not worse; C3 a within-problem shuffle (A1, A2) or a
within-configuration shuffle (A3, A4) reaches C1's gain in at most 5% of 200 draws; C4 a gain of at least +1 row with
the same sign on a second independent read. A candidate passes only if it passes C1 to C4.

**The recorder** [593, 595, 597-600]. A logits processor listed first sees the raw float32 logits of the full
vocabulary on every call path (`transformers` 5.13 runs custom processors before top-k and top-p; at temperature 1.0
there is no temperature warper). Proof (`proof_recorder*.py` → `.out`): generated tokens byte-identical with the
recorder on and off on all call paths, including the deployed fast path and the multi-text path; recorded values equal
a raw recomputation within 6e-6; two sabotaged recorders detected. An independent pre-upload review of v123r found one
blocker (with at least two failed attempt groups and the K-halving retry, a failed sub-batch's confidences could attach
to the wrong template while logged as ok); v124r (`sub_v141r`) marks a batch done only after a full return and logs any
mismatch as bad; the delta review reproduced 0 wrong traces in 8 failure scenarios (the old build: 98) and gave GO
[597, 599, 600]. A scorer edge case found by the same review (a read with no confidences counted as complete) was fixed
by addendum 4 before any server data [600].

**The run** (Codabench 1004374, main track, research, 20 October; every hidden case answered robust; case 18 timed out
and cases 19 to 21 were skipped when the job clock ran out; board 0.33 by design) [601, 607]. Log
`work/runs/v124r_main_1004374.log` (534,187 bytes, 3,598 confidence lines), scored with the frozen `parse_conf.py` and
`score_conf.py` → `work/miners19/laneConf/score_v124r_1004374.out` [614]. Machinery check: the scorer reproduces lane
G's 60 of 71 on the dress read. Every batch's recorder status was ok; no trace had a missing confidence.

| Read (seed) | Templates | Baseline LOTO, 71 / 44 / fresh 24 | A1 | A2 | A3 | A4 |
|---|---|---|---|---|---|---|
| 94286138 (primary) | 28, complete | 62 / 40 / 19 | −3 / −3 / +0 | +0 / +0 / +0 | −12 / −12 / −3 | −9 / −9 / +0 |
| 681617219 (second, C4) | 28, complete | 57 / 35 / 18 | −1 / −1 / +0 | +0 / +0 / +0 | −7 / −7 / −2 | −3 / −3 / +1 |
| 794012114 (information) | 28, complete | 62 / 40 / 19 | −2 / −2 / −1 | +0 / +0 / +0 | −12 / −12 / −3 | −11 / −11 / −3 |
| 560372929 (information) | 24, partial | 59 / 37 / 18 | −7 / −7 / +0 | +0 / +0 / +0 | −7 / −7 / −2 | −4 / −4 / +1 |

C3 on the primary read: 0 of 200 shuffles reach C1's criterion for every candidate. Verdict: every candidate fails C1
and C4 (A3 also fails C2, 16 of 24 against 19): FAIL [614]. The pre-built entry variants (`sub_v142m`, `sub_v143s`,
built before the data so that a pass could become an entry within hours) stay unused [604, 606].

**The baseline column is that read's own form.** Lane CONF trains each read's rule on that read's own pair_nat (62, 57,
62 of 71). With the training reading of the deployed fit (the fit-time pair16, as `decision.json` was fitted) the same
three reads give 57, 59 and 62 [618]. Either way one fresh read moves the deployed rule's count by up to 5 of 71 rows,
consistent with the noise study (Section 2.6) [585]; 23 of 28 templates' pair_nat differ between the two reads that
both give 62 [614].

**Why confidence fails here.** DeepConf uses confidence to filter or weight the traces of one problem before voting;
our label asks whether a configuration's accuracy survives edited texts of a problem it already solves. Across
problems, mean confidence (A3, A4) tracks difficulty less sharply than agreement, and inside a problem the weights
barely change the agreement (A2 equals the baseline on every read).

#### Lane ROWS80: the organisers' 12 new Skywork rows [617, 618]

**Data.** Hugging Face commit fa8af758 of `train-main-v2` (15 October) adds 12 Skywork-OR1-Math-7B rows on problems
already in the file; 9 are labelled (7 robust; non-robust: T11 and T19), 3 are unlabelled. All 12 match an existing
template (T01, T02, T04 to T11, T19, T21); none is on the three old Skywork templates (T13, T15, T16). The old 82 rows
and their labels are unchanged. We found the update on 20 October [617]. Pre-registration
`work/miners19/rows80/PREREG_rows80.txt` (md5 c0f69a27...) and `ADDENDUM_rows80.txt` (R1 to R9 before any score; R10, a
correction of a known-answer expectation made before any score on the new rows) [618].

**Q1, the decision: Skywork's route.** Rule fixed before scoring: switch the nominees' Skywork route to the stand-in
only if, pooled over the stand-in reads, it beats the own run by at least 2 of the 9 new rows and is not worse on the 3
old rows or on the 2 new non-robust rows, under both stand-in schemes (`decision.json` frozen; refitted
leave-one-template-out on 80 rows).

| Route | New 9 | Old 3 | New non-robust 2 | All 12 |
|---|---|---|---|---|
| Always robust | 7 | 2 | 0 | 9 |
| Own run, v37 read (the read the rule was designed on; decision read) | 9 | 2 | 2 | 11 |
| Own run, dress read (information) | 7 | 1 | 0 | 8 |
| Stand-in, frozen, mean of 8 reads | 7.25 | 2.88 | 1.75 | 10.12 |
| Stand-in, refitted on 80 rows, mean of 8 reads | 7.38 | 2.88 | 1.62 | 10.25 |

Per read the stand-in trails the own run's decision read by 1 to 3 of the 9 new rows. Decision: keep the own run
[618]. Caveat: the two own reads disagree on 3 of 12 rows (T11, T16, T19), and the decision read is right on all
three, so the gap between the routes is within read-to-read noise; with the dress own read the stand-in leads by 0.25
to 0.38 on the new 9, still short of the bar.

**Q2, information: the deployed rules on all 80 rows** (v95's rules: high prior, Skywork own run at least 1 of 3 at
9,000 tokens, Olmo own run at least 2 of 3 at 10,000; `decision.json` refitted leave-one-template-out on 80 rows):

| Read | All 80 | New 9 | Old 71 | Balanced |
|---|---|---|---|---|
| Always robust | 59 | 7 | 52 | 0.500 |
| Dress 987666 | 67 | 7 | 60 | 0.782 |
| r3 + qwen_r2 | 71 | 9 | 62 | 0.862 |
| r4 + qwen_r2 | 71 | 9 | 62 | 0.862 |
| m1 + qwen_m | 70 | 9 | 61 | 0.823 |
| m2 + qwen_m | 71 | 9 | 62 | 0.878 |
| v124r 94286138 | 66 | 7 | 59 | 0.805 |
| v124r 681617219 | 65 | 7 | 58 | 0.766 |
| v124r 794012114 | 69 | 7 | 62 | 0.830 |
| **Pooled (mean of 8)** | **68.75 = 0.859** | 8.00 | 60.75 | 0.826 |

Pooled per configuration: Qwen 10.75 of 12, Skywork 9.50 of 12, Olmo 8.50 of 9, DeepSeek 8.62 of 10, gpt-oss high 13.00
of 15, low 5.12 of 7, medium 13.25 of 15. Caveat: v115, v116, v121 and v122 stop Olmo at 7,200 tokens (Section 4.5);
the held Olmo readings are at 10,000.

**Q3, information: a refit on clear-cut rows only** (max drop at most 0.05 or at least 0.35; 62 of 80 rows),
out-of-fold by template: the deployed rules lose 0.50 rows of 80 pooled (per read −1, −1, −2, +1, −2, +2, 0, −1). No
bar was set and nothing was built [618].

**What it shows.** The Skywork route was chosen with board feedback on 10 to 11 October (Section 2.3); these rows were
published on 15 October and first scored on 20 October. On them the route is not refuted, which is the first
out-of-sample check of a board-chosen route we have; it is also not shown to be better than the stand-in.

#### CRP19: six fragility vectors [609-613, 619]

**Frame** (`work/miners19/crp19/FRAME.md`, written before any lane ran [609]). Our deployed readings measure difficulty;
the label is fragility among solved problems, where the solve rate says little (Section 3.1). The question: is there a
label-free quantity, computable inside the per-case budget, that separates fragile from robust solved problems beyond
difficulty? Banned default answers: more samples or agreement, length or finishing, LLM ratings of robustness, probes
on short generations, re-solved siblings, and token confidence (then in test).

**Lane X: three cross-domain features** (`work/miners19/crp19/X/`; `PREREG_coincidence.txt` and `PREREG_deadinput.txt`
before computing; `coincidence.py` → `coincidence.out`, `deadinput.py` → `deadinput.out`) [610]. Bars: Spearman with
the raters' mean LATENT over the rated pool at least +0.20 (permutation p at most 0.01), a partial Spearman controlling
problem size at least +0.15, and, for the two problem-text features, a within-configuration AUC of at least 0.70 on the
71 rows above difficulty's; sabotage arms must lose.

| Feature | Pool n | Spearman with LATENT | Partial | Within-configuration AUC, 71 rows | Verdict |
|---|---|---|---|---|---|
| Accidental numeric identities (KD) | 279 | +0.012 | +0.011 | 0.597 (difficulty 0.935) | KILL |
| Shallow wrong formulas that hit the answer (EMx) | 263 | −0.099 | −0.097 | 0.471 | KILL |
| Given numbers never reused in gpt-oss low's traces (DEAD) | 208 | +0.008 | −0.002 | 0.616 (information only) | KILL (sabotage did not lose) |

**Key headroom** (post hoc, information only; `keyscored.py` → `keyscored.out`, `INFO_keyscored.md`) [611]. Within
configuration on all 71 rows the deployed reading (dress read, K 32) reaches AUC 0.929, agreement over 80 pooled attempts
0.948, the modal share 0.942, and accuracy scored against the public key 0.935. The six templates where gpt-oss low's
mode disagrees with the key (T20, T22 to T25, T27) are already read as hard. Leave-one-template-out the key-scored
reading gains at most 2 rows with 80 pooled attempts and none at one 32-attempt read pair, where the key and the plain
mode tie and read-to-read noise (58 against 60) is larger. Three zero-cost key proxies (the mode of slow attempts, of
the longest third, of answers confirmed by a second read) match the key on 0.79 to 0.86 of templates and change no row
at K 32.

**Premise reliance (V1) and instance-binding depth (V2)** (`work/miners19/crp19/premise/`; `PREREG_premise.txt` before
any score; local Qwen3.5-4B in 4-bit weights; 34 rated pool problems with a correct Qwen3.5-4B write-up; 1,212
teacher-forced passes) [613, 619]. V1: per stated condition, the drop in the write-up's log-likelihood when the
condition is deleted (copied tokens excluded); primary aggregate S_min = min over conditions / median. V2: the depth at
which a number swap starts to lower the write-up's likelihood. Bars: Spearman with LATENT at most −0.30 and a partial
(difficulty) at most −0.25; sabotage arms must lose.

| Arm | n | Spearman with LATENT | Partial | Result |
|---|---|---|---|---|
| V1 S_min, own write-up | 11 defined | +0.150 | +0.349 | FAIL (wrong sign) |
| V1 sabotage: mismatched write-up | 21 | −0.420 | −0.465 | did not lose |
| V1 sabotage: function-word deletion | 20 | −0.392 | −0.276 | did not lose |
| V1 whole write-up (secondary) | 24 | −0.104 | +0.105 | FAIL |
| V2 depth, own write-up | 27 | −0.038 | −0.036 | FAIL |

**The measured cause.** Deleting the whole problem changes the write-up's log-likelihood by −0.315 nats per token over
its first quarter (where it restates the problem) and by −0.002 over the rest (median over problems; positive on 15 of
34). Once the write-up has restated the problem, the scorer no longer reads the problem text, so deleting one condition
cannot show whether the solution used it; single deletions move the scored tokens by a median 0.003 nats per token,
function-word deletions by 0.0016 [619]. Both vectors are closed for a write-up that restates the problem.

**Tally.** Six vectors tested (lane X three, key proxies, V1, V2), none survives; five failed a pre-set bar and the key
proxies were post hoc (Appendix D, group 13). With lane CONF and the key-headroom check, this supports Section 5.3: the
deployed difficulty reading is near its own ceiling (within-configuration AUC 0.93), and the remaining errors are rows
where fragility departs from difficulty [611, 619].

#### Seed variants v121 and v122 [588, 601, 608]

v121 (`sub_v138m`) and v122 (`sub_v139s`) are v115 and v116 with every reading's seed shifted by 271828 (zip md5s in
Section 10). Board runs on 20 October (OFFICIAL board, one draw each): v121 15 of 21 (v115: 15), v122 9 of 14 (v116:
9), every case answered, none invalid [608]. Equal totals are what the noise study expects (one total moves by about
1.3 and 1.0 cases; Section 2.6); the per-case calls were not read.
