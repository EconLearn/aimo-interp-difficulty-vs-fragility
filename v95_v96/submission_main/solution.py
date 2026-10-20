"""AIMO Interpretability Challenge submission v95 (main track; bundle sub_v114m = v83 / sub_v101m adapted to per-case
processes, ledger 464-465).

Per-case processes (the evaluation now runs every case in its own process, one after another, on a shared job budget):
the decision rules are v83's, only the work per case changes. (a) gpt-oss high: answered robust at once from the public
prior, before anything is imported or loaded. (b) Skywork / Olmo: the judged model's own run comes FIRST (K 3, fast decode
path after its check, rule as in params); the stand-in reading is taken only for a problem the own run left without a
reading. (c) Qwen / DeepSeek / gpt-oss low / medium: stand-in reading (gpt-oss low, up to K 32 in one batch, cap 3,000) +
Qwen quick finish, inside a per-case time target (params case_target_seconds): K is reduced, or the quick finish skipped
(decision.json's agreement_only model), when both would not fit. A budget-like environment variable, if any, caps the
target. The first call of a process with several problems, and every later call, take v83's multi-call path unchanged
(old harness), except that gpt-oss high is answered at once there too.

v83's method. Two label-free readings per problem, each taken once and reused for every judged configuration:
(1) gpt-oss-120b at LOW reasoning effort makes K attempts (organisers' sampling settings, budget 3,000 tokens); the reading
is the pairwise agreement among attempts that finish on their own. (2) Qwen3.5-4B with thinking switched off makes 4
attempts; the reading is whether any finishes within 2,000 tokens. A small logistic model fitted on the 71 public labelled
rows (agreement, quick finish, strength of the judged configuration) gives robust / non-robust (ledger 101, 113).
K is planned from the time left; attempts that have finished are removed from the batch (ledger 75, 79); spare time of a
call buys more attempts for that call's problems, most uncertain first (ledger 110). About hidden problems only counts are printed.
"""
import json
import math
import os
import re
import sys
import time

_T0 = time.time()
_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "params.json"), "r", encoding="utf-8") as _f:
    _P = json.load(_f)
with open(os.path.join(_HERE, "decision.json"), "r", encoding="utf-8") as _f:
    _D = json.load(_f)
with open(os.path.join(_HERE, "calib.json"), "r", encoding="utf-8") as _f:
    _CALIB = json.load(_f)["rows"]
_SMALL = any(n.lower() == "small.txt" for n in os.listdir(_HERE))          # small-track bundle: four configurations
_S = {"calls": 0, "read": {}, "smp": {}, "fin": {}, "research_done": False, "spa": {}, "new": [], "compact": {}, "stems": set(), "fast7": {}}
_STRENGTH = {"Skywork/Skywork-OR1-Math-7B:default": 1.0, "allenai/Olmo-3-7B-Think:default": 1.0,
             "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B:default": 1.0, "Qwen/Qwen3.5-4B:default": 1.0,
             "openai/gpt-oss-120b:low": 1.0, "openai/gpt-oss-120b:medium": 2.0, "openai/gpt-oss-120b:high": 3.0}


_CASE = {"pid": None, "calls": 0, "t0": None, "target": None, "own_target": None, "env_cap": None}
_NOT_BUDGET = ("HF_", "HUGGINGFACE", "NCCL", "TORCH", "PYTORCH", "CUDA", "TRANSFORMERS", "VLLM", "PIP_", "TOKENIZERS",
               "OMP_", "MKL", "GRPC", "AWS_", "GCS", "GOOGLE", "AZURE", "WANDB", "REQUESTS", "URLLIB", "KUBE", "DOCKER",
               "API_", "HTTP", "SSH", "GIT")      # library / network settings whose names contain TIMEOUT: never a budget


def _log(msg):
    print(f"[v114m {time.time() - _T0:7.1f}s] {msg}", flush=True)


def _proc_start():
    """Wall-clock start of this process from /proc (Linux), or None."""
    try:
        with open("/proc/self/stat", "r") as f:
            st = f.read()
        ticks = float(st[st.rindex(")") + 2:].split()[19])          # field 22: start time in clock ticks after boot
        with open("/proc/stat", "r") as f:
            btime = next(float(x.split()[1]) for x in f if x.startswith("btime"))
        return btime + ticks / os.sysconf("SC_CLK_TCK")
    except Exception:
        return None


def _shown(v, n=40):
    """A value printed in the harness probe: short tokens only (no spaces), else its length."""
    v = str(v)
    return v if re.fullmatch(r"[\w./:=,+-]{0,%d}" % n, v) else f"<{len(v)} chars>"


def _probe(t_call):
    """Once per process: the case clock (process start if /proc has it, else this call), the NAMES of environment
    variables that may describe the harness, sys.argv (short tokens only), and budget-like variables (name, value; a
    numeric one caps the case targets at env_cap_factor x its value in seconds; epoch values count as deadlines)."""
    _CASE.update(pid=os.getpid(), calls=0, t0=t_call, env_cap=None)
    ps = _proc_start()
    if ps is not None and 0.0 <= t_call - ps <= 120.0:
        _CASE["t0"] = ps
    tgt, own = float(_P.get("case_target_seconds", 200.0)), float(_P.get("own_case_target_seconds", 400.0))
    _CASE.update(target=tgt, own_target=own)
    try:
        names = sorted(k for k in os.environ if re.search(r"AIMO|CODABENCH|CASE|JOB|BUDGET", k, re.I))
        _log(f"harness probe: pid {os.getpid()}, process start {'unknown' if ps is None else f'{t_call - ps:.1f}s before this call'}; "
             f"env names with AIMO/CODABENCH/CASE/JOB/BUDGET: {names}; argv: {[_shown(a, 120) for a in sys.argv[:16]]}")
    except Exception:
        pass
    caps = []
    for k in sorted(os.environ):
        if not re.search(r"BUDGET|DEADLINE|TIMEOUT|REMAINING", k, re.I):
            continue
        if re.search(r"KEY|TOKEN|SECRET|PASS", k, re.I):
            _log(f"harness probe: budget-like env {k} (value not shown)")
            continue
        v = os.environ.get(k, "").strip()
        try:
            x = float(v)
        except ValueError:
            x = None
        if x is None:
            note = "not numeric, not used"
        elif k.upper().startswith(_NOT_BUDGET):
            note = "library setting, not used"
        else:
            secs, kind = x, "seconds"
            if 1e9 <= x < 1e10:
                secs, kind = x - _CASE["t0"], "epoch deadline (s)"
            elif 1e12 <= x < 1e13:
                secs, kind = x / 1000.0 - _CASE["t0"], "epoch deadline (ms)"
            ours = re.search(r"BUDGET|REMAINING|DEADLINE|CASE|JOB|AIMO|CODABENCH|INGESTION|SUBMISSION", k, re.I)
            if (0.0 if ours else float(_P.get("env_cap_min_seconds", 60.0))) <= secs <= 1e5:   # generic TIMEOUT names:
                                                                                                 # only plausible budgets
                cap = float(_P.get("env_cap_factor", 0.8)) * secs
                caps.append(cap)
                note = f"read as {kind}: {secs:.0f}s -> case targets capped at {cap:.0f}s"
            else:
                note = f"read as {kind}: {secs:.0f}s, outside the plausible range, not used"
        _log(f"harness probe: budget-like env {k}={_shown(v)}: {note}")
    if caps:
        _CASE["env_cap"] = min(caps)
        _CASE.update(target=min(tgt, _CASE["env_cap"]), own_target=min(own, _CASE["env_cap"]))


def _cap_end(t):
    """An absolute end time no later than the budget read from the environment (if any)."""
    return t if not _CASE.get("env_cap") else min(t, _CASE["t0"] + _CASE["env_cap"])


def _decide(prim, qfin, strength):
    """Robust (True) or not, from whichever readings exist: the primary reading (gpt-oss) and/or quick finish (Qwen)."""
    z = _margin(prim, qfin, strength)
    return True if z is None else z <= 0


def _own_secs(ks, spec, scale):
    """Predicted seconds of one own-model reading (ks = attempts per problem), packed into batches of at most rows_max rows."""
    from planner import batch_seconds
    t = spec["time_fast"] if spec.get("time_fast") and _S["fast7"].get(spec["model"]) else spec["time"]
    a_ms, b_ms = t["a_ms"], t["b_ms"]
    lim, tot, rows = spec.get("rows_max", 27), 0.0, 0
    for k in ks:
        if rows and rows + k > lim:
            tot += batch_seconds(rows, spec["cap"], a_ms, b_ms)
            rows = 0
        rows += k
    if rows:
        tot += batch_seconds(rows, spec["cap"], a_ms, b_ms)
    return 1.15 * scale * tot


def _own_read(problems, left_calls, spec, unc):
    """Ledger 339, 348, 352: the judged 7B model's own run to the end, taken BEFORE the call's top-up. If every new problem
    fits at K_max it gets K_max (the form that scored 19 on the board, ledger 350). Otherwise (final scale) one attempt per
    problem, most uncertain nominee answer first, for as many problems as fit; leftover time upgrades the first of them to
    K_max. Problems without a reading keep the nominee's answer. Hidden problems: counts only."""
    fr = _S.setdefault("fr_" + spec["name"], {})
    uniq = list(dict.fromkeys(problems))
    todo = [p for p in uniq if p not in fr]
    if not todo:
        return "no new problems"
    scale = 1.0
    if spec.get("scale_from_reading", True):          # measured slowdown so far: the reading, and any own-model run
        scale = max([1.0, _S["spa"].get(_P["reading"]["name"], 1.0)] +   # already finished in this run (ledger 367)
                    [v for k, v in _S["spa"].items() if k.startswith("own_")])
    if spec.get("time_fast") and spec.get("fast7b") and _P.get("fast7b", True):   # plan with the fast time model only
        import engine2 as E                                                        # after the check passed (ledger 357)
        _fast7_ok(E, *E.load(spec["model"]), spec)
    now = time.time()
    hard_end = _cap_end(_T0 + spec["total_seconds"] - (left_calls - 1) * spec["reserve_later_seconds"])
    end = now + spec.get("share", 1.0) * max(0.0, hard_end - now)  # plan inside a share when another own run comes later;
    left = end - now - 20.0                                         # the clock only stops the batch at the hard end
    km = spec["K_max"]
    if _own_secs([km] * len(todo), spec, scale) <= left:
        order, ks = todo, [km] * len(todo)               # board shape: exactly the v65 reading
    else:
        order = sorted(todo, key=unc)                   # most uncertain nominee answer first (ties keep call order)

        def plan(sp):
            n = 0
            while n < len(order) and _own_secs([1] * (n + 1), sp, scale) <= left:
                n += 1
            ks = [1] * n
            for i in range(n):
                trial = ks[:i] + [km] + ks[i + 1:]
                if _own_secs(trial, sp, scale) > left:
                    break
                ks = trial
            return ks
        ks = plan(spec)
        if spec.get("split_subset", False) and sum(ks) >= 4:   # ledger 367: two batches, most uncertain first, so a clock
            spec = dict(spec, rows_max=min(spec.get("rows_max", 27), (sum(ks) + 1) // 2))   # cut loses at most the second
            ks = plan(spec)
        order = order[:len(ks)]
    if not order:
        return f"new problems {len(todo)}, none read (window {left:.0f}s, time scale {scale:.2f})"
    pred = _own_secs(ks, spec, scale)
    got = _read(order, spec, 0, max(time.time() + 60.0, hard_end), spec.get("seed_base", 600000) * _S["calls"], ks=ks)
    for t, (f, smp) in got.items():
        fin = sum(1 for x in smp if x["natural"])
        far = sum(1 for x in smp if not x["natural"] and x["n_tokens"] >= 0.85 * spec["cap"])
        if fin or far:                                  # an attempt cut early by the clock says nothing
            fr[t] = (fin, far, len(smp))
    return (f"new problems {len(todo)}, read {len(order)} (K {km}: {sum(1 for k in ks if k == km)}, K 1: {sum(1 for k in ks if k == 1)}), "
            f"window {left:.0f}s, predicted {pred:.0f}s, took {time.time() - now:.0f}s, time scale {scale:.2f}, "
            f"with a reading {sum(1 for t in order if t in fr)}")


def _own_apply(problems, preds, spec):
    """Robust iff enough attempts ended on their own: min_ended of K_max attempts, or the single attempt (ledger 352: the
    rule is never applied with fewer attempts than it needs). A case without a reading keeps the answer it had."""
    fr = _S.get("fr_" + spec["name"], {})
    out, n_read, n_changed, hist = list(preds), 0, 0, {}
    for i, p in enumerate(problems):
        v = fr.get(p)
        if v is None:
            continue
        n_read += 1
        need = spec.get("min_ended", 1) if v[2] >= spec["K_max"] else 1
        new = v[0] >= need
        comb = spec.get("combine", "replace")            # ledger 322: two readers must agree ("and") or either may say robust ("or")
        if comb == "and":
            new = bool(out[i]) and new
        elif comb == "or":
            new = bool(out[i]) or new
        n_changed += int(bool(new) != bool(out[i]))
        out[i] = bool(new)
    for p in dict.fromkeys(problems):
        if p in fr:
            key = f"{fr[p][0]}/{fr[p][2]}"
            hist[key] = hist.get(key, 0) + 1
    return out, (f"cases with a reading {n_read}/{len(problems)}, problems by attempts ended alone {dict(sorted(hist.items()))}, "
                 f"answers changed {n_changed}, robust calls {sum(out)}/{len(out)}")


def _margin(prim, qfin, strength):
    """Decision score (> 0: non-robust); None when no reading exists."""
    if prim is not None and qfin is not None:
        d, vals = _D["full"], (prim, qfin, strength)
    elif prim is not None:
        d, vals = _D.get("primary_only") or _D["agreement_only"], (prim, strength)
    elif qfin is not None:
        d, vals = _D["finish_only"], (qfin, strength)
    else:
        return None
    z = d["beta"][0]
    for b, v, m, sd in zip(d["beta"][1:], vals, d["mu"], d["sd"]):
        z += b * (v - m) / sd
    return z


def _time_model(spec):
    """(fixed ms per step, ms per row per step, share of row-steps run, correction measured in this run)."""
    t = spec.get("time", {})
    if spec.get("time_fast") and _S.get("fast7", {}).get(spec.get("model")):   # own run on the fast decode path (ledger 365)
        t = spec["time_fast"]
    if spec.get("time_slow") and "gpt-oss" in spec.get("model", ""):   # ledger 196: fast decode path off -> v7's measured model
        try:
            import engine2 as E
            if not E._FAST.get("on"):
                t = spec["time_slow"]
        except Exception:
            t = spec["time_slow"]
    used = t.get("used_compact", 0.7) if _S["compact"].get(spec["model"] + json.dumps(spec.get("chat", {}), sort_keys=True)) else 1.0
    return t.get("a_ms", 28.0), t.get("b_ms", 1.3), used, _S["spa"].get(spec["name"], 1.0)


def _compact_ok(E, model, tok, spec):
    """Use the compacting loop only after it has passed its known-answer check on this model in this run."""
    if not spec.get("compact"):
        return False
    key = spec["model"] + json.dumps(spec.get("chat", {}), sort_keys=True)
    if key not in _S["compact"]:
        try:
            texts = list(dict.fromkeys(r["text"] for r in _CALIB))
            t0 = time.time()
            ok, detail = E.self_test_compact(model, tok, E.build_prompt(tok, texts[0], spec.get("chat", {})),
                                             E.build_prompt(tok, texts[1], spec.get("chat", {})), **spec.get("selftest", {}))
            _log(f"{spec['name']}: compacting-loop check {'PASSED' if ok else ('NOT RUN' if ok is None else 'FAILED')} ({detail}; {time.time() - t0:.1f}s)")
            _S["compact"][key] = bool(ok)
            if ok and "gpt-oss" in spec["model"] and _P.get("fastpath", True):   # ledger 188: fast decode path, self-checked
                t1 = time.time()
                try:
                    fok, fdet = E.enable_fastpath(model, tok, E.build_prompt(tok, texts[0], spec.get("chat", {})),
                                                  E.build_prompt(tok, texts[1], spec.get("chat", {})))
                except Exception as fexc:
                    fok, fdet = False, f"error {type(fexc).__name__}"
                _log(f"{spec['name']}: fast decode path {'ON' if fok else 'OFF'} ({fdet}; {time.time() - t1:.1f}s)")
        except Exception as exc:
            _log(f"{spec['name']}: compacting-loop check error ({type(exc).__name__}: {str(exc)[:120]})")
            _S["compact"][key] = False
    return _S["compact"][key]


def _fast7_ok(E, model, tok, spec):
    """Ledger 357: the own-run model's fast decode path (grouped attention + in-place K/V cache) is used only after its
    known-answer check passed on this model in this run (teacher-forced agreement, identical greedy tokens, sabotage
    fails); otherwise, or on any error, the default path."""
    if not spec.get("fast7b") or not _P.get("fast7b", True):
        return False
    key = spec["model"]
    if key not in _S["fast7"]:
        t0 = time.time()
        try:
            texts = list(dict.fromkeys(r["text"] for r in _CALIB))
            ok, detail, _ = E.enable_fast7b(model, tok, spec["model"], E.build_prompt(tok, texts[0], spec.get("chat", {})),
                                            E.build_prompt(tok, texts[1], spec.get("chat", {})), **spec.get("fast7b_check", {}))
        except Exception as exc:
            ok, detail = False, f"error {type(exc).__name__}: {str(exc)[:120]}"
            try:
                E._FAST7["on"].discard(spec["model"])
            except Exception:
                pass
        _log(f"{spec['name']}: fast decode path check {'PASSED' if ok else 'FAILED'}, {'fast' if ok else 'default'} path "
             f"({detail}; {time.time() - t0:.1f}s)")
        _S["fast7"][key] = bool(ok)
    return _S["fast7"][key]


def _fast7_events(E, spec):
    try:
        while E._FAST7["events"]:
            _log(f"{spec['name']}: {E._FAST7['events'].pop(0)}")
            _S["fast7"][spec["model"]] = False
    except Exception:
        pass


_EDITOR = "You are a careful editor of mathematics competition problems."
_REWRITE = {
    # wording follows the organisers' own perturbed versions in their public sample (ledger 84)
    "domain": ("Rewrite the problem below as a new word problem set in a completely different real-world context "
               "(different objects, people and setting). Keep exactly the same mathematical structure, the same numbers "
               "and the same final answer. Do not solve the problem and do not add hints. Output only the rewritten "
               "problem.\n\nProblem:\n"),
    "nosol": ("Change one or two of the numbers in the problem below so that its conditions contradict each other and "
              "the problem has no valid answer. Keep the wording and the final question exactly as they are; change "
              "only numbers (you may add one short numeric condition if that is needed). Do not state or hint that the "
              "problem is now impossible, and do not solve it. Output only the changed problem.\n\nProblem:\n"),
    "renum": ("Change the numbers in the problem below to different values of similar size, so that it stays a "
              "well-posed problem of the same kind with one valid answer. Keep the wording and the final question "
              "exactly as they are; change only numbers. Do not solve the problem. Output only the changed "
              "problem.\n\nProblem:\n"),
    "distract": ("Insert one or two short irrelevant remarks (in parentheses or as a side clause) into the problem "
                 "below. The remarks must not change the mathematics and must not give any hint. Keep everything else "
                 "exactly the same. Do not solve the problem. Output only the changed problem.\n\nProblem:\n"),
}


def _variants(E, model, tok, spec, texts, deadline):
    """Research only: the instrument model rewrites each PUBLIC problem `n` times (new story, or one premise broken)."""
    rw = spec["rewrite"]
    n = rw.get("n", 2)
    prompts = [E.build_prompt(tok, _REWRITE[rw["kind"]] + t, spec.get("chat", {}), system=_EDITOR) for t in texts for _ in range(n)]
    out, step = [], rw.get("rows_max", 64)
    t0 = time.time()
    for i in range(0, len(prompts), step):
        if time.time() > deadline:
            break
        out += E.attempts_compact(model, tok, spec["model"], prompts[i:i + step], rw.get("cap", 1200), spec.get("seed", 7) + 31 * i, deadline, spec.get("seg", 128))
    var = []
    for j in range(len(texts)):
        got = [r["full"] for r in out[j * n:(j + 1) * n] if r["natural"] and 40 <= len(r["full"]) <= 6000 and "ANSWER:" not in r["full"]]
        var.append(got)
    _log(f"{spec['name']}: rewrites for {sum(1 for v in var if v)}/{len(texts)} public templates, {sum(len(v) for v in var)} usable of {len(out)}, {time.time() - t0:.1f}s")
    return var


def _read(texts, spec, k, deadline, seed0, ks=None):
    """K attempts per text (or ks[i] for text i: top-up) in as few batches as memory allows; returns {text: (features, samples)}."""
    import engine2 as E
    from planner import choose_rows
    model, tok = E.load(spec["model"])
    if not texts:
        return {}
    # one segment means no row is ever removed, so the compacting loop needs no check there
    compact = bool(spec.get("compact")) and (spec["cap"] <= spec.get("seg", 256) or _compact_ok(E, model, tok, spec))
    if not compact and spec.get("fast7b"):            # own runs (ordinary path): fast decode path after its check
        _fast7_ok(E, model, tok, spec)
    chat = spec.get("chat", {})
    if spec.get("rewrite"):                          # research only: attempts on rewritten versions of public problems
        if not compact:
            _log(f"{spec['name']}: skipped (needs the compacting loop)")
            return {}
        var = _variants(E, model, tok, spec, texts, deadline)
        keep = [j for j in range(len(texts)) if var[j]]
        texts = [texts[j] for j in keep]
        var = [var[j] for j in keep]
        for j, t in enumerate(texts):
            _S.setdefault("shown", {})[(spec["name"], t)] = var[j][0]
            _S.setdefault("nvar", {})[(spec["name"], t)] = len(var[j])
        rowprompts = [[E.build_prompt(tok, v[m % len(v)], chat) for m in range(k)] for v in var]
    elif spec.get("perturb"):                        # research only: surface changes that keep the answer, one per attempt
        import perturb as PT
        pk = spec["perturb"]
        rowprompts = [[E.build_prompt(tok, PT.perturb(t, pk.get("seed", 1) + 97 * i + m, pk.get("kind", "distract")), chat) for m in range(k)]
                      for i, t in enumerate(texts)]
    else:
        rowprompts = [[E.build_prompt(tok, t, chat)] * kk for t, kk in zip(texts, ks or [k] * len(texts))]
    prefill = spec.get("prefill", "")                # research only: the answer is asked for at once, with no reasoning
    if prefill:
        if not compact:
            _log(f"{spec['name']}: skipped (needs the compacting loop)")
            return {}
        rowprompts = [[p + prefill for p in rp] for rp in rowprompts]
    if not texts:
        return {}
    ptoks = max(len(tok(p, add_special_tokens=False)["input_ids"]) for rp in rowprompts for p in set(rp))
    static = spec.get("gen", {}).get("cache_implementation") == "static"
    rows = choose_rows(spec["cap"], ptoks, E.kv_bytes_per_token(model, spec["cap"], static), E.free_gpu_bytes(), spec.get("rows_max", 128))
    ks = [len(rp) for rp in rowprompts]              # attempts per text; texts are packed into batches of at most `lim` rows
    lim = rows
    out, i, retried = {}, 0, False
    gen = dict(spec.get("gen", {}))
    while i < len(texts) and time.time() < deadline:
        j, tot = i, 0
        while j < len(texts) and (j == i or tot + ks[j] <= lim):
            tot += ks[j]
            j += 1
        idx = list(range(i, j))
        batch = [p for j in idx for p in rowprompts[j]]
        E._GEN_KW = gen
        try:                                         # fast decode path only for specs that ask for it and passed the check
            E._FAST7["use"] = bool(spec.get("fast7b") and _S["fast7"].get(spec["model"]))
        except Exception:
            pass
        tb = time.time()
        try:
            if compact:
                res = E.attempts_compact(model, tok, spec["model"], batch, spec["cap"], seed0 + i, deadline, spec.get("seg", 256),
                                         "ANSWER:" if prefill.endswith("ANSWER:") else "")
            else:
                res = E.attempts(model, tok, spec["model"], batch, spec["cap"], seed0 + i, deadline)
        except Exception as exc:
            msg = str(exc).lower()
            if "out of memory" in msg and len(idx) > 1:
                import gc
                import torch
                del exc
                gc.collect()
                torch.cuda.empty_cache()
                if not retried:                      # first try the same batch again after a clean-up (ledger 99)
                    retried = True
                    _log(f"{spec['name']}: out of memory, retrying {len(idx)} problems after clean-up")
                    continue
                lim = max(1, tot // 2)
                retried = False
                _log(f"{spec['name']}: out of memory, batch now {lim} rows")
                continue
            if compact and prefill and "out of memory" not in msg:
                _log(f"{spec['name']}: skipped, compacting loop failed ({type(exc).__name__}: {str(exc)[:100]})")
                return out                           # the ordinary path cannot read a prefilled answer
            if compact and "out of memory" not in msg:
                compact = False
                _S["compact"][spec["model"] + json.dumps(spec.get("chat", {}), sort_keys=True)] = False
                _log(f"{spec['name']}: compacting loop failed ({type(exc).__name__}: {str(exc)[:100]}); ordinary generation from here")
                continue
            if gen and "out of memory" not in msg:
                _log(f"{spec['name']}: generate options {gen} rejected ({type(exc).__name__}); using defaults")
                gen = {}
                continue
            raise
        el = time.time() - tb
        _fast7_events(E, spec)
        steps = max(r["n_tokens"] for r in res)
        used = (f", row-steps {res[0]['row_steps']} = {100.0 * res[0]['row_steps'] / max(steps * len(batch), 1):.0f}% of uncompacted"
                if compact else "")
        kb = sorted({ks[j] for j in idx})
        _log(f"{spec['name']}: batch {len(batch)} rows (K {kb[0] if len(kb) == 1 else f'mixed {kb[0]}-{kb[-1]}'}), {steps} steps, {el:.1f}s"
             f"{' (cut by clock)' if res[0]['cut'] else ''}, {1000 * el / max(steps, 1):.0f} ms/step, {el / len(batch):.2f} s/attempt{used}"
             f"{' [fast decode path]' if spec.get('fast7b') and _S['fast7'].get(spec['model']) else ''}")
        if not res[0]["cut"]:
            from planner import batch_seconds
            a_ms, b_ms, used_share, _ = _time_model(spec)
            ratio = el / max(batch_seconds(len(batch), spec["cap"], a_ms, b_ms, used_share), 1e-9)
            old = _S["spa"].get(spec["name"])
            _S["spa"][spec["name"]] = min(3.0, max(0.3, ratio if old is None else 0.5 * old + 0.5 * ratio))
        off = 0
        for j in idx:
            s = res[off:off + ks[j]]
            off += ks[j]
            out[texts[j]] = (E.features(s, spec["cap"]), s)
        i += len(idx)
        if res[0]["cut"]:
            break
    return out


def _research():
    all_texts = list(dict.fromkeys(r["text"] for r in _CALIB))
    drop_of = {i + 1: [r["max_drop"] for r in _CALIB if r["text"] == t] for i, t in enumerate(all_texts)}
    for spec in _P["research"]:
        if spec.get("texts_file"):                   # hand-made sibling versions of PUBLIC problems
            with open(os.path.join(_HERE, spec["texts_file"]), "r", encoding="utf-8") as f:
                items = [(x["id"], x["text"], x["T"]) for x in json.load(f)["items"]]
        else:
            items = [(f"T{i + 1:02d}", t, i + 1) for i, t in enumerate(all_texts)
                     if not spec.get("templates") or (i + 1) in spec["templates"]]
        if spec.get("suffix"):                       # same question with a fixed extra instruction (a control arm)
            items = [(lab, t + spec["suffix"], T) for lab, t, T in items]
        if _P.get("research_limit"):                 # local tests only
            items = items[: _P["research_limit"]]
        if time.time() > _T0 + _P["research_until_seconds"] - 60:
            _log(f"{spec['name']}: skipped (time)")
            continue
        texts = [t for _, t, _ in items]
        try:
            got = _read(texts, spec, spec["K"], min(_T0 + _P["research_until_seconds"], time.time() + spec["seconds"]), spec.get("seed", 7))
        except Exception as exc:
            _log(f"{spec['name']}: failed ({type(exc).__name__}: {str(exc)[:160]})")
            continue
        for lab, t, T in items:
            if t not in got:
                continue
            f, smp = got[t]
            drops = drop_of.get(T, [0.0])
            codes = " ".join(f"{x['n_tokens']}{'n' if x['natural'] else ('f' if x['forced'] else 'c')}"
                             f"{re.sub(r'[^0-9A-Za-z.+-]', '_', x['answer'])[:24] if x['answer'] else 'x'}" for x in smp)   # public problems: the answers themselves
            nv = _S.get("nvar", {}).get((spec["name"], t))
            _log(f"{spec['name']} {lab} drop {sum(drops) / len(drops):+.2f} | pair_nat {f['pair_nat']:.2f} natural {f['natural']:.2f}"
                 f"{'' if nv is None else f' variants {nv}'} | {codes}")
            shown = _S.get("shown", {}).get((spec["name"], t))
            if shown:                                # public problem as rewritten by the instrument (for a sanity read)
                _log(f"{spec['name']} {lab} text: " + re.sub(r"\s+", " ", shown)[:300])
        _log(f"{spec['name']}: read {len(got)}/{len(texts)} public texts")


def _qwen_seconds(n):
    """Rough cost of the quick-finish reading for n problems (ledger 38: about 10 ms + 0.75 ms per row per step)."""
    bk = _P["finish"]
    rows = bk["K"] * n
    full, rest = divmod(rows, bk.get("rows_max", 128))
    step = lambda r: (10.0 + 0.75 * r) / 1000.0
    return 1.2 * bk["cap"] * (full * step(bk.get("rows_max", 128)) + (step(rest) if rest else 0.0)) + 15.0


def _topup(uniq, spec, strength, left_calls, budget_end, hard):
    """Spare time of this call buys more attempts for THIS call's problems that already have a reading with fewer than
    K_top attempts (most of them were read at a small K by an earlier call): most uncertain decision first, every problem
    to the first of `top_levels` before any goes higher. Later calls keep the time for a minimum reading of their own new problems
    (same floor as plan_k) and the last call may use everything (ledger 110)."""
    from planner import plan_topup, call_seconds
    kt = spec.get("K_top", spec["K_max"])
    cand = [t for t in uniq if t in _S["smp"] and len(_S["smp"][t]) < kt]
    if not cand or _S.get("primary_dead") or not spec.get("topup", True):
        return {}, 0.0, 0.0
    a_ms, b_ms, used, scale = _time_model(spec)
    later = max(left_calls - 1, 0)
    avg_new = sum(_S["new"]) / max(len(_S["new"]), 1)
    pool = max(0.0, (budget_end - time.time()) * _P["primary_time_share"] - 30.0)
    floor = later * scale * call_seconds(max(1, int(round(avg_new))), spec["K_min"], spec.get("rows_max", 112), spec["cap"], a_ms, b_ms, used) if later else 0.0
    allow = min(max(0.0, pool - floor) / (later + 1), max(0.0, hard - time.time() - 30.0))
    pf = _D.get("primary_feature", "pair_nat")

    def unc(t):
        f = _S["fin"].get(t)
        z = _margin(_S["read"][t][pf], None if f is None else float(f["natural"] > 0), strength)
        return abs(z) if z is not None else 0.0
    prio = sorted(cand, key=unc)
    add, pred = plan_topup({t: len(_S["smp"][t]) for t in cand}, prio, sorted({min(int(x), kt) for x in spec.get("top_levels", [4])} | {kt}), 0.9 * allow,
                           spec.get("rows_max", 112), spec["cap"], a_ms, b_ms, used, scale)
    if not add:
        return {}, allow, 0.0
    texts = [t for t in prio if t in add]
    got = _read(texts, spec, 0, min(hard, time.time() + 1.5 * pred + 60.0), 300000 * _S["calls"], ks=[add[t] for t in texts])
    import engine2 as E
    for t, (f, smp) in got.items():
        _S["smp"][t] = _S["smp"][t] + list(smp)
        _S["read"][t] = E.features(_S["smp"][t], spec["cap"])
    return {t: add[t] for t in got}, allow, pred


def _standin(texts, t_end):
    """Per-case stand-in reading (gpt-oss low, up to K_max attempts in ONE batch, cap 3,000; v83's seeds of call 1) and
    Qwen quick finish, inside the case's end time t_end. Before gpt-oss is loaded: started only if its load estimate plus
    K_min fits. After the load (time measured): K = the largest that fits WITH the quick finish's predicted cost if that K
    is at least case_qfin_min_K, else the largest that fits alone (the decision then uses decision.json's agreement_only
    model). The quick finish then runs whenever the time left still covers its predicted cost; a quick finish cut by the
    clock before any attempt ended is discarded (it says nothing). Returns a note (counts only)."""
    from planner import call_seconds
    spec, bk = _P["reading"], _P["finish"]
    margin = float(_P.get("case_margin_seconds", 10.0))
    uniq = list(dict.fromkeys(texts))
    todo = [t for t in uniq if t not in _S["read"]]
    todo2 = [t for t in uniq if t not in _S["fin"]]
    q_est = _qwen_seconds(len(todo2)) if todo2 else 0.0
    kmin, kcap, rows = spec["K_min"], spec["K_max"], spec.get("rows_max", 112)

    def fit(a_ms, b_ms, used, scale, left, extra):
        k = 0
        for c in range(kmin, kcap + 1):
            if scale * call_seconds(len(todo), c, rows, spec["cap"], a_ms, b_ms, used) + extra <= left:
                k = c
        return k
    note = []
    if todo and not _S.get("primary_dead"):
        tm = spec.get("time", {})
        if fit(tm.get("a_ms", 28.0), tm.get("b_ms", 1.3), tm.get("used_compact", 0.7), 1.0, t_end - time.time() - margin,
               float(_P.get("oss_load_seconds_est", 30.0))) < kmin:
            note.append(f"gpt-oss not loaded (left {t_end - time.time():.0f}s: no time for K {kmin})")
        else:
            try:
                import engine2 as E
                _compact_ok(E, *E.load(spec["model"]), spec)
            except Exception as exc:
                _S["primary_dead"] = True
                note.append(f"gpt-oss failed to load ({type(exc).__name__})")
                _log(f"agreement instrument failed to load ({type(exc).__name__}: {str(exc)[:120]})")
            if not _S.get("primary_dead"):
                a_ms, b_ms, used, scale = _time_model(spec)
                left = t_end - time.time() - margin
                kq = fit(a_ms, b_ms, used, scale, left, q_est) if todo2 else 0
                with_q = bool(todo2) and kq >= min(int(_P.get("case_qfin_min_K", 16)), kcap)
                k = kq if with_q else fit(a_ms, b_ms, used, scale, left, 0.0)
                if k >= kmin:
                    pred = scale * call_seconds(len(todo), k, rows, spec["cap"], a_ms, b_ms, used)
                    t1, got = time.time(), {}
                    try:
                        got = _read(todo, spec, k, max(time.time() + 30.0, t_end - margin - (q_est if with_q else 0.0)), 100000 * _S["calls"])
                    except Exception as exc:
                        _S["primary_dead"] = True
                        _log(f"agreement reading failed ({type(exc).__name__}: {str(exc)[:120]})")
                    for t, (f, smp) in got.items():
                        _S["read"][t] = f
                        _S["smp"][t] = list(smp)
                    note.append(f"K {k} (planned {'with' if with_q else 'WITHOUT'} the quick finish; left {left:.0f}s, predicted "
                                f"{pred:.0f}s, took {time.time() - t1:.0f}s), read {len(got)}/{len(todo)}")
                else:
                    note.append(f"gpt-oss loaded, no time for K {kmin} (left {left:.0f}s)")
    _S["new"].append(len(todo))
    if todo2:
        left = t_end - time.time() - margin / 2.0
        if left >= q_est:
            try:
                gb = _read(todo2, bk, bk["K"], t_end - margin / 2.0, 200000 * _S["calls"])
                kept = 0
                for t, (f, smp) in gb.items():
                    if smp and smp[0].get("cut") and not any(x["natural"] for x in smp):
                        continue
                    _S["fin"][t] = f
                    kept += 1
                note.append(f"quick finish {kept}/{len(todo2)}")
            except Exception as exc:
                note.append(f"quick finish failed ({type(exc).__name__})")
                _log(f"finish reading failed ({type(exc).__name__}: {str(exc)[:120]})")
        else:
            note.append(f"quick finish skipped (left {left:.0f}s < predicted {q_est:.0f}s)")
    return "; ".join(note) if note else "nothing to read"


def _case(cfg, strength, problems):
    """First call of a process with a lone problem (the per-case harness, ledger 464): see the module docstring."""
    uniq = list(dict.fromkeys(problems))
    owns = [o for o in ([_P["sky"]] if _P.get("sky") else []) + list(_P.get("owns", [])) if cfg in o.get("apply_cfgs", [])]
    t0 = _CASE["t0"]
    t_end = t0 + (_CASE["own_target"] if owns else _CASE["target"])
    for own in owns:                                   # the judged model's own run FIRST; nothing else is loaded for it
        tm = [own["time"]] + ([own["time_fast"]] if own.get("time_fast") and own.get("fast7b") and _P.get("fast7b", True) else [])
        need = float(_P.get("own_load_seconds_est", 25.0)) + 20.0 + min(_own_secs([1] * len(uniq), dict(own, time=t, time_fast=None), 1.0) for t in tm)
        if t_end - time.time() < need:                 # not even one attempt per problem fits: do not load the model
            _log(f"case ({cfg}): {own['name']} own run first: skipped, model not loaded (left {t_end - time.time():.0f}s, "
                 f"one attempt needs ~{need:.0f}s)")
            continue
        try:
            import engine2 as E
            E.load(own["model"])                       # loaded before planning, so the plan sees the time left
            sp = dict(own, total_seconds=t_end - _T0, reserve_later_seconds=0.0, share=1.0)
            note = _own_read(problems, 1, sp, lambda t: 0.0)
        except Exception as exc:
            note = f"failed ({type(exc).__name__}: {str(exc)[:100]})"
        _log(f"case ({cfg}): {own['name']} own run first: {note}")
    missing = [p for p in uniq if not any(p in _S.get("fr_" + o["name"], {}) for o in owns)]
    st = "not needed (own reading)"
    if missing:                                        # no own configuration, or the own run left a problem unread
        st = _standin(missing, t_end if not owns else min(t_end, time.time() + _CASE["target"]))
    pf = _D.get("primary_feature", "pair_nat")
    preds, kinds = [], {}
    for p in problems:
        a, f = _S["read"].get(p), _S["fin"].get(p)
        prim, q = (None if a is None else a[pf]), (None if f is None else float(f["natural"] > 0))
        preds.append(bool(_decide(prim, q, strength)))
        kind = ("full" if q is not None else "agreement_only") if prim is not None else ("finish_only" if q is not None else "none")
        kinds[kind] = kinds.get(kind, 0) + 1
    for own in owns:
        try:
            preds, note = _own_apply(problems, preds, own)
        except Exception as exc:
            note = f"failed, answers unchanged ({type(exc).__name__}: {str(exc)[:100]})"
        _log(f"case ({cfg}): {own['name']} combined by '{own.get('combine', 'replace')}': {note}")
    _log(f"case ({cfg}): {len(problems)} case(s), target {t_end - t0:.0f}s{' (env cap)' if _CASE.get('env_cap') and _CASE['env_cap'] < t_end - t0 + 1e-6 else ''}, "
         f"stand-in: {st}, stand-in decision models {dict(sorted(kinds.items()))}, predicted robust {sum(preds)}/{len(preds)}, "
         f"elapsed {time.time() - t0:.1f}s")
    return preds


def are_robust(model_id: str, reasoning_effort: str = "default", problems: list = None) -> list:
    t_call = time.time()
    problems = list(problems or [])
    _S["calls"] += 1
    cfg = f"{model_id}:{(reasoning_effort or 'default').strip().lower()}"
    strength = _STRENGTH.get(cfg, 1.0)
    if _CASE["pid"] != os.getpid():                   # once per process (also after a fork)
        try:
            _probe(t_call)
        except Exception as exc:
            _CASE.update(pid=os.getpid(), calls=0, t0=t_call, target=float(_P.get("case_target_seconds", 200.0)),
                         own_target=float(_P.get("own_case_target_seconds", 400.0)), env_cap=None)
            _log(f"harness probe failed ({type(exc).__name__})")
    _CASE["calls"] += 1
    if cfg in _P.get("prior_robust", []):             # ledger 336 / 464: answered at once, nothing imported or loaded
        _log(f"call {_S['calls']} ({cfg}): {len(problems)} cases answered robust at once from the public prior")
        return [True for _ in problems]
    if not problems:
        return []
    if (_CASE["calls"] == 1 and len(set(problems)) <= int(_P.get("case_mode_max_problems", 1))
            and _P.get("entry_mode", "full") == "full" and not _P.get("research")):
        try:
            return _case(cfg, strength, problems)
        except Exception as exc:
            _log(f"fallback ({type(exc).__name__}: {str(exc)[:160]})")
            return [True for _ in problems]
    try:
        spec, bk = _P["reading"], _P["finish"]
        mode = _P.get("entry_mode", "full")          # "full": both readings; "finish": quick-finish reading only;
        expected = _P.get("expected_calls_small", 4) if _SMALL else _P["expected_calls"]
        left_calls = max(1, expected - _S["calls"] + 1)                       # "constant": research run, every case answered robust
        pending = bool(_P.get("research")) and not _S["research_done"]
        if mode == "constant":
            if pending:
                _S["research_done"] = True
                try:
                    _research()
                except Exception as exc:
                    _log(f"research failed ({type(exc).__name__}: {str(exc)[:160]})")
            _log(f"call {_S['calls']} ({cfg}): {len(problems)} cases, research run, all answered robust")
            return [True for _ in problems]
        budget_end = _cap_end(_T0 + (_P["first_call_seconds"] + _P["reserve_per_call_seconds"] * (left_calls - 1) if pending else _P["total_seconds"]))
        uniq = list(dict.fromkeys(problems))
        todo = [p for p in uniq if p not in _S["read"]]
        todo2 = [p for p in uniq if p not in _S["fin"]]
        _S["stems"].update(re.sub(r"\d+", "#", p)[:80] for p in uniq)
        if mode == "finish":
            _S["primary_dead"] = True                # this run answers from the quick-finish reading alone
        if todo and not _S.get("primary_dead"):      # load and check the instrument before the clock of this call is planned
            try:
                import engine2 as E
                _compact_ok(E, *E.load(spec["model"]), spec)
            except Exception as exc:
                _S["primary_dead"] = True
                _log(f"agreement instrument failed to load ({type(exc).__name__}: {str(exc)[:120]})")
        from planner import plan_k
        a_ms, b_ms, used_share, scale = _time_model(spec)
        k_cap = spec["K_max"]
        if _S["calls"] == 1 and len(todo) >= _P.get("first_call_cap_min_problems", 10):   # final shape only; board unchanged
            k_cap = min(spec["K_max"], _P.get("first_call_K_max", spec["K_max"]))
        k, allow, predicted = plan_k(len(todo), _S["new"], left_calls, budget_end - time.time(), _P["primary_time_share"],
                                     spec["K_min"], k_cap, _P["future_new_factor"], spec.get("rows_max", 112), spec["cap"],
                                     a_ms, b_ms, used_share, scale)   # ledger 406: call 1 is planned before any speed is measured
        _S["new"].append(len(todo))
        hard = budget_end - _P["reserve_per_call_seconds"] * (left_calls - 1)
        deadline = max(time.time() + 45.0, hard - _qwen_seconds(len(todo2)))      # the plan sets K; the clock is only a last resort
        got = {}
        if todo and not _S.get("primary_dead"):
            try:
                got = _read(todo, spec, k, deadline, 100000 * _S["calls"])
            except Exception as exc:               # the strong instrument is unusable (load failure, repeated OOM)
                _S["primary_dead"] = True
                _log(f"agreement reading failed ({type(exc).__name__}: {str(exc)[:120]})")
        for t, (f, smp) in got.items():
            _S["read"][t] = f
            _S["smp"][t] = list(smp)
        if todo2 and time.time() < hard:
            try:                                   # second reading: small model, thinking off, quick finish (ledger 49)
                gb = _read(todo2, bk, bk["K"], max(time.time() + 45.0, hard), 200000 * _S["calls"])
                for t, (f, smp) in gb.items():
                    _S["fin"][t] = f
            except Exception as exc:
                _log(f"finish reading failed ({type(exc).__name__}: {str(exc)[:120]})")
        pf = _D.get("primary_feature", "pair_nat")

        def _unc(t):
            a, f = _S["read"].get(t), _S["fin"].get(t)
            z = _margin(None if a is None else a[pf], None if f is None else float(f["natural"] > 0), strength)
            return abs(z) if z is not None else 0.0
        owns = [o for o in ([_P["sky"]] if _P.get("sky") else []) + list(_P.get("owns", [])) if cfg in o.get("apply_cfgs", [])]
        for own in owns:                               # ledger 352: the own run comes before the (elastic) top-up
            try:
                note = _own_read(problems, left_calls, own, _unc)
            except Exception as exc:
                note = f"failed, answers unchanged ({type(exc).__name__}: {str(exc)[:100]})"
            _log(f"call {_S['calls']}: {own['name']} run to the end: {note}")
        top, tallow, tpred = {}, 0.0, 0.0
        if time.time() < hard:
            try:
                top, tallow, tpred = _topup(uniq, spec, strength, left_calls, budget_end, hard)
            except Exception as exc:
                _log(f"top-up failed ({type(exc).__name__}: {str(exc)[:120]})")
        kk = sorted(len(_S["smp"][p]) for p in uniq if p in _S["smp"])
        preds = []
        for p in problems:
            a, f = _S["read"].get(p), _S["fin"].get(p)
            preds.append(bool(_decide(None if a is None else a[_D.get("primary_feature", "pair_nat")], None if f is None else float(f["natural"] > 0), strength)))
        for own in owns:                               # ledger 339, 348: configurations read by their own model
            try:
                preds, sky_note = _own_apply(problems, preds, own)
            except Exception as exc:
                sky_note = f"failed, answers unchanged ({type(exc).__name__}: {str(exc)[:100]})"
            _log(f"call {_S['calls']}: {own['name']} combined by '{own.get('combine', 'replace')}': {sky_note}")
        if cfg in _P.get("prior_robust", []):         # ledger 336
            n_was = sum(preds)
            preds = [True for _ in problems]
            _log(f"call {_S['calls']}: configuration answered from its public prior (robust); the reading had called {n_was}/{len(preds)} robust")
        _log(f"call {_S['calls']} ({cfg}): {len(problems)} cases, new problems {len(todo)}, K {k} (allowance {allow:.0f}s, predicted {predicted:.0f}s, time-model correction {scale:.2f}), "
             f"agreement {len(got)}/{len(todo)}, finish {sum(1 for p in uniq if p in _S['fin'])}/{len(uniq)}, problems so far {len(_S['fin'])}, "
             f"templates so far {len(_S['stems'])}, predicted robust {sum(preds)}/{len(preds)} | top-up {len(top)} problems +{sum(top.values())} attempts "
             f"(allowance {tallow:.0f}s, predicted {tpred:.0f}s), attempts per problem min {kk[0] if kk else 0} median {kk[len(kk) // 2] if kk else 0} max {kk[-1] if kk else 0}")
        if not _S["research_done"] and _P.get("research"):
            _S["research_done"] = True
            try:
                _research()
            except Exception as exc:
                _log(f"research failed ({type(exc).__name__}: {str(exc)[:160]})")
        return preds
    except Exception as exc:
        _log(f"fallback ({type(exc).__name__}: {str(exc)[:160]})")
        return [True for _ in problems]
