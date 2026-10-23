"""Permutation null for the 'same label' claim of the four-page report (draft 36), exactly as pre-registered in
PREREG_samelabel.txt (md5 recorded in PREREG_samelabel.txt.md5 before this script was first run).

Loader: the row table (ALLROWS) is built with the code of work/miners19/draft32/recompute_matched_v32.py, section 0,
copied verbatim below (that script is not imported or run: it would rewrite its .out). Read-only: writes only
perm_samelabel.out next to this file.

usage: PYTHONDONTWRITEBYTECODE=1 ~/.venvs/aimo-hf/bin/python perm_samelabel.py   (CPU, seconds)
"""
import collections
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
AIMO = os.environ.get("AIMO_DIR", ".")  # folder holding hf/ and work/
WORK = os.path.join(AIMO, "work")
sys.path.insert(0, os.path.join(WORK, "miners17", "laneG"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import g_common as G  # noqa: E402  (read-only: FULLCFG)

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- the pre-registration must be unchanged
PRE = os.path.join(HERE, "PREREG_samelabel.txt")
rec = open(os.path.join(HERE, "PREREG_samelabel.txt.md5")).read().split()
assert md5(PRE) == rec[0], "PREREG_samelabel.txt changed after its md5 was recorded"
P("# perm_samelabel.py: permutation null for the 'same label' claim (computed, post hoc claim, pre-registered test; nothing OFFICIAL)")
P(f"   PREREG_samelabel.txt md5 {md5(PRE)} (recorded: {' '.join(rec[2:])})")

# ---------------------------------------------------------------- loader: recompute_matched_v32.py section 0, verbatim
sha = lambda t: hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]  # noqa: E731
F_OLD = os.path.join(AIMO, "hf", "train-main-v2.parquet")
F_NEW = os.path.join(WORK, "miners19", "scan", "raw", "hf_train_main_v2_fa8af758", "train-00000-of-00001.parquet")
F_CAL = os.path.join(WORK, "sub_v135m", "calib.json")
for nm, p in (("hf/train-main-v2.parquet", F_OLD), ("fa8af758 parquet", F_NEW), ("calib.json (v135m)", F_CAL),
              ("calib.json (v101m)", os.path.join(WORK, "sub_v101m", "calib.json")),
              ("g_common.py", os.path.join(WORK, "miners17", "laneG", "g_common.py")),
              ("recompute_matched_v32.py (loader source)", os.path.join(WORK, "miners19", "draft32", "recompute_matched_v32.py"))):
    P(f"   md5 {nm:42s} {md5(p)}")
old = pd.read_parquet(F_OLD)
new = pd.read_parquet(F_NEW)
cal = json.load(open(F_CAL))["rows"]
cal101 = json.load(open(os.path.join(WORK, "sub_v101m", "calib.json")))["rows"]
assert [r["text"] for r in cal] == [r["text"] for r in cal101]
texts = list(dict.fromkeys(r["text"] for r in cal))
assert len(old) == 82 and len(new) == 94 and len(cal) == 82 and len(texts) == 28
assert all(old.problem[i] == new.problem[i] and old.model_id[i] == new.model_id[i] for i in range(82))
stem = lambda t: re.sub(r"\s+", " ", re.sub(r"\d+", "#", t))[:60]  # noqa: E731  (build_calib.py)
st2T = {}
for r in cal:
    st2T.setdefault(r["stem"], texts.index(r["text"]) + 1)
SH = G.FULLCFG


def lab(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else int(not bool(v))


ALLROWS = []          # all 94 rows: parquet index, template, configuration, label, max_drop, text key, read-text key
for i in range(94):
    q = new.iloc[i]
    T = texts.index(cal[i]["text"]) + 1 if i < 82 else st2T[stem(q.problem)]
    src = old.problem[i] if i < 82 else q.problem
    ALLROWS.append(dict(i=i, T=T, cfg=SH[f"{q.model_id}:{q.reasoning_effort}"], y=lab(q.is_robust), drop=float(q.max_drop),
                        key=sha(src), readkey=sha(texts[T - 1]), new=i >= 82))
for r in ALLROWS:
    r["match"] = r["key"] == r["readkey"]
own = [r["own_text"] in (True, "True") for r in cal]
assert [r["match"] for r in ALLROWS[:82]] == own
LAB71 = [r for r in ALLROWS if not r["new"] and r["y"] is not None]
LAB80 = LAB71 + [r for r in ALLROWS if r["new"] and r["y"] is not None]
assert len(LAB71) == 71 and len(LAB80) == 80
# ---------------------------------------------------------------- end of the verbatim loader

CFG_ORDER = ["Qwen", "Skywork", "Olmo", "DeepSeek", "high", "low", "medium"]
SEED, NPERM = 20261022, 10000


def groups(rows):
    """Indices of the rows of each multi-configuration problem (same exact text, >= 2 configurations)."""
    grp = collections.defaultdict(list)
    for j, r in enumerate(rows):
        grp[r["key"]].append(j)
    return [v for v in grp.values() if len({rows[j]["cfg"] for j in v}) >= 2]


def stats(y, multi):
    one = sum(1 for g in multi if len({int(y[j]) for j in g}) == 1)
    withnr = [g for g in multi if any(y[j] == 1 for j in g)]
    allnr = sum(1 for g in withnr if all(y[j] == 1 for j in g))
    return one, len(withnr), allnr, (allnr / len(withnr) if withnr else None)


def run(name, rows, guard):
    y = np.array([r["y"] for r in rows], dtype=int)
    multi = groups(rows)
    one, nwith, allnr, s2 = stats(y, multi)
    P(f"\n## {name}: {len(rows)} labelled rows, {int((y == 0).sum())} robust ({(y == 0).mean():.3f}); {len(multi)} multi-configuration problems")
    P(f"   observed: S1 one label {one} of {len(multi)}; with an NR label {nwith}, all NR {allnr} -> S2 {s2 if s2 is None else round(s2, 3)}")
    if guard is not None:
        assert (len(multi), one, nwith, allnr) == guard, f"guard failed: {(len(multi), one, nwith, allnr)} != {guard}"
        P(f"   guard: reproduces recompute_matched_v32.out section 5 {guard} (multi, one label, with NR, all NR)")
    P("   per configuration (rows, NR) in the case set: " + ", ".join(
        f"{c} {sum(1 for r in rows if r['cfg'] == c)}/{sum(1 for r in rows if r['cfg'] == c and r['y'] == 1)}" for c in CFG_ORDER))
    P("   multi-configuration problems (template: configuration label): " + "; ".join(
        f"T{rows[g[0]]['T']:02d} " + " ".join(f"{rows[j]['cfg']} {'NR' if y[j] else 'R'}" for j in g) for g in sorted(multi, key=lambda g: rows[g[0]]["T"])))
    idx = {c: np.array([j for j, r in enumerate(rows) if r["cfg"] == c]) for c in CFG_ORDER}
    rng = np.random.default_rng(SEED)
    S1, S2 = np.empty(NPERM, int), np.full(NPERM, np.nan)
    yp = y.copy()
    for k in range(NPERM):
        for c in CFG_ORDER:
            if len(idx[c]):
                yp[idx[c]] = y[idx[c]][rng.permutation(len(idx[c]))]
        o, _, _, s = stats(yp, multi)
        S1[k] = o
        if s is not None:
            S2[k] = s
    n1 = int((S1 >= one).sum())
    defined = ~np.isnan(S2)
    n2 = int((defined & (S2 >= s2 - 1e-12)).sum()) if s2 is not None else 0
    P(f"   null S1: mean {S1.mean():.2f} of {len(multi)}; 5th / 95th percentile {np.percentile(S1, 5):.0f} / {np.percentile(S1, 95):.0f}; "
      f"distribution " + ", ".join(f"{v}: {int((S1 == v).sum())}" for v in range(S1.min(), S1.max() + 1)))
    P(f"   p1 = P(S1 >= {one}) = {n1} / {NPERM} = {n1 / NPERM:.4f}; (1 + {n1}) / {NPERM + 1} = {(1 + n1) / (NPERM + 1):.4f}")
    P(f"   null S2: defined in {int(defined.sum())} of {NPERM} (undefined: {NPERM - int(defined.sum())}); mean where defined "
      f"{np.nanmean(S2):.3f}; 5th / 95th percentile {np.nanpercentile(S2, 5):.3f} / {np.nanpercentile(S2, 95):.3f}")
    P(f"   p2 = P(S2 >= {s2:.3f}) = {n2} / {NPERM} = {n2 / NPERM:.4f} (undefined counted as not reaching); conditional on defined "
      f"{n2} / {int(defined.sum())} = {n2 / max(1, int(defined.sum())):.4f}")
    return dict(one=one, multi=len(multi), p1=n1 / NPERM, mean1=S1.mean(), p2=n2 / NPERM, s2=s2, nwith=nwith, allnr=allnr)


R80 = run("80 labelled cases by exact text (PRIMARY: the paper's 15 of 16)", LAB80, (16, 15, 5, 4))
R71 = run("71 labelled cases of the 82-row file (SECONDARY: 14 of 15)", LAB71, (15, 14, 4, 3))
R63 = run("63 instance-matched cases of the 71 (information only, no decision)", [r for r in LAB71 if r["match"]], None)

P("\n## verdict under the pre-registered rule (p <= 0.05 stands; 0.05 < p <= 0.20 weakened; p > 0.20 not shown)")
for nm, R in (("80, S1 (primary)", R80), ("71, S1", R71), ("80, S2", R80), ("71, S2", R71)):
    p = R["p1"] if "S1" in nm else R["p2"]
    v = "STANDS" if p <= 0.05 else ("WEAKENED" if p <= 0.20 else "NOT SHOWN")
    P(f"   {nm:18s} p = {p:.4f} -> {v}")

# ================================================================ POST HOC (added after the pre-registered result above was seen)
# Not pre-registered; information only. The pre-registered null keeps each configuration's robust share but ignores
# difficulty (PREREG 'KNOWN LIMITS'): easy problems are robust for every model. This variant shuffles labels only within
# each (configuration, hard / easy template) cell (hard = g_common.HARD, the paper's Table 1 split), so a small p here
# means labels cluster by problem beyond the hard / easy split. The lines above are unchanged by this addition
# (perm_samelabel_run1_prereg_only.out is the first run's output; check with diff).
P("\n## POST HOC (not pre-registered; added after the result above): the same nulls, shuffling within configuration x hard / easy template")


def run_strat(name, rows):
    y = np.array([r["y"] for r in rows], dtype=int)
    multi = groups(rows)
    one, nwith, allnr, s2 = stats(y, multi)
    cells = collections.defaultdict(list)
    for j, r in enumerate(rows):
        cells[(r["cfg"], r["T"] in G.HARD)].append(j)
    keys = sorted(cells, key=lambda k: (CFG_ORDER.index(k[0]), k[1]))
    idx = {k: np.array(cells[k]) for k in keys}
    hard_multi = [g for g in multi if rows[g[0]]["T"] in G.HARD]
    rng = np.random.default_rng(SEED)
    S1, S2 = np.empty(NPERM, int), np.full(NPERM, np.nan)
    H1 = np.empty(NPERM, int)
    yp = y.copy()
    for k in range(NPERM):
        for c in keys:
            yp[idx[c]] = y[idx[c]][rng.permutation(len(idx[c]))]
        o, _, _, s = stats(yp, multi)
        S1[k] = o
        H1[k] = stats(yp, hard_multi)[0]
        if s is not None:
            S2[k] = s
    h_one = stats(y, hard_multi)[0]
    n1 = int((S1 >= one).sum())
    nh = int((H1 >= h_one).sum())
    defined = ~np.isnan(S2)
    n2 = int((defined & (S2 >= s2 - 1e-12)).sum())
    P(f"   {name}: S1 {one} of {len(multi)}: null mean {S1.mean():.2f}, 95th percentile {np.percentile(S1, 95):.0f}, p1 = {n1} / {NPERM} = {n1 / NPERM:.4f}")
    P(f"      hard-template problems only: one label {h_one} of {len(hard_multi)}: null mean {H1.mean():.2f}, p = {nh} / {NPERM} = {nh / NPERM:.4f}")
    P(f"      S2 {allnr} of {nwith} all NR: null defined in {int(defined.sum())}, mean {np.nanmean(S2):.3f}, p2 = {n2} / {NPERM} = {n2 / NPERM:.4f}")


run_strat("80 labelled cases", LAB80)
run_strat("71 labelled cases", LAB71)
run_strat("63 matched cases", [r for r in LAB71 if r["match"]])
open(os.path.join(HERE, "perm_samelabel.out"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
