"""Final-scale clock rehearsal of the sub_v80m bundle's own-model runs (Skywork / Olmo run to the end).
A COPY of the bundle (params unchanged) runs through the organisers' ingestion program with rehearsal/mock_engine2.py
in MOCK_OWN=1 mode (per-model step costs, finishing lengths; see the comment block in the mock). Virtual clock.
Shapes: (a) board scale (the 21-case / 16-problem main validation shape, plus random 2-5 cases per call) and
(b) final scale (30 problems x 7 configurations), plus a problems-per-call sweep. Speeds: as modelled, every model
1.4x slower, and the 7B models alone 1.6x slower (the board's Olmo reading: ~730 s for 2 problems at K 3).
usage: python rehearsal/run_final_scale.py [bundle] [small]   (output also in rehearsal/final_scale_<bundle>.out)
Release copy: paths are relative to the release folder. [bundle] is a sub-folder of the release (default submission_main).
The organisers' ingestion program is looked up in <release>/getting-started/ (a clone of
https://github.com/aimo-interp/getting-started), or wherever the AIMO_INGESTION environment variable points."""
import hashlib, json, os, random, re, shutil, subprocess, sys

W = os.path.dirname(os.path.abspath(__file__)); WORK = os.path.dirname(W)
ING = os.environ.get('AIMO_INGESTION') or os.path.join(WORK, 'getting-started', 'components', 'ingestion_program', 'ingestion.py')
BUNDLE = sys.argv[1] if len(sys.argv) > 1 else 'submission_main'
TMP = os.path.join(W, 'final_scale_tmp_' + BUNDLE + ('_small' if len(sys.argv) > 2 and sys.argv[2] == 'small' else ''))   # one per run: runs may overlap
PAR = json.load(open(os.path.join(WORK, BUNDLE, 'params.json')))
TAG = re.search(r'_log\(msg\):\s*\n\s*print\(f"\[(\w+) ', open(os.path.join(WORK, BUNDLE, 'solution.py')).read()).group(1)
_tm = PAR['reading'].get('time', {})                   # gpt-oss: the bundle's own time model (as run_rehearsal.py)
BASE_ENV = {'MOCK_A': str(_tm.get('a_ms', 28.0)), 'MOCK_B': str(_tm.get('b_ms', 1.3)), 'MOCK_USED': str(_tm.get('used_compact', 0.7)), 'MOCK_OWN': '1'}
CFG = [("Qwen/Qwen3.5-4B", "default"), ("Skywork/Skywork-OR1-Math-7B", "default"), ("allenai/Olmo-3-7B-Think", "default"),
       ("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "default"), ("openai/gpt-oss-120b", "high"), ("openai/gpt-oss-120b", "low"),
       ("openai/gpt-oss-120b", "medium")]                # harness call order
TRACK = sys.argv[2] if len(sys.argv) > 2 else 'main'  # 'small': the four small configurations, --track small
if TRACK == 'small':
    CFG = CFG[:4]
OWNS = {s['name']: s for s in ([PAR['sky']] if PAR.get('sky') else []) + PAR.get('owns', [])}
OWN_CFG = {s['apply_cfgs'][0]: s for s in OWNS.values()}


def text(tag, i):
    return f"Synthetic problem {tag}-{i}: find the value of N for these parameters. " + "x" * 200


def board_exact(seed):
    """The main validation shape: cases per call 2,3,2,3,3,5,3 (21), new problems 2,2,2,2,3,4,1 (16)."""
    P = [text(f"b{seed}", i) for i in range(16)]
    per = [[0, 1], [2, 3, 0], [4, 5], [6, 7, 2], [8, 9, 10], [11, 12, 13, 14, 4], [15, 11, 12]]
    return [(m, e, P[j]) for (m, e), js in zip(CFG, per) for j in js]


def board_random(seed):
    rng, seen, cases, n = random.Random(seed), [], [], 0
    for m, e in CFG:
        here = []
        for _ in range(rng.randint(2, 5)):
            old = [p for p in seen if p not in here]
            if old and rng.random() < 0.3:
                p = rng.choice(old)
            else:
                p = text(f"r{seed}", n); n += 1; seen.append(p)
            here.append(p)
        cases += [(m, e, p) for p in here]
    return cases


def final(seed, n_prob, incl):
    rng = random.Random(seed)
    P = [text(f"f{seed}-{n_prob}", i) for i in range(n_prob)]
    return [(m, e, p) for m, e in CFG for p in P if rng.random() < incl]


def run(cases, env):
    shutil.rmtree(TMP, ignore_errors=True)
    for d in ('in', 'out'):
        os.makedirs(os.path.join(TMP, d))
    sub = os.path.join(TMP, 'sub')
    shutil.copytree(os.path.join(WORK, BUNDLE), sub, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy(os.path.join(W, 'mock_engine2.py'), os.path.join(sub, 'engine2.py'))
    with open(os.path.join(TMP, 'in', 'cases.jsonl'), 'w') as f:
        for i, (m, e, t) in enumerate(cases):
            f.write(json.dumps({"id": f"c{i:04d}", "model_id": m, "reasoning_effort": e, "problem": t}) + '\n')
    trace = os.path.join(TMP, 'trace.jsonl')
    r = subprocess.run([sys.executable, ING, os.path.join(TMP, 'in'), os.path.join(TMP, 'out'), sub, '--track', TRACK],
                       capture_output=True, text=True, env=dict(os.environ, **BASE_ENV, MOCK_TRACE=trace, **env))
    log = r.stdout + r.stderr
    summ = json.load(open(os.path.join(TMP, 'out', 'ingestion_summary.json')))
    rows = [json.loads(x) for x in open(trace)] if os.path.exists(trace) else []
    return log, summ, rows


def analyse(cases, log, summ, rows):
    calls = re.findall(r'\[' + TAG + r'\s+([\d.]+)s\] call (\d+) \(([^)]*)\): (\d+) cases, new problems (\d+), K (\d+)', log)
    owns = re.findall(r'\[' + TAG + r'\s+([\d.]+)s\] call (\d+): (\w+) run to the end[^:]*: (.*)', log)
    batches = re.findall(r'\[' + TAG + r'\s+([\d.]+)s\] (own_\w+): batch (\d+) rows \(K ([^)]*)\), (\d+) steps, ([\d.]+)s( \(cut by clock\))?', log)
    by_cfg = {}
    for m, e, t in cases:
        by_cfg.setdefault(f"{m}:{e}", []).append(t)
    out, prev = [], 0.0
    for t_end, n, cfg, ncase, nnew, kg in calls:
        t_end = float(t_end)
        probs = by_cfg.get(cfg, [])
        row = dict(call=int(n), cfg=cfg.split('/')[-1], cases=int(ncase), uniq=len(set(probs)), new=int(nnew), K_oss=int(kg),
                   sec=t_end - prev, end=t_end)
        prev = t_end
        for _, cn, name, note in owns:
            if int(cn) != int(n):
                continue
            spec = OWNS[name]
            k = re.search(r', K (\d+),', note)
            row['own'] = name
            k2 = re.search(r'\(K (\d+): (\d+), K 1: (\d+)\)', note)        # sub_v82m form: problems at K_max and at K 1
            row['K_own'] = int(k.group(1)) if k else (f"{k2.group(2)}xK{k2.group(1)}+{k2.group(3)}xK1" if k2 else None)
            row['note'] = note if not k else re.search(r'cases with a reading [\d/]+', note).group(0)
            bs = [b for b in batches if b[1] == name]      # each own model runs in one call only (its own configuration)
            row['own_sec'] = sum(float(b[5]) for b in bs)
            row['own_cut'] = sum(1 for b in bs if b[6])
            # per case: attempts that ended alone or ran to >= 0.85 cap (the solution's 'fin or far'), from the mock's trace
            full = fewer = none = 0
            flag = 0
            for p in probs:
                key = hashlib.md5((spec['model'] + "|" + p).encode()).hexdigest()
                att = [x for x in rows if x['key'] == key]
                inf = sum(1 for x in att if x['nat'] or x['n'] >= 0.85 * spec['cap'])
                if inf >= spec['K_max']:
                    full += 1
                elif inf >= 1:
                    fewer += 1
                else:
                    none += 1
                if inf >= 1 and spec.get('min_ended', 1) >= 2 and inf < spec['min_ended'] and not (k2 and len(att) == 1):
                    flag += 1              # read, but fewer complete attempts than min_ended: forced non-robust
            row.update(full=full, fewer=fewer, none=none, flag=flag)
        out.append(row)
    return out


SPEEDS = [("1.0x", {}), ("1.4x all models", {'MOCK_SLOW': '1.4'}), ("1.6x 7B models only", {'MOCK_OWN_SLOW': '1.6'})]
SHAPES = [("board exact (21 cases, 16 problems) seed 1", board_exact(1)), ("board exact seed 2", board_exact(2)),
          ("board random 2-5 per call seed 3", board_random(3)), ("board random seed 4", board_random(4)),
          ("final 30 problems x 7, 93% included, seed 5", final(5, 30, 0.93)), ("final 30 x 7, 93%, seed 6", final(6, 30, 0.93)),
          ("final 30 x 7, all included", final(7, 30, 1.0))]
SWEEP = [(f"sweep {n} problems x 7, all included", final(100 + n, n, 1.0)) for n in (3, 5, 7, 10, 15, 20)]

if __name__ == '__main__':
    lines = [f"{BUNDLE} (log tag {TAG}) own-run clock rehearsal; mock MOCK_OWN=1; virtual clock; harness limit 3,600 s"]
    for spd, env in SPEEDS:
        lines.append(f"\n===== speed {spd}")
        for name, cases in SHAPES + SWEEP:
            log, summ, rows = run(cases, env)
            res = analyse(cases, log, summ, rows)
            end = max([r['end'] for r in res] or [0.0])
            fb = log.count('fallback (')
            app = re.findall(r'attempts per problem min (\d+) median (\d+) max (\d+)', log)   # gpt-oss reading after the last call
            app = f" | oss attempts/problem at the end min {app[-1][0]} median {app[-1][1]} max {app[-1][2]}" if app else ""
            lines.append(f"--- {name}: cases {len(cases)}, problems {len({t for _, _, t in cases})} | invalid {summ['invalid_predictions']}/{summ['cases']} "
                         f"| calls {len(res)} | virtual end {end:.0f} s {'INSIDE' if end <= 3600 else 'OVER'} 3,600 | fallbacks {fb}{app}")
            for r in res:
                s = (f"  call {r['call']} {r['cfg']:32s} cases {r['cases']:3d} problems {r['uniq']:3d} new(oss) {r['new']:3d} K_oss {r['K_oss']:2d} "
                     f"| {r['sec']:6.0f} s, ends {r['end']:6.0f} s")
                if 'own' in r:
                    s += (f" | {r['own']} K {r['K_own']} ({r['note']}), own {r['own_sec']:.0f} s, cut batches {r['own_cut']} "
                          f"| cases read with 3 complete attempts {r['full']}, 1-2 {r['fewer']}, none {r['none']}"
                          + (f" | FLAG Olmo read with <2 complete attempts: {r['flag']}" if r['flag'] else ""))
                lines.append(s)
            print('\n'.join(lines[-len(res) - 1:]), flush=True)
    with open(os.path.join(W, f'final_scale_{BUNDLE}{"_small" if TRACK == "small" else ""}.out'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    shutil.rmtree(TMP, ignore_errors=True)
