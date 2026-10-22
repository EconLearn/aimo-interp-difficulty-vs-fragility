"""Draft 37 of the four-page report: the difficulty-preserving null for the 'same label' claim and the
leave-one-configuration-out label check, exactly as pre-registered in PREREG_samelabel_difficulty.txt (md5 recorded in
PREREG_samelabel_difficulty.txt.md5 before this script existed).

Loader: the row table (ALLROWS, LAB71, LAB80) is built with the loader of ../draft36/perm_samelabel.py (itself verbatim
from work/miners19/draft32/recompute_matched_v32.py section 0), copied verbatim below; neither script is imported or run.
Difficulty: the deployed agreement of the K 32 dress read, g_common.parse_dress() (lane G, imported read-only, as
recompute_matched_v32.py section 1 does). Key-scored accuracy (information only): xbench.LOW (lane X, read-only).
Read-only: writes only samelabel_difficulty.out next to this file.

usage: PYTHONDONTWRITEBYTECODE=1 ~/.venvs/aimo-hf/bin/python samelabel_difficulty.py   (CPU, about a minute)
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

import g_common as G  # noqa: E402  (read-only: FULLCFG, HARD, parse_dress)
import xbench  # noqa: E402  (read-only: LOW, the pooled attempts; information-only key-scored bins)

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- the pre-registration must be unchanged
PRE = os.path.join(HERE, "PREREG_samelabel_difficulty.txt")
rec = open(os.path.join(HERE, "PREREG_samelabel_difficulty.txt.md5")).read().split()
assert md5(PRE) == rec[0], "PREREG_samelabel_difficulty.txt changed after its md5 was recorded"
P("# samelabel_difficulty.py: difficulty-preserving null and leave-one-configuration-out check for the 'same label' claim")
P("# (computed; post hoc claim, pre-registered test; nothing OFFICIAL)")
P(f"   PREREG_samelabel_difficulty.txt md5 {md5(PRE)} (recorded: {' '.join(rec[2:])})")

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
              ("dress log", os.path.join(WORK, "runs", "v88_dress_987666.log")),
              ("perm_samelabel.py (loader source)", os.path.join(WORK, "miners19", "draft36", "perm_samelabel.py"))):
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
LAB63 = [r for r in LAB71 if r["match"]]

CFG_ORDER = ["Qwen", "Skywork", "Olmo", "DeepSeek", "high", "low", "medium"]
SEED, NPERM, NBOOT = 20261022, 10000, 10000
pool, _ = G.parse_dress()
A = {T: float(pool[T]["prim"]) for T in range(1, 29)}                    # deployed agreement, dress read K 32
KEYACC = {T: float(np.mean([a[3] for a in xbench.LOW[T]])) for T in range(1, 29)}   # info only: key-scored accuracy, 80 attempts


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


def bins_for(rows, score, nb):
    """Equal-count bins of a per-template score over the distinct problems (exact texts) of the case set."""
    prob = {}
    for r in rows:
        prob.setdefault(r["key"], r["T"])
    vals = np.array([score[T] for T in prob.values()])
    cuts = np.quantile(vals, [k / nb for k in range(1, nb)])
    pbin = {k: int((score[T] > cuts).sum()) for k, T in prob.items()}
    return cuts, pbin, collections.Counter(pbin.values())


def shuffle_null(rows, cell_of, seed=SEED):
    """Permute labels within cells; returns observed (S1, nwith, allnr, S2) and the null arrays S1, S2."""
    y = np.array([r["y"] for r in rows], dtype=int)
    multi = groups(rows)
    obs = stats(y, multi)
    cells = collections.defaultdict(list)
    for j, r in enumerate(rows):
        cells[cell_of(r)].append(j)
    keys = sorted(cells, key=lambda k: (CFG_ORDER.index(k[0]),) + tuple(k[1:]))
    idx = [np.array(cells[k]) for k in keys]
    rng = np.random.default_rng(seed)
    S1, S2 = np.empty(NPERM, int), np.full(NPERM, np.nan)
    yp = y.copy()
    for k in range(NPERM):
        for ix in idx:
            yp[ix] = y[ix][rng.permutation(len(ix))]
        o, _, _, s = stats(yp, multi)
        S1[k] = o
        if s is not None:
            S2[k] = s
    return obs, S1, S2, multi, cells, keys


def pvals(obs, S1, S2):
    one, _, _, s2 = obs
    n1 = int((S1 >= one).sum())
    defined = ~np.isnan(S2)
    n2 = int((defined & (S2 >= s2 - 1e-12)).sum()) if s2 is not None else 0
    return n1, n2, int(defined.sum())


def branch(p):
    return "STANDS" if p <= 0.05 else ("WEAKENED" if p <= 0.20 else "NOT SHOWN")


# ================================================================ guards
P("\n## guards (run before any new result)")
y80 = np.array([r["y"] for r in LAB80])
for name, rows, want in (("LAB80", LAB80, (16, 15, 5, 4)), ("LAB71", LAB71, (15, 14, 4, 3))):
    y_ = np.array([r["y"] for r in rows], dtype=int)
    m_ = groups(rows)
    o = stats(y_, m_)
    got = (len(m_), o[0], o[1], o[2])
    assert got == want, f"G1 failed on {name}: {got} != {want}"
    P(f"   G1 {name}: multi {got[0]}, one label {got[1]}, with an NR label {got[2]}, all NR {got[3]} = {want}: ok")
obs, S1, S2, _, _, _ = shuffle_null(LAB80, lambda r: (r["cfg"],))
n1, n2, nd = pvals(obs, S1, S2)
assert f"{S1.mean():.2f}" == "5.88" and n1 == 0, f"G2 failed: {S1.mean():.2f}, {n1}"
P(f"   G2 draft 36's within-configuration null re-run here on LAB80: null mean {S1.mean():.2f} of 16, {n1} of {NPERM} reach 15 "
  f"(perm_samelabel.out: 5.88, 0): ok")


def auc_within(score, rows):
    """Within-configuration AUC; score: higher = more non-robust; ties count half (xbench.auc_within's definition)."""
    num = den = 0.0
    for c in set(r["cfg"] for r in rows):
        nr = [score(r) for r in rows if r["cfg"] == c and r["y"] == 1]
        rr = [score(r) for r in rows if r["cfg"] == c and r["y"] == 0]
        for a in nr:
            for b in rr:
                num += 1.0 if a > b else 0.5 if a == b else 0.0
                den += 1
    return (num / den if den else float("nan")), int(den)


g3 = auc_within(lambda r: 1 - A[r["T"]], LAB63)
assert f"{g3[0]:.3f}" == "0.914" and g3[1] == 105, f"G3 failed: {g3}"
P(f"   G3 within-configuration AUC of the deployed agreement on the 63 matched cases: {g3[0]:.3f} ({g3[1]} pairs) = 0.914: ok")

# ================================================================ (a) PRIMARY: within configuration x agreement tertile
P("\n## (a) PRIMARY: labels shuffled within configuration x tertile of deployed agreement (dress read K 32)")
RES = {}
for name, rows, nobs in (("LAB80", LAB80, "15 of 16"), ("LAB71", LAB71, "14 of 15")):
    cuts, pbin, counts = bins_for(rows, A, 3)
    obs, S1, S2, multi, cells, keys = shuffle_null(rows, lambda r, pb=pbin: (r["cfg"], pb[r["key"]]))
    n1, n2, nd = pvals(obs, S1, S2)
    one, nwith, allnr, s2 = obs
    RES[name] = dict(p1=n1 / NPERM, p2=n2 / NPERM, mean1=S1.mean(), n1=n1, n2=n2, one=one, multi=len(multi), s2=s2,
                     mean2=np.nanmean(S2), lo=np.percentile(S1, 5), hi=np.percentile(S1, 95))
    P(f"\n### {name} ({len(rows)} labelled cases; {len(pbin)} distinct problems; {len(multi)} multi-configuration problems; observed {nobs})")
    P(f"   tertile cut points of agreement over the {len(pbin)} problems: {cuts[0]:.3f}, {cuts[1]:.3f}; problems per bin "
      f"(0 = lowest agreement = hardest): " + ", ".join(f"{b}: {counts[b]}" for b in range(3)))
    P("   multi-configuration problems (template, agreement, bin: labels): " + "; ".join(
        f"T{rows[g[0]]['T']:02d} {A[rows[g[0]]['T']]:.3f} b{pbin[rows[g[0]]['key']]}: "
        + " ".join(f"{rows[j]['cfg']} {'NR' if rows[j]['y'] else 'R'}" for j in g) for g in sorted(multi, key=lambda g: rows[g[0]]["T"])))
    P("   cells (configuration, bin): rows/NR: " + ", ".join(
        f"{k[0]} b{k[1]} {len(cells[k])}/{sum(rows[j]['y'] for j in cells[k])}" for k in keys))
    P(f"   observed: S1 {one} of {len(multi)}; with an NR label {nwith}, all NR {allnr} -> S2 {s2:.3f}")
    P(f"   null S1: mean {S1.mean():.2f} of {len(multi)}; 5th / 95th percentile {np.percentile(S1, 5):.0f} / {np.percentile(S1, 95):.0f}; "
      "distribution " + ", ".join(f"{v}: {int((S1 == v).sum())}" for v in range(S1.min(), S1.max() + 1)))
    P(f"   p1 = P(S1 >= {one}) = {n1} / {NPERM} = {n1 / NPERM:.4f}; (1 + {n1}) / {NPERM + 1} = {(1 + n1) / (NPERM + 1):.4f}")
    P(f"   null S2: defined in {nd} of {NPERM}; mean where defined {np.nanmean(S2):.3f}; p2 = P(S2 >= {s2:.3f}) = {n2} / {NPERM} = "
      f"{n2 / NPERM:.4f} (undefined counted as not reaching); conditional on defined {n2} / {nd} = {n2 / max(1, nd):.4f}")

P("\n## verdict under the pre-registered rule (branch = the weaker of LAB80 and LAB71; p <= 0.05 stands; 0.05 < p <= 0.20 "
  "weakened; p > 0.20 not shown)")
order = ["STANDS", "WEAKENED", "NOT SHOWN"]
for stat in ("p1", "p2"):
    b80, b71 = branch(RES["LAB80"][stat]), branch(RES["LAB71"][stat])
    v = order[max(order.index(b80), order.index(b71))]
    P(f"   {stat} ({'S1, one label' if stat == 'p1' else 'S2, all non-robust'}): LAB80 p = {RES['LAB80'][stat]:.4f} -> {b80}; "
      f"LAB71 p = {RES['LAB71'][stat]:.4f} -> {b71}; VERDICT {v}")
    if stat == "p1":
        V1 = v
P(f"   title: {'kept (not fragility stated as a finding)' if V1 == 'STANDS' else 'FALLBACK: Answer agreement measures difficulty: a robustness predictor and its self-audit'}")

# ================================================================ information only
P("\n## information only (no decision): other bin counts, the 63 matched cases, key-scored accuracy tertiles")
for name, rows in (("LAB80", LAB80), ("LAB71", LAB71), ("LAB63", LAB63)):
    for label, score, nb in (("agreement, 2 bins", A, 2), ("agreement, 3 bins (tertiles)", A, 3), ("agreement, 4 bins", A, 4),
                             ("agreement, 5 bins", A, 5), ("key-scored accuracy, 3 bins", KEYACC, 3)):
        if name != "LAB63" and label == "agreement, 3 bins (tertiles)":
            continue
        cuts, pbin, counts = bins_for(rows, score, nb)
        obs, S1, S2, multi, _, _ = shuffle_null(rows, lambda r, pb=pbin: (r["cfg"], pb[r["key"]]))
        n1, n2, nd = pvals(obs, S1, S2)
        P(f"   {name} {label:30s}: S1 {obs[0]} of {len(multi)}: null mean {S1.mean():.2f}, p1 = {n1} / {NPERM} = {n1 / NPERM:.4f}; "
          f"S2 {obs[2]} of {obs[1]}: null mean {np.nanmean(S2):.3f}, p2 = {n2} / {NPERM} = {n2 / NPERM:.4f}")

# ================================================================ (b) SECONDARY: leave-one-configuration-out label check
P("\n## (b) SECONDARY: label ~ agreement (M0) against label ~ agreement + the other configurations' mean label on the same "
  "text (M1); ridge logistic, leave-one-template-out; template bootstrap")


def fit_logit(X, y, lam=1.0):
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    b = np.zeros(Z.shape[1])
    L = np.diag([0.0] + [lam] * X.shape[1])
    for _ in range(100):
        p = 1 / (1 + np.exp(-Z @ b))
        g = Z.T @ (y - p) - L @ b
        H = Z.T @ (Z * (p * (1 - p))[:, None]) + L
        step = np.linalg.solve(H, g)
        b = b + step
        if np.max(np.abs(step)) < 1e-10:
            break
    return b, mu, sd


def predict(model, X):
    b, mu, sd = model
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    return 1 / (1 + np.exp(-Z @ b))


def auc_idx(score, y, cfg, idx):
    """Within-configuration AUC over the (possibly repeated) row indices idx."""
    num = den = 0.0
    s, yy, cc = score[idx], y[idx], cfg[idx]
    for c in np.unique(cc):
        a = s[(cc == c) & (yy == 1)]
        b = s[(cc == c) & (yy == 0)]
        if len(a) and len(b):
            d = a[:, None] - b[None, :]
            num += (d > 0).sum() + 0.5 * (d == 0).sum()
            den += d.size
    return num / den if den else np.nan


SEC = {}
for name, rows0 in (("LAB80", LAB80), ("LAB71", LAB71)):
    multi = groups(rows0)
    rows = [rows0[j] for g in multi for j in g]
    y = np.array([r["y"] for r in rows], dtype=float)
    cfg = np.array([r["cfg"] for r in rows])
    T = np.array([r["T"] for r in rows])
    x1 = np.array([A[r["T"]] for r in rows])
    x2 = np.array([np.mean([o["y"] for o in rows if o["key"] == r["key"] and o["cfg"] != r["cfg"]]) for r in rows])
    p0, p1_ = np.zeros(len(rows)), np.zeros(len(rows))
    for t in np.unique(T):
        tr, te = T != t, T == t
        m0 = fit_logit(x1[tr, None], y[tr])
        m1 = fit_logit(np.column_stack([x1[tr], x2[tr]]), y[tr])
        p0[te] = predict(m0, x1[te, None])
        p1_[te] = predict(m1, np.column_stack([x1[te], x2[te]]))
    full0 = fit_logit(x1[:, None], y)
    full1 = fit_logit(np.column_stack([x1, x2]), y)
    allidx = np.arange(len(rows))
    a0, a1 = auc_idx(p0, y, cfg, allidx), auc_idx(p1_, y, cfg, allidx)
    c0, c1 = ((p0 >= 0.5) == (y == 1)).mean(), ((p1_ >= 0.5) == (y == 1)).mean()
    rng = np.random.default_rng(SEED)
    U = np.unique(T)
    by = {u: np.where(T == u)[0] for u in U}
    bA0, bA1, bD, bC0, bC1, bCD = [], [], [], [], [], []
    dropped = 0
    for _ in range(NBOOT):
        ix = np.concatenate([by[u] for u in rng.choice(U, len(U), replace=True)])
        u0, u1 = auc_idx(p0, y, cfg, ix), auc_idx(p1_, y, cfg, ix)
        if np.isnan(u0) or np.isnan(u1):
            dropped += 1
            continue
        k0, k1 = ((p0[ix] >= 0.5) == (y[ix] == 1)).mean(), ((p1_[ix] >= 0.5) == (y[ix] == 1)).mean()
        bA0.append(u0), bA1.append(u1), bD.append(u1 - u0), bC0.append(k0), bC1.append(k1), bCD.append(k1 - k0)
    ci = lambda v: (np.percentile(v, 2.5), np.percentile(v, 97.5))  # noqa: E731
    SEC[name] = dict(a0=a0, a1=a1, d=a1 - a0, ci_d=ci(bD), c0=c0, c1=c1)
    P(f"\n### {name}: {len(rows)} cases on {len(multi)} multi-configuration problems ({int(y.sum())} non-robust; {len(U)} templates)")
    P(f"   full-data fit (information): M0 beta {np.round(full0[0], 3).tolist()}; M1 beta {np.round(full1[0], 3).tolist()} "
      "(intercept, agreement, others' mean label; standardised)")
    P(f"   LOTO within-configuration AUC: M0 (agreement) {a0:.3f} [{ci(bA0)[0]:.3f}, {ci(bA0)[1]:.3f}]; M1 (+ others' label) {a1:.3f} "
      f"[{ci(bA1)[0]:.3f}, {ci(bA1)[1]:.3f}]; difference {a1 - a0:+.3f} [{ci(bD)[0]:+.3f}, {ci(bD)[1]:+.3f}]")
    P(f"   LOTO accuracy (non-robust iff p >= 0.5): M0 {int(round(c0 * len(rows)))}/{len(rows)} = {c0:.3f} [{ci(bC0)[0]:.3f}, {ci(bC0)[1]:.3f}]; "
      f"M1 {int(round(c1 * len(rows)))}/{len(rows)} = {c1:.3f} [{ci(bC1)[0]:.3f}, {ci(bC1)[1]:.3f}]; difference {c1 - c0:+.3f} "
      f"[{ci(bCD)[0]:+.3f}, {ci(bCD)[1]:+.3f}]")
    P(f"   bootstrap: {NBOOT} template resamples, seed {SEED}; dropped (no within-configuration pair) {dropped}")
    wrong1 = [f"T{rows[i]['T']:02d} {rows[i]['cfg']} {'NR' if y[i] else 'R'} (p {p1_[i]:.2f})" for i in range(len(rows)) if (p1_[i] >= 0.5) != (y[i] == 1)]
    wrong0 = [f"T{rows[i]['T']:02d} {rows[i]['cfg']} {'NR' if y[i] else 'R'} (p {p0[i]:.2f})" for i in range(len(rows)) if (p0[i] >= 0.5) != (y[i] == 1)]
    P(f"   M1 wrong: {', '.join(wrong1) or 'none'}")
    P(f"   M0 wrong: {', '.join(wrong0) or 'none'}")

lo80 = SEC["LAB80"]["ci_d"][0]
P(f"\n## secondary reading (pre-registered: SUPPORTS iff the 95% interval of the LAB80 AUC difference lies above 0): "
  f"{'SUPPORTS' if lo80 > 0 else 'NOT SHOWN'} (LAB80 difference {SEC['LAB80']['d']:+.3f}, interval lower end {lo80:+.3f})")
open(os.path.join(HERE, "samelabel_difficulty.out"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
