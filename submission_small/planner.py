"""Budget planning for the capped-solve reading. Pure Python so it can be unit-tested without a model.

Facts it is built on: (1) every call needs at least one generation batch, and a batch lasts about
cap * ms_per_step whatever the number of rows; (2) the cap must be the same for every problem in a
run, or readings are not comparable; (3) rows are limited by GPU memory."""


def choose_cap(ms_per_step, total_seconds, calib_batches, expected_calls, cap_min, cap_max, safety=0.85):
    """One cap for the whole run: the budget divided over all the batches we expect to need."""
    batches = max(1, calib_batches + expected_calls)
    cap = int(safety * total_seconds * 1000.0 / (ms_per_step * batches))
    return max(cap_min, min(cap_max, cap)), cap >= cap_min


def choose_rows(cap, prompt_tokens, kv_bytes_per_token, free_bytes, rows_hard_max, safety=0.6):
    """Largest batch whose key/value cache fits in the free memory."""
    per_row = (cap + prompt_tokens + 64) * kv_bytes_per_token
    return max(1, min(rows_hard_max, int(safety * free_bytes / max(per_row, 1))))


def choose_k(n_texts, rows, k_min, k_max):
    """Attempts per problem: fill one batch if possible."""
    if n_texts <= 0:
        return k_min
    return max(k_min, min(k_max, rows // n_texts))


# ---- row-dependent timing (measured on the contest server, ledger 38: about 10 ms + 0.62 ms per row) ----

def fit_step_model(rows_a, ms_a, rows_b, ms_b, a_min=1.0, b_min=0.0):
    """ms per step = a + b * rows, from two measurements; floors guard against a noisy fit."""
    if rows_b == rows_a:
        return max(ms_a, a_min), b_min
    b = max(b_min, (ms_b - ms_a) / (rows_b - rows_a))
    a = max(a_min, ms_a - b * rows_a)
    return a, b


def cap_for_first_call(a, b, allow_s, n_texts, k_min, cap_min, cap_max, lcf, safety):
    """Largest cap for which K_min attempts on every problem of this call fit its time allowance."""
    ms = lcf * (a + b * max(n_texts, 1) * k_min)
    cap = int(safety * allow_s * 1000.0 / ms)
    return max(cap_min, min(cap_max, cap)), cap >= cap_min


def k_and_rows(a, b, allow_s, cap, n_texts, k_min, k_max, rows_mem, lcf, safety):
    """Attempts per problem and rows per batch so that ONE batch fits the allowance."""
    budget_ms_per_step = safety * allow_s * 1000.0 / max(cap * lcf, 1.0)
    rows_time = int((budget_ms_per_step - a) / b) if b > 0 else rows_mem
    rows = max(1, min(rows_mem, rows_time))
    k = max(k_min, min(k_max, rows // max(n_texts, 1)))
    return k, max(rows, k)


# ---- attempts per problem from the time left (ledger 72, 79) ----

def batch_seconds(rows, cap, a_ms, b_ms, used=1.0):
    """One generation batch: every step pays a fixed cost while any row is unfinished, plus a per-row cost for the
    share of row-steps actually run (`used` < 1 when finished rows are removed from the batch)."""
    return cap * (a_ms + used * b_ms * rows) / 1000.0


def call_seconds(n_new, k, rows_max, cap, a_ms, b_ms, used=1.0):
    per = max(1, rows_max // k)                       # problems per batch
    full, rest = divmod(n_new, per)
    return full * batch_seconds(per * k, cap, a_ms, b_ms, used) + (batch_seconds(rest * k, cap, a_ms, b_ms, used) if rest else 0.0)


def plan_k(n_new, new_history, left_calls, seconds_left, primary_share, k_min, k_max, future_factor,
           rows_max, cap, a_ms, b_ms, used=1.0, scale=1.0):
    """Attempts per new problem for this call: the largest K whose predicted time fits this call's share of the
    time left. Later calls are assumed to bring `future_factor` times the average number of new problems per call so
    far, and enough is always left for them to take a minimum reading. Returns (K, allowance, predicted seconds)."""
    if n_new <= 0:
        return k_min, 0.0, 0.0
    hist = list(new_history) + [n_new]
    avg_new = sum(hist) / len(hist)
    later = max(left_calls - 1, 0)
    cost = lambda n, k: scale * call_seconds(n, k, rows_max, cap, a_ms, b_ms, used)
    pool = max(0.0, seconds_left * primary_share - 30.0)
    floor = later * cost(max(1, int(round(avg_new))), k_min) if later else 0.0
    allow = max(0.0, min(pool * n_new / (n_new + future_factor * avg_new * later), pool - floor))
    k = k_min
    for cand in range(k_min, k_max + 1):
        if cost(n_new, cand) <= allow:
            k = cand
    return k, allow, cost(n_new, k)


# ---- top-up: spare time of a call -> more attempts on this call's problems (ledger 110) ----

def topup_seconds(rows, rows_max, cap, a_ms, b_ms, used=1.0, scale=1.0):
    full, rest = divmod(rows, max(rows_max, 1))
    return scale * (full * batch_seconds(rows_max, cap, a_ms, b_ms, used) + (batch_seconds(rest, cap, a_ms, b_ms, used) if rest else 0.0))


def plan_topup(cur, prio, targets, allow, rows_max, cap, a_ms, b_ms, used=1.0, scale=1.0):
    """Extra attempts per problem. `cur`: attempts so far per problem; `prio`: problems, most uncertain decision first;
    `targets`: attempt levels filled in turn (every problem to the first level before any goes to the next).
    Increments are taken in that order while the predicted time of all of them together fits `allow`; the first one that
    does not fit ends the plan, so the order is never broken. Returns ({problem: extra attempts}, predicted seconds)."""
    add, rows = {}, 0
    for tgt in targets:
        for t in prio:
            have = cur[t] + add.get(t, 0)
            if have >= tgt:
                continue
            if topup_seconds(rows + tgt - have, rows_max, cap, a_ms, b_ms, used, scale) > allow:
                return add, topup_seconds(rows, rows_max, cap, a_ms, b_ms, used, scale) if rows else 0.0
            add[t] = add.get(t, 0) + tgt - have
            rows += tgt - have
    return add, topup_seconds(rows, rows_max, cap, a_ms, b_ms, used, scale) if rows else 0.0
