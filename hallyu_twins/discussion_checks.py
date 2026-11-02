"""Checks added in the second review round (no model calls; read-only on the final runs).

  python -m hallyu_twins.discussion_checks --runs outputs/final_* --est outputs/analysis_final/estimates.csv \
      --dest outputs/analysis_final --embedding openai

Writes (all exploratory):
  rb_language.csv     favorability error on all 30 countries by language group, raw and adjusted for the human level
  rb_prior.csv        what the twins' 30-country favorability tracks (printed profile vs the model's own recall) and
                      leave-one-out accuracy of linear predictors built from each information source
  rb_calibrated.csv   the same leave-one-out linear calibration (CAL-LOCO) applied to SSR, DLR and the persona-free
                      estimate, with paired sign-flip tests (all 30 countries for favorability; listed countries per item)
  rb_ssr_variants.csv SSR re-scored from the same answers with single anchor sets, leave-one-set-out and nearest-anchor
  rb_ssr_range.csv    distribution of individual SSR top-2-box scores (how close real answers get to 0 and 100%)
  rb_judge.csv        (if outputs/judge exists) the same free-text answers classified by an LLM judge
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from . import table_eval as TE
from .codebook import CONTINENT, COUNTRIES, ITEMS, OVERALL_FAV, OVERALL_REC, TARGETS_POP_15
from .elicit import SSRScorer
from .robustness import _b2, _model, _scored, _signflip_p, knowledge_share
from .tables import TABLE_DIR

EN_OFFICIAL = ["United States", "United Kingdom", "Canada", "Australia", "India", "Philippines", "Singapore", "South Africa"]
CONT_EUROPE = [c for c in COUNTRIES if CONTINENT[c] == "Europe" and c != "United Kingdom"]


FILE_ORDER = pd.read_csv(TABLE_DIR / "targets_xq5_all30.csv")["country"].tolist()


def _a30() -> pd.Series:
    return pd.read_csv(TABLE_DIR / "targets_xq5_all30.csv").set_index("country")["value"].astype(float)[COUNTRIES]


def _sources(E, B2, probes: Path) -> dict:
    """Country-level favorability (all 30) per model: SSR, DLR, B2 and the model's own recall of the previous edition."""
    out = {}
    for mdl in sorted(E.model.unique()):
        f = E[(E.model == mdl) & (E["var"] == OVERALL_FAV)]
        d = {"Twins SSR": f[f.cond == "Twins SSR"].set_index("country")["est"][COUNTRIES],
             "Twins DLR": f[f.cond == "Twins DLR"].set_index("country")["est"][COUNTRIES],
             "B2 persona-free LLM": B2[(B2.model == mdl) & (B2["var"] == OVERALL_FAV)].set_index("country")["est"][COUNTRIES]}
        rc = probes / mdl / "recall.csv"
        if rc.exists():
            d["Recall of previous edition"] = pd.read_csv(rc).groupby("country")["favorability"].mean()[COUNTRIES]
        out[mdl] = d
    return out


def language(src: dict, boot: int = 2000, seed: int = 23) -> pd.DataFrame:
    """Mean signed error by group, and the group coefficient in error ~ human level + group (bootstrap CI)."""
    A = _a30()
    rows = []
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, 30, size=(boot, 30))
    for mdl, d in src.items():
        for meth in ("Twins SSR", "Twins DLR", "B2 persona-free LLM"):
            e = (d[meth] - A).to_numpy()
            h = A.to_numpy()
            for gname, members in (("English official language", EN_OFFICIAL), ("Continental Europe", CONT_EUROPE)):
                g = np.array([c in members for c in COUNTRIES], dtype=float)
                X = np.column_stack([np.ones(30), h, g])
                coef = np.linalg.lstsq(X, e, rcond=None)[0]
                bs = []
                for ii in idx:
                    if g[ii].min() == g[ii].max():
                        continue
                    bs.append(np.linalg.lstsq(X[ii], e[ii], rcond=None)[0][2])
                lo, hi = np.percentile(bs, [2.5, 97.5])
                rows.append({"model": mdl, "method": meth, "group": gname, "n_group": int(g.sum()), "n_other": int(30 - g.sum()),
                             "bias_group": float(e[g == 1].mean()), "bias_other": float(e[g == 0].mean()),
                             "raw_diff": float(e[g == 1].mean() - e[g == 0].mean()),
                             "adj_diff": float(coef[2]), "adj_lo": float(lo), "adj_hi": float(hi), "slope_human_level": float(coef[1])})
    return pd.DataFrame(rows)


def _loo_mae(cols: list[np.ndarray], y: np.ndarray) -> float:
    err = []
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        X = np.column_stack([np.ones(len(y))] + cols)
        b = np.linalg.lstsq(X[m], y[m], rcond=None)[0]
        err.append(abs(np.clip(X[i] @ b, 0, 100) - y[i]))
    return float(np.mean(err))


def prior(src: dict) -> pd.DataFrame:
    A = _a30()
    K = pd.Series({c: 100 * knowledge_share(c) for c in COUNTRIES})
    rows = []
    for mdl, d in src.items():
        ssr, rc, b2 = d["Twins SSR"], d.get("Recall of previous edition"), d["B2 persona-free LLM"]
        r = {"model": mdl}
        for name, s in (("human", A), ("knowledge share", K), ("recall", rc), ("B2", b2)):
            r[f"rho_SSR_{name}"] = float(stats.spearmanr(ssr, s)[0])
        r["rho_recall_human"] = float(stats.spearmanr(rc, A)[0])
        r["rho_knowledge_human"] = float(stats.spearmanr(K, A)[0])
        z = lambda x: (x - x.mean()) / x.std()
        Y, Xk, Xr = z(ssr.to_numpy()), z(K.to_numpy()), z(rc.to_numpy())
        X = np.column_stack([np.ones(30), Xk, Xr])
        b = np.linalg.lstsq(X, Y, rcond=None)[0]
        r["beta_knowledge"], r["beta_recall"] = float(b[1]), float(b[2])
        r["R2_knowledge_recall"] = float(1 - ((Y - X @ b) ** 2).sum() / ((Y - Y.mean()) ** 2).sum())
        r["R2_knowledge"] = float(np.corrcoef(Y, Xk)[0, 1] ** 2)
        r["R2_recall"] = float(np.corrcoef(Y, Xr)[0, 1] ** 2)
        y, k, rr, s = A.to_numpy(), K.to_numpy(), rc.to_numpy(), ssr.to_numpy()
        for lab, cols in (("knowledge", [k]), ("recall", [rr]), ("B2", [b2.to_numpy()]), ("SSR", [s]),
                          ("knowledge+recall", [k, rr]), ("knowledge+SSR", [k, s]), ("recall+SSR", [rr, s]),
                          ("knowledge+recall+SSR", [k, rr, s])):
            r[f"LOO_MAE_{lab}"] = _loo_mae(cols, y)
        rows.append(r)
    return pd.DataFrame(rows)


def calibrated(src: dict, E: pd.DataFrame, B2: pd.DataFrame) -> pd.DataFrame:
    """CAL-LOCO (TE.cal_loco, as in the main analysis) applied to every elicitation, with paired sign-flip tests."""
    rows = []
    A = _a30()
    K = pd.Series({c: knowledge_share(c) for c in COUNTRIES})
    prof = TE.cal_loco(K, A)                      # = B-PROFILE (leave-one-out linear regression on the knowledge share)
    for mdl, d in src.items():
        cal = {m: TE.cal_loco(d[m], A)[COUNTRIES] for m in ("Twins SSR", "Twins DLR", "B2 persona-free LLM")}
        cal["B-PROFILE (no LLM)"] = prof[COUNTRIES]
        for m, s in cal.items():
            mm = TE.metrics(s, A)
            rows.append({"scope": "XQ5 all 30", "model": mdl, "method": m + ("" if m.startswith("B-PROFILE") else " + CAL-LOCO"),
                         "n": mm["n"], "MAE_pp": mm["MAE_pp"], "bias_pp": mm["bias_pp"], "contrast": "", "diff_pp": np.nan, "p_signflip": np.nan})
        for other in ("Twins DLR", "B2 persona-free LLM", "B-PROFILE (no LLM)"):
            dd = (cal["Twins SSR"] - A).abs() - (cal[other] - A).abs()
            # same country order (and Monte Carlo draws) as robustness.xq5_all30_paired, so a contrast reported in both
            # tables has one p-value
            p, test = _signflip_p(dd.reindex(FILE_ORDER).to_numpy())
            rows.append({"scope": "XQ5 all 30", "model": mdl, "method": "Twins SSR + CAL-LOCO",
                         "contrast": "vs " + other + ("" if other.startswith("B-PROFILE") else " + CAL-LOCO"),
                         "n": 30, "MAE_pp": np.nan, "bias_pp": np.nan, "diff_pp": float(dd.mean()), "p_signflip": p})
    # listed countries, each item: the same calibration for DLR and B2 (SSR reproduces metrics.csv)
    tr = TE.truth()
    for var in (OVERALL_FAV, OVERALL_REC, "POPMEAN"):
        h = tr[tr["var"] == var].set_index("country")["human"]
        for mdl in sorted(E.model.unique()):
            cand = {m: E[(E.model == mdl) & (E.cond == m) & (E["var"] == var)].set_index("country")["est"] for m in ("Twins SSR", "Twins DLR")}
            cand["B2 persona-free LLM"] = B2[(B2.model == mdl) & (B2["var"] == var)].set_index("country")["est"]
            cal = {m: TE.cal_loco(s, h)[h.index] for m, s in cand.items()}
            for m, s in cal.items():
                mm = TE.metrics(s, h)
                rows.append({"scope": f"{var} listed", "model": mdl, "method": m + " + CAL-LOCO", "n": mm["n"], "MAE_pp": mm["MAE_pp"],
                             "bias_pp": mm["bias_pp"], "contrast": "", "diff_pp": np.nan, "p_signflip": np.nan})
            for other in ("Twins DLR", "B2 persona-free LLM"):
                dd = (cal["Twins SSR"] - h).abs() - (cal[other] - h).abs()
                p, test = _signflip_p(dd.to_numpy())
                rows.append({"scope": f"{var} listed", "model": mdl, "method": "Twins SSR + CAL-LOCO", "contrast": f"vs {other} + CAL-LOCO",
                             "n": len(h), "MAE_pp": np.nan, "bias_pp": np.nan, "diff_pp": float(dd.mean()), "p_signflip": p})
    return pd.DataFrame(rows)


def _set_probs(scorer: SSRScorer, var: str, texts: list[str]) -> list[np.ndarray]:
    """Per-anchor-set (n, 5) probabilities with the main (Maier) mapping, and per-set similarity matrices."""
    it = ITEMS[var]
    R = scorer.embedder.embed([t if t else "(no answer)" for t in texts])
    out = []
    for A in scorer.anchors(it):
        S = R @ A.T
        W = np.clip(S - S.min(axis=1, keepdims=True), 0, None) + 1e-12
        out.append((W / W.sum(axis=1, keepdims=True), S))
    return out


def ssr_variants(runs: list[Path], scorer: SSRScorer) -> tuple[pd.DataFrame, pd.DataFrame]:
    tr = TE.truth()
    A30 = _a30()
    rows, rng_rows = [], []
    for run in runs:
        mdl = _model(run)
        s = _scored(run)
        s = s[(s.cond == "P3a") & (s["round"] == 1) & (s["mode"] == "ssr") & s["p1"].notna()]
        est = {}                                  # variant -> var -> country series
        for var, g in s.groupby("var"):
            sets = _set_probs(scorer, var, g["text"].fillna("").tolist())
            main = np.mean([P for P, _ in sets], axis=0)
            assert np.allclose(main, g[["p1", "p2", "p3", "p4", "p5"]].to_numpy(), atol=1e-9), f"SSR rebuild mismatch {mdl} {var}"
            variants = {"all sets (main)": main[:, 3] + main[:, 4]}
            k = len(sets)
            for j in range(k):
                variants[f"anchor set {j + 1} only"] = sets[j][0][:, 3] + sets[j][0][:, 4]
                if k > 2:
                    P = np.mean([sets[i][0] for i in range(k) if i != j], axis=0)
                    variants[f"without anchor set {j + 1}"] = P[:, 3] + P[:, 4]
            variants["nearest anchor (hard)"] = np.mean([(S.argmax(axis=1) >= 3).astype(float) for _, S in sets], axis=0)
            for vn, t2 in variants.items():
                est.setdefault(vn, {})[var] = pd.Series(100 * t2, index=g["country"].to_numpy()).groupby(level=0).mean()
            t2 = variants["all sets (main)"]
            grp = "Popularity (13 domains)" if var in TARGETS_POP_15 else ITEMS[var].var
            rng_rows.append({"model": mdl, "var": var, "group": grp, "n": len(t2), "min": float(t2.min()), "p01": float(np.percentile(t2, 1)),
                             "p99": float(np.percentile(t2, 99)), "max": float(t2.max()), "share_ge_0.9": float((t2 >= 0.9).mean()),
                             "share_le_0.1": float((t2 <= 0.1).mean())})
        for vn, d in est.items():
            pop = pd.concat([d[v] for v in TARGETS_POP_15 if v in d], axis=1).mean(axis=1) if all(v in d for v in TARGETS_POP_15) else None
            for var in (OVERALL_FAV, OVERALL_REC, "POPMEAN"):
                e = pop if var == "POPMEAN" else d.get(var)
                if e is None:
                    continue
                h = tr[tr["var"] == var].set_index("country")
                m = TE.metrics(e, h["human"])
                rows.append({"model": mdl, "variant": vn, "var": var, "scope": "listed", **m})
                if var == OVERALL_FAV:
                    m = TE.metrics(e, A30)
                    rows.append({"model": mdl, "variant": vn, "var": var, "scope": "all 30", **m})
    R = pd.DataFrame(rng_rows)
    agg = R.groupby(["model", "group"]).agg(n=("n", "sum"), min=("min", "min"), p01=("p01", "min"), p99=("p99", "max"),
                                             max=("max", "max")).reset_index()
    return pd.DataFrame(rows), agg


def anchor_similarity(scorer: SSRScorer) -> pd.DataFrame:
    """Cosine similarity between the five anchor statements of each set (how close the scale points lie)."""
    rows = []
    for var in [OVERALL_FAV, OVERALL_REC] + list(TARGETS_POP_15):
        for j, A in enumerate(scorer.anchors(ITEMS[var])):
            S = A @ A.T
            iu = np.triu_indices(5, 1)
            rows.append({"var": var, "set": j + 1, "mean_pairwise": float(S[iu].mean()), "min_pairwise": float(S[iu].min()),
                         "max_pairwise": float(S[iu].max()), "sim_1_5": float(S[0, 4]), "sim_4_5": float(S[3, 4])})
    return pd.DataFrame(rows)


def judge_eval(judge_root: Path, runs: list[Path]) -> pd.DataFrame | None:
    """The same SSR answers classified by an LLM judge (scripts/judge_rescore.py): country top-2-box under the judge,
    and the share of answers in the top box (option 5), whose country ordering carries the intensity of the answer."""
    if not judge_root.exists():
        return None
    tr = TE.truth()
    A30 = _a30()
    rows = []
    for f in sorted(judge_root.glob("*/judge_scores.csv")):
        J = pd.read_csv(f)
        judge = f.parent.name
        for (mdl, var), g0 in J.groupby(["model", "var"]):
            g = g0[g0["judge_option"].between(1, 5)]
            t2b = (g.assign(t=(g["judge_option"] >= 4) * 100.0).groupby("country")["t"].mean())
            top = (g.assign(t=(g["judge_option"] == 5) * 100.0).groupby("country")["t"].mean())
            ssr = g.groupby("country")["ssr_t2b"].mean() * 100
            h = tr[tr["var"] == var].set_index("country")["human"]
            for scope, hh in (("listed", h),) + ((("all 30", A30),) if var == OVERALL_FAV else ()):
                m = TE.metrics(t2b, hh)
                ix = hh.index.intersection(top.index)
                rows.append({"judge": judge, "model": mdl, "var": var, "scope": scope, "n_answers": len(g0), "n_parsed": len(g),
                             "MAE_pp": m.get("MAE_pp"), "bias_pp": m.get("bias_pp"),
                             "t2b_all_answers": float((g["judge_option"] >= 4).mean() * 100),
                             "mid_all_answers": float((g["judge_option"] == 3).mean() * 100),
                             "low_all_answers": float((g["judge_option"] <= 2).mean() * 100),
                             "topbox_min": float(top[ix].min()), "topbox_max": float(top[ix].max()),
                             "rho_topbox_human": float(stats.spearmanr(top[ix], hh[ix])[0]),
                             "rho_ssr_human": float(stats.spearmanr(ssr[ix], hh[ix])[0]),
                             "rho_topbox_ssr": float(stats.spearmanr(top[ix], ssr[ix])[0])})
    out = pd.DataFrame(rows)
    # agreement between judges on the answers both classified
    fs = sorted(judge_root.glob("*/judge_scores.csv"))
    if len(fs) >= 2:
        a, b = (pd.read_csv(x) for x in fs[:2])
        M = a[a.judge_option.between(1, 5)].merge(b[b.judge_option.between(1, 5)], on=["model", "resp_id", "var"])
        out = pd.concat([out, pd.DataFrame([{"judge": f"agreement {fs[0].parent.name} vs {fs[1].parent.name}", "n_parsed": len(M),
                                              "exact_agreement": float((M.judge_option_x == M.judge_option_y).mean()),
                                              "t2b_agreement": float(((M.judge_option_x >= 4) == (M.judge_option_y >= 4)).mean())}])],
                        ignore_index=True)
    return out


def item_coherence_b2(B2: pd.DataFrame) -> pd.DataFrame:
    """Cross-item Spearman correlation of the persona-free estimate (B2), on the countries where both human values are
    printed (the same countries as the "same countries as human" rows of extra_analyses.item_coherence)."""
    tr = TE.truth().pivot(index="country", columns="var", values="human")
    rows = []
    for mdl, g in B2.groupby("model"):
        W = g.groupby(["country", "var"])["est"].mean().unstack()
        dom = [c for c in W.columns if c.startswith("XQ1_")]
        assert len(dom) == 13, dom
        W["POPMEAN"] = W[dom].mean(axis=1)
        for x, y in ((OVERALL_FAV, OVERALL_REC), (OVERALL_FAV, "POPMEAN"), (OVERALL_REC, "POPMEAN")):
            sub = tr[[x, y]].dropna().index.intersection(W.index)
            r, p = stats.spearmanr(W.loc[sub, x], W.loc[sub, y])
            rows.append({"pair": f"{x}~{y}", "source": "B2 persona-free LLM (same countries as human)", "model": mdl,
                         "n": len(sub), "spearman": r, "p": p})
    return pd.DataFrame(rows)


def main(runs, est_csv, dest, embedder):
    E = pd.read_csv(est_csv)
    B2 = pd.concat([_b2(r).assign(model=_model(r)) for r in runs], ignore_index=True)
    probes = Path(runs[0]).parent / "probes"
    src = _sources(E, B2, probes)
    out = {"rb_language": language(src), "rb_prior": prior(src), "rb_calibrated": calibrated(src, E, B2),
           "rb_item_coherence_b2": item_coherence_b2(B2)}
    scorer = SSRScorer(embedder)
    out["rb_anchor_similarity"] = anchor_similarity(scorer)
    v, rg = ssr_variants(runs, scorer)
    out["rb_ssr_variants"], out["rb_ssr_range"] = v, rg
    j = judge_eval(Path(runs[0]).parent / "judge", runs)
    if j is not None:
        out["rb_judge"] = j
    for k, df in out.items():
        df.to_csv(dest / f"{k}.csv", index=False)
        print("wrote", k, len(df))


if __name__ == "__main__":
    from .embed import default_cache, make_embedder
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--est", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--embedding", default="openai")
    a = ap.parse_args()
    main([Path(r) for r in a.runs], Path(a.est), Path(a.dest), make_embedder({"provider": a.embedding}, default_cache("outputs/cache")))
