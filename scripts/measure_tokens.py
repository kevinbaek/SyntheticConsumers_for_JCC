"""Measure input/output tokens of one full run, per call type, for the cost appendix.

  python scripts/measure_tokens.py --model claude-sonnet-5 --out outputs/final_claude-sonnet-5 --sample 150
  python scripts/measure_tokens.py --model gpt-5.5 --out outputs/final_gpt-5.5 --tiktoken-dir <dir with node_modules/js-tiktoken>
  python scripts/measure_tokens.py --model gemini-3.1-pro --out outputs/final_gemini-3.1-pro --sample 25 --live

Counting method per vendor (written into the output so the appendix can state it):
  claude  Anthropic token-counting endpoint (free) on a random sample per call type; output = count of
          [user ".", assistant <response>] minus count of [user "."]
  gpt     every call counted offline with the o200k_base tokenizer (js-tiktoken), +3 tokens per message, +3 reply
  gemini  --live: fresh API calls on a random sample per call type, reading usage_metadata (prompt, candidates,
          thoughts); responses are not cached and not used in any analysis
Totals = per-type mean x the design's call count for that type.
"""
import argparse
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from hallyu_twins import multicountry as mc
from hallyu_twins.config import load_config

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--sample", type=int, default=150)
ap.add_argument("--live", action="store_true")
ap.add_argument("--tiktoken-dir")
ap.add_argument("--seed", type=int, default=11)
a = ap.parse_args()
cfg = load_config("configs/default.yaml")
spec = next(m for m in cfg.models if m.name == a.model)
out = Path(a.out)

tw = pd.read_csv(out / "twins.csv")
c1 = mc.round1_calls(tw)
r1 = {json.loads(x)["call_id"]: json.loads(x)["text"] for x in open(out / "raw_r1.jsonl")}
by = {cid: mc.parse_json(t) for cid, t in r1.items()}
parsed = {c["resp_id"]: by.get(c["call_id"], {}) for c in c1 if c["mode"] == "ssr" and c["cond"] == "P3a"}
sub = tw.groupby("country", group_keys=False).head(30)
with tempfile.TemporaryDirectory() as td:
    c2 = mc.round2_calls(sub, parsed, 3, cfg.seed, Path(td))
cb = mc.b2_calls(3)
resp = dict(r1)
for f in ("raw_r2.jsonl", "raw_b2.jsonl"):
    if (out / f).exists():
        resp.update({json.loads(x)["call_id"]: json.loads(x)["text"] for x in open(out / f)})
types = {"r1_ssr": [c for c in c1 if c["mode"] == "ssr"], "r1_dlr": [c for c in c1 if c["mode"] == "dlr"],
         "r2_network": c2, "b2_direct": cb}
rng = np.random.default_rng(a.seed)


def sample(cs):
    if a.model.startswith("claude"):       # output tokens need the response: sample answered calls only
        cs = [c for c in cs if c["call_id"] in resp]
    if a.model.startswith("gpt") or len(cs) <= a.sample:
        return cs
    return [cs[i] for i in sorted(rng.choice(len(cs), a.sample, replace=False))]


res = {}
if a.model.startswith("claude"):
    import anthropic
    cl = anthropic.Anthropic(base_url="https://api.anthropic.com", api_key=os.environ[spec.api_key_env], max_retries=6)

    def cnt(system, msgs):
        kw = {"model": spec.model_id, "messages": msgs}
        if system:
            kw["system"] = system
        return cl.messages.count_tokens(**kw).input_tokens

    base = cnt(None, [{"role": "user", "content": "."}])

    def one(c):
        system = "\n".join(m["content"] for m in c["messages"] if m["role"] == "system")
        msgs = [m for m in c["messages"] if m["role"] != "system"]
        t = resp.get(c["call_id"], "")
        o = cnt(None, [{"role": "user", "content": "."}, {"role": "assistant", "content": t.strip() or "."}]) - base
        return cnt(system or None, msgs), o
    method = "Anthropic token-counting endpoint on a random sample per call type"
elif a.model.startswith("gpt"):
    method = "o200k_base tokenizer (js-tiktoken) on every call, +3 tokens per message and +3 for the reply"
    tmp = Path(tempfile.mkdtemp())
    rows = []
    for tname, cs in types.items():
        for c in cs:
            rows.append({"t": tname, "in": [m["content"] for m in c["messages"]], "out": resp.get(c["call_id"], ""),
                         "has": c["call_id"] in resp})
    (tmp / "calls.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    js = ("const fs=require('fs');const {Tiktoken}=require('js-tiktoken/lite');const o=require('js-tiktoken/ranks/o200k_base');"
          "const e=new Tiktoken(o.default||o);const L=fs.readFileSync(process.argv[2],'utf8').split('\\n');"
          "for(const l of L){const r=JSON.parse(l);let i=3;for(const m of r.in){i+=3+e.encode(m).length;}"
          "console.log(JSON.stringify([r.t,i,e.encode(r.out).length,r.has]));}")
    script = Path(a.tiktoken_dir) / "count_calls.js"      # beside node_modules so require() resolves
    script.write_text(js)
    p = subprocess.run(["node", str(script), str(tmp / "calls.jsonl")], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stderr[-2000:])
    lines = p.stdout.split("\n")
    counted = pd.DataFrame([json.loads(x) for x in lines if x], columns=["t", "in", "out", "has"])
else:
    from hallyu_twins.llm import make_llm
    llm = make_llm(spec, None)          # no cache: probe calls never enter the run's cache
    method = "fresh API calls on a random sample per call type, usage_metadata (prompt, candidates, thoughts)"

    def one(c):
        llm._call(c["messages"], c.get("rep", 0))
        return llm.last_usage()            # per-thread usage of this call

for tname, cs in types.items():
    if a.model.startswith("gpt"):
        g = counted[counted.t == tname]
        ins, outs, th = g["in"].to_numpy(float), g.loc[g.has, "out"].to_numpy(float), np.zeros(1)
        n_s = int(g.has.sum())          # calls with a response (input is counted for all design calls)
        if n_s == 0:
            outs = np.array([np.nan])
    else:
        s = sample(cs)
        if not a.model.startswith("claude") and not a.live:
            raise SystemExit("gemini needs --live")
        with ThreadPoolExecutor(6) as ex:
            got = list(ex.map(one, s))
        ins = np.array([x[0] for x in got], float)
        outs = np.array([x[1] for x in got], float)
        th = np.array([x[2] if len(x) > 2 else 0 for x in got], float)
        n_s = len(s)
    res[tname] = {"design_calls": len(cs), "sampled": n_s, "mean_in": float(ins.mean()), "mean_out": float(outs.mean()),
                  "mean_thinking": float(th.mean()), "sd_in": float(ins.std()), "sd_out": float(outs.std())}
tot = {k: sum(v["design_calls"] * v[f"mean_{k}"] for v in res.values()) for k in ("in", "out", "thinking")}
rec = {"model": a.model, "method": method, "per_type": res, "total_calls": sum(v["design_calls"] for v in res.values()),
       "total_input_tokens": tot["in"], "total_output_tokens": tot["out"], "total_thinking_tokens": tot["thinking"]}
json.dump(rec, open(out / "token_measure.json", "w"), indent=1)
print(json.dumps(rec, indent=1))
