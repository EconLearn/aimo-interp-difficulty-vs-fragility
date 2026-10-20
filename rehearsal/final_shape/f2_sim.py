"""Lane F2: the final at N x 170 s (ledger 537), simulated exactly from per-case mock tables (f2_tables.py). OFFLINE.

Harness rules (ledger 464 / 492): cases run one after another, each in a fresh process with no budget information, on ONE
shared job budget B; a case whose time exceeds the budget left times out (invalid) and every later case is skipped.
B = N x 170 s (organisers, ledger 537), with and without the 180 s safety margin seen in our logs (B - 180).

Mixes (per 21 main / 14 small cases, scaled to N by largest remainder):
  main  val   = the validation mix  Qwen 2, Skywork 3, Olmo 2, DeepSeek 3, high 3, low 5, medium 3
  main  worst = Olmo- / stand-in-heavy, no instant 'high' and no fast Skywork: Qwen 4, Olmo 6, DeepSeek 4, low 4, medium 3
  small val   = Qwen 5, Skywork 3, Olmo 3, DeepSeek 3
  small worst = Qwen 4, Olmo 6, DeepSeek 4
Order: board-like (7B / 4B models in configuration blocks in harness order, then the gpt-oss efforts interleaved), case k on
synthetic problem NEW-k (distinct problems). Sensitivity: 200 random orders x random problem draws (mean / worst answered).

Times of the moot-skip bundles (v104 / v105 / v107 / v108 and variants built on them) are taken at the PUBLIC-ROW moot rate
(lane F's hybrid.py rule: the mock's random readings make the quick finish moot ~97% of the time, public stand-in rows 25/44):
a mock-moot case keeps its fast time with probability rate / mock rate (md5 of the key), else it takes the base bundle's time
(same answer; checked). Base: v104 <- v95, v105 <- v96, v107 <- v100, v108 <- v101, a variant <- its no-skip twin.

Expected accuracy (lane F's rule): an answered case scores its configuration's public-row accuracy on the v95 line when it was
decided by a full reading (own run, agreement + quick finish, agreement only), its public robust base rate when answered by
the prior / quick finish only / fallback; unanswered = 0. STD-decided Skywork / Olmo cases (v107 / v108) score an ASSUMED
Skywork 2/3, Olmo 8/9 (= v95 + ~1 of 12 rows, the blind-writer average of ledger 528; v102 unread).

usage: f2_sim.py run  [--out FILE]          (all bundles, all shapes)
"""
import argparse, hashlib, json, os, random, sys
from collections import Counter

S2 = os.environ.get("F2_TABLES") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "tables")   # release copy
MAIN7 = ["Qwen", "Skywork", "Olmo", "DeepSeek", "high", "low", "medium"]
SMALL4 = ["Qwen", "Skywork", "Olmo", "DeepSeek"]
ACC = {"Qwen": 11 / 12, "Skywork": 1 / 3, "Olmo": 8 / 9, "DeepSeek": 8 / 10, "high": 13 / 15, "low": 6 / 7, "medium": 14 / 15}
BASE = {"Qwen": 8 / 12, "Skywork": 2 / 3, "Olmo": 7 / 9, "DeepSeek": 7 / 10, "high": 13 / 15, "low": 5 / 7, "medium": 10 / 15}
ACC_STD = {"Skywork": 2 / 3, "Olmo": 8 / 9}
FULL_KINDS = ("own", "full", "agr")
RATE = {"Qwen": 7 / 12, "DeepSeek": 6 / 10, "low": 4 / 7, "medium": 8 / 15, "Skywork": 25 / 44, "Olmo": 25 / 44}
MIX = {("main", "val"): {"Qwen": 2, "Skywork": 3, "Olmo": 2, "DeepSeek": 3, "high": 3, "low": 5, "medium": 3},
       ("main", "worst"): {"Qwen": 4, "Skywork": 0, "Olmo": 6, "DeepSeek": 4, "high": 0, "low": 4, "medium": 3},
       ("small", "val"): {"Qwen": 5, "Skywork": 3, "Olmo": 3, "DeepSeek": 3},
       ("small", "worst"): {"Qwen": 4, "Skywork": 0, "Olmo": 6, "DeepSeek": 4}}
SPEEDS = ("srv", 1.0, 1.2, 1.4, 1.6)
# 'srv' = the 1.0x mock times x the per-configuration ratio server / mock measured on v95's board run (991447, 3,030 s;
# ledger 471) against the mock's board times at 1.0x: Qwen 176/191.6, Skywork 138/148.5 (the two full runs; incl. the 46 s
# case 0.72), Olmo 209/199.1, DeepSeek 174.3/191.6, low 174/191.6, medium 181.3/191.6 (answers = the 1.0x answers)
SRV = {"Qwen": 0.919, "Skywork": 0.929, "Olmo": 1.050, "DeepSeek": 0.910, "high": 1.0, "low": 0.908, "medium": 0.946}


def add_srv(T):
    std = bool(T.get("std"))                          # STD bundles: Skywork / Olmo cases run gpt-oss (+ Qwen), not the 7B
    for k, r in list(T["cases"].items()):
        sp, c, p = k.split("|", 2)
        if sp == "1.0":
            f = 0.92 if std and c in ("Skywork", "Olmo") else SRV[c]
            T["cases"][f"srv|{c}|{p}"] = dict(r, sec=round(r["sec"] * f, 2))
    return T


def load(name):
    return add_srv(json.load(open(os.path.join(S2, f"T_{name}.json"))))


def hybrid(T, B):
    """T's answers, times at the public-row moot rate (base table B supplies the no-skip time)."""
    mock, tot = Counter(), Counter()
    for k, r in T["cases"].items():
        sp, c, _ = k.split("|", 2)
        if c in RATE:
            tot[(sp, c)] += 1
            mock[(sp, c)] += bool(r.get("qfin_moot"))
    H = dict(T)
    H["cases"] = {}
    for k, r in T["cases"].items():
        sp, c, _ = k.split("|", 2)
        r = dict(r)
        if c in RATE and r.get("qfin_moot"):
            keep = RATE[c] / (mock[(sp, c)] / tot[(sp, c)])
            u = int(hashlib.md5(k.encode()).hexdigest(), 16) % 10 ** 6 / 1e6
            if u >= keep:
                b = B["cases"][k]
                assert b["pred"] == r["pred"], (k, b["pred"], r["pred"])
                r["sec"] = b["sec"]
                r["qfin_moot"] = False
        H["cases"][k] = r
    return H


def counts(track, mix, n):
    w = MIX[(track, mix)]
    tot = sum(w.values())
    raw = {c: n * v / tot for c, v in w.items()}
    out = {c: int(x) for c, x in raw.items()}
    for c in sorted(raw, key=lambda c: -(raw[c] - out[c]))[: n - sum(out.values())]:
        out[c] += 1
    return out


def layout(track, mix, n, rng=None, texts=None, std_cov=0.0, pub_texts=()):
    """[(cfg, text)] in harness order (board-like) or shuffled (rng)."""
    cnt = counts(track, mix, n)
    cases = []
    for c in (MAIN7 if track == "main" else SMALL4):
        if c not in ("high", "low", "medium"):
            cases += [c] * cnt.get(c, 0)
    effs = []
    for c in ("high", "low", "medium"):
        k = cnt.get(c, 0)
        effs += [((i + 0.5) / k, c) for i in range(k)]
    cases += [c for _, c in sorted(effs)]
    if rng is not None:
        rng.shuffle(cases)
    out = []
    pool = list(range(50))
    for k, c in enumerate(cases):
        j = k if rng is None else rng.choice(pool)
        t = f"Synthetic problem NEW-{j}: find the value of N for these parameters. " + "x" * 200
        if pub_texts and c in ("Skywork", "Olmo") and (rng.random() if rng else (k % 100) / 100.0) < std_cov:
            t = pub_texts[(k if rng is None else rng.randrange(len(pub_texts))) % len(pub_texts)]
        out.append((c, t))
    return out


def score(r):
    c, kd = r["cfg"], r["kind"]
    if kd == "std:std":
        return ACC_STD[c]
    if kd == "std:fallback":
        return ACC[c] if "own_" in r.get("note", "") else BASE[c]
    return ACC[c] if kd in FULL_KINDS else BASE[c]


def simulate(T, cases, sp, budget):
    used, dead, ok, to, sk, acc = 0.0, False, 0, 0, 0, 0.0
    preds = []
    for c, p in cases:
        r = T["cases"][f"{sp}|{c}|{p}"]
        left = budget - used
        if dead or left <= 0:
            sk += 1
            preds.append(None)
            continue
        if r["sec"] > left:
            to += 1
            used, dead = budget, True
            preds.append(None)
            continue
        used += r["sec"]
        if r["valid"]:
            ok += 1
            acc += score(r)
            preds.append(r["pred"])
        else:
            preds.append(None)
    n = len(cases)
    return dict(n=n, ok=ok, inv=n - ok, to=to, sk=sk, acc=acc / n, used=used, spare=budget - used, preds=preds)


def ceiling(T, cases, sp):
    return sum(score(T["cases"][f"{sp}|{c}|{p}"]) for c, p in cases) / len(cases)


def per_cfg(T, sp, cfgs, syn_only=True):
    out = {}
    for c in cfgs:
        v = [r["sec"] for k, r in T["cases"].items() if k.startswith(f"{sp}|{c}|") and (not syn_only or "NEW-" in k)]
        if v:
            out[c] = sum(v) / len(v)
    return out


def tables():
    """name -> (track, table at the public-row moot rate where relevant, is_std)."""
    T = {}
    T["v95"] = ("main", load("v95"), False)
    T["v104"] = ("main", hybrid(load("v104"), T["v95"][1]), False)
    T["v96"] = ("small", load("v96"), False)
    T["v105"] = ("small", hybrid(load("v105"), T["v96"][1]), False)
    if os.path.exists(os.path.join(S2, "T_v107.json")) and os.path.exists(os.path.join(S2, "T_v100.json")):
        T["v107"] = ("main", hybrid(load("v107"), load("v100")), True)
    if os.path.exists(os.path.join(S2, "T_v108.json")) and os.path.exists(os.path.join(S2, "T_v101.json")):
        T["v108"] = ("small", hybrid(load("v108"), load("v101")), True)
    for extra in os.environ.get("F2_EXTRA", "").split(","):
        if not extra:
            continue
        name, track, base = extra.split(":")         # e.g. v109:main:v109nm  (variant : track : its no-skip twin)
        T[name] = (track, hybrid(load(name), load(base)) if base != "-" else load(name), False)
    return T


def pub_texts():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import f2_tables
    return f2_tables.public_texts()


def run(out=None, names=None, draws=200):
    TT = tables()
    names = names or list(TT)
    pt = pub_texts()
    L = []
    for track in ("main", "small"):
        bs = [b for b in names if b in TT and TT[b][0] == track]
        if not bs:
            continue
        L.append(f"\n## {track}: cases answered / N, expected accuracy (invalid = 0), spare or [timeouts + skipped]; budget N x 170 s "
                 f"WITH the 180 s margin (no margin in brackets when it differs)\n")
        L.append("| mix | N | speed | " + " | ".join(bs) + " |")
        L.append("|---|---|---|" + "---|" * len(bs))
        for mix in ("val", "worst"):
            for n in (30, 40, 50):
                for sp in SPEEDS:
                    cells = []
                    for b in bs:
                        tr, T, std = TT[b]
                        cs = layout(track, mix, n)
                        a = simulate(T, cs, sp, 170.0 * n - 180.0)
                        z = simulate(T, cs, sp, 170.0 * n)
                        cell = f"{a['ok']}/{n} {a['acc']:.3f}" + (f" (+{a['spare']:.0f} s)" if a["inv"] == 0 else f" [{a['to']}+{a['sk']}]")
                        if z["ok"] != a["ok"]:
                            cell += f" (no margin {z['ok']}/{n} {z['acc']:.3f})"
                        cells.append(cell)
                    L.append(f"| {mix} | {n} | {sp}{'' if sp == 'srv' else 'x'} | " + " | ".join(cells) + " |")
        # ceilings and per-configuration seconds
        L.append("\nper-configuration mean case seconds on the 50 synthetic new problems (moot-skip bundles at the public-row moot rate):\n")
        cfgs = MAIN7 if track == "main" else SMALL4
        L.append("| bundle | speed | " + " | ".join(cfgs) + " | val-mix mean | worst-mix mean |")
        L.append("|---|---|" + "---|" * (len(cfgs) + 2))
        for b in bs:
            for sp in SPEEDS:
                pc = per_cfg(TT[b][1], sp, cfgs)
                mv = sum(pc[c] * w for c, w in MIX[(track, "val")].items()) / sum(MIX[(track, "val")].values())
                mw = sum(pc[c] * w for c, w in MIX[(track, "worst")].items()) / sum(MIX[(track, "worst")].values())
                L.append(f"| {b} | {sp}{'' if sp == 'srv' else 'x'} | " + " | ".join(f"{pc[c]:.0f}" for c in cfgs) + f" | {mv:.0f} | {mw:.0f} |")
        # random orders / problem draws: mean and worst answered
        L.append(f"\nsensitivity: {draws} random case orders x random problem draws, budget with margin: mean answered (worst draw)\n")
        L.append("| mix | N | speed | " + " | ".join(bs) + " |")
        L.append("|---|---|---|" + "---|" * len(bs))
        for mix in ("val", "worst"):
            for n in (30, 40, 50):
                for sp in SPEEDS:
                    cells = []
                    for b in bs:
                        tr, T, std = TT[b]
                        rng = random.Random(1000 + n)
                        res = [simulate(T, layout(track, mix, n, rng=rng), sp, 170.0 * n - 180.0) for _ in range(draws)]
                        okm = sum(r["ok"] for r in res) / draws
                        accm = sum(r["acc"] for r in res) / draws
                        cells.append(f"{okm:.1f} ({min(r['ok'] for r in res)}) {accm:.3f}")
                    L.append(f"| {mix} | {n} | {sp}{'' if sp == 'srv' else 'x'} | " + " | ".join(cells) + " |")
        std_bs = [b for b in bs if TT[b][2]]
        if std_bs:
            L.append("\nSTD bundles with Skywork / Olmo problems that STD COVERS (public templates with a lane L program; "
                     "the main table above uses synthetic problems = STD finds no usable code -> fallback), budget with margin:\n")
            L.append("| mix | N | speed | " + " | ".join(std_bs) + " |")
            L.append("|---|---|---|" + "---|" * len(std_bs))
            for mix in ("val",):
                for n in (30, 40, 50):
                    for sp in SPEEDS:
                        cells = []
                        for b in std_bs:
                            cs = layout(track, mix, n, std_cov=1.0, pub_texts=pt)
                            a = simulate(TT[b][1], cs, sp, 170.0 * n - 180.0)
                            cells.append(f"{a['ok']}/{n} {a['acc']:.3f}" + (f" (+{a['spare']:.0f} s)" if a["inv"] == 0 else f" [{a['to']}+{a['sk']}]"))
                        L.append(f"| {mix} | {n} | {sp}{'' if sp == 'srv' else 'x'} | " + " | ".join(cells) + " |")
    txt = "\n".join(L)
    print(txt)
    if out:
        with open(out, "w") as f:
            f.write(txt + "\n")
    return TT


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--out", default=None)
    ap.add_argument("--names", default=None)
    ap.add_argument("--draws", type=int, default=200)
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.out, a.names.split(",") if a.names else None, a.draws)
