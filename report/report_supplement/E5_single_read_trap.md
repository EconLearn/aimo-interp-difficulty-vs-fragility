# Supplement to the technical report: Appendix E.5 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29) at the
end of this file; the report keeps a summary or a pointer.*

### E.5 The single-read trap and reruns (Sections 4.1 and 9)

Five readings looked like large gains on one read and fell back on the next (public rows):

| Reading | First read | Next read (same bar) | Ledger |
|---|---|---|---|
| gpt-oss medium modal share + quick finish + strength | 0.90 / 0.93 | 0.79 / 0.81 | [93, 112] |
| low effort answers within 2,000 tokens (small rows, AUC) | 0.969 | 0.828 | [116, 117] |
| examinee-matched unanimity at the configuration's own effort (71 rows; gpt-oss rows in brackets) | 0.887 / 0.906 (33 of 37) | 0.789 / 0.822 (26 of 37) | [120, 132] |
| two-reader guard band with fallback | 0.873 / 0.863 | 0.803 / 0.815 on an older read, budget-confounded and so not a clean refutation [119]; hybrid 0.803 on a fresh read at the right budget [132] | [119, 132] |
| medium reading as a feature for medium / high rows | above the stand-in (the figure is in a lane output, not the ledger) | 0.817 / 0.842 against the stand-in's 0.845 / 0.844 | [134] |

None of these was tuned on the second read; each failed a bar written before it. The forced-answer certificate is a
sixth case (two right flips post hoc, then 0 right and 5 wrong); it is listed once, in Appendix E.6.3.

Read-to-read noise: four independent K 8 reads of the frozen stand-in rule scored 0.746, 0.817, 0.887 and 0.831 on the
71 rows (computed, `standin_k.out`); verifying a +0.03 gain needs 410 to 1,028 independent labelled rows [195]. Two
reasonable definitions of one pooled medium reading gave 0.859 and 0.789 on the same data [112]; two reads with the same
decoder differ in AUC by a median of 0.09 and a 95th percentile of 0.24 at K 8 [185].

- **Same-day reruns of one build reproduced every count.** Two copies of one file uploaded by mistake gave identical
  counts in every call [307]. +Skywork own, its same-seed rerun and +Coverage (identical at board scale) gave the same
  per-call counts and 19, 19, 19 [363]. +Olmo own and its rerun gave 17 and 17 [345]. Two small builds on 12 October
  were identical (8 and 8) [369].
- **Cross-day reruns of one file differed** [386]. The stand-in nominee scored 14 on 6 October and its byte-identical
  copy 15 on 10 October (Skywork-case robust calls 2 of 3 against 3 of 3; 7 against 8 robust calls in all). The medium
  stand-in reading came out 1 of 3 robust on 10 October and 2 of 3 on 11 October.
- **Builds that read identically can diverge across days.** For +Fast 7B's 17 against +Coverage's 19 (Section 4.1), the
  log shows a base reading moved (the parity of Skywork's "answers changed" count, 2 then 1), but the own run overrides
  those calls, the fast path also changed the 7B numerics, and the log does not show which configuration's call swapped
  [369]. On the small board, the recipe as at +Skywork own and as at +Coverage
  differed in the stand-in reading and in Olmo's finishing counts (9 and 8) [366].
- **Olmo's own run on the small board:** on the same three problems it gave a
  different pattern in each of three runs: 1 of 3 problems robust [341]; 3 of 3, with attempts ended {2 of 3: 2, 3 of 3:
  1} [359]; 2 of 3, {1 of 3: 1, 3 of 3: 2} [366]. On the main board its pattern never moved (Appendix A.2).

So the repeated 19 was a coinciding draw of correlated runs, not a replication of the reading's noise [369]. One main
case is 0.048 of accuracy. To compare two builds, compare per-call counts from the same run before reading anything into
the score.

**A recipe is a distribution of board scores**: a two-point difference between builds can be one swapped call; +Fast
7B's 17 came from one robust call landing on a different case (a swap costs two points) [369]. **Labelled public rows
saturate.** Three entries that differ in final-scale coverage all score 60 of 71 [379], and the 12 own-model rows can
show a large loss, never a gain [370]; once the stand-in was fitted on these rows, they stopped being a test set for
anything sharing its readings.

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.5:*

None of these was tuned on the second read; each failed a bar written before it. The forced-answer certificate is a
sixth case (two right flips post hoc, then 0 right and 5 wrong); it is listed once, in Appendix E.6.3.
