"""Robustness and design checks requested in peer review (no new model calls; read-only on the runs).

  python -m hallyu_twins.robustness --runs outputs/final_* --est outputs/analysis_final/estimates.csv \
      --dest outputs/analysis_final --embedding openai

None of these analyses changes the pre-specified evaluation (metrics.csv, paired.csv): they add views of
the same responses. Outputs (CSV, prefix rb_):
  rb_xq5_all30.csv        XQ5 on all 30 countries (report p. 38 prints the full ranking), on the 14 listed and on
                          the 16 middle countries; all comparators incl. B-PROFILE and leave-one-out B5;
                          CAL-LOCO fitted on the 14 listed countries and tested on the 16 middle ones
  rb_xq5_all30_paired.csv paired MAE and Spearman contrasts on all 30 countries (twins vs non-LLM comparators, B2)
  rb_listed_extra.csv     B-PROFILE and B5-LOO on the listed countries of each item (pre-specified set)
  rb_censoring.csv        XQ6 / POPMEAN: unlisted countries must lie between the 7th-lowest and 7th-highest printed
                          values; share of synthetic estimates outside that band, and the n-weighted mean of the
                          unlisted group backed out of the printed 30-country total vs the synthetic one
  rb_within_group.csv     Spearman within the top-7 and within the bottom-7 (not inflated by the gap between groups)
  rb_dlr_reversal.csv     forward vs reversed option order under DLR (country T2B difference, sign-flip test)
  rb_anchor_selftest.csv  each SSR anchor statement scored as if it were an answer (attainable T2B range)
  rb_duplicates.csv       personas identical to another persona of the same country; identical responses
  rb_verbatim.csv         round-2 answers identical to the same twin's round-1 answer, by arm
  rb_wave14.csv           twins' error against the previous wave's value vs the current wave (recall check)
  rb_signflip.csv         exact sign-flip test for the paired MAE contrasts (alternative to the bootstrap p)
  rb_noise_ceiling.csv    expected MAE of a perfect predictor given human sampling error (and twin Monte Carlo error)
  rb_two_level.csv        two-level bootstrap (twins within countries, then countries) for MAE of DLR and SSR
  rb_margins.csv          achieved vs printed persona margins, per dimension (max absolute gap over countries)
  rb_probes.csv           recall probe (previous-edition values from memory) and B2 without the survey description
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from . import table_eval as TE
from .codebook import CONTINENT, COUNTRIES, ITEMS, OVERALL_FAV, OVERALL_REC, TARGETS_POP_15, WAVE15_N
from .elicit import SSRScorer, anchor_texts
from .tables import TABLE_DIR, carry_forward, global_mean, load_targets, marginals

N = pd.Series(WAVE15_N, dtype=float)
NTOT = float(N.sum())
ITEML = {"XQ5": "Favorability", "XQ6": "Recommendation", "POPMEAN": "Popularity"}
_SCORED: dict = {}


def _scored(run: Path) -> pd.DataFrame:
    """scored.csv written by the analysis (same embedder); read once per process."""
    k = str(run)
    if k not in _SCORED:
        s = pd.read_csv(run / "scored.csv")
        tw = pd.read_csv(run / "twins.csv").set_index("resp_id")
        s["country"] = tw.loc[s.resp_id, "country"].to_numpy()
        s["t2b"] = np.where(s["mode"] == "ssr", s["p4"] + s["p5"], (s["dlr"] >= 4).astype(float).where(s["dlr"].notna()))
        _SCORED[k] = s
    return _SCORED[k]


def _model(run: Path) -> str:
    return json.load(open(run / "run_meta.json"))["model"]


def _b2(run: Path) -> pd.DataFrame:
    b = pd.read_csv(run / "b2_direct.csv").rename(columns={"t2b": "est"})
    return b.assign(cond="B2 persona-free LLM")


def knowledge_share(country: str) -> float:
    """Share of the country's respondents who say they know Korea very well (printed profile)."""
    return float(marginals(country)["korea_awareness"].get(1.0, np.nan))


def _loo_linear(x: pd.Series, y: pd.Series, targets) -> pd.Series:
    out = {}
    for c in targets:
        o = [i for i in y.index if i != c and not np.isnan(x.get(i, np.nan))]
        if len(o) < 3 or np.isnan(x.get(c, np.nan)):
            continue
        b, a = np.polyfit(x[o], y[o], 1)
        out[c] = float(np.clip(a + b * x[c], 0, 100))
    return pd.Series(out, dtype=float)


def _extreme_recovery(e: pd.Series, h: pd.Series, k: int = 7) -> float:
    ix = e.dropna().index.intersection(h.index)
    if len(ix) < 2 * k:
        return np.nan
    e, h = e[ix], h[ix]
    pt, pb = set(e.nlargest(k).index), set(e.nsmallest(k).index)
    tt, tb = set(h.nlargest(k).index), set(h.nsmallest(k).index)
    return (len(pt & tt) + len(pb & tb)) / (2 * k)


def _boot_mae(e: pd.Series, h: pd.Series, B: int = 2000, seed: int = 11) -> tuple[float, float]:
    ix = e.dropna().index.intersection(h.index)
    err = np.abs(e[ix].to_numpy() - h[ix].to_numpy())
    rng = np.random.default_rng(seed)
    bs = err[rng.integers(0, len(err), (B, len(err)))].mean(axis=1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ---------------------------------------------------------------------------------------------------------
def xq5_all30(E: pd.DataFrame, B2: pd.DataFrame) -> pd.DataFrame:
    A = pd.read_csv(TABLE_DIR / "targets_xq5_all30.csv").set_index("country")["value"].astype(float)
    listed = TE.truth().query("var == 'XQ5'").set_index("country")
    lists = listed["list"]
    assert (A[listed.index] == listed["human"]).all(), "listed XQ5 values differ between files"
    middle = [c for c in A.index if c not in listed.index]
    preds = []
    for (mdl, cond), g in E[(E["var"] == OVERALL_FAV) & E.cond.isin(["Twins DLR", "Twins SSR"])].groupby(["model", "cond"]):
        s = g.set_index("country")["est"]
        preds += [(mdl, cond, s), (mdl, cond + " + CAL-LOCO (LOO, 30)", TE.cal_loco(s, A))]
        # calibrate on the 14 listed (extreme) countries only, apply to the 16 middle ones
        b, a = np.polyfit(s[listed.index], A[listed.index], 1)
        preds.append((mdl, cond + " + CAL-LOCO (fit on 14 listed)", pd.Series({c: float(np.clip(a + b * s[c], 0, 100)) for c in middle})))
    for mdl, g in B2[B2["var"] == OVERALL_FAV].groupby("model"):
        preds.append((mdl, "B2 persona-free LLM", g.set_index("country")["est"]))
    gm = global_mean()[OVERALL_FAV]
    ks = pd.Series({c: knowledge_share(c) for c in A.index})
    base = {"B0 uniform": pd.Series(40.0, index=A.index),
            "B5 30-country total": pd.Series(gm, index=A.index),
            "B5 leave-one-out total": pd.Series({c: (NTOT * gm - N[c] * A[c]) / (NTOT - N[c]) for c in A.index}),
            "LOCO mean": pd.Series({c: A.drop(c).mean() for c in A.index}),
            "LOCO continent mean": pd.Series({c: A[[o for o in A.index if o != c and CONTINENT[o] == CONTINENT[c]]].mean()
                                              if any(CONTINENT[o] == CONTINENT[c] for o in A.index if o != c) else A.drop(c).mean()
                                              for c in A.index}),
            "B-PROFILE knowledge share (LOO)": _loo_linear(ks, A, A.index)}
    t = load_targets()
    d = t[(t.wave == 14) & (t.stat == "t2b_delta") & (t["var"] == OVERALL_FAV) & (t.country != "ALL30")].set_index("country")["value"]
    base["B1 carry-forward"] = pd.Series({c: round(A[c] - d[c], 1) for c in d.index if c in A.index})
    preds += [("none", k, v) for k, v in base.items()]
    rows = []
    for mdl, meth, s in preds:
        for scope, idx in (("all 30", list(A.index)), ("14 listed", list(listed.index)), ("16 middle", middle)):
            if "fit on 14 listed" in meth and scope != "16 middle":
                continue                                   # defined for the held-out middle countries only
            h = A[idx]
            m = TE.metrics(s, h, lists if scope == "14 listed" else None)
            if "MAE_pp" not in m:
                continue
            const = meth in ("B0 uniform", "B5 30-country total", "B5 leave-one-out total") or meth.startswith("LOCO mean")
            if const or "CAL-LOCO (LOO" in meth:
                m["spearman"] = m["pearson"] = m["split_acc"] = np.nan
            lo, hi = _boot_mae(s, h)
            m.update({"model": mdl, "method": meth, "scope": scope, "MAE_lo": lo, "MAE_hi": hi,
                      "extreme7_recovery": _extreme_recovery(s, h) if scope == "all 30" and not const else np.nan})
            rows.append(m)
    return pd.DataFrame(rows)


def xq5_all30_paired(E: pd.DataFrame, B2: pd.DataFrame) -> pd.DataFrame:
    """Paired comparisons on all 30 countries (XQ5): MAE difference with an exact-style sign-flip test
    (Monte Carlo, 200,000 draws) and the Spearman difference with a country bootstrap (5,000)."""
    A = pd.read_csv(TABLE_DIR / "targets_xq5_all30.csv").set_index("country")["value"].astype(float)
    ks = pd.Series({c: knowledge_share(c) for c in A.index})
    gm = global_mean()[OVERALL_FAV]
    base = {"B-PROFILE knowledge share (LOO)": _loo_linear(ks, A, A.index),
            "LOCO continent mean": pd.Series({c: A[[o for o in A.index if o != c and CONTINENT[o] == CONTINENT[c]]].mean()
                                              for c in A.index}),
            "B5 30-country total": pd.Series(gm, index=A.index)}
    rows = []
    rng = np.random.default_rng(17)
    for (mdl, cond), g in E[(E["var"] == OVERALL_FAV) & (E.cond == "Twins SSR")].groupby(["model", "cond"]):
        s = g.set_index("country")["est"].reindex(A.index)
        cands = {"Twins SSR": s, "Twins SSR + CAL-LOCO (LOO, 30)": TE.cal_loco(s, A).reindex(A.index)}
        b2 = B2[(B2.model == mdl) & (B2["var"] == OVERALL_FAV)].set_index("country")["est"].reindex(A.index)
        for an, a in cands.items():
            for bn, b in list(base.items()) + [("B2 persona-free LLM", b2)]:
                d = ((a - A).abs() - (b - A).abs()).to_numpy()
                p, kind = _signflip_p(d)
                rho_diff, lo, hi = np.nan, np.nan, np.nan
                if an == "Twins SSR" and bn in ("B-PROFILE knowledge share (LOO)", "LOCO continent mean", "B2 persona-free LLM"):
                    ra = stats.spearmanr(a, A)[0]
                    rb = stats.spearmanr(b, A)[0]
                    bs = []
                    idx = np.arange(len(A))
                    for _ in range(5000):
                        i = rng.choice(idx, len(idx))
                        bs.append(stats.spearmanr(a.iloc[i], A.iloc[i])[0] - stats.spearmanr(b.iloc[i], A.iloc[i])[0])
                    rho_diff, lo, hi = ra - rb, np.nanpercentile(bs, 2.5), np.nanpercentile(bs, 97.5)
                rows.append({"model": mdl, "a": an, "b": bn, "n": len(A), "MAE_a": float((a - A).abs().mean()),
                             "MAE_b": float((b - A).abs().mean()), "MAE_diff_pp": float(np.mean(d)), "p_signflip": p,
                             "test": kind, "rho_diff": rho_diff, "rho_diff_lo": lo, "rho_diff_hi": hi})
    return pd.DataFrame(rows)


def listed_extra() -> pd.DataFrame:
    """B-PROFILE and B5-LOO on the pre-specified listed countries of each item."""
    tr = TE.truth()
    gm = global_mean()
    rows = []
    for var in TE.KEY:
        h = tr[tr["var"] == var].set_index("country")["human"]
        lists = tr[tr["var"] == var].set_index("country")["list"]
        ks = pd.Series({c: knowledge_share(c) for c in h.index})
        for meth, s in (("B-PROFILE knowledge share (LOO)", _loo_linear(ks, h, h.index)),
                        ("B5 leave-one-out total", pd.Series({c: (NTOT * gm[var] - N[c] * h[c]) / (NTOT - N[c]) for c in h.index}))):
            m = TE.metrics(s, h, lists)
            if meth.startswith("B5"):
                m["spearman"] = m["pearson"] = m["split_acc"] = np.nan
            lo, hi = _boot_mae(s, h)
            m.update({"model": "none", "method": meth, "var": var, "MAE_lo": lo, "MAE_hi": hi})
            rows.append(m)
    return pd.DataFrame(rows)


def _pop11(runs: list[Path], E: pd.DataFrame, B2: pd.DataFrame) -> pd.DataFrame:
    """Country popularity averaged over the 11 domains common to earlier waves (without XQ1_12, XQ1_13), for the
    twins (round 1) and B2, so that the 11-domain sensitivity compares like with like. The 13-domain average
    rebuilt the same way must equal the main estimates (checked)."""
    d11 = [v for v in TARGETS_POP_15 if v not in ("XQ1_12", "XQ1_13")]
    out = []
    for run in runs:
        s = _scored(run)
        s = s[(s.cond == "P3a") & (s["round"] == 1) & s["var"].isin(TARGETS_POP_15) & s["t2b"].notna()]
        s = s.assign(cond_l=np.where(s["mode"] == "ssr", "Twins SSR", "Twins DLR"))
        g = s.groupby(["country", "cond_l", "var"])["t2b"].mean().mul(100).reset_index()
        for vars_, lab in ((TARGETS_POP_15, "POPMEAN"), (d11, "POPMEAN11")):
            m = g[g["var"].isin(vars_)].groupby(["country", "cond_l"])["t2b"].mean().reset_index()
            out.append(m.rename(columns={"cond_l": "cond", "t2b": "est"}).assign(var=lab, model=_model(run)))
    b = B2[B2["var"].isin(TARGETS_POP_15)]
    for vars_, lab in ((TARGETS_POP_15, "POPMEAN"), (d11, "POPMEAN11")):
        m = b[b["var"].isin(vars_)].groupby(["model", "country"])["est"].mean().reset_index()
        out.append(m.assign(var=lab, cond="B2 persona-free LLM"))
    P = pd.concat(out, ignore_index=True)
    chk = P[P["var"] == "POPMEAN"].merge(pd.concat([E[E.cond.isin(["Twins DLR", "Twins SSR"])], B2]),
                                         on=["model", "cond", "country", "var"], suffixes=("", "_main"))
    assert len(chk) == 3 * 30 * 3 and np.allclose(chk.est, chk.est_main, atol=1e-9), "13-domain rebuild mismatch"
    return P[P["var"] == "POPMEAN11"]


def censoring(E: pd.DataFrame, B2: pd.DataFrame, P11: pd.DataFrame | None = None) -> pd.DataFrame:
    tr = TE.truth()
    t = load_targets()
    totals = {"XQ6": float(t[(t.country == "ALL30") & (t.wave == 15) & (t.stat == "t2b") & (t["var"] == "XQ6")].value.iloc[0])}
    dom = t[(t.country == "ALL30") & (t.wave == 15) & (t.stat == "t2b") & t["var"].isin(TARGETS_POP_15)].set_index("var")["value"]
    totals["POPMEAN"] = float(dom.mean())                                   # 13 domains (main definition)
    totals["POPMEAN (11 domains)"] = float(dom.drop(["XQ1_12", "XQ1_13"]).mean())
    rows = []
    allE = pd.concat([E[E.cond.isin(["Twins DLR", "Twins SSR"])], B2] + ([P11] if P11 is not None else []))
    for var_key, total in totals.items():
        var = "POPMEAN" if var_key.startswith("POPMEAN") else var_key
        syn_var = "POPMEAN11" if var_key == "POPMEAN (11 domains)" else var
        if syn_var == "POPMEAN11" and P11 is None:
            continue
        g = tr[tr["var"] == var].set_index("country")
        lo_band = g[g["list"] == "bottom"]["human"].max()
        hi_band = g[g["list"] == "top"]["human"].min()
        unl = [c for c in COUNTRIES if c not in g.index]
        listed_sum = float((N[g.index] * g["human"]).sum())
        backout = (NTOT * total - listed_sum) / float(N[unl].sum())
        for (mdl, cond), s in allE[allE["var"] == syn_var].groupby(["model", "cond"]):
            s = s.set_index("country")["est"]
            su = s.reindex(unl).dropna()
            outside = ((su < lo_band) | (su > hi_band))
            dist = np.maximum(lo_band - su, 0) + np.maximum(su - hi_band, 0)
            syn_mean = float((N[su.index] * su).sum() / N[su.index].sum())
            rows.append({"var": var_key, "model": mdl, "method": cond, "n_unlisted": len(su), "band_lo": lo_band,
                         "band_hi": hi_band, "share_outside_band": float(outside.mean()),
                         "mean_distance_outside_pp": float(dist.mean()), "human_unlisted_mean_backout": backout,
                         "synthetic_unlisted_mean": syn_mean, "error_unlisted_mean_pp": syn_mean - backout,
                         "printed_or_derived_total": total})
    return pd.DataFrame(rows)


def within_group(E: pd.DataFrame, B2: pd.DataFrame) -> pd.DataFrame:
    tr = TE.truth()
    rows = []
    allE = pd.concat([E[E.cond.isin(["Twins DLR", "Twins SSR"])], B2])
    for (mdl, cond, var), s in allE[allE["var"].isin(TE.KEY)].groupby(["model", "cond", "var"]):
        s = s.set_index("country")["est"]
        g = tr[tr["var"] == var].set_index("country")
        for grp in ("top", "bottom"):
            ix = g.index[g["list"] == grp].intersection(s.index)
            r = stats.spearmanr(s[ix], g.loc[ix, "human"])[0] if len(ix) >= 4 and s[ix].nunique() > 1 else np.nan
            rows.append({"model": mdl, "method": cond, "var": var, "group": grp, "n": len(ix), "spearman": r})
    return pd.DataFrame(rows)


def _signflip_p(d: np.ndarray, max_exact: int = 20, draws: int = 200_000, seed: int = 5) -> tuple[float, str]:
    d = d[~np.isnan(d)]
    n = len(d)
    obs = abs(d.mean())
    if n <= max_exact:
        signs = np.array(list(itertools.product([1, -1], repeat=n)), dtype=np.int8)
        stat = np.abs((signs * d).mean(axis=1))
        return float((stat >= obs - 1e-12).mean()), "exact"
    rng = np.random.default_rng(seed)
    stat = np.abs((rng.choice([1, -1], (draws, n)) * d).mean(axis=1))
    return float((stat >= obs - 1e-12).mean()), f"Monte Carlo ({draws})"


def dlr_reversal(runs: list[Path]) -> pd.DataFrame:
    rows = []
    for run in runs:
        s = _scored(run)
        s = s[(s.cond == "P3a") & (s["mode"] == "dlr") & s["t2b"].notna()]
        pop = s[s["var"].str.startswith("XQ1_")].groupby(["resp_id", "country", "reverse"])["t2b"].mean().reset_index().assign(var="POPMEAN")
        s = pd.concat([s[s["var"].isin([OVERALL_FAV, OVERALL_REC])][["resp_id", "country", "reverse", "t2b", "var"]], pop])
        for var, g in s.groupby("var"):
            W = g.groupby(["country", "reverse"])["t2b"].mean().unstack()
            d = 100 * (W[True] - W[False]).to_numpy()
            p, kind = _signflip_p(d)
            rows.append({"model": _model(run), "var": var, "countries": int(np.isfinite(d).sum()),
                         "t2b_forward_pct": 100 * float(g[~g.reverse.astype(bool)]["t2b"].mean()),
                         "t2b_reversed_pct": 100 * float(g[g.reverse.astype(bool)]["t2b"].mean()),
                         "mean_country_diff_pp": float(np.nanmean(d)), "p_signflip": p, "test": kind})
    return pd.DataFrame(rows)


def anchor_selftest(scorer: SSRScorer) -> pd.DataFrame:
    rows = []
    for var in [OVERALL_FAV, OVERALL_REC] + list(TARGETS_POP_15):
        item = ITEMS[var]
        sets = anchor_texts(item)
        for si, s in enumerate(sets):
            P = scorer.probs(item, s)
            for k, (text, p) in enumerate(zip(s, P), start=1):
                rows.append({"var": var, "anchor_set": si + 1, "anchor_point": k, "anchor_text": text,
                             "t2b_if_given_as_answer": float(p[3] + p[4]), "expected_score": float(p @ np.arange(1, 6))})
    return pd.DataFrame(rows)


ATTRS = ["sex", "age", "occupation", "education", "marital", "korea_awareness", "nationality"]


def duplicates(runs: list[Path]) -> pd.DataFrame:
    rows = []
    for run in runs:
        tw = pd.read_csv(run / "twins.csv")
        key = tw[["country"] + ATTRS].astype(str).agg("|".join, axis=1)
        grp = tw.groupby(key)["resp_id"].apply(list)
        dup = grp[grp.map(len) > 1]
        raw = {json.loads(x)["call_id"]: json.loads(x)["text"] for x in open(run / "raw_r1.jsonl")}
        rev = tw.set_index("resp_id")["reverse"]
        for mode in ("ssr", "dlr"):
            ident_pairs = pairs = 0
            for ids in dup:
                for a, b in itertools.combinations(ids, 2):
                    if mode == "dlr" and rev[a] != rev[b]:
                        continue                                   # different prompt (option order)
                    pairs += 1
                    ident_pairs += raw.get(f"P3a|{a}|{mode}|r1") == raw.get(f"P3a|{b}|{mode}|r1")
            rows.append({"model": _model(run), "mode": mode, "duplicate_groups": len(dup),
                         "twins_in_groups": int(dup.map(len).sum()), "same_prompt_pairs": pairs,
                         "identical_response_pairs": ident_pairs})
    return pd.DataFrame(rows)


def verbatim(runs: list[Path]) -> pd.DataFrame:
    rows = []
    for run in runs:
        s = _scored(run)
        r1 = s[(s.cond == "P3a") & (s["mode"] == "ssr")].set_index(["resp_id", "var"])["text"]
        for cond in ("P3a+N1self", "P3a+N2random", "P3a+N3homophily"):
            r2 = s[s.cond == cond].set_index(["resp_id", "var"])["text"]
            ix = r1.index.intersection(r2.index)
            same = (r1[ix].str.strip() == r2[ix].str.strip())
            it = np.where(pd.Index(ix.get_level_values("var")).str.startswith("XQ1_"), "popularity (XQ1)", "own preference (XQ5, XQ6)")
            for t in ("popularity (XQ1)", "own preference (XQ5, XQ6)"):
                m = it == t
                rows.append({"model": _model(run), "cond": cond, "item_type": t, "pairs": int(m.sum()),
                             "share_verbatim_repeat": float(same[m].mean())})
    return pd.DataFrame(rows)


def wave14(E: pd.DataFrame) -> pd.DataFrame:
    """For countries with a printed change: is the synthetic value closer to the previous wave than to the current?"""
    A = pd.read_csv(TABLE_DIR / "targets_xq5_all30.csv").set_index("country")["value"]
    tr = TE.truth()
    rows = []
    for var in (OVERALL_FAV, OVERALL_REC):
        h15 = A if var == OVERALL_FAV else tr[tr["var"] == var].set_index("country")["human"]
        h14 = pd.Series({c: carry_forward(c).get(var) for c in h15.index}).dropna()
        if var == OVERALL_FAV:   # the full ranking supplies the 2025 level for the four extra changes
            t = load_targets()
            d = t[(t.wave == 14) & (t.stat == "t2b_delta") & (t["var"] == var) & (t.country != "ALL30")].set_index("country")["value"]
            h14 = pd.Series({c: round(A[c] - d[c], 1) for c in d.index})
        for (mdl, cond), g in E[(E["var"] == var) & E.cond.isin(["Twins DLR", "Twins SSR"])].groupby(["model", "cond"]):
            s = g.set_index("country")["est"]
            ix = h14.index.intersection(s.index)
            rows.append({"model": mdl, "method": cond, "var": var, "n": len(ix),
                         "MAE_vs_wave15": float((s[ix] - h15[ix]).abs().mean()),
                         "MAE_vs_wave14": float((s[ix] - h14[ix]).abs().mean()),
                         "share_closer_to_wave14": float(((s[ix] - h14[ix]).abs() < (s[ix] - h15[ix]).abs()).mean())})
    return pd.DataFrame(rows)


def signflip(E: pd.DataFrame, paired_csv: Path) -> pd.DataFrame:
    tr = TE.truth()
    P = pd.read_csv(paired_csv)
    est = E.copy()
    rows = []
    for _, r in P.iterrows():
        h = tr[tr["var"] == r["var"]].set_index("country")["human"]
        a = est[(est.model == r.model) & (est.cond == r.a) & (est["var"] == r["var"])].set_index("country")["est"]
        b = est[(est.model == r.model) & (est.cond == r.b) & (est["var"] == r["var"])].set_index("country")["est"]
        if a.empty or b.empty:
            continue                                   # contrasts with baselines/corrections: see paired.csv
        ix = a.index.intersection(b.index).intersection(h.index)
        d = ((a[ix] - h[ix]).abs() - (b[ix] - h[ix]).abs()).to_numpy()
        p, kind = _signflip_p(d)
        rows.append({"model": r.model, "var": r["var"], "a": r.a, "b": r.b, "n": len(ix), "diff_pp": float(d.mean()),
                     "p_bootstrap": r.p_two_sided, "p_signflip": p, "test": kind})
    return pd.DataFrame(rows)


def noise_ceiling(mc_csv: Path | None) -> pd.DataFrame:
    tr = TE.truth()
    MC = pd.read_csv(mc_csv) if mc_csv and mc_csv.exists() else None
    rows = []
    for var in TE.KEY:
        g = tr[tr["var"] == var].set_index("country")["human"]
        p = g / 100
        se_h = 100 * np.sqrt(p * (1 - p) / N[g.index])            # simple-random-sampling approximation
        rows.append({"var": var, "source": "human sampling error only", "model": "-", "mode": "-",
                     "expected_MAE_perfect_pp": float((se_h * np.sqrt(2 / np.pi)).mean())})
        if MC is not None:
            for _, r in MC[MC["var"] == var].iterrows():
                se = np.sqrt(se_h ** 2 + r.se_median_pp ** 2)
                rows.append({"var": var, "source": "human + twin Monte Carlo error", "model": r.model, "mode": r["mode"],
                             "expected_MAE_perfect_pp": float((se * np.sqrt(2 / np.pi)).mean())})
    return pd.DataFrame(rows)


def two_level(runs: list[Path], B: int = 1000, seed: int = 3) -> pd.DataFrame:
    tr = TE.truth()
    rows = []
    for run in runs:
        s = _scored(run)
        s = s[(s.cond == "P3a") & s["t2b"].notna()]
        pop = s[s["var"].str.startswith("XQ1_")].groupby(["resp_id", "country", "mode"])["t2b"].mean().reset_index().assign(var="POPMEAN")
        s = pd.concat([s[s["var"].isin([OVERALL_FAV, OVERALL_REC])][["resp_id", "country", "mode", "t2b", "var"]], pop])
        for var in TE.KEY:
            h = tr[tr["var"] == var].set_index("country")["human"]
            rng = np.random.default_rng(seed)
            data = {m: {c: 100 * g["t2b"].to_numpy() for c, g in s[(s["var"] == var) & (s["mode"] == m)].groupby("country")}
                    for m in ("dlr", "ssr")}
            cs = [c for c in h.index if c in data["dlr"] and c in data["ssr"]]
            hv = h[cs].to_numpy()
            mae = {m: [] for m in ("dlr", "ssr")}
            diff = []
            for _ in range(B):
                cidx = rng.integers(0, len(cs), len(cs))
                errs = {}
                for m in ("dlr", "ssr"):
                    est = np.array([rng.choice(data[m][cs[i]], len(data[m][cs[i]])).mean() for i in range(len(cs))])
                    errs[m] = np.abs(est - hv)
                for m in ("dlr", "ssr"):
                    mae[m].append(errs[m][cidx].mean())
                diff.append((errs["ssr"] - errs["dlr"])[cidx].mean())
            point = {m: float(np.mean(np.abs(np.array([data[m][c].mean() for c in cs]) - hv))) for m in ("dlr", "ssr")}
            for m in ("dlr", "ssr"):
                rows.append({"model": _model(run), "var": var, "quantity": f"MAE {m.upper()}", "point": point[m],
                             "lo": float(np.percentile(mae[m], 2.5)), "hi": float(np.percentile(mae[m], 97.5)), "B": B})
            rows.append({"model": _model(run), "var": var, "quantity": "MAE SSR - MAE DLR", "point": point["ssr"] - point["dlr"],
                         "lo": float(np.percentile(diff, 2.5)), "hi": float(np.percentile(diff, 97.5)), "B": B})
    return pd.DataFrame(rows)


def margins(runs: list[Path]) -> pd.DataFrame:
    run = runs[0]                                   # the same personas (same seed) are used by every model
    tw = pd.read_csv(run / "twins.csv")
    rows = []
    for c in COUNTRIES:
        g = tw[tw.country == c]
        for dim, m in marginals(c).items():
            ach = g[dim].value_counts(normalize=True)
            gap = max(abs(float(ach.get(k, 0.0)) - float(v)) for k, v in m.items())
            rows.append({"country": c, "dimension": dim, "max_abs_gap_pp": 100 * gap})
    D = pd.DataFrame(rows)
    same = all((pd.read_csv(r / "twins.csv").drop(columns=[], errors="ignore").equals(tw)) for r in runs)
    S = D.groupby("dimension")["max_abs_gap_pp"].agg(["median", "max"]).reset_index()
    return S.assign(same_personas_all_models=same)


def probes_eval(probe_root: Path) -> pd.DataFrame:
    """Recall probe (values the model says it remembers from the previous edition) and neutral-wording B2,
    scored like everything else. Wave-15 XQ5 truth on all 30 countries; XQ6/POPMEAN on the listed countries."""
    A = pd.read_csv(TABLE_DIR / "targets_xq5_all30.csv").set_index("country")["value"]
    tr = TE.truth()
    t = load_targets()
    d = t[(t.wave == 14) & (t.stat == "t2b_delta") & (t.country != "ALL30")]
    w14 = {}
    for var in (OVERALL_FAV, OVERALL_REC):
        h15 = A if var == OVERALL_FAV else tr[tr["var"] == var].set_index("country")["human"]
        dv = d[d["var"] == var].set_index("country")["value"]
        w14[var] = pd.Series({c: round(h15[c] - dv[c], 1) for c in dv.index if c in h15.index})
    rows = []
    for mdir in sorted(Path(probe_root).glob("*")):
        if not (mdir / "recall.csv").exists():
            continue
        R = pd.read_csv(mdir / "recall.csv")
        basis = R["basis"].value_counts(normalize=True).to_dict()
        for var, col in ((OVERALL_FAV, "favorability"), (OVERALL_REC, "recommendation")):
            s = pd.to_numeric(R[col], errors="coerce").groupby(R.country).mean()
            h = A if var == OVERALL_FAV else tr[tr["var"] == var].set_index("country")["human"]
            for target, hh in (("wave 15 (current)", h), ("wave 14 (previous, implied)", w14[var])):
                m = TE.metrics(s, hh)
                m.update({"model": mdir.name, "probe": "recall of previous edition", "var": var, "target": target,
                          "share_self_labelled_recall": float(basis.get("recall", 0.0))})
                rows.append(m)
        B = pd.read_csv(mdir / "b2_neutral.csv")
        for var in TE.KEY:
            s = B[B["var"] == var].set_index("country")["t2b"]
            h = tr[tr["var"] == var].set_index("country")
            m = TE.metrics(s, h["human"], h["list"])
            m.update({"model": mdir.name, "probe": "B2 without survey description", "var": var, "target": "wave 15 listed"})
            rows.append(m)
            if var == OVERALL_FAV:
                m = TE.metrics(s, A)
                m.update({"model": mdir.name, "probe": "B2 without survey description", "var": var, "target": "wave 15 all 30"})
                rows.append(m)
    return pd.DataFrame(rows)


def main(runs, est_csv, dest, embedder):
    E = pd.read_csv(est_csv)
    B2 = pd.concat([_b2(r).assign(model=_model(r)) for r in runs], ignore_index=True)
    out = {"rb_xq5_all30": xq5_all30(E, B2), "rb_xq5_all30_paired": xq5_all30_paired(E, B2), "rb_listed_extra": listed_extra(), "rb_censoring": censoring(E, B2, _pop11(runs, E, B2)),
           "rb_within_group": within_group(E, B2), "rb_dlr_reversal": dlr_reversal(runs),
           "rb_anchor_selftest": anchor_selftest(SSRScorer(embedder)), "rb_duplicates": duplicates(runs),
           "rb_verbatim": verbatim(runs), "rb_wave14": wave14(E), "rb_signflip": signflip(E, dest / "paired.csv"),
           "rb_noise_ceiling": noise_ceiling(dest / "monte_carlo_error.csv"), "rb_margins": margins(runs),
           "rb_two_level": two_level(runs), "rb_probes": probes_eval(Path(runs[0]).parent / "probes")}
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
