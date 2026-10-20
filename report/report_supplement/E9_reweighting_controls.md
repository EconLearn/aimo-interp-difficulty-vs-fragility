# Supplement to the technical report: Appendix E.9 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix
part and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references
point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's
folder.*

### E.9 Reweighting controls in full (Section 3.4)

A reweighting of the 71 rows to five moments of the hidden set matched the
board's specificity (0.61 against 0.60) [192], but that match is arithmetic, not evidence: two of the five moments are
the stand-in's own non-robust call shares on the hidden run, and with the class mix fixed at 0.50 they force specificity
= sensitivity − 0.333; any random base reweighted to the same targets gives 0.614 (computed [401]). Controls without
those targets (public rows, 90% template-bootstrap ranges [401]): class mix 50/50 alone leaves specificity at 0.846
[0.72, 0.93]; adding the strength mix, 0.851; adding the hidden calls' mean low-effort reading length (1,592 tokens)
lowers it to 0.772 [0.65, 0.89], a drop of −0.075 [−0.14, −0.00] (P 0.95), about a third of the gap to the board's 0.60
and below the 5th percentile of 200 random reweightings with the same effective sample size (0.846 [0.78, 0.91]; 4% of
draws at or below 0.772). Matching the full seven-configuration mix as well reaches 0.687, but with effective sample
size 30 and leave-one-template-out values of 0.58 to 0.74 it rests on two templates.

On the reading-length reading, the hidden problems are read longer, and longer reads
go with more false alarms. The stand-in's false alarms on small models are confident: on public rows they score as
harder than truly non-robust rows of the same strength [192] (on the board, shifting the threshold toward the
stated base rate scored 13 against 16 [140]; Section 5.1).
