"""Stratified twin samples (per country, proportional to sex x age-band cells)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def stratified_sample(df: pd.DataFrame, n_per_country: int, seed: int,
                      strata: tuple[str, ...] = ("sex", "age_band")) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    parts = []
    for country, g in df.groupby("country", sort=True):
        n = min(n_per_country, len(g))
        cells = g.groupby(list(strata), dropna=False)
        alloc = (cells.size() / len(g) * n)
        base = np.floor(alloc).astype(int)
        rem = n - base.sum()
        if rem > 0:  # largest remainders
            order = (alloc - base).sort_values(ascending=False).index[:rem]
            base.loc[order] += 1
        for key, k in base.items():
            cell = cells.get_group(key if isinstance(key, tuple) else (key,))
            if k > 0:
                idx = rng.choice(cell.index.to_numpy(), size=min(k, len(cell)), replace=False)
                parts.append(df.loc[idx])
    return pd.concat(parts).sort_values(["country", "resp_id"]).reset_index(drop=True)


def subsample(df: pd.DataFrame, n_per_country: int, seed: int) -> pd.DataFrame:
    """Nested subsample used for ablations (subset of the main twin sample)."""
    idx = [i for _, g in df.groupby("country", sort=True)
           for i in g.sample(min(n_per_country, len(g)), random_state=seed).index]
    return df.loc[idx].reset_index(drop=True)
