"""Compare rebuilt per-case tables (build_tables.sh) with the reference case table shipped in rehearsal/expected/.

For every case run (table, speed, configuration, synthetic problem) it checks that validity, answer, decision path
(kind), the moot flag and the clock-cut flag are identical, and reports the largest difference in case seconds. Mock
times carry about 0.1 s of run-to-run jitter (real CPU time leaks into the virtual clock); answers and paths do not.

usage: python3 rehearsal/final_shape/compare_tables.py [--tables DIR] [--expected CSV]
       python3 rehearsal/final_shape/compare_tables.py --write CSV [--tables DIR]   (writes a case table from DIR)
Defaults: --tables rehearsal/final_shape/tables (or $F2_TABLES), --expected rehearsal/expected/case_table.csv."""
import argparse, csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REL = os.path.abspath(os.path.join(HERE, "..", ".."))
NAMES = ("v111", "v111nm", "v112", "v112nm", "v95", "v96")
COLS = ("table", "speed", "cfg", "problem", "valid", "pred", "kind", "qfin_moot", "cut", "sec")


def rows_of(path, name):
    T = json.load(open(path))
    out = {}
    for k, r in T["cases"].items():
        sp, cfg, text = k.split("|", 2)
        m = re.match(r"Synthetic problem (NEW-\d+):", text)
        if not m:          # only the 50 synthetic new problems are tabled (build_tables.sh --new-only)
            continue
        out[(name, f"{float(sp):.1f}", cfg, m.group(1))] = dict(
            valid=str(bool(r["valid"])), pred=str(r["pred"]), kind=str(r["kind"]), qfin_moot=str(bool(r.get("qfin_moot"))),
            cut=str(bool(r.get("cut"))), sec=f"{float(r['sec']):.2f}")
    return out


def tables(d):
    got = {}
    for n in NAMES:
        p = os.path.join(d, f"T_{n}.json")
        if os.path.exists(p):
            got[n] = rows_of(p, n)
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=os.environ.get("F2_TABLES") or os.path.join(REL, "rehearsal", "final_shape", "tables"))
    ap.add_argument("--expected", default=os.path.join(REL, "rehearsal", "expected", "case_table.csv"))
    ap.add_argument("--write", default=None)
    a = ap.parse_args()
    got = tables(a.tables)
    if not got:
        sys.exit(f"no T_*.json tables in {a.tables}: run rehearsal/final_shape/build_tables.sh first")
    if a.write:
        with open(a.write, "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(COLS)
            for n in NAMES:
                for key in sorted(got.get(n, {}), key=lambda k: (k[1], k[2], int(k[3].split("-")[1]))):
                    r = got[n][key]
                    w.writerow(list(key) + [r[c] for c in COLS[4:]])
        print(f"wrote {a.write}: {sum(len(v) for v in got.values())} case runs from {', '.join(got)}")
        return
    exp = {}
    with open(a.expected, newline="") as f:
        for r in csv.DictReader(f):
            exp.setdefault(r["table"], {})[tuple(r[c] for c in COLS[:4])] = r
    bad = 0
    for n in NAMES:
        if n not in exp:
            continue
        if n not in got:
            print(f"T_{n}.json: not built here (skipped)")
            continue
        e, g = exp[n], got[n]
        missing = sorted(set(e) - set(g))
        extra = sorted(set(g) - set(e))
        diff = [k for k in e if k in g and any(e[k][c] != g[k][c] for c in COLS[4:9])]
        dsec = max((abs(float(e[k]["sec"]) - float(g[k]["sec"])) for k in e if k in g), default=0.0)
        bad += len(missing) + len(extra) + len(diff)
        print(f"T_{n}.json: {len(g)} case runs, {len(e) - len(missing)} of {len(e)} expected present, "
              f"{len(diff)} differ in validity / answer / path / flags, max |time difference| {dsec:.2f} s"
              + (f", {len(extra)} unexpected" if extra else ""))
        for k in diff[:10]:
            print("   ", " ".join(k), {c: (e[k][c], g[k][c]) for c in COLS[4:9] if e[k][c] != g[k][c]})
    print("ALL MATCH (answers, validity, paths)" if bad == 0 else f"{bad} MISMATCHES")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
