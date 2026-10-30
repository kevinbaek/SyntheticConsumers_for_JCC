"""Check the offline GPT-5.5 token counts (o200k_base, +3 per message, +3 for the reply) against the usage reported
by the API on a fresh stratified sample of the released prompts. Fresh calls with new seeds; the main run and its
cache are untouched.

  python scripts/check_gpt_tokens.py --n 8 --tok <dir with js-tiktoken node_modules>
"""
import argparse
import json
import random
import subprocess
from pathlib import Path

from openai import OpenAI

from hallyu_twins.config import load_config

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=8, help="calls per prompt type")
ap.add_argument("--tok", required=True)
ap.add_argument("--out", default="outputs/final_gpt-5.5/token_check.json")
a = ap.parse_args()
cfg = load_config("configs/default.yaml")
spec = next(m for m in cfg.models if m.name == "gpt-5.5")
run = Path("outputs/final_gpt-5.5")
pools = {"r1 ssr": [], "r1 dlr": [], "r2": [], "b2": []}
for f, kind in (("prompts_r1.jsonl", None), ("prompts_r2.jsonl", "r2"), ("prompts_b2.jsonl", "b2")):
    for line in open(run / f):
        d = json.loads(line)
        k = kind or ("r1 ssr" if "|ssr|" in d["call_id"] else "r1 dlr")
        pools[k].append(d)
rng = random.Random(20261030)
sample = [(k, d) for k, v in pools.items() for d in rng.sample(v, a.n)]
client = OpenAI(timeout=180, max_retries=2)
rows = []
for k, d in sample:
    kw = dict(model=spec.model_id, messages=d["messages"], max_completion_tokens=spec.max_tokens, seed=777)
    if spec.temperature is not None:
        kw["temperature"] = spec.temperature
    kw.update(spec.extra)
    r = client.chat.completions.create(**kw)
    rows.append({"type": k, "call_id": d["call_id"], "in": [m["content"] for m in d["messages"]],
                 "out": r.choices[0].message.content or "", "api_in": r.usage.prompt_tokens,
                 "api_out": r.usage.completion_tokens})
json.dump(rows, open(a.out + ".raw", "w"))          # keep the API results before offline counting
tmp = Path(a.tok) / "check_in.jsonl"
with open(tmp, "w") as f:
    for r in rows:
        f.write(json.dumps({"t": r["type"], "in": r["in"], "out": r["out"], "has": True}) + "\n")
# count_calls.js reads one JSON object per line and must not see a trailing empty line
tmp.write_text(tmp.read_text().rstrip("\n"))
res = subprocess.run(["node", "count_calls.js", "check_in.jsonl"], cwd=a.tok, capture_output=True, text=True, check=True)
offl = [json.loads(x) for x in res.stdout.strip().splitlines()]
for r, o in zip(rows, offl):
    r["offline_in"], r["offline_out"] = o[1], o[2]
    del r["in"], r["out"]
tot = {q: sum(r[q] for r in rows) for q in ("api_in", "offline_in", "api_out", "offline_out")}
summary = {"calls": len(rows), **tot,
           "input_rel_diff": (tot["offline_in"] - tot["api_in"]) / tot["api_in"],
           "output_rel_diff": (tot["offline_out"] - tot["api_out"]) / tot["api_out"],
           "max_abs_input_diff_per_call": max(abs(r["offline_in"] - r["api_in"]) for r in rows)}
json.dump({"summary": summary, "calls": rows}, open(a.out, "w"), indent=1)
print(json.dumps(summary, indent=1))
