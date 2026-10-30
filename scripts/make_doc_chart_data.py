"""Small tidy CSVs, one per manuscript chart, cut from outputs/analysis_final/*.csv (no recomputation).

  python scripts/make_doc_chart_data.py outputs/analysis_final
writes outputs/analysis_final/doc_charts/c_*.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/analysis_final")
O = D / "doc_charts"
O.mkdir(exist_ok=True)
M = pd.read_csv(D / "metrics.csv")
MODELS = [m for m in ["gpt-5.5", "gemini-3.1-pro", "claude-sonnet-5"] if m in set(M.model)]
LAB = {"gpt-5.5": "GPT-5.5", "gemini-3.1-pro": "Gemini 3.1 Pro", "claude-sonnet-5": "Claude Sonnet 5"}
SLUG = {"gpt-5.5": "gpt", "gemini-3.1-pro": "gemini", "claude-sonnet-5": "claude"}
ITEM = {"XQ5": "Favorability", "XQ6": "Recommendation", "POPMEAN": "Popularity"}
r1 = lambda x: None if pd.isna(x) else round(float(x), 1)  # noqa: E731
r2 = lambda x: None if pd.isna(x) else round(float(x), 2)  # noqa: E731


def mae():
    rows = []
    twins = [("Twins DLR", "Direct rating"), ("Twins SSR", "SSR"), ("Twins SSR + CAL-LOCO", "SSR + CAL-LOCO"),
             ("Twins SSR + CAL-STYLE", "SSR + CAL-STYLE"), ("B2 persona-free LLM", "Persona-free estimate")]
    base = [("B0 uniform", "Uniform 40%"), ("B5 30-country total", "30-country total"),
            ("LOCO continent mean", "Continent mean"), ("B-XITEM cross-item regression", "Cross-item regression")]
    k = 0
    for meth, lab in twins + base:
        k += 1
        for v in ITEM:
            for mdl in (MODELS if (meth, lab) in twins else ["none"]):
                r = M[(M.model == mdl) & (M.method == meth) & (M["var"] == v)]
                if r.empty:
                    continue
                r = r.iloc[0]
                rows.append({"order": k, "item": ITEM[v], "kind": "twins" if mdl != "none" else "baseline", "method": lab,
                             "model": LAB.get(mdl, "Baseline"), "slug": SLUG.get(mdl, "base"), "n": int(r.n),
                             "mae": r1(r.MAE_pp), "lo": r1(r.MAE_lo), "hi": r1(r.MAE_hi), "rho": r2(r.spearman),
                             "bias": r1(r.bias_pp), "spread": r2(r.sd_ratio)})
    pd.DataFrame(rows).to_csv(O / "c_mae.csv", index=False)


def scatter():
    W = pd.read_csv(D / "country_estimates_wide.csv").dropna(subset=["human"])
    W = W[W.cond.isin(["Twins DLR", "Twins SSR"]) & W["var"].isin(list(ITEM))]
    MODE = {"Twins DLR": "Direct rating", "Twins SSR": "Semantic similarity rating"}
    out = pd.DataFrame({"item": W["var"].map(ITEM), "mode": W.cond.map(MODE),
                        "model": W.model.map(LAB), "slug": W.model.map(SLUG), "country": W.country,
                        "human": W.human.round(1), "est": W.est.round(1)})
    out["_i"] = W["var"].map({"XQ5": 0, "XQ6": 1, "POPMEAN": 2})
    out["_m"] = W.model.map({m: k for k, m in enumerate(MODELS)})
    out.sort_values(["_i", "mode", "_m", "country"]).drop(columns=["_i", "_m"]).to_csv(O / "c_scatter.csv", index=False)


def bands():
    A = pd.read_csv(D / "all30.csv")
    rows = []
    for v in ["XQ5", "XQ6"]:
        g = A[A["var"] == v]
        h = g.iloc[0]
        rows.append({"item": ITEM[v], "source": "Published survey", "slug": "human", "mode": "-", "b2b": r1(h.human_b2b),
                     "mid": r1(h.human_mid), "t2b": r1(h.human_t2b), "js": None})
        for mdl in MODELS:
            for meth in ["Twins DLR", "Twins SSR"]:
                r = g[(g.model == mdl) & (g.method == meth)]
                if r.empty:
                    continue
                r = r.iloc[0]
                rows.append({"item": ITEM[v], "source": LAB[mdl], "slug": SLUG[mdl], "mode": meth.replace("Twins ", ""),
                             "b2b": r1(r.syn_b2b), "mid": r1(r.syn_mid), "t2b": r1(r.syn_t2b), "js": round(float(r.JS_sim), 3)})
    pd.DataFrame(rows).to_csv(O / "c_bands.csv", index=False)


def domains():
    P = pd.read_csv(D / "domain_profile.csv")
    names = {"XQ1_1": "Drama", "XQ1_2": "Variety show", "XQ1_3": "Film", "XQ1_4": "Music", "XQ1_5": "Animation",
             "XQ1_6": "Publishing", "XQ1_7": "Webtoon", "XQ1_8": "Game", "XQ1_9": "Fashion", "XQ1_10": "Beauty",
             "XQ1_11": "Food", "XQ1_12": "Character", "XQ1_13": "Performance"}
    P = P[P.method.isin(["Twins SSR", "Twins DLR"])].copy()
    h = P.groupby("var")["human"].first()
    rank = h.rank(ascending=False, method="first").astype(int)
    out = pd.DataFrame({"domain": P["var"].map(names), "var": P["var"], "rank": P["var"].map(rank),
                        "human": P.human.round(1), "mode": P.method.str.replace("Twins ", "", regex=False),
                        "model": P.model.map(LAB), "slug": P.model.map(SLUG), "synthetic": P.synthetic.round(1)})
    out["mode"] = out["mode"].map({"DLR": "Direct rating", "SSR": "Semantic similarity rating"})
    out["_m"] = P.model.map({m: k for k, m in enumerate(MODELS)})
    out.sort_values(["mode", "rank", "_m"]).drop(columns="_m").to_csv(O / "c_domains.csv", index=False)


def network():
    N = pd.read_csv(D / "network_by_item.csv")
    arm = {"P3a+N1self": "N1 self-reflection", "P3a+N2random": "N2 random", "P3a+N3homophily": "N3 homophily"}
    it = {"social perception (XQ1)": "Perceived popularity (social)", "own preference (XQ5, XQ6)": "Own favorability and recommendation"}
    out = pd.DataFrame({"model": N.model.map(LAB), "slug": N.model.map(SLUG), "arm": N.cond.map(arm),
                        "item_type": N.item_type.map(it), "pairs": N.pairs,
                        "moved_pct": (100 * N["share_moved_gt_0.25"]).round(1), "mean_abs_shift": N.mean_abs_shift.round(3),
                        "mean_shift": N.mean_shift.round(3)})
    out["_m"] = N.model.map({m: k for k, m in enumerate(MODELS)})
    out["_t"] = N.item_type.map({"social perception (XQ1)": 0, "own preference (XQ5, XQ6)": 1})
    out.sort_values(["_t", "arm", "_m"]).drop(columns=["_m", "_t"]).to_csv(O / "c_network.csv", index=False)


def continent():
    C = pd.read_csv(D / "continent_error.csv")
    C = C[C.cond.isin(["Twins DLR", "Twins SSR"])]
    out = pd.DataFrame({"model": C.model.map(LAB), "slug": C.model.map(SLUG), "mode": C.cond.str.replace("Twins ", "", regex=False),
                        "item": C["var"].map(ITEM), "continent": C.continent, "mean_error": C.mean_error_pp.round(1),
                        "n": C.n_countries})
    out.to_csv(O / "c_continent.csv", index=False)


def gradient():
    G = pd.read_csv(D / "persona_gradients.csv")
    G = G[(G.attribute.isin(["korea_awareness", "age_band"])) & (G.level != "spearman(code, score)") & (G["var"] == "XQ5")]
    LV = {"little": (1, "knows little"), "somewhat": (2, "knows somewhat"), "knows Korea very well": (3, "knows very well")}
    G = G[G.attribute == "korea_awareness"]
    out = pd.DataFrame({"model": G.model.map(LAB), "slug": G.model.map(SLUG),
                        "mode": G["mode"].map({"dlr": "Direct rating", "ssr": "Semantic similarity rating"}),
                        "order": G.level.map(lambda x: LV[x][0]), "level": G.level.map(lambda x: LV[x][1]), "n": G.n,
                        "t2b": G.t2b_pct.round(1), "mean_score": G.mean_score.round(2)})
    out["_m"] = G.model.map({m: k for k, m in enumerate(MODELS)})
    out.sort_values(["mode", "_m", "order"]).drop(columns="_m").to_csv(O / "c_gradient.csv", index=False)


def corr():
    rows = []
    I = pd.read_csv(D / "item_coherence.csv")
    for _, r in I.iterrows():
        rows.append({"analysis": "item coherence", "pair": r.pair, "source": r.source, "model": LAB.get(r.model, "-"),
                     "n": int(r.n), "rho": r2(r.spearman), "p": None if pd.isna(r.p) else round(float(r.p), 4)})
    if (D / "inter_model.csv").stat().st_size > 2:
        X = pd.read_csv(D / "inter_model.csv")
        for _, r in X.iterrows():
            rows.append({"analysis": "inter-model agreement", "pair": f"{LAB[r.model_a]} ~ {LAB[r.model_b]}",
                         "source": f"{r.method}, {ITEM[r['var']]}", "model": "-", "n": int(r.n_countries),
                         "rho": r2(r.spearman), "p": None if pd.isna(r.p) else round(float(r.p), 4)})
    A = pd.read_csv(D / "mode_agreement.csv")
    for mdl, g in A.groupby("model"):
        rows.append({"analysis": "DLR-SSR agreement within twin", "pair": "median over 15 items", "source": "same twin, same item",
                     "model": LAB.get(mdl, mdl), "n": int(g.n_twins.median()), "rho": r2(g.spearman_dlr_ssr.median()), "p": None})
    pd.DataFrame(rows).to_csv(O / "c_corr.csv", index=False)


for f in (mae, scatter, bands, domains, network, continent, gradient, corr):
    try:
        f()
        print("ok", f.__name__)
    except Exception as e:  # noqa: BLE001
        print("FAILED", f.__name__, type(e).__name__, e)
