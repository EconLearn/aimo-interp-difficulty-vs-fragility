# Supplement to the technical report: Appendix A.2 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October (draft 28): as in the report's draft 28, the comparison with other teams, a model of another team's
uploads and two verbatim ledger quotes are replaced by neutral wording; the counts and tables are unchanged.*

### A.2 Own-run answer changes (validation-set inference; H1)

**How board counts guided the order of changes** (Section 4.1). From 10 October we iterated genuine method variants
against the board, which the contest site invites ("Iterate on the leaderboard until the final deadline"), with a
public-row reason written before each upload,
no constant answers per configuration, no per-case probes, and the nominee chosen separately [322, 333].
Per-configuration counts with the board arithmetic located a run's errors by configuration before the next change was
chosen [329, 338, 339, 348]. The order, and when to stop, used validation-set information. Appendix A.1 lists all 78
board uploads from 4 to 14 October (86 of the 300 allowed were used [436]) and the nine from 15 to 16 October, two of
them not made by us [473, 503]. Right / wrong deductions from the board arithmetic are validation-set inference.

**Worked example of the board arithmetic**, the +High prior run [338]: 11 robust
calls and a score of 16 give 16 = 2 × right + 11 − 11, so 8 were right and 3 wrong, 10 − 8 = 2 robust cases were missed,
and 3 + 2 = 5 errors leave 21 − 5 = 16.

This tally uses the board arithmetic and per-call counts. It infers hidden-label information at the level of counts per
change, and is shown here only to size the evidence.

| Board | Change | Answers changed | Right | Wrong | Basis | Ledger |
|---|---|---|---|---|---|---|
| main | +Olmo own against +High prior | 1 | 1 | 0 | previous stage's run: same seeds, identical counts in every other configuration | [342] |
| main | +Skywork own against +Olmo own | 2 | 2 | 0 | as above | [350] |
| small | Olmo own run against Skywork rule on all cases | 2 | 1 | 1 | previous variant's run | [341] |
| small | small recipe (Skywork 2 + Olmo 1 changes against the stand-in in the same run) | 3 | not determinable | not determinable | the stand-in's in-run score is not observed | [359] |

- Main board: 3 of 3 right; one-sided exact sign test p = 0.125.
- Both boards, where determinable: 4 of 5 right; p = 0.19 (computed: 6 / 32).
- **Both p-values are best cases.** The coin-flip null assumes each change had even odds of being right without label
  information. These changes were aimed using board counts: per-configuration counts had located the run's errors
  before Olmo's and Skywork's own runs were chosen [338, 339, 348] (Section 4.1). The
  only untargeted transfer, the same recipe moved unchanged to the small board, gave no gain (9, level) [352].
- The changes compare the own run with the gpt-oss stand-in. The one board comparison with the other 7B model is the
  small-board row above (Olmo's own run against Skywork's reading: 1 right, 1 wrong) [341]; Section 3.3.
- Caveat: the right / wrong split uses the previous stage's run as the baseline, not same-run arithmetic. It assumes the
  other readings repeated, which held in the per-configuration counts but which [329b] warns against in general.
- The fresh-seed reruns [393] are not tallied: they redraw the same rules rather than change one. Their same-run
  arithmetic: 11 robust calls with 9 right (seed offset 7777), 9 with 7 right (424242). Their per-call counts:

  | Rerun | Per-call robust counts that moved against +Fast 7B | Robust calls | Main board |
  |---|---|---|---|
  | seed offset 7777 (Codabench 981204) | Skywork 2 of 3 (one problem's own attempts ended 1 of 3 instead of 0 of 3); all others unchanged | 11 | 18 |
  | seed offset 424242 (981207) | DeepSeek 0 of 3 (was 1), low 2 of 5 (was 1), medium 1 of 3 (was 2); own-run patterns unchanged | 9 | 16 |

- **The recipe's draws.** The 19 is the +Skywork own draw, reused by its same-seed
  rerun and by +Coverage. On the main board most of the swing came from the stand-in (DeepSeek, low and medium calls
  moved); Skywork's own-run pattern moved once (one problem, 0 → 1 of 3 attempts ended) and Olmo's never (2 and 0 of 3
  on its two problems in every logged main run [342, 345, 369, 393]).
- **The medium draw.** Medium came out 2 of 3 robust in the same-seed main runs of
  11 October and two other runs, and 1 of 3 in seven others; with 1 of 3, +Olmo own would have read 16, not 17 [200,
  203, 282, 329, 330, 334, 338, 342, 393] (ledger [342] says 15, which a one-call change cannot produce).
- **A selection model of the board.** A binomial model fits 0.825 per upload (90% interval 0.725 to 0.900) to the
  recipe's four distinct draws on the same 21 cases [422]; treating the draws as independent, the interval understates
  the uncertainty for new cases, and our best draw, 19, also contains ordinary best-of-n luck.
- Skywork's reading of every main case (Section 3.3, Appendix E.11): 9 robust calls, 5 right [299].
