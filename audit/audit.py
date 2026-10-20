"""Generalisation audit of a contest entry from two CSV files: the tables of Sections 2.2 and 2.3 of the report.

usage:
  python3 audit.py ROWS.csv CHANGES.csv --board NAME:CASES:NEG:OBSERVED:ROWSETS [--board ...] [--kept GAIN] [--draws D1,D2]

Needs Python 3.8+ and numpy only. CPU, a few seconds. Worked example (v95, the report's main entry):
  python3 audit.py v95_rows.csv v95_changes.csv --board main:21:10:16/19:all,fresh \
      --board small:14:7:10/9/8:small,small+fresh --draws 19,17,18,16 > audit_v95.out
  (inputs from make_v95_inputs.py; the output reprints lane G's g1 / g3 / g5 numbers for v95, ledger 509)

ROWS.csv, one row per labelled public row (header required; extra columns are ignored):
  template  cluster id for the bootstrap (rows of one template are resampled together)
  label     1 = the positive class (here non-robust), 0 = the other class (robust)
  call      the entry's OUT-OF-SAMPLE call for the row, same coding (e.g. leave-one-template-out refits); the script
            does not refit anything: whatever was fitted on labels must already be held out when `call` is made
  fresh     1 if the row was not seen while the entry was built (e.g. newly published problems), else 0
  subset    optional; names of row subsets separated by ';' (e.g. 'small' for the small track's configurations)
CHANGES.csv, one row per candidate change tried against the board (header required):
  name, changed (hidden answers the change altered), right (how many of those were right; validation inference)

--board NAME:CASES:NEG:OBSERVED:ROWSETS  a board of CASES hidden cases, NEG of them label 0, observed score OBSERVED
         (several observed scores: separate by '/'); ROWSETS = comma list of 'all', 'fresh' or a subset name, '+' for
         an intersection (e.g. 'small+fresh').
--kept   observed board gain kept by keep-if-better selection; default: the sum over changes of max(2 right - changed, 0)
--draws  board scores of reruns on the SAME hidden cases (reading noise only), for comparison with the case-sampling SD

Table 1 (Section 2.2): accuracy of the out-of-sample calls with a template-cluster bootstrap 95% interval (10,000
resamples), the accuracy at the board's class mix (each class's recall weighted by the board's class counts), and the
predicted board score: Binomial(CASES, p) mixed over the bootstrap p's (model-based), with P(score <= observed).
Table 2 (Section 2.3): the board gain that 'keep a change only if the board score rises' yields when every changed
answer is right with probability 0.5 (coin flips), 0.6 or 0.7 (model-based; 200,000 simulations), against the gain kept.
Seeds are fixed (bootstrap 17, selection 5), so the output is deterministic.
"""
import argparse
import csv
import math
import sys

import numpy as np

B_BOOT, SEED_BOOT, N_SEL, SEED_SEL = 10000, 17, 200000, 5


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tboot(T, fn, B=B_BOOT, seed=SEED_BOOT):
    """Template-cluster bootstrap: resample templates with replacement; fn(row index array) -> value (NaN dropped)."""
    rng = np.random.default_rng(seed)
    U = np.unique(T)
    by = {u: np.where(T == u)[0] for u in U}
    out = []
    for _ in range(B):
        idx = np.concatenate([by[u] for u in rng.choice(U, len(U), replace=True)])
        v = fn(idx)
        if v is not None and not np.isnan(v):
            out.append(v)
    out = np.array(out)
    return np.percentile(out, 2.5), np.percentile(out, 97.5), out


def mix_acc(y, c, neg, pos):
    """Accuracy on a set with `neg` label-0 and `pos` label-1 cases: per-class recall weighted by the class counts."""
    if not ((y == 1).any() and (y == 0).any()):
        return np.nan
    return (neg * (c[y == 0] == 0).mean() + pos * (c[y == 1] == 1).mean()) / (neg + pos)


def binom_pmf(n, p):
    k = np.arange(n + 1)
    return np.array([math.comb(n, int(i)) for i in k], float) * p ** k * (1 - p) ** (n - k)


def rowset_mask(name, fresh, subsets):
    m = np.ones(len(fresh), bool)
    for part in name.split("+"):
        if part == "all":
            continue
        m &= fresh if part == "fresh" else np.array([part in s for s in subsets])
    return m


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("rows")
    ap.add_argument("changes")
    ap.add_argument("--board", action="append", required=True)
    ap.add_argument("--kept", type=int)
    ap.add_argument("--draws")
    a = ap.parse_args(argv)

    R = read_csv(a.rows)
    T = np.array([r["template"] for r in R])
    y = np.array([int(r["label"]) for r in R])
    c = np.array([int(r["call"]) for r in R])
    fresh = np.array([int(r.get("fresh") or 0) == 1 for r in R])
    subsets = [set(filter(None, (r.get("subset") or "").split(";"))) for r in R]
    P = print
    P("# Generalisation audit (audit.py). Labels: accuracy = measured on the given out-of-sample calls; predicted board "
      "and selection null = model-based.")
    P(f"rows {len(R)} (label 0: {int((y == 0).sum())}, label 1: {int((y == 1).sum())}) on {len(np.unique(T))} templates; "
      f"fresh rows {int(fresh.sum())} on {len(np.unique(T[fresh]))} templates")

    P("\n## Table 1. Out-of-sample accuracy against the board (template-cluster bootstrap, 10,000 resamples)")
    P("| Board | Row set | Rows | Accuracy [95%] | At the board's class mix [95%] | Predicted board, expected (90% range) "
      "| Observed | P(score <= observed) |")
    P("|---|---|---|---|---|---|---|---|")
    for spec in a.board:
        name, n, neg, obs, sets = spec.split(":")
        n, neg = int(n), int(neg)
        obs = [int(o) for o in obs.split("/")]
        for rs in sets.split(","):
            m = rowset_mask(rs, fresh, subsets)
            yy, cc, TT = y[m], c[m], T[m]
            acc = (yy == cc).mean()
            lo, hi, _ = tboot(TT, lambda ix: (cc[ix] == yy[ix]).mean())
            p0 = mix_acc(yy, cc, neg, n - neg)
            mlo, mhi, ps = tboot(TT, lambda ix: mix_acc(yy[ix], cc[ix], neg, n - neg))
            pmf = np.mean([binom_pmf(n, p) for p in ps], axis=0)
            cdf = np.cumsum(pmf)
            q05, q95 = int(np.searchsorted(cdf, 0.05)), int(np.searchsorted(cdf, 0.95))
            P(f"| {name} ({n} cases, {neg} label 0) | {rs} | {int(m.sum())} | {int((yy == cc).sum())}/{int(m.sum())} = "
              f"{acc:.3f} [{lo:.3f}, {hi:.3f}] | {p0:.3f} [{mlo:.3f}, {mhi:.3f}] | {n * p0:.1f} ({q05} to {q95}) | "
              f"{', '.join(map(str, obs))} | {', '.join(f'{cdf[o]:.2f}' for o in obs)} |")
    if a.draws:                                      # compared with the first board, all rows
        d = np.array([float(x) for x in a.draws.split(",")])
        n0, neg0 = (int(v) for v in a.board[0].split(":")[1:3])
        pm = mix_acc(y, c, neg0, n0 - neg0)
        P(f"\nreruns on the same hidden cases: mean {d.mean():.2f}, SD {d.std(ddof=1):.2f} (reading noise only); binomial SD "
          f"of a new {n0}-case set at p {pm:.3f}: {math.sqrt(n0 * pm * (1 - pm)):.2f} (case sampling as well)")

    C = read_csv(a.changes)
    m_ = np.array([int(r["changed"]) for r in C])
    r_ = np.array([int(r["right"]) for r in C])
    kept = a.kept if a.kept is not None else int(np.clip(2 * r_ - m_, 0, None).sum())
    P("\n## Table 2. Keep-if-better selection against a null (model-based; 200,000 simulations)")
    P("candidates (changed, right): " + "; ".join(f"{r['name']} ({r['changed']}, {r['right']})" for r in C))
    P(f"changed answers {int(m_.sum())}, right {int(r_.sum())}; observed kept board gain {kept:+d}")
    P("| Each changed answer right with probability | Expected kept gain | 90% range | P(kept gain >= observed) |")
    P("|---|---|---|---|")
    rng = np.random.default_rng(SEED_SEL)
    for p in (0.5, 0.6, 0.7):
        X = 2 * rng.binomial(m_[None, :], p, size=(N_SEL, len(m_))) - m_[None, :]
        G = np.clip(X, 0, None).sum(1)
        P(f"| {p} | {G.mean():+.2f} | {int(np.percentile(G, 5))} to {int(np.percentile(G, 95))} | {np.mean(G >= kept):.2f} |")
    P("Reading: a kept gain inside the coin-flip range cannot show that the kept changes generalise (nor that they do not).")


if __name__ == "__main__":
    sys.exit(main())
