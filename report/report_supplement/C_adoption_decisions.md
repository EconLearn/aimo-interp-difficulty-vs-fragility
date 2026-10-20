# Supplement to the technical report: Appendix C in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 17 October: the decisions on v111 to v114 (Section 4.5 of the report) are in the report's Appendix C only. Note
added 17 October, later: below, "the final files" are the files scored on 15 and 16 October (v95, v96); the nominees for
the final are v111 to v114 (Section 4.5 of the report). Note added 18 October: v102's log, unread below, was read on 18
October [555]: STD and the gpt-oss probe failed, so v107 / v108 were rejected (the report's Section 6.4 and Appendix
C).*

## Appendix C. Adoption decisions and their bars

| Decision | Bar, written before the data | Measured | Outcome |
|---|---|---|---|
| fast 7B decode path [361, 365] | fast ≤ 0.67 × default (Skywork), ≤ 0.80 × (Olmo); checks pass; no fallback | 0.42, 0.48; checks passed (server) | adopted |
| +Coverage at board scale (H1) [354, 362] | 19 = board behaviour unchanged | 19, identical counts | adopted |
| +Fast 7B at board scale (H1) [368, 369] | 19 expected; check lines passed; own batches on the fast path | 17 with identical per-configuration counts; checks passed | +Coverage kept until the dress rehearsal |
| +Fast 7B replaces +Coverage (H1) [370, 375] | dress ends inside 3,400 s with no fallback and both fast checks passed; not worse by more than 1 of the 12 labelled Skywork and Olmo rows or 2 of all 71 | 2,671 s; 9 against 8 of 12; 60 against 60; it differed from +Coverage only on Olmo (8 against 7 of 9) and medium (13 against 14 of 15, a stand-in draw) [373, 375] | adopted |
| +Skywork K 3 replaces +Fast 7B (H1) [376, 379, 387] | end ≤ 3,400 s, no fallback, at least 25 of 28 Skywork problems at K 3 in one or two batches, no out-of-memory, Skywork right on at least 2 of its 3 labelled rows (T16 should turn right), and overall not worse than 60 of 71 by more than 2 [376] | the dress passed all but the Skywork-row condition (3,051 s; 28 of 28 at K 3 in one batch; 60 of 71): T16 had 0 of 3 attempts ending inside 9,000 tokens [379] | rejected by the pre-set rule; **adopted post hoc** on the K 1 against K 3 test (Section 4.1; Appendix E.4) |
| medium own agreement [372, 373] | beat the stand-in by ≥ 2 of 15 medium rows | stand-in 14 of 15 | rejected |
| DeepSeek own run [346, 348] | rule right on ≥ 5 of 6 public rows | 4 of 6 | rejected |
| fresh-seed reruns [384, 393] | none: a measurement, not a selection | 18 and 16 | never nominated; reported as the recipe's distribution (Section 4.1) |
| +Stand-in depth replaces +Skywork K 3 (H1) [395, 396, 404] | dress: first-call K ≥ 16, end ≤ 3,300 s, no fallback, both fast checks pass, Skywork K 3 on ≥ 25 of 28, Olmo reads ≥ 20 of 28, labelled rows not worse than 60/71 by > 2 | first-call K 16; 3,034 s; no fallback; checks passed; Skywork K 3 on 28; Olmo read 28; 59 of 71 (server) | **adopted** (its small twin replaced the small candidate); +Skywork K 3 became the first fallback (second since +First-call cap). Expected size about +0.1 to +0.5 case at measured speed and about −0.7 to −0.4 at 1.4x slower (estimates; Section 4.1, Appendix E.4) |
| +First-call cap replaces +Stand-in depth (H1) [406] | none written before the data: a guard adopted after a mock comparison at three speeds found +Stand-in depth's slow-server tail; at measured speed the +Stand-in depth dress is expected to carry over, since its call 1 already read K 16 [404] | mock, 39 shapes per track, 0 invalid, final shapes end 2,854 to 3,050 s: Skywork reads every problem at every speed (1.4x: 8 to 10 at K 3; +Stand-in depth 1 of 25 in one shape); Olmo 8 to 16 at 1.4x (+Stand-in depth 6 to 16, +Skywork K 3 10 to 16), 10 to 16 at 1.6x for the 7B models (+Stand-in depth 7 to 16, +Skywork K 3 16 to 22); call 1 K 16 at every speed; board shapes identical | **adopted** (with its small twin); +Stand-in depth is the first fallback, then +Skywork K 3, +Fast 7B. Expected size about +0.1 to +0.5 case at measured speed and about −0.4 to −0.1 at 1.4x slower (estimates; Section 4.1, Appendix E.4) |
| per-case rebuild (v95 / v96) replaces v83 / v84 (H2) [464, 466, 471] | none written before the data: v83 does not fit the per-case harness (mock: 6 of 21 main cases lost at measured speed, 11 at 1.4x slower [466]) | mock 21 of 21 and 14 of 14 cases valid [466]; board 16 of 21 and 10 of 14, every case complete [471] | **adopted** as the nominees for the per-case harness; v83 / v84 stay the nominees for the original harness |
| change v95's board-chosen parts before the final (generalisation audit) [509] | none written before the data: an audit | public rows: high prior +1 to +2 rows per read, Olmo 0 to +1, Skywork 0 to −2; board +3 inside the coin-flip selection range; swap worth about 0 ± 1 case per 21 (guess) | **no change** (Section 2) |
| fresh-regime recalibration of the stand-in (lane R) [514, 515] | R1 fresh rows ≥ 20 of 24; R2 exposed rows lose ≤ 1; R3 random-template sabotage ≤ 0.05; R4 sign | R1 19 of 24 (fail; base 18); R2 to R4 pass | **no change** (Section 2.4) |
| prior-shift (label-shift) correction of the stand-in, lane S2 [525, 526] | L1 ≥ +2 row-equivalents leave-one-template-out at a 50/50 and at the board's mix; L2 fresh ≥ 18 of 24; L3 the reversed sign lowers accuracy | L1 −1.04 (board mix −0.64); L2 19; L3 −6.11; premise wrong (`decision.json` already class-balanced) | **no change**; no v106 built (Section 2.4; Appendix E.16) |
| v104 replaces v95 (H2) [505, 510] | built only if its answers are identical at 21 cases (set in the round's frame [505]); then one board run [510] | identical on 2,856 of 2,856 main runs (1,632 small, 84 original-harness); about 10% faster; board run not yet made; v105, its small twin, likewise [517] | pending one board run |
| STD entries v107 / v108 (v100 / v101 with v104's skip; same answers [531]) replace v95 / v96 (H2) [482, 494, 511] | the v102 read passes S1 to S5 (S5 at ≤ 190 s), then board ≥ 16 of 21 and ≥ 10 of 14 | pending: log not read at writing [518]; the bench's blind replication gave 9, 11 and 10 of 12 7B rows, no writer passing the frozen scorer (Section 6.5) [521, 523, 528] | pending |
| white-box probe on Qwen3.5-4B states as a lead (local proxy) [498-500, 506, 507, 516] | W1 ≥ 0.60; W2 ≥ 11 of 12, ≥ 63 of 71, fresh ≥ 20 of 24; W3 ≤ 0.30; W4 time | bare text W1 0.277, W2 8 / 60 / 18; after the own solution 0.454, 10 / 62 / 19; after 2,048 thinking tokens 0.304, 9 / 61 / 18 | not a lead (Section 5.2) |
| input-gradient share on Qwen3.5-4B (lane GRAD) as a lead (local proxy) [532, 533] | G1 AUC ≥ 0.75 on Qwen's 12 rows; G2 the same after removing difficulty ≥ 0.70; G3 shuffled token classes ≤ 0.60 | G1 0.250 (reversed); G2 0.219; G3 0.499 | not a lead (Section 5.2) |
| internal-state probe as a lead [388, 394] | balanced accuracy ≥ 0.80, ≥ 0.15 above its shuffled control, ≥ 0.70 on hard rows | best inner-CV probe 0.669 (shuffled 0.525, hard 0.570); post hoc layers 0.64 to 0.73 | not a lead; reported as a baseline (Section 5.2) |

**Chronology of the main candidate** (from +Fast 7B on, the small candidate followed each step as the same code plus the
small marker; versions and md5s in Appendix B):

- **11 October.** +High prior, +Olmo own and +Skywork own were scored in turn [338, 342, 350]; +Coverage replaced
  +Skywork own at the same board score, with more final-scale reading [362].
- **12 October.** +Fast 7B replaced +Coverage after its dress passed the pre-set rule [375]. +Skywork K 3 was rejected
  by its dress bar [379]; at 21:53 UTC the K 1 against K 3 analysis reversed that post hoc, and +Skywork K 3 replaced
  +Fast 7B as the main candidate [387].
- **13 October.** +Stand-in depth replaced +Skywork K 3 at 19:22 UTC, after its dress passed a bar set before the data
  [404]; at 19:38 UTC +First-call cap replaced +Stand-in depth, on a mock comparison and with no bar set before the data
  [406].
- So the nominee changed three times in about 22 hours (ledger times; computed). Its exact code then ran once in a
  server dress rehearsal on 14-15 October (61 of 71 labelled rows; end 2,916 s) [440].
- **15-16 October.** The harness changed to one process per case [464]; v95 and v96, v83's rules rebuilt per case, were
  uploaded as entries and scored 16 of 21 and 10 of 14 with every case complete; they are the final files (Section 10)
  [466, 469, 471].
- **16 October (later).** A generalisation audit found no reason to change v95 / v96 [509]; v104 was built as an
  answer-identical faster variant [510]; the STD candidates v100 / v101 wait on the v102 read [494, 495, 503].
- **16 to 17 October.** W-think failed its bars [516]; lane R failed and changed nothing [515]; v105 was built [517];
  v102's log could not be read (Codabench logged out) [518].
- **17 October.** Three blind STD writers did not reproduce the contaminated bench (9, 11 and 10 of 12 7B rows) [521,
  523, 528]; a prior-shift correction of the stand-in failed and changed nothing [525, 526]; v102's log was still unread
  [525] (Appendix E.16).
- **17 October (later).** X6 failed when read blind, which closes its planned override for gpt-oss high [530]; v107 /
  v108 replaced v100 / v101 as the gated STD entries, with the same answers [531]; lane GRAD failed [532, 533]; v102's
  log was still unread.
