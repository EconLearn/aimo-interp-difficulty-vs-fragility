# Supplement to the technical report: Appendix E.1 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix
part and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references
point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's
folder.*

### E.1 The own-run rules row by row (Section 3.2)

**Per-configuration readings and their public support** (public rows; in-sample for the stand-in and prior rows;
rows right / read over all reads; hard region in brackets, for the stand-in as hard-region rows right, refit, mean of
six reads):

| Configuration | Reading in the entry | Rows right / read, all reads (hard region) |
|---|---|---|
| Olmo-3-7B-Think | Own run, ≤ 3 attempts, cap 10,000; robust iff ≥ 2 of 3 end (1 attempt: iff it ends) | 30 / 34 over five reads (9 / 10) |
| Skywork-OR1-Math-7B | Own run, ≤ 3 attempts, cap 9,000; robust iff ≥ 1 of 3 ends | 6 / 15 over five reads (1 / 10) |
| gpt-oss low | Stand-in (here the examinee itself) | 5 / 7 in each of three dresses (2.0 / 4) [336, 373, 375, 379] |
| gpt-oss high | Public prior "robust" | 13 / 15 (7 / 9) [336, 373] |
| gpt-oss medium | Stand-in | 14, 13 and 13 of 15 in three dresses (8.8 / 10) [336, 373, 375, 379] |
| Qwen3.5-4B | Stand-in | 11 / 12 in the first three dresses, 10 / 12 in the fourth (4.3 / 5) [336, 373, 404] |
| DeepSeek-R1-0528-Qwen3-8B | Stand-in | 9 / 10 in each dress (4.3 / 5) [336, 373] |

No own-label row supports what the board gain needs, calling hard robust problems robust [387]: Olmo has no hard robust
row, and Skywork's only one, T16, was right in one read of five, just inside the 9,000 cap [389].

**The own-run rules row by row** (public rows; [387] and the logs it reads; the dress-rehearsal counts are from [373,
375, 379]). "R" or "N" is what the rule called; the attempt counts are attempts that ended on their own.

| Own labelled row | Region | Label | Skywork full read (K 3) | Skywork originals read (K 2) | Dress, +Coverage ¹ | Dress, +Fast 7B | Dress, +Skywork K 3 (K 3) |
|---|---|---|---|---|---|---|---|
| Skywork T15 | easy | robust | R, right (3 of 3) | R, right (2 of 2) | right | right | right |
| Skywork T16 | hard | robust | R, right (2 of 3) | N, wrong (0 of 2) | wrong | wrong | wrong (0 of 3) |
| Skywork T13 | hard | non-robust | R, wrong (2 of 3) | R, wrong (1 of 2) | wrong | wrong | wrong |
| **Skywork rule, right / rows** | | | 2 / 3 | 1 / 3 | 1 / 3 | 1 / 3 | 1 / 3 |

| Own labelled row | Region | Label | Olmo full read (K 3) | Olmo full read (K 1) | Dress, +Coverage ¹ | Dress, +Fast 7B | Dress, +Skywork K 3 |
|---|---|---|---|---|---|---|---|
| Olmo T15, T17, T18 | easy | robust | right (3 of 3 each) | not read | right | right | right |
| Olmo T06, T07, T08 | easy | robust | not read | not read | right | right | right |
| Olmo T04 | easy | robust | not read | not read | wrong | wrong | wrong |
| Olmo T10 | hard | non-robust | right (0 of 3) | right (0 of 1) | right | right | right |
| Olmo T13 | hard | non-robust | right (0 of 3) | right (0 of 1) | wrong | right | right |
| **Olmo rule, right / rows** | | | 5 / 5 | 2 / 2 | 7 / 9 | 8 / 9 | 8 / 9 |

¹ In the +Coverage dress the own runs read only 13 (Skywork) and 9 (Olmo) of 28 problems at K 1 [373], so some answers
in that column are the stand-in's.

The +Stand-in depth dress is not in these tables: the ledger records its totals only, not which row changed [404]. Its
per-configuration totals: Qwen 10 / 12, Skywork's rule 1 / 3, Olmo's 7 / 9 (Olmo at K 3 on 2 problems, K 1 on 26),
medium 14 / 15, the rest as in the +Skywork K 3 dress (59 of 71 against 60).

- **The support first cited for Olmo's rule was easy against hard**: Olmo's 9 of 9 against 0 of 8 attempts ended, on
  its easy robust rows T15, T17 and T18 against its hard non-robust rows T10 and T13 [339]; Section 3.4.

- **Skywork's ending lengths.** On the easy templates its ending attempts stop between 2,190 and 8,867 tokens (computed
  from the attempt codes in `own_q1q2.out`), but its own robust T16 usually runs to or near the cap, and as a reader it
  never ends T23, a robust row of another configuration [269, 312, 387]. In the full read, where T16 was right, its 2
  ending attempts stopped at 8,448 and 8,715 tokens, just inside the 9,000 cap [387, 389].
- **Skywork as a reader of all 71 rows** (indirect support for its rule): it ended at least one
  attempt on 17 of 19 hard robust rows and 6 of 18 hard non-robust rows (computed, [387]; Section 3.3).
