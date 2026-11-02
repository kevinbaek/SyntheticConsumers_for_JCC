"""Synthetic microdata with the same variable names and survey flow as the KOFICE raw file.

Used only for dry runs and tests before the real raw data arrive. Numbers are invented;
never report anything computed from this file.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..codebook import (COUNTRIES, DOMAINS, HISTORY_ATTITUDE, OVERALL_FAV, OVERALL_REC,
                        RESP_ID, WAVE14_COUNTRIES, WAVE15_N, WEIGHT)

# Rough country affinity (latent, invented) so that rankings are non-trivial.
_AFFINITY = {
    "Philippines": 1.3, "India": 1.1, "Indonesia": 1.1, "Thailand": 0.9, "Mexico": 0.9, "UAE": 0.8,
    "Malaysia": 0.8, "Vietnam": 0.8, "Brazil": 0.7, "South Africa": 0.7, "United States": 0.6,
    "Saudi Arabia": 0.6, "Egypt": 0.5, "United Kingdom": 0.5, "Taiwan": 0.5, "Singapore": 0.5,
    "Chile": 0.4, "Australia": 0.3, "China": 0.3, "Turkiye": 0.2, "Argentina": 0.1, "Spain": 0.1,
    "Canada": 0.0, "France": -0.2, "Italy": -0.3, "Poland": -0.4, "Germany": -0.4, "Japan": -0.5,
    "Kazakhstan": -0.5, "Russia": -0.8, "Hong Kong": 0.4,
}
_DOMAIN_BASE = {"drama": 0.4, "variety": -0.2, "movie": 0.6, "music": 0.3, "animation": -0.1,
                "publication": -0.8, "webtoon": -0.6, "game": -0.3, "fashion": 0.1, "beauty": 0.2, "food": 0.7}
_CUTS = np.array([-2.2, -1.2, 0.1, 1.6])   # ordinal thresholds for 5-point items


def _ordinal(latent: np.ndarray, rng: np.random.Generator, noise: float = 0.9) -> np.ndarray:
    z = latent + rng.normal(0, noise, size=latent.shape)
    return 1 + (z[:, None] > _CUTS[None, :]).sum(axis=1)


def make_wave(wave: int, scale: float = 0.1, seed: int = 0) -> pd.DataFrame:
    """Generate one wave in raw KOFICE variable naming (numeric codes)."""
    rng = np.random.default_rng(seed + wave)
    countries = COUNTRIES if wave == 15 else WAVE14_COUNTRIES
    code_of = {c: i + 1 for i, c in enumerate(COUNTRIES)} | {"Hong Kong": 31}
    drift = 0.0 if wave == 15 else -0.05
    rows = []
    for c in countries:
        n = max(40, int(round(WAVE15_N.get(c, 700) * scale)))
        mu = _AFFINITY[c] + drift + rng.normal(0, 0.05)
        sex = rng.integers(1, 3, n)
        band = rng.choice([1, 2, 3, 4, 5], n, p=[0.25, 0.25, 0.25, 0.125, 0.125])
        age = np.array([rng.integers(*{1: (15, 20), 2: (20, 30), 3: (30, 40), 4: (40, 50), 5: (50, 60)}[b]) for b in band])
        aware = rng.choice([1, 2, 3], n, p=[0.28, 0.57, 0.15])
        trait = rng.normal(0, 0.7, n)                 # individual Hallyu affinity
        latent = mu + trait + 0.35 * (2 - aware) - 0.12 * (band - 3) + 0.1 * (sex == 2)
        df = pd.DataFrame({
            RESP_ID: [f"w{wave}_{code_of[c]:02d}_{i:04d}" for i in range(n)],
            "SQ1AA": code_of[c], "SQ1AB": rng.integers(1, 5, n), "SQ1B": 1,
            "SQ2": sex, "SQ3": age, "SQ3A": band, "SQ4B": aware,
            "DDQ1": rng.integers(1, 4, n), "DDQ2": rng.integers(1, 11, n), "DDQ3": rng.integers(1, 5, n),
            "DDQ4": rng.integers(1, 6, n), "DDQ6": rng.integers(1, 7, n),
        })
        answered_lists = []
        exp_mat = {}
        for dom, d in DOMAINS.items():
            p = 1 / (1 + np.exp(-(-0.4 + latent + _DOMAIN_BASE[dom]
                                  + (0.4 * (sex == 2) if dom in ("beauty", "drama") else 0)
                                  + (0.4 * (sex == 1) if dom == "game" else 0))))
            exp = rng.random(n) < p
            exp_mat[dom] = exp
            df[d["exp"]] = np.where(exp, 1, 2)
            df[f"SQ6A_{list(DOMAINS).index(dom) + 1}"] = np.where(exp & (rng.random(n) < 0.8), 1, 2)
        exp_any = np.column_stack(list(exp_mat.values()))
        # ensure every respondent has >= 1 experienced domain (screening criterion)
        none = ~exp_any.any(axis=1)
        exp_any[none, list(DOMAINS).index("food")] = True
        df.loc[none, DOMAINS["food"]["exp"]] = 1
        for i in range(n):
            doms = [d for j, d in enumerate(DOMAINS) if exp_any[i, j]]
            if len(doms) > 6:
                doms = list(rng.choice(doms, 6, replace=False))
            answered_lists.append(doms)
        df["SQ6C"] = np.clip(np.round(3 + latent + rng.normal(0, 1, n)), 1, 5)
        for j, var in enumerate(HISTORY_ATTITUDE):
            df[var] = _ordinal(latent * 0.9 + (0.2 if j in (2, 4) else 0), rng, noise=1.0)
        for dom, d in DOMAINS.items():
            fav = _ordinal(latent + _DOMAIN_BASE[dom] * 0.5, rng)
            rec = np.clip(fav + rng.choice([-1, 0, 0, 0, 1], n), 1, 5)
            mask = np.array([dom in a for a in answered_lists])
            df[d["fav"]] = np.where(mask, fav, np.nan)
            df[d["rec"]] = np.where(mask, rec, np.nan)
            pop_latent = mu * 1.2 + _DOMAIN_BASE[dom] + 0.3 * trait
            df[d["pop"]] = _ordinal(pop_latent, rng, noise=1.0)
        df[OVERALL_FAV] = _ordinal(latent + 0.3, rng)
        df[OVERALL_REC] = np.clip(df[OVERALL_FAV] + rng.choice([-1, 0, 0, 0, 1], n), 1, 5)
        df[WEIGHT] = rng.uniform(0.7, 1.3, n)
        rows.append(df)
    out = pd.concat(rows, ignore_index=True)
    # sprinkle "don't know" style missing codes to exercise recoding
    out.loc[out.sample(frac=0.003, random_state=seed).index, OVERALL_REC] = 99
    return out
