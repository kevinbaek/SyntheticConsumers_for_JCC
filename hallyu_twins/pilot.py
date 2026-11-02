"""Table-only pilot: one country, one model, targets printed in the summary report.

Stages (each idempotent, files under <out>/):
  prepare  -> twins.csv, marginal_check.csv, jobs_r1.jsonl (+ agent batches)
  round2   -> jobs_r2.jsonl (network exposure on social items), needs responses_r1.jsonl
  analyze  -> scored.csv, summary.csv, network.csv, report.md, figure

Conditions
  P1     country label only (identical personas; variation = model sampling only)
  P3a    country + sex/age/education/occupation/marital + Korea awareness (from the report's
         respondent-profile table). "a" = awareness only; per-country content-use rates are not
         printed in the summary report, so P3's behavioural cues cannot be used here.
  P3a+N  P3a, second round after seeing k homophilous neighbours' round-1 answers
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .codebook import ITEMS, OVERALL_FAV, OVERALL_REC, TARGETS_POP_15
from .elicit import SSRScorer, parse_dlr
from .jobs import agent_batches, read_jsonl, round1_jobs, round2_jobs, write_jsonl
from .network import build_network, homophily_diagnostic
from .tables import carry_forward, country_targets, global_mean, marginal_check, synthesize

ITEMS_PILOT = TARGETS_POP_15 + [OVERALL_FAV, OVERALL_REC]        # survey order: XQ1 block, XQ5, XQ6
NETWORK_ITEMS = [OVERALL_FAV, OVERALL_REC]


def prepare(country: str, out: Path, n: int = 30, n_p1: int = 10, seed: int = 20261030,
            per_batch: int = 5) -> list[dict]:
    out.mkdir(parents=True, exist_ok=True)
    twins = synthesize(country, n, seed)
    twins.to_csv(out / "twins.csv", index=False)
    marginal_check(twins, country).to_csv(out / "marginal_check.csv", index=False)
    p1 = twins.iloc[:n_p1].copy()
    jobs = round1_jobs(p1, "P1", "P1", ITEMS_PILOT, seed=seed) + round1_jobs(twins, "P3a", "P3", ITEMS_PILOT, seed=seed)
    write_jsonl(jobs, out / "jobs_r1.jsonl")
    agent_batches(jobs, out / "agent_batches_r1", per_batch)
    return jobs


def round2(out: Path, k: int = 3, seed: int = 20261030, per_batch: int = 5) -> list[dict]:
    twins = pd.read_csv(out / "twins.csv")
    r1 = {r["job_id"]: r["text"] for r in read_jsonl(out / "responses_r1.jsonl")}
    nbrs = build_network(twins, "homophily", k=k, seed=seed, feature_set="P3")
    rnd = build_network(twins, "random", k=k, seed=seed, feature_set="P3")
    json.dump({"homophily": nbrs, "homophily_sim": homophily_diagnostic(twins, nbrs, "P3"),
               "random_sim": homophily_diagnostic(twins, rnd, "P3")},
              open(out / "network.json", "w"), indent=1)
    jobs = round2_jobs(twins, "P3a", "P3a+N", "homophily", nbrs, r1, NETWORK_ITEMS, level="P3")
    write_jsonl(jobs, out / "jobs_r2.jsonl")
    agent_batches(jobs, out / "agent_batches_r2", per_batch)
    return jobs


# ---------------------------------------------------------------------------------------
def score(out: Path, scorer: SSRScorer) -> pd.DataFrame:
    jobs = read_jsonl(out / "jobs_r1.jsonl") + (read_jsonl(out / "jobs_r2.jsonl") if (out / "jobs_r2.jsonl").exists() else [])
    resp = {}
    for f in ("responses_r1.jsonl", "responses_r2.jsonl"):
        if (out / f).exists():
            resp.update({r["job_id"]: r["text"] for r in read_jsonl(out / f)})
    rows = []
    for j in jobs:
        rows.append({k: j[k] for k in ("job_id", "cond", "resp_id", "var", "mode", "round", "reverse")}
                    | {"text": resp.get(j["job_id"])})
    df = pd.DataFrame(rows)
    missing = df["text"].isna().sum()
    if missing:
        print(f"[pilot] {missing} jobs have no response yet")
    df = df.dropna(subset=["text"])
    df["dlr"] = np.nan
    m = df["mode"] == "dlr"
    df.loc[m, "dlr"] = [parse_dlr(t, r) for t, r in zip(df.loc[m, "text"], df.loc[m, "reverse"])]
    for k in range(1, 6):
        df[f"p{k}"] = np.nan
    for var, g in df[df["mode"] == "ssr"].groupby("var"):
        P = scorer.probs(ITEMS[var], g["text"].tolist())
        df.loc[g.index, [f"p{k}" for k in range(1, 6)]] = P
    df.to_csv(out / "scored.csv", index=False)
    return df


def _twin_matrix(df: pd.DataFrame, cond: str, mode: str) -> pd.DataFrame:
    """twins x items matrix of per-twin T2B (SSR: p4+p5; DLR: 1{answer>=4})."""
    g = df[(df.cond == cond) & (df["mode"] == mode)]
    val = (g["p4"] + g["p5"]) if mode == "ssr" else (g["dlr"] >= 4).astype(float).where(g["dlr"].notna())
    return g.assign(v=val).pivot_table(index="resp_id", columns="var", values="v")


def _stats(M: pd.DataFrame) -> dict[str, float]:
    out = {v: 100 * M[v].mean() for v in (OVERALL_FAV, OVERALL_REC) if v in M}
    pops = [c for c in TARGETS_POP_15 if c in M]
    if pops:
        out["POPMEAN"] = 100 * M[pops].mean(axis=0).mean()
    return out


def summarize(df: pd.DataFrame, country: str, out: Path, B: int = 2000, seed: int = 1) -> pd.DataFrame:
    tgt = country_targets(country)
    b1, gm = carry_forward(country), global_mean()
    rng = np.random.default_rng(seed)
    rows = []
    for cond in sorted(df.cond.unique()):
        for mode in ("ssr", "dlr"):
            M = _twin_matrix(df, cond, mode)
            if M.empty:
                continue
            point = _stats(M)
            boots = [_stats(M.iloc[rng.integers(0, len(M), len(M))]) for _ in range(B)]
            for var, est in point.items():
                bs = np.array([b[var] for b in boots])
                t = tgt.get(var)
                rows.append({"cond": cond, "mode": mode, "var": var, "n_twins": len(M), "synthetic": round(est, 1),
                             "ci_lo": round(float(np.percentile(bs, 2.5)), 1),
                             "ci_hi": round(float(np.percentile(bs, 97.5)), 1),
                             "human": t, "error_pp": None if t is None else round(est - t, 1),
                             "B0_uniform_err": None if t is None else round(40.0 - t, 1),
                             "B1_carryfwd_err": None if (t is None or var not in b1) else round(b1[var] - t, 1),
                             "B5_global_err": None if (t is None or var not in gm) else round(gm[var] - t, 1)})
    S = pd.DataFrame(rows)
    S.to_csv(out / "summary.csv", index=False)
    return S


def network_effect(df: pd.DataFrame, out: Path) -> pd.DataFrame:
    rows = []
    for var in NETWORK_ITEMS:
        for mode in ("ssr", "dlr"):
            a = df[(df.cond == "P3a") & (df["var"] == var) & (df["mode"] == mode)].set_index("resp_id")
            b = df[(df.cond == "P3a+N") & (df["var"] == var) & (df["mode"] == mode)].set_index("resp_id")
            if a.empty or b.empty:
                continue
            ix = a.index.intersection(b.index)
            if mode == "ssr":
                xa = (a.loc[ix, [f"p{k}" for k in range(1, 6)]].to_numpy() @ np.arange(1, 6))
                xb = (b.loc[ix, [f"p{k}" for k in range(1, 6)]].to_numpy() @ np.arange(1, 6))
            else:
                xa, xb = a.loc[ix, "dlr"].to_numpy(float), b.loc[ix, "dlr"].to_numpy(float)
            rows.append({"var": var, "mode": mode, "n": len(ix), "mean_r1": round(float(np.nanmean(xa)), 3),
                         "mean_r2": round(float(np.nanmean(xb)), 3), "sd_r1": round(float(np.nanstd(xa, ddof=1)), 3),
                         "sd_r2": round(float(np.nanstd(xb, ddof=1)), 3),
                         "share_changed": round(float(np.mean(np.abs(xa - xb) > (0.25 if mode == 'ssr' else 0))), 3)})
    N = pd.DataFrame(rows)
    N.to_csv(out / "network_effect.csv", index=False)
    return N


def figure(S: pd.DataFrame, country: str, out: Path) -> None:
    """Dot plot: synthetic estimate with 95% CI vs the human value per item; one panel per item."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"ssr": "#2a78d6", "dlr": "#eb6834"}
    markers = {"ssr": "o", "dlr": "s"}
    labels = {OVERALL_FAV: "Overall favorability (XQ5)", OVERALL_REC: "Recommendation (XQ6)",
              "POPMEAN": "Mean popularity, 13 domains (XQ1)"}
    conds = [c for c in ("P1", "P3a", "P3a+N") if c in set(S.cond)]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharex=True)
    for ax, var in zip(axes, labels):
        sub = S[S["var"] == var]
        for yi, cond in enumerate(conds):
            for k, mode in enumerate(("ssr", "dlr")):
                r = sub[(sub.cond == cond) & (sub["mode"] == mode)]
                if r.empty:
                    continue
                r = r.iloc[0]
                y = yi + (k - 0.5) * 0.28
                ax.plot([r.ci_lo, r.ci_hi], [y, y], color=colors[mode], lw=2, solid_capstyle="round")
                ax.plot(r.synthetic, y, markers[mode], color=colors[mode], ms=8, mec="white", mew=1.5,
                        label=mode.upper() if (yi == 0 and var == OVERALL_FAV) else None)
        h = sub["human"].dropna()
        if len(h):
            ax.axvline(h.iloc[0], color="#444444", lw=1.5, ls="--", zorder=0)
            ax.text(h.iloc[0] + 1, -0.75, f"human {h.iloc[0]:.1f}", fontsize=8, color="#444444", va="center")
        b1 = carry_forward(country).get(var)
        if b1 is not None:
            ax.plot(b1, -0.75, "D", mfc="white", mec="#777777", mew=1.5, ms=7,
                    label="B1 carry-forward (wave 14)" if var == OVERALL_FAV else None)
        ax.set_yticks(range(len(conds)), conds)
        ax.set_ylim(-1.1, len(conds) - 0.5)
        ax.set_title(labels[var], fontsize=10)
        ax.set_xlim(0, 104)
        ax.grid(axis="x", color="#e6e6e6", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("Top-2-box share (%)", fontsize=9)
    fig.legend(frameon=False, fontsize=8, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"{country}: synthetic twins vs published survey (2026 Overseas Hallyu Survey)", fontsize=11)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(out / "pilot_figure.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def sensitivity(out: Path, embedder, taus=(0.01, 0.02, 0.05), cond: str = "P3a") -> pd.DataFrame:
    """Descriptive only (NOT used to choose settings): how the SSR level moves with the mapping."""
    df = pd.read_csv(out / "scored.csv")
    g = df[(df.cond == cond) & (df["mode"] == "ssr") & (df["round"] == 1)]
    rows = []
    settings = [("maier", None)] + [("softmax", t) for t in taus]
    for method, tau in settings:
        sc = SSRScorer(embedder, method=method, tau=tau or 0.02)
        est = {}
        for var, gv in g.groupby("var"):
            P = sc.probs(ITEMS[var], gv["text"].tolist())
            est[var] = 100 * float((P[:, 3] + P[:, 4]).mean())
        pops = [est[v] for v in TARGETS_POP_15 if v in est]
        rows.append({"mapping": method if tau is None else f"softmax tau={tau}", "XQ5": round(est[OVERALL_FAV], 1),
                     "XQ6": round(est[OVERALL_REC], 1), "POPMEAN": round(float(np.mean(pops)), 1)})
    T = pd.DataFrame(rows)
    T.to_csv(out / "ssr_sensitivity.csv", index=False)
    return T


def heterogeneity(out: Path, cond: str = "P3a") -> pd.DataFrame:
    """Does the synthetic answer move with persona attributes? (Direction only; no human micro-data.)"""
    df = pd.read_csv(out / "scored.csv")
    tw = pd.read_csv(out / "twins.csv").set_index("resp_id")
    g = df[(df.cond == cond) & (df["round"] == 1) & (df["var"].isin([OVERALL_FAV, OVERALL_REC]))].copy()
    g["score"] = np.where(g["mode"] == "ssr", g[[f"p{k}" for k in range(1, 6)]].to_numpy() @ np.arange(1, 6), g["dlr"])
    for c in ("korea_awareness", "age_band", "sex"):
        g[c] = tw.loc[g.resp_id, c].to_numpy()
    rows = []
    for (var, mode), gv in g.groupby(["var", "mode"]):
        for c in ("korea_awareness", "age_band", "sex"):
            means = gv.groupby(c)["score"].mean().round(2).to_dict()
            rows.append({"var": var, "mode": mode, "attribute": c, "mean_by_level": means,
                         "spearman_rho": round(float(gv[[c, "score"]].corr("spearman").iloc[0, 1]), 2)})
    H = pd.DataFrame(rows)
    H.to_csv(out / "heterogeneity.csv", index=False)
    return H
