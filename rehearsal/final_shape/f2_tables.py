"""Lane F2 (final at N x 170 s): per-case tables for the six bundles at speeds 1.0 / 1.2 / 1.4 / 1.6 (mock), OFFLINE.

Reuses lane F's machinery unchanged (miners17/laneF/shapes_mock.py: one case per (bundle, configuration, problem text,
speed) in a fresh process of the per-case mock, rehearsal/run_per_case.py). A case process keeps no state and receives no
budget, so any job layout is then simulated exactly from the table (f2_sim.py).

STD bundles (v107 = sub_v125m, v100 = sub_v119m, v108 = sub_v126s, v101 = sub_v120s) use the STD mock of ledger 494 / 531
(scratch copies run_per_case_v100.py + mock_engine2_v100.py in scratchpad/v125_mock, MOCK_STD_PROGS = lane L programs).
Their tables hold, besides the usual texts (board + 50 synthetic NEW problems: STD finds no usable code -> fallback), the
15 PUBLIC templates that have a lane L program, for Skywork / Olmo only (STD validated path).

usage: python rehearsal/final_shape/f2_tables.py BUNDLE TRACK OUT.json [--std] [--speeds 1.0,1.2,1.4,1.6]
                                                              [--set k=json ...] [--workers 6]
"""
import argparse, importlib.util, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)                                  # release copy: shapes_mock.py sits next to this file
import shapes_mock as SM  # noqa: E402

# release copy: the STD mock and its programs are not part of this release (--std does not run here)
SCR = os.path.join(HERE, "std_mock_not_released")
STD_HARNESS = os.path.join(SCR, "v125_mock", "run_per_case_v100.py")
PROGS = os.path.join(SCR, "progs")
PROG_T = [1, 3, 4, 6, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18, 26]


def public_texts():
    rows = json.load(open(os.path.join(WORK, "submission_main", "calib.json")))["rows"]   # release copy: rebuilt calib.json
    T = list(dict.fromkeys(r["text"] for r in rows))
    return [T[t - 1] for t in PROG_T]


def std_kind(log, cfg):
    m = re.search(r"\[std-case\] cfg=\S+ validated=(\d+) latent=(\S+) call=(\w) source=(\w+)", log)
    if m:
        return "std:" + m.group(4)
    return None


def build(bundle, track, out, speeds, sets, std, workers, cfgs_only=None, new_only=False):
    if std:
        spec = importlib.util.spec_from_file_location("run_per_case_v100", STD_HARNESS)
        R2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(R2)
        SM.R = R2
    R = SM.R
    tmp, sub = R.prepare(bundle, sets)
    env0 = {k: v for k, v in os.environ.items() if not re.search(r"BUDGET|DEADLINE|TIMEOUT|REMAINING|^MOCK_", k, re.I)}
    env0.update(R.BASE_ENV)
    if std:
        env0["MOCK_STD_PROGS"] = PROGS
    cfgs = SM.MAIN7 if track == "main" else SM.SMALL4
    if cfgs_only:
        cfgs = [c for c in cfgs if c in cfgs_only]
    texts = SM.problem_texts(50)
    if new_only:
        texts = [t for t in texts if "NEW-" in t]
    pub = public_texts() if std else []
    jobs = []
    for sp in speeds:
        env = dict(env0, MOCK_SLOW=str(sp))
        for c in cfgs:
            tl = texts + (pub if c in ("Skywork", "Olmo") else [])
            for j, p in enumerate(tl):
                jobs.append((sp, c, p, env, f"{sp}_{c}_{j}"))

    def go(a):
        sp, c, p, env, tag = a
        r = SM.one_case(sub, tmp, env, c, p, tag)
        return sp, c, p, r

    if std:   # one_case's kind_of does not know the STD lines: re-run the log parse via a wrapper
        orig = SM.one_case

        def one_case_std(sub_, tmp_, env_, cfg_, text_, tag_):
            import subprocess
            model, effort = R.CFG[cfg_]
            cf = os.path.join(tmp_, f"case_{tag_}.json")
            with open(cf, "w") as f:
                json.dump({"id": tag_, "model_id": model, "reasoning_effort": effort, "problem": text_}, f)
            r = subprocess.run([R.PY, R.__file__, "--child", sub_, cf], capture_output=True, text=True, env=env_, cwd=tmp_)
            m = re.search(r"^@@RESULT (.*)$", r.stdout, re.M)
            res = json.loads(m.group(1)) if m else dict(elapsed=0.0, valid=False, pred=None, err="crash " + r.stderr[-200:])
            log = r.stdout + r.stderr
            k = std_kind(log, cfg_) or SM.kind_of(log, cfg_)
            return dict(cfg=cfg_, sec=round(res["elapsed"] + float(env_.get("MOCK_PROC_S", "2")), 2), valid=res["valid"],
                        pred=res["pred"][0] if res["valid"] else None, kind=k, note=R.note_of(log),
                        qfin_moot=bool(re.search(r"quick finish moot", log)), cut="(cut by clock)" in log,
                        std_line=(re.search(r"\[std-case\][^\n]*", log).group(0)[:300] if "[std-case]" in log else ""))
        SM.one_case = one_case_std
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(go, jobs))
    T = {"bundle": bundle, "track": track, "sets": list(sets), "std": std, "speeds": speeds, "n_new": 50,
         "public_prog_templates": PROG_T if std else [], "cases": {}}
    for sp, c, p, r in res:
        T["cases"][f"{sp}|{c}|{p}"] = r
    with open(out, "w") as f:
        json.dump(T, f)
    print(f"wrote {out}: {len(res)} case runs", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("track")
    ap.add_argument("out")
    ap.add_argument("--std", action="store_true")
    ap.add_argument("--speeds", default="1.0,1.2,1.4,1.6")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--cfgs", default=None, help="comma list: build these configurations only")
    ap.add_argument("--new-only", action="store_true", help="only the 50 synthetic new problems (no board texts)")
    a = ap.parse_args()
    build(a.bundle, a.track, a.out, [float(x) for x in a.speeds.split(",")], a.set, a.std, a.workers,
          a.cfgs.split(",") if a.cfgs else None, a.new_only)
