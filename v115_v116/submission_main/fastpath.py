"""Fast decode path for gpt-oss under transformers 5.13 (drop-in module for a submission bundle; NOT applied anywhere).

Why (miners6/eng/time_decomp.py, 31 server batches): batch_ms = 25.6*steps + 0.466*row_steps + 0.481*row_steps*KV/1000.
The KV-length term is 33-40% of a low-effort batch and 42-61% of medium/high batches. gpt-oss has _supports_sdpa=False and
flash/flex are not usable here, so transformers runs `eager_attention_forward`, which per decode step and full-attention
layer (a) torch.cat's the whole K/V cache into a new tensor, (b) repeat_kv-copies K and V 8x (64 query heads / 8 KV heads)
and (c) reads the 8x copies in two matmuls: ~19x the K/V bytes per step (first principles: 0.39 ms per row per 1,000 KV
tokens at 1.8 TB/s; fitted 0.48). This module removes (b)+(c) (grouped attention: the 8 query heads of a group are folded
into the query axis so K/V are read once, ~1x) and (a) (slab cache: K/V written in place into chunk-grown buffers).

Everything is opt-in and reversible:
    import fastpath as FP
    FP.install(model)            # grouped attention in place of eager (gpt-oss only; returns False if not applicable)
    cache = FP.slab_cache(model) # pass as past_key_values on the FIRST generate() of a batch (gen_compact keeps it)
    FP.uninstall()
    FP.TopKTopP(40, 0.95)        # optional LogitsProcessor: top-k then top-p on the 40 survivors (no 201k-vocab sort);
                                 # use with top_k=0, top_p=1.0 in generate(). Same distribution, different random stream.
"""
import torch
from torch.nn import functional as F
from transformers.cache_utils import DynamicCache, DynamicLayer
from transformers.generation.logits_process import LogitsProcessor

_STATE = {"orig": None, "qchunk_elems": 1 << 27, "sabotage": False}


def grouped_sinks_attention(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
    """Same arithmetic as transformers' gpt-oss eager_attention_forward (scores, + mask, cat sinks, - max, softmax in the
    input dtype, drop sink, @ V), but query head h = kv*G + g is folded into the query axis of KV head kv, so K and V are
    never repeated. Prefill is processed in query chunks so the score tensor stays under ~2^27 elements."""
    B, H, Q, D = query.shape
    Hkv, L = key.shape[1], key.shape[-2]
    G = H // Hkv
    sinks = module.sinks
    if _STATE["sabotage"]:                       # sabotage arm: wrong head->group mapping (head h uses KV head h % Hkv)
        query = query.view(B, G, Hkv, Q, D).transpose(1, 2)
        sinks = sinks.view(G, Hkv).t()
    q5 = query.reshape(B, Hkv, G, Q, D)          # a view at decode (Q == 1)
    snk = sinks.reshape(1, Hkv, G, 1, 1)
    step = max(1, int(_STATE["qchunk_elems"] // max(B * H * L, 1)))
    outs = []
    for q0 in range(0, Q, step):
        q1 = min(Q, q0 + step)
        qc = q5[:, :, :, q0:q1].reshape(B, Hkv, G * (q1 - q0), D)
        w = torch.matmul(qc, key.transpose(2, 3)) * scaling              # [B, Hkv, G*q, L]: K read once
        w = w.view(B, Hkv, G, q1 - q0, L)
        if attention_mask is not None:
            w = w + attention_mask[:, :, None, q0:q1, :L]                 # [B,1,1,q,L] broadcast (sliced to L as in eager)
        comb = torch.cat([w, snk.expand(B, Hkv, G, q1 - q0, 1).to(w.dtype)], dim=-1)
        comb = comb - comb.max(dim=-1, keepdim=True).values
        probs = F.softmax(comb, dim=-1, dtype=comb.dtype)
        p = probs[..., :-1].to(value.dtype).reshape(B, Hkv, G * (q1 - q0), L)
        outs.append(torch.matmul(p, value).view(B, Hkv, G, q1 - q0, D))  # V read once
    o = outs[0] if len(outs) == 1 else torch.cat(outs, dim=3)
    o = o.reshape(B, H, Q, D)
    if _STATE["sabotage"]:
        o = o.view(B, Hkv, G, Q, D).transpose(1, 2).reshape(B, H, Q, D)
    return o.transpose(1, 2).contiguous(), None


def install(model, sabotage=False, qchunk_elems=1 << 27):
    """Route gpt-oss eager attention through grouped_sinks_attention. Only for gpt-oss loaded with eager attention."""
    import transformers.models.gpt_oss.modeling_gpt_oss as M
    cfg = getattr(model, "config", None)
    if getattr(cfg, "model_type", "") != "gpt_oss" or getattr(cfg, "_attn_implementation", "eager") != "eager":
        return False
    if _STATE["orig"] is None:
        _STATE["orig"] = M.eager_attention_forward
    _STATE["sabotage"], _STATE["qchunk_elems"] = bool(sabotage), int(qchunk_elems)
    M.eager_attention_forward = grouped_sinks_attention
    return True


def uninstall():
    import transformers.models.gpt_oss.modeling_gpt_oss as M
    if _STATE["orig"] is not None:
        M.eager_attention_forward = _STATE["orig"]
    _STATE["sabotage"] = False


class SlabLayer(DynamicLayer):
    """Full-attention cache layer that writes new K/V in place into a buffer grown in chunks (one copy per `chunk`
    tokens instead of a full torch.cat copy every step). keys/values are views of the filled part."""
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


def slab_cache(model, chunk=512):
    """DynamicCache with SlabLayer for every full-attention layer (sliding layers keep their 127-token cat layer)."""
    cache = DynamicCache(config=model.config)
    types = getattr(model.config.get_text_config(decoder=True), "layer_types", None) or []
    for i, t in enumerate(types):
        if t == "full_attention" and type(cache.layers[i]) is DynamicLayer:
            cache.layers[i] = SlabLayer()
            cache.layers[i].chunk = chunk
    return cache


class TopKTopP(LogitsProcessor):
    """top-k (40) then top-p (0.95) computed on the k survivors only: the same kept set as transformers' TopK followed by
    TopP (TopP removes token j when the probability mass of strictly more likely tokens is >= top_p), without sorting the
    201,088-token vocabulary. Use with generate(top_k=0, top_p=1.0, temperature=1.0)."""

    def __init__(self, k=40, p=0.95):
        self.k, self.p = int(k), float(p)

    def __call__(self, input_ids, scores):
        v, i = torch.topk(scores, self.k, dim=-1)                 # descending
        pr = v.float().softmax(-1)
        excl = pr.cumsum(-1) - pr
        v = v.masked_fill(excl >= self.p, float("-inf"))
        return torch.full_like(scores, float("-inf")).scatter_(-1, i, v)
