"""Fast decode path for the judged decoder models WITHOUT attention sinks (Skywork-OR1-Math-7B = Qwen2, 28 query / 4 KV
heads; DeepSeek-R1-0528-Qwen3-8B = Qwen3, 32 / 8; Olmo-3-7B-Think = Olmo3, 32 / 32 with a 4,096-token sliding window on 24
of 32 layers) under transformers 5.13 with sdpa attention. Ledger 357.

Why. transformers' sdpa_attention_forward uses SDPA's own grouped-query mode only when attention_mask is None; our batches
are left-padded, so a mask is always present and every decode step repeat_kv-copies K and V G times (G = 7 for Skywork)
and SDPA then reads the G-fold copies. The default DynamicLayer also torch.cat's the whole cache every step (and the
sliding-window layer cat's its whole window). This module removes both, as fastpath.py did for gpt-oss (ledger 186-196):
  (a) grouped attention: at decode (one query token) the G query heads of each KV head are folded into SDPA's query axis
      ([B, H, 1, D] -> [B, Hkv, G, D]), so K and V are read once and never copied. The mask [B, 1, 1, L] (boolean for
      sdpa, additive for eager) broadcasts over the folded axis exactly as it broadcasts over heads in the default path.
      Prefill (more than one query token), MHA layers (G = 1), sinks, dropout and any unexpected mask shape go to the
      original function unchanged.
  (b) slab cache: new K/V are written in place into buffers grown in chunks (full layers) or compacted once per chunk
      (sliding-window layers, which return exactly the tokens DynamicSlidingWindowLayer returns, in the same order).
For Olmo-3-7B (G = 1) only (b) applies.

Everything is opt-in and reversible:
    import fast7b as F7
    with F7.active(model):                         # (a) registered for sdpa while the block runs; restored on exit
        model.generate(..., past_key_values=F7.slab_cache(model), use_cache=True)   # (b) a FRESH cache per call
    ok, detail = F7.self_check(model, tok, prompt_a, prompt_b)       # known-answer check, sabotage arm included
use_cache=True matters: Olmo-3-7B-Think's config.json says use_cache false; from_pretrained leaves generation_config.use_cache
None (generate then makes its own cache), but a cache passed in while use_cache resolves to False is filled with the whole
sequence every step and gives wrong tokens (seen on a tiny Olmo3 built with from_config).
Sabotage switch (tests only): active(model, sabotage="heads") gives query head h the KV head h % Hkv instead of h // G;
sabotage="cache" makes the slab overwrite the previous token's K/V with the new token's (an off-by-one cache bug).
"""
import contextlib

import torch
from torch.nn import functional as F
from transformers.cache_utils import DynamicCache, DynamicLayer, DynamicSlidingWindowLayer
from transformers.generation.logits_process import LogitsProcessor, LogitsProcessorList
from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS

_MISSING = object()
_ST = {"orig": None, "prev": _MISSING, "installed": False, "mods": set(), "sabotage": None, "mode": "sdpa",
       "n_fast": 0, "n_orig": 0}


def _orig_call(module, query, key, value, attention_mask, dropout, scaling, is_causal, kwargs):
    _ST["n_orig"] += 1
    return _ST["orig"](module, query, key, value, attention_mask, dropout=dropout, scaling=scaling, is_causal=is_causal, **kwargs)


def grouped_attention(module, query, key, value, attention_mask, dropout=0.0, scaling=None, is_causal=None, **kwargs):
    """Drop-in for transformers' sdpa_attention_forward. Decode steps of the installed model's grouped layers are computed
    with the G query heads of KV head kv (heads kv*G .. kv*G+G-1, repeat_kv's mapping) on SDPA's query axis."""
    B, H, Q, D = query.shape
    Hkv = key.shape[1]
    G = H // max(Hkv, 1)
    m = attention_mask
    if (id(module) not in _ST["mods"] or Q != 1 or G <= 1 or Hkv * G != H or dropout or kwargs.get("output_attentions")
            or getattr(module, "sinks", None) is not None or key.shape[-1] != D
            or (m is not None and (m.dim() != 4 or m.shape[0] not in (1, B) or m.shape[1] != 1 or m.shape[2] != 1))):
        return _orig_call(module, query, key, value, attention_mask, dropout, scaling, is_causal, kwargs)
    _ST["n_fast"] += 1
    sab = _ST["sabotage"] == "heads"
    qf = query.reshape(B, G, Hkv, D).transpose(1, 2) if sab else query.reshape(B, Hkv, G, D)
    if _ST["mode"] == "matmul":                      # explicit form (eager arithmetic: fp32 softmax), K/V still read once
        w = torch.matmul(qf, key.transpose(2, 3)) * (scaling if scaling is not None else D ** -0.5)
        if m is not None:
            w = w.masked_fill(~m, float("-inf")) if m.dtype == torch.bool else w + m
        o = torch.matmul(F.softmax(w, dim=-1, dtype=torch.float32).to(value.dtype), value)
    else:
        o = F.scaled_dot_product_attention(qf, key, value, attn_mask=m, dropout_p=0.0, scale=scaling, is_causal=False)
    if sab:
        o = o.transpose(1, 2)                        # back to head order g*Hkv + kv (only the K/V assignment is wrong)
    return o.reshape(B, 1, H, D), None              # = default's attn_output.transpose(1, 2).contiguous() for Q == 1


def groups(model):
    """Largest query-heads-per-KV-head ratio over the model's attention layers (1 = multi-head attention)."""
    return max([int(getattr(m, "num_key_value_groups", 1)) for m in model.modules()
                if hasattr(m, "num_key_value_groups") and hasattr(m, "layer_idx")] or [1])


def install(model, mode="sdpa"):
    """Register grouped_attention for 'sdpa' (local mapping of transformers' ALL_ATTENTION_FUNCTIONS), acting only on
    this model's grouped attention layers. Returns False (nothing installed) for MHA models, sinks or a non-sdpa model."""
    uninstall()
    mods = [m for m in model.modules() if hasattr(m, "num_key_value_groups") and hasattr(m, "layer_idx")
            and int(m.num_key_value_groups) > 1 and getattr(m, "sinks", None) is None]
    impl = {getattr(getattr(m, "config", None), "_attn_implementation", None) for m in mods}
    if not mods or impl != {"sdpa"}:
        return False
    _ST["prev"] = ALL_ATTENTION_FUNCTIONS._local_mapping.get("sdpa", _MISSING)
    _ST["orig"] = ALL_ATTENTION_FUNCTIONS["sdpa"]
    _ST["mods"] = {id(m) for m in mods}
    _ST["mode"] = mode
    ALL_ATTENTION_FUNCTIONS["sdpa"] = grouped_attention
    _ST["installed"] = True
    return True


def uninstall():
    if _ST["installed"]:
        if _ST["prev"] is _MISSING:
            ALL_ATTENTION_FUNCTIONS._local_mapping.pop("sdpa", None)
        else:
            ALL_ATTENTION_FUNCTIONS["sdpa"] = _ST["prev"]
    _ST.update(installed=False, prev=_MISSING, mods=set())


@contextlib.contextmanager
def active(model, sabotage=None, mode="sdpa"):
    """Fast attention (if applicable) and the slab sabotage flag for the duration of the block; always restored."""
    _ST["sabotage"] = sabotage
    try:
        install(model, mode)
        yield _ST["installed"]
    finally:
        uninstall()
        _ST["sabotage"] = None


class SlabLayer(DynamicLayer):
    """Full-attention layer: K/V written in place into a buffer grown in `chunk`-token steps (one copy per chunk instead
    of a torch.cat copy of the whole cache every step). keys/values are views of the filled part."""
    chunk = 512

    def lazy_initialization(self, key_states, value_states):
        super().lazy_initialization(key_states, value_states)
        self.n, self.kbuf, self.vbuf = 0, None, None

    def _grow(self, need, like):
        B, Hh, _, D = like.shape
        cap = ((need + self.chunk - 1) // self.chunk) * self.chunk
        nk = torch.empty((B, Hh, cap, D), dtype=like.dtype, device=like.device)
        nv = torch.empty((B, Hh, cap, D), dtype=like.dtype, device=like.device)
        if self.kbuf is not None and self.n:
            nk[:, :, :self.n].copy_(self.kbuf[:, :, :self.n])
            nv[:, :, :self.n].copy_(self.vbuf[:, :, :self.n])
        self.kbuf, self.vbuf = nk, nv

    def update(self, key_states, value_states, *args, **kwargs):
        if not self.is_initialized:
            self.lazy_initialization(key_states, value_states)
        q = key_states.shape[-2]
        if self.kbuf is None or self.n + q > self.kbuf.shape[-2] or self.kbuf.shape[0] != key_states.shape[0]:
            self._grow(self.n + q, key_states)
        self.kbuf[:, :, self.n:self.n + q].copy_(key_states)
        self.vbuf[:, :, self.n:self.n + q].copy_(value_states)
        if _ST["sabotage"] == "cache" and q == 1 and self.n:          # sabotage: previous token's K/V lost
            self.kbuf[:, :, self.n - 1:self.n].copy_(key_states)
            self.vbuf[:, :, self.n - 1:self.n].copy_(value_states)
        self.n += q
        self.keys, self.values = self.kbuf[:, :, :self.n], self.vbuf[:, :, :self.n]
        return self.keys, self.values

    def get_seq_length(self):
        return self.n if self.is_initialized else 0

    def batch_select_indices(self, indices):
        if self.is_initialized and self.n:
            self.kbuf, self.vbuf = self.kbuf[indices], self.vbuf[indices]
            self.keys, self.values = self.kbuf[:, :, :self.n], self.vbuf[:, :, :self.n]

    def crop(self, max_length):
        raise NotImplementedError("SlabLayer does not support crop")

    def batch_repeat_interleave(self, repeats):
        raise NotImplementedError("SlabLayer does not support batch_repeat_interleave")


class SlabSlidingLayer(DynamicSlidingWindowLayer):
    """Sliding-window layer with in-place writes. Returns exactly what DynamicSlidingWindowLayer.update returns (the last
    min(seen, window - 1) cached tokens followed by the new ones, in order) and keeps the same cumulative_length, so the
    masks built from get_mask_sizes are unchanged. The kept window is moved to the buffer front once per `chunk` steps."""
    chunk = 256

    def lazy_initialization(self, key_states, value_states):
        super().lazy_initialization(key_states, value_states)
        self.kbuf = self.vbuf = None
        self.s = self.e = 0                           # kept tokens are buf[:, :, s:e]

    def update(self, key_states, value_states, *args, **kwargs):
        if not self.is_initialized:
            self.lazy_initialization(key_states, value_states)
        q = key_states.shape[-2]
        self.cumulative_length += q
        if self.kbuf is None or self.e + q > self.kbuf.shape[-2] or self.kbuf.shape[0] != key_states.shape[0]:
            B, Hh, _, D = key_states.shape
            kept = self.e - self.s
            cap = max(kept + q, self.sliding_window - 1 + q) + self.chunk
            nk = torch.empty((B, Hh, cap, D), dtype=key_states.dtype, device=key_states.device)
            nv = torch.empty((B, Hh, cap, D), dtype=key_states.dtype, device=key_states.device)
            if self.kbuf is not None and kept:
                nk[:, :, :kept].copy_(self.kbuf[:, :, self.s:self.e])
                nv[:, :, :kept].copy_(self.vbuf[:, :, self.s:self.e])
            self.kbuf, self.vbuf, self.s, self.e = nk, nv, 0, kept
        self.kbuf[:, :, self.e:self.e + q].copy_(key_states)
        self.vbuf[:, :, self.e:self.e + q].copy_(value_states)
        if _ST["sabotage"] == "cache" and q == 1 and self.e > self.s:
            self.kbuf[:, :, self.e - 1:self.e].copy_(key_states)
            self.vbuf[:, :, self.e - 1:self.e].copy_(value_states)
        full_k, full_v = self.kbuf[:, :, self.s:self.e + q], self.vbuf[:, :, self.s:self.e + q]
        self.e += q
        if self.sliding_window > 1:                   # default keeps full[..., -(window - 1):, :]
            self.s = max(self.s, self.e - (self.sliding_window - 1))
        self.keys, self.values = self.kbuf[:, :, self.s:self.e], self.vbuf[:, :, self.s:self.e]
        return full_k, full_v

    def batch_select_indices(self, indices):
        if self.is_initialized and self.kbuf is not None and self.e > self.s:
            self.kbuf, self.vbuf = self.kbuf[indices], self.vbuf[indices]
            self.keys, self.values = self.kbuf[:, :, self.s:self.e], self.vbuf[:, :, self.s:self.e]

    def crop(self, max_length):
        raise NotImplementedError("SlabSlidingLayer does not support crop")

    def batch_repeat_interleave(self, repeats):
        raise NotImplementedError("SlabSlidingLayer does not support batch_repeat_interleave")


def slab_cache(model, chunk=512, sliding_chunk=256):
    """DynamicCache with every plain DynamicLayer -> SlabLayer and every DynamicSlidingWindowLayer -> SlabSlidingLayer
    (same window); any other layer kind (linear attention, indexed, quantized) is left as it is. One per generate()."""
    cache = DynamicCache(config=model.config)
    for i, layer in enumerate(cache.layers):
        if type(layer) is DynamicLayer:
            cache.layers[i] = SlabLayer()
            cache.layers[i].chunk = chunk
        elif type(layer) is DynamicSlidingWindowLayer:
            cache.layers[i] = SlabSlidingLayer(sliding_window=layer.sliding_window)
            cache.layers[i].chunk = sliding_chunk
    return cache


@torch.no_grad()
def cache_unit(model, chunk=512, sliding_chunk=256):
    """Known-answer check of the slab layers against transformers' own layers on the model's device, with the model's
    real window and the chunk sizes slab_cache uses: random K/V, a prompt-sized first update, then single-token updates
    past one buffer growth / window compaction, a row reorder (batch_select_indices) half-way. Returned K/V, mask sizes
    and lengths must be identical at every step. The 64-token generation check never reaches a 4,096-token window; this
    does. Returns (ok, detail)."""
    dev = model.get_input_embeddings().weight.device
    kinds = {}
    for layer in slab_cache(model, chunk, sliding_chunk).layers:
        if type(layer) is SlabLayer:
            kinds.setdefault("full", (DynamicLayer, lambda: SlabLayer(), chunk))
        elif type(layer) is SlabSlidingLayer:
            w = layer.sliding_window
            kinds.setdefault(f"sliding {w}", (lambda w=w: DynamicSlidingWindowLayer(sliding_window=w),
                                              lambda w=w: SlabSlidingLayer(sliding_window=w), sliding_chunk, w))
    out = []
    g = torch.Generator(device="cpu").manual_seed(7)
    for name, spec in kinds.items():
        ref_cls, fast_cls, ch = spec[0], spec[1], spec[2]
        w = spec[3] if len(spec) > 3 else 0
        a = ref_cls() if name != "full" else DynamicLayer()
        b = fast_cls()
        b.chunk = ch
        steps = (w + ch + 64) if w else (2 * ch + 64)
        first = max(5, w - 40) if w else ch - 20
        bad, half = 0, steps // 2
        for s in range(steps):
            q = first if s == 0 else 1
            k = torch.randn(2, 2, q, 8, generator=g).to(dev)
            v = torch.randn(2, 2, q, 8, generator=g).to(dev)
            if s == half:
                idx = torch.tensor([1, 0], device=dev)
                a.batch_select_indices(idx)
                b.batch_select_indices(idx)
            same_sizes = a.get_mask_sizes(q) == b.get_mask_sizes(q)
            ka, va = a.update(k, v)
            kb, vb = b.update(k, v)
            if not (same_sizes and a.get_seq_length() == b.get_seq_length() and ka.shape == kb.shape
                    and torch.equal(ka, kb) and torch.equal(va, vb)):
                bad += 1
        out.append((name, steps, bad))
    ok = all(b == 0 for _, _, b in out)
    return ok, ", ".join(f"{n} {s} updates {'identical' if b == 0 else f'{b} DIFFER'}" for n, s, b in out)


def slab_counts(model):
    c = slab_cache(model)
    return sum(type(x) is SlabLayer for x in c.layers), sum(type(x) is SlabSlidingLayer for x in c.layers), len(c.layers)


class TeacherForce(LogitsProcessor):
    """Records the argmax of the scores at every step, then forces the reference token (teacher forcing inside
    generate(), so the real decode path - position ids, masks, cache - is exercised)."""

    def __init__(self, ref, plen):
        self.ref, self.plen, self.hits, self.n = ref, plen, 0, 0

    def __call__(self, input_ids, scores):
        t = input_ids.shape[1] - self.plen
        want = self.ref[:, t]
        self.hits += int((scores.argmax(-1) == want).sum())
        self.n += int(want.numel())
        out = torch.full_like(scores, float("-inf"))
        out.scatter_(1, want[:, None], 0.0)
        return out

    def agreement(self):
        return self.hits / max(self.n, 1)


@torch.no_grad()
def self_check(model, tok, prompt_a, prompt_b, steps=64, greedy=32, sabotage=True, mode="sdpa", min_tf=0.99, slab_kw=None):
    """Known-answer check on the loaded model. Three rows (a, b, a; b has another length, so rows are left-padded).
    Reference = default path, greedy, `steps` tokens. PASS iff (0) cache_unit passes, (1) teacher-forced next-token argmax agreement of the fast
    path with the reference >= min_tf, (2) the fast path's free greedy continuation equals the reference for `greedy`
    tokens on every row, and (3) the sabotage arm (heads for grouped models, cache for MHA) FAILS (1) or (2).
    Returns (ok, detail, numbers)."""
    dev = model.get_input_embeddings().weight.device
    enc = tok([prompt_a, prompt_b, prompt_a], return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
    ids, mask = enc["input_ids"], enc["attention_mask"]
    plen, pad = ids.shape[1], tok.pad_token_id
    base = dict(input_ids=ids, attention_mask=mask, do_sample=False, pad_token_id=pad, eos_token_id=[pad])
    uninstall()
    ref = model.generate(max_new_tokens=steps, **base)[:, plen:]
    if ref.shape[1] < steps or bool((ref == pad).any()):
        return False, "reference run stopped early", {}
    G = groups(model)
    nf, ns, nl = slab_counts(model)
    skw = dict(slab_kw or {})

    def tf(fast, sab=None):
        rec = TeacherForce(ref, plen)
        lp = LogitsProcessorList([rec])
        if fast:
            with active(model, sabotage=sab, mode=mode):
                model.generate(max_new_tokens=steps, logits_processor=lp, past_key_values=slab_cache(model, **skw), use_cache=True, **base)
        else:
            model.generate(max_new_tokens=steps, logits_processor=lp, **base)
        return rec.agreement()

    def free(sab=None):
        with active(model, sabotage=sab, mode=mode):
            n0 = _ST["n_fast"]
            got = model.generate(max_new_tokens=greedy, past_key_values=slab_cache(model, **skw), use_cache=True, **base)[:, plen:]
            used = _ST["n_fast"] - n0
        return bool(got.shape[1] == greedy and torch.equal(got, ref[:, :greedy])), used

    num = {"groups": G, "slab_full": nf, "slab_sliding": ns, "layers": nl, "rows": 3, "prompt_tokens": plen}
    cu_ok, cu_det = cache_unit(model, **{k: skw[k] for k in ("chunk", "sliding_chunk") if k in skw})
    num["cache_unit"] = cu_ok
    num["tf_default"] = tf(False)
    num["tf_fast"] = tf(True)
    num["greedy_fast"], num["fast_attention_calls"] = free()
    ok = num["tf_fast"] >= min_tf and num["greedy_fast"] and cu_ok
    detail = (f"cache unit ({cu_det}); teacher-forced argmax agreement default {num['tf_default']:.3f} fast {num['tf_fast']:.3f} over "
              f"{3 * steps} positions, greedy {greedy} tokens x 3 rows {'identical' if num['greedy_fast'] else 'DIFFERENT'}")
    if sabotage:
        sab = "heads" if G > 1 else "cache"
        num["sabotage"] = sab
        num["tf_sabotage"] = tf(True, sab)
        num["greedy_sabotage"], _ = free(sab)
        num["sabotage_fails"] = not (num["tf_sabotage"] >= min_tf and num["greedy_sabotage"])
        detail += (f"; sabotage ({sab}) {num['tf_sabotage']:.3f} / greedy {'identical' if num['greedy_sabotage'] else 'different'}"
                   f" -> {'fails as it must' if num['sabotage_fails'] else 'PASSES: check not discriminating'}")
        ok = ok and num["sabotage_fails"]
    detail += (f"; groups {G}, grouped-attention decode calls {num['fast_attention_calls']}, slab layers full {nf} "
               f"sliding {ns} of {nl}")
    return bool(ok), detail, num
