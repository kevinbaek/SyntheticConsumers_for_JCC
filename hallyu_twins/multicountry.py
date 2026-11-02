"""Table-only multi-country test: 30 countries x models x {SSR, DLR} x persona network.

Questionnaire mode: one call per twin per mode returns all 15 target items as JSON (XQ1_1..13
popularity, XQ5, XQ6), which is ~15x cheaper than one call per item and mirrors a respondent
filling in one questionnaire. Round 2 re-asks every item after a network exposure:
  N1 self      reflection only (no neighbours)          -> controls for the extra round
  N2 random    k random same-country twins' answers      -> controls for "hearing anyone"
  N3 homophily k most similar same-country twins         -> the treatment
Outputs are expanded to one row per (twin, item) in the same files pilot.score() reads.
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .codebook import COUNTRIES, ITEMS, OVERALL_FAV, OVERALL_REC, TARGETS_POP_15, WAVE15_N
from .elicit import SYSTEM, SSRScorer, options_text, parse_dlr
from .jobs import job_id, read_jsonl, write_jsonl
from .network import build_network, homophily_diagnostic
from .personas import DISPLAY, build_persona
from .tables import carry_forward, global_mean, load_targets, synthesize

ITEMS15 = TARGETS_POP_15 + [OVERALL_FAV, OVERALL_REC]
QID = {v: f"Q{i + 1:02d}" for i, v in enumerate(ITEMS15)}
VAR = {q: v for v, q in QID.items()}

SSR_BATCH = ("Please answer each of the following survey questions as this person. For each question, answer in "
             "one or two sentences in your own words. Do not give numbers and do not quote answer options.\n\n"
             "{questions}\n\nReply with a JSON object only, mapping each question id (Q01...) to your answer.")
DLR_BATCH = ("Please answer each of the following survey questions as this person by choosing one option number.\n\n"
             "{questions}\n\nReply with a JSON object only, mapping each question id (Q01...) to the option number.")
NET_BATCH = ("Before you finish the survey, think again about the questions below. {context}\n\n{questions}\n\n"
             "Answer each question again in one or two sentences in your own words. People differ, so keep your own "
             "view unless what you heard genuinely changes it. Do not give numbers. Reply with a JSON object only, "
             "mapping each question id (Q01...) to your answer.")


def _qblock(mode: str, reverse: bool) -> str:
    out = []
    for v in ITEMS15:
        it = ITEMS[v]
        if mode == "dlr":
            out.append(f"{QID[v]}. {it.text}\n{options_text(it.scale, reverse)}")
        else:
            out.append(f"{QID[v]}. {it.text}")
    return "\n\n".join(out)


def _qkey(k) -> str | None:
    m = re.search(r"(\d+)", str(k))
    return f"Q{int(m.group(1)):02d}" if m and 1 <= int(m.group(1)) <= len(ITEMS15) else None


def parse_json(text: str) -> dict:
    """Question id -> answer. Keys are normalised ("Q 4", "q04", "Q POP04" -> "Q04"); if the JSON is
    malformed, well-formed "Qnn": value pairs are still recovered; empty or null answers are dropped."""
    out: dict[str, str] = {}
    m = re.search(r"\{.*\}", text or "", flags=re.S)
    d = None
    if m:
        try:
            d = json.loads(m.group(0), strict=False)       # tolerate raw newlines/tabs inside strings
        except json.JSONDecodeError:
            d = None
    if isinstance(d, dict):
        items = d.items()
    else:
        items = re.findall(r'"\s*(Q[^"]{0,8}?)\s*"\s*:\s*("(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?)', text or "")
        def _val(v):
            if not v.startswith('"'):
                return v
            try:
                return json.loads(v, strict=False)
            except json.JSONDecodeError:
                return v[1:-1]
        items = [(k, _val(v)) for k, v in items]
    for k, v in items:
        q = _qkey(k)
        if q is None or v is None or str(v).strip() == "":
            continue
        out[q] = str(v)
    return out


def prepare(out: Path, n_per_country: int, seed: int, countries=None) -> pd.DataFrame:
    out.mkdir(parents=True, exist_ok=True)
    tw = pd.concat([synthesize(c, n_per_country, seed) for c in (countries or COUNTRIES)], ignore_index=True)
    tw.to_csv(out / "twins.csv", index=False)
    return tw


def round1_calls(tw: pd.DataFrame) -> list[dict]:
    calls = []
    for _, row in tw.iterrows():
        p = build_persona(row, "P3")
        sys = SYSTEM.format(persona=p.text)
        rev = bool(row["reverse"])                     # balanced random assignment made in tables.synthesize
        for mode, tmpl in (("ssr", SSR_BATCH), ("dlr", DLR_BATCH)):
            calls.append({"call_id": f"P3a|{p.resp_id}|{mode}|r1", "cond": "P3a", "resp_id": p.resp_id, "mode": mode,
                          "round": 1, "reverse": rev and mode == "dlr", "country": row.country,
                          "messages": [{"role": "system", "content": sys},
                                       {"role": "user", "content": tmpl.format(questions=_qblock(mode, rev and mode == "dlr"))}]})
    return calls


def round2_calls(tw: pd.DataFrame, r1: dict[str, dict], k: int, seed: int, out: Path) -> list[dict]:
    nets = {"N2random": build_network(tw, "random", k, seed, "P3"),
            "N3homophily": build_network(tw, "homophily", k, seed, "P3")}
    json.dump({"k": k, "similarity": {n: homophily_diagnostic(tw, g, "P3") for n, g in nets.items()},
               "edges": nets}, open(out / "network.json", "w"), indent=1)
    calls = []
    for _, row in tw.iterrows():
        p = build_persona(row, "P3")
        own = r1.get(p.resp_id, {})
        if not own:
            continue                                   # nothing to reflect on; excluded from all network arms
        sys = SYSTEM.format(persona=p.text)
        for cond in ("N1self", "N2random", "N3homophily"):
            blocks = []
            for v in ITEMS15:
                q = QID[v]
                lines = [f"{q}. {ITEMS[v].text}", f"  You answered earlier: \"{own.get(q, '')}\""]
                if cond != "N1self":
                    for n in nets[cond].get(p.resp_id, []):
                        t = r1.get(n, {}).get(q)
                        if t:
                            lines.append(f"  Someone you know said: \"{t}\"")
                blocks.append("\n".join(lines))
            ctx = ("Take a moment to reflect on your earlier answers." if cond == "N1self" else
                   "Here is what some people you know in your daily life said about the same questions.")
            calls.append({"call_id": f"P3a+{cond}|{p.resp_id}|ssr|r2", "cond": f"P3a+{cond}", "resp_id": p.resp_id,
                          "mode": "ssr", "round": 2, "reverse": False, "country": row.country,
                          "messages": [{"role": "system", "content": sys},
                                       {"role": "user", "content": NET_BATCH.format(context=ctx, questions="\n\n".join(blocks))}]})
    return calls


B2_BATCH = ("Consider adults aged 15-59 living in {country} who have used Korean cultural content, surveyed online in "
            "late 2025. Estimate the percentage who would choose the top two options ('{top}') for each question "
            "below.\n\n{questions}\n\nReply with a JSON object only, mapping each question id (Q01...) to a percentage "
            "between 0 and 100. Do not look anything up.")


def b2_calls(reps: int = 1) -> list[dict]:
    qs = "\n".join(f"{QID[v]}. {ITEMS[v].text} (top two options: '{ITEMS[v].scale.labels[3]}' or "
                   f"'{ITEMS[v].scale.labels[4]}')" for v in ITEMS15)
    return [{"call_id": f"B2|{c}" + (f"|k{r}" if r else ""), "cond": "B2", "country": c, "rep": r,
             "messages": [{"role": "user", "content": B2_BATCH.format(country=DISPLAY.get(c, c), top="4 or 5",
                                                                     questions=qs)}]}
            for c in COUNTRIES for r in range(reps)]


def execute(calls: list[dict], llm, path: Path, workers: int) -> list[dict]:
    def one(c):
        try:
            t = llm.complete(c["messages"], rep=c.get("rep", 0), call_id=c["call_id"]).text
        except Exception as e:  # noqa: BLE001
            t = f"__ERROR__ {type(e).__name__}: {e}"
        return {"call_id": c["call_id"], "text": t}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(one, calls))
    write_jsonl(res, path)
    return res


def expand(calls: list[dict], res: list[dict], out: Path, rnd: int) -> tuple[list[dict], dict]:
    """Write per-item jobs/responses (pilot.score schema); return parsed answers by twin."""
    by = {r["call_id"]: parse_json(r["text"]) for r in res}
    jobs, resp, parsed = [], [], {}
    for c in calls:
        ans = by.get(c["call_id"], {})
        if c["mode"] == "ssr" and c["cond"] == "P3a":
            parsed[c["resp_id"]] = ans
        for v in ITEMS15:
            jid = job_id(c["cond"], c["resp_id"], v, c["mode"], rnd)
            jobs.append({"job_id": jid, "cond": c["cond"], "resp_id": c["resp_id"], "var": v, "mode": c["mode"],
                         "round": rnd, "reverse": c["reverse"], "country": c["country"]})
            if QID[v] in ans:
                resp.append({"job_id": jid, "text": ans[QID[v]]})
    write_jsonl(jobs, out / f"jobs_r{rnd}.jsonl")
    write_jsonl(resp, out / f"responses_r{rnd}.jsonl")
    return jobs, parsed


# ---------------------------------------------------------------------------------------
def country_table(scored: pd.DataFrame, tw: pd.DataFrame) -> pd.DataFrame:
    """country x cond x mode x var synthetic T2B (%)."""
    s = scored.copy()
    s["country"] = s.resp_id.map(tw.set_index("resp_id")["country"])
    s["t2b"] = np.where(s["mode"] == "ssr", s["p4"] + s["p5"], (s["dlr"] >= 4).astype(float).where(s["dlr"].notna()))
    T = s.groupby(["country", "cond", "mode", "var"])["t2b"].mean().mul(100).reset_index()
    pop = T[T["var"].isin(TARGETS_POP_15)].groupby(["country", "cond", "mode"])["t2b"].mean().reset_index()
    pop["var"] = "POPMEAN"
    return pd.concat([T, pop], ignore_index=True)


def evaluate(T: pd.DataFrame, b2: pd.DataFrame, out: Path) -> pd.DataFrame:
    tg = load_targets()
    tg15 = tg[(tg.wave == 15) & (tg.stat == "t2b") & (tg.country != "ALL30")]
    rows = []
    groups = [(c, m) for c, m in T[["cond", "mode"]].drop_duplicates().itertuples(index=False)] + [("B2", "direct")]
    for var in (OVERALL_FAV, OVERALL_REC, "POPMEAN"):
        truth = tg15[tg15["var"] == var].set_index("country")["value"]
        cf = {c: carry_forward(c).get(var) for c in truth.index}
        for cond, mode in groups:
            if cond == "B2":
                est = b2[b2["var"] == var].set_index("country")["t2b"]
            else:
                est = T[(T.cond == cond) & (T["mode"] == mode) & (T["var"] == var)].set_index("country")["t2b"]
            ix = truth.index.intersection(est.index)
            if len(ix) < 4:
                continue
            e, h = est[ix], truth[ix]
            top = set(h.sort_values(ascending=False).index[:7])
            pred_top = set(e.sort_values(ascending=False).index[:len(top)])
            # 30-country weighted mean vs the printed all-country value
            allc = est.reindex(COUNTRIES).dropna()
            wmean = float(np.average(allc, weights=[WAVE15_N[c] for c in allc.index])) if len(allc) else np.nan
            rows.append({"var": var, "cond": cond, "mode": mode, "n_countries": len(ix),
                         "MAE_pp": round(float(np.mean(np.abs(e - h))), 1),
                         "bias_pp": round(float(np.mean(e - h)), 1),
                         "spearman": round(float(stats.spearmanr(e, h)[0]), 2),
                         "top7_hit": f"{len(top & pred_top)}/{len(top)}",
                         "sd_ratio": round(float(np.std(e) / np.std(h)), 2),
                         "w_mean_30": round(wmean, 1),
                         "human_all30": global_mean().get(var),
                         "B1_MAE_pp": (round(float(np.mean([abs(cf[c] - truth[c]) for c in ix if cf.get(c) is not None])), 1)
                                       if any(cf.get(c) is not None for c in ix) else None),
                         "B1_n": sum(cf.get(c) is not None for c in ix),
                         "MAE_on_B1_countries": (round(float(np.mean([abs(e[c] - truth[c]) for c in ix if cf.get(c) is not None])), 1)
                                                 if any(cf.get(c) is not None for c in ix) else None),
                         "B0_MAE_pp": round(float(np.mean(np.abs(40.0 - h))), 1)})
    E = pd.DataFrame(rows)
    E.to_csv(out / "evaluation.csv", index=False)
    return E


def domain_structure(T: pd.DataFrame, b2: pd.DataFrame, out: Path) -> pd.DataFrame:
    """Pooled 30-country popularity T2B by domain vs the printed all-country domain values."""
    tg = load_targets()
    h = tg[(tg.country == "ALL30") & (tg.wave == 15) & (tg["var"].isin(TARGETS_POP_15))].set_index("var")["value"]
    w = pd.Series(WAVE15_N)
    rows = []
    for (cond, mode), g in T[T["var"].isin(TARGETS_POP_15)].groupby(["cond", "mode"]):
        est = g.pivot(index="country", columns="var", values="t2b")
        pooled = est.apply(lambda col: np.average(col.dropna(), weights=w[col.dropna().index]))
        ix = h.index.intersection(pooled.index)
        rows.append({"cond": cond, "mode": mode, "spearman_domains": round(float(stats.spearmanr(pooled[ix], h[ix])[0]), 2),
                     "MAE_pp": round(float(np.mean(np.abs(pooled[ix] - h[ix]))), 1)})
    if not b2.empty:
        est = b2[b2["var"].isin(TARGETS_POP_15)].pivot(index="country", columns="var", values="t2b")
        pooled = est.apply(lambda col: np.average(col.dropna(), weights=w[col.dropna().index]))
        ix = h.index.intersection(pooled.index)
        rows.append({"cond": "B2", "mode": "direct", "spearman_domains": round(float(stats.spearmanr(pooled[ix], h[ix])[0]), 2),
                     "MAE_pp": round(float(np.mean(np.abs(pooled[ix] - h[ix]))), 1)})
    D = pd.DataFrame(rows)
    D.to_csv(out / "domain_structure.csv", index=False)
    return D


def network_diagnostics(scored: pd.DataFrame, out: Path) -> pd.DataFrame:
    s = scored[scored["mode"] == "ssr"].copy()
    s["e"] = s[[f"p{k}" for k in range(1, 6)]].to_numpy() @ np.arange(1, 6)
    base = s[s.cond == "P3a"].set_index(["resp_id", "var"])["e"]
    rows = []
    for cond in sorted(set(s.cond) - {"P3a"}):
        x = s[s.cond == cond].set_index(["resp_id", "var"])["e"]
        ix = base.index.intersection(x.index)
        d = (x[ix] - base[ix])
        for _ in (0,):
            rows.append({"cond": cond, "n_pairs": len(ix), "mean_shift": round(float(d.mean()), 3),
                         "share_changed_>0.25": round(float((d.abs() > 0.25).mean()), 3),
                         "sd_r1": round(float(base[ix].groupby(level="var").std().mean()), 3),
                         "sd_r2": round(float(x[ix].groupby(level="var").std().mean()), 3)})
    N = pd.DataFrame(rows)
    N.to_csv(out / "network_diagnostics.csv", index=False)
    return N


def parse_b2(res: list[dict]) -> pd.DataFrame:
    rows = []
    for r in res:
        c = r["call_id"].split("|")[1]
        d = parse_json(r["text"])
        for v in ITEMS15:
            try:
                rows.append({"country": c, "var": v, "t2b": float(re.findall(r"[\d.]+", d.get(QID[v], ""))[0])})
            except (IndexError, ValueError):
                pass
    B = pd.DataFrame(rows)
    if not B.empty:
        B = B.groupby(["country", "var"], as_index=False)["t2b"].mean()      # average over repetitions
        pop = B[B["var"].isin(TARGETS_POP_15)].groupby("country")["t2b"].mean().reset_index()
        pop["var"] = "POPMEAN"
        B = pd.concat([B, pop], ignore_index=True)
    return B


def run(llm, out: Path, n_per_country: int = 10, k: int = 3, seed: int = 20261030, workers: int = 8,
        embedder=None, countries=None, n_network: int | None = None, b2_reps: int = 1) -> dict:
    """n_network: nested per-country subsample that receives the network conditions (default all)."""
    from . import pilot
    tw = prepare(out, n_per_country, seed, countries)
    c1 = round1_calls(tw)
    r1 = execute(c1, llm, out / "raw_r1.jsonl", workers)
    _, parsed = expand(c1, r1, out, 1)
    sub = tw if not n_network else tw.groupby("country", group_keys=False).head(n_network)
    sub.to_csv(out / "twins_network.csv", index=False)
    c2 = round2_calls(sub, parsed, k, seed, out)
    r2 = execute(c2, llm, out / "raw_r2.jsonl", workers)
    expand(c2, r2, out, 2)
    rb = execute(b2_calls(b2_reps), llm, out / "raw_b2.jsonl", workers)
    b2 = parse_b2(rb)
    b2.to_csv(out / "b2_direct.csv", index=False)
    # token usage of the API calls made by THIS process (cache hits cost nothing), saved before scoring
    json.dump({"calls": len(c1) + len(c2) + len(rb),
               "errors": sum(r["text"].startswith("__ERROR__") for r in r1 + r2 + rb),
               "usage_this_process": dict(llm.usage)}, open(out / "call_usage.json", "w"), indent=1)
    scored = pilot.score(out, SSRScorer(embedder))
    T = country_table(scored, tw)
    T.to_csv(out / "country_t2b.csv", index=False)
    errors = sum(r["text"].startswith("__ERROR__") for r in r1 + r2 + rb)
    return {"evaluation": evaluate(T, b2, out), "domains": domain_structure(T, b2, out),
            "network": network_diagnostics(scored, out), "errors": errors, "calls": len(c1) + len(c2) + len(rb)}


def reanalyze(out: Path, embedder) -> dict:
    """Recompute every table from saved files (no LLM calls)."""
    from . import pilot
    tw = pd.read_csv(out / "twins.csv")
    scored = pilot.score(out, SSRScorer(embedder))
    T = country_table(scored, tw)
    T.to_csv(out / "country_t2b.csv", index=False)
    b2 = pd.read_csv(out / "b2_direct.csv") if (out / "b2_direct.csv").exists() else pd.DataFrame()
    return {"evaluation": evaluate(T, b2, out), "domains": domain_structure(T, b2, out),
            "network": network_diagnostics(scored, out), "T": T, "b2": b2}


def figure(T: pd.DataFrame, b2: pd.DataFrame, out: Path, model: str) -> None:
    """Synthetic vs printed country T2B for the countries the summary report lists (top/bottom 7)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tg = load_targets()
    tg = tg[(tg.wave == 15) & (tg.stat == "t2b") & (tg.country != "ALL30")]
    series = [("P3a", "dlr", "DLR", "#eb6834", "s"), ("P3a", "ssr", "SSR", "#2a78d6", "o"),
              ("P3a+N3homophily", "ssr", "SSR + homophily network", "#1baf7a", "^"),
              ("B2", "direct", "Persona-free direct estimate", "#777777", "D")]
    titles = {OVERALL_FAV: "Overall favorability (XQ5)", OVERALL_REC: "Recommendation (XQ6)",
              "POPMEAN": "Mean popularity, 13 domains (XQ1)"}
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.4))
    for ax, var in zip(axes, titles):
        h = tg[tg["var"] == var].set_index("country")["value"]
        for cond, mode, lab, col, mk in series:
            src = b2[b2["var"] == var] if cond == "B2" else T[(T.cond == cond) & (T["mode"] == mode) & (T["var"] == var)]
            if src.empty:
                continue
            e = src.set_index("country")["t2b"].reindex(h.index)
            ax.scatter(h, e, s=38, marker=mk, facecolor=col if mk != "D" else "white", edgecolor=col if mk == "D" else "white",
                       linewidth=1.3, label=lab if var == OVERALL_FAV else None, zorder=3)
        ax.plot([0, 100], [0, 100], color="#bbbbbb", lw=1, ls="--", zorder=1)
        lo = 0 if var == "POPMEAN" else 20
        ax.set_xlim(lo, 100); ax.set_ylim(lo, 100)
        ax.set_title(titles[var], fontsize=10)
        ax.set_xlabel("Published survey, top-2-box %", fontsize=9)
        ax.grid(color="#eeeeee", lw=0.8); ax.spines[["top", "right"]].set_visible(False)
        for c in ("Japan", "Philippines", "Russia"):
            if c in h.index:
                ax.annotate(c, (h[c], h[c]), xytext=(3, -10), textcoords="offset points", fontsize=7, color="#555555")
    axes[0].set_ylabel("Synthetic twins, top-2-box %", fontsize=9)
    fig.legend(frameon=False, fontsize=8, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.03))
    fig.suptitle(f"{model}: 30-country table-only test (countries printed in the report's top/bottom-7 lists)", fontsize=11)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(out / "multicountry_figure.png", dpi=170, bbox_inches="tight")
    plt.close(fig)
