# AIMO Interpretability Challenge 2026: entry v111 (main track) and v112 (small track)

Code for our entry to the AIMO Interpretability Challenge (NeurIPS 2026, Codabench 16180). The technical report
("Difficulty is not fragility: an audited robustness predictor and 70 negative results"; four-page version and the full
report with its supplement in `report/`) describes the method and every measurement behind it.

v111 and v112 are our first candidate nominees for the final evaluation (all six: "Candidate nominees" below). They are v95 (main) and v96 (small), whose code we
released earlier as `release_public_v95/` and which is copied unchanged into `v95_v96/` here for the comparisons, with
four changes that save time or remove a crash (listed with their ledger ids under "What changed from v95 / v96" below). The decision rules are v95's. v111 gives v95's answers whenever the
server runs at the speed the entry plans for. v112's per-case time targets are shorter than v96's, and that changes some
answers (details below).

**Status (18 October 2026): both files have run on the validation board under the per-case harness.** v111 scored 17 of 21 (0.81; every case answered, 2,634 s) and v112 9 of 14 (0.64; every case answered, 1,913 s). For comparison, v95 scored 16 of 21 (0.76) and v96 10 of 14 (0.71). Timing numbers elsewhere in this README that are labelled as mock come from local mocks on a virtual clock (no GPU, no model); on the server v111 and v112 took 0.95 and 0.92 of the time of the server-calibrated mock (report, Appendix E.17).

**Added on 19 October 2026: v115 (main) and v116 (small)**, optional variants of v111 / v112 that keep every case under
170 s, in case the final's "170 seconds per sample" is a limit on each case rather than an average. Their files are in
`v115_v116/`; see "Optional per-case-safe variants" near the end.

**Added on 20 October 2026: v121 (main) and v122 (small)**, seed variants of v115 / v116: the same entries with every
reading's random seed shifted by a fixed offset, so that a second nominee reads each problem independently. Their files
are in `v121_v122/`; see "Seed variants" near the end.

**Candidate nominees.** Several submissions may be nominated per track for the final. Our candidates are the six files
below; this README rebuilds each zip byte for byte. The final nomination (which of these files are nominated) will be
made and announced through the organisers' channel, by the procedure the organisers announce; that procedure had not
been published on 20 October.

| Track | Entry | Zip | md5 | Codabench submission | Validation board | Section |
|---|---|---|---|---|---|---|
| main | v111 | `aimo_v111_main.zip` | `9686c9cec06ec4dc40f9b728f7ef17db` | 1000991 | 17/21 | "Building the two zips" |
| main | v115 | `aimo_v115_main.zip` | `ad191e2e2262b0a918ec1aaf83bcf9c7` | 1003729 | 15/21 | "Optional per-case-safe variants" |
| main | v121 | `aimo_v121_main.zip` | `22ced3169a4d73b5cfe9b7ceb0d815b6` | 1004377 | 15/21 | "Seed variants" |
| small | v112 | `aimo_v112_small.zip` | `8b404890d71bc5483ccce18f88887636` | 1000212 | 9/14 | "Building the two zips" |
| small | v116 | `aimo_v116_small.zip` | `d3ada3a4b8ff05b5876582246008bbf9` | 1003727 | 9/14 | "Optional per-case-safe variants" |
| small | v122 | `aimo_v122_small.zip` | `4de6852eee8d4c3e6ccb07576c422a31` | 1004381 | 9/14 | "Seed variants" |

v111 / v112 are built for 170 s per case as an average over the job; v115 / v116 and v121 / v122 keep every case under
170 s. Board scores are one run each on the validation board's 21 and 14 cases, not new problems.

License: code under the MIT License (see LICENSE); the technical report text under CC BY 4.0.

Dates in this README are Pacific time (PDT); the report uses UTC.

## Before you start: Python and packages

- **One interpreter for every command.** Every command below is written `python3` and is run from this folder unless the
  step says otherwise. `python3` must be Python 3.11 or later with numpy, pandas and pyarrow. Our checks used Python
  3.11.15 with numpy 2.4.6, pandas 3.0.6 and pyarrow 25.0.1, on an Apple-silicon Mac (M4) with Info-ZIP `zip` 3.0.
- **On macOS** the system `python3` is 3.9 and has no pyarrow, and there is no `python` command. Install Python 3.11
  (python.org or Homebrew) and make a virtual environment first; inside it `python3` is the venv's Python. For example
  (this needs a network connection and was not part of our offline check, which used an existing venv with the versions
  above):

  ```sh
  python3.11 -m venv .venv && . .venv/bin/activate && pip install numpy==2.4.6 pandas==3.0.6 pyarrow==25.0.1
  ```

- Only `training/build_calib.py` needs pyarrow. The mocks, the refit, `training/moot_count.py` and the audit also ran on
  the system Python 3.9.6 (numpy 2.0.2, pandas 2.3.3) with identical outputs.
- `build_tables.sh` runs `python3` by default; `PY=/path/to/python` chooses another one. Usage lines inside some scripts
  still write `python`: use the same `python3`.

## First step: rebuild `calib.json` (problem texts are not redistributed)

This public copy does not include the organisers' problem texts. The nine files that hold them are left out
(`submission_main/calib.json`, `submission_small/calib.json`, `training/sub_v1c/calib.json`, and the same file in
`v95_v96/submission_main/`, `v95_v96/submission_small/`, `v115_v116/submission_main/`,
`v115_v116/submission_small/`, `v121_v122/submission_main/` and `v121_v122/submission_small/`), and the 84 lines of
`training/runs/v4_main_960863.log` that printed a problem text now read
`[problem text omitted from the public release]` (those lines are not read by any script).

**The input file.** The organisers' public train set is the Hugging Face dataset `aimo-interp/train-main-v2`, revision
`23791d9b120132087877b0459f953d5959fc8455`. That is the dataset's last commit (dated 17 September 2026, still its head
when we checked on 9 October), so our copy, downloaded on 2 October, comes from it. The copy is 9,534 bytes with 82 rows,
md5 `3394dba3f01210c6f653ae0bea9f7de5` (sha256 `bedfb551ea0f4d95d5e70e1df7cf61395ce2d36eeba2869aba6a90fc3c198824`).
`calib.json` depends on the row order (a template's text is its first problem in file order), so use the file as
downloaded, not a re-export through `datasets`, and check its md5 first. The data card lists the data as
`data/train-*.parquet` (one split). We did not record the exact file name when we downloaded it, and we did not
re-download it for the 17 October check (offline). The command below assumes the usual single-file name; if it fails,
take the one parquet file under `data/` at this revision and check its md5. The dataset has a later commit (`fa8af758`,
15 October 2026) that adds 12 Skywork rows; `calib.json` was not built from that file, so do not use it here.

```sh
curl -L -o train-main-v2.parquet https://huggingface.co/datasets/aimo-interp/train-main-v2/resolve/23791d9b120132087877b0459f953d5959fc8455/data/train-00000-of-00001.parquet
md5 train-main-v2.parquet   # 3394dba3f01210c6f653ae0bea9f7de5 (md5sum on Linux)
```

**Rebuild and copy to the nine places:**

```sh
python3 training/build_calib.py /path/to/train-main-v2.parquet calib.json   # needs pandas + pyarrow
md5 calib.json        # d5b98e21169c0ae100c14009340b7fca (md5sum on Linux)
mkdir -p training/sub_v1c
for d in submission_main submission_small training/sub_v1c v95_v96/submission_main v95_v96/submission_small v115_v116/submission_main v115_v116/submission_small v121_v122/submission_main v121_v122/submission_small; do cp calib.json "$d/"; done
```

Checked on 17 October 2026 from a fresh copy of this folder, every command exactly as written in this README except the
three that need a network connection (`pip install`, `curl`, `git clone`; we used local copies instead): after this
step, `refit_low16.py` reproduces `decision.json` byte for byte (md5 `f29963e26fb37c91a2f4045d2116e2df`), the zip
commands below reproduce both zips (md5s in the table below), and the mocks reproduce the numbers given below and the
reference outputs in `rehearsal/expected/`. Everything else in this README assumes the step is done.

## Contents

```
release_public_v111/
  README.md
  submission_main/    the main-track entry v111 (9 files with calib.json, each byte-identical to the zip's)
  submission_small/   the small-track entry v112: the same code with its own log tag and per-case targets, plus an
                      empty small.txt (10 files)
  v95_v96/            the scored v95 (submission_main/) and v96 (submission_small/) files, copied unchanged from
                      release_public_v95/, for the paired mocks and the old-path check (8 + 9 files, + calib.json)
  v115_v116/          added 19 October: the optional per-case-safe variants v115 (submission_main/) and v116
                      (submission_small/) (8 + 9 files, + calib.json; section near the end)
  v121_v122/          added 20 October: the seed variants v121 (submission_main/) and v122 (submission_small/) of
                      v115 / v116 (8 + 9 files, + calib.json; section near the end)
  rehearsal/          the virtual-clock mocks of the per-case harness and of the original single-process harness, and the
                      contest-server dress-rehearsal wrapper (as in the v95 release)
    final_shape/      the final-shape simulation (30 to 50 cases at N x 170 s): table builder, simulator, drivers, an
                      old-path answer check and a table comparison script
    expected/         reference outputs of every mock command below, and the per-case tables as one CSV
  training/           how calib.json and decision.json were produced from the public labelled rows (as in the v95
                      release), plus moot_count.py (the public-row counts of changes 1 and 3)
  audit/              the generalisation-audit script of the report (Sections 2.2-2.3), its two input CSVs and its
                      expected output
  report/             the technical report; figures/ holds the scripts behind the numbers the four-page version names,
                      with their outputs and pre-registrations (section at the end)
```

Files have mode 644 (`rw-r--r--`), folders 755. The release has 108 files before the first step (118 after it: the
rebuilt `calib.json` and its nine copies); 17 of them, in `v115_v116/`, were added on 19 October, and 17, in
`v121_v122/`, on 20 October.

## The task in one paragraph

Each case is a (math problem, judged configuration) pair. The seven configurations are Qwen3.5-4B,
Skywork-OR1-Math-7B, Olmo-3-7B-Think, DeepSeek-R1-0528-Qwen3-8B, and gpt-oss-120b at low, medium and high reasoning
effort. The entry must say whether the configuration's accuracy survives the organisers' perturbations of the problem
(robust) or not, through `are_robust(model_id, reasoning_effort, problems)`, on one GPU with no internet.

## The harness

- **Original harness (until 15 October 2026).** One 3,600 s job, one process: the harness calls `are_robust` once per
  configuration (seven calls on the main track, four on the small track), and an entry can keep state across calls.
- **Per-case harness (since 15 October 2026).** Every case runs in its own process, one case after another, and the cases
  share one job budget: the ingestion log reads `case_timeout_s=4200 job_timeout_s=4200 safety_margin_s=180`, so about
  4,020 s for the 21 main or 14 small validation cases. The entry's state resets with every case (one call, one problem).
  A case that runs past the budget left is invalid, and every later case is skipped.
- **The final (organisers, 17 October 2026, in a public GitHub reply).** 30 to 50 questions; the time limit is adjusted
  so that the time per problem stays about the same, "170 seconds per sample"; several submissions can be nominated for
  the final. Our mocks therefore use a job budget of N x 170 s minus the 180 s safety margin (ledger 537).

v95 / v96 were built for the validation board's 4,020 s for 21 or 14 cases (191 s or 287 s per case). At 170 s per case
the mocks show v95 losing cases once the server is 1.2x slower than modelled, and v96 losing cases even at the speed
measured on the server (tables below). v111 / v112 were built for that budget.

## What changed from v95 / v96

Four changes. The ledger ids point to our internal research notes (not part of this release); each entry there holds
the evidence summarised here.

| Change | Tracks | Ledger | Files | Effect on answers |
|---|---|---|---|---|
| 1. Moot quick-finish skip (first built as v104 / v105) | both | 510 (main), 517 (small twin) | `solution.py`, `params.json` `"qfin_skip_moot": true` | none: skipped only when it cannot change the answer |
| 2. Clock-cut guard (first built as v109 / v110) | both | 538 (after the organisers' 170 s per case, 537) | `solution.py`, `params.json` `"qfin_skip_cut": true` | none at the planned speed; acts only on a slower server |
| 3. v112's per-case targets (first built as v110) | small only | 538 | `params.json` (code is shared) | changes some small-track answers (below) |
| 4. Pre-mortem fixes F1-F5 | both | 539 (found, patches), 540 (ported, v111 / v112 built) | `solution.py` (F1, F2, F3, F5), `engine2.py` (F4) | none when no fault occurs |

**1. Moot quick-finish skip (ledger 510, 517).** In a per-case stand-in reading, the Qwen3.5-4B quick finish is skipped
when it cannot change the answer: the full decision model gives the same answer for quick finish 0 and 1, and the
`agreement_only` model (which v95 uses whenever the quick finish is skipped, discarded or fails) gives that answer too.
The gpt-oss reading, its K and its clock are unchanged, so every answer is v95's; Qwen is not loaded in those cases and
the case ends sooner. Code: `_qfin_moot()` and the `qfin_skip_moot` block in `_standin()`. On the public rows the quick
finish is moot for 25 of the 44 labelled stand-in rows (Qwen 7 of 12, DeepSeek 6 of 10, gpt-oss low 4 of 7, medium 8 of
15; these per-configuration rates are the `RATE` values in `rehearsal/final_shape/f2_sim.py`). That count uses the
first gpt-oss low read alone (logs v2 + v3). With the feature `decision.json` is fitted on (`pair_nat`, the mean of both
reads) it is 31 of 44, so 25 of 44 is the conservative choice for the time estimates (fewer moot cases, longer cases).
`training/moot_count.py` recomputes both from the logs with the entry's own `_qfin_moot()`:

```sh
cd training && python3 moot_count.py && cd ..   # read 1: moot 25 of 44, full != agreement_only 9 of 44; pair_nat: 31 and 3
```

**2. Clock-cut guard (ledger 538).** In a per-case stand-in reading, the quick finish is also skipped when the gpt-oss
reading was stopped by the case clock, which happens only when the server runs slower than the plan (the quick finish
would then end late or be cut and discarded). At the planned speed the reading ends before its deadline and the guard
does not act. Code: the `qfin_skip_cut` block in `_standin()`. The same change adds an own-run planning window
(`own_plan_seconds`, `plan_total_seconds` in the planner call), which is switched off on the main track (no
`own_plan_seconds` key) and used by change 3.

**3. v112's per-case targets (ledger 538; small track only).** `params.json` changes `case_target_seconds` 210 -> 165,
`own_case_target_seconds` 400 -> 232, and adds `"own_plan_seconds": 400`:

- The stand-in's gpt-oss reading keeps K 32, but the Qwen quick finish no longer fits in 165 s, so a stand-in case whose
  quick finish is not moot is decided by `decision.json`'s `agreement_only` model. On the public rows the two models have
  the same leave-one-template-out accuracy (0.845 on the public mix; 0.827 against 0.844 when the classes are weighted
  50-50), and they give different answers on 9 of the 44 public stand-in rows (first read; 3 of 44 with `pair_nat`;
  `training/moot_count.py`, above). Our estimate (ledger 538) is about 1.6
  expected answer changes per 14 small cases against v96 at the planned speed: no change in expected accuracy on the
  public mix, and about 0.14 fewer correct answers per 14 cases with the classes weighted 50-50. That estimate comes from
  comparisons with internal bundles that are not in this release.
- Skywork and Olmo own runs are planned in v96's 400 s window (K 3) but stopped at 232 s. An attempt stopped at 85% or
  more of its token cap still counts as not ended (the existing rule), so up to about 1.4x the mock's speed the reading
  is v96's. At 1.6x the paired board mock below shows two Olmo answers changing.

**4. Pre-mortem fixes F1-F5 (ledger 539, 540).** A fault-injection pre-mortem of the earlier nominees found crashes or
invalid answers that these fixes remove:

- **F1:** a log line never raises (closed or broken stdout, full disk, encoding). Before, the error escaped every handler,
  because each handler logs, and the case was invalid.
- **F2:** unusual call arguments do not crash: a legacy positional call `(model_id, problems)`, a non-string effort, or
  unhashable problem items. An empty (warm-up) call does not use up the per-case mode.
- **F3:** when the batch of a single problem hits CUDA out of memory, its K is halved (not below the spec's `K_min`, which
  is 4 for the gpt-oss reading) and the batch is retried, instead of losing the whole gpt-oss reading.
- **F4** (`engine2.py`): `parse_answer` no longer raises on an answer line longer than 4,300 digits (Python's limit on
  converting long digit strings to int).
- **F5:** a budget-like environment value of 0 or below is not read as a budget. Before, it made every case answer
  "robust".

Evidence (ledger 540; internal fault-injection mock, whose scripts are not part of this release): with no fault, all 420
board-shape mock cases give the same status and answer as the bundles without F1-F5. Across the fault catalogue, invalid
outcomes fall from 42 to 24 (main) and from 17 to 5 (small). The remaining 29 are job-level timeouts that no code inside a
case can prevent. Cost: an out-of-memory error that repeats adds about 60 s to a case.

## Method (short)

The entry reads the judged model itself wherever that fits, and falls back to a stand-in reading elsewhere. The decision
rules are v83's, unchanged in v95 / v96 and here.

| Configuration | Reading |
|---|---|
| Olmo-3-7B-Think | Its own run: up to 3 attempts at a 10,000-token cap; robust iff at least 2 of 3 end on their own (1 of 1 when only one attempt fits) |
| Skywork-OR1-Math-7B | Its own run: up to 3 attempts at a 9,000-token cap; robust iff at least 1 ends on its own |
| gpt-oss-120b low | Its own answer agreement at low effort (the stand-in model is the examinee here) |
| gpt-oss-120b high | Public prior: "robust" |
| gpt-oss-120b medium, Qwen3.5-4B, DeepSeek-R1-0528-Qwen3-8B | Stand-in reading (below) |

**Stand-in reading.** gpt-oss-120b at low effort makes up to 32 attempts per problem at a 3,000-token cap with the
organisers' sampling settings; the statistic is the probability that two attempts that finished on their own give the
same answer. A second reading runs Qwen3.5-4B with thinking switched off (4 attempts, 2,000 tokens; 1 if any attempt
finishes on its own). A class-balanced logistic regression on (agreement, quick finish, configuration strength) turns
these into robust / non-robust. Its coefficients are in `decision.json` (see Training data below).

**What v111 / v112 do in each case** (per-case harness; `solution.py`, the `case_*` keys in `params.json`):

- *gpt-oss high:* answered "robust" at once from the public prior, before any model is loaded.
- *Skywork and Olmo:* the judged model's own run comes first, at 3 attempts; the stand-in reading is taken only for a
  problem the own run left without a reading. Olmo uses the 7B fast decode path after its check (below); Skywork uses the
  default decode path (`"fast7b": false` in its spec). Own-run target: 400 s (v111); planned in 400 s, stopped at 232 s
  (v112).
- *Qwen, DeepSeek, gpt-oss low and medium:* the stand-in reading (up to 32 attempts in one batch), then the Qwen quick
  finish unless it is moot (change 1) or the reading was cut by the clock (change 2), inside a per-case time target
  (`case_target_seconds`: 210 s for v111, 165 s for v112). When both would not fit, the stand-in's attempts are reduced or
  the quick finish is skipped. Whenever the quick finish is skipped, `decision.json`'s `agreement_only` model decides. A
  budget-like environment variable, if the harness sets one (and it is above 0), caps the target.
- The entry logs the names of its environment variables (and the values of budget-like ones) once per process.
- A first call with several problems, and every later call in the same process, take v83's multi-call path (original
  harness) unchanged, except that gpt-oss high is answered at once there too. On that path v111 / v112 give v95 / v96's
  answers (old-path check below).

**Fitting the own runs into the hour** (original harness; still used by the multi-call path), the decode paths and the
time planning are unchanged from v95; see the v95 release README and the report's section on deployment inside the GPU
budget. In short: coverage first (one attempt per problem before any third attempt); a fast decode path for the 7B
models (`fast7b.py`) and for gpt-oss (`fastpath.py`), each checked inside every run before use (greedy agreement with the
default path at least 0.99, and a deliberately broken variant must fail the same check); per-model step-cost models plan
the number of attempts against the time left (`planner.py`, `params.json`).

**What each file does** (both submission folders):

| File | Role |
|---|---|
| `solution.py` | Harness interface (`are_robust`), per-case and multi-call handling, own-run planning and decisions |
| `engine2.py` | Model loading, prompts, generation, finished-attempt removal, features (F4 in `parse_answer`) |
| `fastpath.py` | gpt-oss decode path |
| `fast7b.py` | 7B decode path and its in-run checks |
| `planner.py` | Time planning |
| `perturb.py` | Answer-preserving surface changes to a problem text, for a research mode that is off in this entry (no `perturb` key in `params.json`) |
| `params.json` | Caps, attempts, time models, routing per configuration, the per-case targets and the switches of changes 1-3 |
| `decision.json` | Stand-in logistic coefficients and a note of the rows they were fitted on |
| `calib.json` | The organisers' 82 public rows (71 labelled), with problem templates (rebuilt in the first step) |
| `small.txt` | Small track only: an empty marker file that switches the entry to the four small configurations |

`submission_small/solution.py` differs from `submission_main/solution.py` only in its docstring and its log tag (`v130s`
instead of `v129m`); the tracks differ in `params.json` (change 3) and `small.txt`. Code comments cite "ledger N",
`miners*` folders and earlier bundle names (`sub_v114m`, `sub_v123m`, `sub_v127m` and so on). These point to our internal
research notes, which are not part of this release.

## Building the two zips

The submission is a flat zip of the folder's files. A zip stores each file's modification time and Unix mode, and a copy
or a checkout keeps neither reliably, so set both first. The times are those stored in the zips (`unzip -Z -T`); `touch`
and `zip` both use local time, so this works in any time zone. Every file must have mode 644 (`rw-r--r--`): with 664,
which a copy or checkout under umask 002 gives, both md5s differ. Then Info-ZIP 3.0 (`zip -X`) with this file order
reproduces the zips exactly:

```sh
cd submission_main
chmod 644 *
touch -t 202610151513.28 *
touch -t 202610171450.10 params.json
touch -t 202610171532.48 engine2.py solution.py
zip -X ../aimo_v111_main.zip calib.json decision.json engine2.py fast7b.py fastpath.py params.json perturb.py planner.py solution.py

cd ../submission_small
chmod 644 *
touch -t 202610161534.38 *
touch -t 202610171450.10 params.json
touch -t 202610171532.48 engine2.py solution.py
zip -X ../aimo_v112_small.zip calib.json decision.json engine2.py fast7b.py fastpath.py params.json perturb.py planner.py small.txt solution.py
cd ..
md5 aimo_v111_main.zip aimo_v112_small.zip   # md5sum on Linux; expected values in the table below
```

| Zip | md5 | Validation board (per-case harness) |
|---|---|---|
| `aimo_v111_main.zip` | `9686c9cec06ec4dc40f9b728f7ef17db` | 17/21 = 0.81 (18 October 2026; 21/21 cases answered, 2,634 s) |
| `aimo_v112_small.zip` | `8b404890d71bc5483ccce18f88887636` | 9/14 = 0.64 (18 October 2026; 14/14 cases answered, 1,913 s) |

Checked on 17 October 2026: in a scratch copy of this folder, with `calib.json` rebuilt from `train-main-v2.parquet` as
in the first step and the commands above, both zips match these md5s byte for byte (`cmp` against our built zips), in
three time zones (`TZ=UTC`, `Asia/Tokyo`, `America/New_York`), and also from a copy made under umask 002 (files 664
before the `chmod`).

Per-file md5s:

| File | md5 (submission_main) | Same as v95? |
|---|---|---|
| `solution.py` | `fe5a693846b8a57482b7418ae94a20ec` | no (changes 1, 2, 4; log tag `v129m`) |
| `engine2.py` | `277bb168c75094016789f413cab1d09a` | no (F4 only; v95 `a9504066dcdcaa3ad2acc226240e4f2c`) |
| `params.json` | `e9caafed363b4b5581cfe9ef4c32bdf8` | no (adds `"qfin_skip_moot": true`, `"qfin_skip_cut": true`) |
| `calib.json` | `d5b98e21169c0ae100c14009340b7fca` | yes |
| `decision.json` | `f29963e26fb37c91a2f4045d2116e2df` | yes |
| `fastpath.py` | `f37dc9d33728e16c3f3a9aae721caf58` | yes |
| `fast7b.py` | `4c561240c072a4ddac305b51325036b7` | yes |
| `perturb.py` | `8423d484daa95c0ef0c591aeed22d63e` | yes |
| `planner.py` | `901cb2f066201e4fbd02bec3b3669a8d` | yes |

`submission_small` has the same files as `submission_main` except `solution.py` (md5
`419a239498887d7510e86e4aa71edb75`, log tag `v130s`) and `params.json` (md5 `03e1397f37316ffa01e8ec6a8918dc1d`: the two
keys above plus `case_target_seconds` 165, `own_case_target_seconds` 232, `own_plan_seconds` 400), plus the empty
`small.txt`. Against v96, `solution.py`, `params.json` and `engine2.py` differ; the other seven files (with `calib.json`
and `small.txt`) are byte-identical.

## Hardware and runtime

- **Contest server:** one NVIDIA RTX PRO 6000 Blackwell (96 GB; about 95 GiB usable), no internet. Model weights are
  supplied offline by the harness; the entry loads them with `local_files_only=True`.
- **Software:** the organisers' evaluation image (`Dockerfile.competition` in the getting-started repository):
  PyTorch 2.12.1 with CUDA 13.2, `transformers` 5.13.0, `accelerate` 1.13.0. The entry needs nothing beyond that image.
- **Time budget, per-case harness:** stand-in cases work to a target of 210 s (v111) or 165 s (v112); Skywork / Olmo own
  runs to 400 s (v111) or 232 s (v112). The final allows about 170 s per case on average over one shared job budget, so
  the short cases (gpt-oss high, about 2 s each; stand-in cases whose quick finish is moot) make room for the longer ones.
- **Time budget, original harness:** the multi-call path plans for 3,200 s in total (`params.json`, `total_seconds`) with
  a 150 s reserve per later call, leaving a margin under the 3,600 s limit.
- **Local tests without a GPU:** `engine2.py` reads the environment variable `AIMO_LOCAL_MODEL` to load a small local
  model instead of the named one. This is for local plumbing tests only; results are meaningless.

## Mock rehearsals (local, no GPU, no model)

All mocks replace `engine2.py` with `rehearsal/mock_engine2.py`, which has no model: it advances a virtual clock by
per-model step costs taken from server logs and returns random readings (seeded by the problem text, so runs repeat).
They test timing, coverage and validity of the output, not accuracy. **Requirements:** `python3` as in "Before you
start" (the mocks use the standard library only). Run every command from this folder, after the first step.

**Run-to-run jitter.** The mock's virtual clock is real time plus an offset (`mock_engine2.py`), so a little of the
child process's real CPU time leaks into it. Job totals and seconds to spare therefore vary by about +-1 s from run to
run (for example 3,837 or 3,838 s), and per-case times by about 0.1 s; the answer, validity and decision path of each
case do not vary. Averages over the 200 random orders of the final-shape tables can move in the third decimal (0.627
against 0.626 seen once), and rows within a few seconds of the budget edge (v112, worst-case mix, N 30, 1.0x: 2 to 3 s to
spare) can flip on a slow or busy machine.

**Reference outputs.** `rehearsal/expected/` holds the output of every mock command below, made in a fresh copy of this
folder on 17 October 2026, and `case_table.csv`, our original per-case tables (one row per case run: table, speed,
configuration, synthetic problem, validity, answer, decision path, moot and clock-cut flags, seconds). Compare your outputs
with these files; expect only the jitter described above.

**Which checks use `v95_v96/`.** The paired board mock (default pairs), the v95 / v96 columns of the final-shape tables
and the old-path check compare with the scored v95 / v96 files in `v95_v96/` (copied unchanged from
`release_public_v95/`; `calib.json` copied in by the first step). Everything about v111 / v112 alone runs without it.

One bias matters for the moot skip: the mock's random readings make the quick finish moot in about 97% of stand-in
cases, against 25 of 44 public stand-in rows. Raw `run_per_case.py` times therefore understate v111 / v112's time per
case. The final-shape tables correct for this (`f2_sim.hybrid`: a moot case keeps its short time only at the public-row
rate, otherwise it takes the time of the same bundle with the skip switched off).

### Per-case harness: `rehearsal/run_per_case.py`

A mock of the per-case harness: every case runs in a fresh Python process, one after another, on a shared budget
(default 4,020 s); a case that runs past the budget left times out and every later case is skipped. Model loading and
the decode-path checks are charged in every process. The step costs are calibrated to the server timings of a per-case
rerun (see the comment block at the top of the script).

```sh
python3 rehearsal/run_per_case.py --bundle submission_main --shape main               # 21 cases in the board's order
python3 rehearsal/run_per_case.py --bundle submission_main --shape main --slow 1.4    # every step 1.4x slower
python3 rehearsal/run_per_case.py --bundle submission_small --shape small             # 14 cases
python3 rehearsal/run_per_case.py --bundle submission_small --shape small --slow 1.4
python3 rehearsal/run_per_case.py --bundle submission_main --shape main --budget 3390  # 21 x 170 - 180 s
```

Other options: `--shape final` / `final_mix`, `--seed`, `--budget`, `--no-budget`, `--set key=json` (overrides a
`params.json` value), `--mockenv K=V`, `--log FILE`; `--suite` compares internal bundle names that do not exist here.

Checked on 17 October 2026 from a fresh copy of this folder (raw mock times, seed 1): v111 21 of 21 main cases valid,
2,790 s at modelled speed and 3,172 s at 1.4x slower; v112 14 of 14 small cases valid, 2,237 s and 2,561 s (all against
4,020 s); with `--budget 3390`, v111 21 of 21 valid in 2,790 s of 3,390 s; 0 timeouts, 0 skipped everywhere. Reference
outputs, in the order of the commands: `rehearsal/expected/per_case_main.out`, `per_case_main_1.4x.out`,
`per_case_small.out`, `per_case_small_1.4x.out`, `per_case_main_budget3390.out`.

**Paired with v95 / v96: `rehearsal/final_shape/board_mock.py`.** It runs the board shapes for two bundles side by side
(seeds 1 and 2; 1.0x, 1.4x, 1.6x; the 4,020 s board budget and N x 170 - 180 s) and prints case-by-case answer identity.
The default pairs are v95 / v96 (`v95_v96/submission_main`, `v95_v96/submission_small`) against v111 / v112; other pairs
can be given as `MAIN_OLD MAIN_NEW SMALL_OLD SMALL_NEW`. It takes about 25 s.

```sh
python3 rehearsal/final_shape/board_mock.py > board_mock.out     # compare with rehearsal/expected/board_mock.out
```

Without `v95_v96/` (or to check only the v111 / v112 cells), pair each bundle with itself; this reproduces every
v111 / v112 cell of the table below:

```sh
python3 rehearsal/final_shape/board_mock.py submission_main submission_main submission_small submission_small > board_mock_self.out
```

Checked on 17 October 2026 (raw mock times; the v95 / v96 column comes from `v95_v96/`):

| Track, budget | Speed | v95 / v96 | v111 / v112 | Same answers |
|---|---|---|---|---|
| main, 4,020 s | 1.0x / 1.4x / 1.6x | 21/21 answered; 3,339 / 3,837 / 3,986 s (seed 1) | 21/21; 2,790 / 3,172 / 3,320 s | 21/21 at every speed, both seeds |
| main, 3,390 s (21 x 170 - 180) | 1.0x | 21/21 | 21/21 | 21/21 |
| main, 3,390 s | 1.4x and 1.6x | 17/21 (1 timeout, 3 skipped) | 21/21 | 17/21 (all 17 v95 answers) |
| small, 4,020 s | 1.0x / 1.4x | 14/14; 2,574 / 3,065 s | 14/14; 2,237 / 2,561 s | 14/14 |
| small, 4,020 s | 1.6x | 14/14; 3,248 s | 14/14; 2,640 s | 12/14 (two Olmo answers change) |
| small, 2,200 s (14 x 170 - 180) | 1.0x | 12/14 (1 timeout, 1 skipped) | 13/14 (1 timeout) | 12/14 |
| small, 2,200 s | 1.4x / 1.6x | 10/14, 9/14 | 11/14, 11/14 | 10 to 12 of 14 |

A 14-case small job at 14 x 170 - 180 s is tighter per case (157 s) than a 30 to 50-case final (164 to 166 s), and v112
loses one case there even at modelled speed.

### Final shape (30 to 50 cases at N x 170 s): `rehearsal/final_shape/`

Because a case process keeps no state and receives no budget, a case's time and answer depend only on (bundle,
configuration, problem, speed). `f2_tables.py` (with `shapes_mock.py`) runs each case once in a fresh `run_per_case.py`
process and stores the table; `f2_sim.py` then simulates any job layout exactly from the table with the harness rules
(cases in order on one shared budget; a timeout ends the job). `final_shape_tables.py` prints the tables below.

```sh
sh rehearsal/final_shape/build_tables.sh          # PY=/path/to/python to choose another Python than python3
python3 rehearsal/final_shape/compare_tables.py   # rebuilt tables vs rehearsal/expected/case_table.csv
python3 rehearsal/final_shape/final_shape_tables.py --out final_shape_tables.md   # vs rehearsal/expected/final_shape_tables.md
```

`build_tables.sh` builds the per-case tables of v111 and v112 on 50 synthetic new problems at 1.0x / 1.2x / 1.4x / 1.6x,
plus the same bundles with the moot skip off (`--set qfin_skip_moot=false`, used for the public-row correction above),
and the v95 / v96 tables from `v95_v96/` for comparison (skipped, with a message, when `v95_v96/` has no `calib.json`;
`V95=DIR` points at another folder holding `submission_main/` and `submission_small/`). It writes the tables to
`rehearsal/final_shape/tables/`. Run time with 5 workers on an idle Apple-silicon Mac (M4): about 45 s for all six
tables (v111, v112, their moot-skip-off twins, v95, v96); about 2.5 minutes was seen on a busy machine. `compare_tables.py` checks every case run against our original
tables (validity, answer, decision path and flags must be identical; it prints the largest time difference) and exits
non-zero on any mismatch. `final_shape_tables.py` takes about 1 s.

What the simulation assumes (`f2_sim.py`, comment block):

- budget N x 170 s minus the 180 s safety margin (the result without the margin is also shown when it differs);
- the validation mix of configurations (main: Qwen 2, Skywork 3, Olmo 2, DeepSeek 3, high 3, low 5, medium 3 per 21;
  small: Qwen 5, Skywork 3, Olmo 3, DeepSeek 3 per 14) and a worst-case mix without fast cases (main: Qwen 4, Olmo 6,
  DeepSeek 4, low 4, medium 3; small: Qwen 4, Olmo 6, DeepSeek 4), scaled to N;
- a board-like order (7B and 4B configurations in blocks, then the gpt-oss efforts interleaved), and 200 random orders;
- speed `srv`: the 1.0x mock times scaled per configuration to v95's server board run (3,030 s), which the scaled mock
  gives as 3,125 s; 1.0x to 1.6x: the mock's step costs times that factor;
- expected accuracy: each answered case scores its configuration's public-row accuracy (in-sample, v95 line) if a full
  reading decided it, or the public robust base rate otherwise; an unanswered case scores 0. This is a rough model, not a
  prediction of the final score.

Checked on 17 October 2026 from a fresh copy of this folder: the rebuilt tables match our original ones
(`rehearsal/expected/case_table.csv`) case by case: same answer, validity and decision path on all 3,400 v111 / v112 and
all 2,200 v95 / v96 case runs, times within about 0.1 s. `rehearsal/expected/final_shape_tables.md` is the output of
`final_shape_tables.py` on our original tables; on rebuilt tables, seconds to spare differ from it by up to 1 s and a
random-order average can differ in the third decimal (jitter, above); the board-like-order counts below did not change. Cases answered of N, validation mix, board-like order, budget N x 170 - 180 s (the
v95 / v96 column needs the v95 / v96 tables, from `v95_v96/`):

| Track | Speed | v95 / v96 (N = 30 / 40 / 50) | v111 / v112 (N = 30 / 40 / 50) |
|---|---|---|---|
| main | srv | 30 / 40 / 50 | 30 / 40 / 50 (1,089 / 1,447 / 1,575 s to spare) |
| main | 1.0x | 30 / 40 / 50 | 30 / 40 / 50 (543 / 845 / 1,163 s to spare) |
| main | 1.2x | 28 / 39 / 48 | 30 / 40 / 50 |
| main | 1.4x | 26 / 36 / 45 | 30 / 40 / 50 (467 / 784 / 938 s to spare) |
| main | 1.6x | 25 / 34 / 44 | 30 / 40 / 50 (256 / 515 / 610 s to spare) |
| small | srv | 28 / 37 / 48 | 30 / 40 / 50 (470 / 491 / 819 s to spare) |
| small | 1.0x | 27 / 36 / 46 | 30 / 40 / 50 (238 / 209 / 462 s to spare) |
| small | 1.2x | 24 / 32 / 41 | 28 / 36 / 47 |
| small | 1.4x | 23 / 30 / 38 | 27 / 35 / 45 |
| small | 1.6x | 21 / 28 / 36 | 25 / 33 / 43 |

Mean case seconds at the validation mix (public-row moot rate): main v95 157 s, v111 143 s at 1.0x (147 / 132 s at
`srv`); small v96 180 s, v112 156 s at 1.0x (171 / 149 s at `srv`). Over 200 random orders the validation-mix results
are the same as above for v111 (every case answered in every draw at every speed) and, for v112, every case answered at
`srv` and 1.0x. On the worst-case mix at 1.0x, v111 loses 2 to 3 cases in board-like order (up to 5 in the worst random
draw) and v112 up to 1 (up to 2); full tables in the script's output. Our estimate is that the small track cannot answer
every case at 1.4x with its readings intact, because its per-case floor is about 172 s at that speed (ledger 538).

### Old single-process path: `rehearsal/final_shape/oldpath_check.py`

Runs two bundles through all seven calls in one process (12 synthetic problems per call, the original harness's
multi-call path) and compares the 84 answers.

```sh
python3 rehearsal/final_shape/oldpath_check.py submission_main v95_v96/submission_main     # vs rehearsal/expected/oldpath_main.out
python3 rehearsal/final_shape/oldpath_check.py submission_small v95_v96/submission_small   # vs rehearsal/expected/oldpath_small.out
```

Checked on 17 October 2026: identical answers on the old path, 84 of 84, for v111 against v95 and for v112 against v96
(last line of each output: `identical answers on the old single-process path: True 84 answers`).

### Original harness: `rehearsal/run_final_scale.py`

Runs a copy of a submission folder through the organisers' ingestion program (one process, all calls) at board scale
and at an assumed final scale (30 problems x 7 configurations), at three speeds. The ingestion program is the
organisers' public getting-started repository, https://github.com/aimo-interp/getting-started, file
`components/ingestion_program/ingestion.py` at commit `de794053debe75a711400696e66b60937cebbb1b` (md5 of that file:
`6a42cae18112b5d4fc5d71c9bd4fd1c7`). It is not included here. Clone that repository into this folder as
`getting-started/` (the script looks there), or set `AIMO_INGESTION` to the path of `ingestion.py`:

```sh
git clone https://github.com/aimo-interp/getting-started && git -C getting-started checkout de794053debe75a711400696e66b60937cebbb1b
md5 getting-started/components/ingestion_program/ingestion.py   # 6a42cae18112b5d4fc5d71c9bd4fd1c7
MOCK_FAST7=1 MOCK_FAST7_T=Skywork:20:0.2,Olmo:12:1.8 MOCK_OWN_T=Olmo:8:7.1 python3 rehearsal/run_final_scale.py submission_main
MOCK_FAST7=1 MOCK_FAST7_T=Skywork:20:0.2,Olmo:12:1.8 MOCK_OWN_T=Olmo:8:7.1 python3 rehearsal/run_final_scale.py submission_small small
```

Checked on 17 October 2026 for v111 / v112 (fresh copy, `AIMO_INGESTION` pointing at a local clone at that commit; the
clone step itself needs a network connection and was not repeated offline): all 39 runs per track (13 shapes x 3
speeds) ended inside 3,600 s (latest 3,041 s main, 3,123 s small) with 0 invalid predictions and 0 fallbacks, the same
as v95 / v96. Both tracks together take a few seconds. The outputs are written to `rehearsal/final_scale_submission_main.out` and
`rehearsal/final_scale_submission_small_small.out` (the second argument `small` adds `_small`); the reference copies
have the same names in `rehearsal/expected/`. See the v95 release README for the mock settings.

### Changes from our working copies

Paths and usage lines only, no logic:

- `run_per_case.py`, `shapes_mock.py`, `f2_tables.py` and `board_mock.py`: the usage lines name `python` (`python3` in
  `board_mock.py`) instead of our local Python path. Otherwise `run_per_case.py`, `mock_engine2.py`, `run_final_scale.py` and `dress_wrapper.py` are
  byte-identical to the v95 release's copies, and `shapes_mock.py` and `oldpath_check.py` to our working copies.
- `f2_tables.py`: imports `shapes_mock.py` from its own folder, reads the public templates from
  `submission_main/calib.json`, and points its STD options at a folder that does not exist here (`--std` was for
  internal research bundles and does not run in this release).
- `f2_sim.py`: reads the tables from `rehearsal/final_shape/tables/` or `F2_TABLES` (it was a scratch folder).
- `board_mock.py`: takes the bundle pairs from the command line (they were internal bundle names); the default pairs
  are `v95_v96/` against this release's folders.
- `final_shape_tables.py` and `build_tables.sh` are new: they replace our internal driver and build script, which named
  internal bundles. The simulation itself is `f2_sim.py`'s. `build_tables.sh` reads the v95 / v96 code from `v95_v96/`
  (or `V95=DIR`).
- New for this release, no counterpart in our working copies: `compare_tables.py` (checks rebuilt tables against
  `rehearsal/expected/case_table.csv`, and wrote that CSV from our original tables with `--write`),
  `training/moot_count.py`, the reference outputs in `rehearsal/expected/`, and the copy of the v95 / v96 files in
  `v95_v96/` (byte-identical to `release_public_v95/submission_main/` and `submission_small/`).

## Dress rehearsal (on the contest server)

`rehearsal/dress_wrapper.py` is unchanged from the v95 release and was not re-run for v111 / v112. It is a
research-only submission that runs a candidate entry at the final-test shape of the original harness on the real
server, answering every hidden case "robust". See the v95 release README for how to build and read it.

## Training data and how the fitted files were made

`calib.json` and `decision.json` are byte-identical to v95's, and `training/` is the v95 release's folder unchanged
except for the added `moot_count.py`.

**Only the organisers' public labelled rows were used:** `train-main-v2.parquet`, the public train set covering the
main-track models, published by the organisers on Hugging Face (organisation `aimo-interp`). It has 82 rows over 28
problem templates: 52 robust, 19 non-robust and 11 in the organisers' unlabelled band. No other labels were used.

**`calib.json`** holds these 82 rows with their problem template; `training/build_calib.py` rebuilds it (first step).
It is a reconstruction written for the release; it uses the same template rule as our original scripts and reproduces
the shipped file byte for byte.

**`decision.json`** was written by `training/refit_low16.py`, which runs a chain of scripts by `exec`:
`refit_low16.py` -> `consolidated.py` -> `medium.py` -> `scorecard.py` -> `pool_all.py` (copied unchanged). The model
is a class-balanced logistic regression (Newton steps with a small ridge, standardised features), fitted on the 71
labelled rows with three features:

- `pair_nat`: the gpt-oss-120b low-effort answer agreement at a 3,000-token cap, the mean of two independent K 8 reads
  of the 28 public templates;
- `qfin`: whether any of 4 Qwen3.5-4B no-thinking attempts finished within 2,000 tokens;
- `strength`: 1 for the small models and gpt-oss low, 2 for medium, 3 for high.

It also writes two reduced models (`agreement_only`, `finish_only`) that the entry uses when one reading is missing,
and a leave-one-template-out accuracy note for each.

**Inputs (included).** The readings come from four server logs of our own research runs on the 28 PUBLIC templates
(hidden validation cases appear in them only as counts), in `training/runs/`; the public rows the scripts read are in
`training/sub_v1c/calib.json` (identical to `submission_main/calib.json`). Run the fit from inside `training/`:

| Log (path the scripts expect) | md5 | Used for |
|---|---|---|
| `runs/r1_small_957664.log` | `9ec8763a36fe32ae390372b0816604b8` | Qwen quick-finish reading (`qfin`) |
| `runs/v2_main_960630.log` | `7aa21a2f34ad418b4ed82a830831efa1` | gpt-oss low read 1 (templates 1-9), medium read |
| `runs/v3_main_960796.log` | `648634428d4bdbf780b74b1433c62894` | gpt-oss low read 1 (templates 10-28), medium read |
| `runs/v4_main_960863.log` | `d731ebfd7fecb85ab7496cbec1d05f57` (problem-text lines redacted; original `d4ead196dfabd4aa264699c42c49f208`) | gpt-oss low read 2 |

```sh
cd training && python3 refit_low16.py decision.json && cd ..   # needs numpy + pandas; writes training/decision.json
md5 training/decision.json                                     # f29963e26fb37c91a2f4045d2116e2df
```

Checked on 17 October 2026 from a fresh copy of this folder (Python 3.11.15, numpy 2.4.6, pandas 3.0.6, pyarrow 25.0.1;
also Python 3.9.6, numpy 2.0.2, pandas 2.3.3): the output is byte-identical to the shipped `decision.json` (md5
`f29963e26fb37c91a2f4045d2116e2df`). It prints the notes 0.845 / 0.844 (`full`, public mix / 50-50) and 0.845 / 0.827
(`agreement_only`).

The own-run thresholds in `params.json` (1 of 3 attempts for Skywork, 2 of 3 for Olmo) and the "robust" prior for
gpt-oss high were chosen by hand from the public rows and our logs, not fitted by a script; they are not validated
rules. The per-case time targets were also set by hand and not fitted to labels: 210 / 400 s (v95, kept in v111) and
165 / 232 s (v112, chosen from a mock search over the two targets, ledger 538).

## Optional per-case-safe variants: v115 (main) and v116 (small)

**Why.** The organisers' reply of 17 October gives "170 seconds per sample" for the final but does not say whether that
is an average over the job, which is what v111 / v112 are built for, or a limit on each case. Another team asked the
organisers exactly this on 19 October (getting-started GitHub issue #6); there was no answer when this section was
written. Under a 170 s per-case limit some v111 / v112 cases would time out. On the validation board v111's two Olmo
cases took 209 s and four stand-in cases 173 to 179 s, so it would answer 15 of 21; v112's three Olmo cases took 173,
210 and 210 s, so it would answer 11 of 14 (measured case times of the board runs; ledger 572, 573). v115 and v116 keep
every case below about 160 s. Use v111 / v112 if 170 s is an average over the job, v115 / v116 if it is a per-case
limit.

**What changes.** Only `params.json`, the `solution.py` docstring and the log tag (`v135m` / `v136s`); every other file
is byte-identical to v111's / v112's, and the decision rules are the same:

| `params.json` key | v111 → v115 | v112 → v116 | Why |
|---|---|---|---|
| `case_target_seconds` (stand-in cases) | 210 → 165 | 165 (unchanged) | v112's small-track target, now on main too |
| `own_case_target_seconds` (Skywork / Olmo own runs stopped at) | 400 → 160 | 232 → 160 | ends own-run cases inside 170 s |
| `own_plan_seconds` | absent → 400 | 400 (unchanged) | own runs are still planned at K 3, as before |
| `own_load_seconds_est` | 25 → 0 | 25 → 0 | with 25 s the pre-load check would skip Skywork's own run at a 160 s target |
| `sky` → `cap` (Olmo's own-run token cap; the key name is historical) | 10,000 → 7,200 | 10,000 → 7,200 | Olmo's 3 attempts at 10,000 tokens took about 198 s |

Olmo's rule is unchanged (robust iff at least 2 of 3 attempts end on their own), but at the shorter cap fewer attempts
end, so Olmo cases lean towards "non-robust": on the small board all three Olmo cases ended 0 of 3, where v112 had one
case at 3 of 3 (ledger 575).

**Board results** (OFFICIAL validation board, per-case harness, one run each, 19 October 2026):

| Zip | md5 | Board | Cases answered | Job | Longest case |
|---|---|---|---|---|---|
| `aimo_v115_main.zip` | `ad191e2e2262b0a918ec1aaf83bcf9c7` | 15/21 = 0.71 | 21/21 | 2,288 s | 148 s |
| `aimo_v116_small.zip` | `d3ada3a4b8ff05b5876582246008bbf9` | 9/14 = 0.64 | 14/14 | 1,720 s | 147 s |

v116 scored the same as v112. v115 scored two fewer than v111 (17/21): the two calls that differ are both stand-in cases
whose gpt-oss reading differed between the 18 and 19 October runs (run-to-run reading noise on the server); no Olmo,
Skywork or prior call changed (ledger 576). One draw per file on 21 and 14 cases, not new problems.

**Building the two zips.** After the first step (which copies `calib.json` into both `v115_v116/` folders), with the
same Info-ZIP 3.0 and the same rules as above (mode 644, modification times as stored in the zips, local time):

```sh
cd v115_v116/submission_main
chmod 644 *
touch -t 202610151513.28 *
touch -t 202610171532.48 engine2.py
touch -t 202610191206.26 params.json solution.py
zip -X ../aimo_v115_main.zip calib.json decision.json engine2.py fast7b.py fastpath.py params.json perturb.py planner.py solution.py

cd ../submission_small
chmod 644 *
touch -t 202610161534.38 *
touch -t 202610171532.48 engine2.py
touch -t 202610191206.26 params.json solution.py
zip -X ../aimo_v116_small.zip calib.json decision.json engine2.py fast7b.py fastpath.py params.json perturb.py planner.py small.txt solution.py
cd ..
md5 aimo_v115_main.zip aimo_v116_small.zip   # ad191e2e2262b0a918ec1aaf83bcf9c7, d3ada3a4b8ff05b5876582246008bbf9
cd ..
```

Per-file md5s: `solution.py` `a0a1126e14c97ceb889b70a43d0e9918` (v115) and `685c9d2ebbb374232d9a00a1188912f7` (v116);
`params.json` `afc8776517ec92ad23f4060e3203e990` (the same file in both); the other files as in the v111 table above
(`small.txt` empty).

Checked on 19 October 2026 from a fresh copy of this folder, with `calib.json` rebuilt from `train-main-v2.parquet` as
in the first step: these commands reproduce both zips byte for byte (`cmp` against our uploaded zips) under `TZ=UTC`,
`Asia/Tokyo`, `America/New_York` and `America/Los_Angeles`, and from a copy made under umask 002. The per-case mock runs
them unchanged (mock, not server): `python3 rehearsal/run_per_case.py --bundle v115_v116/submission_main --shape main`
gives 21 of 21 cases valid in 2,693 s, longest case 150 s (2,858 s and 162 s with `--slow 1.4`); with
`--bundle v115_v116/submission_small --shape small`, 14 of 14 in 2,091 s, longest 150 s (2,228 s and 162 s at 1.4x).
The mock reference outputs in `rehearsal/expected/` and the final-shape tables cover v111 / v112 only. The replica of
the board runs behind the per-case numbers above (our lane F4) is not part of this release.

## Seed variants: v121 (main) and v122 (small)

**Why.** Every reading is a random draw with fixed seeds, so two nominated files with the same code would read every
problem the same way whenever they run in the same server state. v121 and v122 shift every seed by a fixed offset, so
they read each problem independently of v115 / v116. If the final counts the best of several nominated entries, that
adds an independent read; otherwise v121 / v122 are interchangeable with v115 / v116 (same decision rules, same time
targets, every case under 170 s).

**What changes.** One line in `_read()` of `solution.py`, the function through which every reading runs (the stand-in's
gpt-oss reading, the Qwen quick finish and the Skywork / Olmo own runs):

```python
    seed0 = seed0 + _P.get("seed_offset", 0)
```

with the new `params.json` key `"seed_offset": 271828` (fixed before any run), plus a new first paragraph in the
`solution.py` docstring and the log tag (`v138m` / `v139s` instead of `v135m` / `v136s`). Every other file is
byte-identical to v115's / v116's.

**Board results** (OFFICIAL validation board, per-case harness, one run each; uploaded and scored on 20 October 2026
UTC, the night of 19 to 20 October PDT):

| Zip | md5 | Board | Cases answered |
|---|---|---|---|
| `aimo_v121_main.zip` | `22ced3169a4d73b5cfe9b7ceb0d815b6` | 15/21 = 0.71 | 21/21, 0 invalid |
| `aimo_v122_small.zip` | `4de6852eee8d4c3e6ccb07576c422a31` | 9/14 = 0.64 | 14/14, 0 invalid |

Both equal their parents' totals (v115 15/21, v116 9/14). From reading noise alone a board total moves by about 1.3
cases on main and 1.0 on small (report, Section 2.6), so one draw each cannot rank the variants. We read only the scores
of these two runs, not their logs, so their job time and longest case are not given here.

**Building the two zips.** After the first step (which copies `calib.json` into both `v121_v122/` folders), with the
same Info-ZIP 3.0 and the same rules as above (mode 644, modification times as stored in the zips, local time). Every
file carries the same time:

```sh
cd v121_v122/submission_main
chmod 644 *
touch -t 202610200300.00 *
zip -X ../aimo_v121_main.zip calib.json decision.json engine2.py fast7b.py fastpath.py params.json perturb.py planner.py solution.py

cd ../submission_small
chmod 644 *
touch -t 202610200300.00 *
zip -X ../aimo_v122_small.zip calib.json decision.json engine2.py fast7b.py fastpath.py params.json perturb.py planner.py small.txt solution.py
cd ..
md5 aimo_v121_main.zip aimo_v122_small.zip   # 22ced3169a4d73b5cfe9b7ceb0d815b6, 4de6852eee8d4c3e6ccb07576c422a31
cd ..
```

Per-file md5s: `solution.py` `a0c36a91da34cdacc557ef2f3089f199` (v121) and `da00c2d23271b332d300484ea06176a9` (v122);
`params.json` `5ade8fb245f122f23b84d1f7a3747399` (the same file in both); the other files as in the v111 table above
(`small.txt` empty).

Checked on 20 October 2026 from a fresh copy of this folder, with `calib.json` rebuilt from `train-main-v2.parquet`
(md5 `3394dba3f01210c6f653ae0bea9f7de5`, the 82-row file) as in the first step: the commands of this README rebuild all
six zips (v111, v112, v115, v116, v121, v122) byte for byte (`cmp` against our uploaded zips) under `TZ=UTC`,
`Asia/Tokyo`, `America/New_York` and `America/Los_Angeles`, and from a copy made under umask 002 (files 664 before the
`chmod`), and `refit_low16.py` reproduces `decision.json`. The per-case mock runs v121 / v122 unchanged (mock, not
server): `python3 rehearsal/run_per_case.py --bundle v121_v122/submission_main --shape main` gives 21 of 21 cases valid
in 2,693 s, longest case 150 s (2,857 s and 162 s with `--slow 1.4`); with `--bundle v121_v122/submission_small --shape
small`, 14 of 14 in 2,091 s, longest 150 s (2,228 s and 162 s at 1.4x). These are v115's / v116's mock times within the
mock's jitter. The mock tests timing and validity, not accuracy, and the reference outputs in `rehearsal/expected/`
cover v111 / v112 only.

## Limitations

See the report's Limitations section. In short:

- v111 and v112 have each run once on the validation board (status line above): one draw per file on 21 and 14
  cases, not new problems. Timings labelled as mock are virtual-clock mocks calibrated to server logs, not server
  measurements, and the speed of the final's server is not known.
- In the mock, v112 cannot answer every small-track case at 170 s per case once the server is 1.2x slower than modelled
  (at 1.4x: 27 of 30, 35 of 40, 45 of 50), and v112 changes some answers against v96 (change 3).
- The fault-injection evidence for F1-F5 comes from internal scripts that are not part of this release.
- v115 and v116 have each run once on the validation board; whether the final needs them depends on an answer the
  organisers had not given when they were added. Their timing evidence beyond the board runs is the per-case mock above
  and an internal replica that is not part of this release.
- v121 and v122 have each run once on the validation board, and we read their scores, not their logs; their timing
  evidence is their parents' board runs and the per-case mock above. Whether a second, independently seeded nominee
  helps depends on how the final ranks several nominated entries, which the organisers had not said on 20 October.
- Few public labels per configuration; the stand-in's public accuracy is in-sample; the expected-accuracy column of the
  final-shape tables is a rough in-sample model.

## Audit script: `audit/`

`audit/audit.py` (numpy only; added on 17 October 2026) reproduces the generalisation-audit tables of the report
(Sections 2.2-2.3). Given per-row out-of-sample calls (`v95_rows.csv`: template, label, call, fresh, subset,
configuration) and the list of board-chosen changes (`v95_changes.csv`), it prints accuracy with a template-cluster
bootstrap, the board-mix accuracy, a binomial-mixture board prediction with P(score <= observed), and the keep-if-better
selection null. It does not need the first step. Run it from `audit/`:

```sh
cd audit
python3 audit.py v95_rows.csv v95_changes.csv --board main:21:10:16/19:all,fresh --board small:14:7:10/9/8:small,small+fresh --draws 19,17,18,16 > audit.out
cmp audit.out audit_v95.out && echo identical
cd ..
```

Checked on 17 October 2026: the output is byte-identical to `audit_v95.out` under Python 3.11.15 and 3.9.6.

## Report scripts: `report/figures/`

The four-page report (Appendix A) names the scripts behind its tests, intervals and matched-case numbers. They are in
`report/figures/`, each with its output and, for a pre-registered test, the pre-registration and the md5 recorded before
the script first ran (`*.md5`; each script refuses to run if its pre-registration has changed):

| Script → output | Numbers in the four-page report | Pre-registration (md5) |
|---|---|---|
| `perm_samelabel.py` → `perm_samelabel.out` | the null that ignores difficulty: 5.88 of 16 on average (Appendix A) | `PREREG_samelabel.txt` (6afb3e0fdfa4ea7af5f455d24deb463d) |
| `samelabel_difficulty.py` → `samelabel_difficulty.out` | the difficulty-preserving null: 9.43 of 16, p <= 0.0001; 10.30 of 15, p = 0.0035; AUC 0.882 to 0.976 (Section 4, Appendix A) | `PREREG_samelabel_difficulty.txt` (f1df21c8fc9961e443536e2ccd978565) |
| `intervals_v37.py` → `intervals_v37.out` | template-bootstrap and exact intervals (Appendix A) | the same |
| `paired_v38.py` → `paired_v38.out` | paired tests against always robust, McNemar p = 0.1796 and 0.1797 (post hoc) | none |
| `recompute_matched_v32.py` → `recompute_matched_v32.out` | the matched-case table and the label-peeking oracle (Appendix A) | none |
| `rows80.py` → `rows80.out` | own run 8.0 against 7.25 on the 9 Skywork cases labelled later (Section 5); 68.75 of 80 (Appendix A) | `PREREG_rows80.txt` (c0f69a27f6c38bcfb84ac1193fac1d04) and `ADDENDUM_rows80.txt` |
| `make_agreement_by_label_v32.py` → `make_agreement_by_label_v32.out` | Figure 1 (it writes the figure next to itself; the copy in `report/four_page/` is byte-identical) | none |

`perm_samelabel_run1_prereg_only.out` is the first run of `perm_samelabel.py`, before its post hoc lines were added; the
first lines of `perm_samelabel.out` are identical to it. The md5s that the outputs print for other scripts are those of
our working copies, which differ from the copies here only in the line that sets the data folder (and, in the figure
script, the path printed in its last line).

**These scripts read files that are not in this repository**, so they can be read here but not re-run from it alone. Set
`AIMO_DIR` to the folder that holds them (the scripts give each path relative to it): the organisers' public parquet at
two revisions (`aimo-interp/train-main-v2`, revision 23791d9b as `hf/train-main-v2.parquet`, and the 15 October revision
fa8af758), `calib.json` (which `training/build_calib.py` rebuilds), our server logs of reads of the public templates (for
example the read of 15 October, Codabench 987666), and our analysis modules and their inputs (for example lane G's loader
`g_common.py`, and lane X's `xbench.py` with its pool of attempts). Each script needs numpy and pandas (also scipy for
`intervals_v37.py`, `paired_v38.py` and `recompute_matched_v32.py`; matplotlib for the figure), writes only its `.out`
(and the figure) next to itself, and runs on a CPU in under two minutes:

```sh
AIMO_DIR=/path/to/held/folder python3 report/figures/perm_samelabel.py
```

Checked on 23 October 2026: run from this layout with `AIMO_DIR` set to our folder, every `.out` above and the figure
were reproduced byte for byte (Python 3.11.15 with numpy 2.4.6, pandas 3.0.3 and scipy 1.17.1; the figure with Python
3.9.6 and matplotlib 3.9.4).
