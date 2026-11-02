"""Load KOFICE raw microdata into one tidy respondent table.

Accepted inputs: .sav (SPSS, needs pyreadstat), .csv, .xlsx, .parquet. Column names must
follow the KOFICE variable guide (see codebook.py).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..codebook import (ALL_TARGETS, CONTINENT, DEMOGRAPHICS, DOMAINS, HISTORY_ATTITUDE,
                        HISTORY_BEHAVIOR, KOREA_AWARENESS, RESP_ID, WEIGHT, ValueCodes)


def read_raw(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if p.suffix == ".sav":
        import pyreadstat  # optional dependency
        df, _meta = pyreadstat.read_sav(str(p))
        return df
    if p.suffix == ".csv":
        return pd.read_csv(p)
    if p.suffix in (".xlsx", ".xls"):
        return pd.read_excel(p)
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    raise ValueError(f"Unsupported file type: {p}")


def tidy(raw: pd.DataFrame, wave: int, country_codes: dict[int, str],
         codes: ValueCodes | None = None) -> pd.DataFrame:
    """Rename/recode raw columns. Keeps raw outcome/history variable names as columns."""
    codes = codes or ValueCodes()
    df = raw.copy()
    keep = set(ALL_TARGETS) | set(HISTORY_BEHAVIOR) | set(HISTORY_ATTITUDE) | set(DEMOGRAPHICS.values()) \
        | {KOREA_AWARENESS, RESP_ID, WEIGHT}
    missing_cols = [c for c in keep if c not in df.columns]
    if RESP_ID in df and df[RESP_ID].duplicated().any():
        raise ValueError(f"wave {wave}: duplicated respondent ids in {RESP_ID}")
    if missing_cols:
        # history/target columns may legitimately be absent in older waves; warn loudly
        print(f"[loader] wave {wave}: {len(missing_cols)} expected columns absent, e.g. {missing_cols[:5]}")
    df = df[[c for c in df.columns if c in keep]].copy()
    num = df.select_dtypes(include=[np.number]).columns
    df[num] = df[num].mask(df[num].isin(codes.missing))
    out = pd.DataFrame({
        "resp_id": df[RESP_ID].astype(str),
        "wave": wave,
        "country": df[DEMOGRAPHICS["country"]].map(lambda v: country_codes.get(int(v)) if pd.notna(v) else None),
        "weight": df[WEIGHT] if WEIGHT in df else 1.0,
    })
    if out["country"].isna().any():
        bad = sorted(df.loc[out["country"].isna(), DEMOGRAPHICS["country"]].dropna().unique())
        raise ValueError(f"Unmapped country codes {bad}; set country_codes in the config.")
    out["continent"] = out["country"].map(CONTINENT)
    for key, var in DEMOGRAPHICS.items():
        if key != "country" and var in df:
            out[key] = df[var].values
    out["sex_label"] = out.get("sex").map(codes.sex) if "sex" in out else None
    out["age_band_label"] = out.get("age_band").map(codes.age_band) if "age_band" in out else None
    if KOREA_AWARENESS in df:
        out["korea_awareness"] = df[KOREA_AWARENESS].values
    for dom, d in DOMAINS.items():
        out[f"exp_{dom}"] = (df[d["exp"]] == codes.experience_yes).astype(int).values if d["exp"] in df else np.nan
    for var in HISTORY_BEHAVIOR + HISTORY_ATTITUDE + ALL_TARGETS:
        if var in df and var not in out:
            out[var] = df[var].values
    # skip-logic: which domain blocks did the respondent actually answer (<= 6)?
    fav_vars = {dom: d["fav"] for dom, d in DOMAINS.items()}
    out["answered_domains"] = [
        [dom for dom, v in fav_vars.items() if v in out and pd.notna(row[v])]
        for _, row in out.iterrows()
    ]
    too_many = out["answered_domains"].map(len).gt(6).sum()
    if too_many:
        print(f"[loader] warning: {too_many} respondents answered >6 domain blocks; check skip logic")
    return out.reset_index(drop=True)


def load_wave(path: str | Path, wave: int, country_codes: dict[int, str]) -> pd.DataFrame:
    return tidy(read_raw(path), wave, country_codes)
