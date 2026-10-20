# Old single-process harness path (several problems per call, 7 calls in ONE process): v95 vs v104 must give the same answers.
import sys, os, json, subprocess, re
sys.path.insert(0, 'rehearsal'); import run_per_case as R
CHILD = r'''
import sys, json, importlib.util
sub = sys.argv[1]; sys.path.insert(0, sub)
spec = importlib.util.spec_from_file_location("participant_solution", sub + "/solution.py"); m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m; spec.loader.exec_module(m)
P = [f"Synthetic problem OLD-{i}: find the value of N for these parameters. " + "x" * 200 for i in range(12)]
out = []
for c in ["Qwen", "Skywork", "Olmo", "DeepSeek", "high", "low", "medium"]:
    mid, eff = {"Qwen": ("Qwen/Qwen3.5-4B", "default"), "Skywork": ("Skywork/Skywork-OR1-Math-7B", "default"), "Olmo": ("allenai/Olmo-3-7B-Think", "default"),
                "DeepSeek": ("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "default"), "high": ("openai/gpt-oss-120b", "high"),
                "low": ("openai/gpt-oss-120b", "low"), "medium": ("openai/gpt-oss-120b", "medium")}[c]
    out.append(m.are_robust(mid, reasoning_effort=eff, problems=P))
import time
print("@@OUT " + json.dumps(out))
'''
res = {}
for b in sys.argv[1:]:
    tmp, sub = R.prepare(b, ())
    env = {k: v for k, v in os.environ.items() if not re.search(r"BUDGET|DEADLINE|TIMEOUT|REMAINING|^MOCK_", k, re.I)}
    env.update(R.BASE_ENV, MOCK_SLOW="1.0")
    open(os.path.join(tmp, "child.py"), "w").write(CHILD)
    r = subprocess.run([R.PY, os.path.join(tmp, "child.py"), sub], capture_output=True, text=True, env=env, cwd=tmp)
    m = re.search(r"^@@OUT (.*)$", r.stdout, re.M)
    res[b] = json.loads(m.group(1)) if m else r.stderr[-500:]
    print(b, "calls", len(res[b]) if m else res[b], "| v83 path lines:", len(re.findall(r"call \d+ \(", r.stdout)), "| case-mode lines:", len(re.findall(r"case \(", r.stdout)))
a, b = list(res.values())
print("identical answers on the old single-process path:", a == b, sum(len(x) for x in a), "answers")
