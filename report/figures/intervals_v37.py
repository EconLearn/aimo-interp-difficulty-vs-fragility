"""Draft 37 of the four-page report: the intervals pre-registered in PREREG_samelabel_difficulty.txt, part (c).

  1. template-bootstrap 95% intervals (cluster = template, 10,000 resamples, numpy default_rng(20261022)) for the
     headline within-configuration AUCs on the 63 matched cases: 0.914 (deployed agreement, K 32, all), 0.821 (the same,
     hard), 0.897 (agreement over the 80 pooled attempts, hard), 0.872 (key-scored accuracy over the same attempts, hard),
     and the paired difference 0.897 - 0.872;
  2. exact Clopper-Pearson 95% intervals for 15 of 21 (main board), 9 of 14 (small board) and 55 of 63 (public, LOTO).

Machinery copied read-only from work/miners19/draft32/recompute_matched_v32.py (pair_nat, pooled, keyacc, the
within-configuration AUC of xbench.auc_within, lane G's template bootstrap scheme); the row loader is
../draft36/perm_samelabel.py's, copied verbatim. Neither script is imported or run. g_common and xbench are imported
read-only (parse_dress, LOW), as recompute_matched_v32.py does. Writes only intervals_v37.out next to this file.

usage: PYTHONDONTWRITEBYTECODE=1 ~/.venvs/aimo-hf/bin/python intervals_v37.py   (CPU, about a minute)
"""
import collections
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
AIMO = "<AIMO_DIR>"
WORK = os.path.join(AIMO, "work")
sys.path.insert(0, os.path.join(WORK, "miners17", "laneG"))
sys.path.insert(0, os.path.join(WORK, "miners17", "laneX"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import beta  # noqa: E402

import g_common as G  # noqa: E402
import xbench  # noqa: E402

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


PRE = os.path.join(HERE, "PREREG_samelabel_difficulty.txt")
rec = open(os.path.join(HERE, "PREREG_samelabel_difficulty.txt.md5")).read().split()
assert md5(PRE) == rec[0], "PREREG_samelabel_difficulty.txt changed after its md5 was recorded"
P("# intervals_v37.py: template-bootstrap AUC intervals and exact binomial intervals (computed; nothing OFFICIAL except the "
  "board counts, which are board scores)")
P(f"   PREREG_samelabel_difficulty.txt md5 {md5(PRE)} (part c; recorded: {' '.join(rec[2:])})")

# ---------------------------------------------------------------- loader: perm_samelabel.py (= recompute_matched_v32.py section 0), verbatim
sha = lambda t: hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]  # noqa: E731
F_OLD = os.path.join(AIMO, "hf", "train-main-v2.parquet")
F_NEW = os.path.join(WORK, "miners19", "scan", "raw", "hf_train_main_v2_fa8af758", "train-00000-of-00001.parquet")
F_CAL = os.path.join(WORK, "sub_v135m", "calib.json")
for nm, p in (("hf/train-main-v2.parquet", F_OLD), ("fa8af758 parquet", F_NEW), ("calib.json (v135m)", F_CAL),
              ("calib.json (v101m)", os.path.join(WORK, "sub_v101m", "calib.json")),
              ("g_common.py", os.path.join(WORK, "miners17", "laneG", "g_common.py")),
              ("xbench.py", os.path.join(WORK, "miners17", "laneX", "xbench.py")),
              ("x_pool.json", os.path.join(WORK, "miners17", "laneX", "x_pool.json")),
              ("dress log", os.path.join(WORK, "runs", "v88_dress_987666.log"))):
    P(f"   md5 {nm:26s} {md5(p)}")
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
assert [(r["T"], r["cfg"], r["y"]) for r in xbench.ROWS] == [(r["T"], r["cfg"], r["y"]) for r in LAB71]

# ---------------------------------------------------------------- recompute_matched_v32.py section 1 (copied)
pool, _ = G.parse_dress()
TS = range(1, 29)
agree = {T: pool[T]["prim"] for T in TS}
LOW = xbench.LOW


def pair_nat(att):
    K = len(att)
    c = collections.Counter(a[2] for a in att if a[1] and a[2] is not None)
    return sum(v * (v - 1) for v in c.values()) / (K * (K - 1))


pooled = {T: pair_nat(LOW[T]) for T in TS}
keyacc = {T: float(np.mean([a[3] for a in LOW[T]])) for T in TS}
assert all(len(LOW[T]) == 80 for T in TS)
HARD = G.HARD
M63 = [r for r in LAB71 if r["match"]]
H32 = [r for r in M63 if r["T"] in HARD]
assert len(M63) == 63 and len(H32) == 32

SEED, NBOOT = 20261022, 10000


def arrays(rows, f):
    return (np.array([1 - f[r["T"]] for r in rows]), np.array([r["y"] for r in rows]), np.array([r["cfg"] for r in rows]),
            np.array([r["T"] for r in rows]))


def auc_idx(score, y, cfg, idx):
    """Within-configuration AUC (xbench.auc_within's definition: ties count half) over the row indices idx."""
    num = den = 0.0
    s, yy, cc = score[idx], y[idx], cfg[idx]
    for c in np.unique(cc):
        a = s[(cc == c) & (yy == 1)]
        b = s[(cc == c) & (yy == 0)]
        if len(a) and len(b):
            d = a[:, None] - b[None, :]
            num += (d > 0).sum() + 0.5 * (d == 0).sum()
            den += d.size
    return (num / den if den else np.nan), int(den)


P("\n## 1. headline within-configuration AUCs on the 63 matched cases, template bootstrap (cluster = template; "
  f"{NBOOT} resamples; default_rng({SEED}); 95% percentile interval)")
want = {"0.914": ("deployed agreement, dress read K 32, all cases", M63, agree, 105),
        "0.821": ("deployed agreement, dress read K 32, hard cases", H32, agree, 39),
        "0.897": ("agreement over the 80 pooled attempts, hard cases", H32, pooled, 39),
        "0.872": ("key-scored accuracy over the 80 pooled attempts, hard cases", H32, keyacc, 39)}
RES = {}
for printed, (label, rows, f, npairs) in want.items():
    s, y, c, T = arrays(rows, f)
    a, den = auc_idx(s, y, c, np.arange(len(rows)))
    assert f"{a:.3f}" == printed and den == npairs, f"guard failed: {label} {a:.3f} ({den}) != {printed} ({npairs})"
    RES[printed] = (s, y, c, T)
    P(f"   guard: {label}: {a:.3f} on {len(rows)} cases ({int(y.sum())} non-robust, {den} pairs, {len(np.unique(T))} templates) = printed {printed}: ok")


def boot(keys, rows_T):
    """One shared resample stream: each resample draws templates once and evaluates every listed AUC on it."""
    rng = np.random.default_rng(SEED)
    U = np.unique(rows_T)
    by = {u: np.where(rows_T == u)[0] for u in U}
    vals = {k: [] for k in keys}
    dropped = 0
    for _ in range(NBOOT):
        ix = np.concatenate([by[u] for u in rng.choice(U, len(U), replace=True)])
        got = {k: auc_idx(*RES[k][:3], ix)[0] for k in keys}
        if any(np.isnan(v) for v in got.values()):
            dropped += 1
            continue
        for k in keys:
            vals[k].append(got[k])
    return {k: np.array(v) for k, v in vals.items()}, dropped


ci = lambda v: (np.percentile(v, 2.5), np.percentile(v, 97.5))  # noqa: E731
# all 63 cases: 0.914 alone
b_all, d_all = boot(["0.914"], RES["0.914"][3])
lo, hi = ci(b_all["0.914"])
P(f"   0.914 (all 63 cases): 95% interval {lo:.3f} to {hi:.3f}; dropped resamples {d_all}")
# hard cases: the three hard AUCs on the same resamples (paired), and the difference 0.897 - 0.872
assert (RES["0.821"][3] == RES["0.897"][3]).all() and (RES["0.897"][3] == RES["0.872"][3]).all()
b_h, d_h = boot(["0.821", "0.897", "0.872"], RES["0.821"][3])
for k in ("0.821", "0.897", "0.872"):
    lo, hi = ci(b_h[k])
    P(f"   {k} (32 hard cases): 95% interval {lo:.3f} to {hi:.3f}; dropped resamples {d_h}")
diff = b_h["0.897"] - b_h["0.872"]
lo, hi = ci(diff)
P(f"   difference 0.897 - 0.872 = {0.897 - 0.872:+.3f} (unrounded {auc_idx(*RES['0.897'][:3], np.arange(32))[0] - auc_idx(*RES['0.872'][:3], np.arange(32))[0]:+.4f}): "
  f"paired 95% interval {lo:+.3f} to {hi:+.3f}; share of resamples with the difference <= 0: {(diff <= 0).mean():.3f}")
P(f"   wording (pre-registered): {'only marginally, within noise' if lo <= 0 <= hi else 'agreement beats accuracy'}")

P("\n## 2. exact Clopper-Pearson 95% intervals (board counts are board scores, OFFICIAL; one run each)")


def cp(k, n):
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    return lo, hi


for label, k, n, kr in (("main board, the entry", 15, 21, 10), ("small board, the entry", 9, 14, 7),
                        ("public, LOTO, the entry", 55, 63, 49)):
    lo, hi = cp(k, n)
    inside = lo <= kr / n <= hi
    P(f"   {label}: {k} of {n} = {k / n:.3f}; 95% interval {lo:.3f} to {hi:.3f} ({lo:.2f} to {hi:.2f}); always robust {kr} of {n} = "
      f"{kr / n:.3f} {'INSIDE' if inside else 'outside'} the interval -> "
      f"{'not distinguishable from always robust on its own' if inside else 'above always robust'}")
for label, k, n in (("main board, always robust", 10, 21), ("small board, always robust", 7, 14), ("public, always robust", 49, 63)):
    lo, hi = cp(k, n)
    P(f"   {label}: {k} of {n} = {k / n:.3f}; 95% interval {lo:.3f} to {hi:.3f} (information)")
open(os.path.join(HERE, "intervals_v37.out"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
