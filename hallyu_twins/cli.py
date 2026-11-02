"""Command line entry point.

  hallyu-twins pilot prepare  --country Japan --n 30 --out outputs/pilot_japan
  hallyu-twins pilot run      --config configs/default.yaml --model gpt-5.5 --out outputs/pilot_japan_gpt
  hallyu-twins pilot ingest   --out outputs/pilot_japan --round 1 --responses DIR   (agent executor)
  hallyu-twins pilot round2   --out outputs/pilot_japan
  hallyu-twins pilot analyze  --out outputs/pilot_japan --country Japan --embedding onnx
  hallyu-twins multicountry   --model claude-sonnet-5 --n 10 --k 3       (30 countries, table targets)
  hallyu-twins experiment     --config configs/default.yaml [--mock] [--model NAME ...]
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from .config import load_config


def _embedder(kind: str, cache_dir: str):
    from .embed import default_cache, make_embedder
    spec = {"onnx": {"provider": "onnx"}, "openai": {"provider": "openai"}, "mock": {"provider": "mock"}}[kind]
    return make_embedder(spec, default_cache(cache_dir))


def _analyze(out: Path, country: str, embedding: str, cache_dir: str) -> None:
    from . import pilot
    from .elicit import SSRScorer
    emb = _embedder(embedding, cache_dir)
    df = pilot.score(out, SSRScorer(emb))
    S = pilot.summarize(df, country, out)
    pilot.network_effect(df, out)
    pilot.sensitivity(out, emb)
    pilot.heterogeneity(out)
    pilot.figure(S, country, out)
    print(S.to_string())


def main(argv=None) -> None:
    ap = argparse.ArgumentParser("hallyu-twins")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("pilot")
    p.add_argument("stage", choices=["prepare", "run", "ingest", "round2", "analyze"])
    p.add_argument("--country", default="Japan")
    p.add_argument("--n", type=int, default=30)
    p.add_argument("--n-p1", type=int, default=10)
    p.add_argument("--k", type=int, default=3)
    p.add_argument("--out", default="outputs/pilot_japan")
    p.add_argument("--config", default="configs/default.yaml")
    p.add_argument("--model")
    p.add_argument("--round", type=int, default=1)
    p.add_argument("--responses", help="directory with responses_*.jsonl written by an agent executor")
    p.add_argument("--embedding", default="onnx", choices=["onnx", "openai", "mock"])
    m = sp.add_parser("multicountry")
    m.add_argument("--config", default="configs/default.yaml")
    m.add_argument("--model", required=True)
    m.add_argument("--n", type=int, default=10)
    m.add_argument("--k", type=int, default=3)
    m.add_argument("--workers", type=int, default=12)
    m.add_argument("--embedding", default="onnx", choices=["onnx", "openai", "mock"])
    m.add_argument("--out")
    m.add_argument("--reanalyze", action="store_true", help="recompute tables from saved responses only")
    e = sp.add_parser("experiment")
    e.add_argument("--config", default="configs/default.yaml")
    e.add_argument("--mock", action="store_true")
    e.add_argument("--model", action="append")
    a = ap.parse_args(argv)

    if a.cmd == "multicountry":
        from . import multicountry as mc
        from .llm import Cache, make_llm
        cfg = load_config(a.config)
        spec = next(x for x in cfg.models if x.name == a.model)
        out = Path(a.out or f"outputs/mc_{a.model}")
        emb = _embedder(a.embedding, cfg.cache_dir)
        if a.reanalyze:
            r = mc.reanalyze(out, emb)
        else:
            llm = make_llm(spec, Cache(str(Path(cfg.cache_dir) / f"{spec.name}.sqlite")))
            mc.run(llm, out, a.n, a.k, cfg.seed, a.workers, emb)
            r = mc.reanalyze(out, emb)
        mc.figure(r["T"], r["b2"], out, spec.name)
        print(r["evaluation"].to_string())
        return

    if a.cmd == "experiment":
        from . import experiment
        r = experiment.run(load_config(a.config), mock=a.mock, models=a.model)
        print(json.dumps(r["criteria"], indent=1))
        return

    from . import pilot
    from .jobs import read_jsonl, run_jobs, write_jsonl
    out = Path(a.out)
    cfg = load_config(a.config)
    if a.stage == "prepare":
        pilot.prepare(a.country, out, a.n, a.n_p1, cfg.seed)
    elif a.stage == "ingest":
        jobs = {j["job_id"] for j in read_jsonl(out / f"jobs_r{a.round}.jsonl")}
        rows = {}
        for f in sorted(glob.glob(str(Path(a.responses) / "responses_*.jsonl"))):
            for r in read_jsonl(f):
                if r["job_id"] in jobs:
                    rows[r["job_id"]] = {"job_id": r["job_id"], "text": str(r["text"]), "model": "agent"}
        write_jsonl(list(rows.values()), out / f"responses_r{a.round}.jsonl")
        print(f"ingested {len(rows)}/{len(jobs)}")
    elif a.stage == "round2":
        pilot.round2(out, a.k, cfg.seed)
    elif a.stage == "analyze":
        _analyze(out, a.country, a.embedding, cfg.cache_dir)
    elif a.stage == "run":
        from .llm import Cache, make_llm
        spec = next(m for m in cfg.models if m.name == a.model)
        llm = make_llm(spec, Cache(str(Path(cfg.cache_dir) / f"{spec.name}.sqlite")))
        if not (out / "jobs_r1.jsonl").exists():
            pilot.prepare(a.country, out, a.n, a.n_p1, cfg.seed)
        write_jsonl(run_jobs(read_jsonl(out / "jobs_r1.jsonl"), llm, cfg.max_workers), out / "responses_r1.jsonl")
        j2 = pilot.round2(out, a.k, cfg.seed)
        write_jsonl(run_jobs(j2, llm, cfg.max_workers), out / "responses_r2.jsonl")
        _analyze(out, a.country, a.embedding, cfg.cache_dir)


if __name__ == "__main__":
    main()
