"""Lane F2: board-shape per-case mocks (rehearsal/run_per_case.py, 21 main / 14 small cases on the 4,020 s board budget, and the
same cases on a 170 s-per-case budget minus the 180 s margin), new bundle vs its parent, seeds 1-2, speeds 1.0 / 1.4 / 1.6.
Prints job seconds, invalid counts and case-by-case answer identity. OFFLINE.
usage: python3 rehearsal/final_shape/board_mock.py [MAIN_OLD MAIN_NEW SMALL_OLD SMALL_NEW] > OUT
Release copy: the bundle pairs are taken from the command line (folders relative to the release folder, or absolute); the
default compares the v95 / v96 code shipped in v95_v96/ (calib.json copied in, README first step) with v111 / v112."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(WORK, "rehearsal"))
import run_per_case as R  # noqa: E402

_A = sys.argv[1:5] if len(sys.argv) >= 5 else ["v95_v96/submission_main", "submission_main",
                                                "v95_v96/submission_small", "submission_small"]
PAIRS = {"main": (_A[0], _A[1]), "small": (_A[2], _A[3])}
for shape, (old, new) in PAIRS.items():
    n = 21 if shape == "main" else 14
    for budget in (4020.0, 170.0 * n - 180.0):
        for seed in (1, 2):
            for slow in (1.0, 1.4, 1.6):
                a = R.run(old, shape, seed=seed, slow=slow, budget=budget, quiet=True)
                b = R.run(new, shape, seed=seed, slow=slow, budget=budget, quiet=True)
                same = sum(1 for x, y in zip(a["rows"], b["rows"]) if x["pred"] == y["pred"] and x["status"] == y["status"])
                diff = [f"{i + 1}:{x['cfg']} {x['pred']}->{y['pred']}" for i, (x, y) in enumerate(zip(a["rows"], b["rows"]))
                        if x["pred"] != y["pred"] or x["status"] != y["status"]]
                print(f"{shape:5s} budget {budget:5.0f} seed {seed} {slow}x | {old} {a['total']:5.0f}s ok {a['ok']}/{n} "
                      f"(to {a['timeouts']}, skip {a['skipped']}) | {new} {b['total']:5.0f}s ok {b['ok']}/{n} "
                      f"(to {b['timeouts']}, skip {b['skipped']}) | identical {same}/{n}" + (f" | {'; '.join(diff)}" if diff else ""),
                      flush=True)
