"""Non-LLM and persona-free baselines. Every LLM condition is compared with all of them.

B0 uniform            p = 0.2 for every point
B1 carry-forward      wave-14 weighted country distribution of the same item (27 common countries)
B2 persona-free LLM   the model is asked for the country's answer shares directly (no twins)
B3 ML                 multinomial logistic model trained on wave 14 with the SAME persona features
                      the twins see (P4 feature set), applied to wave-15 twins
B4 neighbours         leave-one-out mean of same-continent countries in wave 15 (an upper-bound-ish
                      baseline: it uses other countries' wave-15 answers)
"""

from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from .metrics import wdist
from .network import FEATURE_SETS


def b0(twins: pd.DataFrame, var: str) -> pd.DataFrame:
    return pd.DataFrame(0.2, index=twins.index, columns=[f"p{k}" for k in range(1, 6)])


def b1(twins: pd.DataFrame, var: str, wave14: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for c, g in wave14.groupby("country"):
        if var in g:
            rows[c] = wdist(g[var].to_numpy(float), g["weight"].to_numpy(float))
    P = np.vstack([rows.get(c, np.full(5, np.nan)) for c in twins["country"]])
    return pd.DataFrame(P, index=twins.index, columns=[f"p{k}" for k in range(1, 6)])


def b4(twins: pd.DataFrame, var: str, wave15: pd.DataFrame) -> pd.DataFrame:
    dist = {c: wdist(g[var].to_numpy(float), g["weight"].to_numpy(float)) for c, g in wave15.groupby("country")}
    cont = wave15.groupby("country")["continent"].first()
    out = {}
    for c in dist:
        peers = [dist[o] for o in dist if o != c and cont[o] == cont[c] and not np.isnan(dist[o]).any()]
        out[c] = np.mean(peers, axis=0) if peers else np.full(5, np.nan)
    P = np.vstack([out.get(c, np.full(5, np.nan)) for c in twins["country"]])
    return pd.DataFrame(P, index=twins.index, columns=[f"p{k}" for k in range(1, 6)])


def _X(df: pd.DataFrame, cols: list[str], ref: pd.DataFrame | None = None) -> pd.DataFrame:
    X = pd.get_dummies(df[cols + ["country"]].astype({"country": "category"}), columns=["country"] +
                       [c for c in ("sex", "marital", "occupation", "education") if c in cols], dtype=float)
    X = X.fillna(X.mean(numeric_only=True)).fillna(0)
    if ref is not None:
        X = X.reindex(columns=ref.columns, fill_value=0.0)
    return X


def b3(twins: pd.DataFrame, var: str, wave14: pd.DataFrame, feature_set: str = "P4", seed: int = 0) -> pd.DataFrame:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    cols = [c for c in FEATURE_SETS[feature_set] if c in wave14 and c in twins]
    tr = wave14.dropna(subset=[var])
    if tr.empty:
        return pd.DataFrame(np.nan, index=twins.index, columns=[f"p{k}" for k in range(1, 6)])
    Xtr = _X(tr, cols)
    Xte = _X(twins, cols, ref=Xtr)
    sc = StandardScaler().fit(Xtr)
    y = tr[var].astype(int).to_numpy()
    clf = LogisticRegression(max_iter=2000, C=1.0, random_state=seed)
    clf.fit(sc.transform(Xtr), y, sample_weight=tr["weight"].to_numpy(float))
    proba = clf.predict_proba(sc.transform(Xte))
    P = np.zeros((len(twins), 5))
    for j, k in enumerate(clf.classes_):
        P[:, int(k) - 1] = proba[:, j]
    return pd.DataFrame(P, index=twins.index, columns=[f"p{k}" for k in range(1, 6)])


B2_PROMPT = ("Consider adults aged 15-59 in {country} who have used Korean cultural content. In an online survey "
             "they were asked: \"{question}\" with options:\n{options}\nEstimate the percentage of adults choosing "
             "each option. Reply with JSON only, keys \"1\"..\"5\", values summing to 100.")


def b2_messages(country: str, item) -> list[dict]:
    opts = "\n".join(f"{i + 1}. {lab}" for i, lab in enumerate(item.scale.labels))
    return [{"role": "user", "content": B2_PROMPT.format(country=country, question=item.text, options=opts)}]


def parse_b2(text: str) -> np.ndarray:
    m = re.search(r"\{.*\}", text or "", flags=re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
        v = np.array([float(d.get(str(k), np.nan)) for k in range(1, 6)])
        return v / np.nansum(v)
    except (ValueError, AttributeError):
        return np.full(5, np.nan)
