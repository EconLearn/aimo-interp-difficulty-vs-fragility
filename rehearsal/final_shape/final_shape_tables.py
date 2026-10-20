"""Final-shape tables for this release, with lane F2's simulation (f2_sim.py, unchanged logic): the 30 / 40 / 50-case final
at N x 170 s announced by the organisers (ledger 537), budget N x 170 s minus the 180 s safety margin seen in our logs (the
result without the margin is added in brackets when it differs), the validation mix and a worst-case mix, board-like order
and 200 random orders x random problem draws, speeds srv / 1.0 / 1.2 / 1.4 / 1.6 (see f2_sim.py for 'srv' and the mixes).

Reads the per-case tables that build_tables.sh writes with f2_tables.py into rehearsal/final_shape/tables/ (or the folder
in the environment variable F2_TABLES):
  T_v111.json + T_v111nm.json (main; the second is the same bundle with the moot quick-finish skip off, which supplies the
  no-skip case time when f2_sim.hybrid puts the moot rate at the public-row rate), T_v112.json + T_v112nm.json (small), and,
  when present, T_v95.json / T_v96.json built from the v95 / v96 release for comparison.

Written for this release (it replaces our internal driver, which compared internal bundle names); the tables, the hybrid
rule and the simulation are f2_sim.py's.
usage: python rehearsal/final_shape/final_shape_tables.py [--out FILE] [--draws 200]"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f2_sim as F  # noqa: E402

BUNDLES = (("v95", "main", None), ("v111", "main", "v111nm"), ("v96", "small", None), ("v112", "small", "v112nm"))


def tables():
    TT = {}
    for name, track, nm in BUNDLES:
        if not os.path.exists(os.path.join(F.S2, f"T_{name}.json")):
            continue
        T = F.load(name)
        if nm:
            T = F.hybrid(T, F.load(nm))
        TT[name] = (track, T, False)
    if "v111" not in TT and "v112" not in TT:
        sys.exit(f"no tables in {F.S2}: run rehearsal/final_shape/build_tables.sh first")
    return TT


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--draws", type=int, default=200)
    a = ap.parse_args()
    F.tables = tables
    F.run(a.out, None, a.draws)
