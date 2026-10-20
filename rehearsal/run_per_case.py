"""Mock of the organisers' PER-CASE evaluation harness (ledger 464-465): every case runs in its OWN fresh Python process,
one after another, on a shared job budget (4,200 s - 180 s safety margin = 4,020 s). A case whose time exceeds the budget
left times out (invalid) and every later case is skipped (invalid).

Each case: a fresh subprocess (this file with --child) imports the bundle copy's solution.py the way the ingestion does
and calls are_robust(model_id, reasoning_effort=effort, problems=[problem]). The bundle copy's engine2.py is
rehearsal/mock_engine2.py (virtual clock: starts at 0 in every process) plus a per-case calibration block appended below
(model loading and self-check costs per process, which the old single-process mock modelled only as 6 s / 3 s once per run).
The child reports its own elapsed VIRTUAL seconds; the parent adds MOCK_PROC_S per process (Python start, harness work).

Calibration (defaults; ledger 363, 365, 376, 465 and the coordinator's server timings of v65's per-case rerun 990657):
  gpt-oss-120b load 13 s + compacting check 4 s + fast decode path check 5 s  -> ready at ~22 s  (server: 17-22 s)
  gpt-oss low stand-in: 36 + 0.6 x 0.3 x rows ms/step, ALWAYS the full 3,000 steps (server: 40-45 ms/step, 1,238-3,000 steps
                        -> the mock's 125 s for K 32 is the server's slow end, 52-123 s)
  Qwen3.5-4B quick finish: load 3 s, 16 + 0.9 x rows ms/step (K 4: 19.6 ms/step, 2,000 steps = 39 s; server 38-40 s)
  7B own runs: load 15 s (unmeasured guess), fast-path check 8 s (unmeasured guess);
               fast path Skywork 20 + 0.2/row, Olmo 12 + 1.8/row (MOCK_FAST7_T, the bundle's planning values);
               default path Skywork 8 + 2.2/row (14.6 ms/step at 3 rows; server 14-15), Olmo 8 + 7.1/row (29 at 3; server 30)
  Process overhead 2 s per case (guess).
usage:
  python rehearsal/run_per_case.py --bundle sub_v114m --shape main [--seed 1] [--slow 1.4]
      [--budget 4020] [--budget-env NAME] [--no-budget] [--set key=json ...] [--mockenv K=V ...] [--log FILE]
  python rehearsal/run_per_case.py --suite [--out FILE]     (the comparison set of the v95 build)
shapes: main (21 cases in the board's order), small (14), final (30 problems x 7 configurations, configuration blocks in
harness order), final_mix (the same 210 cases, problem by problem)."""
import argparse, importlib.util, json, os, re, shutil, subprocess, sys, tempfile, time

W = os.path.dirname(os.path.abspath(__file__)); WORK = os.path.dirname(W)
PY = sys.executable
BASE_ENV = dict(MOCK_A="36", MOCK_B="0.3", MOCK_USED="0.6", MOCK_OWN="1", MOCK_FAST7="1",
                MOCK_FAST7_T="Skywork:20:0.2,Olmo:12:1.8", MOCK_OWN_T="Olmo:8:7.1,Skywork:8:2.2,Qwen:16:0.9",
                MOCK_LOAD_OSS="13", MOCK_LOAD_QWEN="3", MOCK_LOAD_7B="15", MOCK_FASTPATH_S="5", MOCK_FAST7_CHECK_S="8",
                MOCK_PROC_S="2")
CALIB_PATCH = '''

# ---- per-case calibration appended by rehearsal/run_per_case.py (exists only in the temporary bundle copy) ----
_LOAD_S = (float(os.environ.get("MOCK_LOAD_OSS", "13")), float(os.environ.get("MOCK_LOAD_QWEN", "3")),
           float(os.environ.get("MOCK_LOAD_7B", "15")))


def load(model_id):                                   # one model on the GPU at a time, as the real engine2.load
    if _LOADED[0] != model_id:
        _adv(_LOAD_S[0] if is_harmony(model_id) else _LOAD_S[1] if "qwen3.5" in model_id.lower() else _LOAD_S[2])
        _LOADED[0] = model_id
    return model_id, _Tok()


def enable_fastpath(model, tok, prompt_a, prompt_b, steps=64):
    _adv(float(os.environ.get("MOCK_FASTPATH_S", "5")))
    _FAST["on"] = True
    return True, "mock check"


_enable_fast7b_mock = enable_fast7b


def enable_fast7b(model, tok, model_id, prompt_a, prompt_b, **kw):
    _adv(float(os.environ.get("MOCK_FAST7_CHECK_S", "8")))
    return _enable_fast7b_mock(model, tok, model_id, prompt_a, prompt_b, **kw)
'''
CFG = {"Qwen": ("Qwen/Qwen3.5-4B", "default"), "Skywork": ("Skywork/Skywork-OR1-Math-7B", "default"),
       "Olmo": ("allenai/Olmo-3-7B-Think", "default"), "DeepSeek": ("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "default"),
       "high": ("openai/gpt-oss-120b", "high"), "low": ("openai/gpt-oss-120b", "low"), "medium": ("openai/gpt-oss-120b", "medium")}
ORDER7 = ["Qwen", "Skywork", "Olmo", "DeepSeek", "high", "low", "medium"]


def text(tag, i):
    return f"Synthetic problem {tag}-{i}: find the value of N for these parameters. " + "x" * 200


def shape(name, seed):
    """[(configuration, problem text)] in harness order."""
    if name == "main":      # ledger 464's order; problems shared across configurations as on the main board (16 problems)
        blocks = [("Qwen", [0, 1]), ("Skywork", [2, 3, 0]), ("Olmo", [4, 5]), ("DeepSeek", [6, 7, 2]), ("high", [8]),
                  ("low", [11, 12, 13]), ("medium", [15, 11]), ("high", [9]), ("low", [14]), ("medium", [12]), ("low", [4]),
                  ("high", [10])]
        return [(c, text(f"m{seed}", j)) for c, js in blocks for j in js]
    if name == "small":     # Qwen 5, Skywork 3, Olmo 3, DeepSeek 3 (10 problems)
        blocks = [("Qwen", [0, 1, 2, 3, 4]), ("Skywork", [5, 6, 0]), ("Olmo", [7, 8, 1]), ("DeepSeek", [9, 5, 2])]
        return [(c, text(f"s{seed}", j)) for c, js in blocks for j in js]
    if name in ("final", "final_mix"):
        P = [text(f"f{seed}", i) for i in range(30)]
        if name == "final":
            return [(c, p) for c in ORDER7 for p in P]
        return [(c, p) for p in P for c in ORDER7]
    raise SystemExit(f"unknown shape {name}")


def set_path(d, path, value):
    keys = path.split(".")
    for k in keys[:-1]:
        d = d[int(k)] if isinstance(d, list) else d[k]
    k = keys[-1]
    if isinstance(d, list):
        d[int(k)] = value
    else:
        d[k] = value


def prepare(bundle, sets):
    tmp = tempfile.mkdtemp(prefix="per_case_")
    sub = os.path.join(tmp, "sub")
    shutil.copytree(os.path.join(WORK, bundle), sub, ignore=shutil.ignore_patterns("__pycache__"))
    with open(os.path.join(W, "mock_engine2.py")) as f:
        mock = f.read()
    with open(os.path.join(sub, "engine2.py"), "w") as f:
        f.write(mock + CALIB_PATCH)
    if sets:
        p = os.path.join(sub, "params.json")
        d = json.load(open(p))
        for s in sets:
            k, v = s.split("=", 1)
            set_path(d, k, json.loads(v))
        json.dump(d, open(p, "w"), indent=1)
    return tmp, sub


def note_of(log):
    """Short note from the entry's own log lines (counts only)."""
    n = []
    if re.search(r"answered robust at once|answered from its public prior", log):
        n.append("prior")
    for name, kk, k3, k1 in re.findall(r"(own_\w+) (?:own run first|run to the end): new problems \d+, read \d+ \(K (\d+): (\d+), K 1: (\d+)\)", log):
        n.append(f"{name} K{kk if int(k3) else 1}")
    if re.search(r"own_\w+ (?:own run first|run to the end): (failed|new problems \d+, none read)", log):
        n.append("own: no reading")
    m = re.search(r"stand-in: (.*?), stand-in decision models", log)
    if m:
        k = re.search(r"K (\d+) \(planned (with|WITHOUT)", m.group(1))
        if k:
            n.append(f"oss K{k.group(1)}")
        elif "not needed" not in m.group(1):
            n.append("oss none")
        q = re.search(r"quick finish (\d+)/(\d+)", m.group(1))
        if q:
            n.append(f"qfin {q.group(1)}/{q.group(2)}")
        elif "quick finish skipped" in m.group(1):
            n.append("qfin skipped")
    m = re.search(r"call 1 \([^)]*\): \d+ cases, new problems \d+, K (\d+) .*?finish (\d+)/(\d+)", log)
    if m:
        n.append(f"oss K{m.group(1)} qfin {m.group(2)}/{m.group(3)}")
    if "fallback (" in log:
        n.append("FALLBACK")
    return ", ".join(n)


def run(bundle, shape_name, seed=1, slow=1.0, budget=4020.0, budget_env=None, no_budget=False, sets=(), mockenv=(),
        log_path=None, quiet=False, label=""):
    cases = shape(shape_name, seed)
    tmp, sub = prepare(bundle, sets)
    env0 = {k: v for k, v in os.environ.items() if not re.search(r"BUDGET|DEADLINE|TIMEOUT|REMAINING|^MOCK_", k, re.I)}
    env0.update(BASE_ENV, MOCK_SLOW=str(slow))
    env0.update(dict(kv.split("=", 1) for kv in mockenv))
    proc_s = float(env0.get("MOCK_PROC_S", "2"))
    out = [f"[ingestion] MOCK per-case harness: bundle={bundle} shape={shape_name} seed={seed} slow={slow}x cases={len(cases)} "
           f"job_budget_s={'none' if no_budget else f'{budget:.0f}'}{f' budget_env={budget_env}' if budget_env else ''}"
           f"{' sets=' + ';'.join(sets) if sets else ''}{' mockenv=' + ';'.join(mockenv) if mockenv else ''}"]
    if not quiet:
        print(out[0], flush=True)
    total, rows, logs, dead = 0.0, [], [], False
    for i, (c, prob) in enumerate(cases):
        model, effort = CFG[c]
        head = f"case {i + 1}/{len(cases)} id=c{i:04d} model={model} effort={effort}"
        left = budget - total
        if dead or (not no_budget and left <= 0):
            rows.append(dict(cfg=c, status="skipped", sec=0.0, pred=None))
            line = f"{head}: skipped (job budget exhausted)"
        else:
            cf = os.path.join(tmp, f"case{i:04d}.json")
            json.dump({"id": f"c{i:04d}", "model_id": model, "reasoning_effort": effort, "problem": prob}, open(cf, "w"))
            env = dict(env0)
            if budget_env:
                env[budget_env] = f"{left:.0f}"
            r = subprocess.run([PY, os.path.abspath(__file__), "--child", sub, cf], capture_output=True, text=True, env=env, cwd=tmp)
            m = re.search(r"^@@RESULT (.*)$", r.stdout, re.M)
            res = json.loads(m.group(1)) if m else dict(elapsed=0.0, valid=False, pred=None, err=f"child crashed: {r.stderr[-300:]}")
            sec = res["elapsed"] + proc_s
            log = r.stdout + r.stderr
            logs.append(f"===== {head}\n{log}")
            note = note_of(log)
            if not no_budget and sec > left:
                rows.append(dict(cfg=c, status="timeout", sec=left, pred=None, need=sec, note=note))
                line = f"{head}: TIMED OUT after {left:.0f}s (budget {left:.0f}s; would have needed {sec:.0f}s) [{note}]"
                total, dead = budget, True
            else:
                st = "ok" if res["valid"] else "INVALID"
                rows.append(dict(cfg=c, status=st, sec=sec, pred=res["pred"], note=note))
                line = f"{head}: {st} in {sec:.1f}s (budget {left:.0f}s) [{note}]{'' if res['valid'] else ' ' + res.get('err', '')}"
                total += sec
        out.append(line)
        if not quiet:
            print(line, flush=True)
    inv = sum(1 for r in rows if r["status"] != "ok")
    to = sum(1 for r in rows if r["status"] == "timeout")
    sk = sum(1 for r in rows if r["status"] == "skipped")
    stats = {}
    for r in rows:
        if r["status"] == "ok":
            stats.setdefault(r["cfg"], []).append(r["sec"])
    per = "; ".join(f"{c} {len(v)}x {min(v):.0f}-{max(v):.0f}s (mean {sum(v) / len(v):.0f})" for c, v in
                    sorted(stats.items(), key=lambda kv: ORDER7.index(kv[0])))
    summ = (f"done: cases {len(cases)}, ok {len(cases) - inv}, invalid {inv}, timeouts {to}, skipped {sk}, "
            f"elapsed {total:.0f} s{'' if no_budget else f' of {budget:.0f} s'} | per configuration: {per}")
    out.append(summ)
    if not quiet:
        print(summ, flush=True)
    if log_path:
        with open(log_path, "a") as f:
            f.write("\n".join(out) + "\n" + "\n".join(logs) + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    return dict(label=label, bundle=bundle, shape=shape_name, rows=rows, total=total, invalid=inv, timeouts=to, skipped=sk,
                lines=out, ok=len(cases) - inv, stats=stats)


def child(sub, case_file):
    t0 = time.time()                                  # the mock engine patches time.time on import, offset starting at 0
    case = json.load(open(case_file))
    sys.path.insert(0, sub)
    res, valid, err = None, False, ""
    try:
        spec = importlib.util.spec_from_file_location("participant_solution", os.path.join(sub, "solution.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        res = mod.are_robust(case["model_id"], reasoning_effort=case["reasoning_effort"], problems=[case["problem"]])
        valid = type(res) is list and len(res) == 1 and all(type(x) is bool for x in res)
    except Exception as exc:
        err = f"{type(exc).__name__}: {str(exc)[:200]}"
    print("@@RESULT " + json.dumps(dict(elapsed=time.time() - t0, valid=valid, pred=res if valid else None, err=err)), flush=True)


def suite(out_path=None, log_path=None):
    """The comparison set of the v95 build: v95 (sub_v114m / sub_v115s) vs v83 (sub_v101m / its small twin sub_v102s)."""
    R, txt = [], []

    def go(label, bundle, shp, **kw):
        r = run(bundle, shp, quiet=True, label=label, log_path=log_path, **kw)
        R.append(r)
        txt.append(f"\n##### {label}\n" + "\n".join(r["lines"]))
        print(f"{label:62s} ok {r['ok']:3d}/{len(r['rows']):3d} timeouts {r['timeouts']} skipped {r['skipped']:3d} "
              f"elapsed {r['total']:6.0f} s", flush=True)
        return r
    pairs = []
    for seed in (1, 2):
        for slow in (1.0, 1.4):
            a = go(f"main seed {seed} {slow}x  v95 sub_v114m", "sub_v114m", "main", seed=seed, slow=slow)
            b = go(f"main seed {seed} {slow}x  v83 sub_v101m", "sub_v101m", "main", seed=seed, slow=slow)
            pairs.append((a, b))
            a = go(f"small seed {seed} {slow}x v96 sub_v115s", "sub_v115s", "small", seed=seed, slow=slow)
            b = go(f"small seed {seed} {slow}x v84 sub_v102s (v83 small twin)", "sub_v102s", "small", seed=seed, slow=slow)
            pairs.append((a, b))
    for shp in ("final", "final_mix"):
        go(f"{shp} 210 cases 1.0x v95 sub_v114m", "sub_v114m", shp)
        go(f"{shp} 210 cases 1.0x v83 sub_v101m", "sub_v101m", shp)
    go("final 210, NO budget (time to answer all) v95", "sub_v114m", "final", no_budget=True)
    go("final 210, NO budget (time to answer all) v83", "sub_v101m", "final", no_budget=True)
    # sensitivity (v95, main seed 1, 1.0x)
    go("SENS main: Olmo fast path at the board-measured speed (23.4+1.1/row)", "sub_v114m", "main",
       mockenv=("MOCK_FAST7_T=Skywork:20:0.2,Olmo:23.4:1.1",))
    go("SENS main: Skywork default path (owns.0.fast7b=false)", "sub_v114m", "main", sets=("owns.0.fast7b=false",))
    go("SENS main: both fast-path checks FAIL (default paths)", "sub_v114m", "main", mockenv=("MOCK_FAST7=0",))
    go("SENS main: 7B load 40 s, gpt-oss load 30 s", "sub_v114m", "main", mockenv=("MOCK_LOAD_7B=40", "MOCK_LOAD_OSS=30"))
    go("SENS main: tight job budget 2,500 s, no budget env", "sub_v114m", "main", budget=2500.0)
    go("SENS main: tight job budget 2,500 s, budget env CASE_BUDGET_S", "sub_v114m", "main", budget=2500.0,
       budget_env="CASE_BUDGET_S")
    go("SENS main: case_target_seconds 240", "sub_v114m", "main", sets=("case_target_seconds=240",))
    # rule check: with no time limit v95 must give v83's answers case by case (same readings, seeds and K)
    for shp, b95, b83 in (("main", "sub_v114m", "sub_v101m"), ("small", "sub_v115s", "sub_v102s")):
        for seed in (1, 2):
            a = go(f"RULE {shp} seed {seed}: v95 with targets 100000 s", b95, shp, seed=seed, no_budget=True,
                   sets=("case_target_seconds=100000", "own_case_target_seconds=100000"))
            b = go(f"RULE {shp} seed {seed}: v83", b83, shp, seed=seed, no_budget=True)
            same = sum(1 for x, y in zip(a["rows"], b["rows"]) if x["pred"] == y["pred"] and x["pred"] is not None)
            msg = f"RULE CHECK {shp} seed {seed}: identical answers {same}/{len(a['rows'])}"
            diff = [f"{i + 1}:{x['cfg']} v95 {x['pred']} v83 {y['pred']}" for i, (x, y) in enumerate(zip(a["rows"], b["rows"]))
                    if x["pred"] != y["pred"]]
            txt.append(msg + (" | differ: " + "; ".join(diff) if diff else ""))
            print(txt[-1], flush=True)
    if out_path:
        with open(out_path, "w") as f:
            f.write("\n".join(txt) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[3])
        sys.exit(0)
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default="sub_v114m")
    ap.add_argument("--shape", default="main")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--slow", type=float, default=1.0)
    ap.add_argument("--budget", type=float, default=4020.0)
    ap.add_argument("--budget-env", default=None)
    ap.add_argument("--no-budget", action="store_true")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--mockenv", action="append", default=[])
    ap.add_argument("--log", default=None)
    ap.add_argument("--suite", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.suite:
        suite(a.out, a.log)
    else:
        run(a.bundle, a.shape, a.seed, a.slow, a.budget, a.budget_env, a.no_budget, a.set, a.mockenv, a.log)
