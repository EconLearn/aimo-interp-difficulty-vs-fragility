"""Figure 1 of the four-page report, draft 32: the stand-in's agreement on each labelled public row, by label, on easy
and on hard templates, with the INSTANCE-MISMATCHED rows drawn hollow. A copy of make_agreement_by_label_v30.py (kept
unchanged, with its figure and output) that adds the instance check found by the second prize-judge review of draft 31.

Data (held files only, CPU, no model runs; computed, post hoc: the labels were seen long before):
  rows       the 71 labelled public rows exactly as decision.json was fitted (lane G, work/miners17/laneG/g_common.py,
             build_fit_data); label y = 1 for non-robust
  matched    a row is instance-matched when its own labelled problem text is the template text every one of our reads
             used. The organisers' file re-instantiates some templates with other numbers; calib.json, built from it by
             release/training/build_calib.py, records this per row as `own_text` (row problem == the template's first
             problem in file order). 8 of the 71 labelled rows are not matched; work/miners19/draft32/
             recompute_matched_v32.py re-derives the same 8 from the parquet by sha1 of the texts.
  agreement  the dress read (Codabench 987666, work/runs/v88_dress_987666.log, 15 October; ledger 440): per template,
             pair_nat of gpt-oss-120b low at K 32 and a 3,000-token cap, the reading the entry deploys (g_common.parse_dress)
  regions    hard = the 17 labelled templates a 2,000-token Olmo-Instruct reader never finishes, fixed before the hard-region
             lab (ledger 267b, 278; g_common.HARD); easy = the other 10 labelled templates
  AUC        within-configuration AUC (non-robust rows compared only with robust rows of the same configuration), on the
             matched rows and on all rows: the dress read; agreement over 80 pooled gpt-oss low attempts from six other
             held reads; the share of those attempts that match the public answer key (work/miners17/laneX/x_pool.json,
             xbench.auc_within); and the range over the six single held reads.
  LOTO       the entry's rules (v95) leave-one-template-out on the dress read (g_common.run_policy), and the same with the
             key-scored share in place of agreement.
Writes agreement_by_label_v32.png and make_agreement_by_label_v32.out next to this script. Run with the system python3
(matplotlib, pandas, numpy): python3 figures/make_agreement_by_label_v32.py
"""
import collections
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
AIMO = os.environ.get('AIMO_DIR', os.path.dirname(HERE))  # folder holding hf/ and work/
WORK = os.path.join(AIMO, 'work')
sys.path.insert(0, os.path.join(WORK, 'miners17', 'laneG'))
sys.path.insert(0, os.path.join(WORK, 'miners17', 'laneX'))
from g_common import HARD, V95, build_fit_data, parse_dress, run_policy  # noqa: E402
import xbench  # noqa: E402

OUT_PNG = os.path.join(HERE, 'agreement_by_label_v32.png')
OUT_TXT = os.path.join(HERE, 'make_agreement_by_label_v32.out')
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
cal = json.load(open(os.path.join(WORK, 'sub_v135m', 'calib.json')))['rows']
lab_rows = [r for r in cal if r['label'] is not None]
assert [(r['model_id'], r['effort']) for r in lab_rows] == list(zip(D.model_id, D.effort))
match = np.array([r['own_text'] in (True, 'True') for r in lab_rows])
assert len(match) == 71 and int((~match).sum()) == 8


def pair_nat(att):
    K = len(att)
    c = collections.Counter(a[2] for a in att if a[1] and a[2] is not None)
    return sum(v * (v - 1) for v in c.values()) / (K * (K - 1))


pooled = {T: pair_nat(LOW[T]) for T in TS}
keyacc = {T: float(np.mean([a[3] for a in LOW[T]])) for T in TS}
reads = sorted({a[4] for T in TS for a in LOW[T]})
single = {r: {T: pair_nat([a for a in LOW[T] if a[4] == r]) for T in TS} for r in reads}

R_all = xbench.ROWS
assert [(r['T'], r['cfg'], r['y']) for r in R_all] == list(zip(Tr.tolist(), cfg.tolist(), y.tolist()))
for r, m in zip(R_all, match):
    r['match'] = bool(m)
auc = lambda f, rows: xbench.auc_within({T: 1 - f[T] for T in TS}, rows)  # noqa: E731
sel = lambda region, matched: [r for r in R_all if (region == 'all' or (r['T'] in HARD) == (region == 'hard'))  # noqa: E731
                               and (r['match'] or not matched)]

say('# Figure 1, draft 32: agreement by label, easy vs hard templates, mismatched rows hollow (computed, post hoc; held files only)')
say(f'rows {len(y)} ({y.sum()} non-robust); hard {hard.sum()} rows on {len(set(Tr[hard]))} templates ({y[hard].sum()} non-robust); '
    f'easy {(~hard).sum()} rows on {len(set(Tr[~hard]))} templates ({(~hard).sum() - y[~hard].sum()} robust)')
say(f'instance-matched rows {int(match.sum())} ({int(y[match].sum())} non-robust); hard {int((hard & match).sum())} '
    f'({int(y[hard & match].sum())} non-robust); easy {int((~hard & match).sum())} ({int((~hard & match).sum() - y[~hard & match].sum())} robust)')
say('mismatched rows (hollow): ' + ', '.join(f'T{Tr[i]:02d} {cfg[i]} {"non-robust" if y[i] else "robust"}' for i in np.where(~match)[0]))
say('\n## within-configuration AUC (value, rows, non-robust rows, within-configuration pairs): matched [all]')
res = {}
for name, f in (('deployed agreement, dress read K 32', agree), ('agreement, 80 pooled attempts', pooled),
                ('key-scored accuracy, 80 pooled attempts', keyacc)):
    parts = []
    for region in ('all', 'hard', 'easy'):
        am, aa = auc(f, sel(region, True)), auc(f, sel(region, False))
        res[(name, region)] = (am[0], aa[0])
        parts.append(f'{region} {am[0]:.3f} ({am[1]}, {am[2]}, {am[3]}) [{aa[0]:.3f} ({aa[1]}, {aa[2]}, {aa[3]})]')
    say(f'{name:42s} ' + ' | '.join(parts))
sh_m = [auc(single[r], sel('hard', True))[0] for r in reads]
sh_a = [auc(single[r], sel('hard', False))[0] for r in reads]
say(f'single held reads (K 8 or 16), hard rows: matched range {min(sh_m):.3f} to {max(sh_m):.3f} [all {min(sh_a):.3f} to {max(sh_a):.3f}]')

say('\n## the entry (v95 rules) leave-one-template-out on the dress read (lane G run_policy)')
yh = run_policy(D, FIT, pool, V95, 'loto')
ok = yh == y
say(f'right: matched {int(ok[match].sum())}/{int(match.sum())} [all {int(ok.sum())}/71]; hard matched {int(ok[hard & match].sum())}/'
    f'{int((hard & match).sum())} [all {int(ok[hard].sum())}/{int(hard.sum())}]')
D2 = D.copy()
D2['pair16'] = [keyacc[T] for T in D2['T'].values]
yk = run_policy(D2, FIT, {T: dict(pool[T], prim=keyacc[T]) for T in pool}, V95, 'loto')
say('key-scored share in place of agreement (ceiling), rows changed: '
    + '; '.join(f'T{Tr[i]:02d} {cfg[i]} {"fixed" if yk[i] == y[i] else "broken"}{"" if match[i] else " (mismatched)"}'
                for i in np.where(yk != yh)[0]))

BAND = (0.555, 0.825)
inb = lambda i: BAND[0] <= agree[Tr[i]] <= BAND[1]  # noqa: E731
for lbl, mm in (('matched', match), ('all', np.ones(71, bool))):
    br = [i for i in range(len(y)) if hard[i] and mm[i] and y[i] == 0 and inb(i)]
    bn = [i for i in range(len(y)) if hard[i] and mm[i] and y[i] == 1 and inb(i)]
    say(f'hard rows with agreement 0.56 to 0.82, {lbl}: {len(br)} robust, {len(bn)} non-robust (information; draft 32 draws no band)')
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
k32 = res[('deployed agreement, dress read K 32', 'hard')]
p80 = res[('agreement, 80 pooled attempts', 'hard')]
key = res[('key-scored accuracy, 80 pooled attempts', 'hard')]
n_easy_m = int((~hard & match).sum())
n_hard_m, nr_hard_m = int((hard & match).sum()), int(y[hard & match].sum())
panels = ((axes[0], ~hard, f'Easy templates (10): 34 rows, 33 robust\n({n_easy_m} matched, {n_easy_m - int(y[~hard & match].sum())} robust)',
           (0.0, 1.15), 0.068, 'Within-configuration AUC 1.00,\nfrom one non-robust row'),
          (axes[1], hard, f'Hard templates (17): 37 rows, 18 non-robust\n({n_hard_m} matched, {nr_hard_m} non-robust)', (0.0, 1.0), 0.085,
           f'Within-configuration AUC,\nmatched rows [all rows]\n{k32[0]:.3f} [{k32[1]:.3f}] at K 32\n'
           f'{p80[0]:.3f} [{p80[1]:.3f}] with 80 attempts\n{key[0]:.3f} [{key[1]:.3f}] against the key'))
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
    for lab, xc, col in ((0, xr, S1), (1, xn, S2)):
        idx = [i for i in range(len(y)) if mask[i] and y[i] == lab]
        vals = [agree[Tr[i]] for i in idx]
        offs = swarm(vals, dx=dx)
        for i, v, o in zip(idx, vals, offs):
            is13 = Tr[i] == 13
            ax.scatter([xc + o], [v], s=26 if is13 else 17, marker='D' if is13 else 'o',
                       facecolor=col if match[i] else SURF, edgecolor=SURF if match[i] else col,
                       linewidth=0.8 if match[i] else 1.0, zorder=3)
        if ax is axes[1] and lab == 1:
            x13 = [xc + o for i, o in zip(idx, offs) if Tr[i] == 13]
            ax.text(max(x13) + 0.09, agree[13], 'T13', va='center', ha='left', fontsize=6.5, color=INK)
    n_r = int(((y == 0) & mask).sum())
    n_n = int(((y == 1) & mask).sum())
    ax.set_xticks([xr, xn])
    ax.set_xticklabels([f'Robust ({n_r})', f'Non-robust ({n_n})'])
    ax.set_xlim(-0.72, 1.5)
    ax.set_title(title, fontsize=7.5, color=INK, loc='left', pad=6, linespacing=1.15)
    ax.text(-0.68, 0.50 if ax is axes[1] else 0.3, note, fontsize=6.3, color=MUTED, ha='left', va='top', linespacing=1.2)
axes[0].scatter([], [], s=17, marker='o', facecolor=MUTED, edgecolor=SURF, label='matched row')
axes[0].scatter([], [], s=17, marker='o', facecolor=SURF, edgecolor=MUTED, linewidth=1.0, label='other numbers (Section 2)')
axes[0].legend(loc='lower left', bbox_to_anchor=(-0.02, -0.02), fontsize=6.0, frameon=False, handletextpad=0.2, borderaxespad=0.2)
axes[0].set_ylim(-0.03, 1.05)
axes[0].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
axes[0].set_ylabel('Stand-in agreement on the original\n(K 32; one server read)', fontsize=7, color=MUTED)
fig.tight_layout(w_pad=1.2)
fig.savefig(OUT_PNG, bbox_inches='tight', facecolor=SURF)
say(f'\nsaved {os.path.relpath(OUT_PNG, os.path.dirname(HERE))}')
open(OUT_TXT, 'w').write('\n'.join(LINES) + '\n')
