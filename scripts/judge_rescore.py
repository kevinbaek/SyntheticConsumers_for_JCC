"""Second scoring of the same free-text SSR answers (review round 2): an LLM judge classifies each favorability
(XQ5) and recommendation (XQ6) answer into the five labelled options. No new twin answers are generated; the judge
sees only the answer text (no persona, country or model), in shuffled batches mixing models and countries.

  python scripts/judge_rescore.py --judge gpt-5.5 --out outputs/judge                 # all answers
  python scripts/judge_rescore.py --judge claude-sonnet-5 --every 10 --out outputs/judge  # every 10th batch (agreement)

Writes outputs/judge/<judge>/judge_scores.csv, raw_judge.jsonl, prompts_judge.jsonl, judge_meta.json.
"""
import argparse
import json
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd

from hallyu_twins import multicountry as mc
from hallyu_twins.codebook import ITEMS
from hallyu_twins.config import load_config
from hallyu_twins.llm import Cache, make_llm

RUNS = ["claude-sonnet-5", "gpt-5.5", "gemini-3.1-pro"]
PROMPT = ("You are coding answers to an open-ended survey question.\n\nQuestion: \"{q}\"\n\nAnswer options:\n{opts}\n\n"
          "For each answer below, choose the option number (1-5) that best matches what the respondent says. Judge only "
          "from the answer text.\n\n{answers}\n\nReply with a JSON object only, mapping each answer id (A01, A02, ...) to "
          "an option number.")

ap = argparse.ArgumentParser()
ap.add_argument("--judge", required=True)
ap.add_argument("--out", default="outputs/judge")
ap.add_argument("--batch", type=int, default=50)
ap.add_argument("--every", type=int, default=1, help="judge only every k-th batch (subset for agreement checks)")
ap.add_argument("--workers", type=int, default=12)
a = ap.parse_args()
cfg = load_config("configs/default.yaml")
spec = next(m for m in cfg.models if m.name == a.judge)
llm = make_llm(spec, Cache(str(Path(cfg.cache_dir) / f"{spec.name}.sqlite")))
out = Path(a.out) / a.judge
out.mkdir(parents=True, exist_ok=True)

rows = []
for m in RUNS:
    run = Path(f"outputs/final_{m}")
    s = pd.read_csv(run / "scored.csv")
    tw = pd.read_csv(run / "twins.csv").set_index("resp_id")
    s = s[(s.cond == "P3a") & (s["round"] == 1) & (s["mode"] == "ssr") & s["var"].isin(["XQ5", "XQ6"]) & s["text"].notna()].copy()
    s["country"] = tw.loc[s.resp_id, "country"].to_numpy()
    P = s[["p1", "p2", "p3", "p4", "p5"]].to_numpy()
    s["ssr_expected"] = P @ np.arange(1, 6)
    s["ssr_t2b"] = P[:, 3] + P[:, 4]
    s["model"] = m
    rows.append(s[["model", "resp_id", "country", "var", "text", "ssr_expected", "ssr_t2b"]])
A = pd.concat(rows, ignore_index=True)

calls, members = [], {}
for var in ("XQ5", "XQ6"):
    it = ITEMS[var]
    g = A[A["var"] == var].reset_index(drop=True)
    order = list(range(len(g)))
    random.Random(20261030 + (var == "XQ6")).shuffle(order)          # fixed shuffle: models and countries mixed
    opts = "\n".join(f"{k + 1}. {lab}" for k, lab in enumerate(it.scale.labels))
    for b, start in enumerate(range(0, len(order), a.batch)):
        if b % a.every:
            continue
        idx = order[start:start + a.batch]
        ans = "\n".join(f"A{j + 1:02d}: \"{g.loc[i, 'text']}\"" for j, i in enumerate(idx))
        cid = f"JUDGE|{var}|b{b:04d}"
        calls.append({"call_id": cid, "rep": 0, "messages": [{"role": "user", "content": PROMPT.format(q=it.text, opts=opts, answers=ans)}]})
        members[cid] = (var, [g.loc[i, ["model", "resp_id"]].tolist() for i in idx])

res = mc.execute(calls, llm, out / "raw_judge.jsonl", workers=a.workers)
with open(out / "prompts_judge.jsonl", "w") as f:
    for c in calls:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
lab = []
bad = 0
for r in res:
    var, mem = members[r["call_id"]]
    m = re.search(r"\{.*\}", r["text"], flags=re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        d = {}
    for j, (mdl, rid) in enumerate(mem):
        v = d.get(f"A{j + 1:02d}")
        try:
            v = int(v)
        except (TypeError, ValueError):
            v = -1
        bad += v not in (1, 2, 3, 4, 5)
        lab.append({"model": mdl, "resp_id": rid, "var": var, "judge_option": v})
L = pd.DataFrame(lab).merge(A.drop(columns="text"), on=["model", "resp_id", "var"], how="left")
L.to_csv(out / "judge_scores.csv", index=False)
meta = {"judge": spec.name, "model_id": spec.model_id, "calls": len(calls), "answers": len(L), "unparsed": int(bad),
        "errors": sum(r["text"].startswith("__ERROR__") for r in res), "usage": getattr(llm, "usage", {})}
json.dump(meta, open(out / "judge_meta.json", "w"), indent=1)
print(json.dumps(meta))
