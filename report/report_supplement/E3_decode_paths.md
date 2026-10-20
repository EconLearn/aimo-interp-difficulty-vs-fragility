# Supplement to the technical report: Appendix E.3 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 20 October: text moved out of the report in draft 27 is in the addendum of 20 October at the end of this file.
Note added 20 October (draft 29): text moved out of the report in draft 29 is in the addendum of 20 October (draft 29)
at the end of this file; the report keeps a summary or a pointer.*

### E.3 Decode paths: diagnosis, checks, coverage scenarios and the gpt-oss bench (Section 4.4; the coverage scenarios are original harness)

**Diagnosis** [357]. At short context Skywork costs about 1 ms per row per step, against about 4.6 at long context; Olmo
about 1.5 to 2 against 9 to 10. The cost was in two places in `transformers` 5.13:

- The SDPA attention integration disables its grouped-query path whenever an attention mask is present. Our left-padded
  batches always have one. So every decode step copies K and V once per query head that shares them: 7 times for
  Skywork, which has 28 query heads over 4 KV heads.
- The dynamic cache appends with `torch.cat`, which copies the whole cache at every step.

These are the same two costs we had removed for gpt-oss earlier (below).

**+Coverage's server timings** [363]: Skywork (9 rows to 9,000 steps) planned 511 s, took 423
s; Olmo (6 rows to 10,000 steps) planned 713 s, took 507 s (about 7.1 ms per row per step). **Planned against actual
own-run times in the dresses**: +Coverage Skywork 702 s planned, 542 s taken, Olmo
1,023 and 663 s [373]; +Fast 7B Skywork 693 and 404 s, Olmo 1,086 and 728 s, Olmo in batches of 16 + 11 rows [375];
+Skywork K 3 Skywork 468 and 324 s [379].

**Change** [360]. A decode-step attention in which the query heads of one KV head share a single read of K and V, with
the mask unchanged. Prefill and models without grouped attention keep the original code. K and V are written in place
into a pre-grown cache, for full and sliding-window layers. Olmo-3-7B-Think has 32 query and 32 KV heads, so for Olmo
only the cache part applies.

**Safety.** The path is checked inside every run before use: greedy agreement with the default path must be at least
0.99; a deliberately broken variant (wrong head mapping, or a corrupted cache) must fail the same check; any error other
than out-of-memory reruns the batch on the default path and switches the fast path off. Mac checks before any server run
(computed, fp32): a tiny Qwen2-shaped model (28/4 heads) agreed 1.000 over 192 positions, maximum logit difference 3e-7,
and the head sabotage scored 0.016 and failed as required; a tiny Olmo3-shaped model agreed 1.000 and the cache sabotage
scored 0.411 and failed; the mock's own-run decisions were identical to the default path in 78 of 78 cases [360].

**Server speed test** (pre-registered [361], read in [365]): four ABBA arms on 12 rows (4 public
templates × 3 attempts), same seeds, forced to 7,000 tokens; bar: fast ≤ 0.67 × default ms/step for Skywork, ≤ 0.80 ×
for Olmo.

| Model | Default | Fast | Ratio (bar) | Check on server | Basis |
|---|---|---|---|---|---|
| Skywork-OR1-Math-7B | 343.5 s = 49 ms/step | 144.3 s = 21 ms/step | 0.42 (≤ 0.67): **2.4x faster** | agreement 1.000, greedy identical, sabotage failed | server [365] |
| Olmo-3-7B-Think | 532.9 s = 76 ms/step | 258.2 s = 37 ms/step | 0.48 (≤ 0.80): **2.1x faster** | same | server [365] |

The ratios are of wall seconds; by ms per step they are 0.43 and 0.49 [365].

**Original-harness coverage in the mock** [354, 367, 376, 379]. At server speed +Coverage on the default path read
12 to 14 of about 28 Skywork cases and 8 to 10 Olmo cases at the final shape (6 to 7 and 3 to 6 at 1.4x slower);
+Fast 7B read 25 to 30 and 24 to 28 (18 to 22 and 11 to 17 at 1.4x), with no clock cut and every run ending by 3,112 s.
+Skywork K 3 changed parameters only (Skywork batches of up to 90 rows planned at 20 + 0.3 ms per row per step; Olmo
batches capped at 16 rows by memory at cap 10,000, 12 + 1.8 ms); its mock read every Skywork problem at K 3 at 1.0x and
13 to 22 at 1.4x, and its mock cost at 84 rows (36.8 ms per step) is close to the 36 ms per step measured in its dress.
The full scenario tables, the sensitivity to older step costs and the three-way comparison of the guards are repository
material: `work/rehearsal/final_scale_sub_v92m.out`, `final_scale_sub_tmp_ff25.out`, `final_scale_sub_v98m.out` and
`final_scale_sub_v101m.out` [367, 376, 395, 406].

**The gpt-oss path.** gpt-oss uses attention sinks, so `transformers` falls back to eager attention. Per decode step
this concatenates the whole K/V cache and copies K and V eight times (64 query heads, 8 KV heads): about 19 times the
bytes needed [183]. The fix folds each KV head's eight query heads into the query axis; the arithmetic is unchanged and
the sinks are kept. K and V are written in place into a pre-grown buffer. The server bench was pre-registered [186] and
read in [193]:

| Shape (rows × context) | Original path | Fast path | Ratio | Basis |
|---|---|---|---|---|
| 112 × 3,072 | 225.2 ms/step | 54.9 ms/step | 0.24 | server [193] |
| 32 × 7,168 | 145.4 ms/step | 39.1 ms/step | 0.27 | server [193] |

- **Equivalence.** Teacher-forced argmax agreement with the original path was 0.987, against 0.977 between two runs of
  the original path itself. A deliberately broken head mapping was caught (agreement 0.000) [193].
- **End to end.** The low-effort reading ran in 130.8 s instead of 235.9 s (1.8x).
- **Where the time goes now.** The step is bound by kernel launches (about 36 ms) [193]. A batch lasts as long as its
  longest attempt, so the gain is best spent on more attempts per batch rather than more batches [200].

We also remove finished attempts from the batch and the cache every 128 steps; this gave identical greedy tokens and
cost 2.0 to 2.4 s per attempt instead of about 5.0 s (server) [99]. Together these paid for the stand-in reading at 32
attempts per problem, inside about 1,300 s on the board [282]. Runtime matters for ranking: ties are broken by the
faster average runtime over three repeated trials (contest site). On the board, +Fast 7B ended at 1,787 s against
+Coverage's 2,674 s [369].

### Addendum of 20 October

*Text moved out of the report in draft 27 to keep its main text within the limit (verbatim, from draft 26).*

*From Section 9, lesson 5 (the numbers are still in the report's Section 4.4 table):*

5. **Profile the decode step, and gate fast paths with an in-run check and a sabotage arm**: 2.1x to 2.4x for the 7B
   models with greedy output unchanged, and 0.24 to 0.27 of the step time for gpt-oss (Section 4.4).

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Appendix E.3:*

**Diagnosis** [357]. At short context Skywork costs about 1 ms per row per step, against about 4.6 at long context; Olmo
about 1.5 to 2 against 9 to 10. The cost was in the two places Section 4.4 names (masked attention without the
grouped-query path; a cache appended with `torch.cat`), the same two costs we had removed for gpt-oss earlier (below).
