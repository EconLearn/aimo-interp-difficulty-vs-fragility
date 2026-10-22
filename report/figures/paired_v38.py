"""Draft 38 of the four-page report: paired tests against always answering robust, and the checks a fifth cold reader
asked for (computed, post hoc; nothing here was pre-registered; nothing OFFICIAL except the board totals, which are board
scores). Read-only: writes only paired_v38.out next to this file.

  1. the public cases: the entry's leave-one-template-out calls (v95 rules on the K 32 dress read; lane G run_policy,
     decision.json refitted per fold, exactly as work/miners19/draft32/recompute_matched_v32.py section 2) against always
     robust on the SAME cases: discordant counts and an exact two-sided McNemar test (binomial on the discordant cases),
     on the 63 matched cases and on the 22 newer (AIME-2026) cases among them; exact Clopper-Pearson intervals for 55 of 63
     and 17 of 22;
  2. the boards: only totals are known (hidden labels are never read), so no paired test is possible. A gain of d cases
     over always robust needs at least d non-robust calls, all right; the smallest two-sided sign-test p any board could
     give is then 2 x 0.5^d. Printed for every board total the report names;
  3. the 0.897 - 0.872 comparison (agreement against key-scored accuracy over the 80 attempts pooled from six reads, hard
     matched cases): pair counts (right, tied, misordered) and the pairs on which the two orderings differ; the read
     names and attempts per read; the template bootstrap of intervals_v37.py re-run with the same seed and scheme, now
     splitting the 'difference <= 0' share into exactly 0 (ties) and below 0;
  4. template counts: hard and easy templates with labelled cases, with matched cases, and the hard templates whose
     labelled cases are all on other numbers.

Machinery copied read-only: the row loader of ../draft36/perm_samelabel.py (via ../draft37/intervals_v37.py, verbatim),
section 1 of recompute_matched_v32.py (pair_nat, pooled, keyacc) and its section 2 call of G.run_policy; the bootstrap
of ../draft37/intervals_v37.py (auc_idx, boot). No script is imported or run except the read-only modules g_common and
xbench, which recompute_matched_v32.py and intervals_v37.py import the same way.

usage: PYTHONDONTWRITEBYTECODE=1 ~/.venvs/aimo-hf/bin/python paired_v38.py   (CPU, about a minute)
"""
import collections
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
AIMO = "{AIMO}"
WORK = os.path.join(AIMO, "work")
sys.path.insert(0, os.path.join(WORK, "miners17", "laneG"))
sys.path.insert(0, os.path.join(WORK, "miners17", "laneX"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import beta, binom  # noqa: E402

import g_common as G  # noqa: E402
import xbench  # noqa: E402

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


P("# paired_v38.py: paired tests against always robust, the 0.897 - 0.872 pair counts and bootstrap ties, template counts "
  "(computed, post hoc, not pre-registered; board totals are board scores, OFFICIAL)")

# ---------------------------------------------------------------- loader: perm_samelabel.py (= intervals_v37.py), verbatim
sha = lambda t: hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]  # noqa: E731
F_OLD = os.path.join(AIMO, "hf", "train-main-v2.parquet")
F_NEW = os.path.join(WORK, "miners19", "scan", "raw", "hf_train_main_v2_fa8af758", "train-00000-of-00001.parquet")
F_CAL = os.path.join(WORK, "sub_v135m", "calib.json")
for nm, p in (("hf/train-main-v2.parquet", F_OLD), ("fa8af758 parquet", F_NEW), ("calib.json (v135m)", F_CAL),
              ("calib.json (v101m)", os.path.join(WORK, "sub_v101m", "calib.json")),
              ("g_common.py", os.path.join(WORK, "miners17", "laneG", "g_common.py")),
              ("xbench.py", os.path.join(WORK, "miners17", "laneX", "xbench.py")),
              ("x_pool.json", os.path.join(WORK, "miners17", "laneX", "x_pool.json")),
              ("dress log", os.path.join(WORK, "runs", "v88_dress_987666.log")),
              ("intervals_v37.py (bootstrap source)", os.path.join(WORK, "miners19", "draft37", "intervals_v37.py")),
              ("recompute_matched_v32.py (LOTO source)", os.path.join(WORK, "miners19", "draft32", "recompute_matched_v32.py"))):
    P(f"   md5 {nm:40s} {md5(p)}")
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


def cp(k, n):
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    return lo, hi


def mcnemar_exact(b, c):
    """Two-sided exact McNemar test = two-sided binomial (sign) test of b against b + c at 1/2 (doubled smaller tail, at most 1)."""
    n = b + c
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * binom.cdf(min(b, c), n, 0.5)))


# ================================================================ 1. public cases: the entry against always robust, paired
P("\n## 1. public cases: the entry (LOTO calls, v95 rules, dress read K 32) against always robust on the same cases")
D, FIT = G.build_fit_data()
assert [(int(T), c, int(yy)) for T, c, yy in zip(D["T"], D.cfg, D.y)] == [(r["T"], r["cfg"], r["y"]) for r in LAB71]
pool, _ = G.parse_dress()
y71 = np.array([r["y"] for r in LAB71])
M71 = np.array([r["match"] for r in LAB71])
Tr, cfg = D["T"].values, D.cfg.values
fresh = np.isin(Tr, sorted(G.FRESH))
yh = G.run_policy(D, FIT, pool, G.V95, "loto")                     # recompute_matched_v32.py section 2, the same call
ok = yh == y71
assert int(ok[M71].sum()) == 55 and int(M71.sum()) == 63, "guard: LOTO right on matched cases is not 55 of 63"
assert int(ok[M71 & fresh].sum()) == 17 and int((M71 & fresh).sum()) == 22, "guard: newer matched cases not 17 of 22"
err = ", ".join(f"T{Tr[i]:02d} {cfg[i]} {'NR' if y71[i] else 'R'}" for i in np.where(~ok & M71)[0])
assert err == "T05 Qwen R, T16 Skywork R, T13 Skywork NR, T08 Olmo R, T25 high NR, T26 high NR, T09 low R, T10 low NR", err
P(f"   guard: LOTO right 55/63 matched, 17/22 newer matched, errors = recompute_matched_v32.out section 2 ({err}): ok")
for lbl, m in (("the 63 matched cases", M71), ("the 22 newer (AIME-2026) cases among them", M71 & fresh)):
    yy, hh = y71[m], yh[m]
    n, nr = len(yy), int(yy.sum())
    entry, ar = int((yy == hh).sum()), int((yy == 0).sum())
    b = int(((hh == 1) & (yy == 1)).sum())          # entry right, always robust wrong (non-robust call on a non-robust case)
    c = int(((hh == 1) & (yy == 0)).sum())          # entry wrong, always robust right (non-robust call on a robust case)
    both_wrong = int(((hh == 0) & (yy == 1)).sum())
    assert entry - ar == b - c
    p = mcnemar_exact(b, c)
    lo, hi = cp(entry, n)
    P(f"   {lbl}: the entry {entry} of {n}, always robust {ar} of {n} (non-robust cases {nr}); non-robust calls {b + c}: "
      f"right {b}, wrong {c}; robust calls on non-robust cases {both_wrong} (both wrong); discordant {b} against {c}; "
      f"exact two-sided McNemar p = {p:.4f} ({p:.2f}); Clopper-Pearson 95% interval of the entry {lo:.3f} to {hi:.3f} "
      f"({lo:.2f} to {hi:.2f}); always robust {ar / n:.3f}")

# ================================================================ 2. boards: the best case any total allows
P("\n## 2. boards (totals only; hidden labels are never read): the smallest two-sided sign-test p a total allows")
P("   a total k against always robust's r needs at least d = k - r non-robust calls; at best all d are right and no other "
  "non-robust call is made, so p >= 2 x 0.5^d (exact two-sided sign test on the discordant cases, capped at 1)")
for lbl, k, n, r in (("main board, the entry (15 of 21)", 15, 21, 10), ("small board, the entry (9 of 14)", 9, 14, 7),
                     ("main board, earlier build (16 of 21)", 16, 21, 10), ("main board, earlier build (17 of 21)", 17, 21, 10),
                     ("small board, earlier build (10 of 14)", 10, 14, 7)):
    d = k - r
    pmin = mcnemar_exact(d, 0)
    nmax_sig = [m for m in range(d, n + 1, 2) if mcnemar_exact((m + d) // 2, (m - d) // 2) <= 0.05]
    P(f"   {lbl}: always robust {r}; gain +{d}; smallest p {pmin:.4f} ({pmin:.3f})"
      + (f"; p <= 0.05 only if the entry made at most {max(nmax_sig)} non-robust calls" if nmax_sig else "; never <= 0.05"))

# ================================================================ 3. 0.897 against 0.872: pair counts, reads, bootstrap ties
P("\n## 3. agreement (0.897) against key-scored accuracy (0.872), 80 attempts pooled, the 32 hard matched cases")
TS = range(1, 29)
LOW = xbench.LOW


def pair_nat(att):
    K = len(att)
    cc = collections.Counter(a[2] for a in att if a[1] and a[2] is not None)
    return sum(v * (v - 1) for v in cc.values()) / (K * (K - 1))


pooled = {T: pair_nat(LOW[T]) for T in TS}
keyacc = {T: float(np.mean([a[3] for a in LOW[T]])) for T in TS}
assert all(len(LOW[T]) == 80 for T in TS)
per_read = collections.Counter(a[4] for a in LOW[1])
assert all(collections.Counter(a[4] for a in LOW[T]) == per_read for T in TS)
P(f"   reads pooled: {len(per_read)}; attempts per read: " + ", ".join(f"{k} {v}" for k, v in sorted(per_read.items()))
  + f"; total {sum(per_read.values())}")
dress = os.path.basename(os.path.join(WORK, "runs", "v88_dress_987666.log"))
P(f"   the K 32 headline read (dress log {dress}, Codabench 987666) among them: "
  f"{any('987666' in str(k) or 'dress' in str(k) for k in per_read)}")
HARD = G.HARD
M63 = [r for r in LAB71 if r["match"]]
H32 = [r for r in M63 if r["T"] in HARD]
assert len(M63) == 63 and len(H32) == 32


def pairs_of(f, rows):
    out = {}
    for c in sorted(set(r["cfg"] for r in rows)):
        for a in [r for r in rows if r["cfg"] == c and r["y"] == 1]:
            for b in [r for r in rows if r["cfg"] == c and r["y"] == 0]:
                sa, sb = 1 - f[a["T"]], 1 - f[b["T"]]          # higher score = more non-robust
                out[(c, a["T"], b["T"])] = "right" if sa > sb else ("tied" if sa == sb else "misordered")
    return out


pa, pk = pairs_of(pooled, H32), pairs_of(keyacc, H32)
assert set(pa) == set(pk)
for nm, pp in (("agreement, 80 pooled attempts", pa), ("key-scored accuracy, same attempts", pk)):
    cnt = collections.Counter(pp.values())
    auc = (cnt["right"] + 0.5 * cnt["tied"]) / len(pp)
    P(f"   {nm}: pairs {len(pp)}; right {cnt['right']}, tied {cnt['tied']}, misordered {cnt['misordered']}; AUC {auc:.3f}")
diffp = [(k, pa[k], pk[k]) for k in sorted(pa) if pa[k] != pk[k]]
P(f"   pairs ordered differently by the two: {len(diffp)}: " + "; ".join(
    f"{c} T{a:02d} NR / T{b:02d} R: agreement {x}, key {y}" for (c, a, b), x, y in diffp))
dright = sum((x == 'right') - (y == 'right') + 0.5 * ((x == 'tied') - (y == 'tied')) for _, x, y in diffp)
P(f"   net difference: {dright:+.1f} of {len(pa)} pairs = {dright / len(pa):+.4f} (the printed +0.025)")

# the bootstrap of intervals_v37.py, re-run: same seed, same scheme, same order of keys
SEED, NBOOT = 20261022, 10000


def arrays(rows, f):
    return (np.array([1 - f[r["T"]] for r in rows]), np.array([r["y"] for r in rows]), np.array([r["cfg"] for r in rows]),
            np.array([r["T"] for r in rows]))


def auc_idx(score, y, cfg_, idx):
    num = den = 0.0
    s, yy, cc = score[idx], y[idx], cfg_[idx]
    for c in np.unique(cc):
        a = s[(cc == c) & (yy == 1)]
        b = s[(cc == c) & (yy == 0)]
        if len(a) and len(b):
            d = a[:, None] - b[None, :]
            num += (d > 0).sum() + 0.5 * (d == 0).sum()
            den += d.size
    return (num / den if den else np.nan), int(den)


agree = {T: pool[T]["prim"] for T in TS}
RES = {"0.821": arrays(H32, agree), "0.897": arrays(H32, pooled), "0.872": arrays(H32, keyacc)}
for k in RES:
    assert f"{auc_idx(*RES[k][:3], np.arange(32))[0]:.3f}" == k


def boot(keys, rows_T):
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


b_h, d_h = boot(["0.821", "0.897", "0.872"], RES["0.821"][3])
diff = b_h["0.897"] - b_h["0.872"]
lo, hi = np.percentile(diff, 2.5), np.percentile(diff, 97.5)
le0 = float((diff <= 0).mean())
assert (f"{lo:+.3f}", f"{hi:+.3f}", f"{le0:.3f}") == ("+0.000", "+0.176", "0.593"), (lo, hi, le0)
eq0 = float((np.abs(diff) < 1e-12).mean())
lt0 = float((diff < -1e-12).mean())
gt0 = float((diff > 1e-12).mean())
P(f"   bootstrap re-run (intervals_v37.py scheme, default_rng({SEED}), {NBOOT} resamples, {d_h} dropped): interval {lo:+.3f} to "
  f"{hi:+.3f} and share <= 0 {le0:.3f} reproduced (guard: ok)")
P(f"   of the kept resamples: difference exactly 0 (a tie) {eq0:.3f}; below 0 {lt0:.3f}; above 0 {gt0:.3f}")
tdiff = sorted({a for (c, a, b), x, y in diffp} | {b for (c, a, b), x, y in diffp})
P(f"   templates of the differing pairs: {', '.join(f'T{t:02d}' for t in tdiff)} (a resample without them gives a difference of exactly 0)")

# ================================================================ 4. template counts
P("\n## 4. template counts (hard = G.HARD, ledger 267b / 278)")
lab_T = sorted({r["T"] for r in LAB71})
mat_T = sorted({r["T"] for r in M63})
hard_lab = [T for T in lab_T if T in HARD]
hard_mat = [T for T in mat_T if T in HARD]
easy_lab = [T for T in lab_T if T not in HARD]
easy_mat = [T for T in mat_T if T not in HARD]
P(f"   G.HARD: {len(HARD)} templates; labelled templates (71 cases): {len(lab_T)}; with a matched case (63): {len(mat_T)}")
P(f"   hard templates with a labelled case: {len(hard_lab)}; with a matched case: {len(hard_mat)}; hard templates whose labelled "
  f"cases are all on other numbers: {', '.join(f'T{T:02d}' for T in hard_lab if T not in hard_mat)}")
P(f"   easy templates with a labelled case: {len(easy_lab)}; with a matched case: {len(easy_mat)}")
nh = sum(1 for r in M63 if r["T"] in HARD)
P(f"   matched cases: hard {nh} ({sum(r['y'] for r in M63 if r['T'] in HARD)} non-robust) on {len(hard_mat)} templates; easy "
  f"{63 - nh} ({sum(1 - r['y'] for r in M63 if r['T'] not in HARD)} robust) on {len(easy_mat)} templates")
open(os.path.join(HERE, "paired_v38.out"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
