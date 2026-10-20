"""Rebuild calib.json (the public labelled rows bundled with the entry) from the organisers' public train file.

usage: python training/build_calib.py train-main-v2.parquet calib.json
needs: pandas + pyarrow (local tooling only; the entry itself reads the JSON).

Written for the release as a reconstruction: the original file was made interactively. It reproduces the shipped
calib.json byte for byte (md5 d5b98e21169c0ae100c14009340b7fca) from train-main-v2.parquet (82 rows).
Per row: model_id, effort (= reasoning_effort), label (1 = non-robust, 0 = robust, null = the organisers' unlabelled
band), max_drop, and the problem template. Problems are numeric re-instantiations of 28 templates (36 distinct texts),
so `stem` = the text with every digit run replaced by '#' and whitespace collapsed, first 60 characters; `text` = the
first problem of that template in file order; `own_text` = whether this row's own problem is that text.
"""
import json
import math
import re
import sys

import pandas as pd


def stem(t):
    return re.sub(r"\s+", " ", re.sub(r"\d+", "#", t))[:60]


def main(src, out):
    p = pd.read_parquet(src)
    first = {}
    for _, q in p.iterrows():
        first.setdefault(stem(q.problem), q.problem)
    rows = []
    for _, q in p.iterrows():
        unl = q.is_robust is None or (isinstance(q.is_robust, float) and math.isnan(q.is_robust))
        t = first[stem(q.problem)]
        rows.append({"model_id": q.model_id, "effort": q.reasoning_effort, "stem": stem(q.problem), "text": t,
                     "own_text": q.problem == t, "label": None if unl else int(not bool(q.is_robust)),
                     "max_drop": float(q.max_drop)})
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps({"rows": rows}))
    print(f"wrote {out}: {len(rows)} rows, {sum(r['label'] is not None for r in rows)} labelled, {len(first)} templates")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
