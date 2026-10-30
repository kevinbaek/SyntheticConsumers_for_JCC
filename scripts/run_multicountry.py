"""30-country table-only test. Usage:
  python scripts/run_multicountry.py --model claude-sonnet-5 --n 10 --k 3 --out outputs/mc_claude-sonnet-5
Keys are read from the env var named in configs/default.yaml (api_key_env)."""
import argparse, json, time
from pathlib import Path
import pandas as pd
from hallyu_twins import multicountry as mc
from hallyu_twins.config import load_config
from hallyu_twins.llm import Cache, make_llm
from hallyu_twins.embed import make_embedder, default_cache

ap = argparse.ArgumentParser()
ap.add_argument("--config", default="configs/default.yaml")
ap.add_argument("--model", required=True)
ap.add_argument("--n", type=int, default=10)
ap.add_argument("--k", type=int, default=3)
ap.add_argument("--workers", type=int, default=12)
ap.add_argument("--n-network", type=int, default=None, help="nested per-country subsample for network conditions")
ap.add_argument("--b2-reps", type=int, default=1)
ap.add_argument("--embedding", default="onnx")
ap.add_argument("--out")
a = ap.parse_args()
cfg = load_config(a.config)
spec = next(m for m in cfg.models if m.name == a.model)
out = Path(a.out or f"outputs/mc_{a.model}")
llm = make_llm(spec, Cache(str(Path(cfg.cache_dir) / f"{spec.name}.sqlite")))
emb = make_embedder({"provider": a.embedding}, default_cache(cfg.cache_dir))
t = time.time()
r = mc.run(llm, out, n_per_country=a.n, k=a.k, seed=cfg.seed, workers=a.workers, embedder=emb,
           n_network=a.n_network, b2_reps=a.b2_reps)
meta = {"model": spec.name, "model_id": spec.model_id, "cutoff": spec.cutoff, "n_per_country": a.n, "k": a.k,
        "n_network": a.n_network, "b2_reps": a.b2_reps,
        "calls": r["calls"], "errors": r["errors"], "usage": llm.usage, "minutes": round((time.time() - t) / 60, 1),
        "embedding": a.embedding}
json.dump(meta, open(out / "run_meta.json", "w"), indent=1)
pd.set_option("display.width", 250)
print(json.dumps(meta)); print(r["evaluation"].to_string()); print(r["domains"].to_string()); print(r["network"].to_string())
