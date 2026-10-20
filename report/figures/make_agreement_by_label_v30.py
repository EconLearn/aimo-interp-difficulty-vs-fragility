"""Figure 1 of the four-page report, draft 30: the stand-in's agreement on each labelled public row, by label, on easy
and on hard templates. It replaces draft 29's board figure (make_board_vs_audit_v29.py, kept unchanged; that figure is
now Figure 1 of the supplement).

Data (held files only, CPU, no model runs; computed, post hoc: the labels were seen long before):
  rows       the 71 labelled public rows exactly as decision.json was fitted (lane G, work/miners17/laneG/g_common.py,
             build_fit_data); label y = 1 for non-robust
  agreement  the dress read (Codabench 987666, work/runs/v88_dress_987666.log, 15 October; ledger 440): per template,
             pair_nat of gpt-oss-120b low at K 32 and a 3,000-token cap, the reading the entry deploys (g_common.parse_dress)
  regions    hard = the 17 labelled templates a 2,000-token Olmo-Instruct reader never finishes, fixed before the hard-region
             lab (ledger 267b, 278; g_common.HARD); easy = the other 10 labelled templates
  AUC        within-configuration AUC (non-robust rows compared only with robust rows of the same configuration; higher =
             non-robust reads lower), as in ledger 611 and work/miners19/crp19/X/keyscored.py: the dress read; agreement
             over 80 pooled gpt-oss low attempts from six other held reads; and the share of those 80 attempts that match
             the public answer key (work/miners17/laneX/x_pool.json, xbench.auc_within). Single held reads (K 8 or 16)
             give the range printed last.
  LOTO       the entry's rules (v95) leave-one-template-out on the dress read, as in lane G (g_common.run_policy): errors by
             region; and the same with the key-scored share in place of agreement (keyscored.py's ceiling)
Writes agreement_by_label_v30.png and make_agreement_by_label_v30.out next to this script. Run with the system python3
(matplotlib, pandas, numpy): python3 figures/make_agreement_by_label_v30.py
"""
import collections
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AIMO = os.path.dirname(HERE)
WORK = os.path.join(AIMO, 'work')
sys.path.insert(0, os.path.join(WORK, 'miners17', 'laneG'))
sys.path.insert(0, os.path.join(WORK, 'miners17', 'laneX'))
from g_common import HARD, V95, build_fit_data, parse_dress, run_policy  # noqa: E402
import xbench  # noqa: E402

OUT_PNG = os.path.join(HERE, 'agreement_by_label_v30.png')
OUT_TXT = os.path.join(HERE, 'make_agreement_by_label_v30.out')
INK, MUTED, GRID, SURF = '#0b0b0b', '#52514e', '#d9d8d3', '#fcfcfb'      # make_board_vs_audit_v29.py's tokens
S1, S2 = '#2a78d6', '#c2571a'                                            # robust, non-robust (validated pair)
LINES = []


def say(s=''):
    LINES.append(s)
    print(s)


# ---------------------------------------------------------------- data
D, FIT = build_fit_data()
pool, _ = parse_dress()
y = D.y.values.astype(int)
Tr = D['T'].values
cfg = D.cfg.values
TS = range(1, 29)
hard = np.isin(Tr, sorted(HARD))
agree = {T: pool[T]['prim'] for T in TS}
LOW = xbench.LOW


def pair_nat(att):
    K = len(att)
    c = collections.Counter(a[2] for a in att if a[1] and a[2] is not None)
    return sum(v * (v - 1) for v in c.values()) / (K * (K - 1))


pooled = {T: pair_nat(LOW[T]) for T in TS}
keyacc = {T: float(np.mean([a[3] for a in LOW[T]])) for T in TS}
reads = sorted({a[4] for T in TS for a in LOW[T]})
single = {r: {T: pair_nat([a for a in LOW[T] if a[4] == r]) for T in TS} for r in reads}

R_all = xbench.ROWS
R_hard = [r for r in R_all if r['T'] in HARD]
R_easy = [r for r in R_all if r['T'] not in HARD]
assert sorted((r['T'], r['cfg'], r['y']) for r in R_all) == sorted(zip(Tr.tolist(), cfg.tolist(), y.tolist()))
auc = lambda f, rows: xbench.auc_within({T: 1 - f[T] for T in TS}, rows)

say('# Figure 1, draft 30: agreement by label, easy vs hard templates (computed, post hoc; held files only)')
say(f'rows {len(y)} ({y.sum()} non-robust); hard {hard.sum()} rows on {len(set(Tr[hard]))} templates '
    f'({y[hard].sum()} non-robust); easy {(~hard).sum()} rows on {len(set(Tr[~hard]))} templates '
    f'({(~hard).sum() - y[~hard].sum()} robust)')
say('\n## within-configuration AUC (value, rows, non-robust rows, within-configuration pairs)')
res = {}
for name, f in (('deployed agreement, dress read K 32', agree), ('agreement, 80 pooled attempts', pooled),
                ('key-scored accuracy, 80 pooled attempts', keyacc)):
    a_all, a_hard, a_easy = auc(f, R_all), auc(f, R_hard), auc(f, R_easy)
    res[name] = a_hard[0]
    say(f'{name:42s} all {a_all[0]:.3f} ({a_all[1]}, {a_all[2]}, {a_all[3]}) | hard {a_hard[0]:.3f} '
        f'({a_hard[1]}, {a_hard[2]}, {a_hard[3]}) | easy {a_easy[0]:.3f} ({a_easy[1]}, {a_easy[2]}, {a_easy[3]})')
sh = [auc(single[r], R_hard)[0] for r in reads]
say(f'hard rows: 80 pooled attempts ({80 / 32:.1f}x the deployed K 32) add '
    f'{res["agreement, 80 pooled attempts"] - res["deployed agreement, dress read K 32"]:.3f} AUC; the key-scored share '
    f'{res["key-scored accuracy, 80 pooled attempts"] - res["deployed agreement, dress read K 32"]:.3f}')
say(f'single held reads (K 8 or 16), hard rows: {", ".join(f"{v:.3f}" for v in sh)}; range {min(sh):.3f} to {max(sh):.3f}')

say('\n## the entry (v95 rules) leave-one-template-out on the dress read (lane G run_policy)')
yh = run_policy(D, FIT, pool, V95, 'loto')
err = yh != y
say(f'right {int((~err).sum())}/71; hard {int((~err)[hard].sum())}/{hard.sum()}; easy {int((~err)[~hard].sum())}/'
    f'{(~hard).sum()}; errors on hard rows {int(err[hard].sum())} of {int(err.sum())}')
for i in np.where(err)[0]:
    say(f'   T{Tr[i]:02d} {cfg[i]:8s} {"non-robust" if y[i] else "robust":10s} region {"hard" if hard[i] else "easy"} '
        f'agreement {agree[Tr[i]]:.3f}')
D2 = D.copy()
D2['pair16'] = [keyacc[T] for T in D2['T'].values]
yk = run_policy(D2, FIT, {T: dict(pool[T], prim=keyacc[T]) for T in pool}, V95, 'loto')
say(f'key-scored share in place of agreement (ceiling): right {int((yk == y).sum())}/71; hard {int((yk == y)[hard].sum())}'
    f'/{hard.sum()}; rows changed: '
    + '; '.join(f'T{Tr[i]:02d} {cfg[i]} {"fixed" if yk[i] == y[i] else "broken"}' for i in np.where(yk != yh)[0]))

BAND = (0.555, 0.825)
inb = lambda i: BAND[0] <= agree[Tr[i]] <= BAND[1]
band_r = [i for i in range(len(y)) if hard[i] and y[i] == 0 and inb(i)]
band_n = [i for i in range(len(y)) if hard[i] and y[i] == 1 and inb(i)]
lo = min(agree[Tr[i]] for i in band_r + band_n)
hi = max(agree[Tr[i]] for i in band_r + band_n)
say(f'\n## hard rows with agreement {lo:.3f} to {hi:.3f} ({lo:.2f} to {hi:.2f}): {len(band_r)} robust, {len(band_n)} non-robust')
say('   robust: ' + ', '.join(f'T{Tr[i]:02d} {cfg[i]}' for i in band_r))
say('   non-robust: ' + ', '.join(f'T{Tr[i]:02d} {cfg[i]}' for i in band_n))
t13 = [i for i in range(len(y)) if Tr[i] == 13]
t13txt = ', '.join(cfg[i] + (' non-robust' if y[i] else ' robust') for i in t13)
say(f'T13 rows: {t13txt}; agreement {agree[13]:.3f}')
open(OUT_TXT, 'w').write('\n'.join(LINES) + '\n')


# ---------------------------------------------------------------- figure
def swarm(vals, dy=0.032, dx=0.085):
    """x offsets for a dot strip: each point takes the free slot nearest the centre line (0, +dx, -dx, +2dx, ...)
    among points within dy of it. Deterministic (points placed from the top down)."""
    order = np.argsort(-np.asarray(vals), kind='stable')
    placed, xs = [], np.zeros(len(vals))
    for i in order:
        near = [x for (x, v) in placed if abs(v - vals[i]) < dy]
        k = 0
        while True:
            cand = (k + 1) // 2 * dx * (1 if k % 2 else -1)
            if all(abs(cand - x) > dx * 0.9 for x in near):
                break
            k += 1
        xs[i] = cand
        placed.append((cand, vals[i]))
    return xs


plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 7.5})
fig, axes = plt.subplots(1, 2, figsize=(5.5, 2.6), dpi=300, sharey=True, gridspec_kw={'width_ratios': [1.1, 1]})
fig.patch.set_facecolor(SURF)
a_k32 = res['deployed agreement, dress read K 32']
a_80 = res['agreement, 80 pooled attempts']
a_key = res['key-scored accuracy, 80 pooled attempts']
panels = ((axes[0], ~hard, 'Easy templates (10): 34 rows, 33 robust', (0.0, 1.15), 0.068,
           'Within-configuration AUC 1.00,\nfrom one non-robust row'),
          (axes[1], hard, 'Hard templates (17): 37 rows, 18 non-robust', (0.0, 1.0), 0.085,
           f'Within-configuration AUC\n{a_k32:.3f} at K 32 (this read)\n{a_80:.3f} with 80 attempts\n'
           f'{a_key:.3f} scored against the key'))
for ax, mask, title, (xr, xn), dx, note in panels:
    ax.set_facecolor(SURF)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color(GRID)
    ax.spines['bottom'].set_color(GRID)
    ax.grid(axis='y', color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', colors=MUTED, labelsize=7, length=0)
    ax.tick_params(axis='x', length=0, colors=INK, labelsize=7.5)
    if ax is axes[1]:
        ax.axhspan(*BAND, color=GRID, alpha=0.45, lw=0, zorder=0)
        ax.text(0.5, (BAND[0] + BAND[1]) / 2, f'{len(band_r)} robust\nand {len(band_n)}\nnon-robust\nrows mix',
                ha='center', va='center', fontsize=6.5, color=MUTED, linespacing=1.1)
    for lab, xc, col in ((0, xr, S1), (1, xn, S2)):
        idx = [i for i in range(len(y)) if mask[i] and y[i] == lab]
        vals = [agree[Tr[i]] for i in idx]
        offs = swarm(vals, dx=dx)
        for i, v, o in zip(idx, vals, offs):
            is13 = Tr[i] == 13
            ax.scatter([xc + o], [v], s=26 if is13 else 17, marker='D' if is13 else 'o', facecolor=col,
                       edgecolor=SURF, linewidth=0.8, zorder=3)
        if ax is axes[1] and lab == 1:
            x13 = [xc + o for i, o in zip(idx, offs) if Tr[i] == 13]
            ax.text(max(x13) + 0.09, agree[13], 'T13', va='center', ha='left', fontsize=6.5, color=INK)
    n_r = int(((y == 0) & mask).sum())
    n_n = int(((y == 1) & mask).sum())
    ax.set_xticks([xr, xn])
    ax.set_xticklabels([f'Robust ({n_r})', f'Non-robust ({n_n})'])
    ax.set_xlim(-0.72, 1.5)
    ax.set_title(title, fontsize=8, color=INK, loc='left', pad=6)
    ax.text(-0.68, 0.47 if ax is axes[1] else 0.3, note, fontsize=6.5, color=MUTED, ha='left', va='top',
            linespacing=1.2)
axes[0].set_ylim(-0.03, 1.05)
axes[0].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
axes[0].set_ylabel('Stand-in agreement on the original\n(K 32; one server read)', fontsize=7, color=MUTED)
fig.tight_layout(w_pad=1.2)
fig.savefig(OUT_PNG, bbox_inches='tight', facecolor=SURF)
say(f'\nsaved {OUT_PNG}')
open(OUT_TXT, 'w').write('\n'.join(LINES) + '\n')
