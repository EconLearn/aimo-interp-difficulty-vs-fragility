# Supplement to the technical report: Appendix F.7 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 17 October: rows for the evidence of 16 and 17 October (Section 4.5, Appendix E.17, the second nominees and the
evidence copied to `work/evidence_scratch_20261017/`) are in the report's Appendix F.7. Note added 18 October: the row
'§6.4 v102 read (pending)' is superseded; v102 was read on 18 October [555], and the rows for 18 October are in the
report's Appendix F.7.*

### F.7 Table-to-script map

| Table or number | Script | Input | Ledger |
|---|---|---|---|
| §3.3 and E.11 cross-reading matrix; §5.2 Olmo balanced accuracy | `work/miners12/review/xread.py` → `xread.out` | the logs of the next row, `miners7/design/common.py` (stand-in features), `sub_v86m/decision.json`, `runs/v49_small_972813.log` | [399] |
| §3.2 and E.1 own-row reads; §3.3 AUCs; §4.1 and E.4 K 1 against K 3; §5.2 Skywork and Olmo rows | `work/miners12/review/own_q1q2.py` → `own_q1q2.out` | `runs/v37_small_968679.log`, `runs/v30_small_967901.log`, `runs/v34_small_968332.log`, `runs/v33b_small_968241.log`, `runs/v39_small_968823.log`; dress-rehearsal counts from the ledger (those logs were read in the browser and are not held) | [387] |
| E.4 stand-in accuracy against K; §5.2 always-robust and stand-in refit rows | `work/miners12/review/standin_k.py` → `standin_k.out` | answer-bearing gpt-oss-low logs | [387] |
| §3.2 hard-region lab | `work/hardlab.py`, `work/hardlab_rules.py` → `runs/hardlab.out` | six gpt-oss reads, public rows | [278, 336] |
| E.2 own signals for Qwen, DeepSeek, high | `work/miners12/ownsig/ownsig.py` → `ownsig.out` | server logs, public rows | [356] |
| §3.4 and E.8 Skywork run to the end | `work/analyse_full2.py` → `runs/v37_full2.out` | `runs/v37_small_968679.log` | [269] |
| §4.1, E.3, E.4 mock coverage, expected cases and stress tests | `work/rehearsal/run_final_scale.py` + `mock_engine2.py` → `rehearsal/final_scale_<bundle>.out`; E.4's expected cases read the final-shape lines at 1.0x and 1.4x of `final_scale_sub_v92m.out`, `final_scale_sub_v98m.out` and `final_scale_sub_v101m.out`; the nominees' stress test is in `rehearsal/stress_v83_v84/` [423]; the v74, v80 and v83 numbers need `MOCK_FAST7=1 MOCK_FAST7_T=Skywork:20:0.2,Olmo:12:1.8 MOCK_OWN_T=Olmo:8:7.1` (as in `release/README.md`); E.3's sensitivity is the same command without the two `_T` settings; v80's mock is `final_scale_sub_tmp_ff25.out` (v74's bundle with `future_new_factor` 0.25; v80's own bundle `final_scale_sub_v98m.out` gives the same final-shape counts), v83's `final_scale_sub_v101m.out`, the small nominee's `final_scale_sub_v102s_small.out` (v82's `final_scale_sub_v100s_small.out`) | bundles | [353, 354, 367, 376, 380, 395, 398, 403, 406, 423] |
| §4.4 and E.3 7B speed test | research bundle `sub_v85r`; server log of the speed-test upload | — | [361, 365] |
| §4.4 and E.3 gpt-oss decode bench | `work/sub_v24r/bench_fastpath.py` (also `work/miners6/eng/`) | server log | [186, 193] |
| §4.1 and E.4 dress rehearsals | `work/rehearsal/dress_wrapper.py`; bundles `sub_v89r`, `sub_v90r`, `sub_v93r`, `sub_v99r` | server logs (read in the browser) | [370, 373, 375, 379, 404] |
| §3.4 reweighting and its simpler worlds (W_LS, W_COV) | `work/miners7/shift/s1_features.py` to `s4_q4_requirement.py` → `s2_shift_sim.out` | public rows, stand-in logs | [192] |
| E.5 single-read table | `work/medium_rep.py`, `work/analyse_v8.py`, `work/miners4/p2_cut2000_rep.py`, `p3_bracket_rep.py`, `p5_ruleA_v8.py` | server logs | [112, 117, 119, 132, 134] |
| §5 and E.6 negative results | `work/analyse_internal.py` [173], `analyse_distill.py` [217], `analyse_viva.py` [308], `analyse_factory.py` [309, 312, 318, 319], `analyse_sib.py` [314], `analyse_sp.py` [321], `analyse_cert.py` [197] | server logs | as listed |
| §4.1 and A.2 fresh-seed reruns | bundles `sub_v95m`, `sub_v96m` (`seed_offset` 7777 / 424242 added to every seed) | server logs (read in the browser) | [384, 385, 393] |
| §5.2 probe baseline | research bundle `sub_v97r` (`probe.py`; local test `chk97r/`) | server log '[probe]' lines (read in the browser) | [388, 391, 394] |
| `decision.json`, `calib.json` | `release/training/refit_low16.py`, `release/training/build_calib.py` | four server logs; `train-main-v2.parquet` | [382] |
| §3.4 fresh against exposed rows; E.12 taxonomy, family identification, T10 mutant, edit-side negatives | `work/miners14/laneB/b3_exposure.py`, `b1_taxonomy.py`, `b2_equivalent_mutants.py`, `b4_lossy_final_map.py`, `b5_boundary_policy.py` (each → `.out` beside it) | `sub_v101m/calib.json`, `hf/aimo-interp-challenge-sample-full.parquet`, gpt-oss low's answer counts from `runs/v53_small_973321.log` and `runs/v54_small_973443.log`, typed into `b2` | [446] |
| §6 and E.12 dormant-condition rating | `work/miners14/laneA/score_five_raters.py` (md5 a5ab28cd5b6e9efe473345ae45963b07); `a6_score.py`, `a10_replication.py`; lane A's other tests `a1_vectors.py` | the five rating files, `blind_problems.json`, `sub_v101m/calib.json`, `runs/v88_dress_987666.log` | [447, 451-453, 457] |
| E.12 lanes C and D | `work/miners14/laneC/lc1_engineering_scores.py`; `work/miners14/laneD/d1_bench.py`, `kick_power.py` | held logs, ledger counts, the older per-family sample | [443, 445] |
| §6 and E.12 group 5: distilled rater | `work/miners15/distill/text_rater.py` (md5 65a7a7d5ba4626d598fc2f80a48730ea) | `pool.json`, the pool ratings in `ratings/`, the five rater files | [474, 475, 477] |
| §6 and E.12 group 5: in-hour observables | `work/miners16/laneS/s_proxies.py` → `s_proxies.out` (bars in `PREREG_laneS.txt`) | `s_matched_rows.json`, the pool ratings, another team's public generations | [478, 479] |
| §4.2 per-case mock | `work/rehearsal/run_per_case.py` (also in `release_public_v95/rehearsal/`); the final-size rows use `--shape final` and `--shape final_mix` (re-run 16 October) | bundles `sub_v114m`, `sub_v115s`, `sub_v101m`, `sub_v102s` | [466] |
| §4.2 per-case server costs and results | ingestion logs of 990657, 991447 and 991452, read on Codabench (not held as files) | — | [464, 465, 471] |
| §2 and E.13 generalisation audit | `work/miners17/laneG/g1_policy_loto.py` to `g5_selection.py` (each → `.out`; shared code `g_common.py`) | `runs/v88_dress_987666.log`, the held reads, `release/training` | [509] |
| §4.3 and E.15 final-shape risk; v104 | `work/miners17/laneF/shapes_mock.py` → `mock_outputs.md` | bundles `sub_v114m`, `sub_v115s`, `sub_v123m` | [510] |
| §6 and E.14 STD bench | `work/miners16/laneL/l3_census.py`, `l3b_transcription.py`, `l2_retrieval_anchors.py`, `l1_aggregation_ceiling.py` (each → `.out`); frozen scorer `score_std_read.py` | `progs/` (hand-written programs), the five rater files | [482] |
| §6 and E.14 cheap raters (v97) | `work/miners14/laneA/score_cheap_raters.py` (frozen) | `runs/v97_cheap_992342_case1.log` | [491] |
| §5 and E.14 4B program writer | `work/miners16/laneQ/gen_q.py`, `harness_q.py` → `score_q_nothink.out`, `score_q_think.out` | `replies_q_nothink.jsonl`, `replies_q_think.jsonl` | [496] |
| §5.2 and E.14 white-box probes | `work/miners17/laneW/extract_w.py`, `probe_w.py`, `extract_wsol.py`, `probe_wsol.py`, `extract_wthink.py`, `probe_wthink.py` (each → `.out` or `.log`) | the rated pool and the 28 templates | [499, 506, 516] |
| §5 and E.14 lane X | `work/miners17/laneX/x1_ddm.py` to `x5_consistency.py`; `x6_na_share.py` (frozen) | `x_pool.json` | [508] |
| §6.4 v102 read (pending) | bundle `sub_v121r`; scorers `score_std_read.py`, `score_woss.py`, `classify_v102.py` | the case-1 lines of the 993976 log | [502, 503, 511] |
| §2.4 and E.13 lane R | `work/miners17/laneR/r_fresh.py` → `r_fresh.out`, `RESULT_R.md` | lane G's inputs | [514, 515] |
| §6.5 and E.16 blind STD writers and the pooled read | `work/miners18/blindSTD/run_blind.py`, `blindSTD2/run_blind2.py`, `blindSTD3/run_blind3.py`, `pooledSTD/run_pooled.py`; frozen scorer `miners16/laneL/score_std_read.py` → `score_A.out`, `score_B.out`, `score_blind2.out`, `score_blind3.txt`, `score_pooled.out`; results in `RESULT_blind.md`, `RESULT_blind2.md`, `RESULT_blind3.md` | the frozen programs (`progs_blind/`, `progs_blind2/`, `progs_blind3/`), `miners14/laneA/blind_problems.json` | [521, 523, 527, 528] |
| §2.4 and E.16 label shift | `work/miners18/laneS/r_shift.py` → `r_shift.out`, `RESULT_S2.md` | lane G's inputs | [525, 526] |
| E.16 X6 read blind | `work/miners17/laneX/x6_na_share.py` (frozen; with and without `--dev`) → `miners18/x6_on_blind.out` | the three blind writers' logs and the pooled log | [530] |
| §5.2 and E.16 lane GRAD | `work/miners18/laneGrad/extract_grad.py`, `gradlib.py`, `score_grad.py` → `score_grad.out`, `RESULT_grad.md` | lane W-sol's generations (`wsol_generations.jsonl`), `sub_v101m/calib.json`, `runs/v88_dress_987666.log` | [532, 533] |
| Figure 1 (§2.2) | `figures/make_board_vs_audit.py` → `figures/board_vs_audit.png` (matplotlib) | board draws typed in from Appendix B; predictive ranges from `g3_board.out`; selection ranges from `g5_selection.out` | [393, 464, 471, 509] |
| Figure 2 (§3.3) | `figures/make_cross_reading.py` → `figures/cross_reading.png` (matplotlib) | the cells of Appendix E.11, typed in from `xread.out` | [399] |

Every decision and bar is in `work/LEDGER.md`, refuted entries kept.
