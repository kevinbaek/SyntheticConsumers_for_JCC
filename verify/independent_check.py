"""Independent re-computation of the headline numbers from the raw API responses.

Deliberately does NOT use hallyu_twins.pilot / multicountry.expand / table_eval / analysis_table.
Only the frozen design inputs are shared (anchor statements, item wording, transcribed targets) and
the embedding cache (same vectors). Re-implements: JSON parsing, reverse-scale mapping, SSR (Maier
min-subtraction), country T2B, MAE, 1-MAE, Spearman, binary JS similarity.

  python verify/independent_check.py outputs/mc_claude-sonnet-5 outputs/analysis_table/estimates.csv
Exit code 1 if any difference exceeds 1e-3 percentage points (stored embeddings are rounded to
6 decimals and re-normalised here, which moves T2B by less than 1e-4 pp).
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hallyu_twins.codebook import ITEMS  # noqa: E402  (item wording + scale labels only)
from hallyu_twins.elicit import anchor_texts  # noqa: E402  (frozen anchor statements only)
from hallyu_twins.embed import default_cache, make_embedder  # noqa: E402  (same cached vectors)

VARS = [f"XQ1_{i}" for i in range(1, 14)] + ["XQ5", "XQ6"]
QID = {f"Q{i + 1:02d}": v for i, v in enumerate(VARS)}


PAIR = re.compile(r'"\s*(Q\d{2})\s*"\s*:\s*(?:"((?:[^"\\]|\\.)*)"|(\d+(?:\.\d+)?))', flags=re.S)


def parse(text):
    """Own tolerant parser: JSON (control characters allowed), else every "Qnn": value pair found in the text."""
    m = re.search(r"\{.*\}", text or "", flags=re.S)
    if m:
        try:
            return {k.strip().upper(): v for k, v in json.loads(m.group(0), strict=False).items()}
        except Exception:
            pass
    return {q.upper(): (s if s is not None else num) for q, s, num in PAIR.findall(text or "")
            if (s or num) not in (None, "")}


def ssr(texts, var, emb):
    R = emb.embed(texts)
    R = R / np.linalg.norm(R, axis=1, keepdims=True)
    acc = np.zeros((len(texts), 5))
    sets = anchor_texts(ITEMS[var])
    for s in sets:
        A = emb.embed(s)
        A = A / np.linalg.norm(A, axis=1, keepdims=True)
        S = R @ A.T
        W = S - S.min(axis=1, keepdims=True) + 1e-12
        acc += W / W.sum(axis=1, keepdims=True)
    return acc / len(sets)


def main(run_dir, est_csv, embedding="openai"):
    run = Path(run_dir)
    emb = make_embedder({"provider": embedding}, default_cache(str(ROOT / "outputs/cache")))
    twdf = pd.read_csv(run / "twins.csv").set_index("resp_id")
    tw = twdf["country"]
    raw = [json.loads(line) for line in open(run / "raw_r1.jsonl")]
    rows = []
    for r in raw:
        cond, rid, mode, _ = r["call_id"].split("|")
        if cond != "P3a":
            continue
        d = parse(r["text"])
        rev = bool(twdf.at[rid, "reverse"]) and mode == "dlr"   # design: balanced random half per country
        for q, v in QID.items():
            if q in d:
                rows.append({"rid": rid, "country": tw[rid], "mode": mode, "var": v, "ans": str(d[q]), "rev": rev})
    D = pd.DataFrame(rows)
    out = []
    for (mode, var), g in D.groupby(["mode", "var"]):
        if mode == "dlr":
            num = g["ans"].str.extract(r"\b([1-5])\b")[0].astype(float)
            num = np.where(g["rev"], 6 - num, num)
            t2b = pd.Series(np.where(np.isnan(num), np.nan, (num >= 4).astype(float)), index=g.index)
        else:
            P = ssr(g["ans"].tolist(), var, emb)
            t2b = pd.Series(P[:, 3] + P[:, 4], index=g.index)
        out.append(g.assign(t2b=100 * t2b))
    D = pd.concat(out)
    C = D.groupby(["country", "mode", "var"])["t2b"].mean().reset_index()
    pop = C[C["var"].str.startswith("XQ1_")].groupby(["country", "mode"])["t2b"].mean().reset_index().assign(var="POPMEAN")
    C = pd.concat([C[C["var"].isin(["XQ5", "XQ6"])], pop])
    C["method"] = C["mode"].map({"dlr": "Twins DLR", "ssr": "Twins SSR"})
    # compare with the package's estimates
    E = pd.read_csv(est_csv)
    model = json.load(open(run / "run_meta.json"))["model"]
    E = E[(E.model == model) & E.cond.isin(["Twins DLR", "Twins SSR"])]
    M = C.merge(E, left_on=["country", "method", "var"], right_on=["country", "cond", "var"], how="outer", indicator=True)
    maxdiff = float(np.nanmax(np.abs(M.t2b - M.est)))
    print(f"[{model}] country estimates compared: {len(M)}, unmatched: {(M._merge != 'both').sum()}, max |diff| = {maxdiff:.2e}")
    # headline metrics recomputed by hand
    T = pd.read_csv(ROOT / "data/pdf_tables/targets_country.csv")
    T = T[(T.wave == 15) & (T.stat == "t2b") & (T.country != "ALL30")]
    res = []
    for (meth, var), g in C.groupby(["method", "var"]):
        h = T[T["var"] == var].set_index("country")["value"]
        e = g.set_index("country")["t2b"]
        ix = h.index.intersection(e.index)
        err = e[ix] - h[ix]
        p, q = e[ix].to_numpy() / 100, h[ix].to_numpy() / 100
        ent = lambda x: -(np.clip(x, 1e-12, 1) * np.log2(np.clip(x, 1e-12, 1)) + np.clip(1 - x, 1e-12, 1) * np.log2(np.clip(1 - x, 1e-12, 1)))
        js = 1 - (ent((p + q) / 2) - (ent(p) + ent(q)) / 2)
        res.append({"model": model, "method": meth, "var": var, "n": len(ix), "MAE_pp": float(np.mean(np.abs(err))),
                    "one_minus_MAE": 1 - float(np.mean(np.abs(err))) / 100, "JS_sim": float(np.mean(js)),
                    "spearman": float(spearmanr(e[ix], h[ix])[0]), "bias_pp": float(np.mean(err))})
    R = pd.DataFrame(res)
    return maxdiff, R


if __name__ == "__main__":
    est = sys.argv[-1]
    worst = 0.0
    allR = []
    for rd in sys.argv[1:-1]:
        d, R = main(rd, est)
        worst = max(worst, d)
        allR.append(R)
    R = pd.concat(allR)
    R.to_csv(ROOT / "verify/independent_metrics.csv", index=False)
    pd.set_option("display.width", 200)
    print(R.round(4).to_string())
    print(f"worst |diff| over models: {worst:.2e} pp")
    sys.exit(0 if worst < 1e-3 else 1)
