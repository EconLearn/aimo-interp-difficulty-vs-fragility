"""Dress rehearsal on the contest server (research only; ledger 370).

The candidate entry's solution.py is shipped as entry.py next to this file, with its own params / engine / calib files.
On the FIRST hidden call this wrapper imports entry.py (its clock starts then) and runs it on the final-test shape built
from the 28 PUBLIC templates: 7 calls in harness order (Qwen, Skywork, Olmo, DeepSeek, gpt-oss high, low, medium), the 28
templates in every call (196 cases). It then prints, for the PUBLIC labelled rows only, the entry's answer next to the
label, and per-configuration counts. Every hidden case is answered robust (a research run; no hidden problem is read).
"""
import json
import os
import time

_T0 = time.time()
_HERE = os.path.dirname(os.path.abspath(__file__))
_DONE = {"ran": False}
_CALLS = [("Qwen/Qwen3.5-4B", "default"), ("Skywork/Skywork-OR1-Math-7B", "default"), ("allenai/Olmo-3-7B-Think", "default"),
          ("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "default"), ("openai/gpt-oss-120b", "high"), ("openai/gpt-oss-120b", "low"),
          ("openai/gpt-oss-120b", "medium")]


def _log(msg):
    print(f"[dress {time.time() - _T0:7.1f}s] {msg}", flush=True)


def _rehearse():
    with open(os.path.join(_HERE, "calib.json"), "r", encoding="utf-8") as f:
        rows = json.load(f)["rows"]
    texts = list(dict.fromkeys(r["text"] for r in rows))
    label = {(r["model_id"], (r["effort"] or "default"), r["text"]): r["label"] for r in rows}
    import entry                                      # the candidate; its own clock (_T0) starts here
    _log(f"entry imported; {len(texts)} public templates x {len(_CALLS)} calls")
    tot = {"n": 0, "right": 0}
    for m, e in _CALLS:
        t0 = time.time()
        preds = entry.are_robust(m, e, list(texts))
        n = right = 0
        line = []
        for i, (t, p) in enumerate(zip(texts, preds)):
            y = label.get((m, e, t))
            if y is None:
                continue
            ok = bool(p) == (y == 0)
            n += 1
            right += int(ok)
            line.append(f"T{i + 1:02d}{'R' if p else 'N'}{'' if ok else '!'}")
        tot["n"] += n
        tot["right"] += right
        _log(f"call {m.split('/')[-1]}:{e}: {time.time() - t0:.0f}s, robust {sum(map(bool, preds))}/{len(preds)}, "
             f"labelled public rows {right}/{n} right | {' '.join(line)}")
    _log(f"DRESS TOTAL: labelled public rows {tot['right']}/{tot['n']} right; entry clock {time.time() - entry._T0:.0f}s, "
         f"wrapper clock {time.time() - _T0:.0f}s")


def are_robust(model_id: str, reasoning_effort: str = "default", problems: list = None) -> list:
    problems = list(problems or [])
    if not _DONE["ran"]:
        _DONE["ran"] = True
        try:
            _rehearse()
        except Exception as exc:
            _log(f"rehearsal failed ({type(exc).__name__}: {str(exc)[:200]})")
    return [True for _ in problems]
