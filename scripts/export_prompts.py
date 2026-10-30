"""Write every prompt of a final run as sent to the API (prompts_r1/r2/b2.jsonl: call_id + messages) and check that
each regenerated prompt reproduces the cache key of the response it produced (so the released prompts are exactly
the ones that were sent).

  python scripts/export_prompts.py --model gpt-5.5 --out outputs/final_gpt-5.5
"""
import argparse
import json
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd

from hallyu_twins import multicountry as mc
from hallyu_twins.config import load_config
from hallyu_twins.llm import _key

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
cfg = load_config("configs/default.yaml")
spec = next(m for m in cfg.models if m.name == a.model)
out = Path(a.out)
tw = pd.read_csv(out / "twins.csv")
c1 = mc.round1_calls(tw)
raw1 = {json.loads(x)["call_id"]: json.loads(x)["text"] for x in open(out / "raw_r1.jsonl")}
by = {cid: mc.parse_json(t) for cid, t in raw1.items()}
parsed = {c["resp_id"]: by.get(c["call_id"], {}) for c in c1 if c["mode"] == "ssr" and c["cond"] == "P3a"}
sub = pd.read_csv(out / "twins_network.csv")
with tempfile.TemporaryDirectory() as td:
    c2 = mc.round2_calls(sub, parsed, 3, cfg.seed, Path(td))
cb = mc.b2_calls(3)
db = sqlite3.connect(f"file:{Path(cfg.cache_dir) / (spec.name + '.sqlite')}?mode=ro", uri=True)
report = {}
for name, calls in (("r1", c1), ("r2", c2), ("b2", cb)):
    keys = [_key(spec.provider, spec.model_id, spec.temperature, spec.max_tokens, spec.extra, c["messages"],
                 c.get("rep", 0), c["call_id"]) for c in calls]
    found = 0
    for i in range(0, len(keys), 900):
        ch = keys[i:i + 900]
        found += db.execute("SELECT count(*) FROM kv WHERE k IN (%s)" % ",".join("?" * len(ch)), ch).fetchone()[0]
    with open(out / f"prompts_{name}.jsonl", "w") as f:
        for c in calls:
            f.write(json.dumps({"call_id": c["call_id"], "rep": c.get("rep", 0), "messages": c["messages"]},
                               ensure_ascii=False) + "\n")
    report[name] = {"calls": len(calls), "prompt_matches_cached_response": found}
json.dump(report, open(out / "prompts_check.json", "w"), indent=1)
print(a.model, report)
