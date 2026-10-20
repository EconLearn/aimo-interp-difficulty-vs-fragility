# Supplement to the technical report: Appendix E.2 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix
part and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references
point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's
folder.*

### E.2 Own readings tried for configurations without own runs (Section 3.2)

**The stand-in's errors** track a strength mismatch between reader and examinee [140, 192]: false alarms where the
judged model is stronger than the low-effort reader (T05), misses where both solve the problem yet the label is
non-robust (T13). **The stand-in in the hard region, by configuration** [336]: over six reads it got gpt-oss high
rows right 5.5 of 9 times (always-robust: 7 of 9) and low rows at chance (2.0 of 4).

- **gpt-oss high** [336, 356, 372]. Answering "robust" on high rows lifts the hard region from 27.5 to 29.0 of 37 rows
  (better in five of six reads). No own reading in our logs beats the prior: the share of attempts ended by 8,000 tokens
  ties the stand-in at AUC 0.923, and own agreement scores 12 of 15 against the prior's 13. With two non-robust rows,
  high cannot be ranked from public data.
- **gpt-oss medium** [372, 373]. Medium's own answer agreement separates its 14 read rows perfectly in hindsight (robust
  0.92 to 1.00, non-robust 0.33 to 0.81). But the non-robust rows were also the ones run at the longer cap, so cap and
  label are confounded. The rule fixed before the next rehearsal required a gain of at least 2 of 15 rows over the
  stand-in. The stand-in scored 14 of 15 (in-sample), so the variant was not adopted.
- **gpt-oss low** [309, 374]. Low's own success rate at K 50 separates its 7 rows, but by 0.08 (0.88 against 0.80), and
  the stand-in's two misses are the two rows at that margin. Section 3.3 and Appendix E.7 discuss why.
- **DeepSeek** [346, 348]. At a 16,000-token cap it ended on its own on 1 of 6 rows, and its forced answers were right
  on robust and non-robust rows alike. The rule "at least one attempt ends" was right on 4 of 6 against a bar of 5. A
  first research run was lost: our time estimate used DeepSeek's short-context speed, 2.7 times too fast at these
  lengths (about 11.6 ms per row per step, server).
- **Qwen** [244, 356]. Full-length attempts finished 4 of 36 times inside 17,761 tokens. Forced-answer agreement at
  5,000 tokens scored AUC 0.89 and 0.72 on two reads, below the stand-in's 0.97.
