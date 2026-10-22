"""Draft 32 of the four-page report: read-only recomputation of every main-text number on INSTANCE-MATCHED rows
(the labelled row's problem text = the text every one of our readings used), with the all-row values beside them.

The second prize-judge review of draft 31 (ledger 664) found that some labelled rows carry a different number instance
from the template text our reads used. This script rebuilds that set itself and recomputes, read-only:
  0. the matched set: sha1(text)[:12] of each labelled row's problem (hf/train-main-v2.parquet for the 82 old rows; the
     15 October revision fa8af758 held in miners19/scan/raw for the 12 Skywork rows added then) against sha1[:12] of the
     template text in calib.json that every read used;
  1. Figure 1's within-configuration AUCs (dress read K 32, 80 pooled attempts, key-scored), all / hard / easy, the
     misordered same-configuration pairs, the agreement band, and the single held reads (machinery of
     figures/make_agreement_by_label_v30.py and draft31/pairs_within_config_v31.py: lane G g_common, lane X xbench);
  2. the entry's rules (v95, lane G run_policy) leave-one-template-out on the dress read; the key-scored ceiling;
  3. Table 1: accuracy with template-bootstrap intervals, the predicted board (lane G g3_board's model) and the 80-row,
     8-read line (lane ADVERSARY's adv_load = the rows80 construction);
  4. decision.json refitted without the mismatched rows: calls on every read, and the decision boundary on a grid;
  5. the thesis counts: labels by exact problem text, and a text-level oracle (other configurations' mean drop >= 0.175);
  6. the five-rater LATENT hard-row AUC (miners14/laneA ratings; a6_score.py's pooled AUC).

usage: PYTHONDONTWRITEBYTECODE=1 ~/.venvs/aimo-hf/bin/python recompute_matched_v32.py   (CPU, about a minute; run from a
scratch folder; writes only recompute_matched_v32.out next to this file)
"""
import collections
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
AIMO = os.environ.get("AIMO_DIR", ".")  # set AIMO_DIR to the folder that holds hf/ and work/ (paths below are relative to it)
WORK = os.path.join(AIMO, "work")
sys.path.insert(0, os.path.join(WORK, "miners17", "laneG"))
sys.path.insert(0, os.path.join(WORK, "miners17", "laneX"))
sys.path.insert(0, os.path.join(WORK, "miners20", "adversary"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import binom, rankdata  # noqa: E402

import g_common as G  # noqa: E402
import xbench  # noqa: E402
import adv_load as AL  # noqa: E402

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


sha = lambda t: hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]  # noqa: E731
F_OLD = os.path.join(AIMO, "hf", "train-main-v2.parquet")
F_NEW = os.path.join(WORK, "miners19", "scan", "raw", "hf_train_main_v2_fa8af758", "train-00000-of-00001.parquet")
F_CAL = os.path.join(WORK, "sub_v135m", "calib.json")
P("# recompute_matched_v32.py: draft 32 numbers on instance-matched rows (computed, post hoc, held files only; nothing OFFICIAL)")
for nm, p in (("hf/train-main-v2.parquet", F_OLD), ("fa8af758 parquet", F_NEW), ("calib.json (v135m)", F_CAL),
              ("calib.json (v101m)", os.path.join(WORK, "sub_v101m", "calib.json")), ("dress log", os.path.join(WORK, "runs", "v88_dress_987666.log")),
              ("x_pool.json", os.path.join(WORK, "miners17", "laneX", "x_pool.json")), ("g_common.py", os.path.join(WORK, "miners17", "laneG", "g_common.py")),
              ("adv_load.py", os.path.join(WORK, "miners20", "adversary", "adv_load.py"))):
    P(f"   md5 {nm:26s} {md5(p)}")

# ================================================================ 0. the matched set
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
P("check: the sha1 match equals calib.json's own_text flag (build_calib.py: row problem == the template's first problem) on 82/82 "
  "rows; the same calib.json (md5 d5b98e21) is in every bundle from sub_v2m (2 October) on")
LAB71 = [r for r in ALLROWS if not r["new"] and r["y"] is not None]
LAB80 = LAB71 + [r for r in ALLROWS if r["new"] and r["y"] is not None]
assert len(LAB71) == 71 and len(LAB80) == 80
mm71 = [r for r in LAB71 if not r["match"]]
mm80 = [r for r in LAB80 if not r["match"]]
mmall = [r for r in ALLROWS if not r["match"]]
desc = lambda r: f"T{r['T']:02d} {r['cfg']} {'NR' if r['y'] else ('R' if r['y'] == 0 else 'unlabelled')}{' (added 15 Oct)' if r['new'] else ''}"  # noqa: E731
P("\n## 0. instance-matched rows (key = sha1(problem text)[:12]; read text = the template text in calib.json that every read used)")
P(f"rows whose text differs from the read text: {len(mmall)} of 94 parquet rows: " + ", ".join(desc(r) for r in mmall))
P(f"labelled: {len(mm71)} of 71 (old rows) mismatched -> {71 - len(mm71)} matched; {len(mm80)} of 80 (with the 9 labelled rows of "
  f"15 Oct) mismatched -> {80 - len(mm80)} matched")
P("   mismatched labelled rows: " + ", ".join(desc(r) for r in mm80))
for r in mm80:
    a = re.findall(r"\d+", (old.problem[r["i"]] if r["i"] < 82 else new.problem[r["i"]]))
    b = re.findall(r"\d+", texts[r["T"] - 1])
    P(f"   {desc(r):34s} labelled-text key {r['key']} vs read-text key {r['readkey']}; first numbers {a[:8]} vs {b[:8]}")
y71 = np.array([r["y"] for r in LAB71])
M71 = np.array([r["match"] for r in LAB71])
P(f"matched 71-row set: {M71.sum()} rows ({int(y71[M71].sum())} NR); mismatched {(~M71).sum()} rows, of them NR {int(y71[~M71].sum())}")

# ================================================================ 1. Figure 1's AUCs on matched rows
D, FIT = G.build_fit_data()
assert [(int(T), c, int(yy)) for T, c, yy in zip(D["T"], D.cfg, D.y)] == [(r["T"], r["cfg"], r["y"]) for r in LAB71]
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
reads = sorted({a[4] for T in TS for a in LOW[T]})
single = {r: {T: pair_nat([a for a in LOW[T] if a[4] == r]) for T in TS} for r in reads}
RX = xbench.ROWS
assert [(r["T"], r["cfg"], r["y"]) for r in RX] == [(r["T"], r["cfg"], r["y"]) for r in LAB71]
for rx, r in zip(RX, LAB71):
    rx["match"] = r["match"]
HARD = G.HARD
SETS = {"all": lambda r: True, "hard": lambda r: r["T"] in HARD, "easy": lambda r: r["T"] not in HARD}
auc = lambda f, rows: xbench.auc_within({T: 1 - f[T] for T in TS}, rows)  # noqa: E731
P("\n## 1. within-configuration AUC (value, rows, non-robust rows, pairs): matched rows [all 71 rows]")
RES = {}
for name, f in (("deployed agreement, dress read K 32", agree), ("agreement, 80 pooled attempts", pooled),
                ("key-scored accuracy, 80 pooled attempts", keyacc)):
    parts = []
    for s, fn in SETS.items():
        am = auc(f, [r for r in RX if fn(r) and r["match"]])
        aa = auc(f, [r for r in RX if fn(r)])
        RES[(name, s)] = (am, aa)
        parts.append(f"{s} {am[0]:.3f} ({am[1]}, {am[2]}, {am[3]}) [{aa[0]:.3f} ({aa[1]}, {aa[2]}, {aa[3]})]")
    P(f"{name:40s} " + " | ".join(parts))
dk = RES[("deployed agreement, dress read K 32", "hard")]
pk = RES[("agreement, 80 pooled attempts", "hard")]
kk = RES[("key-scored accuracy, 80 pooled attempts", "hard")]
P(f"hard rows: 80 pooled attempts ({80 / 32:.1f}x K 32) add {pk[0][0] - dk[0][0]:+.3f} AUC [{pk[1][0] - dk[1][0]:+.3f}]; the key-scored "
  f"share {kk[0][0] - dk[0][0]:+.3f} [{kk[1][0] - dk[1][0]:+.3f}]")
sh_m = [auc(single[r], [x for x in RX if x["T"] in HARD and x["match"]])[0] for r in reads]
sh_a = [auc(single[r], [x for x in RX if x["T"] in HARD])[0] for r in reads]
P(f"single held reads (K 8 or 16), hard rows, matched: {', '.join(f'{v:.3f}' for v in sh_m)}; range {min(sh_m):.3f} to {max(sh_m):.3f} "
  f"[all: range {min(sh_a):.3f} to {max(sh_a):.3f}]")
ez = [x for x in RX if x["T"] not in HARD and x["match"]]
P(f"easy matched rows: {len(ez)}, robust {sum(1 for x in ez if x['y'] == 0)}; hard matched rows: "
  f"{sum(1 for x in RX if x['T'] in HARD and x['match'])}, NR {sum(1 for x in RX if x['T'] in HARD and x['match'] and x['y'] == 1)}")
STANDIN = {"Qwen", "DeepSeek", "low", "medium"}


def pairs(f, rows, label):
    score = {T: 1 - f[T] for T in TS}
    tot, mis, tie, lst = collections.Counter(), collections.Counter(), collections.Counter(), collections.defaultdict(list)
    for c in sorted(set(r["cfg"] for r in rows)):
        for a in [r for r in rows if r["cfg"] == c and r["y"] == 1]:
            for b in [r for r in rows if r["cfg"] == c and r["y"] == 0]:
                tot[c] += 1
                if score[a["T"]] < score[b["T"]]:
                    mis[c] += 1
                    lst[c].append(f"T{a['T']:02d} NR {f[a['T']]:.3f} > T{b['T']:02d} R {f[b['T']]:.3f}")
                elif score[a["T"]] == score[b["T"]]:
                    tie[c] += 1
    N, M = sum(tot.values()), sum(mis.values()) + 0.5 * sum(tie.values())
    P(f"   {label}: pairs {N}, misordered {sum(mis.values())}, ties {sum(tie.values())}, AUC {1 - M / N:.3f}")
    for c in tot:
        if mis[c] or tie[c]:
            P(f"      {c:9s} pairs {tot[c]:3d} misordered {mis[c]} ties {tie[c]} {lst[c]}")
    s_t = sum(tot[c] for c in tot if c in STANDIN)
    s_m = sum(mis[c] for c in tot if c in STANDIN)
    P(f"      stand-in configurations (Qwen, DeepSeek, low, medium): pairs {s_t}, misordered {s_m}; others: pairs {N - s_t}, "
      f"misordered {sum(mis.values()) - s_m}")
    return N, sum(mis.values())


P("\nmisordered same-configuration pairs, deployed agreement (dress read K 32):")
pairs(agree, [r for r in RX if r["T"] in HARD and r["match"]], "hard, matched")
pairs(agree, [r for r in RX if r["T"] in HARD], "hard, all 71 (draft 31: 56 pairs, 7 misordered)")
pairs(agree, [r for r in RX if r["match"]], "all, matched")
pairs(agree, RX, "all, all 71")
BAND = (0.555, 0.825)
for lbl, rows in (("matched", [r for r in RX if r["T"] in HARD and r["match"]]), ("all 71", [r for r in RX if r["T"] in HARD])):
    band = [r for r in rows if BAND[0] <= agree[r["T"]] <= BAND[1]]
    nr = [r for r in band if r["y"] == 1]
    rr = [r for r in band if r["y"] == 0]
    same = sum(1 for a in nr for b in rr if a["cfg"] == b["cfg"])
    KEY71 = {(r["T"], r["cfg"]): r["key"] for r in LAB71}
    same_txt = sum(1 for a in nr for b in rr if KEY71[(a["T"], a["cfg"])] == KEY71[(b["T"], b["cfg"])])
    same_tpl = sum(1 for a in nr for b in rr if a["T"] == b["T"])
    P(f"   band 0.56 to 0.82, hard rows, {lbl}: {len(rr)} robust, {len(nr)} NR; pairs {len(rr) * len(nr)}, same configuration {same}, "
      f"cross configuration {len(rr) * len(nr) - same}; same exact problem text {same_txt}, same template {same_tpl}, different problem "
      f"text {len(rr) * len(nr) - same_txt}; NR rows: " + ", ".join(f"T{r['T']:02d} {r['cfg']}" for r in nr))

# ================================================================ 2. the entry (v95 rules) LOTO on the dress read
P("\n## 2. the entry (v95 rules), leave-one-template-out on the dress read (lane G run_policy; decision.json refitted per fold)")
Tr, cfg = D["T"].values, D.cfg.values
hard = np.isin(Tr, sorted(HARD))
fresh = np.isin(Tr, sorted(G.FRESH))
small = np.isin(cfg, ["Qwen", "Skywork", "Olmo", "DeepSeek"])
yh = G.run_policy(D, FIT, pool, G.V95, "loto")
yin = G.run_policy(D, FIT, pool, G.V95, "shipped")
ok = yh == y71
P(f"LOTO right: matched {int(ok[M71].sum())}/{int(M71.sum())} [all {int(ok.sum())}/71]; in-sample (shipped decision.json) matched "
  f"{int((yin == y71)[M71].sum())}/{int(M71.sum())} [all {int((yin == y71).sum())}/71]")
for lbl, m in (("hard", hard), ("easy", ~hard), ("fresh", fresh), ("small-model", small)):
    P(f"   {lbl:12s} matched {int(ok[m & M71].sum())}/{int((m & M71).sum())} [all {int(ok[m].sum())}/{int(m.sum())}]")
P("   errors on mismatched rows: " + ", ".join(f"T{Tr[i]:02d} {cfg[i]}" for i in np.where(~ok & ~M71)[0])
  + "; right on mismatched rows: " + ", ".join(f"T{Tr[i]:02d} {cfg[i]}" for i in np.where(ok & ~M71)[0]))
ROUTE = {"Skywork": "own run (board-chosen)", "Olmo": "own run (board-chosen)", "high": "prior (board-chosen)"}
for lbl, m in (("fresh, matched", fresh & M71), ("fresh, all 24", fresh)):
    er = [i for i in np.where(~ok & m)[0]]
    P(f"   LOTO errors on {lbl}: {len(er)}; on board-chosen routes {sum(1 for i in er if cfg[i] in ROUTE)}: " + ", ".join(
        f"T{Tr[i]:02d} {cfg[i]} ({ROUTE.get(cfg[i], 'stand-in')})" for i in er))
P("   errors on matched rows: " + ", ".join(f"T{Tr[i]:02d} {cfg[i]} {'NR' if y71[i] else 'R'}{' (hard)' if hard[i] else ''}" for i in np.where(~ok & M71)[0]))
D2 = D.copy()
D2["pair16"] = [keyacc[T] for T in D2["T"].values]
yk = G.run_policy(D2, FIT, {T: dict(pool[T], prim=keyacc[T]) for T in pool}, G.V95, "loto")
ch = np.where(yk != yh)[0]
P(f"key-scored share in place of agreement (ceiling), LOTO: right matched {int((yk == y71)[M71].sum())}/{int(M71.sum())} "
  f"[all {int((yk == y71).sum())}/71]; hard matched {int((yk == y71)[M71 & hard].sum())}/{int((M71 & hard).sum())} "
  f"[all {int((yk == y71)[hard].sum())}/{int(hard.sum())}]; rows changed: "
  + "; ".join(f"T{Tr[i]:02d} {cfg[i]} {'fixed' if yk[i] == y71[i] else 'broken'}{'' if M71[i] else ' (mismatched row)'}" for i in ch))
P(f"   key fixes on matched hard rows: {sum(1 for i in ch if M71[i] and hard[i] and yk[i] == y71[i])} "
  f"[all hard rows: {sum(1 for i in ch if hard[i] and yk[i] == y71[i])}]; breaks {sum(1 for i in ch if M71[i] and yk[i] != y71[i])}")

# ================================================================ 3. Table 1
P("\n## 3. Table 1 on matched rows [all rows]: LOTO accuracy, template-bootstrap 95% interval (10,000, seed 17), predicted board")


def acc_ci(mask, B=10000):
    idx0 = np.where(mask)[0]
    yy, hh, T = y71[idx0], yh[idx0], Tr[idx0]
    lo, hi, _ = G.tboot(T, lambda ix: float((yy[ix] == hh[ix]).mean()), B)
    return int((yy == hh).sum()), len(idx0), (yy == hh).mean(), lo, hi


def predictive(mask, n, n_r, n_nr):
    idx0 = np.where(mask)[0]
    yy, hh, T = y71[idx0], yh[idx0], Tr[idx0]
    p0 = G.board_mix(yy, hh, n_r, n_nr)
    lo, hi, ps = G.tboot(T, lambda ix: G.board_mix(yy[ix], hh[ix], n_r, n_nr), 10000)
    ps = ps[~np.isnan(ps)]
    pmf = np.mean([binom.pmf(np.arange(n + 1), n, p) for p in ps], axis=0)
    cdf = np.cumsum(pmf)
    return p0, n * p0, int(np.searchsorted(cdf, 0.05)), int(np.searchsorted(cdf, 0.95))


for lbl, m, n, nr, nnr in (("all labelled", np.ones(71, bool), 21, 10, 11), ("fresh AIME-2026", fresh, 21, 10, 11),
                           ("small-model", small, 14, 7, 7)):
    vals = []
    for mk in (m & M71, m):
        k, N, a, lo, hi = acc_ci(mk)
        p0, e, q05, q95 = predictive(mk, n, nr, nnr)
        vals.append(f"{k}/{N} = {a:.3f} [{lo:.4f}, {hi:.4f}]; board-mix ({nr} R / {nnr} NR) {p0:.3f} -> predicted {e:.1f} of {n} "
                    f"(90% {q05} to {q95})")
    P(f"   {lbl:16s} matched {vals[0]}\n   {'':16s} all     {vals[1]}")
# the 80-row line: 8 reads pooled (lane ADVERSARY loader = rows80 construction), LOTO-80
D80, FIT80, READS, _pool, _o3 = AL.build()
RN = list(READS)
assert [(int(T), c, int(yy)) for T, c, yy in zip(D80["T"], D80.cfg, D80.y)] == [(r["T"], r["cfg"], r["y"]) for r in LAB80]
y80 = D80.y.values.astype(int)
M80 = np.array([r["match"] for r in LAB80])
Tr80, cfg80 = D80["T"].values, D80.cfg.values
DEP8 = np.array([G.run_policy(D80, FIT80, READS[nm], G.V95, "loto") for nm in RN])
r_m = (DEP8[:, M80] == y80[M80]).sum(1)
r_a = (DEP8 == y80).sum(1)
bal_m = np.mean([G.bal(y80[M80], DEP8[k, M80]) for k in range(len(RN))])
bal_a = np.mean([G.bal(y80, DEP8[k]) for k in range(len(RN))])
P(f"   80 rows, 8 reads pooled, LOTO-80: matched {r_m.mean():.2f}/{int(M80.sum())} = {r_m.mean() / M80.sum():.3f} (per read {min(r_m)} to "
  f"{max(r_m)}: {' '.join(str(v) for v in r_m)}; balanced {bal_m:.3f}; always-robust {int((y80[M80] == 0).sum())}/{int(M80.sum())} = "
  f"{(y80[M80] == 0).mean():.3f}; NR {int(y80[M80].sum())})")
P(f"   {'':16s} all     {r_a.mean():.2f}/80 = {r_a.mean() / 80:.3f} (per read {min(r_a)} to {max(r_a)}; balanced {bal_a:.3f}; always-robust "
  f"{(y80 == 0).mean():.3f})")

# ================================================================ 4. decision.json refitted without the mismatched rows
P("\n## 4. decision.json refitted on the matched rows only (63 of 71): does any call change?")
m63 = G.fit_models(D, FIT, M71)
m71 = G.fit_models(D, FIT, np.ones(71, bool))
for k in ("full", "agreement_only", "finish_only"):
    assert np.allclose(m71[k]["beta"], G.DEC[k]["beta"], atol=2e-4), k
    P(f"   {k:15s} decision.json beta {[round(b, 3) for b in G.DEC[k]['beta']]} -> matched-only refit {[round(float(b), 3) for b in m63[k]['beta']]}")
in80_old = ~D80.new.values.astype(bool)
M80_old = M80 & in80_old
n_changed_shipped, n_changed_loto = [], []
for nm in RN:
    a = G.run_policy(D80, FIT80, READS[nm], G.V95, "split", [(in80_old, np.ones(80, bool))])        # all 71 old rows (= decision.json)
    b = G.run_policy(D80, FIT80, READS[nm], G.V95, "split", [(M80_old, np.ones(80, bool))])         # matched old rows only
    s = G.run_policy(D80, FIT80, READS[nm], G.V95, "shipped")
    assert (a == s).all()
    la = DEP8[RN.index(nm)]
    lb = G.run_policy(D80, FIT80, READS[nm], G.V95, "split", [((Tr80 != T0) & M80, Tr80 == T0) for T0 in np.unique(Tr80)])
    n_changed_shipped.append(int((a != b).sum()))
    n_changed_loto.append(int((la != lb).sum()))
    for lbl, u, v in (("full fit -> matched-only fit", a, b), ("LOTO-80 -> LOTO-80 without mismatched rows", la, lb)):
        for i in np.where(u != v)[0]:
            P(f"      {nm:34s} {lbl:44s} T{Tr80[i]:02d} {cfg80[i]} {'NR' if y80[i] else 'R'}{'' if M80[i] else ' (mismatched row)'}: "
              f"{'N' if u[i] else 'R'} -> {'N' if v[i] else 'R'} ({'fixes' if v[i] == y80[i] else 'breaks'})")
P(f"   calls on the 80 rows, full-fit decision.json vs matched-only refit, per read: {n_changed_shipped} (changed calls)")
P(f"   calls on the 80 rows, LOTO-80 refit with vs without the mismatched rows in training, per read: {n_changed_loto}")
yb = G.run_policy(D, FIT, pool, G.V95, "split", [((Tr != T0) & M71, Tr == T0) for T0 in np.unique(Tr)])
yb_in = G.run_policy(D, FIT, pool, G.V95, "split", [(M71, np.ones(71, bool))])
P(f"   dress read, in-sample: decision.json vs matched-only refit, calls changed on the 71 rows {int((yb_in != yin).sum())}")
P(f"   dress read, LOTO on 71 trained on matched rows only: calls changed {int((yb != yh).sum())}; right on matched {int((yb == y71)[M71].sum())}/{int(M71.sum())}")
# decision boundary on a grid of possible readings (prim 0..1 by 0.001, qfin 0/1, strength 1/2/3)
diff, tot = 0, 0
thr = []
for s in (1.0, 2.0, 3.0):
    for qv in (0.0, 1.0):
        xs = np.linspace(0, 1, 1001)
        za = np.array([G.margin(m71["full"], (x, qv, s)) for x in xs]) > 0
        zb = np.array([G.margin(m63["full"], (x, qv, s)) for x in xs]) > 0
        diff += int((za != zb).sum())
        tot += len(xs)
        ta = xs[np.where(za != za[0])[0][0]] if (za != za[0]).any() else None
        tb = xs[np.where(zb != zb[0])[0][0]] if (zb != zb[0]).any() else None
        thr.append((s, qv, ta, tb))
    for x0 in (0.0,):
        pass
xs = np.linspace(0, 1, 1001)
for s in (1.0, 2.0, 3.0):
    za = np.array([G.margin(m71["agreement_only"], (x, s)) for x in xs]) > 0
    zb = np.array([G.margin(m63["agreement_only"], (x, s)) for x in xs]) > 0
    diff += int((za != zb).sum())
    tot += len(xs)
    ta = xs[np.where(za != za[0])[0][0]] if (za != za[0]).any() else None
    tb = xs[np.where(zb != zb[0])[0][0]] if (zb != zb[0]).any() else None
    thr.append((s, "agreement_only", ta, tb))
P(f"   decision boundary on a grid of readings (agreement 0 to 1 by 0.001 x quick finish 0 / 1 x strength 1 / 2 / 3; and the "
  f"agreement-only model): grid points whose call changes {diff} of {tot}")
P("   agreement threshold (strength, quick finish): decision.json -> matched-only refit: " + "; ".join(
    f"({s:.0f}, {q}) {('%.3f' % a) if a is not None else 'none'} -> {('%.3f' % b) if b is not None else 'none'}" for s, q, a, b in thr))

# ================================================================ 5. thesis counts: labels by exact problem text
P("\n## 5. labels by exact problem text (all 80 labelled rows, each under its own labelled text)")
for nmset, rows in (("80 labelled rows", LAB80), ("71 labelled rows (82-row file)", LAB71)):
    grp = collections.defaultdict(list)
    for r in rows:
        grp[r["key"]].append(r)
    multi = {k: v for k, v in grp.items() if len({r["cfg"] for r in v}) >= 2}
    one = [k for k, v in multi.items() if len({r["y"] for r in v}) == 1]
    withnr = [k for k, v in multi.items() if any(r["y"] == 1 for r in v)]
    allnr = [k for k in withnr if all(r["y"] == 1 for r in multi[k])]
    P(f"   {nmset}: {len(grp)} distinct problem texts; multi-configuration {len(multi)}; one label {len(one)} of {len(multi)}; with an NR "
      f"label {len(withnr)}, NR for all their configurations {len(allnr)} of {len(withnr)}")
    for k, v in sorted(multi.items(), key=lambda kv: kv[1][0]["T"]):
        if len({r["y"] for r in v}) > 1 or any(r["y"] == 1 for r in v):
            P(f"      T{v[0]['T']:02d} text {k}{' (read text)' if v[0]['match'] else ' (other instance)'}: "
              + ", ".join(f"{r['cfg']} {'NR' if r['y'] else 'R'}" for r in v))
grp80 = collections.defaultdict(list)
for r in LAB80:
    grp80[r["key"]].append(r)
single_nr = [v[0] for k, v in grp80.items() if len({r["cfg"] for r in v}) == 1 and v[0]["y"] == 1]
P("   single-configuration problem texts with an NR label (80 rows): " + ", ".join(
    f"T{r['T']:02d} {r['cfg']}{'' if r['match'] else ' (other instance)'}" for r in sorted(single_nr, key=lambda r: r["T"])))

P("\n## 5b. text-level oracle: NR iff the OTHER configurations' rows with the same exact text have mean max_drop >= 0.175 (rows "
  "without another configuration on their text keep the entry's call); against the deployed LOTO-80 calls of the 8 reads")
bykey = collections.defaultdict(list)
for r in ALLROWS:
    bykey[r["key"]].append(r)
for variant, use in (("others = every parquet row (labelled or not)", lambda o: True), ("others = labelled rows only", lambda o: o["y"] is not None)):
    orc = np.full(80, -1)
    for j, r in enumerate(LAB80):
        others = [o for o in bykey[r["key"]] if o["cfg"] != r["cfg"] and use(o)]
        if others:
            orc[j] = int(np.mean([o["drop"] for o in others]) >= 0.175)
    defined = orc >= 0
    fx, br = [], []
    fxa, bra = [], []
    for k in range(len(RN)):
        dep = DEP8[k]
        new_c = np.where(defined, orc, dep)
        fx.append(int(((new_c == y80) & (dep != y80) & M80).sum()))
        br.append(int(((new_c != y80) & (dep == y80) & M80).sum()))
        fxa.append(int(((new_c == y80) & (dep != y80)).sum()))
        bra.append(int(((new_c != y80) & (dep == y80)).sum()))
    P(f"   {variant}: defined on {int((defined & M80).sum())} of {int(M80.sum())} matched rows; per read fixes {fx} breaks {br}; mean fixes "
      f"{np.mean(fx):.2f}, breaks {np.mean(br):.2f} on matched rows [all 80: fixes {np.mean(fxa):.2f}, breaks {np.mean(bra):.2f}]")
    P(f"      oracle alone on its defined matched rows: right {int(((orc == y80) & defined & M80).sum())} of {int((defined & M80).sum())}")

# ================================================================ 6. the five-rater LATENT hard-row AUC
P("\n## 6. LATENT ratings: pooled AUC on hard rows (a6_score.py's AUC; higher rating -> non-robust)")
LA = os.path.join(WORK, "miners14", "laneA")


def load(p):
    d = json.load(open(os.path.join(LA, p)))
    d = {x["id"]: x for x in d} if isinstance(d, list) else d
    return {int(k[1:]): float(v["LATENT"]) for k, v in d.items()}


RAT = [load(p) for p in ("a6_analyst_ratings.json", "a6r_analyst2_ratings.json", "blind3/rater3.json", "blind3/rater4.json", "blind3/rater5.json")]
LAT5 = {T: float(np.mean([r[T] for r in RAT])) for T in TS}


def auc_pooled(score, yv):
    score, yv = np.asarray(score, float), np.asarray(yv)
    pos, neg = score[yv == 1], score[yv == 0]
    rk = rankdata(np.concatenate([pos, neg]))
    return (rk[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


for nm_r, sc in (("rater 1 (the pre-set A6 bar)", RAT[0]), ("mean of the five raters", LAT5)):
    s_all = np.array([sc[T] for T in Tr])
    P(f"   {nm_r:30s} hard rows: matched {auc_pooled(s_all[hard & M71], y71[hard & M71]):.3f} ({int((hard & M71).sum())} rows, "
      f"{int(y71[hard & M71].sum())} NR) [all {auc_pooled(s_all[hard], y71[hard]):.3f} ({int(hard.sum())} rows)]; all rows matched "
      f"{auc_pooled(s_all[M71], y71[M71]):.3f} [{auc_pooled(s_all, y71):.3f}]")

# ================================================================ 7. the strings the paper prints, from the values above
P("\n## 7. PAPER VALUES (draft 32 wording; matched value first, all-row value in square brackets; rounding as printed)")
f3 = lambda v: f"{v:.3f}"  # noqa: E731
r2 = lambda v: f"{v:.2f}"  # noqa: E731


def quiet_pairs(f, rows):
    score = {T: 1 - f[T] for T in TS}
    tot, mis = collections.Counter(), collections.Counter()
    for a in [r for r in rows if r["y"] == 1]:
        for b in [r for r in rows if r["y"] == 0 and r["cfg"] == a["cfg"]]:
            tot[a["cfg"]] += 1
            mis[a["cfg"]] += score[a["T"]] < score[b["T"]]
    st = sum(tot[c] for c in tot if c in STANDIN), sum(mis[c] for c in mis if c in STANDIN)
    return sum(tot.values()), sum(mis.values()), dict(mis), st


hm, ha = [r for r in RX if r["T"] in HARD and r["match"]], [r for r in RX if r["T"] in HARD]
pm, pa = quiet_pairs(agree, hm), quiet_pairs(agree, ha)
assert pm[2] == pa[2] == {"Skywork": 1, "high": 4, "low": 2} or {k: v for k, v in pm[2].items() if v} == {"Skywork": 1, "high": 4, "low": 2}
V = RES
PV = {
    "abstract AUC": f"AUC {f3(V[('deployed agreement, dress read K 32', 'all')][0][0])} [{f3(V[('deployed agreement, dress read K 32', 'all')][1][0])}]",
    "hard AUC": f"{f3(V[('deployed agreement, dress read K 32', 'hard')][0][0])} [{f3(V[('deployed agreement, dress read K 32', 'hard')][1][0])}]",
    "pooled hard": f"{f3(V[('agreement, 80 pooled attempts', 'hard')][0][0])} [{f3(V[('agreement, 80 pooled attempts', 'hard')][1][0])}]",
    "key hard": f"{f3(V[('key-scored accuracy, 80 pooled attempts', 'hard')][0][0])} [{f3(V[('key-scored accuracy, 80 pooled attempts', 'hard')][1][0])}]",
    "abstract ceiling": f"raise it to at most {f3(max(V[('agreement, 80 pooled attempts', 'hard')][0][0], V[('key-scored accuracy, 80 pooled attempts', 'hard')][0][0]))}",
    "single reads": f"the {f3(min(sh_m))} to {f3(max(sh_m))} of single held reads",
    "single reads all": f"{f3(min(sh_a))} to {f3(max(sh_a))}",
    "easy": f"{int((~hard & M71 & (y71 == 0)).sum())} of {int((~hard & M71).sum())} rows are robust",
    "easy all": f"{int((~hard & (y71 == 0)).sum())} of {int((~hard).sum())}",
    "hard rows": f"({int((hard & M71).sum())} rows, {int(y71[hard & M71].sum())} non-robust)",
    "hard rows all": f"({int(hard.sum())} rows, {int(y71[hard].sum())} non-robust)",
    "pairs": f"{pm[1]} of {pm[0]} [{pa[1]} of {pa[0]}] same-configuration pairs",
    "stand-in pairs": f"{pm[3][1]} of {pm[3][0]} [{pa[3][1]} of {pa[3][0]}] on the stand-in's",
    "key fix": f"the key fixes {sum(1 for i in ch if M71[i] and hard[i] and yk[i] == y71[i])} of {int((hard & M71).sum())} hard rows "
               f"[{sum(1 for i in ch if hard[i] and yk[i] == y71[i])} of {int(hard.sum())}]",
    "LOTO abstract": f"gets {int(ok[M71].sum())} of {int(M71.sum())} [{int(ok.sum())} of 71] public and {int(ok[fresh & M71].sum())} of "
                     f"{int((fresh & M71).sum())} [{int(ok[fresh].sum())} of {int(fresh.sum())}] fresh rows",
    "in-sample": f"(in-sample {int((yin == y71)[M71].sum())}, {int((yin == y71).sum())})",
}
k, N, a, lo, hi = acc_ci(M71)
PV["T1 all"] = f"{k}/{N} = {a:.3f} ({r2(lo)} to {r2(hi)}) | {int(ok.sum())}/71 = {ok.mean():.3f}"
k, N, a, lo, hi = acc_ci(fresh & M71)
PV["T1 fresh"] = f"{k}/{N} = {a:.3f} ({r2(lo)} to {r2(hi)}) | {int(ok[fresh].sum())}/{int(fresh.sum())} = {ok[fresh].mean():.3f}"
for lbl, m, n, nr, nnr, tr in (("T1 board all", M71, 21, 10, 11, "main"), ("T1 board fresh", fresh & M71, 21, 10, 11, "main"),
                               ("T1 board small", small & M71, 14, 7, 7, "small")):
    p0, e, q05, q95 = predictive(m, n, nr, nnr)
    PV[lbl] = f"{tr} {e:.1f} ({q05} to {q95})"
PV["T1 small mix"] = f"{G.board_mix(y71[small & M71], yh[small & M71], 7, 7):.3f} | {G.board_mix(y71[small], yh[small], 7, 7):.3f}"
PV["T1 80"] = (f"{r_m.mean():g}/{int(M80.sum())} = {r_m.mean() / M80.sum():.3f} ({min(r_m)} to {max(r_m)} per read; balanced {bal_m:.3f}; "
               f"always-robust {(y80[M80] == 0).mean():.3f}) | {r_a.mean():g}/80 = {r_a.mean() / 80:.3f}")
PV["refit"] = (f"changes no call on the Figure 1 read (0 or 1 on seven others" if n_changed_shipped[0] == 0 and
               max(n_changed_shipped[1:]) == 1 and min(n_changed_shipped[1:]) == 0 and len(n_changed_shipped) == 8 else "REFIT CLAIM FAILS")
grp = collections.defaultdict(list)
for r in LAB80:
    grp[r["key"]].append(r)
multi = [v for v in grp.values() if len({r["cfg"] for r in v}) >= 2]
withnr = [v for v in multi if any(r["y"] == 1 for r in v)]
PV["by text"] = (f"15 of the 16" if (sum(len({r['y'] for r in v}) == 1 for v in multi), len(multi)) == (15, 16) else "BY-TEXT FAILS") + \
    (f"; 4 of the 5" if (sum(all(r['y'] == 1 for r in v) for v in withnr), len(withnr)) == (4, 5) else "; NR FAILS")
orc = np.full(80, -1)
for j, r in enumerate(LAB80):
    others = [o for o in bykey[r["key"]] if o["cfg"] != r["cfg"]]
    if others:
        orc[j] = int(np.mean([o["drop"] for o in others]) >= 0.175)
fx = [int(((np.where(orc >= 0, orc, DEP8[k_]) == y80) & (DEP8[k_] != y80) & M80).sum()) for k_ in range(len(RN))]
bk = [int(((np.where(orc >= 0, orc, DEP8[k_]) != y80) & (DEP8[k_] == y80) & M80).sum()) for k_ in range(len(RN))]
PV["oracle"] = f"would fix {np.mean(fx):.1f} of our calls per read and break {np.mean(bk):.1f}"
s5 = np.array([LAT5[T] for T in Tr])
PV["raters"] = f"{auc_pooled(s5[hard], y71[hard]):.3f} ({auc_pooled(s5[hard & M71], y71[hard & M71]):.3f} on the {int((hard & M71).sum())} matched rows"
PV["mismatch"] = f"{len(mm71)} of the 71 labelled rows ({len(mm80)} of 80)"
for kk, vv in PV.items():
    P(f"   {kk:18s} {vv}")
open(os.path.join(HERE, "recompute_matched_v32.out"), "w").write("\n".join(OUT) + "\n")
