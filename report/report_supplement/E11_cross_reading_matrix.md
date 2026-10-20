# Supplement to the technical report: Appendix E.11 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29) at the
end of this file; the report keeps a summary or a pointer.*

### E.11 The cross-reading matrix in full (Section 3.3)

Each 7B rule reads the other 7B model's labelled rows from the logs and conventions
of Section 3.3 (Skywork K 3 on all 28 templates; Olmo K 3 on 5 templates and K 1 on 13 more). Only the 39 rows on the 18
templates Olmo read are kept, so every reader is scored on the same rows. The stand-in is the shipped rule on its
fit-time reading (in-sample) and the same logistic refitted leave-one-template-out. Cells: rows right / rows read (AUC
of the continuous score: share of attempts ended; −z for the stand-in). Computed (`work/miners12/review/xread.py` →
`xread.out`, [399]); single reads; both 7B thresholds were chosen after seeing public rows [269, 339].

| Reader (public rows) | Skywork's rows (3; 1 NR) | Olmo's rows (5 of 9; 2 NR) | Qwen + DeepSeek rows (11; 6 NR) | All small-model rows (19; 9 NR) | gpt-oss rows (20; 6 NR) | Hard region (34; 15 NR) | All common rows (39; 15 NR) |
|---|---|---|---|---|---|---|---|
| Skywork's own-run rule | **2/3** (0.75) | 3/5 (0.83) | 9/11 (0.83) | 14/19 (0.81) | 17/20 (0.88) | 26/34 (0.81) | 31/39 (0.83) |
| Olmo's own-run rule | 2/3 (0.75) | **5/5** (1.00) | 7/11 (0.60) | 14/19 (0.75) | 11/20 (0.68) | 20/34 (0.63) | 25/39 (0.71) |
| Stand-in, shipped rule, in-sample | 2/3 (0.50) | 5/5 (1.00) | 11/11 (1.00) | 18/19 (0.93) | 16/20 (0.96) | 29/34 (0.93) | 34/39 (0.95) |
| Stand-in, refit leave-one-template-out | 2/3 (0.50) | 4/5 (1.00) | 11/11 (1.00) | 17/19 (0.92) | 15/20 (0.93) | 27/34 (0.88) | 32/39 (0.91) |
| Always robust | 2/3 | 3/5 | 5/11 | 10/19 | 14/20 | 19/34 | 24/39 |

Figure 2 draws the Skywork, Olmo, Qwen + DeepSeek, gpt-oss and all-common columns. The two 7B rules' other small-model
rows sum to Skywork 3/5 + 9/11 = 12/16 and Olmo 2/3 + 7/11 = 9/14 (computed). On gpt-oss medium and high rows Olmo's
rule minus Skywork's is −0.375 each (95% interval −0.75 to −0.12); on small-model rows they tie (14 of 19 each).

**The examinee-specific contrast.** Write a_r(X) for the share of configuration X's
rows that reader r gets right (S = Skywork, O = Olmo, QD = the 11 Qwen and DeepSeek rows). For reader r against the
other reader r′,

  Δ_r = [a_r(own rows of r) − a_r′(own rows of r)] − [a_r(QD) − a_r′(QD)],  and the contrast is C = (Δ_S + Δ_O) / 2.

From the table, Δ_S = (2/3 − 2/3) − (9/11 − 7/11) = −0.18 (template-bootstrap 95% interval −1.23 to +0.75), Δ_O = (5/5 −
3/5) − (7/11 − 9/11) = +0.58 (0.00 to +1.25) and C = +0.20 (−0.25 to +0.75).

- **Per-template reasons.** On Skywork's 3 rows both 7B rules score 2 of 3: Skywork misses T13 (non-robust for all four
  small models; Olmo's call is right on each), Olmo misses T16 (borderline for Skywork too [389]). On Olmo's 5 read rows
  Olmo scores 5, Skywork 3; the difference is T13 and T10, where Olmo's call is equally right on the other small models'
  T13 rows and on low's T10 row, and wrong on medium's and high's T10 rows.
- **Why Olmo's own contrast is large.** Olmo alone gives +0.58 (0.00 to +1.25), resting on two templates and on Olmo
  having no row on T01 or T02, hard robust templates where its strict call is wrong for Qwen and DeepSeek; Skywork alone
  −0.18 (−1.23 to +0.75). The 7B readers disagree on 5 templates.
- **The board rarely compares the right pair.** The own runs beat the stand-in on three main-board answers (board
  arithmetic; Section 4.1). The one board test of own model against the other 7B model, Olmo's own run against Skywork's
  reading on the small-board Olmo cases, changed two answers, one right and one wrong (board arithmetic, two runs)
  [341]. Skywork's reading of other configurations' cases did worse than the stand-in (every case 12 of 21 [299];
  gpt-oss cases 13 [304]).
- **Public rows and board disagree.** Public rows even rank the stand-in above both 7B readers on small-model rows, 18
  or 17 of 19 (table above).

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.11:*

| Reader (public rows) | Skywork's rows (3; 1 NR) | Olmo's rows (5 of 9; 2 NR) | Qwen + DeepSeek rows (11; 6 NR) | All small-model rows (19; 9 NR) | gpt-oss rows (20; 6 NR) | Hard region (34; 15 NR) | All common rows (39; 15 NR) |
|---|---|---|---|---|---|---|---|
| Skywork's own-run rule | **2/3** (0.75) | 3/5 (0.83) | 9/11 (0.83) | 14/19 (0.81) | 17/20 (0.88) | 26/34 (0.81) | 31/39 (0.83) |
| Olmo's own-run rule | 2/3 (0.75) | **5/5** (1.00) | 7/11 (0.60) | 14/19 (0.75) | 11/20 (0.68) | 20/34 (0.63) | 25/39 (0.71) |
| Stand-in, shipped rule, in-sample | 2/3 (0.50) | 5/5 (1.00) | 11/11 (1.00) | 18/19 (0.93) | 16/20 (0.96) | 29/34 (0.93) | 34/39 (0.95) |
| Stand-in, refit leave-one-template-out | 2/3 (0.50) | 4/5 (1.00) | 11/11 (1.00) | 17/19 (0.92) | 15/20 (0.93) | 27/34 (0.88) | 32/39 (0.91) |
| Always robust | 2/3 | 3/5 | 5/11 | 10/19 | 14/20 | 19/34 | 24/39 |

Figure 2 draws the Skywork, Olmo, Qwen + DeepSeek, gpt-oss and all-common columns.

**The examinee-specific contrast.** Write a_r(X) for the share of configuration X's
rows that reader r gets right (S = Skywork, O = Olmo, QD = the 11 Qwen and DeepSeek rows). For reader r against the
other reader r′,

  Δ_r = [a_r(own rows of r) − a_r′(own rows of r)] − [a_r(QD) − a_r′(QD)],  and the contrast is C = (Δ_S + Δ_O) / 2.

From the table, Δ_S = (2/3 − 2/3) − (9/11 − 7/11) = −0.18 (template-bootstrap 95% interval −1.23 to +0.75), Δ_O = (5/5 −
3/5) − (7/11 − 9/11) = +0.58 (0.00 to +1.25) and C = +0.20 (−0.25 to +0.75).
