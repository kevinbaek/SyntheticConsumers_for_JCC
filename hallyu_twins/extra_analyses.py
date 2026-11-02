"""Additional correlation and structure analyses for the manuscript (no new model calls).

  python -m hallyu_twins.extra_analyses --runs outputs/final_* --est outputs/analysis_final/estimates.csv --dest outputs/analysis_final

Outputs (CSV):
  inter_model.csv        Spearman agreement between models' country estimates (all 30 countries, no human data)
  item_coherence.csv     country-level correlation between items (XQ5 vs XQ6, XQ5 vs POPMEAN), human vs synthetic
  continent_error.csv    mean signed error by continent (where does the positivity bias sit?)
  persona_gradients.csv  synthetic answer by persona attribute (Korea awareness, age band, sex, nationality)
  mode_agreement.csv     within-twin agreement of DLR and SSR (same twin, same item)
  domain_profile.csv     13-domain popularity profile, pooled synthetic vs human, per model and mode
  network_by_item.csv    network movement by item type (social perception XQ1 vs own preference XQ5/XQ6)
  variance_decomposition.csv  twin-level R^2 of country dummies vs persona attributes (country-label test)
  error_structure.csv    error vs human level (compression), country-level DLR~SSR agreement
  popmean_sensitivity.csv  POPMEAN as the mean of 13 domains (main) vs 11 domains (earlier waves' set)
  monte_carlo_error.csv  standard error of a country estimate from sampling 100 twins (twin-level SD / sqrt n)
  country_estimates_wide.csv  every country x item x method estimate next to the human value (figure data)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from . import pilot
from . import table_eval as TE
from .codebook import CONTINENT, COUNTRIES, OVERALL_FAV, OVERALL_REC, TARGETS_POP_15, WAVE15_N
from .elicit import SSRScorer
from .tables import load_targets


_SCORED: dict = {}


def _score(run: Path, scorer: SSRScorer) -> pd.DataFrame:
    """pilot.score once per run per process (it re-reads every response and embedding)."""
    k = str(run)
    if k not in _SCORED:
        _SCORED[k] = pilot.score(run, scorer)
    return _SCORED[k].copy()


def _rho(a, b):
    ok = ~(pd.isna(a) | pd.isna(b))
    if ok.sum() < 4:
        return np.nan, np.nan, int(ok.sum())
    r, p = stats.spearmanr(np.asarray(a)[ok], np.asarray(b)[ok])
    return float(r), float(p), int(ok.sum())


def inter_model(E: pd.DataFrame) -> pd.DataFrame:
    rows = []
    models = sorted(E.model.unique())
    for var in TE.KEY:
        for cond in ("Twins SSR", "Twins DLR"):
            W = E[(E.cond == cond) & (E["var"] == var)].pivot(index="country", columns="model", values="est")
            for i, a in enumerate(models):
                for b in models[i + 1:]:
                    if a in W and b in W:
                        r, p, n = _rho(W[a], W[b])
                        rows.append({"var": var, "method": cond, "model_a": a, "model_b": b, "n_countries": n,
                                     "spearman": r, "p": p})
    return pd.DataFrame(rows)


def item_coherence(E: pd.DataFrame) -> pd.DataFrame:
    tr = TE.truth().pivot(index="country", columns="var", values="human")
    rows = []
    for x, y in ((OVERALL_FAV, OVERALL_REC), (OVERALL_FAV, "POPMEAN"), (OVERALL_REC, "POPMEAN")):
        r, p, n = _rho(tr[x], tr[y]) if x in tr and y in tr else (np.nan, np.nan, 0)
        rows.append({"pair": f"{x}~{y}", "source": "human (listed countries)", "model": "-", "n": n, "spearman": r, "p": p})
        for (mdl, cond), g in E[E.cond.isin(["Twins SSR", "Twins DLR"])].groupby(["model", "cond"]):
            W = g.pivot(index="country", columns="var", values="est")
            r, p, n = _rho(W[x], W[y])
            rows.append({"pair": f"{x}~{y}", "source": f"{cond} (30 countries)", "model": mdl, "n": n, "spearman": r, "p": p})
            ix = tr.index.intersection(W.index)
            sub = tr.loc[ix, [x, y]].dropna().index
            r, p, n = _rho(W.loc[sub, x], W.loc[sub, y])
            rows.append({"pair": f"{x}~{y}", "source": f"{cond} (same countries as human)", "model": mdl, "n": n,
                         "spearman": r, "p": p})
    return pd.DataFrame(rows)


def continent_error(E: pd.DataFrame) -> pd.DataFrame:
    tr = TE.truth()
    m = E.merge(tr, on=["country", "var"])
    m["continent"] = m.country.map(CONTINENT)
    m["err"] = m.est - m.human
    g = m.groupby(["model", "cond", "var", "continent"])["err"].agg(["mean", "count"]).reset_index()
    return g.rename(columns={"mean": "mean_error_pp", "count": "n_countries"})


def persona_gradients(run: Path, scorer: SSRScorer, model: str) -> pd.DataFrame:
    s = _score(run, scorer)
    tw = pd.read_csv(run / "twins.csv").set_index("resp_id")
    s = s[(s.cond == "P3a") & s["var"].isin([OVERALL_FAV, OVERALL_REC]) & s["text"].notna()].copy()
    P = s[[f"p{k}" for k in range(1, 6)]].to_numpy()
    s["score"] = np.where(s["mode"] == "ssr", P @ np.arange(1, 6), s["dlr"])
    s["t2b"] = np.where(s["mode"] == "ssr", P[:, 3] + P[:, 4], (s["dlr"] >= 4).astype(float))
    lab = {"korea_awareness": {1: "knows Korea very well", 2: "somewhat", 3: "little"},
           "age_band": {1: "15-19", 2: "20-29", 3: "30-39", 4: "40-49", 5: "50-59"},
           "sex": {1: "male", 2: "female"}, "nationality": {1: "Korean-descended", 2: "local", 3: "third-country"}}
    rows = []
    for attr, names in lab.items():
        s[attr] = tw.loc[s.resp_id, attr].to_numpy()
        for (var, mode), g in s.groupby(["var", "mode"]):
            for lvl, gg in g.groupby(attr):
                rows.append({"model": model, "var": var, "mode": mode, "attribute": attr, "level": names.get(int(lvl), lvl),
                             "n": len(gg), "mean_score": float(gg.score.mean()), "t2b_pct": 100 * float(gg.t2b.mean())})
            if attr in ("korea_awareness", "age_band"):
                r, p, n = _rho(g[attr], g.score)
                rows.append({"model": model, "var": var, "mode": mode, "attribute": attr, "level": "spearman(code, score)",
                             "n": n, "mean_score": r, "t2b_pct": p})
    return pd.DataFrame(rows)


def mode_agreement(run: Path, scorer: SSRScorer, model: str) -> pd.DataFrame:
    s = _score(run, scorer)
    s = s[(s.cond == "P3a") & s["text"].notna()].copy()
    s["e"] = np.where(s["mode"] == "ssr", s[[f"p{k}" for k in range(1, 6)]].to_numpy() @ np.arange(1, 6), s["dlr"])
    W = s.pivot_table(index=["resp_id", "var"], columns="mode", values="e").dropna()
    rows = []
    for var, g in W.groupby(level="var"):
        r, p, n = _rho(g["dlr"], g["ssr"])
        rows.append({"model": model, "var": var, "n_twins": n, "spearman_dlr_ssr": r, "p": p,
                     "dlr_sd": float(g["dlr"].std()), "ssr_sd": float(g["ssr"].std())})
    return pd.DataFrame(rows)


def domain_profile(E13: pd.DataFrame) -> pd.DataFrame:
    t = load_targets()
    h = t[(t.country == "ALL30") & (t.wave == 15) & (t["var"].isin(TARGETS_POP_15))].set_index("var")["value"]
    w = pd.Series(WAVE15_N)
    rows = []
    for (mdl, cond), g in E13.groupby(["model", "cond"]):
        W = g.pivot(index="country", columns="var", values="est").reindex(COUNTRIES)
        for v in TARGETS_POP_15:
            if v in W:
                col = W[v].dropna()
                rows.append({"model": mdl, "method": cond, "var": v, "synthetic": float(np.average(col, weights=w[col.index])),
                             "human": float(h.get(v, np.nan))})
    return pd.DataFrame(rows)


def network_by_item(run: Path, scorer: SSRScorer, model: str) -> pd.DataFrame:
    s = _score(run, scorer)
    s = s[(s["mode"] == "ssr") & s["text"].notna()].copy()
    s["e"] = s[[f"p{k}" for k in range(1, 6)]].to_numpy() @ np.arange(1, 6)
    base = s[s.cond == "P3a"].set_index(["resp_id", "var"])["e"]
    rows = []
    for cond in ("P3a+N1self", "P3a+N2random", "P3a+N3homophily"):
        x = s[s.cond == cond].set_index(["resp_id", "var"])["e"]
        ix = base.index.intersection(x.index)
        d = (x[ix] - base[ix]).reset_index()
        d.columns = ["resp_id", "var", "d"]
        d["item_type"] = np.where(d["var"].str.startswith("XQ1_"), "social perception (XQ1)", "own preference (XQ5, XQ6)")
        for it, g in d.groupby("item_type"):
            rows.append({"model": model, "cond": cond, "item_type": it, "pairs": len(g),
                         "share_moved_gt_0.25": float((g.d.abs() > 0.25).mean()), "mean_abs_shift": float(g.d.abs().mean()),
                         "mean_shift": float(g.d.mean())})
    return pd.DataFrame(rows)


ATTRS = ["age_band", "sex", "education", "occupation", "marital", "nationality", "korea_awareness"]


def _r2(y: np.ndarray, X: np.ndarray) -> float:
    """Adjusted R^2 of an OLS fit with intercept (dummies may be collinear; lstsq handles rank)."""
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    if y.var() == 0:
        return np.nan
    n, k = len(y), np.linalg.matrix_rank(X) - 1
    return float(1 - (res.var() / y.var()) * (n - 1) / (n - k - 1))


def variance_decomposition(run: Path, scorer: SSRScorer, model: str) -> pd.DataFrame:
    """Twin-level answers (P3a) regressed on country dummies, on persona attributes (dummies), and on both:
    how much of the synthetic variation is a country label and how much the persona (Wang 2026's critique)."""
    s = _score(run, scorer)
    tw = pd.read_csv(run / "twins.csv").set_index("resp_id")
    s = s[(s.cond == "P3a") & s["text"].notna()].copy()
    P = s[[f"p{k}" for k in range(1, 6)]].to_numpy()
    s["e"] = np.where(s["mode"] == "ssr", P @ np.arange(1, 6), s["dlr"])
    rows = []
    for (var, mode), g in s.dropna(subset=["e"]).groupby(["var", "mode"]):
        t = tw.loc[g.resp_id]
        C = pd.get_dummies(t["country"], drop_first=True).to_numpy(float)
        A = pd.get_dummies(t[ATTRS].astype(str), drop_first=True).to_numpy(float)
        y = g["e"].to_numpy(float)
        rc, ra, rb = _r2(y, C), _r2(y, A), _r2(y, np.column_stack([C, A]))
        rows.append({"model": model, "var": var, "mode": mode, "n_twins": len(g), "r2_country": rc, "r2_persona": ra,
                     "r2_both": rb, "persona_increment": rb - rc, "country_increment": rb - ra})
    return pd.DataFrame(rows)


def monte_carlo_error(run: Path, scorer: SSRScorer, model: str) -> pd.DataFrame:
    """Sampling error from drawing 100 twins per country: standard error of a country's T2B estimate
    (SD of twin-level T2B / sqrt(n)), summarised over countries. POPMEAN uses the twin's mean over the 13 items."""
    s = _score(run, scorer)
    tw = pd.read_csv(run / "twins.csv").set_index("resp_id")
    s = s[(s.cond == "P3a") & s["text"].notna()].copy()
    s["t2b"] = np.where(s["mode"] == "ssr", s["p4"] + s["p5"], (s["dlr"] >= 4).astype(float).where(s["dlr"].notna()))
    s["country"] = tw.loc[s.resp_id, "country"].to_numpy()
    pop = (s[s["var"].str.startswith("XQ1_")].groupby(["resp_id", "country", "mode"])["t2b"].mean().reset_index()
           .assign(var="POPMEAN"))
    s = pd.concat([s[s["var"].isin([OVERALL_FAV, OVERALL_REC])][["resp_id", "country", "mode", "var", "t2b"]], pop])
    se = (s.dropna(subset=["t2b"]).groupby(["mode", "var", "country"])["t2b"]
          .agg(lambda x: 100 * x.std(ddof=1) / np.sqrt(len(x))).rename("se_pp").reset_index())
    g = se.groupby(["mode", "var"])["se_pp"].agg(["median", "min", "max"]).reset_index()
    return g.assign(model=model).rename(columns={"median": "se_median_pp", "min": "se_min_pp", "max": "se_max_pp"})


def error_structure(E: pd.DataFrame) -> pd.DataFrame:
    """Does the error depend on the human level (compression: high countries under-, low countries over-estimated)?
    Spearman of signed error with the human value, plus the country-level DLR~SSR agreement."""
    tr = TE.truth()
    m = E[E.cond.isin(["Twins SSR", "Twins DLR"])].merge(tr, on=["country", "var"])
    rows = []
    for (mdl, cond, var), g in m.groupby(["model", "cond", "var"]):
        r, p, n = _rho(g.est - g.human, g.human)
        rows.append({"model": mdl, "method": cond, "var": var, "analysis": "error ~ human level", "n": n, "spearman": r, "p": p})
    for (mdl, var), g in E[E.cond.isin(["Twins SSR", "Twins DLR"])].groupby(["model", "var"]):
        W = g.pivot(index="country", columns="cond", values="est")
        if {"Twins SSR", "Twins DLR"} <= set(W.columns):
            r, p, n = _rho(W["Twins SSR"], W["Twins DLR"])
            rows.append({"model": mdl, "method": "SSR vs DLR", "var": var, "analysis": "country estimates, 30 countries",
                         "n": n, "spearman": r, "p": p})
    return pd.DataFrame(rows)


def popmean_sensitivity(E13: pd.DataFrame) -> pd.DataFrame:
    """The report does not say how many domains its country popularity average uses. Main analysis: all 13
    domains of 2025. Sensitivity: the 11 domains common to earlier waves (without character XQ1_12 and
    performance XQ1_13). Same metrics against the printed POPMEAN of the listed countries."""
    tr = TE.truth()
    h = tr[tr["var"] == "POPMEAN"].set_index("country")["human"]
    rows = []
    for (mdl, cond), g in E13.groupby(["model", "cond"]):
        W = g.pivot(index="country", columns="var", values="est")
        for label, cols in (("13 domains", [c for c in TARGETS_POP_15 if c in W]),
                            ("11 domains", [c for c in TARGETS_POP_15 if c in W and c not in ("XQ1_12", "XQ1_13")])):
            est = W[cols].mean(axis=1)
            ix = h.index.intersection(est.dropna().index)
            err = est[ix] - h[ix]
            r, p, n = _rho(est[ix], h[ix])
            rows.append({"model": mdl, "method": cond, "definition": label, "n": n, "MAE_pp": float(err.abs().mean()),
                         "bias_pp": float(err.mean()), "spearman": r})
    return pd.DataFrame(rows)


def country_wide(E: pd.DataFrame) -> pd.DataFrame:
    tr = TE.truth()
    return E.merge(tr, on=["country", "var"], how="left")


def main(runs: list[Path], est_csv: Path, dest: Path, embedder) -> None:
    from .analysis_table import estimates
    scorer = SSRScorer(embedder)
    E = pd.read_csv(est_csv)
    out = {"inter_model": inter_model(E), "item_coherence": item_coherence(E), "continent_error": continent_error(E),
           "country_estimates_wide": country_wide(E)}
    out["error_structure"] = error_structure(E)
    pg, ma, nb, e13, vd, mce = [], [], [], [], [], []
    for run in runs:
        model = json.load(open(run / "run_meta.json"))["model"]
        pg.append(persona_gradients(run, scorer, model))
        ma.append(mode_agreement(run, scorer, model))
        nb.append(network_by_item(run, scorer, model))
        vd.append(variance_decomposition(run, scorer, model))
        mce.append(monte_carlo_error(run, scorer, model))
        _, T13, _ = estimates(run, scorer)
        e13.append(T13.assign(model=model))
    out["persona_gradients"] = pd.concat(pg, ignore_index=True)
    out["mode_agreement"] = pd.concat(ma, ignore_index=True)
    out["network_by_item"] = pd.concat(nb, ignore_index=True)
    out["variance_decomposition"] = pd.concat(vd, ignore_index=True)
    out["monte_carlo_error"] = pd.concat(mce, ignore_index=True)
    out["domain_profile"] = domain_profile(pd.concat(e13, ignore_index=True))
    out["popmean_sensitivity"] = popmean_sensitivity(pd.concat(e13, ignore_index=True))
    for k, df in out.items():
        df.to_csv(dest / f"{k}.csv", index=False)


if __name__ == "__main__":
    from .embed import default_cache, make_embedder
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--est", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--embedding", default="openai")
    a = ap.parse_args()
    main([Path(r) for r in a.runs], Path(a.est), Path(a.dest),
         make_embedder({"provider": a.embedding}, default_cache("outputs/cache")))
