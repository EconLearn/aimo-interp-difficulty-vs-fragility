# Supplement to the technical report: Appendix E.17 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key table; this file holds the part's complete text, including lane F2's tables copied unchanged from
`work/miners18/laneF2/f2_full_tables.md`. Every number here is mock or computed, not board. Section, Appendix and Figure
references point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the
report's folder. Note added 17 October, later: the second nominees v113 / v114, v111's slow-server answer changes and
the pre-mortem's fault list are in the report's Appendix E.17 only. Note added 18 October: v102, unread below, was read
on 18 October and closed the STD entries v107 and v108 [555]; the nominees' board runs are in the report's Appendix
E.17, and lane K and the pre-mortem's fault list are in the addendum at the end of this file. Note added 20 October:
lane F4 (the per-case-limit variants v115 / v116; its board numbers are labelled as such) and five paragraphs moved out
of the report in draft 27 are in the addendum of 20 October at the end of this file. Note added 20 October (draft 28):
lanes OLMO-CAP, SMALL and REFILL [584, 587, 590] and two passages moved out of the report in draft 28 are in the
addendum of 20 October (draft 28) at the end of this file. Note added 20 October (draft 29): text moved out of the
report in draft 29 is in the addendum of 20 October (draft 29) at the end of this file; the report keeps a summary or a
pointer.*

### E.17 The announced final: lane F2, the pre-mortem and the nominees (Section 4.5)

Run offline on 17 October, after the organisers' answer (mock and CPU; no uploads); numbers are mock or computed, not
board [537-540].

**Exact differences from the scored files** (`work/sub_v114m` and `sub_v115s` against `sub_v129m` and `sub_v130s`): only
`solution.py`, `engine2.py` and `params.json` differ; v111 and v112 share their code apart from the log tag.

| `params.json` key | v95 / v96 | v111 | v112 | Effect |
|---|---|---|---|---|
| `qfin_skip_moot` | absent | true | true | skip Qwen's quick finish when the full and agreement-only models give the same answer for either quick-finish value (v104) |
| `qfin_skip_cut` | absent | true | true | skip it when the case clock stopped the gpt-oss reading (v109) |
| `case_target_seconds` | 210 | 210 | 165 | the stand-in keeps K 32, but the quick finish no longer fits: a case whose quick finish is not moot uses the agreement-only model (v110) |
| `own_plan_seconds` / `own_case_target_seconds` | absent / 400 | absent / 400 | 400 / 232 | own run planned in a 400 s window (K 3) but stopped at 232 s; up to about 1.4x the mock's speed the reading is v96's (v110) |

`solution.py` carries the two skips, the own-run window and fixes F1, F2, F3 and F5; `engine2.py` carries F4, a fallback
around the integer conversion in `parse_answer`.

File md5s (`solution.py`, `engine2.py`, `params.json`): v111 fe5a693846b8a57482b7418ae94a20ec,
277bb168c75094016789f413cab1d09a, e9caafed363b4b5581cfe9ef4c32bdf8; v112 419a239498887d7510e86e4aa71edb75, the same
`engine2.py`, 03e1397f37316ffa01e8ec6a8918dc1d (computed, 17 October). Zip md5s: Appendix B.

**Lane F2's method** (`work/miners18/laneF2/`: `f2_sim.py`, `f2_tables.py`, `f2_grid.py`, `f2_final.py`, `build_f2.py`;
outputs `f2_full_tables.md`, `board_mock.out`, `oldpath_check.out`, `zip_mock.out`) [538]. The per-case mock
(`rehearsal/run_per_case.py`) gives each case's time and answer by configuration, problem and speed; the final is then
simulated from those tables with the harness rules seen in our logs: cases run one after another, each in a fresh
process with no budget information, on one shared job budget B, and a case whose time exceeds the budget left times out
and every later case is skipped [464, 492]. B = N × 170 s, the organisers' figure [537], with and without the 180 s
safety margin seen in our logs. Mixes, per 21 main or 14 small cases and scaled to N: the validation mix (main Qwen 2,
Skywork 3, Olmo 2, DeepSeek 3, high 3, low 5, medium 3; small Qwen 5, Skywork 3, Olmo 3, DeepSeek 3) and a worst mix,
Olmo- and stand-in-heavy with no instant gpt-oss high and no fast Skywork (main Qwen 4, Olmo 6, DeepSeek 4, low 4,
medium 3; small Qwen 4, Olmo 6, DeepSeek 4). Order: board-like (the 4B and 7B models in configuration blocks in harness
order, then the gpt-oss efforts interleaved), each case on a distinct synthetic new problem; sensitivity: 200 random
case orders and problem draws. Bundles that skip a moot quick finish are timed at the public-row moot rate of each
configuration (25 of 44 stand-in rows in all), not the mock's (about 97%, from its random readings). "Server" (srv)
multiplies the 1.0x mock times by each configuration's ratio of server to mock time on v95's board run (991447; 3,030 s
[471]), which it reproduces as 3,125 s. Expected accuracy (lane F's rule): an answered case scores its configuration's
public-row accuracy on the v95 line when a full reading decided it, and its public robust base rate when the prior, the
quick finish alone or a fallback did; an unanswered case scores 0. STD-decided Skywork and Olmo cases (v107, v108) score
an assumed 2 of 3 and 8 of 9, the blind-writer average of [528] (v102 unread). Bundles in the tables: v95, v104, v107
and v109 (main), v96, v105, v108 and v110 (small); v111 and v112 match v109 and v110 (below).

The tables below are copied unchanged from `f2_full_tables.md`, with its section lines set in bold. In a cell, "30/30
0.783 (+549 s)" means 30 of 30 cases answered, expected accuracy 0.783 and 549 s to spare; "[1+3]" means 1 timeout and 3
skipped cases; "no margin" gives the result without the 180 s margin where it differs.

**main: cases answered / N, expected accuracy (invalid = 0), spare or [timeouts + skipped]; budget N x 170 s WITH the 180 s margin (no margin in brackets when it differs)**

| mix | N | speed | v95 | v104 | v107 | v109 |
|---|---|---|---|---|---|---|
| val | 30 | srv | 30/30 0.783 (+549 s) | 30/30 0.783 (+1089 s) | 30/30 0.827 (+679 s) | 30/30 0.783 (+1089 s) |
| val | 30 | 1.0x | 30/30 0.783 (+248 s) | 30/30 0.783 (+543 s) | 30/30 0.827 (+14 s) | 30/30 0.783 (+543 s) |
| val | 30 | 1.2x | 28/30 0.723 [1+1] (no margin 29/30 0.754) | 30/30 0.783 (+128 s) | 26/30 0.710 [1+3] (no margin 28/30 0.768) | 30/30 0.783 (+679 s) |
| val | 30 | 1.4x | 26/30 0.666 [1+3] (no margin 28/30 0.723) | 30/30 0.783 (+58 s) | 28/30 0.768 [1+1] (no margin 29/30 0.799) | 30/30 0.783 (+467 s) |
| val | 30 | 1.6x | 25/30 0.637 [1+4] (no margin 26/30 0.666) | 29/30 0.754 [1+0] (no margin 30/30 0.783) | 28/30 0.768 [1+1] (no margin 30/30 0.827) | 30/30 0.783 (+256 s) |
| val | 40 | srv | 40/40 0.790 (+867 s) | 40/40 0.790 (+1487 s) | 40/40 0.829 (+1000 s) | 40/40 0.790 (+1447 s) |
| val | 40 | 1.0x | 40/40 0.790 (+465 s) | 40/40 0.790 (+887 s) | 40/40 0.829 (+251 s) | 40/40 0.790 (+845 s) |
| val | 40 | 1.2x | 39/40 0.769 [1+0] (no margin 40/40 0.790) | 40/40 0.790 (+552 s) | 39/40 0.808 [1+0] (no margin 40/40 0.829) | 40/40 0.790 (+1052 s) |
| val | 40 | 1.4x | 36/40 0.702 [1+3] (no margin 37/40 0.724) | 40/40 0.790 (+220 s) | 39/40 0.808 [1+0] (no margin 40/40 0.829) | 40/40 0.790 (+784 s) |
| val | 40 | 1.6x | 34/40 0.659 [1+5] (no margin 36/40 0.702) | 40/40 0.790 (+3 s) | 39/40 0.808 [1+0] (no margin 40/40 0.829) | 40/40 0.790 (+515 s) |
| val | 50 | srv | 50/50 0.797 (+991 s) | 50/50 0.797 (+1655 s) | 50/50 0.832 (+1105 s) | 50/50 0.797 (+1574 s) |
| val | 50 | 1.0x | 50/50 0.797 (+487 s) | 50/50 0.797 (+1205 s) | 50/50 0.832 (+468 s) | 50/50 0.797 (+1162 s) |
| val | 50 | 1.2x | 48/50 0.761 [1+1] (no margin 49/50 0.780) | 50/50 0.797 (+615 s) | 49/50 0.815 [1+0] (no margin 50/50 0.832) | 50/50 0.797 (+1265 s) |
| val | 50 | 1.4x | 45/50 0.710 [1+4] (no margin 46/50 0.727) | 50/50 0.797 (+221 s) | 49/50 0.815 [1+0] | 50/50 0.797 (+938 s) |
| val | 50 | 1.6x | 44/50 0.691 [1+5] (no margin 45/50 0.710) | 49/50 0.780 [1+0] (no margin 50/50 0.797) | 49/50 0.815 [1+0] (no margin 50/50 0.832) | 50/50 0.797 (+610 s) |
| worst | 30 | srv | 27/30 0.788 [1+2] (no margin 28/30 0.817) | 30/30 0.876 (+125 s) | 30/30 0.847 (+27 s) | 30/30 0.876 (+125 s) |
| worst | 30 | 1.0x | 26/30 0.757 [1+3] (no margin 27/30 0.788) | 27/30 0.788 [1+2] (no margin 29/30 0.848) | 26/30 0.727 [1+3] (no margin 27/30 0.758) | 27/30 0.788 [1+2] (no margin 29/30 0.848) |
| worst | 30 | 1.2x | 23/30 0.669 [1+6] (no margin 24/30 0.700) | 25/30 0.728 [1+4] (no margin 26/30 0.757) | 24/30 0.670 [1+5] | 28/30 0.817 [1+1] (no margin 29/30 0.848) |
| worst | 30 | 1.4x | 22/30 0.640 [1+7] (no margin 23/30 0.669) | 24/30 0.700 [1+5] (no margin 26/30 0.757) | 24/30 0.670 [1+5] (no margin 25/30 0.699) | 27/30 0.788 [1+2] (no margin 28/30 0.817) |
| worst | 30 | 1.6x | 21/30 0.609 [1+8] (no margin 22/30 0.640) | 22/30 0.640 [1+7] (no margin 23/30 0.669) | 23/30 0.639 [1+6] (no margin 25/30 0.699) | 25/30 0.728 [1+4] (no margin 26/30 0.757) |
| worst | 40 | srv | 36/40 0.788 [1+3] (no margin 37/40 0.812) | 40/40 0.878 (+94 s) | 39/40 0.826 [1+0] (no margin 40/40 0.847) | 40/40 0.878 (+54 s) |
| worst | 40 | 1.0x | 35/40 0.767 [1+4] (no margin 36/40 0.788) | 38/40 0.833 [1+1] (no margin 39/40 0.856) | 36/40 0.758 [1+3] (no margin 37/40 0.781) | 38/40 0.833 [1+1] (no margin 39/40 0.856) |
| worst | 40 | 1.2x | 31/40 0.677 [1+8] (no margin 32/40 0.699) | 34/40 0.743 [1+5] (no margin 35/40 0.767) | 32/40 0.668 [1+7] (no margin 33/40 0.692) | 38/40 0.833 [1+1] (no margin 39/40 0.856) |
| worst | 40 | 1.4x | 30/40 0.654 [1+9] | 34/40 0.743 [1+5] (no margin 35/40 0.767) | 33/40 0.692 [1+6] (no margin 34/40 0.713) | 36/40 0.788 [1+3] (no margin 37/40 0.812) |
| worst | 40 | 1.6x | 28/40 0.609 [1+11] (no margin 29/40 0.633) | 32/40 0.699 [1+7] (no margin 33/40 0.722) | 34/40 0.713 [1+5] (no margin 35/40 0.736) | 34/40 0.743 [1+5] (no margin 35/40 0.767) |
| worst | 50 | srv | 46/50 0.806 [1+3] (no margin 47/50 0.824) | 50/50 0.877 (+182 s) | 49/50 0.829 [1+0] (no margin 50/50 0.846) | 50/50 0.877 (+142 s) |
| worst | 50 | 1.0x | 44/50 0.770 [1+5] (no margin 45/50 0.788) | 48/50 0.841 [1+1] (no margin 49/50 0.860) | 45/50 0.757 [1+4] (no margin 46/50 0.774) | 48/50 0.841 [1+1] (no margin 49/50 0.860) |
| worst | 50 | 1.2x | 40/50 0.700 [1+9] (no margin 41/50 0.717) | 44/50 0.770 [1+5] (no margin 45/50 0.788) | 41/50 0.686 [1+8] (no margin 42/50 0.703) | 48/50 0.841 [1+1] (no margin 49/50 0.860) |
| worst | 50 | 1.4x | 38/50 0.664 [1+11] | 41/50 0.717 [1+8] (no margin 42/50 0.734) | 40/50 0.669 [1+9] (no margin 41/50 0.686) | 45/50 0.788 [1+4] (no margin 47/50 0.824) |
| worst | 50 | 1.6x | 35/50 0.609 [1+14] (no margin 36/50 0.628) | 40/50 0.700 [1+9] (no margin 41/50 0.717) | 42/50 0.703 [1+7] (no margin 43/50 0.721) | 43/50 0.753 [1+6] (no margin 44/50 0.770) |

**per-configuration mean case seconds on the 50 synthetic new problems (moot-skip bundles at the public-row moot rate):**

| bundle | speed | Qwen | Skywork | Olmo | DeepSeek | high | low | medium | val-mix mean | worst-mix mean |
|---|---|---|---|---|---|---|---|---|---|---|
| v95 | srv | 176 | 131 | 199 | 174 | 2 | 174 | 181 | 147 | 182 |
| v95 | 1.0x | 191 | 141 | 189 | 191 | 2 | 191 | 191 | 157 | 191 |
| v95 | 1.2x | 206 | 166 | 222 | 206 | 2 | 206 | 206 | 173 | 210 |
| v95 | 1.4x | 207 | 191 | 255 | 207 | 2 | 207 | 207 | 180 | 221 |
| v95 | 1.6x | 207 | 216 | 288 | 207 | 2 | 207 | 207 | 187 | 230 |
| v104 | srv | 151 | 131 | 199 | 154 | 2 | 149 | 156 | 132 | 165 |
| v104 | 1.0x | 167 | 141 | 189 | 166 | 2 | 168 | 170 | 142 | 174 |
| v104 | 1.2x | 176 | 166 | 222 | 176 | 2 | 174 | 174 | 153 | 188 |
| v104 | 1.4x | 182 | 191 | 255 | 177 | 2 | 179 | 181 | 163 | 201 |
| v104 | 1.6x | 175 | 216 | 288 | 176 | 2 | 177 | 174 | 168 | 208 |
| v107 | srv | 151 | 201 | 201 | 154 | 2 | 149 | 156 | 142 | 166 |
| v107 | 1.0x | 167 | 218 | 218 | 166 | 2 | 168 | 170 | 156 | 182 |
| v107 | 1.2x | 176 | 244 | 244 | 176 | 2 | 174 | 174 | 167 | 195 |
| v107 | 1.4x | 182 | 247 | 247 | 177 | 2 | 179 | 181 | 170 | 199 |
| v107 | 1.6x | 175 | 247 | 247 | 176 | 2 | 177 | 174 | 168 | 196 |
| v109 | srv | 150 | 131 | 199 | 153 | 2 | 149 | 158 | 132 | 165 |
| v109 | 1.0x | 167 | 141 | 189 | 166 | 2 | 168 | 172 | 143 | 174 |
| v109 | 1.2x | 156 | 166 | 222 | 156 | 2 | 156 | 156 | 142 | 175 |
| v109 | 1.4x | 156 | 191 | 255 | 156 | 2 | 156 | 156 | 148 | 184 |
| v109 | 1.6x | 156 | 216 | 288 | 156 | 2 | 156 | 156 | 155 | 194 |

**sensitivity: 200 random case orders x random problem draws, budget with margin: mean answered (worst draw)**

| mix | N | speed | v95 | v104 | v107 | v109 |
|---|---|---|---|---|---|---|
| val | 30 | srv | 30.0 (30) 0.783 | 30.0 (30) 0.783 | 30.0 (30) 0.827 | 30.0 (30) 0.783 |
| val | 30 | 1.0x | 30.0 (30) 0.783 | 30.0 (30) 0.783 | 30.0 (29) 0.826 | 30.0 (30) 0.783 |
| val | 30 | 1.2x | 27.7 (25) 0.723 | 30.0 (29) 0.782 | 28.3 (25) 0.781 | 30.0 (30) 0.783 |
| val | 30 | 1.4x | 26.4 (24) 0.691 | 29.2 (26) 0.762 | 27.7 (24) 0.763 | 30.0 (30) 0.783 |
| val | 30 | 1.6x | 25.4 (21) 0.665 | 28.2 (25) 0.737 | 28.0 (25) 0.773 | 30.0 (30) 0.783 |
| val | 40 | srv | 40.0 (40) 0.790 | 40.0 (40) 0.790 | 40.0 (40) 0.829 | 40.0 (40) 0.790 |
| val | 40 | 1.0x | 40.0 (40) 0.790 | 40.0 (40) 0.790 | 40.0 (40) 0.829 | 40.0 (40) 0.790 |
| val | 40 | 1.2x | 38.2 (36) 0.755 | 40.0 (40) 0.790 | 39.3 (37) 0.814 | 40.0 (40) 0.790 |
| val | 40 | 1.4x | 36.6 (33) 0.724 | 39.8 (37) 0.786 | 38.4 (36) 0.795 | 40.0 (40) 0.790 |
| val | 40 | 1.6x | 35.1 (31) 0.694 | 39.0 (36) 0.772 | 38.9 (36) 0.806 | 40.0 (40) 0.790 |
| val | 50 | srv | 50.0 (50) 0.797 | 50.0 (50) 0.797 | 50.0 (50) 0.832 | 50.0 (50) 0.797 |
| val | 50 | 1.0x | 50.0 (50) 0.797 | 50.0 (50) 0.797 | 50.0 (50) 0.832 | 50.0 (50) 0.797 |
| val | 50 | 1.2x | 47.5 (45) 0.757 | 50.0 (50) 0.797 | 49.1 (47) 0.817 | 50.0 (50) 0.797 |
| val | 50 | 1.4x | 45.5 (43) 0.726 | 49.7 (47) 0.792 | 48.0 (45) 0.800 | 50.0 (50) 0.797 |
| val | 50 | 1.6x | 43.8 (41) 0.699 | 48.7 (45) 0.776 | 48.6 (45) 0.809 | 50.0 (50) 0.797 |
| worst | 30 | srv | 26.6 (26) 0.776 | 29.4 (28) 0.857 | 29.3 (28) 0.826 | 29.4 (28) 0.858 |
| worst | 30 | 1.0x | 25.2 (25) 0.737 | 28.0 (26) 0.817 | 26.7 (25) 0.754 | 28.0 (26) 0.817 |
| worst | 30 | 1.2x | 23.0 (22) 0.671 | 25.8 (24) 0.753 | 25.0 (23) 0.705 | 27.9 (27) 0.814 |
| worst | 30 | 1.4x | 21.9 (21) 0.639 | 24.1 (22) 0.704 | 24.4 (22) 0.688 | 26.5 (25) 0.773 |
| worst | 30 | 1.6x | 21.1 (20) 0.615 | 23.5 (21) 0.687 | 24.8 (23) 0.700 | 25.2 (23) 0.737 |
| worst | 40 | srv | 35.9 (35) 0.787 | 39.6 (38) 0.869 | 39.6 (38) 0.839 | 39.6 (38) 0.869 |
| worst | 40 | 1.0x | 34.2 (34) 0.750 | 37.8 (35) 0.829 | 36.1 (34) 0.765 | 37.7 (35) 0.828 |
| worst | 40 | 1.2x | 31.1 (30) 0.681 | 34.8 (33) 0.762 | 33.6 (32) 0.711 | 37.6 (36) 0.824 |
| worst | 40 | 1.4x | 29.6 (28) 0.649 | 32.6 (31) 0.714 | 32.9 (31) 0.696 | 35.7 (34) 0.783 |
| worst | 40 | 1.6x | 28.5 (27) 0.625 | 31.6 (29) 0.694 | 33.4 (32) 0.708 | 34.0 (32) 0.746 |
| worst | 50 | srv | 45.2 (44) 0.792 | 49.6 (48) 0.871 | 49.5 (48) 0.838 | 49.7 (48) 0.871 |
| worst | 50 | 1.0x | 43.1 (42) 0.756 | 47.5 (45) 0.832 | 45.3 (43) 0.767 | 47.4 (45) 0.831 |
| worst | 50 | 1.2x | 39.1 (38) 0.685 | 43.7 (41) 0.767 | 42.3 (40) 0.716 | 47.1 (46) 0.827 |
| worst | 50 | 1.4x | 37.2 (36) 0.653 | 40.8 (38) 0.716 | 41.4 (39) 0.700 | 44.8 (43) 0.785 |
| worst | 50 | 1.6x | 35.7 (34) 0.626 | 39.6 (37) 0.695 | 42.0 (40) 0.711 | 42.6 (40) 0.748 |

**STD bundles with Skywork / Olmo problems that STD COVERS (public templates with a lane L program; the main table above uses synthetic problems = STD finds no usable code -> fallback), budget with margin:**

| mix | N | speed | v107 |
|---|---|---|---|
| val | 30 | srv | 30/30 0.838 (+982 s) |
| val | 30 | 1.0x | 30/30 0.838 (+345 s) |
| val | 30 | 1.2x | 28/30 0.771 [1+1] |
| val | 30 | 1.4x | 28/30 0.771 [1+1] |
| val | 30 | 1.6x | 28/30 0.768 [1+1] |
| val | 40 | srv | 40/40 0.840 (+1377 s) |
| val | 40 | 1.0x | 40/40 0.840 (+662 s) |
| val | 40 | 1.2x | 40/40 0.835 (+23 s) |
| val | 40 | 1.4x | 39/40 0.810 [1+0] |
| val | 40 | 1.6x | 39/40 0.808 [1+0] |
| val | 50 | srv | 50/50 0.844 (+1561 s) |
| val | 50 | 1.0x | 50/50 0.844 (+963 s) |
| val | 50 | 1.2x | 49/50 0.818 [1+0] |
| val | 50 | 1.4x | 49/50 0.815 [1+0] |
| val | 50 | 1.6x | 49/50 0.815 [1+0] |

**small: cases answered / N, expected accuracy (invalid = 0), spare or [timeouts + skipped]; budget N x 170 s WITH the 180 s margin (no margin in brackets when it differs)**

| mix | N | speed | v96 | v105 | v108 | v110 |
|---|---|---|---|---|---|---|
| val | 30 | srv | 28/30 0.698 [1+1] (no margin 29/30 0.725) | 30/30 0.752 (+238 s) | 23/30 0.562 [1+6] (no margin 24/30 0.592) | 30/30 0.752 (+470 s) |
| val | 30 | 1.0x | 27/30 0.672 [1+2] (no margin 28/30 0.698) | 29/30 0.725 [1+0] (no margin 30/30 0.752) | 21/30 0.503 [1+8] (no margin 22/30 0.532) | 30/30 0.752 (+237 s) |
| val | 30 | 1.2x | 24/30 0.592 [1+5] (no margin 25/30 0.618) | 26/30 0.645 [1+3] (no margin 27/30 0.672) | 20/30 0.466 [1+9] | 28/30 0.698 [1+1] (no margin 29/30 0.725) |
| val | 30 | 1.4x | 23/30 0.562 [1+6] | 24/30 0.592 [1+5] (no margin 25/30 0.618) | 19/30 0.440 [1+10] (no margin 20/30 0.466) | 27/30 0.672 [1+2] (no margin 28/30 0.698) |
| val | 30 | 1.6x | 21/30 0.503 [1+8] (no margin 22/30 0.532) | 22/30 0.532 [1+7] (no margin 23/30 0.562) | 19/30 0.440 [1+10] | 25/30 0.611 [1+4] (no margin 26/30 0.638) |
| val | 40 | srv | 37/40 0.696 [1+2] (no margin 38/40 0.716) | 40/40 0.756 (+259 s) | 31/40 0.574 [1+8] | 40/40 0.756 (+490 s) |
| val | 40 | 1.0x | 36/40 0.676 [1+3] (no margin 37/40 0.696) | 38/40 0.716 [1+1] (no margin 39/40 0.736) | 28/40 0.507 [1+11] (no margin 29/40 0.529) | 40/40 0.756 (+208 s) |
| val | 40 | 1.2x | 32/40 0.596 [1+7] (no margin 33/40 0.616) | 34/40 0.636 [1+5] (no margin 35/40 0.656) | 27/40 0.474 [1+12] | 36/40 0.676 [1+3] (no margin 37/40 0.696) |
| val | 40 | 1.4x | 30/40 0.551 [1+9] | 31/40 0.574 [1+8] | 26/40 0.454 [1+13] | 35/40 0.656 [1+4] (no margin 36/40 0.676) |
| val | 40 | 1.6x | 28/40 0.507 [1+11] (no margin 29/40 0.529) | 29/40 0.529 [1+10] (no margin 30/40 0.551) | 26/40 0.454 [1+13] | 33/40 0.602 [1+6] (no margin 34/40 0.622) |
| val | 50 | srv | 48/50 0.727 [1+1] (no margin 49/50 0.743) | 50/50 0.759 (+433 s) | 39/50 0.581 [1+10] | 50/50 0.759 (+819 s) |
| val | 50 | 1.0x | 46/50 0.695 [1+3] (no margin 47/50 0.711) | 49/50 0.743 [1+0] (no margin 50/50 0.759) | 36/50 0.528 [1+13] (no margin 37/50 0.546) | 50/50 0.759 (+462 s) |
| val | 50 | 1.2x | 41/50 0.615 [1+8] (no margin 42/50 0.631) | 45/50 0.679 [1+4] (no margin 46/50 0.695) | 34/50 0.481 [1+15] | 47/50 0.711 [1+2] (no margin 48/50 0.727) |
| val | 50 | 1.4x | 38/50 0.563 [1+11] (no margin 39/50 0.581) | 40/50 0.599 [1+9] (no margin 41/50 0.615) | 33/50 0.466 [1+16] (no margin 34/50 0.481) | 45/50 0.679 [1+4] (no margin 46/50 0.695) |
| val | 50 | 1.6x | 36/50 0.528 [1+13] (no margin 37/50 0.546) | 38/50 0.563 [1+11] | 33/50 0.466 [1+16] | 43/50 0.634 [1+6] (no margin 44/50 0.650) |
| worst | 30 | srv | 26/30 0.767 [1+3] (no margin 27/30 0.794) | 28/30 0.820 [1+1] (no margin 30/30 0.874) | 21/30 0.631 [1+8] (no margin 22/30 0.660) | 30/30 0.874 (+100 s) |
| worst | 30 | 1.0x | 26/30 0.767 [1+3] (no margin 27/30 0.794) | 28/30 0.820 [1+1] (no margin 29/30 0.847) | 20/30 0.601 [1+9] | 30/30 0.874 (+2 s) |
| worst | 30 | 1.2x | 23/30 0.687 [1+6] (no margin 24/30 0.714) | 24/30 0.714 [1+5] (no margin 25/30 0.740) | 18/30 0.508 [1+11] | 26/30 0.767 [1+3] (no margin 27/30 0.794) |
| worst | 30 | 1.4x | 21/30 0.631 [1+8] (no margin 22/30 0.660) | 22/30 0.660 [1+7] (no margin 23/30 0.687) | 18/30 0.508 [1+11] | 25/30 0.740 [1+4] (no margin 27/30 0.794) |
| worst | 30 | 1.6x | 20/30 0.601 [1+9] | 21/30 0.631 [1+8] | 18/30 0.508 [1+11] | 25/30 0.722 [1+4] (no margin 26/30 0.748) |
| worst | 40 | srv | 35/40 0.773 [1+4] (no margin 36/40 0.793) | 39/40 0.853 [1+0] (no margin 40/40 0.873) | 28/40 0.631 [1+11] (no margin 30/40 0.673) | 40/40 0.873 (+176 s) |
| worst | 40 | 1.0x | 35/40 0.773 [1+4] (no margin 36/40 0.793) | 38/40 0.833 [1+1] | 26/40 0.586 [1+13] (no margin 27/40 0.608) | 40/40 0.873 (+40 s) |
| worst | 40 | 1.2x | 31/40 0.693 [1+8] (no margin 32/40 0.713) | 33/40 0.733 [1+6] (no margin 34/40 0.753) | 24/40 0.508 [1+15] | 35/40 0.773 [1+4] (no margin 36/40 0.793) |
| worst | 40 | 1.4x | 28/40 0.631 [1+11] (no margin 29/40 0.653) | 30/40 0.673 [1+9] (no margin 31/40 0.693) | 24/40 0.508 [1+15] (no margin 25/40 0.528) | 35/40 0.773 [1+4] (no margin 36/40 0.793) |
| worst | 40 | 1.6x | 26/40 0.586 [1+13] (no margin 27/40 0.608) | 28/40 0.631 [1+11] | 24/40 0.508 [1+15] (no margin 25/40 0.528) | 34/40 0.736 [1+5] (no margin 35/40 0.756) |
| worst | 50 | srv | 44/50 0.776 [1+5] (no margin 45/50 0.792) | 48/50 0.840 [1+1] (no margin 49/50 0.856) | 35/50 0.630 [1+14] (no margin 36/50 0.648) | 50/50 0.872 (+128 s) |
| worst | 50 | 1.0x | 43/50 0.760 [1+6] (no margin 44/50 0.776) | 46/50 0.808 [1+3] (no margin 47/50 0.824) | 33/50 0.594 [1+16] | 49/50 0.856 [1+0] (no margin 50/50 0.872) |
| worst | 50 | 1.2x | 38/50 0.680 [1+11] (no margin 39/50 0.696) | 42/50 0.744 [1+7] (no margin 43/50 0.760) | 30/50 0.506 [1+19] | 43/50 0.760 [1+6] (no margin 45/50 0.792) |
| worst | 50 | 1.4x | 35/50 0.630 [1+14] | 36/50 0.648 [1+13] (no margin 37/50 0.664) | 30/50 0.506 [1+19] (no margin 31/50 0.521) | 43/50 0.760 [1+6] (no margin 44/50 0.776) |
| worst | 50 | 1.6x | 32/50 0.577 [1+17] (no margin 33/50 0.594) | 34/50 0.612 [1+15] | 30/50 0.506 [1+19] (no margin 31/50 0.521) | 42/50 0.724 [1+7] (no margin 44/50 0.756) |

**per-configuration mean case seconds on the 50 synthetic new problems (moot-skip bundles at the public-row moot rate):**

| bundle | speed | Qwen | Skywork | Olmo | DeepSeek | val-mix mean | worst-mix mean |
|---|---|---|---|---|---|---|---|
| v96 | srv | 176 | 131 | 199 | 174 | 171 | 185 |
| v96 | 1.0x | 191 | 141 | 189 | 191 | 180 | 191 |
| v96 | 1.2x | 206 | 166 | 222 | 206 | 201 | 213 |
| v96 | 1.4x | 207 | 191 | 255 | 207 | 214 | 228 |
| v96 | 1.6x | 207 | 216 | 288 | 207 | 226 | 242 |
| v105 | srv | 151 | 131 | 199 | 154 | 158 | 172 |
| v105 | 1.0x | 167 | 141 | 189 | 166 | 166 | 176 |
| v105 | 1.2x | 176 | 166 | 222 | 176 | 184 | 196 |
| v105 | 1.4x | 182 | 191 | 255 | 177 | 199 | 212 |
| v105 | 1.6x | 175 | 216 | 288 | 176 | 208 | 224 |
| v108 | srv | 151 | 244 | 290 | 154 | 201 | 211 |
| v108 | 1.0x | 167 | 266 | 315 | 166 | 220 | 230 |
| v108 | 1.2x | 176 | 299 | 347 | 176 | 239 | 249 |
| v108 | 1.4x | 182 | 314 | 344 | 177 | 244 | 250 |
| v108 | 1.6x | 175 | 328 | 347 | 176 | 245 | 249 |
| v110 | srv | 137 | 131 | 199 | 136 | 149 | 163 |
| v110 | 1.0x | 149 | 141 | 189 | 149 | 156 | 166 |
| v110 | 1.2x | 157 | 166 | 222 | 157 | 173 | 185 |
| v110 | 1.4x | 157 | 191 | 227 | 157 | 179 | 187 |
| v110 | 1.6x | 157 | 216 | 231 | 157 | 185 | 189 |

**sensitivity: 200 random case orders x random problem draws, budget with margin: mean answered (worst draw)**

| mix | N | speed | v96 | v105 | v108 | v110 |
|---|---|---|---|---|---|---|
| val | 30 | srv | 28.5 (27) 0.714 | 30.0 (29) 0.751 | 23.9 (21) 0.598 | 30.0 (30) 0.752 |
| val | 30 | 1.0x | 27.0 (26) 0.674 | 29.3 (28) 0.733 | 21.9 (20) 0.547 | 30.0 (30) 0.752 |
| val | 30 | 1.2x | 24.1 (23) 0.603 | 26.5 (25) 0.662 | 20.0 (18) 0.486 | 28.0 (27) 0.703 |
| val | 30 | 1.4x | 22.6 (22) 0.566 | 24.4 (23) 0.609 | 19.6 (17) 0.476 | 27.0 (26) 0.675 |
| val | 30 | 1.6x | 21.3 (20) 0.534 | 23.2 (21) 0.579 | 19.5 (17) 0.474 | 26.1 (25) 0.643 |
| val | 40 | srv | 38.3 (37) 0.723 | 40.0 (40) 0.756 | 32.0 (30) 0.605 | 40.0 (40) 0.756 |
| val | 40 | 1.0x | 36.3 (35) 0.687 | 39.3 (37) 0.744 | 29.3 (27) 0.553 | 40.0 (40) 0.756 |
| val | 40 | 1.2x | 32.5 (31) 0.615 | 35.4 (33) 0.670 | 26.8 (24) 0.489 | 37.7 (36) 0.711 |
| val | 40 | 1.4x | 30.5 (29) 0.576 | 32.8 (31) 0.620 | 26.2 (23) 0.479 | 36.2 (35) 0.684 |
| val | 40 | 1.6x | 28.7 (27) 0.541 | 31.1 (29) 0.587 | 26.1 (23) 0.476 | 34.9 (34) 0.651 |
| val | 50 | srv | 48.2 (47) 0.733 | 50.0 (50) 0.759 | 40.6 (38) 0.618 | 50.0 (50) 0.759 |
| val | 50 | 1.0x | 45.7 (44) 0.695 | 49.5 (48) 0.752 | 37.3 (35) 0.568 | 50.0 (50) 0.759 |
| val | 50 | 1.2x | 41.0 (40) 0.623 | 44.8 (43) 0.680 | 34.1 (31) 0.503 | 47.5 (46) 0.722 |
| val | 50 | 1.4x | 38.4 (37) 0.585 | 41.3 (39) 0.628 | 33.4 (31) 0.493 | 45.8 (44) 0.695 |
| val | 50 | 1.6x | 36.2 (35) 0.552 | 39.3 (37) 0.598 | 33.3 (30) 0.491 | 44.2 (43) 0.663 |
| worst | 30 | srv | 26.1 (25) 0.760 | 28.1 (26) 0.818 | 22.7 (21) 0.660 | 29.6 (29) 0.861 |
| worst | 30 | 1.0x | 25.3 (25) 0.737 | 27.4 (26) 0.799 | 20.8 (18) 0.607 | 29.1 (28) 0.847 |
| worst | 30 | 1.2x | 22.6 (22) 0.657 | 24.7 (23) 0.718 | 19.2 (17) 0.528 | 26.1 (25) 0.760 |
| worst | 30 | 1.4x | 21.1 (20) 0.615 | 22.7 (21) 0.661 | 19.1 (17) 0.526 | 25.8 (25) 0.750 |
| worst | 30 | 1.6x | 19.8 (19) 0.577 | 21.5 (19) 0.625 | 19.2 (17) 0.528 | 25.5 (25) 0.725 |
| worst | 40 | srv | 35.3 (34) 0.770 | 38.0 (36) 0.830 | 30.9 (28) 0.673 | 39.9 (39) 0.870 |
| worst | 40 | 1.0x | 34.3 (33) 0.748 | 37.1 (35) 0.810 | 28.3 (25) 0.618 | 39.3 (38) 0.858 |
| worst | 40 | 1.2x | 30.6 (30) 0.668 | 33.3 (31) 0.727 | 26.1 (23) 0.538 | 35.4 (34) 0.772 |
| worst | 40 | 1.4x | 28.7 (27) 0.626 | 30.8 (29) 0.672 | 26.0 (23) 0.536 | 35.0 (34) 0.763 |
| worst | 40 | 1.6x | 27.0 (25) 0.589 | 29.2 (25) 0.636 | 26.1 (23) 0.539 | 34.7 (33) 0.738 |
| worst | 50 | srv | 44.4 (43) 0.774 | 47.7 (45) 0.832 | 38.7 (35) 0.674 | 49.9 (49) 0.870 |
| worst | 50 | 1.0x | 43.2 (42) 0.753 | 46.7 (44) 0.814 | 35.5 (32) 0.619 | 49.3 (48) 0.860 |
| worst | 50 | 1.2x | 38.5 (38) 0.672 | 41.9 (39) 0.731 | 32.7 (29) 0.539 | 44.3 (43) 0.772 |
| worst | 50 | 1.4x | 36.0 (34) 0.628 | 38.6 (36) 0.673 | 32.6 (29) 0.536 | 43.8 (42) 0.763 |
| worst | 50 | 1.6x | 33.8 (32) 0.589 | 36.5 (34) 0.636 | 32.7 (29) 0.538 | 43.4 (42) 0.738 |

**STD bundles with Skywork / Olmo problems that STD COVERS (public templates with a lane L program; the main table above uses synthetic problems = STD finds no usable code -> fallback), budget with margin:**

| mix | N | speed | v108 |
|---|---|---|---|
| val | 30 | srv | 30/30 0.818 (+157 s) |
| val | 30 | 1.0x | 27/30 0.738 [1+2] |
| val | 30 | 1.2x | 20/30 0.477 [1+9] |
| val | 30 | 1.4x | 19/30 0.440 [1+10] |
| val | 30 | 1.6x | 19/30 0.440 [1+10] |
| val | 40 | srv | 40/40 0.823 (+354 s) |
| val | 40 | 1.0x | 38/40 0.783 [1+1] |
| val | 40 | 1.2x | 27/40 0.476 [1+12] |
| val | 40 | 1.4x | 26/40 0.457 [1+13] |
| val | 40 | 1.6x | 26/40 0.454 [1+13] |
| val | 50 | srv | 50/50 0.832 (+343 s) |
| val | 50 | 1.0x | 47/50 0.784 [1+2] |
| val | 50 | 1.2x | 34/50 0.494 [1+15] |
| val | 50 | 1.4x | 33/50 0.472 [1+16] |
| val | 50 | 1.6x | 32/50 0.450 [1+17] |

**Answer changes of the new pair at the validation mix (per 21 main / 14 small cases)**

| bundle (vs parent) | speed | answers changed in the mock | quick finishes dropped | expected answer changes (public rows: 9 of 44) | accuracy cost on the 50-50 LOTO (0.017 per drop; 0 on the public-mix LOTO) |
|---|---|---|---|---|---|
| v109 (vs v104) | srv | 0.00 | 0.00 | 0.00 | -0.00 |
| v109 (vs v104) | 1.0 | 0.00 | 0.00 | 0.00 | -0.00 |
| v109 (vs v104) | 1.2 | 0.30 | 13.00 | 2.66 | -0.22 |
| v109 (vs v104) | 1.4 | 0.06 | 6.76 | 1.38 | -0.11 |
| v109 (vs v104) | 1.6 | 0.00 | 5.98 | 1.22 | -0.10 |
| v110 (vs v105) | srv | 0.32 | 8.00 | 1.64 | -0.14 |
| v110 (vs v105) | 1.0 | 0.32 | 8.00 | 1.64 | -0.14 |
| v110 (vs v105) | 1.2 | 0.00 | 8.00 | 1.64 | -0.14 |
| v110 (vs v105) | 1.4 | 0.12 | 4.16 | 0.85 | -0.07 |
| v110 (vs v105) | 1.6 | 1.86 | 3.68 | 0.75 | -0.06 |

**The nominees against their parents.** v109 and v110 against v104 and v105 (`board_mock.out`, `oldpath_check.out`,
`zip_mock.out`) [538]: on the board shape (seeds 1 and 2; 1.0x, 1.4x and 1.6x; budgets of 4,020 s and 3,390 s on main,
4,020 s and 2,200 s on small) every main answer is identical (21 of 21 in all 12 jobs); on small, answers are identical
at 1.0x and 1.4x, while at 1.6x two Olmo cases change on the 4,020 s budget (the own run stops at 232 s) and three or
four cases on the 2,200 s budget. On the old single-process path both pairs give identical answers (84 of 84). Built
from their zips, v109 answers 21 of 21 on the board shape at 1.0x (2,791 s) and 1.4x (3,172 s), and v110 14 of 14 (2,237
s and 2,561 s). v111 and v112 against v109 and v110 [540]: 24 paired board-shape jobs (seeds 1 and 2; 1.0x, 1.4x and
1.6x; the 4,020 s and the N × 170 − 180 s budgets) match in status and answer on all 420 cases, with times within 0.015
s; the old path gives 84 of 84; the final shapes are identical (main: every validation-mix case answered through 1.4x;
small: 27, 35 and 45 at 1.4x).

**The pre-mortem** (`work/miners18/premortem/`: `pm_*.py`, `patches/` with 15 files, `results/`) [539, 540]. Faults were
injected into temporary copies of each bundle running on the mock engine, with the real bundles untouched: 73 fault
classes in 129 variants, each against v95, v96, v104 and v105, in three passes. Case-level faults run one fresh process
per configuration; job-level faults run the whole per-case mock (21 or 14 cases, 4,020 s budget). The classes cover
model loading and memory (weights missing, out of memory at load or mid-generation, illegal memory access), failing
decode-path self-checks, chat-template errors, slow loads and a batch that ignores its deadline, degenerate readings
(NaN or infinite agreement, no finished attempt), odd problem texts (very long, empty, emoji, special tokens, lone
surrogates, control characters), output and file-system faults (stdout closed, broken pipe, full disk, read-only or
unwritable folders, an empty environment), odd call arguments, and job-level faults (a slow GPU at 1.6x to 3.0x, the
clock near the job end, a hung case, whole-job failures). Real-code checks ran `engine2.py`'s parser, prompts and
features on the CPU with the Qwen3.5-4B tokenizer (`transformers` 5.13.0).

Found in all four bundles: a stdout write that fails (broken pipe, full disk) crashes every case; a legacy positional
call, a non-string effort or an unhashable problem item crashes the call; `parse_answer` raises ValueError on an answer
above 4,300 digits (Python's integer-string limit; found in the real code) and costs the whole batch; out of memory on a
lone problem drops the whole gpt-oss reading, because the handler needs more than one problem; and a budget variable of
'0' is read as a zero budget, so every case is answered robust. Timeouts: v95 answers 18 of 21 at 2.0x and 17 of 21 at
2.5x (v104 21 of 21); with slow loads at 2.5x, 17 of 21 on both main bundles; the job-end clock and a stuck case cannot
be fixed inside a case.

Fixes, written as patches and not applied to v95, v96, v104 or v105: F1, logging never raises; F2, argument handling;
F3, out of memory halves K, down to K_min, and retries; F4, a digit-limit fallback; F5, '0' is not a budget. F1 to F5
are answer-identical without a fault (16 board jobs identical); the optional F6 (a watchdog) and F7 (a speed-aware quick
finish) were not adopted. Ported onto v109 and v110 as v111 and v112, they cut invalid outcomes in the fault catalogue
from 42 to 24 (main) and from 17 to 5 (small): F1 and F2 crashes 30 → 0, a lone-problem out of memory keeps the gpt-oss
reading, a '0' variable takes the normal path and 5,000-digit answers parse. The remaining 29 are job-level timeouts.
Cost: a repeating out-of-memory error adds about 60 s per case [540].

### Addendum of 18 October

*Added for draft 26 of the report, after the nominees' board runs; the report's Appendix E.17 summarises it, and
Appendix D counts lane K as group 10.*

**Lane K: a small-track time trade** [553, 554] (`work/miners18/laneK/`: `PREREG_laneK.txt`, `ADDENDUM_K.txt`,
`k_trade.py` → `k_trade.out`, `RESULT_K.md`; CPU, logged readings only, no model run; accuracy measured on public rows
with the stand-in's models refitted leave-one-template-out; times model-based, from lane F2's server-calibrated
tables):

| Lane | Reading or premise | Bar | Measured | Verdict |
|---|---|---|---|---|
| K [553, 554] | B: K 9 (fixed from the time model before any accuracy) plus the Qwen quick finish and the full model, against A: K 32 agreement-only (v112's deployed model), on the small stand-in rows | K1 B − A ≥ +1 expected row with no loss on fresh rows; K2 B above A in at least 3 of 4 reads; K3 a shuffled quick finish must not beat A | v112's line (22 rows): −1.40 (reads −1.69, −1.64, −1.09, −1.19; fresh −0.21); v114's line (25 rows): −1.93 (reads −2.07, −1.93, −2.25, −1.47; fresh −0.72); K2 0 of 4; K3 −2.70 and −3.75 | failed (K1, K2); K3 passed; v112 and v114 keep K 32 |

The four reads come from two gpt-oss pools (two K 16 reads pooled per job), so they are not four independent reads. K
13 and K 16 also miss the bar (B − A −0.10 / −0.32 and +0.18 / −0.04 on the two lines), and K 16 does not fit 165 s.

**The pre-mortem's fault list** (moved verbatim from the report's Appendix E.17 in draft 26 [539, 540]):

The pre-mortem's server-reachable
bugs: an answer above 4,300 digits makes `parse_answer` raise and loses the batch; out of memory on a lone problem drops
the whole gpt-oss reading; a failing stdout write crashes every case. Its other faults: a legacy positional call or
non-string effort, unhashable problem items, and a budget variable of 0 read as a zero budget. After the fixes a problem
text with a lone surrogate character still loses every reading, though the case stays valid (`pm_table_all.md`, P11); a
repeating out-of-memory error adds about 60 s per case.

### Addendum of 20 October

*Added for draft 27 of the report [572-576]. Board numbers are OFFICIAL board (one draw each, on the validation cases,
not new problems); replica numbers are model-based; mock numbers are mock.*

**Lane F4: the per-case-limit variants v115 and v116** (`work/miners18/laneF4/`; `f4_build.py` builds the bundles,
`f4_sim.py` → `f4_sim.out` holds the replica tables, `f4_bench.out` its checks, `f4_zipcheck.out` and `f4_sens.out`
real-code mock checks).

*Why* [572]. On 19 October another team asked the organisers on GitHub (getting-started issue #6) whether the final's
"170 seconds per sample" is an average over the run or a limit on each case. If it is a per-case limit, the nominees'
longest cases would time out: on the board v111's two Olmo cases took 209 s and four stand-in cases 173 to 179 s, and
v112's three Olmo cases 173, 210 and 210 s (server, `work/miners18/boardkit/out_18oct/`).

*What changes* (`f4_build.py`; `params.json` only, plus the `solution.py` docstring and log tag; every other file is
byte-identical to the parent):

| `params.json` key | v111 → v115 (`sub_v129m` → `sub_v135m`) | v112 → v116 (`sub_v130s` → `sub_v136s`) |
|---|---|---|
| `case_target_seconds` (stand-in) | 210 → 165 | 165 (unchanged) |
| `own_case_target_seconds` | 400 → 160 | 232 → 160 |
| `own_plan_seconds` (own runs still planned at K 3) | absent → 400 | 400 (unchanged) |
| `own_load_seconds_est` | 25 → 0 | 25 → 0 |
| Olmo own-run cap (`sky` → `cap`) | 10,000 → 7,200 | 10,000 → 7,200 |

With `own_load_seconds_est` 25 the pre-load check would skip Skywork's own run at a 160 s target. Olmo's rule (robust
iff at least 2 of 3 attempts end on their own) is unchanged; at the shorter cap fewer attempts end.

*Replica* [573]. `f4_model.py` replays each case's route from the logged readings of the 18 October runs (state A) and
the 16 October runs (state B); it reproduces 126 of 126 measured server cases and 1,056 of 1,056 real-code mock cases
(`f4_bench.out`). Under a 170 s per-case limit, on the board cases at measured speed (state A), v111 answers 15 of 21 and
v112 11 of 14; v115 and v116 answer every case at 1.0x to 1.2x (longest case 154 s at 1.0x, 160 s at 1.2x). The finals,
copied from `f4_sim.out` with only the headings demoted (board-like order; in brackets the mean and minimum over random orders):

#### FINALS N x 170 s, per-case limit 170 s, state A (18 Oct readings), budget N x 170 - 180 s: answered of N, board-like order [random orders: mean (min)]

| track | mix | bundle | speed | N 30 | N 40 | N 50 | mean case s | max case s |
|---|---|---|---|---|---|---|---|---|
| main | val | v111 | x1.0 | 19 [22.0 (16)] | 30 [29.3 (22)] | 36 [36.4 (28)] | 121 | 210 |
| main | val | v111 | x1.1 | 20 [21.3 (15)] | 26 [28.3 (17)] | 32 [35.1 (27)] | 130 | 231 |
| main | val | v111 | x1.2 | 25 [23.2 (17)] | 29 [30.7 (23)] | 38 [38.3 (31)] | 134 | 252 |
| main | val | v115 | x1.0 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 105 | 155 |
| main | val | v115 | x1.1 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 113 | 160 |
| main | val | v115 | x1.2 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 117 | 160 |
| main | worst | v111 | x1.0 | 16 [15.8 (8)] | 20 [20.8 (14)] | 25 [25.8 (18)] | 158 | 210 |
| main | worst | v111 | x1.1 | 11 [14.6 (8)] | 17 [19.3 (12)] | 22 [23.8 (14)] | 171 | 231 |
| main | worst | v111 | x1.2 | 15 [17.1 (9)] | 24 [22.5 (16)] | 27 [27.9 (21)] | 176 | 252 |
| main | worst | v115 | x1.0 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 132 | 155 |
| main | worst | v115 | x1.1 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 140 | 160 |
| main | worst | v115 | x1.2 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 143 | 160 |
| small | val | v112 | x1.0 | 24 [24.0 (24)] | 31 [31.0 (31)] | 39 [39.0 (39)] | 136 | 210 |
| small | val | v112 | x1.1 | 24 [24.0 (24)] | 31 [31.0 (31)] | 39 [39.0 (39)] | 148 | 231 |
| small | val | v112 | x1.2 | 24 [24.0 (24)] | 31 [31.0 (31)] | 39 [39.0 (39)] | 154 | 232 |
| small | val | v116 | x1.0 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 126 | 155 |
| small | val | v116 | x1.1 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 135 | 160 |
| small | val | v116 | x1.2 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 139 | 160 |
| small | worst | v112 | x1.0 | 17 [17.0 (17)] | 23 [23.0 (23)] | 28 [28.0 (28)] | 159 | 210 |
| small | worst | v112 | x1.1 | 17 [17.0 (17)] | 23 [23.0 (23)] | 28 [28.0 (28)] | 173 | 231 |
| small | worst | v112 | x1.2 | 17 [17.0 (17)] | 23 [23.0 (23)] | 28 [28.0 (28)] | 177 | 232 |
| small | worst | v116 | x1.0 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 137 | 155 |
| small | worst | v116 | x1.1 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 145 | 160 |
| small | worst | v116 | x1.2 | 30 [30.0 (30)] | 40 [40.0 (40)] | 50 [50.0 (50)] | 148 | 160 |

What v115 / v116 give up if 170 s is only an average (answer changes against v111 / v112 at the same speed, no limit;
c is the chance that a dropped quick finish changes the answer), copied from `f4_sim.out` in the same way:

#### ANSWER CHANGES on the BOARD cases (v115 vs v111, v116 vs v112; same speed, no limit; state A = 18 Oct inputs)

| track | speed | quick finishes dropped (same reading) | readings differ | Olmo cases that can flip | E[changes] c=0.10 / 0.23 / 0.47 (Olmo emp / mock) |
|---|---|---|---|---|---|
| main | x1.0 | 5 | 0 | 0 | 0.50 (0.50) / 1.16 (1.16) / 2.37 (2.37) |
| main | x1.1 | 8 | 0 | 0 | 0.80 (0.80) / 1.85 (1.85) / 3.79 (3.79) |
| main | x1.2 | 5 | 7 | 0 | 0.50 (0.50) / 1.16 (1.16) / 2.37 (2.37) |
| small | x1.0 | 0 | 0 | 1 | 0.19 (0.41) / 0.19 (0.41) / 0.19 (0.41) |
| small | x1.1 | 0 | 0 | 1 | 0.36 (0.48) / 0.36 (0.48) / 0.36 (0.48) |
| small | x1.2 | 0 | 2 | 1 | 0.75 (0.65) / 0.75 (0.65) / 0.75 (0.65) |

#### EXPECTED ANSWER CHANGES per 21 main / 14 small cases of the VALIDATION mix on new problems (draws from the measured pool, state A, no limit)

| track | speed | qfin drops /N | readings differ /N | Olmo expected flips /N (emp / mock) | E[changes] /N, c = 0.10 / 0.23 / 0.47 (Olmo emp) | same, Olmo mock |
|---|---|---|---|---|---|---|
| main | x1.0 | 5.56 | 0.00 | 0.23 / 0.41 | 0.79 / 1.52 / 2.87 | 0.97 / 1.69 / 3.04 |
| main | x1.1 | 5.12 | 1.72 | 0.47 / 0.51 | 0.99 / 1.66 / 2.90 | 1.02 / 1.70 / 2.94 |
| main | x1.2 | 3.78 | 6.34 | 0.76 / 0.67 | 1.13 / 1.63 / 2.55 | 1.05 / 1.55 / 2.46 |
| small | x1.0 | 0.00 | 0.00 | 0.35 / 0.61 | 0.35 / 0.35 / 0.35 | 0.61 / 0.61 / 0.61 |
| small | x1.1 | 0.00 | 0.00 | 0.71 / 0.77 | 0.71 / 0.71 / 0.71 | 0.77 / 0.77 / 0.77 |
| small | x1.2 | 0.00 | 1.80 | 1.13 / 1.01 | 1.13 / 1.13 / 1.13 | 1.01 / 1.01 / 1.01 |

*Decision logic* [573, 576]: if the limit is per case, v111 loses about 29% of the cases; if it is an average, v115
costs about 3%, so v115 is the better single choice unless the chance of a per-case limit is below about 9 to 10%. With
several nominations per track: v111 and v115 on main, v116 and v112 on small (`NOMINATION_SHEET.md`, 19 October).

*Board runs* (OFFICIAL board, 19 October): v115 (Codabench 1003729) 15 of 21 (0.7143), 21 of 21 answered, 0 invalid,
job 2,288 s, longest case 148 s (Olmo 147 to 148 s, stand-in 97 to 142 s) [576]; v116 (1003727) 9 of 14 (0.6429), 14 of
14 answered, job 1,720 s, longest case 147 s (Olmo 146 to 147 s, stand-in 84 to 145 s; `runs/v116_small_1003727.log`)
[575]. v115's log was read on the site and not archived; its calls were compared with v111's as strings: they differ in
exactly two calls, both on stand-in routes where gpt-oss's agreement reading differed between the 18 and 19 October runs
(the fast path's greedy check read 1.000 on 18 October and 0.995 on 19 October; one case's quick finish became moot,
another's ran); no Olmo, Skywork or prior call changed [576]. On small, the 7,200 cap made all three Olmo cases end 0 of
3, where v112 had one at 3 of 3 (robust) [575]. No case-level label inference is made.

*Zips*: `f4_zipcheck.out` runs the unzipped `dist/` files against the bundle folders in the recalibrated mock (PASS,
identical on every board shape, seed, speed and state). `release_public_v111/v115_v116/` rebuilds both zip md5s byte for
byte from a fresh copy (report, Appendix F.8).

**Text moved out of the report in draft 27** (verbatim, from draft 26):

From Section 4.5:

**Nominees.** v111 is v95 plus two skips of Qwen's quick finish (when it cannot change the answer, and when the case
clock has cut the gpt-oss reading) and fixes F1 to F5. In the mock it gives v95's answers at server speed and 1.0x, and
1.2 to 2.7 expected answer changes per 21 at 1.2x to 1.6x (against v104). v112 adds to v96 the same, a 165 s stand-in
target and own runs stopped at 232 s: about 1.6 expected answer changes per 14 small cases, −0.14 case per 14 at a 50-50
class mix (model-based) [538]. **Second nominees** v113 and v114 read Skywork's cases with the stand-in (Section 2.3;
public rows: Appendix E.17) [544]. In the mock no other answer differs and no case is lost.

**Pre-mortem.** 73 fault classes injected into v95, v96, v104 and v105 (mock; CPU checks of the real code) found three
bugs reachable on the contest server and three faults of unusual calls or environments (Appendix E.17) [539]. F1 to F5
change no answer without a fault and cut invalid outcomes from 42 to 24 (main) and 17 to 5 (small); the other 29 are
job-level timeouts [540].

**Board runs** (OFFICIAL board, one draw each) [556-564]: v111 17 of 21, v113 16, v112 9 of 14 and v114 8 (v96: 10 of
the same 14), every case answered, at about 125 s per main and 135 s per small case against the final's 170 s (v96:
about 162 s). By 13:25 UTC on 18 October the site had not scored v111's first run (1000213); a re-run (1000991) made
identical calls.

From Appendix E.17:

**Mock details behind Section 4.5** [538-540]. At N 40 and 1.4x, expected accuracy (lane F's in-sample model) is 0.702
for v95 against 0.790 for v111, and 0.551 for v96 against 0.656 for v112. v104 is safe to 1.4x, v105 only at server
speed. At N × 170 s v108 loses cases at every speed; v107 answers every validation-mix case at server speed and 1.0x but
loses cases from 1.2x. Against v104, v111's clock-cut skip changes −0.10 to −0.22 case per 21 at 1.2x to 1.6x with a
50-50 class mix (model-based), and nothing on the public-mix leave-one-template-out. The pre-mortem's bugs and faults,
one by one, are in `report_supplement/E17_announced_final.md` (addendum of 18 October).

**The second nominees** [544]. v113 and v114 (`sub_v131m`, `sub_v132s`) give Skywork's own-run spec an empty
`apply_cfgs`, so a Skywork case takes the stand-in route at strength 1; `solution.py` differs only in its docstring and
log tag. In `work/miners18/v113/`: `pub_rows.out` (lane G's machinery) shows on main only Skywork rows changing, T13
(non-robust) fixed in every read and T16 (robust) fixed in the dress read (60 → 62 of 71) and broken in the fifth. On
public rows (measured, leave-one-template-out, five reads) v113 gains +2, +1, +1, +1 and 0 rows over v111, and v114 the
same with the quick finish and +1, 0, +1, +1 and −1 with the agreement-only model that decides its Skywork cases in the
mock. `final_shapes_v113.out`: non-Skywork cases identical in answer, validity and path on 1,500 main and 750 small case
runs; small at 1.4x answers 28, 37 and 47 of 30, 40 and 50 (v112: 27, 35, 45); in 200 random orders v113 answers one
case fewer than v111 once (worst mix, N 50, 1.0x; 0.07 s short; `knife_edge.out`). `board_mock_v113.out`,
`oldpath_v113.out` and `zip_mock_v113.out`: no fewer cases on board shapes, multi-call answers differing only on
Skywork, zips that run as their bundles.

### Addendum of 20 October (draft 28)

*Added for draft 28 of the report: three lanes run on 20 October on the CPU from held logs (no uploads; Appendix D, group 11), and text moved out of the report's Section 4.5 (verbatim, from draft 27).*

**Lane OLMO-CAP** [584] (`work/miners19/laneOlmo/`: `PREREG_olmo.txt`, then `ADDENDUM_olmo.txt` written before any
metric; `olmo_cap.py` → `olmo_cap.out`). Question: at v115 / v116's 7,200-token Olmo cap, does another vote threshold or
a length rule reproduce the 10,000-token rule's calls? Data: 72 public Olmo attempts on 31 problems (37 ended under
10,000 tokens). Bar A1: the chosen rule agrees with the 10,000-token rule on at least 90% of resampled K 3 groups and
beats the deployed rule (at least 2 of 3 attempts end) by at least 10 points. Result: at least 1 of 3 agrees 0.959
against 0.911, +4.8 points (problem-bootstrap 95% interval 0.000 to +0.128): FAIL; A2 to A4 passed. Under the deployed
rule 21% of the problems robust at 10,000 tokens flip to non-robust at 7,200 (14% on the exact part), about one call per
40 small cases (model-based). The one board Olmo case that was 3 of 3 at 10,000 tokens had all three attempts end
between 7,200 and 8,362 tokens: no threshold recovers it, only a longer cap or faster decoding. v115 / v116 unchanged.

**Lane SMALL** [587] (`work/miners19/laneSmall/`: `PREREG_small.txt`, then `ADDENDUM_small.txt` written before any fit;
`r_small.py` → `r_small.out`). Question: does the stand-in's logistic rule refitted on the 34 small-model rows (S1), or
with a per-configuration intercept (S2), read those rows better? Bars: B1 leave-one-template-out at least 2 rows above
the v112 line (28 of 34); B2 fresh small rows not worse; B3 a within-configuration label shuffle reaches B1's gain in at
most 5% of 200 draws; B4 B1 holds on at least 2 independent reads. Result: S1 and S2 both 28 of 34 (+0) on the dress
read and +0 on the four other reads (S2 breaks one fresh row on one read): FAIL on B1 and B4; B2 passed, B3 only
trivially. The remaining stand-in errors are T05 rows whose reading looks non-robust. No v117 was built.

**Lane REFILL** [586, 590] (`work/miners19/refill/`: `refill.py` → `refill.out`; no bar was set). Question: would
refilling the stand-in batch's finished slots with new attempts, or two staged shorter batches, buy accuracy at the same
time? Result (model-based, from public per-attempt lengths and 77 server batches): slot utilisation is 0.70 (median of
26 board readings); decoding is bound by reading the weights (86% of a step's cost is fixed), so at the same step budget
refill raises K from 32 to about 34 (24 with a 25% bookkeeping cost), worth +0.000 to +0.005 stand-in accuracy, and it
biases the reading toward short attempts; staged batches lose 0.106 accuracy at 1,500 steps (95% interval −0.227 to
−0.020) and cost 1.7 to 1.9 times the time at 2,000 to 2,500 steps. Not built.

**Text moved out of the report in draft 28** (verbatim, from draft 27):

*From Section 4.5:*

**Public-default variants** v113 and v114 read Skywork's cases with the stand-in (Section 2.3;
Appendix E.17) [544]; in the mock no other answer differs and no case is lost.

A mix with no gpt-oss high or Skywork cases still costs v111 2 or 3 cases at 1.0x (expected accuracies: Appendix E.17)
[538].

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Section 5.1:*

**Slot refill did not pay** (no bar; computed from held logs) [590]: refilling the stand-in batch's finished slots
raises K from 32 to only about 34 at the same step budget, since decoding is weight-bound (86% of a step's cost is
fixed), and it biases the reading toward short attempts; staged shorter batches lose accuracy (−0.106 at 1,500 steps).

*From Section 4.5:*

**A per-case limit?** Whether "170 seconds per sample" is a job average or a per-case limit is unanswered (another team
asked on GitHub, issue #6, 19 October) [572]. Under such a limit v111's board run would lose 6 of 21 cases (two Olmo
cases at 209 s, four stand-in cases at 173 to 179 s) and v112's 3 of 14 (server times) [573]. v115 and v116 stop own
runs at 160 s and cap Olmo at 7,200 tokens (v115 also targets 165 s on stand-in cases): 15 of 21 and 9 of 14 on the
board, no case over 148 s [575, 576]. v115's two calls that differ from v111's are stand-in cases whose gpt-oss reading
changed between days: reading noise (Section 2.6) [576]. The shorter Olmo cap costs about one call per 40 small cases
(model-based): on 72 public attempts, 21% of problems robust at 10,000 tokens flip to non-robust at 7,200, and a
pre-registered threshold refit missed its bar (+4.8 points against +10) [584].

*From Appendix E.17:*

**The board runs** [556-564] (`work/miners18/boardkit/analyse_board_run.py` [552]; totals and per-case times only).
Jobs: v111 2,634 s, v113 2,620 s, v112 1,913 s, v114 1,882 s, none invalid; v111, v113, v112 and v114 took 0.950, 0.922,
0.918 and 0.893 of the server-calibrated mock's time (`work/miners18/boardkit/out_18oct/`) [557, 558]. On small the
165 s target skipped the quick finish on 4 stand-in cases in both files; lane F3 kept it [559]. Projected from measured
times (model-based), every validation-mix case is answered at N 30 to 50. v111's first run (1000213) answered every case
in 2,638 s but was still unscored 10 h later [562, 563]; its re-run (1000991) made identical calls [564]. v113 differs
from v111 only on Skywork's cases, the route the board chose (Section 2.3), so this board cannot rank the two.

*From Appendix E.17:*

**Two server states** [566] (computed from the logs; v95's and v96's archived on 18 October: `runs/v95_main_991447.log`,
3,030 s; `runs/v96_small_991452.log`, 2,265 s). On 16 October gpt-oss low's compacting-loop check failed on all 13
stand-in cases of v95 and all 8 of v96, so neither compaction nor the fast path ran (49 to 63 ms per step), and the case
clock skipped 5 and 4 of their quick finishes. On 18 October the same check, in identical code, passed on every stand-in
case of v111 to v114 (39 to 49 ms per step; no main quick finish skipped for time). The two days' readings are different
samples, so one-case board differences between them are not design effects.

*From Appendix E.17:*

**The second nominees of 18 October** [544]. v113 and v114 (`sub_v131m`, `sub_v132s`) give Skywork's own-run spec an
empty `apply_cfgs`, so a Skywork case takes the stand-in route at strength 1. On public rows (measured,
leave-one-template-out, five reads) only Skywork rows change: T13 (non-robust) fixed in every read and T16 (robust)
fixed in the dress read and broken in the fifth; v113 gains +2, +1, +1, +1 and 0 rows over v111. In the mock no other
case changes and none is lost (`work/miners18/v113/`; full text: `report_supplement/E17_announced_final.md`, addendum of
20 October).
