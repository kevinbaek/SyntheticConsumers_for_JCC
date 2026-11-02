"""Confirmatory pipeline on KOFICE microdata (1:1 digital twins), or on mock data for dry runs.

For each model:
  1. SSR calibration on wave-14 twins (softmax tau only; 'maier' needs none). Wave 15 never used.
  2. MAIN   P4 / true label / no network, all wave-15 twins.
  3. ABLATE on a nested subsample: P0..P4 (+P4D), label none/swap, network self/random/homophily.
  4. Baselines B0, B1, B3, B4 (B2 optional, needs the model).
  5. Metrics per (model, condition, mode, item) + pre-registered success criteria.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import baselines as B
from .codebook import ITEMS, OVERALL_FAV, OVERALL_REC, TARGETS_POP, questionnaire_order
from .config import Config, ModelSpec
from .data.loader import load_wave, tidy
from .data.mock import make_wave
from .data.sampling import stratified_sample, subsample
from .elicit import SSRScorer, parse_dlr
from .embed import default_cache, make_embedder
from .jobs import read_jsonl, round1_jobs, round2_jobs, run_jobs, write_jsonl
from .llm import Cache, make_llm
from .metrics import item_metrics, onehot, split_half_ceiling
from .network import build_network, homophily_diagnostic
from .personas import build_persona, distill_profile

PCOLS = [f"p{k}" for k in range(1, 6)]


def load_data(cfg: Config, mock: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    if mock:
        w15 = tidy(make_wave(15, scale=0.1, seed=cfg.seed), 15, cfg.country_codes)
        w14 = tidy(make_wave(14, scale=0.1, seed=cfg.seed), 14, cfg.country_codes)
    else:
        w15 = load_wave(cfg.raw_wave15, 15, cfg.country_codes)
        w14 = load_wave(cfg.raw_wave14, 14, cfg.country_codes_w14 or cfg.country_codes)
    return w15, w14


def items_for(row) -> list[str]:
    return questionnaire_order(list(row["answered_domains"]))


def _execute(jobs, llm, path: Path, workers: int) -> dict[str, str]:
    write_jsonl(jobs, path.with_name(path.stem + "_jobs.jsonl"))
    res = run_jobs(jobs, llm, workers)
    write_jsonl(res, path)
    return {r["job_id"]: r["text"] for r in res}


def _score(jobs, texts, scorer: SSRScorer, human: pd.DataFrame, tau: float | None = None) -> pd.DataFrame:
    df = pd.DataFrame([{k: j[k] for k in ("cond", "resp_id", "country", "var", "mode", "round", "reverse")}
                       | {"text": texts.get(j["job_id"])} for j in jobs])
    out = []
    for (var, mode), g in df.groupby(["var", "mode"]):
        if mode == "ssr":
            P = scorer.probs(ITEMS[var], g["text"].fillna("").tolist(), tau=tau)
        else:
            P = onehot(np.array([parse_dlr(t, r) for t, r in zip(g["text"], g["reverse"])]))
        out.append(pd.concat([g.reset_index(drop=True), pd.DataFrame(P, columns=PCOLS)], axis=1))
    S = pd.concat(out, ignore_index=True)
    H = human.set_index("resp_id")
    S["h"] = [H.at[r, v] if v in H.columns else np.nan for r, v in zip(S.resp_id, S["var"])]
    S["w"] = H.loc[S.resp_id, "weight"].to_numpy()
    for c in ("continent", "sex", "age_band"):
        S[c] = H.loc[S.resp_id, c].to_numpy()
    return S


def calibrate_tau(cfg: Config, llm, scorer: SSRScorer, w14: pd.DataFrame, out: Path) -> float:
    """Pick softmax tau minimising mean KS distance on wave-14 twins (all items pooled by item)."""
    if scorer.method != "softmax":
        return float("nan")
    n_c = max(5, int(np.ceil(cfg.n_calibration_twins / w14.country.nunique())))
    cal = stratified_sample(w14, n_c, cfg.seed + 14)
    jobs = round1_jobs(cal, "CAL", cfg.main_condition["persona"], items_for, modes=("ssr",), seed=cfg.seed)
    texts = _execute(jobs, llm, out / "calibration_responses.jsonl", cfg.max_workers)
    best, rows = None, []
    for tau in cfg.ssr_tau_grid:
        S = _score(jobs, texts, scorer, cal, tau=tau)
        ks = [item_metrics(g)[0]["ks_sim"] for _, g in S.groupby("var") if g.h.notna().sum() > 20]
        rows.append({"tau": tau, "ks_sim": float(np.mean(ks))})
        if best is None or rows[-1]["ks_sim"] > best[1]:
            best = (tau, rows[-1]["ks_sim"])
    pd.DataFrame(rows).to_csv(out / "calibration_tau.csv", index=False)
    return best[0]


def run_model(cfg: Config, spec: ModelSpec, w15: pd.DataFrame, w14: pd.DataFrame, root: Path) -> pd.DataFrame:
    out = root / spec.name
    out.mkdir(parents=True, exist_ok=True)
    cache = Cache(str(Path(cfg.cache_dir) / f"{spec.name}.sqlite"))
    llm = make_llm(spec, cache)
    scorer = SSRScorer(make_embedder(cfg.embedding, default_cache(cfg.cache_dir)), method=cfg.ssr_method)
    tau = calibrate_tau(cfg, llm, scorer, w14, out)
    twins = stratified_sample(w15, cfg.n_per_country, cfg.seed)
    sub = subsample(twins, cfg.n_per_country_ablation, cfg.seed + 1)
    twins.to_csv(out / "twins.csv", index=False)
    scored = []

    def run(jobs, name, human):
        texts = _execute(jobs, llm, out / f"{name}.jsonl", cfg.max_workers)
        S = _score(jobs, texts, scorer, human, tau=None if np.isnan(tau) else tau)
        scored.append(S)
        return texts

    mc = cfg.main_condition
    run(round1_jobs(twins, "MAIN", mc["persona"], items_for, mc["label"], seed=cfg.seed), "main", twins)
    for lvl in cfg.ablations["persona"]:
        distilled = None
        if lvl == "P4D":
            distilled, audit = {}, []
            for _, row in sub.iterrows():
                txt = build_persona(row, "P4").text
                prof, verdict = distill_profile(txt, llm, llm)
                audit.append({"resp_id": row.resp_id, "passed": prof is not None, "verdict": verdict})
                if prof:
                    distilled[str(row.resp_id)] = prof
            pd.DataFrame(audit).to_csv(out / "p4d_audit.csv", index=False)
        texts = run(round1_jobs(sub, f"A-{lvl}", lvl, items_for, seed=cfg.seed, distilled=distilled), f"abl_{lvl}", sub)
        if lvl == "P4":
            r1_p4 = texts
    for lab in cfg.ablations["label"]:
        if lab != "true":
            run(round1_jobs(sub, f"A-P4-{lab}", "P4", items_for, lab, seed=cfg.seed), f"abl_label_{lab}", sub)
    diag = {}
    for kind in cfg.ablations["network"]:
        if kind == "none":
            continue
        nb = {} if kind == "self" else build_network(sub, kind, cfg.network_k, cfg.seed, cfg.network_features)
        if nb:
            diag[kind] = homophily_diagnostic(sub, nb, cfg.network_features)
        run(round2_jobs(sub, "A-P4", f"N-{kind}", kind, nb, r1_p4, cfg.network_items, "P4"), f"net_{kind}", sub)
    json.dump({"tau": tau, "network_similarity": diag}, open(out / "run_meta.json", "w"), indent=1)
    S = pd.concat(scored, ignore_index=True)
    S["model"] = spec.name
    S.to_parquet(out / "scored.parquet") if _has_pyarrow() else S.to_csv(out / "scored.csv.gz", index=False)
    return S


def _has_pyarrow() -> bool:
    try:
        import pyarrow  # noqa: F401
        return True
    except ImportError:
        return False


def baseline_scores(twins: pd.DataFrame, w15: pd.DataFrame, w14: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    rows = []
    for var in items:
        tw = twins[twins[var].notna()] if var in twins else twins.iloc[0:0]
        if tw.empty:
            continue
        for name, P in (("B0", B.b0(tw, var)), ("B1", B.b1(tw, var, w14)), ("B3", B.b3(tw, var, w14)),
                        ("B4", B.b4(tw, var, w15))):
            d = pd.DataFrame({"model": "baseline", "cond": name, "mode": "dist", "var": var,
                              "resp_id": tw.resp_id.values, "country": tw.country.values,
                              "continent": tw.continent.values, "sex": tw.sex.values,
                              "age_band": tw.age_band.values, "h": tw[var].values, "w": tw.weight.values})
            rows.append(pd.concat([d, P.reset_index(drop=True)], axis=1))
    return pd.concat(rows, ignore_index=True)


def evaluate(S: pd.DataFrame, w15: pd.DataFrame, cfg: Config, out: Path) -> pd.DataFrame:
    rows = []
    for (model, cond, mode, var), g in S.groupby(["model", "cond", "mode", "var"]):
        if g.h.notna().sum() < 20:
            continue
        m, _ = item_metrics(g.reset_index(drop=True))
        rows.append({"model": model, "cond": cond, "mode": mode, "var": var} | m)
    M = pd.DataFrame(rows)
    ceil = {}
    for var in M["var"].unique():
        hum = w15[["country", var, "weight"]].dropna().rename(columns={var: "h", "weight": "w"})
        ceil[var] = split_half_ceiling(hum, min(cfg.split_half_reps, 200), cfg.seed)
    M["ceiling_bc"] = M["var"].map(ceil)
    M["CA"] = M["r_bc"] / M["ceiling_bc"]
    M.to_csv(out / "metrics_by_item.csv", index=False)
    return M


def success_criteria(M: pd.DataFrame, out: Path) -> dict:
    """Pre-registered criteria for 'beyond country-level inference' (see docs/preregistration.md)."""
    res = {}
    key = [OVERALL_FAV, OVERALL_REC] + TARGETS_POP
    base = M[(M.model == "baseline")].groupby(["cond", "var"]).mean(numeric_only=True)
    for model in sorted(set(M.model) - {"baseline"}):
        mm = M[(M.model == model) & (M.cond == "MAIN") & (M["mode"] == "ssr") & (M["var"].isin(key))]
        if mm.empty:
            continue
        b3 = base.loc["B3"] if "B3" in base.index.get_level_values(0) else None
        b4 = base.loc["B4"] if "B4" in base.index.get_level_values(0) else None
        r_wc = float(mm.r_wc.mean())
        res[model] = {
            "C1_rwc_vs_B3": bool(b3 is not None and r_wc >= float(b3.reindex(mm["var"]).r_wc.mean())),
            "C1b_rwc_gt_0.21": bool(r_wc > 0.21),
            "C2_CA_ge_0.8": bool(mm.CA.mean() >= 0.8),
            "C3_level_le_B4": bool(b4 is not None and mm.level_err_pp.mean() <= float(b4.reindex(mm["var"]).level_err_pp.mean())),
            "C4_HR_0.8_1.2": bool(0.8 <= mm.hr_dist.mean() <= 1.2),
            "values": {"r_wc": r_wc, "CA": float(mm.CA.mean()), "level_err_pp": float(mm.level_err_pp.mean()),
                       "hr_dist": float(mm.hr_dist.mean())},
        }
    json.dump(res, open(out / "success_criteria.json", "w"), indent=1)
    return res


def run(cfg: Config, mock: bool = False, models: list[str] | None = None) -> dict:
    root = Path(cfg.out_dir) / ("mock" if mock else "main")
    root.mkdir(parents=True, exist_ok=True)
    w15, w14 = load_data(cfg, mock)
    specs = [m for m in cfg.models if (models is None or m.name in models)]
    if mock:
        specs = [ModelSpec("mock-llm", "mock", "mock", "G0", "n/a")]
    scored = [run_model(cfg, s, w15, w14, root) for s in specs]
    twins = pd.read_csv(root / specs[0].name / "twins.csv", converters={"answered_domains": eval})
    items = [OVERALL_FAV, OVERALL_REC] + TARGETS_POP + [d for d in w15.columns if d[1:3] == "Q4"]
    S = pd.concat(scored + [baseline_scores(twins, w15, w14, items)], ignore_index=True)
    M = evaluate(S, w15, cfg, root)
    return {"metrics": M, "criteria": success_criteria(M, root), "root": root}
