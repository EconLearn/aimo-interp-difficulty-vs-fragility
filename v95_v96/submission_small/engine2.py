"""Multi-model capped-attempt engine (research runs). Works for the five contest model families:
Qwen3.5 (thinking on/off), Skywork-OR1 and DeepSeek-R1-Qwen3 (R1-style <think>), Olmo-3-Think, gpt-oss (harmony
channels). An attempt that has not answered by the cap is made to close its reasoning and write `ANSWER:`."""
import gc
import os
import re
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizerFast
from transformers.generation.logits_process import LogitsProcessor, LogitsProcessorList
from transformers.generation.stopping_criteria import StoppingCriteria, StoppingCriteriaList

SYSTEM_PROMPT = (
    "You are a precise math problem solver. Solve the given problem step by step, then output your "
    "final answer on the last line in the exact format:\nANSWER: <your answer>\nThis result should be "
    "an integer value or NaN if the given problem does not have a solution."
)
_M = {"name": None, "model": None, "tok": None}
_GEN_KW = {}                                        # extra generate() arguments, e.g. a static cache


def is_harmony(model_id):
    return "gpt-oss" in model_id


def release():
    _M.update(name=None, model=None, tok=None)
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def load_tokenizer(path):
    """Pick a tokenizer that round-trips text. Under transformers 5.13 AutoTokenizer gives DeepSeek-R1-0528-Qwen3-8B a
    legacy Llama conversion that drops spaces (the organisers' baseline loads PreTrainedTokenizerFast for this reason)."""
    probe = "Okay, so 17 plus 26 is 43.\nANSWER: 43"
    last = None
    for cls in (PreTrainedTokenizerFast, AutoTokenizer):
        try:
            tok = cls.from_pretrained(path, local_files_only=True)
        except Exception:
            continue
        last = tok
        if tok.decode(tok.encode(probe, add_special_tokens=False)) == probe and getattr(tok, "chat_template", None):
            return tok
    return last


def load(model_id):
    if _M["name"] == model_id:
        return _M["model"], _M["tok"]
    release()
    path = os.environ.get("AIMO_LOCAL_MODEL", model_id)              # local tests only
    tok = load_tokenizer(path)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    if torch.cuda.is_available():
        kw = {} if is_harmony(model_id) else {"dtype": torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16}
        model = AutoModelForCausalLM.from_pretrained(path, device_map="auto", local_files_only=True, **kw)
    else:
        model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32, local_files_only=True)
    model.eval()
    _M.update(name=model_id, model=model, tok=tok)
    return model, tok


def build_prompt(tok, problem, chat_kwargs, system=None):
    """Chat prompt. `prefill_nothink` (our own key, not a template argument) opens and immediately closes the
    reasoning block so R1-style models that have no thinking switch answer directly."""
    kw = dict(chat_kwargs)
    nothink = kw.pop("prefill_nothink", False)
    msgs = [{"role": "system", "content": system or SYSTEM_PROMPT}, {"role": "user", "content": problem}]
    try:
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw)
    except Exception:
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    if nothink and "</think>" not in p[-40:]:
        p = p + ("\n</think>\n\n" if p.rstrip("\n").endswith("<think>") else "<think>\n\n</think>\n\n")
    return p


def stop_ids(model, tok, model_id):
    ids = set()
    ge = getattr(getattr(model, "generation_config", None), "eos_token_id", None)
    if isinstance(ge, int):
        ids.add(ge)
    elif isinstance(ge, (list, tuple)):
        ids.update(int(i) for i in ge)
    for i in (tok.eos_token_id, tok.pad_token_id):
        if i is not None:
            ids.add(int(i))
    if not is_harmony(model_id):
        for t in ("<|im_end|>", "<|endoftext|>"):
            v = tok.convert_tokens_to_ids(t)
            if isinstance(v, int) and v >= 0 and v != tok.unk_token_id:
                ids.add(v)
    return sorted(ids)


def _norm(a):
    """Canonical form of a stated answer, so that `20808`, `\\(20808\\)`, `**20808**`, `N = 20808`, `{143}`, `(143)`,
    `\\textbf{143}` and `26\\,244` count as the same answer (ledger 104; ledger 195: wrappers the decision's training data had
    stripped, so the entry now scores answers the way its rule was fitted)."""
    a = a.strip()
    for _ in range(2):
        a = re.sub(r"\\(?:boxed|textbf|mathbf|text|mathrm|bf)\s*\{([^{}]*)\}", r"\1", a)
    a = re.sub(r"\\\(|\\\)|\\\[|\\\]|\\[!,;:]|[$*`{}()]", "", a).replace(",", "").strip(" .")
    m = re.fullmatch(r"(?:[A-Za-z]\w{0,8}\s*=\s*)?(-?\d{1,3}(?: \d{3})+|-?\d+)(?:\.0+)?", a)
    if m:
        return str(int(m.group(1).replace(" ", "")))
    if len(a) <= 24 and re.search(r"nan|no solution", a, re.I):
        return "NaN"
    return a[:40] if a else None


def parse_answer(text):
    m = re.findall(r"ANSWER:\s*([^\n<]+)", text)
    if m:
        return _norm(m[-1])
    tail = re.split(r"</think>|<\|channel\|>final<\|message\|>", text)[-1]
    b = re.findall(r"\\boxed\{([^{}]+)\}", tail)
    return _norm(b[-1]) if b else None


_SWITCH = re.compile(r"\b(Wait|Alternatively|Hmm|Actually|Let me re|But wait|Hold on|Let's re)\b")


def text_stats(text, head_chars=8000):
    """Process markers of one attempt (thought switches, computation lines), per 1,000 characters, on the
    first `head_chars` characters (about 2,000 tokens) so attempts of different length compare fairly."""
    h = text[:head_chars]
    k = max(len(h), 1) / 1000.0
    m = re.search(r"answer is|\\boxed|ANSWER:", text)
    return dict(sw=len(_SWITCH.findall(h)) / k, eq=sum(1 for ln in h.splitlines() if ln.rstrip().endswith("=")) / k,
                cand=len(re.findall(r"(?:answer is|ANSWER:)", h)) / k,
                first=(m.start() / 4.0) if m else -1.0)     # rough token position of the first stated candidate


def final_text(text, model_id):
    """What the model wrote after its reasoning (the final channel for gpt-oss, the part after </think> otherwise)."""
    if is_harmony(model_id):
        parts = text.split("<|channel|>final<|message|>")
        return parts[-1].strip() if len(parts) > 1 else ""
    return text.split("</think>")[-1].strip()


def closed_reasoning(text, model_id):
    if is_harmony(model_id):
        return "<|channel|>final" in text
    return "</think>" in text


class ForceAnswerAtCap(LogitsProcessor):
    def __init__(self, tok, model_id, prompt_len, cap, stops, ans_max=12, prompt_closed=False):
        self.tok, self.model_id, self.prompt_len, self.cap, self.stops, self.ans_max = tok, model_id, prompt_len, cap, set(stops), ans_max
        self.prompt_closed = prompt_closed            # thinking switched off in the prompt itself
        if is_harmony(model_id):
            self.sfx_open = tok.encode("<|end|><|start|>assistant<|channel|>final<|message|>ANSWER:", add_special_tokens=False)
        else:
            self.sfx_open = tok.encode("\n</think>\n\nANSWER:", add_special_tokens=False)
        self.sfx_closed = tok.encode("\nANSWER:", add_special_tokens=False)
        self.nl = set(tok.encode("\n", add_special_tokens=False)) | set(tok.encode("\n\n", add_special_tokens=False))
        self.end_id = sorted(self.stops)[0] if not is_harmony(model_id) else tok.convert_tokens_to_ids("<|return|>")
        self.plan = None

    def __call__(self, input_ids, scores):
        step = input_ids.shape[1] - self.prompt_len
        if step < self.cap:
            return scores
        if self.plan is None:
            self.plan = []
            for b in range(input_ids.shape[0]):
                gen = input_ids[b, self.prompt_len:].tolist()
                if any(t in self.stops for t in gen):
                    self.plan.append(None)
                    continue
                text = self.tok.decode(gen, skip_special_tokens=False)
                closed = self.prompt_closed or closed_reasoning(text, self.model_id)
                self.plan.append(self.sfx_closed if closed else self.sfx_open)
        j = step - self.cap
        for b, p in enumerate(self.plan):
            if p is None:
                continue
            if j < len(p):
                t = p[j]
            else:
                k = j - len(p)
                if k >= self.ans_max or (k > 0 and int(input_ids[b, -1]) in self.nl):
                    t = self.end_id
                else:
                    t = int(torch.argmax(scores[b]))
            row = torch.full_like(scores[b], float("-inf"))
            row[t] = 0.0
            scores[b] = row
        return scores


class DeadlineStop(StoppingCriteria):
    def __init__(self, deadline):
        self.deadline, self.hit = deadline, False

    def __call__(self, input_ids, scores, **kwargs):
        if time.time() > self.deadline:
            self.hit = True
        return torch.full((input_ids.shape[0],), self.hit, dtype=torch.bool, device=input_ids.device)


@torch.no_grad()
def attempts(model, tok, model_id, prompts, cap, seed, deadline):
    """One generate() call over `prompts` (T 1.0, top-k 40, top-p 0.95, the organisers' settings)."""
    dev = model.get_input_embeddings().weight.device
    enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
    plen = enc["input_ids"].shape[1]
    stops = stop_ids(model, tok, model_id)
    if getattr(model, "_cache", None) is not None:       # a static cache from an earlier batch size stays allocated otherwise
        model._cache = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def run(fast):
        p = ForceAnswerAtCap(tok, model_id, plen, cap, stops,
                             prompt_closed=(not is_harmony(model_id)) and "</think>" in prompts[0][-40:])
        s = DeadlineStop(deadline)
        kw = dict(**enc, do_sample=True, temperature=1.0, top_k=40, top_p=0.95,
                  max_new_tokens=cap + len(p.sfx_open) + p.ans_max + 2,
                  logits_processor=LogitsProcessorList([p]), stopping_criteria=StoppingCriteriaList([s]),
                  pad_token_id=tok.pad_token_id, eos_token_id=stops, **_GEN_KW)
        torch.manual_seed(seed)
        if not fast:
            return model.generate(**kw), p, s
        import fast7b as F7                          # ledger 357: grouped attention + slab cache, self-checked in this run
        with F7.active(model, mode=_FAST7["mode"]):
            return model.generate(past_key_values=F7.slab_cache(model), use_cache=True, **kw), p, s

    fast = (_FAST7["use"] and model_id in _FAST7["on"] and not is_harmony(model_id)
            and not ({"past_key_values", "cache_implementation", "use_cache"} & set(_GEN_KW)))
    try:
        out, proc, stop = run(fast)
        _FAST7["batches"] += int(fast)
    except Exception as exc:
        if not fast or "out of memory" in str(exc).lower():
            raise
        _FAST7["on"].discard(model_id)              # any other failure: default path from here, this batch again
        _FAST7["events"].append(f"fast decode path failed in generation ({type(exc).__name__}: {str(exc)[:100]}); "
                                f"default path from here")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        out, proc, stop = run(False)
    res = []
    for b in range(out.shape[0]):
        gen = out[b, plen:].tolist()
        n = next((i for i, t in enumerate(gen) if t in stops), len(gen))
        text = tok.decode(gen[:n], skip_special_tokens=False)
        forced = bool(proc.plan is not None and proc.plan[b] is not None)
        finished = (not forced) and n < len(gen) and n < cap      # reached a stop token on its own (cut or not)
        res.append(dict(answer=parse_answer(text), forced=forced, natural=finished,
                        n_tokens=n, cut=stop.hit, closed=proc.prompt_closed or closed_reasoning(text, model_id), tail=text[-160:],
                        **text_stats(text)))
    return res


def kv_bytes_per_token(model, cap=None, static=False):
    """Cache bytes per token per row. Sliding-window layers count in full while the sequence is shorter than the window."""
    cfg = getattr(model.config, "text_config", model.config)
    layers = getattr(cfg, "layer_types", None)
    n_full = layers.count("full_attention") if layers else getattr(cfg, "num_hidden_layers", 32)
    window = getattr(cfg, "sliding_window", None)
    if static and layers:
        n_full = len(layers)                       # a preallocated cache holds every layer at full length
    elif layers and window:
        n_slide = len(layers) - n_full
        n_full = n_full + n_slide * min(1.0, float(window) / float(max(cap or window, 1)))
    heads = getattr(cfg, "num_key_value_heads", None) or getattr(cfg, "num_attention_heads", 16)
    hd = getattr(cfg, "head_dim", None) or (getattr(cfg, "hidden_size", 4096) // getattr(cfg, "num_attention_heads", 16))
    return n_full * 2 * heads * hd * 2


def free_gpu_bytes():
    if not torch.cuda.is_available():
        return 8e9
    gc.collect()
    torch.cuda.empty_cache()                       # blocks cached by the previous batch are free for us
    return float(torch.cuda.mem_get_info()[0])


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
                closed=sum(s["closed"] for s in samples) / k, tokens=sum(min(s["n_tokens"], cap) for s in samples) / (k * cap),
                answered=len(allans) / k)


# ---- compacting generation: attempts that have finished stop costing time (ledger 72) ----

@torch.no_grad()
def gen_compact(model, ids, mask, cap, stops, pad_id, deadline, seg=256, sample=True, extra=None, test_drop=None):
    """Generate up to `cap` new tokens per row in segments of `seg` steps. After each segment the rows that reached a
    stop token are removed from the batch and from the key/value cache, so later steps only pay for unfinished rows.
    Returns (tokens per original row, finished flag per row, cut_by_clock, row_steps)."""
    dev = ids.device
    plen, n0 = ids.shape[1], ids.shape[0]
    stop_t = torch.tensor(sorted(stops), device=dev)
    stopper = DeadlineStop(deadline)
    alive = list(range(n0))
    toks, done = [None] * n0, [False] * n0
    cache, steps, row_steps = None, 0, 0
    kw = dict(do_sample=True, temperature=1.0, top_k=40, top_p=0.95) if sample else dict(do_sample=False)
    kw.update(extra or {})
    while alive and steps < cap and not stopper.hit:
        if cache is not None:
            kw["past_key_values"] = cache
        out = model.generate(input_ids=ids, attention_mask=mask, max_new_tokens=min(seg, cap - steps),
                             stopping_criteria=StoppingCriteriaList([stopper]), pad_token_id=pad_id,
                             eos_token_id=sorted(stops), return_dict_in_generate=True, **kw)
        seq = out.sequences
        new = seq[:, ids.shape[1]:]
        if new.shape[1] == 0:
            break
        steps += new.shape[1]
        row_steps += new.shape[1] * len(alive)
        fin = torch.isin(new, stop_t).any(dim=1).tolist()
        if test_drop and steps == new.shape[1]:          # self-check only: treat these rows as finished after segment 1
            fin = [f or (alive[r] in test_drop) for r, f in enumerate(fin)]
        keep = [r for r in range(len(alive)) if not fin[r]]
        for r, o in enumerate(alive):
            if fin[r]:
                toks[o], done[o] = seq[r, plen:].tolist(), True
        if not keep:
            alive = []
            break
        idx = torch.tensor(keep, device=dev)
        if steps >= cap or stopper.hit:              # last segment: nothing more to generate, so the cache is not touched
            ids, alive = seq[idx], [alive[r] for r in keep]
            break
        add = torch.ones((len(keep), new.shape[1]), dtype=mask.dtype, device=dev)
        cache = out.past_key_values
        if len(keep) < len(alive):
            cache.batch_select_indices(idx)
            ids, mask = seq[idx], torch.cat([mask[idx], add], dim=1)
        else:
            ids, mask = seq, torch.cat([mask, add], dim=1)
        alive = [alive[r] for r in keep]
    for r, o in enumerate(alive):
        toks[o] = ids[r, plen:].tolist()
    return toks, done, stopper.hit, row_steps


def attempts_compact(model, tok, model_id, prompts, cap, seed, deadline, seg=256, answer_prefix=""):
    """Same contract as attempts(), without the forced answer: an attempt still running at the cap is recorded as
    unanswered (`forced` True, answer None), one stopped by the clock as cut. Readings only use natural finishes."""
    dev = model.get_input_embeddings().weight.device
    enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
    stops = stop_ids(model, tok, model_id)
    if getattr(model, "_cache", None) is not None:
        model._cache = None
    gc.collect()                                     # the previous batch's cache must be gone before this one starts
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    torch.manual_seed(seed)
    extra = None
    if _FAST.get("on") and is_harmony(model_id):     # ledger 188: in-place K/V cache for the grouped-attention path
        import fastpath as FP
        extra = {"past_key_values": FP.slab_cache(model)}
    toks, done, cut, row_steps = gen_compact(model, enc["input_ids"], enc["attention_mask"], cap, stops, tok.pad_token_id, deadline, seg, extra=extra)
    closed0 = (not is_harmony(model_id)) and "</think>" in prompts[0][-40:]
    res = []
    for g, d in zip(toks, done):
        n = next((i for i, t in enumerate(g) if t in stops), len(g))
        text = tok.decode(g[:n], skip_special_tokens=False)
        res.append(dict(answer=parse_answer(answer_prefix + text) if (d or answer_prefix) else None, forced=(not d) and n >= cap, natural=bool(d), n_tokens=n, cut=cut,
                        closed=closed0 or closed_reasoning(text, model_id), tail=text[-160:], row_steps=row_steps,
                        full=final_text(text, model_id) if d else "", **text_stats(text)))
    return res


def self_test_compact(model, tok, prompt_a, prompt_b, steps=48, seg=16, after=16):
    """Known-answer check, run once per model before gen_compact is trusted. With greedy decoding, rows generated in
    segments with one row removed after the first segment must give the same tokens as one ordinary generate() call."""
    dev = model.get_input_embeddings().weight.device
    enc = tok([prompt_a, prompt_b, prompt_a], return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
    ids, mask = enc["input_ids"], enc["attention_mask"]
    pad = tok.pad_token_id
    ref = model.generate(input_ids=ids, attention_mask=mask, do_sample=False, max_new_tokens=steps, pad_token_id=pad,
                         eos_token_id=[pad], return_dict_in_generate=True).sequences[:, ids.shape[1]:]
    if ref.shape[1] < steps or bool((ref == pad).any()):
        return None, "reference run stopped early"
    toks, done, _, _ = gen_compact(model, ids, mask, steps, {pad}, pad, time.time() + 600, seg=seg, sample=False, test_drop={1})
    same = [sum(int(a == b) for a, b in zip(toks[r][seg:seg + after], ref[r, seg:seg + after].tolist())) / after for r in (0, 2)]
    ok = bool(done[1] and not done[0] and not done[2] and len(toks[0]) == steps and min(same) >= 0.75)
    return ok, f"row removed {done[1]}, tokens equal after removal {same[0]:.2f}/{same[1]:.2f}"


# ---- fast decode path for gpt-oss (miners6/eng/fastpath.py, ledger 186-188): grouped attention + slab cache, opt-in ----
_FAST = {"on": False}


@torch.no_grad()
def enable_fastpath(model, tok, prompt_a, prompt_b, steps=64):
    """Known-answer check on the loaded model, then switch on: greedy tokens of 3 rows (one left-padded) with the fast
    path must equal the current path's on >= 95% of positions (bf16 kernels may differ in the last bit). Off otherwise."""
    import fastpath as FP
    if getattr(model.config, "model_type", "") != "gpt_oss":
        return False, "not gpt-oss"
    dev = model.get_input_embeddings().weight.device
    enc = tok([prompt_a, prompt_b, prompt_a], return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
    kw = dict(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"], do_sample=False, max_new_tokens=steps,
              pad_token_id=tok.pad_token_id, eos_token_id=[tok.pad_token_id])
    FP.uninstall()
    _FAST["on"] = False
    ref = model.generate(**kw)[:, enc["input_ids"].shape[1]:]
    if not FP.install(model):
        return False, "install refused"
    try:
        got = model.generate(past_key_values=FP.slab_cache(model), **kw)[:, enc["input_ids"].shape[1]:]
        n = min(ref.shape[1], got.shape[1])
        agree = float((ref[:, :n] == got[:, :n]).float().mean()) if n else 0.0
    except Exception as exc:
        FP.uninstall()
        return False, f"error {type(exc).__name__}: {str(exc)[:80]}"
    ok = n == steps and agree >= 0.95
    if not ok:
        FP.uninstall()
    _FAST["on"] = ok
    return ok, f"greedy agreement {agree:.3f} over {n} steps"


# ---- fast decode path for the sink-free 7B/8B models (fast7b.py, ledger 357): own runs only, opt-in, self-checked ----
_FAST7 = {"on": set(), "use": False, "events": [], "mode": "sdpa", "batches": 0}   # use: set per spec by the caller


def enable_fast7b(model, tok, model_id, prompt_a, prompt_b, steps=64, greedy=32, mode="sdpa", min_tf=0.99):
    """Known-answer check on the loaded model (fast7b.self_check: teacher-forced argmax agreement >= min_tf, identical
    greedy continuation, sabotage arm must fail); the fast path is used for model_id only if it passes."""
    import fast7b as F7
    _FAST7["on"].discard(model_id)
    if is_harmony(model_id):
        return False, "gpt-oss has its own path", {}
    _FAST7["mode"] = mode
    try:
        ok, detail, num = F7.self_check(model, tok, prompt_a, prompt_b, steps=steps, greedy=greedy, mode=mode, min_tf=min_tf)
    finally:
        F7.uninstall()
    if ok:
        _FAST7["on"].add(model_id)
    return ok, detail, num
