"""Public-row counts quoted in the README (change 1 and change 3), recomputed with the entry's own rule.

- "moot": the Qwen quick finish cannot change the answer (submission_main/solution.py, _qfin_moot: the full model gives the
  same answer for quick finish 0 and 1, and the agreement_only model gives that answer too);
- "full != agreement_only": the full model with the row's logged quick finish and the agreement_only model disagree.

Rows: the 44 labelled public rows of the four stand-in configurations (Qwen 12, DeepSeek 10, gpt-oss low 7, medium 15).
The agreement value per row comes from the logs in runs/. The README's 25 of 44 and 9 of 44 (and the per-configuration
rates hard-coded in rehearsal/final_shape/f2_sim.py, RATE: 7/12, 6/10, 4/7, 8/15) were computed with gpt-oss low read 1
only (logs v2 + v3, pool_all.py at cap 3,000), as printed first. decision.json is fitted on pair_nat, the mean of read 1
and read 2 (v4 log); the counts with that feature, and with read 2 alone, are printed below it for comparison.

usage (from training/, after the README's first step; needs numpy + pandas):  python3 moot_count.py
"""
import contextlib
import importlib.util
import io
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
SUB = os.path.join(HERE, "..", "submission_main")
spec = importlib.util.spec_from_file_location("entry_solution", os.path.join(SUB, "solution.py"))
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)          # the entry's own _margin / _qfin_moot / _STRENGTH, with its decision.json

CFG = {("Qwen/Qwen3.5-4B", "default"): "Qwen", ("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "default"): "DeepSeek",
       ("openai/gpt-oss-120b", "low"): "low", ("openai/gpt-oss-120b", "medium"): "medium"}
ORDER = ("Qwen", "DeepSeek", "low", "medium")


def count(rows, feat):
    tot, moot, diff = Counter(), Counter(), Counter()
    for _, r in rows.iterrows():
        c = CFG.get((r.model_id, r.effort))
        if c is None:
            continue
        a, s = float(r[feat]), S._STRENGTH[f"{r.model_id}:{r.effort}"]
        tot[c] += 1
        moot[c] += bool(S._qfin_moot(a, s))
        if r.qfin == r.qfin:   # logged quick finish present
            diff[c] += (S._margin(a, float(r.qfin), s) > 0) != (S._margin(a, None, s) > 0)
    return tot, moot, diff


def show(label, rows, feat):
    tot, moot, diff = count(rows, feat)
    per = ", ".join(f"{c} {moot[c]}/{tot[c]}" for c in ORDER)
    print(f"{label:58s} moot {sum(moot.values())} of {sum(tot.values())} ({per}); "
          f"full != agreement_only {sum(diff.values())} of {sum(tot.values())}")


# 1) as computed for the README: read 1 only (pool_all.py, cap 3,000; it parses the v2 / v3 instrument 'oss_low')
argv0 = sys.argv
sys.argv = ["pool_all.py", "3000", "runs/v2_main_960630.log", "runs/v3_main_960796.log", "runs/v4_main_960863.log"]
ns = {"__name__": "pool_all"}
exec(open("pool_all.py").read().split("nread=pd.Series")[0], ns)
L = ns["L"]
show("gpt-oss low read 1 (v2 + v3), cap 3,000 [README]", L[L.pair.notna()], "pair")

# 2) the feature decision.json is fitted on, and read 2 alone (consolidated.py, as refit_low16.py runs it)
ns = {"__name__": "consolidated"}
with contextlib.redirect_stdout(io.StringIO()):     # consolidated.py's own diagnostics are not needed here
    exec(open("consolidated.py").read().split("print(f'\\n{\"rule")[0], ns)
D = ns["D"]
show("pair_nat = mean of read 1 and read 2 (fitted feature)", D, "pair16")
show("gpt-oss low read 2 (v4) alone", D, "pair_v4")
sys.argv = argv0
