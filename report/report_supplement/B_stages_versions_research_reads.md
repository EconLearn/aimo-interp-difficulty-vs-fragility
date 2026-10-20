# Supplement to the technical report: Appendix B in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 17 October: the versions v109 to v114 (Section 4.5 of the report) are listed in the report's Appendix B only. Note
added 17 October, later: below, "the final files" are the files scored on 15 and 16 October (v95, v96); the nominees for
the final are v111 to v114 (Section 4.5 of the report). Note added 18 October: the v102 row's 'log not read at writing'
is superseded; the log was read on 18 October [555] (Section 6.4 of the report).*

## Appendix B. Stages, versions and research reads

**Board path by stage** (main board; H1 unless marked; Section 4.1):

| Stage | Change | Main board | Ledger |
|---|---|---|---|
| Stand-in | one reading for all configurations | 13 to 16 (eleven runs, mean 14.9) | Appendix A.1 |
| +High prior | gpt-oss high answered from its public prior | 16 | [338] |
| +Olmo own | Olmo's own run on Olmo cases | 17 (same-seed rerun 17) | [342, 345] |
| +Skywork own | Skywork's own run on Skywork cases | 19 (same-seed rerun 19) | [350, 352] |
| +Coverage | coverage-first planning (Appendix E.4); same readings at board scale | 19 (same draw as +Skywork own [363]) | [362] |
| +Fast 7B | fast 7B decode path; same seeds | 17, same per-configuration counts as +Coverage | [369] |
| +Fast 7B, fresh seeds | every seed shifted by 7777 / by 424242 | 18 / 16 | [384, 385, 393] |
| **H2:** +Skywork own, rerun not by us | v65 under the per-case harness | 14, with 2 of 21 cases invalid (case 20 timed out, case 21 skipped) | [464, 468] |
| **H2:** per-case rebuild (v95) | v83's decision rules, one process per case (Section 4.2) | 16, every case complete | [466, 471] |

The later H1 stages are not scored. Under the per-case harness the same rules sit at or below the bottom of the H1 draws
(16 to 19): 14 in the organisers' rerun of +Skywork own, with 2 cases invalid (so 14 right of the 19 cases it
answered), and 16 for v95 [464, 471]; the rerun ran a design that did not fit the harness.

Stages in order: Stand-in, +High prior, +Olmo own, +Skywork own, +Coverage, +Fast
7B, then the three final-shape stages +Skywork K 3, +Stand-in depth and +First-call cap (Section 4.1). A version's zip
is `work/dist/aimo_<version>_main.zip` (or `_small.zip`). Under the original harness the fallback order is +Stand-in
depth, +Skywork K 3, +Fast 7B; under the per-case harness the final files are v95 and v96 (Sections 4.2 and 10).

| Name in the text | Version | Bundle | Zip md5 | Board |
|---|---|---|---|---|
| Stand-in (nominated until 11 Oct) | v22 | `sub_v28m` | 8462d4b2cb2df5f6a631964f5e72cd4c | 14; cross-day copy 15 |
| +High prior | v60 | `sub_v75m` | 769f30e23a9045a196b3fb30e0bc70de | 16 |
| +Olmo own | v62 (rerun v62r) | `sub_v77m` | 2d9fbbbf361393eb65ca08e6f9371572 | 17, 17 |
| +Skywork own | v65 (rerun v65r) | `sub_v80m` | 24767cda3c4356e8b94bd98afe10de3c | 19, 19 |
| +Coverage | v67 | `sub_v82m` | b8c88f74bcb32aa1a226540650b31a43 [355] | 19 |
| +Fast 7B | v70 | `sub_v86m` | 9790692eb26fa78f09843b8f101c7fac [368] | 17 |
| +Fast 7B, fresh seeds 1 and 2 | v77, v78 | `sub_v95m`, `sub_v96m` | 0c2c3090..., 7004fc04... [384] | 18, 16 [393] |
| +Skywork K 3 (main candidate until v80; now second fallback) | v74 | `sub_v92m` | e8531c64821ed02e48cc5388ae08f51b | not scored |
| +Stand-in depth (main candidate until v83; now first fallback) = v74 + `future_new_factor` 0.25 | v80 | `sub_v98m` | 72d69c2c3874bfba2a05edd4ccb6e580 [395] | not scored; dress passed [404] |
| **+First-call cap (main nominee under the original harness)** = v80 + `first_call_K_max` 16 when call 1 has ≥ 10 problems (`first_call_cap_min_problems` 10) | v83 | `sub_v101m` | f93ef76c44d0733b22b5282e4c9b3e6a [406] | not scored on the board; its own dress rehearsal (Codabench 987666): 61/71 labelled public rows, end 2,916 s, every own case read [440] |
| Small recipe as at +Skywork own, +Coverage, +Fast 7B | v66, v68, v71 | `sub_v81s`, `sub_v84s`, `sub_v87s` | 7b88a61f..., 62c0e944..., 0633c0cf35c493b8b5a1a4f521bd10e7 [368] | 9, 8, 8 |
| Small candidate until v82 (+Skywork K 3); now the second small fallback | v76 | `sub_v94s` | f28478265747aebd6b78c30d2054f5cb | not scored |
| Small candidate until v84 (+Stand-in depth + small marker); now the first small fallback | v82 | `sub_v100s` | b1bf65c5909207c243ddc3c9d4c377f8 [403] | not scored |
| **Small nominee under the original harness (+First-call cap + small marker)** | v84 | `sub_v102s` | 92d6ffe89dd487f0fe7914c253f3852d [406] | not scored |
| **Final submission, main (per-case harness)** = v83's rules, one process per case (Section 4.2) | v95 | `sub_v114m` | 04460073a0d358ff3be70185906d8f05 [469] | 16 (per-case harness) [471] |
| **Final submission, small (per-case harness)** = the same + small marker | v96 | `sub_v115s` | 5d7ec8f10baf51e91d7a789cfdbb7e6c [469] | 10 of 14 (per-case harness) [471] |
| Dress rehearsals of +Coverage, +Fast 7B, +Skywork K 3, +Stand-in depth | v72, v73, v75, v81 | `sub_v89r`, `sub_v90r`, `sub_v93r`, `sub_v99r` | 51d899cb..., 6fbb1c10..., 248785e2..., 3a6e2a20ac8d459c9397dd180da37562 [395] | research (v81: 10, 0.48, by design [404]) |
| Skywork full read (K 3, 28 templates, cap 9,000) | v37 | `sub_v49s` | — | research |
| Skywork originals read (inside the Skywork expert-text run) | v49 | `sub_v61r` | — | research |
| Olmo full reads (K 3 on 5 templates; K 1 on 15) | v33b; v39 | `sub_v43s`; `sub_v51s` | — | research; v39 not scored |
| 7B speed test | v69 | `sub_v85r` | 3a2badf6e4607c16bbf852169e56b1b4 | research |
| Internal-state probe baseline | v79 | `sub_v97r` | 61c446c337d5b06421897064d4bb7813 [391] | research (10 by design) [394] |
| In-hour dormant-condition rating: gpt-oss medium; anchored prompt, gpt-oss high (Section 6) | v90; v94 | `sub_v109r`; `sub_v113r` | — | research: 10 by design; 0.05 (per-case harness) [461, 464, 470] |
| Kick-and-return (Appendix E.12) | v89 | `sub_v108r` | 52db3754... [450] | research (10 by design) [463, 464] |
| Cheap in-hour rating, four gpt-oss low / medium arms (Section 6) | v97 | `sub_v116r` | 84326862... [473] | research: 1 of 21 (per-case harness); all four arms failed [491]; showed that `/tmp` does not persist [492] |
| STD research read (Section 6) | v98 | `sub_v117r` | 0af0e157efee4d36e7e7725bf85b1745 [489] | built, not uploaded; replaced by v102 [502] |
| Targeted siblings (Appendix E.14) | v99 | `sub_v118r` | e75b327aa1deddaf8ddfec0569f405b8 [493] | built, deprioritised, not uploaded [493] |
| STD entry candidates (v95 / v96 with STD deciding Skywork and Olmo cases) | v100; v101 | `sub_v119m`; `sub_v120s` | 7f45e835aa1f75e705bca2e03538f2b4; a8521a1752f852cf6e7eb1ba38ae588c [495] | superseded by v107 / v108 [531] |
| STD + white-box probe research read (Section 6.4) | v102 | `sub_v121r` | d8ff5e27a4ee7ce65e230a811313c28c [502] | Codabench 993976; log not read at writing [503, 518] |
| Two-stage STD, for branch (b) of the v102 plan | v103 | `sub_v122r` | 7760ccd3... [511] | built, not uploaded [511] |
| Answer-identical faster v95 (Section 4.3) | v104 | `sub_v123m` | 8cdf9cdc8a93c4a71780c08795f7ee06 [510] | not scored [510] |
| Answer-identical faster v96 (Section 4.3) | v105 | `sub_v124s` | 0b9e1896392dd82559ac75815ea8e2eb [517] | not scored [517] |
| STD entry candidates gated on v102 (Section 6.3) = v100 / v101 + v104's skip of a moot quick finish; answers identical on 455 mock case runs | v107; v108 | `sub_v125m`; `sub_v126s` | c7234444740fc0cc96cc15fd4782cc60; 5838d79213c98684595a6ec2cb69d30d [531] | not scored; gated on v102, then one board run each [494, 511, 531] |
| Insurance under the original harness, main: strict compliance (only the judged model loaded; DeepSeek from its public prior) | v85 | `sub_v103m` | e84f193b7df1e4a49c9e88d98bd24386 [409] | 15 (H1) [419] |
| Insurance under the original harness, small: strict compliance | v86 | `sub_v104s` | 0e6c5e085af86357b12c8fcab8c8957f [409] | 8 (H1) [419] |

**File-level differences** (file comparison). v83 differs from +Fast 7B (v70) only in
`params.json` (Skywork and Olmo `rows_max`, `time_fast`; `future_new_factor`; two first-call keys) and `solution.py`
(log tag; three-line cap), and from v80 only in the cap and log tag; v84 adds an empty `small.txt`. v95 differs from
v83 only in `solution.py` (per-case handling; log tag) and `params.json` (Skywork's own run on the default decode path;
nine per-case keys, among them `case_target_seconds` 210 and `own_case_target_seconds` 400); v96 differs from v95 only
in the log tag and the empty `small.txt`. v104 differs from v95 only in `solution.py` (the skip of a quick finish that
cannot change the answer; log tag) and `params.json` (`qfin_skip_moot`) [510]; v105 is v104's code with v96's
empty `small.txt` and its own log tag [517]. v107 and v108 add v104's skip to v100 and v101; at 1.0x the main mock
ends at 2,911 s instead of 3,418 s and the small one at 2,616 s instead of 2,912 s [531].
