# Supplement to the technical report: Section 4.3 as written before the organisers' answer

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report now keeps a short summary of Section
4.3; this file holds the section's earlier complete text, unchanged, with its table of the final's possible shapes,
written before the organisers gave the final's size and budget (Section 4.5). Section, Appendix and Figure references
point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's
folder. Note added 20 October: text moved out of the report in draft 27 is in the addendum of 20 October at the end of
this file.*

### 4.3 The final's possible shapes

Lane F mocked the shapes the final could take (2,856 main and 1,632 small case runs; virtual clock: time and validity,
not accuracy) [510, 520]:

| Final shape (mock) | v95, main: cases answered | v96, small |
|---|---|---|
| Board shape, one 4,020 s job | 21 of 21 to 1.6x slower; 18 at 2.0x | 14 of 14 |
| Job budget scaled per case (191 s main, 287 s small) | all, to 1.6x slower | all, to 1.6x slower |
| Several board-size jobs, 210 (120) cases | 206 to 210 at 1.0x; 176 to 186 at 2.0x | 120 of 120 to 1.4x; 115 to 120 at 2.0x |
| One 4,020 s job, 112 to 350 (64 to 200) cases | 18 to 26 (expected accuracy 0.05 to 0.18) | 15 to 22 |
| Per-case timeout of 191 s, 210 cases | 68 | — |

No variant that keeps v95's answers on 21 cases saves a one-job final above about 28 to 30 main or 23 small cases [510].
**v104** (main) and **v105** (small) skip Qwen's quick finish when it cannot change the answer: answers identical on all
2,856 main mock case runs (v105: Appendix E.15), about 10% and 13% faster, and
v104 answers 21 of 21 at 2.0x slower [510, 517]. Ties are broken by average runtime over three trials [498]. Each needs
one board run before it replaces v95 or v96, and the file to submit follows a rule fixed against the organisers' answer
about the final's shape (Appendix E.15).

### Addendum of 20 October

*Text moved out of the report in draft 27 to keep its main text within the limit (verbatim, from draft 26).*

*From Section 4.3 (the 2,856 identical mock runs are still in the report's Appendix C):*

Before the organisers' answer, lane F mocked the shapes the final could take [510, 520]
(`report_supplement/S43_final_possible_shapes.md`). **v104** (main) and **v105** (small) skip Qwen's quick finish when
it cannot change the answer: answers identical on all 2,856 main mock case runs, about 10% and 13% faster [510, 517].
