"""Table-only mode: targets and persona marginals transcribed from the published report.

Until the raw microdata arrive, the only ground truth is what the summary report prints:
country-level top-2-box shares for a subset of countries (top/bottom 7 lists) and the
respondent-profile table (each country's share of every demographic cell). From the latter we
recover within-country marginals and synthesise personas that match them.

Limitations (state them in the paper): joint distributions are unknown (cells are sampled
independently, with simple plausibility rules); no individual-level grounding (P4) is possible,
so table-only mode can test P1-P3 personas and country-level accuracy only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

TABLE_DIR = Path(__file__).resolve().parent.parent / "data" / "pdf_tables"

AGE_RANGE = {1: (15, 19), 2: (20, 29), 3: (30, 39), 4: (40, 49), 5: (50, 59)}


def load_targets(path: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(path or TABLE_DIR / "targets_country.csv")


def country_targets(country: str, wave: int = 15) -> dict[str, float]:
    t = load_targets()
    t = t[(t.country == country) & (t.wave == wave) & (t.stat == "t2b")]
    return dict(zip(t["var"], t["value"]))


def carry_forward(country: str) -> dict[str, float]:
    """Wave-14 value implied by the wave-15 value and the printed change (B1 baseline)."""
    t = load_targets()
    now = t[(t.country == country) & (t.wave == 15) & (t.stat == "t2b")].set_index("var")["value"]
    d = t[(t.country == country) & (t.wave == 14) & (t.stat == "t2b_delta")].set_index("var")["value"]
    return {v: round(float(now[v] - d[v]), 1) for v in d.index if v in now.index}


def global_mean() -> dict[str, float]:
    t = load_targets()
    t = t[(t.country == "ALL30") & (t.wave == 15) & (t.stat == "t2b")]
    out = dict(zip(t["var"], t["value"]))
    pops = [v for k, v in out.items() if k.startswith("XQ1_")]
    if pops:
        out["POPMEAN"] = round(float(np.mean(pops)), 1)
    return out


def marginals(country: str, path: Path | None = None) -> dict[str, pd.Series]:
    """Within-country category shares from the respondent-profile table (row % x row total)."""
    df = pd.read_csv(path or TABLE_DIR / "respondent_profile.csv")
    if country not in df.columns:
        raise KeyError(f"{country} not transcribed yet in respondent_profile.csv")
    df["count"] = df["row_total"] * df[country] / 100.0
    out = {}
    for dim, g in df[df.dimension != "total"].groupby("dimension", sort=False):
        s = g.set_index("code")["count"]
        out[dim] = s / s.sum()
    return out


def _allowed(band: int, occ: int, edu: int, mar: int) -> bool:
    """Structural zeros for the joint table (band-level plausibility rules)."""
    if occ == 1 and (band != 1 or edu != 1):         # middle/high-school student
        return False
    if occ == 2 and band > 3:                        # university / graduate student
        return False
    if band == 1 and (edu == 3 or mar == 1 or occ in (5, 7, 8)):
        return False
    return True


def joint_table(country: str, iters: int = 200) -> pd.DataFrame:
    """IPF (raking) of band x occupation x education x marital to the printed marginals,
    starting from a seed that is 1 where the combination is plausible and 0 otherwise."""
    m = marginals(country)
    dims = ["age_band", "occupation", "education", "marital"]
    cats = [list(m[d].index) for d in dims]
    idx = pd.MultiIndex.from_product(cats, names=dims)
    w = np.array([1.0 if _allowed(*k) else 0.0 for k in idx])
    for _ in range(iters):
        for d in dims:
            cur = pd.Series(w, index=idx).groupby(level=d).sum()
            f = (m[d] / cur.replace(0, np.nan)).fillna(0)
            w = w * f.reindex(idx.get_level_values(d)).to_numpy()
    w = w / w.sum()
    return pd.DataFrame({"p": w}, index=idx).query("p > 0")


def _code(country: str) -> str:
    from .codebook import COUNTRIES
    j = COUNTRIES.index(country) + 1 if country in COUNTRIES else 99
    return f"{j:02d}{country[:3].upper()}"          # unique even for United States / United Kingdom


def synthesize(country: str, n: int, seed: int) -> pd.DataFrame:
    """Personas drawn from the raked joint table by systematic sampling (close to the printed
    marginals even at small n); sex alternates (quota 50/50), awareness drawn from its marginal."""
    m = marginals(country)
    J = joint_table(country)
    from .codebook import COUNTRIES
    cidx = COUNTRIES.index(country) if country in COUNTRIES else 99
    rng = np.random.default_rng([seed, cidx])            # independent stream per country
    # exact age-band quota (largest remainder), then systematic sampling within band
    share = m["age_band"].sort_index()
    alloc = np.floor(share * n).astype(int)
    rem = n - alloc.sum()
    alloc[(share * n - alloc).sort_values(ascending=False).index[:rem]] += 1
    cells = []
    for band, k in alloc.items():
        if k == 0:
            continue
        Jb = J.xs(band, level="age_band", drop_level=False).sample(frac=1.0, random_state=int(rng.integers(2**31)))
        cum = (Jb["p"] / Jb["p"].sum()).cumsum().to_numpy()
        picks = np.searchsorted(cum, (rng.random() + np.arange(k)) / k)
        cells += [Jb.index[min(i, len(Jb) - 1)] for i in picks]
    cells = [cells[i] for i in rng.permutation(len(cells))]
    nat = m["nationality"]
    nat_draw = rng.choice(nat.index.to_numpy(), size=n, p=nat.to_numpy())
    aw = m["korea_awareness"]
    aw_cum = aw.cumsum().to_numpy()
    aw_draw = aw.index.to_numpy()[np.searchsorted(aw_cum, (rng.random() + np.arange(n)) / n)]
    aw_draw = rng.permutation(aw_draw)
    sexes = rng.permutation(np.resize([1, 2], n))
    rows = []
    for i, (band, occ, edu, mar) in enumerate(cells):
        lo, hi = AGE_RANGE[int(band)]
        if occ == 1:
            lo, hi = 15, 18
        elif occ == 2 and band == 1:
            lo, hi = 18, 19
        elif band == 1 and edu == 2:
            lo, hi = 19, 19
        age = int(rng.integers(lo, hi + 1))
        rows.append({"resp_id": f"{_code(country)}-{seed % 1000:03d}-{i:03d}", "wave": 15,
                     "country": country, "weight": 1.0, "sex": int(sexes[i]), "age": age,
                     "age_band": int(band), "occupation": int(occ), "education": int(edu), "marital": int(mar),
                     "korea_awareness": int(aw_draw[i]), "nationality": int(nat_draw[i])})
    out = pd.DataFrame(rows)
    # option-order arm: exactly half of the country's twins (random, seeded) see reversed DLR options
    rev = np.resize([0, 1], n)
    out["reverse"] = rng.permutation(rev).astype(bool)
    return out


def marginal_check(df: pd.DataFrame, country: str) -> pd.DataFrame:
    """Target vs achieved marginals (report in the appendix)."""
    m = marginals(country)
    rows = []
    for dim, s in m.items():
        if dim not in df:
            continue
        got = df[dim].value_counts(normalize=True)
        for code, p in s.items():
            rows.append({"dimension": dim, "code": code, "target": round(100 * p, 1),
                         "achieved": round(100 * float(got.get(code, 0.0)), 1)})
    return pd.DataFrame(rows)
