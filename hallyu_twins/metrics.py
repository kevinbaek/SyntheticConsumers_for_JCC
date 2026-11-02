"""Reproduction-similarity metrics (individual, country, distribution, structure).

Conventions
* human answers h in {1..5} with survey weights w; synthetic predictions per twin are either a
  probability vector p (SSR, or a one-hot DLR answer) or its expectation.
* "country level" uses weighted human shares vs the mean synthetic probability mass (the SSR
  population distribution is the mixture of twin distributions).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

K = np.arange(1, 6)


def onehot(v: np.ndarray) -> np.ndarray:
    out = np.zeros((len(v), 5))
    ok = ~np.isnan(v)
    out[np.where(ok)[0], v[ok].astype(int) - 1] = 1.0
    out[~ok] = np.nan
    return out


def wdist(h: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    w = np.ones_like(h, dtype=float) if w is None else w
    ok = ~np.isnan(h)
    d = np.array([w[ok][h[ok] == k].sum() for k in K], dtype=float)
    return d / d.sum() if d.sum() else np.full(5, np.nan)


def ks_sim(p: np.ndarray, q: np.ndarray) -> float:
    """1 - Kolmogorov-Smirnov distance between two distributions on 1..5 (Maier et al.)."""
    return float(1 - np.max(np.abs(np.cumsum(p) - np.cumsum(q))))


def jsd(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    def kl(a, b):
        a, b = np.clip(a, 1e-12, 1), np.clip(b, 1e-12, 1)
        return float(np.sum(a * np.log2(a / b)))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def sd_of(d: np.ndarray) -> float:
    mu = d @ K
    return float(np.sqrt(d @ (K - mu) ** 2))


def fisher_mean(rs: list[float], ns: list[int]) -> float:
    rs, ns = np.array(rs, float), np.array(ns, float)
    ok = ~np.isnan(rs) & (ns > 3)
    if not ok.any():
        return float("nan")
    z = np.arctanh(np.clip(rs[ok], -0.999, 0.999))
    return float(np.tanh(np.average(z, weights=ns[ok] - 3)))


def item_metrics(df: pd.DataFrame) -> dict:
    """df rows = twins for one (model, condition, mode, item) with columns
    country, continent, h (human), w (weight), p1..p5 (synthetic probabilities)."""
    P = df[[f"p{k}" for k in K]].to_numpy(float)
    h, w = df["h"].to_numpy(float), df["w"].to_numpy(float)
    ok = ~np.isnan(h) & ~np.isnan(P).any(axis=1)
    df, P, h, w = df[ok], P[ok], h[ok], w[ok]
    e = P @ K
    res = {"n": int(len(df))}
    res["acc_indiv"] = float(1 - np.mean(np.abs(e - h)) / 4)
    rs, ns = [], []
    rows = []
    for c, g in df.groupby("country"):
        idx = df.index.get_indexer(g.index)
        hc, ec, wc, Pc = h[idx], e[idx], w[idx], P[idx]
        if len(np.unique(hc)) > 1 and np.std(ec) > 1e-9:
            rs.append(stats.pearsonr(ec, hc)[0]); ns.append(len(idx))
        dh, ds = wdist(hc, wc), Pc.mean(axis=0)
        rows.append({"country": c, "t2b_h": dh[3:].sum(), "t2b_s": ds[3:].sum(), "mean_h": dh @ K, "mean_s": ds @ K,
                     "ks": ks_sim(dh, ds), "jsd": jsd(dh, ds), "sd_h": sd_of(dh), "sd_s": sd_of(ds),
                     "sd_ind_s": float(np.std(ec)),
                     "sd_ind_h": float(np.sqrt(np.cov(hc, aweights=wc))) if len(hc) > 1 else np.nan})
    C = pd.DataFrame(rows)
    res["r_wc"] = fisher_mean(rs, ns)
    if len(C) >= 3:
        res["r_bc"] = float(stats.spearmanr(C.t2b_s, C.t2b_h)[0])
        res["r_bc_mean"] = float(stats.pearsonr(C.mean_s, C.mean_h)[0])
    res["level_err_pp"] = float(100 * np.mean(np.abs(C.t2b_s - C.t2b_h)))
    res["positivity_pp"] = float(100 * np.mean(C.t2b_s - C.t2b_h))
    res["ks_sim"] = float(C.ks.mean())
    res["jsd"] = float(C.jsd.mean())
    res["hr_dist"] = float(np.mean(C.sd_s / C.sd_h))
    res["hr_indiv"] = float(np.mean(C.sd_ind_s / C.sd_ind_h))
    return res, C


def split_half_ceiling(human: pd.DataFrame, reps: int, seed: int) -> float:
    """Spearman-Brown corrected split-half reliability of country T2B (ceiling for r_bc)."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(reps):
        a, b = [], []
        for _, g in human.groupby("country"):
            m = rng.random(len(g)) < 0.5
            a.append(wdist(g.h.to_numpy(float)[m], g.w.to_numpy(float)[m])[3:].sum())
            b.append(wdist(g.h.to_numpy(float)[~m], g.w.to_numpy(float)[~m])[3:].sum())
        r = stats.spearmanr(a, b)[0]
        out.append(2 * r / (1 + r))
    return float(np.nanmean(out))


def subgroup_sign_agreement(df: pd.DataFrame, col: str, a, b) -> float:
    """Share of countries where the synthetic gap (a - b) has the same sign as the human gap."""
    hits = []
    for _, g in df.groupby("country"):
        ga, gb = g[g[col] == a], g[g[col] == b]
        if len(ga) < 5 or len(gb) < 5:
            continue
        eh = np.average(ga.h, weights=ga.w) - np.average(gb.h, weights=gb.w)
        Pa, Pb = ga[[f"p{k}" for k in K]].to_numpy() @ K, gb[[f"p{k}" for k in K]].to_numpy() @ K
        es = Pa.mean() - Pb.mean()
        if abs(eh) > 1e-9:
            hits.append(np.sign(eh) == np.sign(es))
    return float(np.mean(hits)) if hits else float("nan")


def tost_equivalence(diff_boot: np.ndarray, margin: float) -> bool:
    """90% bootstrap CI of the difference entirely inside (-margin, +margin)."""
    lo, hi = np.percentile(diff_boot, [5, 95])
    return bool(lo > -margin and hi < margin)
