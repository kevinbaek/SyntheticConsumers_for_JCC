"""Job specs: every LLM call is a JSON line, so any executor can fill it.

A job carries the exact chat messages; a response carries ``job_id`` and ``text``. The same
job file can be executed by the API clients in llm.py (main study) or by an external agent
(pilot), and scoring never depends on who executed it.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from .codebook import ITEMS
from .elicit import DLR_USER, messages, options_text
from .network import exposure_prompt
from .personas import build_persona, swap_map


def job_id(cond: str, rid: str, var: str, mode: str, rnd: int = 1, rep: int = 0) -> str:
    return f"{cond}|{rid}|{var}|{mode}|r{rnd}|k{rep}"


def round1_jobs(twins: pd.DataFrame, cond: str, level: str, items, label: str = "true",
                modes=("ssr", "dlr"), reverse_share: float = 0.5, seed: int = 0, rep: int = 0,
                distilled: dict[str, str] | None = None) -> list[dict]:
    """items: a list of variable names, or a function row -> list (skip logic per twin)."""
    swap = swap_map(seed) if label == "swap" else None
    jobs = []
    for i, (_, row) in enumerate(twins.iterrows()):
        if level == "P4D" and not (distilled or {}).get(str(row["resp_id"])):
            continue                                   # failed the leakage audit -> excluded, reported
        p = build_persona(row, level, label, swap,
                          distilled=(distilled or {}).get(str(row["resp_id"])))
        reverse = (i % 2 == 1) if reverse_share == 0.5 else False
        for var in (items(row) if callable(items) else items):
            for mode in modes:
                jobs.append({"job_id": job_id(cond, p.resp_id, var, mode, 1, rep), "cond": cond, "level": level,
                             "label": label, "resp_id": p.resp_id, "country": row["country"], "var": var,
                             "mode": mode, "round": 1, "rep": rep, "reverse": reverse and mode == "dlr",
                             "persona": p.text, "messages": messages(p.text, ITEMS[var], mode, reverse)})
    return jobs


def round2_jobs(twins: pd.DataFrame, src_cond: str, cond: str, kind: str, nbrs: dict[str, list[str]],
                r1: dict[str, str], items: list[str], level: str, rep: int = 0) -> list[dict]:
    """Network conditions: kind = self | random | homophily. r1 maps job_id -> round-1 text."""
    jobs = []
    for i, (_, row) in enumerate(twins.iterrows()):
        p = build_persona(row, level, "true")
        for var in items:
            it = ITEMS[var]
            own = r1.get(job_id(src_cond, p.resp_id, var, "ssr", 1, rep), "")
            nb = [r1.get(job_id(src_cond, n, var, "ssr", 1, rep), "") for n in nbrs.get(p.resp_id, [])]
            nb = [t for t in nb if t]
            base = exposure_prompt("self" if kind == "self" else "exposure", it.text, own, nb)
            sys = messages(p.text, it, "ssr")[0]
            reverse = i % 2 == 1
            ssr_user = base + " Answer in one or two sentences, without numbers."
            dlr_user = base + "\n" + DLR_USER.format(question=it.text, options=options_text(it.scale, reverse))
            for mode, user, rev in (("ssr", ssr_user, False), ("dlr", dlr_user, reverse)):
                jobs.append({"job_id": job_id(cond, p.resp_id, var, mode, 2, rep), "cond": cond, "level": level,
                             "label": "true", "resp_id": p.resp_id, "country": row["country"], "var": var,
                             "mode": mode, "round": 2, "rep": rep, "reverse": rev, "network": kind,
                             "neighbours": nbrs.get(p.resp_id, []), "persona": p.text,
                             "messages": [sys, {"role": "user", "content": user}]})
    return jobs


def write_jsonl(rows: list[dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_jobs(jobs: list[dict], llm, max_workers: int = 8) -> list[dict]:
    def one(j):
        c = llm.complete(j["messages"], rep=j.get("rep", 0), call_id=j["job_id"])
        return {"job_id": j["job_id"], "text": c.text, "model": llm.spec.name, "cached": c.cached}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        return list(ex.map(one, jobs))


def agent_batches(jobs: list[dict], out_dir: str | Path, per_batch: int = 5) -> list[Path]:
    """Group jobs by twin and write one interview file per batch of twins (for agent executors).
    Free-text (ssr) questions are listed before numbered (dlr) ones, as in the API path where
    each call is independent."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    by_twin: dict[str, list[dict]] = {}
    for j in jobs:
        by_twin.setdefault(f"{j['cond']}|{j['resp_id']}", []).append(j)
    keys = list(by_twin)
    paths = []
    for b in range(0, len(keys), per_batch):
        twins = []
        for k in keys[b:b + per_batch]:
            js = sorted(by_twin[k], key=lambda j: j["mode"] != "ssr")   # stable: keeps survey order
            twins.append({"twin": k, "system": js[0]["messages"][0]["content"],
                          "questions": [{"job_id": j["job_id"], "prompt": j["messages"][-1]["content"]} for j in js]})
        p = out_dir / f"batch_{b // per_batch:02d}.json"
        p.write_text(json.dumps(twins, ensure_ascii=False, indent=1), encoding="utf-8")
        paths.append(p)
    return paths
