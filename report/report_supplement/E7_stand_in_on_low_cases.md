# Supplement to the technical report: Appendix E.7 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29) at the
end of this file; the report keeps a summary or a pointer.*

### E.7 Why the stand-in fails on low cases while 7B termination works (Section 3.3)

**How many attempts a solve rate needs:** telling a solve rate of 0.95 from 0.90 needs about 60
attempts [118], 0.93 from 0.85 K ≥ 40 [374]; the own-run rules count endings at K 1 to 3.

**Why the stand-in fails on low cases while 7B termination works (a partial explanation).** For gpt-oss low the stand-in
is the examinee: same model, same effort, up to 32 attempts. It is still at chance on low's hard rows (2.0 of 4) [336]
and misses exactly the two rows where low's own success rate sits 0.08 apart (0.88 robust, 0.80 non-robust) [374]. At K
≤ 32 an agreement estimate cannot resolve that gap, so being the examinee does not help when the label sits at the
examinee's own boundary. An "examinee-matched" unanimity reading of gpt-oss rows also failed to replicate, for a
measured reason: unanimity of 8 rejects a problem solved 95% of the time about 34% of the time [132]. Termination for
the 7B models is a coarser signal. Read at K 3 on all 28 public problems in the +Skywork K 3 dress, Skywork's attempts
ended 0 of 3 on 11 problems and 3 of 3 on 9 [379]. It separates problems far from the model's frontier in either
direction, which is where most of Skywork's public non-robust templates lie. It cannot see a problem the examinee solves
reliably and still fails under the organisers' variants; T13 is the public example (Section 8). Whether the hidden cases
sit far from the frontier we cannot test. And [118] shows that a reader weaker than the judged model predicts better
than a stronger one (organisers' data, AUC 0.83 to 0.87 against 0.60 to 0.74). That supports "not stronger than the
examinee", not "the examinee itself"; the cross-reading matrix (Section 3.3) finds the same on public rows.

**Olmo as a reader is weaker** (Section 3.3's table): AUC 0.63 [0.50, 0.83] on its hard rows; most templates were read
at K 1, and one read was clock-cut at 9,689 tokens (`own_q1q2.out`).

**A caution on public AUCs.** Skywork's termination as a reader of every configuration reaches 0.89 on the public rows,
yet scored 12 of 21 when applied to every main case [299] (more transfers in Appendix E.8). A public AUC as a reader is
not evidence about the board.

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.7:*

**How many attempts a solve rate needs:** telling a solve rate of 0.95 from 0.90 needs about 60
attempts [118], 0.93 from 0.85 K ≥ 40 [374]; the own-run rules count endings at K 1 to 3.

For gpt-oss low the stand-in is the examinee, yet it is at chance on low's hard rows (2.0 of 4) [336] and misses exactly
the two rows where low's own success rate sits 0.08 apart (0.88 robust, 0.80 non-robust) [374]: at K ≤ 32 an agreement
estimate cannot resolve that gap. Termination for the 7B models is a coarser signal that separates problems far from the
model's frontier in either direction, where most of Skywork's public non-robust templates lie; it cannot see a problem
the examinee solves reliably and still fails under the organisers' variants (T13). *Full text:
`report_supplement/E7_stand_in_on_low_cases.md`.*
