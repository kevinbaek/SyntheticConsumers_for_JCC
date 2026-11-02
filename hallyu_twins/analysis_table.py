"""Final analysis of the table-only 30-country study for one or more models.

  python -m hallyu_twins.analysis_table --runs outputs/mc_claude-sonnet-5 outputs/mc_gpt-5.5 --embedding openai

Writes to outputs/analysis_table/: estimates_long.csv, metrics.csv, paired_tests.csv,
domains.csv, all30_distribution.csv, network.csv, summary.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import pilot
from . import table_eval as TE
from .codebook import OVERALL_FAV, OVERALL_REC, TARGETS_POP_15
from .elicit import SSRScorer

COND_LABEL = {("P3a", "dlr"): "Twins DLR", ("P3a", "ssr"): "Twins SSR",
              ("P3a+N1self", "ssr"): "Twins SSR + N1 self-reflection",
              ("P3a+N2random", "ssr"): "Twins SSR + N2 random network",
              ("P3a+N3homophily", "ssr"): "Twins SSR + N3 homophily network"}


SUB_REF = "Twins SSR (network subsample, round 1)"


def estimates(out: Path, scorer: SSRScorer) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (T: country x method x var T2B %, T13: per-domain, Tdist: 3-category distribution)."""
    tw = pd.read_csv(out / "twins.csv")
    s = pilot.score(out, scorer)
    s["country"] = s.resp_id.map(tw.set_index("resp_id")["country"])
    s = s[[(c, m) in COND_LABEL for c, m in zip(s.cond, s["mode"])]].copy()
    s["method"] = [COND_LABEL[(c, m)] for c, m in zip(s.cond, s["mode"])]
    # same-twin reference for the network contrasts: round-1 SSR rows of exactly the (twin, item) pairs
    # that have an answer in every network arm, and the network arms restricted to the same pairs
    net = [c for c in ("P3a+N1self", "P3a+N2random", "P3a+N3homophily") if (s.cond == c).any()]
    if net:
        r1 = s[(s.cond == "P3a") & (s["mode"] == "ssr") & s["text"].notna()]
        pairs = set(zip(r1.resp_id, r1["var"]))
        for c in net:
            g = s[(s.cond == c) & s["text"].notna()]
            pairs &= set(zip(g.resp_id, g["var"]))
        keep = [(c not in net) or ((r, v) in pairs) for c, r, v in zip(s.cond, s.resp_id, s["var"])]
        s = s[keep].copy()
        ref = r1[[(r, v) in pairs for r, v in zip(r1.resp_id, r1["var"])]].copy()
        ref["method"] = SUB_REF
        s = pd.concat([s, ref], ignore_index=True)
    P = s[[f"p{k}" for k in range(1, 6)]].to_numpy()
    dl = s["dlr"].to_numpy()
    isd = (s["mode"] == "dlr").to_numpy()
    onehot = np.zeros_like(P)
    ok = isd & ~np.isnan(dl)
    onehot[np.where(ok)[0], dl[ok].astype(int) - 1] = 1
    P = np.where(isd[:, None], onehot, P)
    valid = ~(isd & np.isnan(dl)) & ~np.isnan(P).any(axis=1)
    s = s[valid].copy()
    P = P[valid]
    s["b2b"], s["mid"], s["t2b"] = 100 * (P[:, 0] + P[:, 1]), 100 * P[:, 2], 100 * (P[:, 3] + P[:, 4])
    g = s.groupby(["country", "method", "var"])[["b2b", "mid", "t2b"]].mean().reset_index()
    T13 = g[g["var"].isin(TARGETS_POP_15)].rename(columns={"t2b": "est", "method": "cond"})[["country", "cond", "var", "est"]]
    pop = g[g["var"].isin(TARGETS_POP_15)].groupby(["country", "method"])["t2b"].mean().reset_index()
    pop["var"] = "POPMEAN"
    T = pd.concat([g[g["var"].isin([OVERALL_FAV, OVERALL_REC])][["country", "method", "var", "t2b"]], pop])
    T = T.rename(columns={"t2b": "est", "method": "cond"})
    Tdist = g[g["var"].isin([OVERALL_FAV, OVERALL_REC])].rename(columns={"method": "cond"})
    n_valid = s.groupby("method").size().to_dict()
    json.dump({"valid_item_rows": n_valid, "dropped_rows": int((~valid).sum())}, open(out / "parse_stats.json", "w"), indent=1)
    return T, T13, Tdist


def b2_estimates(out: Path) -> pd.DataFrame:
    f = out / "b2_direct.csv"
    if not f.exists():
        return pd.DataFrame(columns=["country", "var", "est"])
    b = pd.read_csv(f).rename(columns={"t2b": "est"})
    return b[b["var"].isin([OVERALL_FAV, OVERALL_REC, "POPMEAN"])]


def network(out: Path, scorer: SSRScorer) -> pd.DataFrame:
    s = pilot.score(out, scorer)
    s = s[(s["mode"] == "ssr") & s["text"].notna()].copy()   # pairs are matched by twin and item below
    s["e"] = s[[f"p{k}" for k in range(1, 6)]].to_numpy() @ np.arange(1, 6)
    country = pd.read_csv(out / "twins.csv").set_index("resp_id")["country"]
    base = s[s.cond == "P3a"].set_index(["resp_id", "var"])["e"]
    rows = []
    for cond in ("P3a+N1self", "P3a+N2random", "P3a+N3homophily"):
        x = s[s.cond == cond].set_index(["resp_id", "var"])["e"]
        ix = base.index.intersection(x.index)
        d = x[ix] - base[ix]
        rows.append({"cond": cond, "pairs": len(ix), "mean_shift": float(d.mean()),
                     "abs_shift": float(d.abs().mean()), "share_changed_gt_0.25": float((d.abs() > 0.25).mean()),
                     # spread between twins of the same country and item (not pooled across countries)
                     "within_country_sd_r1": float(_wc_sd(base[ix], country)),
                     "within_country_sd_r2": float(_wc_sd(x[ix], country))})
    return pd.DataFrame(rows)


def _wc_sd(series: pd.Series, country: pd.Series) -> float:
    df = series.rename("e").reset_index()
    df["country"] = df.resp_id.map(country)
    return df.groupby(["country", "var"])["e"].std().mean()


def run(runs: list[Path], embedder, dest: Path) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    scorer = SSRScorer(embedder)
    allM, allP, allD, allA, allN, allE = [], [], [], [], [], []
    tr = TE.truth()
    for out in runs:
        meta = json.load(open(out / "run_meta.json")) if (out / "run_meta.json").exists() else {"model": out.name}
        model = meta["model"]
        T, T13, Tdist = estimates(out, scorer)
        B2 = b2_estimates(out)
        T["model"] = model
        allE.append(T)
        M = TE.evaluate(T[["country", "cond", "var", "est"]], B2, model)
        allM.append(M)
        allD.append(TE.domain_eval(T13, model))
        if not B2.empty:
            b13 = pd.read_csv(out / "b2_direct.csv")
            b13 = b13[b13["var"].isin(TARGETS_POP_15)].rename(columns={"t2b": "est"}).assign(cond="B2 persona-free LLM")
            allD.append(TE.domain_eval(b13[["country", "cond", "var", "est"]], model))
        allA.append(TE.all30_distribution(Tdist, model))
        N = network(out, scorer)
        N["model"] = model
        allN.append(N)
        # paired tests on the key contrasts
        for var in TE.KEY:
            h = tr[tr["var"] == var].set_index("country")["human"]
            get = lambda c: T[(T.cond == c) & (T["var"] == var)].set_index("country")["est"]
            ref = SUB_REF if (T.cond == SUB_REF).any() else "Twins SSR"
            pairs = [("Twins SSR", "Twins DLR"), ("Twins SSR + N3 homophily network", ref),
                     ("Twins SSR + N3 homophily network", "Twins SSR + N2 random network"),
                     ("Twins SSR + N3 homophily network", "Twins SSR + N1 self-reflection")]
            for a, b in pairs:
                allP.append({"model": model, "var": var, "a": a, "b": b} | TE.paired_mae_diff(get(a), get(b), h))
            if not B2.empty:
                allP.append({"model": model, "var": var, "a": "Twins SSR", "b": "B2 persona-free LLM"}
                            | TE.paired_mae_diff(get("Twins SSR"), B2[B2["var"] == var].set_index("country")["est"], h))
            # each correction against the non-LLM comparator that uses the SAME human information
            BL = TE.baselines(tr)
            bl = lambda m: BL[(BL.method == m) & (BL["var"] == var)].set_index("country")["est"]
            Tm = T[["country", "cond", "var", "est"]]
            allP.append({"model": model, "var": var, "a": "Twins SSR", "b": "B5 30-country total"}
                        | TE.paired_mae_diff(get("Twins SSR"), bl("B5 30-country total"), h))
            allP.append({"model": model, "var": var, "a": "Twins SSR + CAL-LOCO", "b": "LOCO continent mean"}
                        | TE.paired_mae_diff(TE.cal_loco(get("Twins SSR"), h), bl("LOCO continent mean"), h))
            allP.append({"model": model, "var": var, "a": "Twins SSR + CAL-STYLE", "b": "B-XITEM cross-item regression"}
                        | TE.paired_mae_diff(TE.cal_style(Tm, tr, "Twins SSR", var), bl("B-XITEM cross-item regression"), h))
    M = pd.concat(allM, ignore_index=True)
    # baselines are model-independent: keep one copy
    M = pd.concat([M[M.model != "none"], M[M.model == "none"].drop_duplicates(["method", "var"])], ignore_index=True)
    P = pd.DataFrame(allP)
    if not P.empty:                                   # Holm adjustment within each model
        P["p_holm"] = np.nan
        for mdl, g in P.groupby("model"):
            g = g.dropna(subset=["p_two_sided"]).sort_values("p_two_sided")
            m_ = len(g)
            adj, run_max = [], 0.0
            for i, pv in enumerate(g["p_two_sided"]):
                run_max = max(run_max, min(1.0, (m_ - i) * pv))
                adj.append(run_max)
            P.loc[g.index, "p_holm"] = adj
    out = {"metrics": M, "paired": P, "domains": pd.concat(allD, ignore_index=True),
           "all30": pd.concat(allA, ignore_index=True), "network": pd.concat(allN, ignore_index=True),
           "estimates": pd.concat(allE, ignore_index=True)}
    for k, df in out.items():
        df.to_csv(dest / f"{k}.csv", index=False)
    return out


if __name__ == "__main__":
    from .embed import default_cache, make_embedder
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--embedding", default="openai")
    ap.add_argument("--dest", default="outputs/analysis_table")
    a = ap.parse_args()
    emb = make_embedder({"provider": a.embedding}, default_cache("outputs/cache"))
    r = run([Path(x) for x in a.runs], emb, Path(a.dest))
    pd.set_option("display.width", 250)
    print(r["metrics"].round(3).to_string())
