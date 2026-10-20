"""Stand-in for engine2 used ONLY in the private-scale rehearsal: no model, a virtual clock that advances by the
server time model, random readings. Same function names as the real engine."""
import hashlib, os, random, time
_REAL = time.time
_OFF = [0.0]
time.time = lambda: _REAL() + _OFF[0]                 # every module that calls time.time() now sees virtual time
FACTOR = float(os.environ.get("MOCK_SLOW", "1.0"))    # server slower than modelled
COMPACT = os.environ.get("MOCK_COMPACT", "1") == "1"
A_MS = float(os.environ.get("MOCK_A", "28.0"))        # gpt-oss: fixed ms per step
B_MS = float(os.environ.get("MOCK_B", "1.3"))         # gpt-oss: ms per row per step
USED = float(os.environ.get("MOCK_USED", "0.7"))      # share of row-steps run when finished rows are removed
_GEN_KW = {}
_LOADED = [None]


def _adv(s):
    _OFF[0] += s


def is_harmony(m):
    return "gpt-oss" in m


class _Tok:
    pad_token_id = 0

    def __call__(self, p, add_special_tokens=False, **kw):
        return {"input_ids": [0] * 300}


def load(model_id):
    if _LOADED[0] != model_id:
        _adv(6.0 if is_harmony(model_id) else 3.0)
        _LOADED[0] = model_id
    return model_id, _Tok()


def build_prompt(tok, problem, chat_kwargs, system=None):
    return problem


def self_test_compact(model, tok, a, b, **kw):
    _adv(4.0)
    return (True, "mock") if COMPACT else (False, "mock: disabled")


def kv_bytes_per_token(model, cap=None, static=False):
    return 38500


def free_gpu_bytes():
    return 27e9


def _rows(model_id, prompts, cap, seed, deadline, seconds, compact):
    start = time.time()
    cut = start + seconds > deadline
    _adv(max(0.0, min(seconds, deadline - start)))
    frac = 1.0 if not cut else max(0.0, (deadline - start) / max(seconds, 1e-9))
    out = []
    for i, p in enumerate(prompts):
        h = int(hashlib.md5(p.encode()).hexdigest(), 16)
        rng = random.Random(h + seed * 7919 + i)
        p_fin = (h % 100) / 100.0 if is_harmony(model_id) else ((h // 100) % 100) / 300.0
        n = int(cap * rng.uniform(0.3, 1.2))
        nat = rng.random() < p_fin and n < cap * frac
        ans = str(rng.choice([h % 97, h % 97, h % 97, h % 89])) if nat else None
        out.append(dict(answer=ans, forced=(not nat) and not cut, natural=nat, n_tokens=min(n, cap), cut=cut, closed=True, tail="",
                        row_steps=int(len(prompts) * cap * 0.7), sw=0.0, eq=0.0, cand=0.0, first=-1.0, full=""))
    return out


CAP2 = float(os.environ.get("MOCK_CAP2", "1e12"))   # readings with a budget >= CAP2 (the own-effort medium reading) use a second time model
A2, B2, USED2 = (float(os.environ.get(k, d)) for k, d in (("MOCK_A2", "11.5"), ("MOCK_B2", "2.0"), ("MOCK_USED2", "0.6")))


def attempts_compact(model, tok, model_id, prompts, cap, seed, deadline, seg=256, answer_prefix=""):
    a, b, u = (A2, B2, USED2) if cap >= CAP2 else (A_MS, B_MS, USED)
    return _rows(model_id, prompts, cap, seed, deadline, FACTOR * cap * (a + u * b * len(prompts)) / 1000.0, True)


# ---- opt-in per-model timing for the ordinary (non-compacting) path: MOCK_OWN=1 (default off = behaviour above unchanged) ----
# Step cost (ms) = a + b * rows, every step, for every row of the batch (generate() keeps finished rows as padding).
# Sources: Skywork 8 + 4.6 (v39 log, ledger 274), Olmo 8 + 6.2 (bundle params), DeepSeek 8 + 11.6 at long context
# (ledger 346), Qwen 10 + 0.75 (ledger 38, the bundle's own _qwen_seconds). Override with MOCK_OWN_T="Olmo:8:9.9,...".
# A batch lasts until its LAST row stops: the cap if any row runs to it, else the longest row (generate() stops early).
# Finishing model, ASSUMED (fitted by eye to the hidden counts in ledger 299 / 289, not measured per attempt):
#   7B thinking models (Skywork, Olmo, DeepSeek): per problem, with probability MOCK_HARD (0.55) a "hard" problem whose
#   attempts end on their own with probability 0.03, else an "easy" one with probability U(0.40, 0.95); an attempt that
#   ends does so at U(3,000, 8,000) tokens (scaled by cap / 9,000 for other caps); the rest run to the cap.
#   Qwen (quick-finish reading, cap 2,000): the default mock's finish chance (0-0.33 per problem), ends at U(0.3, 1.0) x cap.
# MOCK_OWN_SLOW multiplies the time of the 7B models only (on top of MOCK_SLOW, which slows every model).
# MOCK_TRACE=<path>: one JSON line per attempt (model, md5 of the prompt, cap, tokens, ended alone, cut) for the driver.
OWN = os.environ.get("MOCK_OWN", "0") == "1"
OWN_SLOW = float(os.environ.get("MOCK_OWN_SLOW", "1.0"))
HARD = float(os.environ.get("MOCK_HARD", "0.55"))
TRACE = os.environ.get("MOCK_TRACE", "")
_OWN_T = {"Skywork": (8.0, 4.6), "Olmo": (8.0, 6.2), "DeepSeek": (8.0, 11.6), "Qwen": (10.0, 0.75)}
for _kv in filter(None, os.environ.get("MOCK_OWN_T", "").split(",")):
    _k, _a, _b = _kv.split(":")
    _OWN_T[_k] = (float(_a), float(_b))


# ---- fast decode path for own runs (fast7b.py, ledger 357 / 365): MOCK_FAST7=1 makes the per-run check pass; a batch of a
# model whose check passed, run while the caller set _FAST7["use"], costs MOCK_FAST7_T (default: the server's measured
# 0-7,000-token speeds x 1.3 for caps of 9-10k: Skywork 8 + 1.4, Olmo 8 + 3.1). Default off = behaviour above unchanged.
_FAST7 = {"on": set(), "use": False, "events": [], "mode": "sdpa", "batches": 0}
FAST7 = os.environ.get("MOCK_FAST7", "0") == "1"
_FAST7_T = {"Skywork": (8.0, 1.4), "Olmo": (8.0, 3.1)}
for _kv in filter(None, os.environ.get("MOCK_FAST7_T", "").split(",")):
    _k, _a, _b = _kv.split(":")
    _FAST7_T[_k] = (float(_a), float(_b))


def enable_fast7b(model, tok, model_id, prompt_a, prompt_b, **kw):
    if FAST7 and not is_harmony(model_id):
        _FAST7["on"].add(model_id)
        return True, "mock check", {}
    return False, "mock: fast path off", {}


def _own_time(model_id):
    if FAST7 and _FAST7["use"] and model_id in _FAST7["on"]:
        for k, v in _FAST7_T.items():
            if k.lower() in model_id.lower():
                _FAST7["batches"] += 1
                return v[0], v[1], OWN_SLOW
    for k, v in _OWN_T.items():
        if k.lower() in model_id.lower():
            return v[0], v[1], (1.0 if k == "Qwen" else OWN_SLOW)
    return 10.0, 0.75, 1.0


def _own_rows(model_id, prompts, cap, seed, deadline):
    import json
    a, b, extra = _own_time(model_id)
    plan = []
    for i, p in enumerate(prompts):
        hp = hashlib.md5((model_id + "|" + p).encode()).hexdigest()
        h = int(hashlib.md5(p.encode()).hexdigest(), 16)
        prng = random.Random(int(hp, 16))                       # per (model, problem): fixed across seeds and calls
        rng = random.Random(int(hp, 16) + seed * 7919 + i)      # per attempt
        if "qwen" in model_id.lower():
            p_end, lo, hi = ((h // 100) % 100) / 300.0, 0.3 * cap, 1.0 * cap
        else:
            p_end = 0.03 if prng.random() < HARD else prng.uniform(0.40, 0.95)
            lo, hi = 3000.0 * cap / 9000.0, 8000.0 * cap / 9000.0
        ends = rng.random() < p_end
        plan.append((hp, int(rng.uniform(lo, hi)) if ends else None))
    steps = cap if any(L is None for _, L in plan) else max(L for _, L in plan)
    seconds = FACTOR * extra * steps * (a + b * len(prompts)) / 1000.0
    start = time.time()
    cut = start + seconds > deadline
    _adv(max(0.0, min(seconds, deadline - start)))
    done = steps if not cut else int(steps * max(0.0, (deadline - start) / max(seconds, 1e-9)))
    out = []
    for hp, L in plan:
        nat = L is not None and L <= done
        n = L if nat else min(cap, done)
        out.append(dict(answer="7" if (nat or not cut) else None, forced=(not nat) and not cut and n >= cap, natural=nat, n_tokens=n,
                        cut=cut, closed=True, tail="", row_steps=int(len(prompts) * steps), sw=0.0, eq=0.0, cand=0.0, first=-1.0, full=""))
    if TRACE:
        with open(TRACE, "a") as f:
            for (hp, L), r in zip(plan, out):
                f.write(json.dumps(dict(model=model_id, key=hp, cap=cap, n=r["n_tokens"], nat=r["natural"], cut=cut, rows=len(prompts),
                                        sec=round(min(seconds, max(0.0, deadline - start)), 1))) + "\n")
    return out


def attempts(model, tok, model_id, prompts, cap, seed, deadline):
    if OWN and not is_harmony(model_id):
        return _own_rows(model_id, prompts, cap, seed, deadline)
    per_row = B_MS if is_harmony(model_id) else 0.75
    fixed = A_MS if is_harmony(model_id) else 10.0
    return _rows(model_id, prompts, cap, seed, deadline, FACTOR * cap * (fixed + per_row * len(prompts)) / 1000.0, False)


def features(samples, cap):
    k = max(len(samples), 1)

    def pair_rate(ans):
        c = {}
        for a in ans:
            c[a] = c.get(a, 0) + 1
        return sum(v * (v - 1) for v in c.values()) / (k * (k - 1)) if k > 1 else 0.0

    nat = [s["answer"] for s in samples if s["answer"] and s["natural"]]
    allans = [s["answer"] for s in samples if s["answer"]]
    counts = {}
    for a in nat:
        counts[a] = counts.get(a, 0) + 1
    return dict(modal=(max(counts.values()) / k if counts else 0.0), pair_nat=pair_rate(nat), pair=pair_rate(allans), natural=sum(s["natural"] for s in samples) / k,
                closed=1.0, tokens=sum(min(s["n_tokens"], cap) for s in samples) / (k * cap), answered=len(allans) / k)

_FAST = {"on": True}          # rehearsal: the fast decode path counts as on (ledger 196)
