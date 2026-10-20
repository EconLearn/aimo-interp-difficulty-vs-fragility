# Supplement to the technical report: Appendix E.15 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 17 October: the organisers have since given the final's size and budget (30 to 50 questions at about 170 s per
sample [537]; Section 4.5 of the report); statements below that call them unpublished or untestable predate that answer.
Note added 20 October: text moved out of the report in draft 27 is in the addendum of 20 October at the end of this
file. Note added 20 October (draft 28): the code that reads the harness's budget-like environment variables is described
as what it is, a budget reader that only plans time (two phrases reworded; no number changed).*

### E.15 The final-shape risk in full (Sections 4.2, 4.3)

**Lane F's method** (`work/miners17/laneF/shapes_mock.py` → `mock_outputs.md`) [510]. It reuses the per-case mock
`rehearsal/run_per_case.py` (fresh process per case, virtual clock, server-calibrated costs). A case process keeps no
state and receives no budget, so a case's time and answer depend only on configuration, problem and speed; each such
case runs once, and job layouts are then simulated from that table with the harness rules seen in our logs (cases in
order on a shared 4,020 s budget; a case that overruns times out and every later case is skipped) [464, 492]. Expected
accuracy credits an answered case with its configuration's public-row accuracy on the v95 line and an unanswered case
with 0 (or 0.5 for chance). In one 4,020 s job of 112 to 350 cases v95 answers 18 to 26 (18 at 2.0x
slower on 112 cases in configuration blocks) and v96 15 to 22 of 64 to 200 (`mock_outputs.md`); ledger [510]'s summary
gave 19 to 26 and 18 to 25, corrected in [520] (25 is the v104 small twin's column). v105, the small twin of v104, gave
per-case calls identical to v96 in four small mock runs, 2,574 → 2,237 s at 1.0x and 3,065 → 2,655 s at 1.4x [517].

**More shapes** (main, v95; mock): with the cases of new problems interleaved in one 4,020 s job, 24 cases are all
answered at 1.0x (21 at 1.4x), 28 cases 26, and from 35 cases on about 26 at most; a per-case timeout of 300 s answers
210 of 210 at 1.0x. v104 answers 28 of 28 in the same one-job layout at 1.0x and 21 of 21 on the board shape at 2.0x
(`mock_outputs.md`); on the board shape it ends at 3,045 s against v95's 3,341 s [510].

**Answer-changing variants, not built** [510]: C185, v95 with both per-case targets set to 185 s (−0.2 to −0.4 case per
21; fits about 31 to 33 cases in one job), and C45, targets of 45 s, so that almost every case takes the time-forced
fallback, mostly answered robust (−1.5 cases per 21; no size limit).

**The rule fixed against the organisers' answer** [510]: board-like jobs, at least 190 s per case or a per-case timeout
of at least 300 s → keep v95 / v96 (v104 optional, being faster); one job of 22 to 28 main cases → v104; more than about
28 main or 23 small cases → C45 on that track; a per-case timeout below about 200 s → C185. v104 needs one board run
first.

**The earlier mock** (the per-case mock at the validation budget, `--shape final` and `--shape final_mix`):

| Bundle | Shape (mock) | Cases answered | Invalid | Elapsed |
|---|---|---|---|---|
| v95 | main board, 21 cases | 21 of 21 | 0 | 3,339 s [466] |
| v83 | main board, 21 cases | 15 of 21 | 6 (1 timeout, 5 skipped) | 4,020 s |
| v95 | final, 30 problems × 7 configurations, in configuration blocks | 20 of 210 (all Qwen) | 190 | 4,020 s |
| v95 | final, the same 210 cases problem by problem | 25 of 210 | 185 | 4,020 s |

An independent reviewer ran the last three rows; we re-ran them with the same counts (computed, 16 October). Any model
reading of 210 cases would need about 34,000 s [466]. If the harness exposes a budget-like variable, v95 caps its
per-case targets at 0.8 of it; whether that suffices at 210 cases is untested. Otherwise v95's final score depends on
the final's job budget growing with its size, which we cannot test before the final.

**Per-case costs in full** (server, the rerun's log [465]; its ingestion line read `job_timeout_s=4200` and
`safety_margin_s=180` [464]): loading gpt-oss-120b
with its checks 12 to 17 s per process; the stand-in on one problem (K 32, cap 3,000) 52 to 123 s; Qwen's quick finish
38 to 40 s; Skywork's own run (K 3) 40 to 132 s; Olmo's about 298 s. v95 runs Skywork's own run on the default decode
path (14 to 15 ms per step at 3 rows against 20.6 on the fast path) [466], and once per
process its budget reader logs the names of harness-related environment variables, short command-line tokens and the
values of budget-like variables (never the value of a variable whose name suggests a key, token, secret or password); it
reads them only to plan time and alters nothing in the harness.
v104's answers are also identical on 1,632 small mock case runs and on 84 original-harness ones [510]. v65's
rerun spent about 2,000 s of 4,020 on readings it did not use [465]. v95's per-case targets (210 s; own runs 400 s) are
hand-set and shrink only if the harness sets a budget-like environment variable (`sub_v114m/solution.py`; the budget
reader, function `_probe`); the ledger holds no per-configuration counts for 991447 or 990657, nor v95's budget-reader output [464, 466, 469,
471], and we did not read the harness's own files or processes [484].

**The mock's calibration.** The 17 to 22 s in the calibration note of our per-case mock (`rehearsal/run_per_case.py`) is
a longer span: the load plus the fast decode path's check (about 5 s in the mock), until the stand-in can decode; the
mock charges about 22 s.

### Addendum of 20 October

*Text moved out of the report in draft 27 to keep its main text within the limit (verbatim, from draft 26).*

*From Section 4.2 (per-case costs and [492]: the report's Appendix E.15):*

our best small score [471, 476]. The mock runs 10 to 13% slower than the server
(computed; per-case costs in Appendix E.15). Files do not
persist between cases [492].
