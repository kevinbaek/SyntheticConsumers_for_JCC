"""Country-level evaluation against the published report tables (table-only study).

Ground truth: top-2-box (T2B) shares printed for the 14 countries in each top/bottom-7 list
(XQ5 favorability, XQ6 recommendation, POPMEAN = mean 'popular with the general public' share over
13 domains), the 30-country totals, and the 13 domain-level totals.

Metrics (human vs synthetic, per item, over the countries with a printed value)
  MAE_pp        mean |synthetic - human| in percentage points
  one_minus_MAE 1 - MAE on the 0-1 scale (1 = perfect)
  JS_sim        1 - Jensen-Shannon divergence (base 2) between the binary distributions
                (T2B, 1 - T2B), averaged over countries (1 = identical)
  spearman      rank correlation across countries;  pearson   linear correlation
  bias_pp       mean signed error (positivity bias if > 0)
  sd_ratio      SD of synthetic country values / SD of human values (between-country spread)
  split_acc     share of countries placed on the correct side (top-7 vs bottom-7 list) when the
                synthetic values are split at their median

Comparators ("statistical" baselines that use no LLM)
  B0 uniform 40%;  B5 30-country total;  LOCO mean of the other listed countries;
  LOCO continent mean (other listed countries on the same continent, else LOCO mean);
  B1 previous-wave carry-forward (only for countries whose change vs 2024 is printed).
LLM comparator: B2 persona-free direct estimate by the same model.

Cultural response-style correction (cross-validated; never sees the held-out country's value)
  CAL-LOCO   human ~ a + b * synthetic fitted on the other countries of the same item, applied to the
             held-out country (corrects a global level/scale distortion of the twins)
  CAL-STYLE  country offset = mean (human - synthetic) of the SAME country on the OTHER items,
             added to this item (a country-specific response style shared across items, the
             "cultural character" of answering). Needs the country to be listed on >= 1 other item.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .codebook import CONTINENT, COUNTRIES, OVERALL_FAV, OVERALL_REC, TARGETS_POP_15, WAVE15_N
from .tables import carry_forward, global_mean, load_targets

KEY = [OVERALL_FAV, OVERALL_REC, "POPMEAN"]


def truth() -> pd.DataFrame:
    t = load_targets()
    t = t[(t.wave == 15) & (t.stat == "t2b") & (t.country != "ALL30") & (t["var"].isin(KEY))]
    t = t[["country", "var", "value", "list"]].rename(columns={"value": "human"})
    return t.reset_index(drop=True)          # list: top / bottom (7-country figures) / other (change box)


def _js_binary(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    def h(x):
        x = np.clip(x, 1e-12, 1 - 1e-12)
        return -(x * np.log2(x) + (1 - x) * np.log2(1 - x))
    m = (p + q) / 2
    return h(m) - (h(p) + h(q)) / 2


def metrics(est: pd.Series, hum: pd.Series, lists: pd.Series | None = None) -> dict:
    ix = est.dropna().index.intersection(hum.index)
    e, h = est[ix].astype(float), hum[ix].astype(float)
    out = {"n": len(ix)}
    if len(ix) < 3:
        return out
    err = e - h
    out["MAE_pp"] = float(np.mean(np.abs(err)))
    out["one_minus_MAE"] = 1 - out["MAE_pp"] / 100
    out["JS_sim"] = float(np.mean(1 - _js_binary(e.to_numpy() / 100, h.to_numpy() / 100)))
    out["bias_pp"] = float(np.mean(err))
    out["spearman"] = float(stats.spearmanr(e, h)[0]) if e.nunique() > 1 else np.nan
    out["pearson"] = float(stats.pearsonr(e, h)[0]) if e.nunique() > 1 else np.nan
    out["sd_ratio"] = float(np.std(e) / np.std(h))
    if lists is not None:
        tb = [c for c in ix if lists[c] in ("top", "bottom")]
        k = sum(lists[c] == "top" for c in tb)
        if len(tb) >= 4 and 0 < k < len(tb) and e[tb].nunique() > 1:
            # top-k recovery: the k highest predictions are called "top", k = number of true top countries
            pred_top = set(e[tb].sort_values(ascending=False, kind="mergesort").index[:k])
            out["split_acc"] = float(np.mean([(c in pred_top) == (lists[c] == "top") for c in tb]))
    return out


def baselines(tr: pd.DataFrame) -> pd.DataFrame:
    """Country-level predictions of the non-LLM comparators, long format (country, var, method, est)."""
    gm = global_mean()
    rows = []
    for var, g in tr.groupby("var"):
        h = g.set_index("country")["human"]
        for c in h.index:
            others = h.drop(c)
            same = [o for o in others.index if CONTINENT.get(o) == CONTINENT.get(c)]
            rows += [{"country": c, "var": var, "method": "B0 uniform", "est": 40.0},
                     {"country": c, "var": var, "method": "B5 30-country total", "est": gm.get(var, np.nan)},
                     {"country": c, "var": var, "method": "LOCO mean", "est": float(others.mean())},
                     {"country": c, "var": var, "method": "LOCO continent mean",
                      "est": float(others[same].mean()) if same else float(others.mean())}]
            b1 = carry_forward(c).get(var)
            if b1 is not None:
                rows.append({"country": c, "var": var, "method": "B1 carry-forward", "est": b1})
    rows += _cross_item(tr)
    return pd.DataFrame(rows)


def _cross_item(tr: pd.DataFrame) -> list[dict]:
    """B-XITEM: predict a country's item from the mean of its OTHER listed items (human values),
    with a linear map fitted on the other countries (LOCO). Same information as CAL-STYLE, no LLM."""
    H = tr.pivot(index="country", columns="var", values="human")
    Z = (H - H.mean()) / H.std(ddof=0)                             # items on a common scale (no target used)
    rows = []
    for var in KEY:
        x = Z[[v for v in KEY if v != var]].mean(axis=1)          # NaN if no other item listed
        ok = H[var].notna() & x.notna()
        for c in H.index[ok]:
            o = [i for i in H.index[ok] if i != c]
            if len(o) < 3:
                continue
            b, a = np.polyfit(x[o], H.loc[o, var], 1)
            rows.append({"country": c, "var": var, "method": "B-XITEM cross-item regression",
                         "est": float(np.clip(a + b * x[c], 0, 100))})
    return rows


def cal_loco(est: pd.Series, hum: pd.Series) -> pd.Series:
    ix = est.dropna().index.intersection(hum.index)
    out = {}
    for c in ix:
        o = [x for x in ix if x != c]
        b, a = np.polyfit(est[o], hum[o], 1)
        out[c] = float(np.clip(a + b * est[c], 0, 100))
    return pd.Series(out)


def cal_style(T: pd.DataFrame, tr: pd.DataFrame, cond: str, var: str) -> pd.Series:
    """Additive error model e[c,v] = human - synthetic = item bias(v) + country style(c), fitted without the
    held-out cell: item bias = mean error of the OTHER countries on this item; country style = mean over the
    country's OTHER listed items of its error minus that item's mean error among the other countries.
    Prediction = synthetic + item bias + country style. Needs >= 1 other listed item for the country."""
    H = tr.pivot(index="country", columns="var", values="human")
    S = T[T.cond == cond].pivot(index="country", columns="var", values="est")
    E = (H - S.reindex(index=H.index, columns=H.columns))
    out = {}
    for c in H.index:
        if pd.isna(E.at[c, var]):
            continue
        others = [u for u in KEY if u != var and u in E.columns and not pd.isna(E.at[c, u])
                  and E[u].drop(c).notna().any()]
        if not others:
            continue
        item_bias = float(E[var].drop(c).mean())
        style = float(np.mean([E.at[c, u] - E[u].drop(c).mean() for u in others]))
        out[c] = float(np.clip(S.at[c, var] + item_bias + style, 0, 100))
    return pd.Series(out)


def evaluate(T: pd.DataFrame, B2: pd.DataFrame | None, model: str, boot: int = 2000, seed: int = 7) -> pd.DataFrame:
    """T: country x cond x var estimates (columns country, cond, var, est). Returns one row per
    (model, method, var) with metrics and country-bootstrap 95% CIs for MAE and Spearman."""
    tr = truth()
    preds = []
    for cond, g in T.groupby("cond"):
        for var in KEY:
            s = g[g["var"] == var].set_index("country")["est"]
            if s.empty:
                continue
            preds.append((cond, var, s))
            h = tr[tr["var"] == var].set_index("country")["human"]
            if cond.startswith("Twins") and "round 1" not in cond:
                preds.append((f"{cond} + CAL-LOCO", var, cal_loco(s, h)))
                preds.append((f"{cond} + CAL-STYLE", var, cal_style(T, tr, cond, var)))
    if B2 is not None and not B2.empty:
        for var in KEY:
            preds.append(("B2 persona-free LLM", var, B2[B2["var"] == var].set_index("country")["est"]))
    for (method, var), g in baselines(tr).groupby(["method", "var"]):
        preds.append((method, var, g.set_index("country")["est"]))
    rows = []
    for method, var, s in preds:
        hv = tr[tr["var"] == var].set_index("country")
        m = metrics(s, hv["human"], hv["list"])
        if method in ("LOCO mean", "B0 uniform", "B5 30-country total") or method.endswith("CAL-LOCO"):
            # constant, leave-one-out mean, or refitted per fold: ranks are not interpretable
            m["spearman"] = m["pearson"] = m["split_acc"] = np.nan
        import zlib
        rng = np.random.default_rng([seed, zlib.crc32(f"{method}|{var}".encode())])   # order-independent CIs
        ix = s.dropna().index.intersection(hv.index)
        if len(ix) >= 5:
            bm, bs = [], []
            arr = np.array(ix)
            for _ in range(boot):
                b = rng.choice(arr, len(arr), replace=True)
                e, h = s[b].to_numpy(float), hv["human"][b].to_numpy(float)
                bm.append(np.mean(np.abs(e - h)))
                if np.std(e) > 0 and np.std(h) > 0:
                    bs.append(stats.spearmanr(e, h)[0])
            m["MAE_lo"], m["MAE_hi"] = np.percentile(bm, [2.5, 97.5])
            if bs and not np.isnan(m.get("spearman", np.nan)):
                m["rho_lo"], m["rho_hi"] = np.nanpercentile(bs, [2.5, 97.5])
        rows.append({"model": model if not method.startswith(("B0", "B1", "B5", "LOCO", "B-XITEM")) else "none",
                     "method": method, "var": var} | m)
    return pd.DataFrame(rows)


def paired_mae_diff(a: pd.Series, b: pd.Series, hum: pd.Series, boot: int = 5000, seed: int = 11) -> dict:
    """MAE(a) - MAE(b) over common countries with a paired country bootstrap (negative = a better)."""
    ix = a.dropna().index.intersection(b.dropna().index).intersection(hum.index)
    if len(ix) == 0:
        return {"n": 0, "diff_pp": np.nan, "lo": np.nan, "hi": np.nan, "p_two_sided": np.nan}
    d = (np.abs(a[ix] - hum[ix]) - np.abs(b[ix] - hum[ix])).to_numpy(float)
    if np.allclose(d, 0):
        return {"n": len(ix), "diff_pp": 0.0, "lo": 0.0, "hi": 0.0, "p_two_sided": 1.0}
    rng = np.random.default_rng(seed)
    bs = np.array([rng.choice(d, len(d), replace=True).mean() for _ in range(boot)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    p = min(1.0, 2 * min(np.mean(bs <= 0), np.mean(bs >= 0)))
    return {"n": len(ix), "diff_pp": float(d.mean()), "lo": float(lo), "hi": float(hi), "p_two_sided": float(p)}


def domain_eval(T13: pd.DataFrame, model: str) -> pd.DataFrame:
    """13-domain popularity structure: pooled (sample-size weighted) synthetic T2B vs the printed
    30-country domain totals. T13: country x cond x var (XQ1_*) with est."""
    t = load_targets()
    h = t[(t.country == "ALL30") & (t.wave == 15) & (t["var"].isin(TARGETS_POP_15))].set_index("var")["value"]
    w = pd.Series(WAVE15_N)
    rows = []
    for cond, g in T13.groupby("cond"):
        E = g.pivot(index="country", columns="var", values="est").reindex(COUNTRIES)
        pooled = pd.Series({v: np.average(E[v].dropna(), weights=w[E[v].dropna().index]) for v in E.columns if E[v].notna().any()})
        m = metrics(pooled, h)
        rows.append({"model": model, "method": cond, "var": "13 domains (30-country totals)"} | m)
    return pd.DataFrame(rows)


def all30_distribution(Tdist: pd.DataFrame, model: str) -> pd.DataFrame:
    """3-category (1-2 / 3 / 4-5) 30-country distribution for XQ5 and XQ6 vs the printed totals.
    Tdist: cond, var, country, b2b, mid, t2b (%)."""
    t = load_targets()
    a = t[(t.country == "ALL30") & (t.wave == 15)]
    w = pd.Series(WAVE15_N)
    rows = []
    for (cond, var), g in Tdist.groupby(["cond", "var"]):
        hv = a[a["var"] == var].set_index("stat")["value"]
        if not {"b2b", "mid", "t2b"} <= set(hv.index):
            continue
        H = np.array([hv["b2b"], hv["mid"], hv["t2b"]]) / 100
        g = g.set_index("country").reindex(COUNTRIES).dropna()
        S = np.array([np.average(g[c], weights=w[g.index]) for c in ("b2b", "mid", "t2b")]) / 100
        S = S / S.sum()
        m = 0.5 * (H + S)
        kl = lambda x, y: float(np.sum(np.where(x > 0, x * np.log2(np.clip(x, 1e-12, 1) / np.clip(y, 1e-12, 1)), 0)))
        rows.append({"model": model, "method": cond, "var": var,
                     "human_b2b": round(100 * H[0], 1), "human_mid": round(100 * H[1], 1), "human_t2b": round(100 * H[2], 1),
                     "syn_b2b": round(100 * S[0], 1), "syn_mid": round(100 * S[1], 1), "syn_t2b": round(100 * S[2], 1),
                     "JS_sim": 1 - (0.5 * kl(H, m) + 0.5 * kl(S, m))})
    return pd.DataFrame(rows)
