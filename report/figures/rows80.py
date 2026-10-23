"""LANE ROWS80 (ledger 617): PREREG_rows80.txt (md5 c0f69a27...) + ADDENDUM_rows80.txt (written before any score on the new rows).

usage (CPU, ~2 min): ~/.venvs/aimo-hf/bin/python "miners19/rows80/rows80.py"   (from work/; writes rows80.out next to this file)

Q1 (decision): Skywork route, own run (v37, K 3 @ 9,000, robust iff >= 1 of 3 ended) vs the stand-in (decision.json on the
   gpt-oss low reading + quick finish) on the 12 labelled Skywork rows (9 new + 3 old), 8 stand-in reads, frozen and LOTO-80.
Q2 (information): the deployed policy (g_common.V95) leave-one-template-out on all 80 rows, per read and per configuration.
Q3 (information): decision.json refitted on clear-cut rows only (max_drop <= 0.05 or >= 0.35), out-of-fold on all 80 rows.
Machinery: lane G (miners17/laneG/g_common.py) unchanged; v124r reads via miners19/laneConf/parse_conf.py; v37 via
miners12/review/own_q1q2.py's parse() (extracted with ast, so that script's own analysis does not run).
"""
import ast
import hashlib
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.environ.get("AIMO_DIR", "."), "work")  # folder holding hf/ and work/
sys.path.insert(0, os.path.join(WORK, "miners17", "laneG"))
sys.path.insert(0, os.path.join(WORK, "miners19", "laneConf"))
import g_common as G  # noqa: E402
import parse_conf as PC  # noqa: E402

OUT = []


def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


W = lambda *p: os.path.join(WORK, *p)  # noqa: E731
F_NEW = W("miners19", "scan", "raw", "hf_train_main_v2_fa8af758", "train-00000-of-00001.parquet")
F_OLDPQ = os.path.join(G.AIMO, "hf", "train-main-v2.parquet")
F_CAL = W("sub_v135m", "calib.json")
F_V37 = W("runs", "v37_small_968679.log")
F_V124 = W("runs", "v124r_main_1004374.log")
V124_READS = ["94286138", "681617219", "794012114"]

P("# LANE ROWS80: Skywork route on 80 labelled rows (computed; CPU; no model run; nothing OFFICIAL here)")
for nm, p in (("PREREG", os.path.join(HERE, "PREREG_rows80.txt")), ("ADDENDUM", os.path.join(HERE, "ADDENDUM_rows80.txt")),
              ("new parquet", F_NEW), ("old parquet", F_OLDPQ), ("calib", F_CAL), ("decision.json", os.path.join(G.SHIP, "decision.json")),
              ("decision.json v135m", W("sub_v135m", "decision.json")), ("v37 log", F_V37), ("v124r log", F_V124),
              ("dress log", W("runs", "v88_dress_987666.log")), ("g_common.py", os.path.join(WORK, "miners17", "laneG", "g_common.py")),
              ("parse_conf.py", os.path.join(WORK, "miners19", "laneConf", "parse_conf.py")),
              ("own_q1q2.py", W("miners12", "review", "own_q1q2.py"))):
    P(f"   md5 {nm:20s} {md5(p)}")
assert md5(os.path.join(HERE, "PREREG_rows80.txt")).startswith("c0f69a27")
assert md5(os.path.join(G.SHIP, "decision.json")) == md5(W("sub_v135m", "decision.json"))

# ================================================================ data: rows, labels, template mapping
stem = lambda t: re.sub(r"\s+", " ", re.sub(r"\d+", "#", t))[:60]  # noqa: E731  (build_calib.py)
wsn = lambda t: re.sub(r"\s+", " ", t).strip()  # noqa: E731
new = pd.read_parquet(F_NEW)
oldpq = pd.read_parquet(F_OLDPQ)
cal = json.load(open(F_CAL))["rows"]
texts = list(dict.fromkeys(r["text"] for r in cal))
st2T = {}
for r in cal:
    st2T.setdefault(r["stem"], texts.index(r["text"]) + 1)
assert len(new) == 94 and len(oldpq) == 82 and len(cal) == 82 and len(texts) == 28


def lab(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else int(not bool(v))


P("\n## data checks")
bad = []
for i in range(82):
    q, o, r = new.iloc[i], oldpq.iloc[i], cal[i]
    if not (wsn(q.problem) == wsn(o.problem) and q.model_id == o.model_id == r["model_id"] and q.reasoning_effort == o.reasoning_effort == r["effort"]):
        bad.append((i, "row identity"))
    if lab(q.is_robust) != r["label"] or lab(o.is_robust) != r["label"]:
        bad.append((i, "label"))
    if abs(float(q.max_drop) - r["max_drop"]) > 1e-12:
        bad.append((i, "max_drop"))
    if st2T[stem(q.problem)] != texts.index(r["text"]) + 1:
        bad.append((i, "template"))
P(f"old 82 rows: new file rows 0-81 vs old parquet and calib.json (text / model / effort / label / max_drop / template): "
  f"{82 - len({b[0] for b in bad})}/82 identical" + (f"; MISMATCH {bad}" if bad else ""))
assert not bad
old_by_prob = {}
for i in range(82):
    old_by_prob.setdefault(wsn(new.problem[i]), set()).add(st2T[stem(new.problem[i])])
NEWROWS = []
for i in range(82, 94):
    q = new.iloc[i]
    T = st2T.get(stem(q.problem))
    m = wsn(q.problem) in old_by_prob
    NEWROWS.append(dict(i=i, T=T, match=m, own_text=(T is not None and wsn(q.problem) == wsn(texts[T - 1])), model_id=q.model_id,
                        effort=q.reasoning_effort, y=lab(q.is_robust), max_drop=float(q.max_drop)))
    if T is None or not m or T not in old_by_prob[wsn(q.problem)]:
        P(f"   ROW {i} FAILS TO MATCH: T {T}, problem in old rows {m}")
assert all(r["model_id"] == "Skywork/Skywork-OR1-Math-7B" and r["effort"] == "default" for r in NEWROWS)
P(f"new 12 rows (all Skywork-OR1-Math-7B:default): matched to an old problem after whitespace normalisation "
  f"{sum(r['match'] for r in NEWROWS)}/12; templates " + " ".join(f"T{r['T']:02d}" for r in NEWROWS)
  + f"; own_text False: " + (", ".join(f"T{r['T']:02d}" for r in NEWROWS if not r["own_text"]) or "none"))
NEWL = [r for r in NEWROWS if r["y"] is not None]
P(f"new labelled rows {len(NEWL)} (robust {sum(r['y'] == 0 for r in NEWL)}, NR {sum(r['y'] == 1 for r in NEWL)}); null rows "
  + ", ".join(f"T{r['T']:02d} (max_drop {r['max_drop']:+.2f})" for r in NEWROWS if r["y"] is None))
assert len(NEWL) == 9 and sum(r["y"] for r in NEWL) == 2

# ================================================================ fit data D80
D71, FIT = G.build_fit_data()
assert [(a, b) for a, b in zip(D71.model_id, D71.effort)] == [(r["model_id"], r["effort"]) for r in cal if r["label"] is not None]
assert list(D71.y) == [r["label"] for r in cal if r["label"] is not None]
tfeat = D71.drop_duplicates("T").set_index("T")
add = []
for r in NEWL:
    add.append(dict(model_id=r["model_id"], effort=r["effort"], stem=tfeat.loc[r["T"], "stem"], text=texts[r["T"] - 1], label=r["y"],
                    max_drop=r["max_drop"], y=r["y"], T=r["T"], cfg="Skywork", strength=1.0,
                    pair16=float(tfeat.loc[r["T"], "pair16"]), qfin=float(tfeat.loc[r["T"], "qfin"]), new=True))
D80 = pd.concat([D71.assign(new=False), pd.DataFrame(add)], ignore_index=True)
D80["T"] = D80["T"].astype(int)
D80["y"] = D80["y"].astype(int)
y = D80.y.values
Tr = D80["T"].values
cfg = D80.cfg.values
isnew = D80.new.values.astype(bool)
sky = cfg == "Skywork"
old3 = sky & ~isnew
new9 = sky & isnew
nr2 = new9 & (y == 1)
P(f"D80: {len(D80)} rows (robust {int((y == 0).sum())}, NR {int((y == 1).sum())}), templates {len(np.unique(Tr))}; Skywork rows "
  f"{int(sky.sum())} (old {int(old3.sum())}: " + " ".join(f"T{t:02d}" for t in Tr[old3]) + f"; new {int(new9.sum())})")

# ================================================================ reads
pool, _base = G.parse_dress()
HELD = [("runs/v10_main_961407.log", "oss_low_r3", "runs/v10_main_961407.log", "qwen_quick_r2"),
        ("runs/v10_main_961407.log", "oss_low_r4", "runs/v10_main_961407.log", "qwen_quick_r2"),
        ("runs/v12_main_961488.log", "oss_low_m1", "runs/v12_main_961488.log", "qwen_quick_m"),
        ("runs/v12_main_961488.log", "oss_low_m2", "runs/v12_main_961488.log", "qwen_quick_m")]
READS = {"dress 987666": pool}
for ll, li, ql, qi in HELD:
    READS[f"{li}+{qi}"] = G.held_reads(ll, li, ql, qi)
v124 = PC.parse(F_V124)
for rid in V124_READS:
    Rd = v124[rid]
    assert Rd.complete() and not any(Rd.templates[T]["invalid"] for T in Rd.templates)
    READS[f"v124r {rid}+dress qfin"] = {T: dict(prim=float(Rd.templates[T]["pair_nat"]), qfin=pool[T]["qfin"], sky=pool[T]["sky"],
                                               olmo=pool[T]["olmo"]) for T in range(1, 29)}
RNAMES = list(READS)
LANEG5 = RNAMES[:5]
FRESH3 = RNAMES[5:]
q_r2 = READS["oss_low_r3+qwen_quick_r2"]
q_m = READS["oss_low_m1+qwen_quick_m"]
SENS = {}
for rid in V124_READS:
    for qn, qsrc in (("qwen_quick_r2", q_r2), ("qwen_quick_m", q_m)):
        SENS[f"v124r {rid}+{qn}"] = {T: dict(prim=float(v124[rid].templates[T]["pair_nat"]), qfin=qsrc[T]["qfin"], sky=None, olmo=None)
                                     for T in range(1, 29)}

# own run v37 through own_q1q2.py's parser (functions canon + parse extracted with ast; nothing else of that script runs)
src = open(W("miners12", "review", "own_q1q2.py")).read()
ns = {"re": re, "np": np}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("canon", "parse"):
        exec(compile(ast.Module(body=[node], type_ignores=[]), "own_q1q2.py", "exec"), ns)
sky37 = ns["parse"](F_V37, r"full_skywork_[abc]")
assert len(sky37) == 28 and all(len(v) == 3 for v in sky37.values())
gg = {}
for p in ("full_skywork_a", "full_skywork_b", "full_skywork_c"):
    for T, a in G.grab("runs/v37_small_968679.log", p).items():
        gg.setdefault(T, []).extend(a)
same_nk = all([(n, k) for n, k, _g, _i in sky37[T]] == [(n, k) for n, k, _g in gg[T]] for T in range(1, 29))
same_ans = sum([g for _n, _k, g, _i in sky37[T]] == [g for _n, _k, g in gg[T]] for T in range(1, 29))
OWN37 = {T: G.own_reading([(n, k, g) for n, k, g, _i in sky37[T]], 9000) for T in range(1, 29)}
same_held = all(OWN37[T] == READS[RNAMES[1]][T]["sky"] for T in range(1, 29))
kinds = sorted({k for T in sky37 for _n, k, _g, _i in sky37[T]})
P(f"\nv37 own run (own_q1q2 parse): 28 templates x 3 attempts; kinds {kinds}; (tokens, kind) identical to g_common.grab on "
  f"{'28/28' if same_nk else 'NOT ALL'} templates (answers {same_ans}/28); own readings = held_reads' sky on 28/28: {same_held}")
assert same_nk and same_held

# ================================================================ known-answer checks (machinery)
P("\n## known-answer checks (71 rows, lane G / lane CONF numbers)")
m_all = G.fit_models(D71, FIT, np.ones(len(D71), bool))
for k in ("full", "agreement_only", "finish_only"):
    assert np.allclose(m_all[k]["beta"], G.DEC[k]["beta"], atol=2e-4), k
P("refit on the 71 rows reproduces decision.json (three models, 2e-4): OK")
y71 = D71.y.values.astype(int)
EXPECT = {"dress 987666": 60, "oss_low_r3+qwen_quick_r2": 62, "oss_low_r4+qwen_quick_r2": 62, "oss_low_m1+qwen_quick_m": 61,
          "oss_low_m2+qwen_quick_m": 62}
for nm in RNAMES[:5]:
    got = int((G.run_policy(D71, FIT, READS[nm], G.V95, "loto") == y71).sum())
    P(f"   lane G: deployed policy LOTO on 71, {nm:34s} {got}/71 (expected {EXPECT[nm]}: {'OK' if got == EXPECT[nm] else 'FAIL'})")
    assert got == EXPECT[nm]
CONF_EXPECT = dict(zip(V124_READS, (62, 57, 62)))          # score_v124r_1004374.out 'baseline' (ADDENDUM R10)
for rid, nm in zip(V124_READS, FRESH3):
    Dc = D71.copy()
    Dc["pair16"] = Dc["T"].map(lambda T: float(v124[rid].templates[int(T)]["pair_nat"]))     # lane CONF: read's feature in training
    got_c = int((G.run_policy(Dc, FIT, READS[nm], G.V95, "loto") == y71).sum())
    got_g = int((G.run_policy(D71, FIT, READS[nm], G.V95, "loto") == y71).sum())
    P(f"   lane CONF form (training on the read's own pair_nat): {nm:30s} {got_c}/71 (expected {CONF_EXPECT[rid]}: "
      f"{'OK' if got_c == CONF_EXPECT[rid] else 'FAIL'}) | lane G machinery (training on fit-time pair16; used below): {got_g}/71")
    assert got_c == CONF_EXPECT[rid]

STAND = dict(high_prior=False, sky_own=False, olmo_own=False)


def T2(t):
    return f"T{t:02d}"


# ================================================================ Q1
P("\n" + "=" * 110)
P("## Q1 (DECISION): Skywork route - own run (v37, K 3 @ 9,000, robust iff >= 1 of 3 ended) vs stand-in, 12 labelled Skywork rows")
own = np.full(len(D80), -1)
for i in np.where(sky)[0]:
    c = G.own_call(OWN37[Tr[i]], 3, 1)
    own[i] = -9 if c is None else c
assert (own[sky] >= 0).all(), "a Skywork row without an own reading (would keep the stand-in)"
own_dr = np.full(len(D80), -1)
for i in np.where(sky)[0]:
    c = G.own_call(pool[Tr[i]]["sky"], 3, 1)
    own_dr[i] = -9 if c is None else c

calls = {}           # (scheme, read) -> calls on all 80 rows (stand-in on every row)
for nm in RNAMES + list(SENS):
    rd = READS.get(nm, SENS.get(nm))
    calls[("frozen", nm)] = G.run_policy(D80, FIT, rd, STAND, "shipped")
    calls[("loto80", nm)] = G.run_policy(D80, FIT, rd, STAND, "loto")

skyidx = [i for i in np.where(sky)[0]]
skyidx = sorted(skyidx, key=lambda i: (isnew[i], Tr[i]))
P("\nper row (R = robust, N = non-robust; stand-in calls in read order: " + ", ".join(f"{j + 1} = {nm}" for j, nm in enumerate(RNAMES)) + ")")
P(f"{'row':4s} {'T':3s} {'label':5s} {'drop':>6s} | {'v37 own (e/f/a)':16s} call | {'dress own':10s} call | {'stand-in frozen':16s} | {'stand-in LOTO-80':16s}")
for i in skyidx:
    P(f"{'new' if isnew[i] else 'old':4s} {T2(Tr[i])} {'NR' if y[i] else 'R':5s} {D80.max_drop[i]:+6.2f} | {str(OWN37[Tr[i]]):16s} {'N' if own[i] else 'R':4s} | "
      f"{str(pool[Tr[i]]['sky']):10s} {'N' if own_dr[i] else 'R':4s} | "
      f"{''.join('N' if calls[('frozen', nm)][i] else 'R' for nm in RNAMES):16s} | {''.join('N' if calls[('loto80', nm)][i] else 'R' for nm in RNAMES):16s}")


def cnt(yh, m):
    return int((yh == y)[m].sum())


SETS = (("new 9", new9), ("old 3", old3), ("new NR 2", nr2), ("all 12", sky))
P("\nrows right (plain counts): " + " | ".join(f"{s} n {int(m.sum())}" for s, m in SETS))
P(f"   {'always robust':52s} " + "  ".join(f"{s} {cnt(np.zeros(len(D80), int), m)}" for s, m in SETS))
P(f"   {'OWN RUN v37 (decision)':52s} " + "  ".join(f"{s} {cnt(own, m)}" for s, m in SETS))
P(f"   {'own run, dress read (information)':52s} " + "  ".join(f"{s} {cnt(own_dr, m)}" for s, m in SETS))
RES = {}
for sch in ("frozen", "loto80"):
    P(f"\n   stand-in, decision.json {'FROZEN (no refit)' if sch == 'frozen' else 'LOTO refit on 80 rows'}:")
    for nm in RNAMES:
        P(f"   {nm:52s} " + "  ".join(f"{s} {cnt(calls[(sch, nm)], m)}" for s, m in SETS))
    for lbl, group in (("POOLED 8 reads (mean)", RNAMES), ("lane G's 5 reads (mean)", LANEG5), ("3 fresh v124r reads (mean)", FRESH3)):
        v = {s: float(np.mean([cnt(calls[(sch, nm)], m) for nm in group])) for s, m in SETS}
        if lbl.startswith("POOLED"):
            RES[sch] = v
        P(f"   {lbl:52s} " + "  ".join(f"{s} {v[s]:.2f}" for s, _m in SETS))
    P("   sensitivity (information): v124r prims with a held Qwen quick finish instead of the dress qfin")
    for nm in SENS:
        P(f"   {nm:52s} " + "  ".join(f"{s} {cnt(calls[(sch, nm)], m)}" for s, m in SETS))
    alt = [n for n in RNAMES[:5]] + list(SENS)
    v = {s: float(np.mean([cnt(calls[(sch, nm)], m) for nm in alt])) for s, m in SETS}
    P(f"   {'pooled, 5 lane-G reads + 6 sensitivity pairings':52s} " + "  ".join(f"{s} {v[s]:.2f}" for s, _m in SETS))

P("\nDECISION RULE (PREREG; ADDENDUM R4-R5): SWITCH iff pooled stand-in - own >= 2 on the 9 new AND stand-in >= own on the 3 old "
  "AND >= own on the 2 new NR, under BOTH schemes")
ok_all = True
own_v = {s: cnt(own, m) for s, m in SETS}
for sch in ("frozen", "loto80"):
    v = RES[sch]
    c1 = v["new 9"] - own_v["new 9"] >= 2 - 1e-9
    c2 = v["old 3"] >= own_v["old 3"] - 1e-9
    c3 = v["new NR 2"] >= own_v["new NR 2"] - 1e-9
    ok_all &= c1 and c2 and c3
    P(f"   {sch:7s}: new 9 stand-in {v['new 9']:.2f} vs own {own_v['new 9']} -> diff {v['new 9'] - own_v['new 9']:+.2f} "
      f"({'>= 2 PASS' if c1 else '< 2 FAIL'}); old 3 {v['old 3']:.2f} vs {own_v['old 3']} ({'PASS' if c2 else 'FAIL'}); "
      f"new NR 2 {v['new NR 2']:.2f} vs {own_v['new NR 2']} ({'PASS' if c3 else 'FAIL'}) -> {'SWITCH' if (c1 and c2 and c3) else 'KEEP'}")
P(f"   DECISION: {'SWITCH the nominees Skywork route to the stand-in' if ok_all else 'KEEP the own run (rule not met)'}")
per_read_gap = {sch: [cnt(calls[(sch, nm)], new9) - own_v["new 9"] for nm in RNAMES] for sch in ("frozen", "loto80")}
P("   per-read stand-in minus own on the 9 new: " + " | ".join(f"{sch} " + " ".join(f"{d:+d}" for d in per_read_gap[sch]) for sch in per_read_gap))
P("   balanced accuracy on all 12 Skywork rows (always robust 0.500): own v37 "
  f"{G.bal(y[sky], own[sky]):.3f} | own dress read {G.bal(y[sky], own_dr[sky]):.3f} | stand-in mean over 8 reads frozen "
  f"{np.mean([G.bal(y[sky], calls[('frozen', nm)][sky]) for nm in RNAMES]):.3f}, LOTO-80 "
  f"{np.mean([G.bal(y[sky], calls[('loto80', nm)][sky]) for nm in RNAMES]):.3f}")
P("INFORMATION ONLY (not the pre-registered decision): the same rule with the own run read from the DRESS own read, and from the"
  " mean of the two own reads (v37, dress)")
for lbl, ov in (("own = dress read", {s: cnt(own_dr, m) for s, m in SETS}),
                ("own = mean(v37, dress)", {s: 0.5 * (cnt(own, m) + cnt(own_dr, m)) for s, m in SETS})):
    for sch in ("frozen", "loto80"):
        v = RES[sch]
        c1 = v["new 9"] - ov["new 9"] >= 2 - 1e-9
        c2 = v["old 3"] >= ov["old 3"] - 1e-9
        c3 = v["new NR 2"] >= ov["new NR 2"] - 1e-9
        P(f"   {lbl:24s} {sch:7s}: new 9 {v['new 9']:.2f} vs {ov['new 9']:.2f} ({v['new 9'] - ov['new 9']:+.2f}); old 3 {v['old 3']:.2f} vs "
          f"{ov['old 3']:.2f}; new NR 2 {v['new NR 2']:.2f} vs {ov['new NR 2']:.2f} -> {'SWITCH' if (c1 and c2 and c3) else 'KEEP'}")

# ================================================================ Q2
P("\n" + "=" * 110)
P("## Q2 (information): deployed policy (V95: high prior, Skywork own >= 1 of 3 @ 9,000, Olmo own >= 2 of 3 @ 10,000) LOTO on 80 rows")
P("   Skywork own readings: dress read -> dress own read; held reads -> v37; v124r reads -> dress own read (lane CONF pairing)")
P("   caveat: v115 / v121 stop the Olmo own run at 7,200 tokens; the Olmo readings here are at 10,000 (as in lane CONF)")
CFGS = G.CFGS
q2 = {}
z80 = np.zeros(len(D80), int)
P(f"   {'always robust':34s} all {cnt(z80, np.ones(len(D80), bool))}/80 | new 9 {cnt(z80, new9)} | old 71 {cnt(z80, ~isnew)} | bal 0.500 | "
  + " ".join(f"{c} {cnt(z80, cfg == c)}/{int((cfg == c).sum())}" for c in CFGS))
for nm in RNAMES:
    yh = G.run_policy(D80, FIT, READS[nm], G.V95, "loto")
    yh71 = G.run_policy(D71, FIT, READS[nm], G.V95, "loto")
    q2[nm] = yh
    P(f"   {nm:34s} all {cnt(yh, np.ones(len(D80), bool))}/80 | new 9 {cnt(yh, new9)} | old 71 {cnt(yh, ~isnew)} (LOTO-71: "
      f"{int((yh71 == y71).sum())}) | bal {G.bal(y, yh):.3f} | " + " ".join(f"{c} {cnt(yh, cfg == c)}/{int((cfg == c).sum())}" for c in CFGS))
m80 = {k: float(np.mean([cnt(q2[nm], m) for nm in RNAMES])) for k, m in (("all", np.ones(len(D80), bool)), ("new", new9), ("old", ~isnew))}
P(f"   {'POOLED 8 reads (mean)':34s} all {m80['all']:.2f}/80 = {m80['all'] / 80:.3f} | new 9 {m80['new']:.2f} | old 71 {m80['old']:.2f} | "
  f"bal {np.mean([G.bal(y, q2[nm]) for nm in RNAMES]):.3f} | "
  + " ".join(f"{c} {np.mean([cnt(q2[nm], cfg == c) for nm in RNAMES]):.2f}/{int((cfg == c).sum())}" for c in CFGS))
for lbl, group in (("lane G's 5 reads (mean)", LANEG5), ("3 fresh v124r reads (mean)", FRESH3)):
    P(f"   {lbl:34s} all {np.mean([cnt(q2[nm], np.ones(len(D80), bool)) for nm in group]):.2f}/80 | "
      f"new 9 {np.mean([cnt(q2[nm], new9) for nm in group]):.2f} | bal {np.mean([G.bal(y, q2[nm]) for nm in group]):.3f}")
P("   same policy with Skywork read by the stand-in (v113 / v114 route), LOTO-80, for comparison:")
q2s = {}
for nm in RNAMES:
    q2s[nm] = G.run_policy(D80, FIT, READS[nm], dict(G.V95, sky_own=False), "loto")
P(f"   {'POOLED 8 reads (mean)':34s} all {np.mean([cnt(q2s[nm], np.ones(len(D80), bool)) for nm in RNAMES]):.2f}/80 | "
  f"Skywork {np.mean([cnt(q2s[nm], sky) for nm in RNAMES]):.2f}/12 (own-run route {np.mean([cnt(q2[nm], sky) for nm in RNAMES]):.2f}/12) | "
  f"bal {np.mean([G.bal(y, q2s[nm]) for nm in RNAMES]):.3f}")
P("   rows wrong in >= 4 of 8 reads (deployed policy, LOTO-80): " + ", ".join(
    f"{T2(Tr[i])} {cfg[i]} {'NR' if y[i] else 'R'}{' (new)' if isnew[i] else ''} {sum(q2[nm][i] != y[i] for nm in RNAMES)}/8"
    for i in range(len(D80)) if sum(q2[nm][i] != y[i] for nm in RNAMES) >= 4))

# ================================================================ Q3
P("\n" + "=" * 110)
P("## Q3 (information): decision.json refitted on CLEAR-CUT rows only (max_drop <= 0.05 or >= 0.35), out-of-fold on all 80 rows")
cc = ((D80.max_drop.values <= 0.05) | (D80.max_drop.values >= 0.35))
assert (y[D80.max_drop.values >= 0.35] == 1).all() and (y[D80.max_drop.values <= 0.05] == 0).all()
P(f"clear-cut rows {int(cc.sum())}/80 (robust {int((cc & (y == 0)).sum())} of {int((y == 0).sum())}, NR {int((cc & (y == 1)).sum())} of "
  f"{int((y == 1).sum())}); left out of the fit: {int((~cc).sum())} rows (max_drop " + ", ".join(
      sorted({f'{v:+.2f}' for v in D80.max_drop.values[~cc]})) + ")")
splits = [((Tr != T0) & cc, Tr == T0) for T0 in np.unique(Tr)]
hp = sorted({int(y[tr & (cfg == 'high')].mean() > 0.5) for tr, _te in splits})
P(f"high prior over the 27 clear-cut folds: {['robust' if h == 0 else 'NR' for h in hp]}")
for nm_m, mask in (("clear-cut fit, all 80", cc), ("all-row fit, all 80", np.ones(len(D80), bool))):
    mm = G.fit_models(D80, FIT, mask)
    P(f"   coefficients {nm_m:22s} full {[round(float(b), 3) for b in mm['full']['beta']]} | agreement_only "
      f"{[round(float(b), 3) for b in mm['agreement_only']['beta']]}")
P(f"   coefficients {'decision.json (71 rows)':22s} full {[round(b, 3) for b in G.DEC['full']['beta']]} | agreement_only "
  f"{[round(b, 3) for b in G.DEC['agreement_only']['beta']]}")
fit_reads = {T: dict(prim=float(tfeat.loc[T, "pair16"]), qfin=float(tfeat.loc[T, "qfin"]), sky=None, olmo=None) for T in np.unique(Tr)}


def line(name, yh):
    return (f"   {name:52s} all {cnt(yh, np.ones(len(D80), bool))}/80 | new 9 {cnt(yh, new9)} | old 71 {cnt(yh, ~isnew)} | Skywork "
            f"{cnt(yh, sky)}/12 | bal {G.bal(y, yh):.3f}")


P("(a) stand-in on every row, fit-time reads (pair16, qfin):")
a_dep = G.run_policy(D80, FIT, fit_reads, STAND, "loto")
a_cc = G.run_policy(D80, FIT, fit_reads, STAND, "split", splits)
P(line("deployed fit procedure (all training rows), LOTO", a_dep))
P(line("clear-cut fit, out-of-fold", a_cc))
P("   changed rows: " + (", ".join(f"{T2(Tr[i])} {cfg[i]} {'NR' if y[i] else 'R'} drop {D80.max_drop[i]:+.2f}: "
                                  f"{'N' if a_dep[i] else 'R'} -> {'N' if a_cc[i] else 'R'} ({'fixes' if a_cc[i] == y[i] else 'breaks'})"
                                  for i in range(len(D80)) if a_dep[i] != a_cc[i]) or "none"))
P("(b) deployed policy (V95) per read: LOTO deployed fit vs clear-cut fit (rows right of 80; Skywork own run as in Q2)")
diffs = []
for nm in RNAMES:
    b_cc = G.run_policy(D80, FIT, READS[nm], G.V95, "split", splits)
    d = cnt(b_cc, np.ones(len(D80), bool)) - cnt(q2[nm], np.ones(len(D80), bool))
    diffs.append(d)
    P(f"   {nm:34s} deployed fit {cnt(q2[nm], np.ones(len(D80), bool))} -> clear-cut {cnt(b_cc, np.ones(len(D80), bool))} ({d:+d}); "
      f"bal {G.bal(y, q2[nm]):.3f} -> {G.bal(y, b_cc):.3f}; changed rows: " + (", ".join(
          f"{T2(Tr[i])} {cfg[i]} {'NR' if y[i] else 'R'} ({'fixes' if b_cc[i] == y[i] else 'breaks'})"
          for i in range(len(D80)) if b_cc[i] != q2[nm][i]) or "none"))
P(f"   pooled mean difference (clear-cut minus deployed fit): {np.mean(diffs):+.2f} rows of 80 (per read {' '.join(f'{d:+d}' for d in diffs)})")

open(os.path.join(HERE, "rows80.out"), "w").write("\n".join(OUT) + "\n")
