# Supplement to the technical report: Appendix F.2 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix
part and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references
point to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's
folder.*

### F.2 Parameters of v83, the main nominee under the original harness (`work/sub_v101m/params.json`; v80's `sub_v98m` lacks the two first-call keys, and v74's `sub_v92m` also has `future_new_factor` 0.5; v95's `sub_v114m` adds the per-case keys of Appendix B and runs Skywork's own run on the default decode path)

| Parameter | Stand-in reading | Quick-finish reading | Skywork own run | Olmo own run |
|---|---|---|---|---|
| Model | openai/gpt-oss-120b | Qwen/Qwen3.5-4B | Skywork/Skywork-OR1-Math-7B | allenai/Olmo-3-7B-Think |
| Chat-template arguments | `reasoning_effort: low` | `enable_thinking: false` | none (default template) | none (default template) |
| Applies to | Qwen, DeepSeek, medium, low cases (and as fallback) | same, as the second feature | Skywork cases | Olmo cases |
| Cap (tokens) | 3,000 | 2,000 | 9,000 | 10,000 |
| Attempts per problem | K_min 4, K_max 32, top-up to 32 | 4 | up to 3 (K_max) | up to 3 (K_max) |
| Rule | logistic decision (Appendix F.4) | 1 if any attempt ends on its own | robust iff ≥ 1 ends (`min_ended` 1); with 1 attempt, iff it ends | robust iff ≥ 2 end (`min_ended` 2); with 1 attempt, iff it ends |
| Rows per batch, max | 112 | 128 | 90 | 16 |
| Finished-attempt removal | yes, every 128 steps | no | no | no |
| Time model a + b × rows (ms per step) | 36.0 + 0.3, used share 0.6; 33.2 + 0.885, used share 0.48 if the gpt-oss path is off | not planned (fixed estimate) | default 8.0 + 4.6; fast path 20.0 + 0.3 | default 8.0 + 7.5; fast path 12.0 + 1.8 |
| Seed of a batch in call c | 100000·c + first problem index (top-up: 300000·c + index) | 200000·c + index | 400000·c + index (`seed_base`) | 500000·c + index (`seed_base`) |
| Own-run time limit | — | — | 3,300 s from start, minus 150 s per later call; plans inside 45% of the window (`share`) | 3,300 s, minus 150 s per later call; full window |
| Fast decode path | gpt-oss path, self-checked | — | `fast7b` on, self-checked | `fast7b` on, self-checked |

Global settings: `total_seconds` 3,200 for the entry's own plan; `reserve_per_call_seconds` 150; `expected_calls` 7 (4
with `small.txt`); `primary_time_share` 0.8 (share of the time left that the stand-in may plan for); `future_new_factor`
0.25 (later calls assumed to bring a quarter of the average new problems; 0.5 in v74 and earlier, Appendix E.4);
`first_call_K_max` 16 with `first_call_cap_min_problems` 10 (the stand-in's K in call 1 is capped at 16 when call 1 has
10 or more problems, because call 1 is planned before any speed is measured; v83 and v84 only, Appendix E.4 [406]);
`first_call_seconds` 300 (used only when a research arm is pending; none is); `prior_robust`: gpt-oss high; `entry_mode`
full. Own-run time predictions are multiplied by 1.15 and by the slowdown measured earlier in the same run. Own-run
planning: if every new problem fits at K 3 they all get K 3; otherwise 1 attempt each, smallest |margin| first, then
upgrades to K 3 (Appendix E.4). +Coverage cut the reserves for later calls from 420 s and 300 s to 150 s per call;
Skywork plans inside 45% of its window because Olmo comes after it [354]. In `params.json` the
Olmo spec sits under the legacy key `sky` and the Skywork spec under `owns`.
