# Supplement to the technical report: Appendix E.4 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 17 October: the organisers have since given the final's size and budget (30 to 50 questions at about 170 s per
sample [537]; Section 4.5 of the report); statements below that call them unpublished or untestable predate that answer.
Note added 20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29)
at the end of this file; the report keeps a summary or a pointer.*

### E.4 Depth at the final shape (original harness): K 1 against K 3, the stand-in's K, the three guards, expected cases and stress tests (Section 4.1)

**The original-harness planning story** (Section 4.1). *Calls share problems.* Under the original harness, at the final
shape we assumed (as in our dress rehearsals), every call reuses the same ~25 to 30 problems: the stand-in reads each
problem once, in the first call, and serves every configuration; an own run reads only its own call's cases [395]. On
the validation board, by contrast, later calls bring new problems [286]. *The flaw.* The main board has 16 problems
over 7 calls [286]. The final test's size is unpublished [88]; we assumed 25 to 30 problems per call, the size of the
public training file [72, 90, 353]. At +Skywork own, the entry took the largest K ≤ 3 whose predicted batch time fitted
a fixed window (Skywork by 1,200 s into the run, Olmo by 2,100 s) [353]. In the mock, board shapes got K 3 for every own
case, as on the server; the final shape got K 0 for both models at every speed tried, so every case kept the stand-in's
answer. Reading everything at final scale would cost an estimated 5,400 to 8,800 s for the two own runs alone (mock)
[353]. *+Coverage.* The fix changes priorities, not the reading [354]: own runs come before the stand-in's top-up; if
every new problem fits at K 3, all get K 3 with the same order and seeds, so at board scale the entry is +Skywork own;
otherwise each problem gets one attempt, smallest stand-in |margin| first (Appendix F.4), and leftover time upgrades the
first to K 3; unread cases keep the stand-in's answer. One attempt was chosen because finishing counts then looked
all-or-nothing [354], a premise later evidence weakened (Appendix E.5). +Coverage scored 19 with identical per-call
counts, as pre-set [362, 363]; final-scale coverage was still only 12 to 14 of about 28 Skywork cases and 8 to 10 of
about 28 Olmo cases (mock) [367]. *+Fast 7B* is +Coverage plus the fast path (Section 4.4), planning constants fitted on
the speed-test arms, and Olmo planned from Skywork's speed measured in the same run [367]; at server speed the mock
reads 25 to 30 Skywork and 24 to 28 Olmo cases of about 28 [367]. *Dress rehearsals.* The wrapper (Appendix F.7) runs
all 196 public-template cases in harness order and prints per-call time, robust counts and, for the 71 labelled rows
only, answer against label [370]; each dress had a rule set before its data (Appendix C). Own-run coverage of the 56
Skywork and Olmo final-shape cases went from 0 (+Skywork own as built, mock [353]) to 22, 55 and 56 over the first three
dresses (server), with 59 to 61 of the 71 labelled rows right in every dress; +Fast 7B passed its pre-set rule and
replaced +Coverage [375]. *Three guards.* Coverage is not accuracy, and the labelled rows cannot tell coverage variants
apart. After +Fast 7B, three parameter-level guards (+Skywork K 3, +Stand-in depth and +First-call cap) changed how
deeply the entry reads at the final shape; none changes the board shape or has a board score. In short: at the
measured server speed v83 reads every own case at planned depth; if the server is 1.4x slower, it reads about 9 fewer
Skywork problems at K 3 than +Skywork K 3 would (9 against 18 per final test) and the estimated gain becomes a small
loss. A bar set at one speed cannot see a slow-server tail; a mock comparison across speeds did.

**Skywork K 1 against K 3.** The labelled rows cannot tell the coverage variants
apart (all score 60 of 71 [379]), so we tested depth on logs we hold (computed, single reads, [387]): Skywork's rule on
its logged K 3 attempts, Skywork as a reader of all configurations (K 1 averaged over which attempt is kept;
template-bootstrap 95% intervals on the paired difference):

| Rows (Skywork as a reader) | K 3 | K 1 (expected) | K 3 − K 1 | Robust recall K 3 / K 1 | Non-robust recall K 3 / K 1 |
|---|---|---|---|---|---|
| its own 3 rows | 0.667 | 0.667 | 0.000 | 1.00 / 0.83 | 0.00 / 0.33 |
| all 71 rows | 0.859 | 0.798 | +0.061 [−0.03, +0.16] | 0.92 / 0.80 | 0.68 / 0.79 |
| 37 hard rows | 0.784 | 0.739 | +0.045 [−0.08, +0.22] | 0.89 / 0.70 | 0.67 / 0.78 |
| 19 hard robust rows | 0.895 | 0.702 | +0.193 [+0.01, +0.44] | 0.89 / 0.70 | — |

K 3 buys robust recall at some cost in non-robust recall. The +0.19 on hard robust rows is robust recall only, which the
"at least 1 of 3 ends" rule gains by construction. T16, the row that failed +Skywork K 3's bar, has attempts running to
about 8,400 tokens or more, so the cap decides it, not K [387]. For Olmo, K 3 equals K 1 on the 5 templates read at K 3,
too thin to decide; at K 1 it is right on an expected 0.263 of 19 hard robust rows [387].

**The stand-in's K at the final shape.** Before +Stand-in depth, the first call read every problem at K 12 to 13 in the
mock at every speed (+Fast 7B and +Skywork K 3) and at K 12 in the first three server dresses; top-ups reached K 32 for
about five problems per call, so the median was 12 in the four small-model calls [395]. The mock's end-of-run median (32
at 1.0x) hid this. The cause is the planner's reserve for new problems in later calls, which never come when every call
reuses the same problems [395]. In the +Stand-in depth dress, call 1 read all 28 problems at K 16 (the mock had
predicted 18 to 22 [395, 406]); calls 1 to 5 needed no top-ups; the low and medium calls read 16 / 16 / 32 and 16 / 32 /
32 attempts per problem (minimum / median / maximum) [404].

**Stand-in accuracy against K**, from about 80 logged attempts per template (computed, [387]):

| K | Refit at K, leave-one-template-out: all 71 / hard 37 | Shipped coefficients, in-sample: all 71 |
|---|---|---|
| 4 | 0.769 / 0.723 | 0.820 |
| 8 | 0.816 / 0.772 | 0.850 |
| 12 | 0.830 / 0.786 | 0.862 |
| 16 | 0.847 / 0.804 | 0.873 |
| 24 | 0.858 / 0.819 | 0.879 |
| 32 | 0.864 / 0.827 | 0.881 |

With the shipped coefficients, K 4 → 12 gains +0.042 [+0.018, +0.070] and K 12 → 32 gains +0.019 [0.000, +0.040]. Four
independent K 16 reads of the frozen rule scored 0.845 to 0.887 on the 71 rows, a known-answer check on these resamples
[387]. The agreement statistic is unbiased at every K, so the coefficients need no re-centring; only the noise changes
with K. This analysis also corrected an older K curve in [203], which had pooled reads whose logs carried cluster ids
rather than answers and so undercounted agreement [387]. Practical consequence: protect the stand-in's K at final scale;
K 12 → 32 is worth about +0.02 to +0.03.

**The three guards in detail** (original harness).

| Stage | Change | Bar set before the data | Evidence | Expected cases, 1.0x / 1.4x slower (estimate) |
|---|---|---|---|---|
| +Skywork K 3 | every final-scale Skywork problem at K 3 | dress, including Skywork right on ≥ 2 of its 3 rows [376] | dress: K 3 on 28 of 28, but Skywork 1 of 3, so rejected [379]; adopted **post hoc** [387] | reference |
| +Stand-in depth | the planner's time reserve for new problems in later calls halved (0.5 → 0.25; Appendix F.2) | dress, including call-1 K ≥ 16 and Olmo reads ≥ 20 of 28 [395] | dress passed: call 1 K 16 (before: 12), 59/71 [404] | +0.1 to +0.5 / −0.7 to −0.4; 8 Skywork problems unread at 1.4x |
| **+First-call cap (v83, nominated under the original harness)** | call 1's stand-in K ≤ 16 when call 1 has ≥ 10 problems | none: added post hoc after a mock comparison across speeds [406] | mock: every Skywork problem read at every speed, 0 invalid; the +Stand-in depth dress should carry over [404, 406] | +0.1 to +0.5 / −0.4 to −0.1 (ranges 0 to +0.5 / −1.5 to +0.8) |

**+Skywork K 3 was a post hoc reversal.** Its failed row, T16, is decided by the 9,000-token cap, not by K [387]. On
logged attempts K 3 beats K 1 by +0.045 on the 37 hard rows and +0.061 on all 71, and neither 95% interval excludes no
gain; the +0.19 on hard robust rows is robust recall, which the lenient "at least 1 of 3 ends" rule gains by
construction (table above). We adopted it anyway; the board cannot check it.

**+Stand-in depth.** The first three server dresses read call 1 at K 12 because the planner kept that reserve for
later calls that bring no new problems [395]. Halving that reserve raised call 1 to K 16 (mock: 18 to 22) [404, 406] but
dropped low cases from a median of 32 attempts to 16, and about 10 Qwen and DeepSeek cases that probably topped up to K
32 before now stop at 16 [395, 404]; the net is estimated below [426].

**+First-call cap.** Call 1 is planned before any speed is measured: at 1.4x slower, +Stand-in depth's call 1 still took
K 18 to 22, and in one final shape Skywork then read 1 of 25 problems [406]. At measured speed the dress's call 1
already read K 16 [404], so the cap should change nothing there; v83's own dress confirms it (call 1 at K 16 on
all 28 problems, the same own-run coverage) [440]. At 45 or more problems and 1.4x or slower, Skywork's
own run can still be skipped [423] (stress tests at the end of this appendix).

**Expected cases at the final shape** (estimates) [387, 404, 426]. From the final-shape lines at 1.0x and 1.4x of the
three mock files named in Appendix E.3 (three shapes each, divided by 3 per final test), the problems Skywork reads at K
3 were valued at the K 3 against K 1 gain per case on all 71 rows (0.061; interval −0.03 to +0.16), and a call-1
stand-in K of 16 instead of 12 at about +0.017 per case for the Qwen and DeepSeek cases, less the low cases' fall from a
median of 32 attempts to 16 (net +0.14 to +0.48). Against +Skywork K 3 (27.3 Skywork problems at K 3 per final test at
1.0x, 18.3 at 1.4x): +Stand-in depth is worth +0.1 to +0.5 case at measured speed and −0.7 to −0.4 at 1.4x (4.0 problems
at K 3; 8 Skywork problems unread); +First-call cap is worth +0.1 to +0.5 and −0.4 to −0.1 (9.0 at K 3; intervals 0 to
+0.5 and −1.5 to +0.8). Olmo reads are given as counts only (28.0 against 28.0 at 1.0x; 13.0 against 14.0 at 1.4x),
because the ledger has no per-case value for an own read. v83's nomination assumed the speed measured in the real dress
rehearsals [404]. The source lines and arithmetic are repository material ([426] and the files named in Appendix E.3).

**The final shape is an assumption.** The final test "will depend on a new set of problems and variants" [88]; we
planned for 25 to 30 problems per call (above). In a mock stress test of +Fast 7B [380]:

- 45 problems × 7 calls ended at 2,962 s (1.0x) and 3,073 s (1.4x), with 0 invalid predictions; own runs read Skywork 34
  / Olmo 30 cases at 1.0x and 19 / 17 at 1.4x.
- 60 × 7 ended at 2,962 / 2,905 s, with 0 invalid; own runs read 36 / 32 and 21 / 20 cases.
- 1 × 7 ended at 530 / 734 s, with full K 3.

The original-harness nominees were stress-tested later [423]: 1 to 100 problems per call (main x 7, small x 4), 1.0x to
1.6x, and the fast-path check failing; all 96 mock runs gave 0 invalid answers and no fallback and ended by 3,150 s;
seven runs cut one own-run problem at the clock, all at the older default mock speeds, none at the measured speeds [423,
426]. At 45 or more problems and 1.4x or slower, the planner can skip Skywork's own run, because its window falls just
under one minimum batch (main 100 x 7 at 1.4x: 284 s against about 290 s); those cases keep the stand-in reading [423].

**Dress rehearsals in full.**

| Dress rehearsal (server, H1, final shape) | End of run | Skywork own run | Olmo own run | Labelled public rows (in-sample) |
|---|---|---|---|---|
| +Coverage [373] | 2,828 s (mock 3,018) | 13 of 28 read at K 1; 542 s | 9 of 28 at K 1; 663 s | 60/71 |
| +Fast 7B [375] | 2,671 s (mock 3,063) | 28 of 28 (3 at K 3, 25 at K 1); 404 s | 27 of 28 at K 1 (memory-limited batches); 728 s | 60/71 |
| +Skywork K 3 [379] | 3,051 s (mock 3,101 [376]) | 28 of 28 at K 3 in one 84-row batch, 36 ms/step; 324 s | 7 at K 3 + 21 at K 1, three batches; 1,121 s | 60/71 |
| +Stand-in depth [404] | 3,034 s (mock 2,996 [395]) | 28 of 28 at K 3; 324 s | 2 at K 3 + 26 at K 1; 812 s | 59/71 |
| +First-call cap, v83's exact code [440] | 2,916 s (mock 3,020 [435]) | 28 of 28 at K 3; 324 s | 5 at K 3 + 23 at K 1; 1,109 s | 61/71 |

**The slow-server trade.** At 1.4x slower ("1.4x slower" is a mock scenario: every step 1.4 times as long [423]) the
Skywork shortfall at K 3 is worth about −0.6 case (estimate; Olmo reads 13 problems against 14), which cancels or
outweighs the stand-in's +0.1 to +0.5.

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.4:*

Under the original harness, at the final shape we assumed (25 to 30 problems per call, every call reusing them), own-run
coverage of the 56 Skywork and Olmo final-shape cases went from 0 (+Skywork own as built, mock) to 22, 55 and 56 over
the first three dresses (server), with 59 to 61 of the 71 labelled rows right in every dress [353, 373, 375, 379].
Coverage is not accuracy, and the labelled rows cannot tell coverage variants apart. Three parameter-level guards
(+Skywork K 3, +Stand-in depth and +First-call cap) then changed how deeply the entry reads at the final shape; none
changes the board shape or has a board score. At the measured server speed v83 reads every own case at planned depth; if
the server is 1.4x slower, it reads about 9 fewer Skywork problems at K 3 than +Skywork K 3 would (9 against 18 per
final test) and the estimated gain becomes a small loss. A bar set at one speed cannot see a slow-server tail; a mock
comparison across speeds did.

*From Appendix E.4:*

**Skywork K 1 against K 3.** The labelled rows cannot tell the coverage variants apart (all score 60 of 71 [379]), so we
tested depth on logs we hold (computed, single reads, [387]): Skywork's rule on its logged K 3 attempts, Skywork as a
reader of all configurations (K 1 averaged over which attempt is kept; template-bootstrap 95% intervals on the paired
difference).

*From Appendix E.4:*

**+Skywork K 3 was a post hoc reversal.** Its failed row, T16, is decided by the 9,000-token cap, not by K [387]. On
logged attempts K 3 beats K 1 by +0.045 on the 37 hard rows and +0.061 on all 71, and neither 95% interval excludes no
gain; the +0.19 on hard robust rows is robust recall, which the lenient "at least 1 of 3 ends" rule gains by
construction (supplement table). We adopted it anyway; the board cannot check it.
