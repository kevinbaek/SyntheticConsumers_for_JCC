"""Persona networks and social-exposure rounds.

Artificial Societies describes linking grounded personas into an influence network but has not
published how edges are formed or how opinions propagate. We therefore operationalise the idea
transparently and test it as a hypothesis:

* Edges: within-country homophily -- each twin is linked to its k most similar twins on the
  persona feature set (never on outcomes). Homophily is the best-documented tie-formation regularity
  (McPherson et al., 2001) and emerges spontaneously in LLM agent populations (He et al., 2024).
* Controls: (a) "self"   -- second round with a reflection prompt but no neighbours,
            (b) "random" -- k random same-country neighbours (same out-degree).
  Gains of "homophily" over both controls are attributable to *who* one hears from, not to the
  extra round or extra tokens.
* Exposure: one round, Friedkin-Johnsen style anchoring -- the twin sees neighbours' round-1
  free-text answers and is told it may keep or change its own view (no forced consensus, which
  would shrink variance).
* Leakage: neighbours' statements are *synthetic* round-1 outputs, never human answers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .codebook import DOMAINS, HISTORY_ATTITUDE

FEATURE_SETS = {
    "P2": ["sex", "age", "marital", "occupation", "education", "income"],
    "P3": ["sex", "age", "marital", "occupation", "education", "income", "korea_awareness"]
          + [f"exp_{d}" for d in DOMAINS],
    "P4": ["sex", "age", "marital", "occupation", "education", "income", "korea_awareness"]
          + [f"exp_{d}" for d in DOMAINS] + HISTORY_ATTITUDE,
}
CATEGORICAL = {"sex", "marital", "occupation", "education"}


def feature_matrix(df: pd.DataFrame, feature_set: str = "P4") -> np.ndarray:
    cols = [c for c in FEATURE_SETS[feature_set] if c in df]
    parts = []
    for c in cols:
        x = df[c]
        if c in CATEGORICAL:
            parts.append(pd.get_dummies(x.astype("category"), prefix=c).to_numpy(float))
        else:
            v = x.astype(float).to_numpy()
            v = np.where(np.isnan(v), np.nanmean(v) if np.isfinite(np.nanmean(v)) else 0.0, v)
            sd = v.std()
            parts.append(((v - v.mean()) / (sd if sd > 0 else 1.0))[:, None])
    X = np.hstack(parts) if parts else np.zeros((len(df), 1))
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms == 0, 1, norms)


def build_network(df: pd.DataFrame, kind: str, k: int, seed: int,
                  feature_set: str = "P4") -> dict[str, list[str]]:
    """Return {resp_id: [neighbour resp_ids]} within country. kind: homophily | random."""
    rng = np.random.default_rng(seed)
    nbrs: dict[str, list[str]] = {}
    for _, g in df.groupby("country"):
        ids = g["resp_id"].astype(str).to_numpy()
        kk = min(k, len(ids) - 1)
        if kk <= 0:
            for i in ids:
                nbrs[i] = []
            continue
        if kind == "homophily":
            X = feature_matrix(g, feature_set)
            S = X @ X.T
            np.fill_diagonal(S, -np.inf)
            # random tie-break so identical profiles do not always pick the same neighbours
            S = S + rng.uniform(0, 1e-9, S.shape)
            idx = np.argsort(-S, axis=1)[:, :kk]
        elif kind == "random":
            idx = np.array([rng.choice(np.delete(np.arange(len(ids)), i), kk, replace=False)
                            for i in range(len(ids))])
        else:
            raise ValueError(kind)
        for i, row in enumerate(idx):
            nbrs[ids[i]] = [ids[j] for j in row]
    return nbrs


def homophily_diagnostic(df: pd.DataFrame, nbrs: dict[str, list[str]], feature_set: str = "P4") -> float:
    """Mean cosine similarity between twins and their neighbours (report for both network kinds)."""
    sims = []
    for _, g in df.groupby("country"):
        X = feature_matrix(g, feature_set)
        pos = {rid: i for i, rid in enumerate(g["resp_id"].astype(str))}
        for rid, nb in nbrs.items():
            if rid in pos:
                sims += [float(X[pos[rid]] @ X[pos[n]]) for n in nb if n in pos]
    return float(np.mean(sims)) if sims else float("nan")


SELF_PROMPT = ("Before you finish, take a moment to think again about this question: \"{question}\" "
               "You answered earlier: \"{own}\". Answer the question again in your own words. You may keep "
               "or change your view.")
EXPOSURE_PROMPT = ("Before you finish, here is what some people you know in your daily life said about the "
                   "question \"{question}\":\n{statements}\nYou answered earlier: \"{own}\". "
                   "Answer the question again in your own words. People differ, so keep your own view unless "
                   "what you heard genuinely changes it.")


def exposure_prompt(kind: str, question: str, own: str, neighbour_texts: list[str]) -> str:
    if kind == "self":
        return SELF_PROMPT.format(question=question, own=own)
    stmts = "\n".join(f"- Someone you know: \"{t}\"" for t in neighbour_texts)
    return EXPOSURE_PROMPT.format(question=question, statements=stmts, own=own)
