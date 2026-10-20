# Supplement to the technical report: Section 4.1 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report now keeps a short summary of Section
4.1; this file holds the section's complete text as of 17 October, unchanged. Section, Appendix and Figure references
point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's
folder. Note added 20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October
(draft 29) at the end of this file; the report keeps a summary or a pointer.*

### 4.1 The original harness, in brief (H1)

Until 11 October the entry read every case through the stand-in; eleven such variants scored 13 to 16 of 21, mean 14.9
(Appendix A.1). From 10 October we iterated method variants against the board, each with a public-row reason written
before upload; per-configuration counts and the board arithmetic then guided the next change [322, 329, 333, 338, 339,
348], which Appendix A.2 discloses. +High prior scored 16 [338], +Olmo own 17 [342] and +Skywork own 19, with a
same-seed rerun at 19 [350, 352], level with the board's best on 11 October [352]. Three changed answers carry the gain
over +High prior (sign test p = 0.125, a best case, because the changes were aimed); the same recipe gained nothing on
the small board [352]. Fresh-seed reruns scored 18 and 16; the recipe's four distinct draws average 17.5 (SD 1.3) [393],
and before they were scored we wrote that a 16 would mean the same-seed runs overstated the recipe [427]. Planning for
the assumed final scale [353, 354] (fast decode paths, Section 4.4; five server dress rehearsals; three guards)
produced v83, which was never scored (Appendices B, C, E.3, E.4). Appendix A summarises every board upload (all 87 in
`board_uploads_v17.csv`); the 19 is the best of 26 scored main runs to 14 October [333, 369, 419].

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Section 4.1:*

Until 11 October the entry read every case through the stand-in; eleven such variants scored 13 to 16 of 21, mean 14.9
(Appendix A.1). From 10 October we iterated method variants against the board; per-configuration counts and the board
arithmetic guided each next change, which Appendix A.2 discloses [322, 329, 333, 338, 339, 348]. +High prior scored 16
[338], +Olmo own 17 [342] and +Skywork own 19, with a same-seed rerun at 19 [350, 352]. The same recipe gained nothing
on the small board [352]. Fresh-seed reruns scored 18 and 16, and the recipe's four distinct draws average 17.5 (SD 1.3)
[393, 427]. v83, planned for the assumed final scale [353, 354], was never scored (Appendices B, C, E.3, E.4). Full
text: `report_supplement/S41_original_harness_H1.md`.
