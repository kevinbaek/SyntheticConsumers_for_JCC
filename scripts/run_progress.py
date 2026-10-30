"""How many of a final run's model calls are already in the response cache (no API calls).

  python scripts/run_progress.py --model gpt-5.5 --out outputs/final_gpt-5.5
"""
import argparse
import json
import sqlite3
from pathlib import Path

import pandas as pd

from hallyu_twins import multicountry as mc
from hallyu_twins.config import load_config
from hallyu_twins.llm import _key

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--n-network", type=int, default=30)
ap.add_argument("--k", type=int, default=3)
ap.add_argument("--b2-reps", type=int, default=3)
a = ap.parse_args()
cfg = load_config("configs/default.yaml")
spec = next(m for m in cfg.models if m.name == a.model)
out = Path(a.out)
db = sqlite3.connect(f"file:{Path(cfg.cache_dir) / (spec.name + '.sqlite')}?mode=ro", uri=True)


def key(c):
    return _key(spec.provider, spec.model_id, spec.temperature, spec.max_tokens, spec.extra, c["messages"],
                c.get("rep", 0), c["call_id"])


def have(calls):
    ks = [key(c) for c in calls]
    n = 0
    for i in range(0, len(ks), 900):
        ch = ks[i:i + 900]
        n += db.execute("SELECT count(*) FROM kv WHERE k IN (%s)" % ",".join("?" * len(ch)), ch).fetchone()[0]
    return n


tw = pd.read_csv(out / "twins.csv")
c1 = mc.round1_calls(tw)
rep = {"r1": [len(c1), have(c1)]}
raw1 = out / "raw_r1.jsonl"
if raw1.exists():
    r1 = [json.loads(x) for x in open(raw1)]
    _, parsed = mc.expand.__wrapped__(c1, r1) if hasattr(mc.expand, "__wrapped__") else (None, None)
    if parsed is None:  # rebuild parsed answers exactly as run() does, without writing files
        by = {r["call_id"]: mc.parse_json(r["text"]) for r in r1}
        parsed = {c["resp_id"]: by.get(c["call_id"], {}) for c in c1 if c["mode"] == "ssr" and c["cond"] == "P3a"}
    sub = tw.groupby("country", group_keys=False).head(a.n_network)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        c2 = mc.round2_calls(sub, parsed, a.k, cfg.seed, Path(td))
    rep["r2"] = [len(c2), have(c2)]
cb = mc.b2_calls(a.b2_reps)
rep["b2"] = [len(cb), have(cb)]
print(json.dumps({"model": a.model, "calls_total_cached": rep}))
