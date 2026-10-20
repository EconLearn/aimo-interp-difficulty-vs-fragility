"""CRP17 lane F: final-shape risk of the per-case entries (v95 main = sub_v114m, v96 small = sub_v115s) and variants.

OFFLINE mock only. It reuses rehearsal/run_per_case.py (fresh process per case, virtual clock, server-calibrated costs) and
inspects nothing but the entry's own printed lines. Because a case process keeps no state between cases and (in the mock,
as on the server: ledger 484 / 492) receives no budget information, a case's time and answer depend only on (configuration,
problem text, speed). So every case is run ONCE per (bundle, configuration, problem, speed) and any job layout is then
simulated exactly from that table with the harness rules seen in our own logs (ledger 464, 492):
  - cases run one after another on a shared job budget (4,200 s - 180 s margin = 4,020 s);
  - a case whose time exceeds the budget left times out (invalid) and every later case is skipped (invalid).
Layouts: one job; the job budget scaled per case (board ratio: main 4,020/21 s, small 4,020/14 s per case); several board-size
jobs (21 main / 14 small cases per 4,020 s job); and, as a sensitivity, a per-case timeout at the board ratio.
Expected accuracy: an answered case scores the public-row accuracy of its configuration (v95 line, 61/71; CRP_FRAME17) when
it was decided by a full reading (own run, agreement + quick finish, or agreement only: equal leave-one-template-out
accuracy, decision.json), or the configuration's public robust base rate when it was answered by the prior or by the quick
finish alone (finish_only LOTO 0.73 = base rate). An unanswered case scores 0 (invalid) or 0.5 (chance), both reported.

usage: python rehearsal/final_shape/shapes_mock.py table  BUNDLE TRACK OUT.json [--speeds 1.0,1.4] [--n 50]
                                                                      [--set k=json ...] [--small]
       python rehearsal/final_shape/shapes_mock.py report TABLE.json [TABLE.json ...]
"""
import argparse, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(WORK, "rehearsal"))
import run_per_case as R  # noqa: E402

MAIN7 = ["Qwen", "Skywork", "Olmo", "DeepSeek", "high", "low", "medium"]
SMALL4 = ["Qwen", "Skywork", "Olmo", "DeepSeek"]
# public labelled rows (calib.json labels; v95-line answers from CRP_FRAME17): accuracy and robust base rate per configuration
ACC = {"Qwen": 11 / 12, "Skywork": 1 / 3, "Olmo": 8 / 9, "DeepSeek": 8 / 10, "high": 13 / 15, "low": 6 / 7, "medium": 14 / 15}
BASE = {"Qwen": 8 / 12, "Skywork": 2 / 3, "Olmo": 7 / 9, "DeepSeek": 7 / 10, "high": 13 / 15, "low": 5 / 7, "medium": 10 / 15}
FULL_KINDS = ("own", "full", "agr")


def kind_of(log, cfg):
    if re.search(r"answered robust at once|answered from its public prior", log):
        return "prior"
    if "fallback (" in log:
        return "fallback"
    m = re.search(r"combined by '\w+': cases with a reading (\d+)/", log)
    if m and int(m.group(1)) > 0:
        return "own"
    m = re.search(r"stand-in decision models \{([^}]*)\}", log)
    if m:
        k = m.group(1)
        for key, short in (("'full'", "full"), ("'agreement_only'", "agr"), ("'finish_only'", "fin"), ("'none'", "none")):
            if key in k:
                return short
    return "unknown"


def one_case(sub, tmp, env, cfg, text, tag):
    model, effort = R.CFG[cfg]
    cf = os.path.join(tmp, f"case_{tag}.json")
    with open(cf, "w") as f:
        json.dump({"id": tag, "model_id": model, "reasoning_effort": effort, "problem": text}, f)
    r = subprocess.run([R.PY, R.__file__, "--child", sub, cf], capture_output=True, text=True, env=env, cwd=tmp)
    m = re.search(r"^@@RESULT (.*)$", r.stdout, re.M)
    res = json.loads(m.group(1)) if m else dict(elapsed=0.0, valid=False, pred=None, err="crash " + r.stderr[-200:])
    log = r.stdout + r.stderr
    return dict(cfg=cfg, sec=round(res["elapsed"] + float(env.get("MOCK_PROC_S", "2")), 2), valid=res["valid"],
                pred=res["pred"][0] if res["valid"] else None, kind=kind_of(log, cfg), note=R.note_of(log),
                qfin_moot=bool(re.search(r"quick finish moot", log)), cut="(cut by clock)" in log)


def problem_texts(n):
    """Synthetic problems: the board layouts' texts (seeds 1, 2) and n 'new' problems shared by all configurations."""
    t = {}
    for seed in (1, 2):
        for c, p in R.shape("main", seed) + R.shape("small", seed):
            t.setdefault(p, None)
    for i in range(n):
        t.setdefault(R.text("NEW", i), None)
    return list(t)


def table(bundle, track, out, speeds, n, sets, mockenv, workers=8):
    tmp, sub = R.prepare(bundle, sets)
    env0 = {k: v for k, v in os.environ.items() if not re.search(r"BUDGET|DEADLINE|TIMEOUT|REMAINING|^MOCK_", k, re.I)}
    env0.update(R.BASE_ENV)
    env0.update(dict(kv.split("=", 1) for kv in mockenv))
    cfgs = MAIN7 if track == "main" else SMALL4
    texts = problem_texts(n)
    jobs = []
    for sp in speeds:
        env = dict(env0, MOCK_SLOW=str(sp))
        for c in cfgs:
            for j, p in enumerate(texts):
                jobs.append((sp, c, p, env, f"{sp}_{c}_{j}"))
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(lambda a: (a[0], a[1], a[2], one_case(sub, tmp, a[3], a[1], a[2], a[4])), jobs))
    T = {"bundle": bundle, "track": track, "sets": list(sets), "mockenv": list(mockenv), "speeds": speeds, "n_new": n, "cases": {}}
    for sp, c, p, r in res:
        T["cases"][f"{sp}|{c}|{p}"] = r
    with open(out, "w") as f:
        json.dump(T, f)
    print(f"wrote {out}: {len(res)} case runs", flush=True)
    return T


# ---------------------------------------------------------------------------------------------------------- layouts
def layout(track, kind, n, seed=1):
    """[(configuration, problem text)] in harness order."""
    if kind == "board":
        return R.shape("main" if track == "main" else "small", seed)
    P = [R.text("NEW", i) for i in range(n)]
    cfgs = MAIN7 if track == "main" else SMALL4
    if kind == "blocked":                      # all problems of a configuration, configurations in harness order
        return [(c, p) for c in cfgs for p in P]
    if kind == "interleaved":                  # problem by problem
        return [(c, p) for p in P for c in cfgs]
    if kind == "boardlike":                    # the board's habit: 7B / 4B models in blocks, then gpt-oss efforts per problem
        out = [(c, p) for c in cfgs if c not in ("high", "low", "medium") for p in P]
        return out + [(c, p) for p in P for c in cfgs if c in ("high", "low", "medium")]
    raise ValueError(kind)


def simulate(T, cases, speed, mode, track, case_cap=None):
    """mode: one | scaled | jobs | casecap (per-case timeout case_cap, default the board ratio, inside a scaled job budget).
    Returns per-case statuses and summary numbers."""
    per = 4020.0 / (21 if track == "main" else 14)
    cap = case_cap or per
    size = 21 if track == "main" else 14
    recs = [T["cases"][f"{speed}|{c}|{p}"] for c, p in cases]
    status = []
    if mode == "jobs":
        chunks = [list(range(i, min(i + size, len(cases)))) for i in range(0, len(cases), size)]
        budgets = [4020.0] * len(chunks)
    else:
        chunks = [list(range(len(cases)))]
        budgets = [4020.0 if mode == "one" else per * len(cases)]
    status = [None] * len(cases)
    used_total = 0.0
    for idx, B in zip(chunks, budgets):
        used, dead = 0.0, False
        for i in idx:
            r = recs[i]
            left = B - used
            if dead or left <= 0:
                status[i] = "skipped"
                continue
            limit = min(left, cap) if mode == "casecap" else left
            if r["sec"] > limit:
                status[i] = "timeout"
                used += limit
                if limit >= left:
                    dead = True
                continue
            status[i] = "ok" if r["valid"] else "invalid"
            used += r["sec"]
        used_total += used
    ok = [i for i, s in enumerate(status) if s == "ok"]
    n = len(cases)
    exp_ok = sum(ACC[recs[i]["cfg"]] if recs[i]["kind"] in FULL_KINDS else BASE[recs[i]["cfg"]] for i in ok)
    n_un = n - len(ok)
    degraded = sum(1 for i in ok if recs[i]["kind"] not in FULL_KINDS + ("prior",))
    cut = sum(1 for i in ok if recs[i].get("cut"))
    return dict(n=n, ok=len(ok), timeouts=status.count("timeout"), skipped=status.count("skipped"),
                invalid=n_un, acc_invalid0=exp_ok / n, acc_chance=(exp_ok + 0.5 * n_un) / n, degraded=degraded, cut=cut,
                used=used_total, preds=[recs[i]["pred"] if status[i] == "ok" else None for i in range(n)],
                kinds=[recs[i]["kind"] for i in range(n)])


def full_acc(track, cases):
    """Expected accuracy if every case were answered with a full reading (the ceiling of the layout)."""
    return sum(ACC[c] for c, _ in cases) / len(cases)


def report(paths, ns=(16, 30, 50), out=None):
    lines = []
    for path in paths:
        T = json.load(open(path))
        tr = T["track"]
        lines.append(f"\n### {T['bundle']} ({tr}) sets={T['sets']} mockenv={T['mockenv']}")
        lines.append("| layout | cases | budget mode | speed | answered | timeouts | skipped | degraded | exp. acc (invalid=0) | "
                     "exp. acc (unanswered=0.5) | ceiling | job time used s |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for sp in T["speeds"]:
            for seed in (1, 2):
                cs = layout(tr, "board", 0, seed)
                s = simulate(T, cs, sp, "one", tr)
                lines.append(f"| board seed {seed} | {s['n']} | one 4,020 s | {sp}x | {s['ok']} | {s['timeouts']} | {s['skipped']} | "
                             f"{s['degraded']} | {s['acc_invalid0']:.3f} | {s['acc_chance']:.3f} | {full_acc(tr, cs):.3f} | {s['used']:.0f} |")
        for n in ns:
            for lk in (("blocked", "interleaved", "boardlike") if tr == "main" else ("blocked", "interleaved")):
                cs = layout(tr, lk, n)
                for mode in ("one", "scaled", "jobs", "casecap"):
                    for sp in T["speeds"]:
                        s = simulate(T, cs, sp, mode, tr)
                        lines.append(f"| {n} new x {len(MAIN7) if tr == 'main' else 4} {lk} | {s['n']} | {mode} | {sp}x | {s['ok']} | "
                                     f"{s['timeouts']} | {s['skipped']} | {s['degraded']} | {s['acc_invalid0']:.3f} | "
                                     f"{s['acc_chance']:.3f} | {full_acc(tr, cs):.3f} | {s['used']:.0f} |")
        # per-configuration case times
        lines.append("\nper-configuration case seconds (min / mean / max over all synthetic problems) and decision kinds:")
        for sp in T["speeds"]:
            by = {}
            for k, r in T["cases"].items():
                s, c, _ = k.split("|", 2)
                if float(s) != float(sp):
                    continue
                by.setdefault(c, []).append(r)
            parts = []
            for c in (MAIN7 if tr == "main" else SMALL4):
                v = by.get(c, [])
                if not v:
                    continue
                secs = [r["sec"] for r in v]
                kinds = {}
                for r in v:
                    kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
                moot = sum(r.get("qfin_moot", False) for r in v)
                parts.append(f"{c} {min(secs):.0f}/{sum(secs) / len(secs):.0f}/{max(secs):.0f} {kinds}"
                             + (f" qfin-moot {moot}/{len(v)}" if moot else ""))
            lines.append(f"- {sp}x: " + "; ".join(parts))
    txt = "\n".join(lines)
    print(txt)
    if out:
        with open(out, "w") as f:
            f.write(txt + "\n")


def compare(a_path, b_path):
    """Case-by-case answers of two tables (same speeds / texts): identical answers on every board case and new case."""
    A, B = json.load(open(a_path)), json.load(open(b_path))
    keys = sorted(set(A["cases"]) & set(B["cases"]))
    diff = [k for k in keys if A["cases"][k]["pred"] != B["cases"][k]["pred"] or A["cases"][k]["valid"] != B["cases"][k]["valid"]]
    print(f"{a_path} vs {b_path}: {len(keys)} common case runs, answers differ on {len(diff)}")
    for k in diff[:20]:
        print("  ", k[:60], A["cases"][k]["pred"], B["cases"][k]["pred"], A["cases"][k]["note"], "|", B["cases"][k]["note"])
    # board layouts specifically (speeds present in both tables)
    for sp in [x for x in A["speeds"] if x in B["speeds"]]:
        for seed in (1, 2):
            tr = A["track"]
            cs = layout(tr, "board", 0, seed)
            sa, sb = simulate(A, cs, sp, "one", tr), simulate(B, cs, sp, "one", tr)
            same = sum(1 for x, y in zip(sa["preds"], sb["preds"]) if x == y and x is not None)
            print(f"   board seed {seed} {sp}x: identical answered {same}/{len(cs)}; A ok {sa['ok']} used {sa['used']:.0f} s, "
                  f"B ok {sb['ok']} used {sb['used']:.0f} s")
    return len(diff)



# ---------------------------------------------------------------------------------------------------------- compact summary
def key_shapes(track):
    """(label, layout kind, n new problems, budget mode, per-case timeout)"""
    if track == "main":
        return [("board 21 cases, one 4,020 s job (EXPECTED)", "board", 0, "one", None),
                ("16 new x 7 = 112, one job, blocked", "blocked", 16, "one", None),
                ("16 new x 7 = 112, one job, interleaved", "interleaved", 16, "one", None),
                ("30 new x 7 = 210, one job, blocked", "blocked", 30, "one", None),
                ("50 new x 7 = 350, one job, blocked", "blocked", 50, "one", None),
                ("30 x 7, job budget scaled 191 s/case", "blocked", 30, "scaled", None),
                ("30 x 7, 21-case jobs, blocked", "blocked", 30, "jobs", None),
                ("30 x 7, 21-case jobs, interleaved", "interleaved", 30, "jobs", None),
                ("30 x 7, 21-case jobs, board-like", "boardlike", 30, "jobs", None),
                ("30 x 7, per-case timeout 191 s", "interleaved", 30, "casecap", 4020.0 / 21),
                ("30 x 7, per-case timeout 300 s", "interleaved", 30, "casecap", 300.0)]
    return [("board 14 cases, one 4,020 s job (EXPECTED)", "board", 0, "one", None),
            ("16 new x 4 = 64, one job, blocked", "blocked", 16, "one", None),
            ("16 new x 4 = 64, one job, interleaved", "interleaved", 16, "one", None),
            ("30 new x 4 = 120, one job, blocked", "blocked", 30, "one", None),
            ("50 new x 4 = 200, one job, blocked", "blocked", 50, "one", None),
            ("30 x 4, job budget scaled 287 s/case", "blocked", 30, "scaled", None),
            ("30 x 4, 14-case jobs, blocked", "blocked", 30, "jobs", None),
            ("30 x 4, 14-case jobs, interleaved", "interleaved", 30, "jobs", None),
            ("30 x 4, per-case timeout 191 s", "interleaved", 30, "casecap", 4020.0 / 21),
            ("30 x 4, per-case timeout 287 s", "interleaved", 30, "casecap", 4020.0 / 14)]


def summary(paths, speeds=(1.0, 1.4), out=None, names=None):
    Ts = [json.load(open(p)) for p in paths]
    names = names or [os.path.basename(p) for p in paths]
    tr = Ts[0]["track"]
    lines = [f"| shape ({tr}) | speed | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(Ts)]
    for lab, lk, n, mode, cc in key_shapes(tr):
        cs = layout(tr, lk, n)
        for sp in speeds:
            cells = []
            for T in Ts:
                s = simulate(T, cs, sp, mode, tr, cc)
                cells.append(f"{s['ok']}/{s['n']} ans, {s['invalid']} inv, acc {s['acc_invalid0']:.3f} ({s['acc_chance']:.3f})"
                             + (f", {s['cut']} cut" if s['cut'] else "") + (f", {s['degraded']} weak" if s['degraded'] else "")
                             + (f", {s['used']:.0f} s" if lk == "board" else ""))
            lines.append(f"| {lab} | {sp}x | " + " | ".join(cells) + " |")
    txt = "\n".join(lines)
    print(txt)
    if out:
        with open(out, "a") as f:
            f.write(txt + "\n\n")
    return txt


def crossover(paths, speeds=(1.0, 1.4), sizes=(14, 21, 24, 28, 35, 42, 56, 84, 112, 210, 350), out=None, names=None):
    """One 4,020 s job holding the first `size` cases of the interleaved new-problem layout: expected accuracy per table."""
    Ts = [json.load(open(p)) for p in paths]
    names = names or [os.path.basename(p) for p in paths]
    tr = Ts[0]["track"]
    full = layout(tr, "interleaved", 50)
    lines = [f"| cases in ONE 4,020 s job ({tr}, interleaved new problems) | speed | " + " | ".join(names) + " |",
             "|---|---|" + "---|" * len(Ts)]
    for n in sizes:
        cs = full[:n]
        for sp in speeds:
            cells = []
            for T in Ts:
                s = simulate(T, cs, sp, "one", tr)
                cells.append(f"{s['ok']}/{n}, {s['acc_invalid0']:.3f}")
            lines.append(f"| {n} | {sp}x | " + " | ".join(cells) + " |")
    txt = "\n".join(lines)
    print(txt)
    if out:
        with open(out, "a") as f:
            f.write(txt + "\n\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--speeds", default="1.0,1.4")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--mockenv", action="append", default=[])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.cmd == "table":
        table(a.args[0], a.args[1], a.args[2], [float(x) for x in a.speeds.split(",")], a.n, a.set, a.mockenv)
    elif a.cmd == "report":
        report(a.args, out=a.out)
    elif a.cmd == "compare":
        compare(a.args[0], a.args[1])
    elif a.cmd == "summary":
        summary(a.args, [float(x) for x in a.speeds.split(",")], a.out)
    elif a.cmd == "crossover":
        crossover(a.args, [float(x) for x in a.speeds.split(",")], out=a.out)
