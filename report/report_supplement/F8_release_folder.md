# Supplement to the technical report: Appendix F.8 in full

*AIMO Interpretability Challenge 2026 (NeurIPS 2026, Codabench 16180). The report keeps a summary of this appendix part
and its key tables; this file holds the part's complete text, unchanged. Section, Appendix and Figure references point
to the report; numbers in brackets are entries of `work/LEDGER.md`; file paths are relative to the report's folder. Note
added 17 October: the nominees for the final are now v111 / v112, packaged in `release_public_v111/` (the report's
Appendix F.8); `release_public_v95/` below holds the files scored on 15 and 16 October. Note added 20 October:
`release_public_v111/` now also holds v115 / v116 (`v115_v116/`), and a paragraph moved out of the report in draft 27 is
in the addendum of 20 October at the end of this file. Note added 20 October (draft 29): text moved out of the report in
draft 29 is in the addendum of 20 October (draft 29) at the end of this file; the report keeps a summary or a pointer.*

### F.8 Release folder

`release/` holds an open-source copy: submission folders, the mock and dress-rehearsal scripts, and the training scripts
that rebuild `decision.json` and `calib.json` byte for byte [382]. **It packages the original-harness nominees:
+First-call cap for the main track (v83, `sub_v101m`; `solution.py` md5 ef0cb0ca72b555ad3b963375a3ebf8af, `params.json`
b49fe6b4bc2630bc26e8e4002a096932) and its small-track twin (v84, `sub_v102s`; `solution.py`
51f1eec1d25697951c82b3eec650e654)** [407]. The README gives per-file `touch -t` lines (all files, then a later time for
`params.json` and `solution.py` in `submission_main`; one time for `submission_small`) and per-file md5s. A fresh copy
built by following it (`touch -t`, `zip -X`) reproduces the zip md5s f93ef76c44d0733b22b5282e4c9b3e6a
(`dist/aimo_v83_main.zip`) and 92d6ffe89dd487f0fe7914c253f3852d (`dist/aimo_v84_small.zip`) [407], re-checked for this
update on a scratch copy (computed, 13 October); the same check passed for v80 / v82 [405] and v74 / v76 [392] while the
folder packaged them. The README documents the mock's measured step costs [398] and that v83's code differs from v70's
only in the log tag printed by `solution.py` and the three-line first-call cap, with the `params.json` changes listed in
Appendix B (`release/README.md`). Its mock command, run on a scratch copy of `release/` with those step costs,
reproduces v83's and v84's mock outputs (`final_scale_sub_v101m.out`, `final_scale_sub_v102s_small.out`) line for line
apart from the header naming the bundle: 39 runs per track, all inside 3,600 s, 0 invalid predictions (computed, 13
October; the same check passed for v80 / v82). Its Limitations line now says that at modelled speed every Skywork case
gets 3 attempts and most Olmo cases one [400]. A licence and the redistribution terms of the organisers' public problem
texts are still to be settled. Repository link: https://github.com/EconLearn/aimo-interp-difficulty-vs-fragility.

`release_public/` is `release/` without the organisers' problem texts: `calib.json` is rebuilt from their public
parquet with `training/build_calib.py` [431]. **`release_public_v95/` packages the per-case nominees** the same way: v95
(`sub_v114m`; `solution.py` md5 b1e50f8542b8cf2fa6a01f4299f262fd, `params.json` 95aa75dfd9d6e0f04f53ec29c4e47e4e) and
v96 (`sub_v115s`; `solution.py` 32ea012d5d67de3d2827cf5e837f3104), plus the per-case mock `rehearsal/run_per_case.py`.
Its README gives the per-case harness, the `touch -t` lines (read from the uploaded zips' member times) and the zip
commands. From a fresh copy, with `calib.json` rebuilt from `train-main-v2.parquet`, `zip -X` reproduces
04460073a0d358ff3be70185906d8f05 (`dist/aimo_v95_main.zip`) and 5d7ec8f10baf51e91d7a789cfdbb7e6c
(`dist/aimo_v96_small.zip`) byte for byte, `refit_low16.py` reproduces `decision.json`, and the per-case mock gives
[466]'s 3,339 / 3,837 s (main) and 2,574 / 3,065 s (small). A scan for 95 snippets of the 36 public problem texts
(start, middle and end of each) finds none in the folder; in a copy with `calib.json` rebuilt it finds 89, the other 6
belonging to re-numbered texts that `calib.json` does not store (computed, 16 October).

### Addendum of 20 October

*Added for draft 27 of the report.* On 20 October (UTC) `release_public_v111/` gained `v115_v116/` with the files of
v115 (`submission_main/`, 8 files) and v116 (`submission_small/`, 9 files), without `calib.json`, which the first step
now copies to seven places; the release has 91 files before that step and 99 after it. A scan of the new files finds no
personal paths, e-mail addresses or credentials. From a fresh copy, with `calib.json` rebuilt from the public parquet,
the README's commands rebuild `aimo_v115_main.zip` (ad191e2e2262b0a918ec1aaf83bcf9c7) and `aimo_v116_small.zip`
(d3ada3a4b8ff05b5876582246008bbf9) byte for byte under four time zones and from a copy made under umask 002, and the
v111 / v112 zips still rebuild byte for byte.

**Text moved out of the report in draft 27** (verbatim, from Appendix F.8 of draft 26):

**README fix pass** [550]: the outsider test's 13 README gaps [549] are closed, and every offline step passes on a fresh
copy. Commands are written `python3` (Python 3.11 or later with numpy, pandas and pyarrow). `training/moot_count.py`
applies `_qfin_moot()` to the public rows: the quick finish is moot for 25 of the 44 labelled stand-in rows, and `full`
and `agreement_only` differ on 9. Both use the first gpt-oss low read alone; with the fitted feature (`pair_nat`, the
mean of both reads) they are 31 and 3 of 44, so the mocks' 25 of 44 is the conservative choice (longer cases).

### Addendum of 20 October (draft 29)

*Text moved out of the report in draft 29 (verbatim, from draft 28), to keep the report within its word limits.*

*From Section 10:*

**Reproduce v95 and v96** from `release_public_v95/` (Python 3.11 or later; pandas and pyarrow for the first step;
parquet: Appendix F.8):

```sh
python3 training/build_calib.py train-main-v2.parquet calib.json   # md5 d5b98e21...; copy into both submission folders and training/sub_v1c/
cd submission_main && chmod 644 * && touch -t 202610151513.28 * && touch -t 202610151520.50 params.json && touch -t 202610151518.52 solution.py
zip -X ../aimo_v95_main.zip calib.json decision.json engine2.py fast7b.py fastpath.py params.json perturb.py planner.py solution.py
cd .. && python3 rehearsal/run_per_case.py --bundle submission_main --shape main    # 21/21 valid, 3,339 s (3,837 s with --slow 1.4)
python3 rehearsal/run_per_case.py --bundle submission_small --shape small           # 14/14 valid, 2,574 s (3,065 s with --slow 1.4)
```

The README gives the small track's commands and per-file md5s; a fresh copy reproduces both zip md5s byte for byte, and
`training/refit_low16.py` (inside `training/`) reproduces `decision.json` [476].

*From Appendix F.8:*

`release_public/` is `release/` without the organisers' problem texts: `calib.json` is rebuilt from their public parquet
with `training/build_calib.py` [431]. `release_public_v95/` packages the scored per-case files v95 (`sub_v114m`) and v96
(`sub_v115s`) the same way, with the per-case mock `rehearsal/run_per_case.py`; a fresh copy reproduces both zip md5s
(Section 10), `decision.json` and [466]'s mock times, and it holds no public problem text (full text of this appendix:
`report_supplement/F8_release_folder.md`).
