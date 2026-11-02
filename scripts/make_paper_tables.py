"""Build every number-bearing table of the manuscript from outputs/analysis_final/*.csv.

  python scripts/make_paper_tables.py outputs/analysis_final > outputs/analysis_final/paper_tables.md

Nothing in the manuscript's results tables is typed by hand: they are pasted from this output, and
verify/check_paper_numbers.py re-reads the manuscript and checks each number against these CSVs.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import atexit
import io
import re

# Display labels only: the data files call the persona conditions "Twins"; the manuscript calls them
# "Persona" (profile-based synthetic consumers drawn from published margins, not digital twins of real
# people). "## Table:" lines are lookup keys for the manuscript builder and are left unchanged.
_REAL_STDOUT, _BUF = sys.stdout, io.StringIO()
sys.stdout = _BUF
_RELABEL = [(r"\bTwins(?= SSR| DLR|, SSR|, DLR)", "Persona"), (r"\bTwin-item\b", "Persona–item"),
            (r"\bTwins\b", "Personas"), (r"\btwins\b", "personas"), (r"\bTwin\b", "Persona"), (r"\btwin\b", "persona")]


def _relabel(line):
    if line.startswith("## Table:"):
        return line
    for pat, rep in _RELABEL:
        line = re.sub(pat, rep, line)
    return line


@atexit.register
def _flush():
    sys.stdout = _REAL_STDOUT
    _REAL_STDOUT.write("\n".join(_relabel(x) for x in _BUF.getvalue().split("\n")))
    _REAL_STDOUT.flush()


D = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/analysis_final")
M = pd.read_csv(D / "metrics.csv")
P = pd.read_csv(D / "paired.csv")
DOM = pd.read_csv(D / "domains.csv")
A30 = pd.read_csv(D / "all30.csv")
NET = pd.read_csv(D / "network.csv")
MODELS = [m for m in ["gpt-5.5", "gemini-3.1-pro", "claude-sonnet-5"] if m in set(M.model)]
LABEL = {"gpt-5.5": "GPT-5.5", "gemini-3.1-pro": "Gemini 3.1 Pro", "claude-sonnet-5": "Claude Sonnet 5"}
VARS = [("XQ5", "Favorability"), ("XQ6", "Recommendation"), ("POPMEAN", "Popularity")]


def f1(x):
    return "–" if pd.isna(x) else f"{x:.1f}"


def f2(x):
    return "–" if pd.isna(x) else f"{x:.2f}"


def get(model, method, var):
    r = M[(M.model == model) & (M.method == method) & (M["var"] == var)]
    return None if r.empty else r.iloc[0]


def table_no_human():
    rows = ["| Model | Method | " + " | ".join(f"{v} MAE (95% CI) | {v} ρ" for _, v in VARS) + " |",
            "| --- | --- | " + " | ".join("--- | ---" for _ in VARS) + " |"]
    for mdl in MODELS:
        for meth, lab in [("Twins DLR", "Twins, DLR"), ("Twins SSR", "Twins, SSR"), ("B2 persona-free LLM", "Persona-free estimate (B2)")]:
            cells = []
            for v, _ in VARS:
                r = get(mdl, meth, v)
                cells += ["–", "–"] if r is None else [f"{f1(r.MAE_pp)} ({f1(r.MAE_lo)}–{f1(r.MAE_hi)})", f2(r.spearman)]
            rows.append(f"| {LABEL[mdl]} | {lab} | " + " | ".join(cells) + " |")
    for meth, lab in [("B5 30-country total", "30-country total (B5)"), ("B0 uniform", "Uniform 40% (B0)")]:
        cells = []
        for v, _ in VARS:
            r = get("none", meth, v)
            cells += ["–", "–"] if r is None else [f"{f1(r.MAE_pp)} ({f1(r.MAE_lo)}–{f1(r.MAE_hi)})", "–"]
        rows.append(f"| – | {lab} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def table_detail(var):
    cols = ["n", "MAE_pp", "one_minus_MAE", "JS_sim", "spearman", "bias_pp", "sd_ratio", "split_acc"]
    head = "| Model | Method | n | MAE (pp) | 1−MAE | JS sim. | Spearman ρ | Bias (pp) | Spread ratio | Top/bottom-7 accuracy |"
    rows = [head, "| --- | --- | " + " | ".join("---" for _ in cols) + " |"]
    order = ["Twins DLR", "Twins SSR", "Twins SSR + CAL-LOCO", "Twins SSR + CAL-STYLE", "B2 persona-free LLM"]
    for mdl in MODELS:
        for meth in order:
            r = get(mdl, meth, var)
            if r is None:
                continue
            rows.append(f"| {LABEL[mdl]} | {meth} | {int(r.n)} | {f1(r.MAE_pp)} | {f2(r.one_minus_MAE)} | {r.JS_sim:.3f} | "
                        f"{f2(r.spearman)} | {f1(r.bias_pp)} | {f2(r.sd_ratio)} | {f2(r.split_acc)} |")
    for meth in ["B0 uniform", "B5 30-country total", "LOCO mean", "LOCO continent mean", "B-XITEM cross-item regression", "B1 carry-forward"]:
        r = get("none", meth, var)
        if r is None:
            continue
        rows.append(f"| – | {meth} | {int(r.n)} | {f1(r.MAE_pp)} | {f2(r.one_minus_MAE)} | {r.JS_sim:.3f} | "
                    f"{f2(r.spearman)} | {f1(r.bias_pp)} | {f2(r.sd_ratio)} | {f2(r.split_acc)} |")
    return "\n".join(rows)


def table_paired(contrasts):
    rows = ["| Model | Item | A | B | n | MAE(A) − MAE(B), pp (95% CI) | p | p (Holm) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for mdl in MODELS:
        for v, vl in VARS:
            for a, b in contrasts:
                r = P[(P.model == mdl) & (P["var"] == v) & (P.a == a) & (P.b == b)]
                if r.empty:
                    continue
                r = r.iloc[0]
                rows.append(f"| {LABEL[mdl]} | {vl} | {a} | {b} | {int(r.n)} | {r.diff_pp:+.1f} ({r.lo:+.1f} to {r.hi:+.1f}) | {r.p_two_sided:.3f} | {r.p_holm:.3f} |")
    return "\n".join(rows)


def table_network():
    rows = ["| Model | Arm | Twin-item pairs | Answers moved > 0.25 pt | Mean shift (pt) | Within-country SD, round 1 → 2 |",
            "| --- | --- | --- | --- | --- | --- |"]
    for mdl in MODELS:
        for _, r in NET[NET.model == mdl].iterrows():
            rows.append(f"| {LABEL[mdl]} | {r.cond.replace('P3a+', '')} | {int(r.pairs)} | {100 * r['share_changed_gt_0.25']:.1f}% | "
                        f"{r.mean_shift:+.3f} | {r.within_country_sd_r1:.3f} → {r.within_country_sd_r2:.3f} |")
    return "\n".join(rows)


def table_structure():
    rows = ["| Model | Method | 13-domain MAE (pp) | 13-domain ρ | XQ5 3-band JS sim. | XQ6 3-band JS sim. | XQ5 bands, synthetic (1–2 / 3 / 4–5) |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for mdl in MODELS:
        for meth in ["Twins DLR", "Twins SSR", "B2 persona-free LLM"]:
            d = DOM[(DOM.model == mdl) & (DOM.method == meth)]
            a5 = A30[(A30.model == mdl) & (A30.method == meth) & (A30["var"] == "XQ5")]
            a6 = A30[(A30.model == mdl) & (A30.method == meth) & (A30["var"] == "XQ6")]
            dm = d.iloc[0] if not d.empty else None
            bands = f"{a5.iloc[0].syn_b2b:.1f} / {a5.iloc[0].syn_mid:.1f} / {a5.iloc[0].syn_t2b:.1f}" if not a5.empty else "–"
            rows.append(f"| {LABEL[mdl]} | {meth} | {f1(dm.MAE_pp) if dm is not None else '–'} | {f2(dm.spearman) if dm is not None else '–'} | "
                        f"{a5.iloc[0].JS_sim:.3f} | {a6.iloc[0].JS_sim:.3f} | {bands} |" if not a5.empty else
                        f"| {LABEL[mdl]} | {meth} | {f1(dm.MAE_pp) if dm is not None else '–'} | {f2(dm.spearman) if dm is not None else '–'} | – | – | – |")
    h = A30.iloc[0]
    rows.append(f"| – | Human (published) | – | – | – | – | {h.human_b2b:.1f} / {h.human_mid:.1f} / {h.human_t2b:.1f} |")
    return "\n".join(rows)


print("## Table: no human data for the target country\n")
print(table_no_human())
for v, vl in VARS:
    print(f"\n## Table: all metrics, {vl} ({v})\n")
    print(table_detail(v))
print("\n## Table: paired contrasts\n")
print(table_paired([("Twins SSR", "Twins DLR"), ("Twins SSR", "B5 30-country total"), ("Twins SSR", "B2 persona-free LLM"),
                    ("Twins SSR + CAL-STYLE", "B-XITEM cross-item regression"), ("Twins SSR + CAL-LOCO", "LOCO continent mean")]))
print("\n## Table: network contrasts\n")
print(table_paired([("Twins SSR + N3 homophily network", "Twins SSR (network subsample, round 1)"),
                    ("Twins SSR + N3 homophily network", "Twins SSR + N2 random network"),
                    ("Twins SSR + N3 homophily network", "Twins SSR + N1 self-reflection")]))
print()
print(table_network())
print("\n## Table: structure\n")
print(table_structure())


# ---- extra analyses (written by hallyu_twins.extra_analyses) -------------------------------------------
def _opt(name):
    p = D / f"{name}.csv"
    return pd.read_csv(p) if p.exists() and p.stat().st_size > 2 else None


ITEML = {"XQ5": "Favorability", "XQ6": "Recommendation", "POPMEAN": "Popularity"}
VD = _opt("variance_decomposition")
if VD is not None:
    print("\n## Table: twin-level variance explained (adjusted R²), country label vs persona attributes\n")
    print("| Model | Mode | Items | Country only | Persona only | Both | Added by persona | Added by country |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    VD["grp"] = np.where(VD["var"].str.startswith("XQ1_"), "13 popularity items (mean)", VD["var"].map(ITEML))
    for mdl in MODELS:
        for mode in ["dlr", "ssr"]:
            for grp in ["Favorability", "Recommendation", "13 popularity items (mean)"]:
                g = VD[(VD.model == mdl) & (VD["mode"] == mode) & (VD.grp == grp)]
                if g.empty:
                    continue
                print(f"| {LABEL[mdl]} | {mode.upper()} | {grp} | {g.r2_country.mean():.2f} | {g.r2_persona.mean():.2f} | "
                      f"{g.r2_both.mean():.2f} | {g.persona_increment.mean():+.2f} | {g.country_increment.mean():+.2f} |")
ES = _opt("error_structure")
IC = _opt("item_coherence")
IM = _opt("inter_model")
MA = _opt("mode_agreement")
print("\n## Table: correlation analyses (Spearman ρ)\n")
print("| Analysis | Model | Method | Items | n | ρ | p |")
print("| --- | --- | --- | --- | --- | --- | --- |")
if IC is not None:
    for _, r in IC.iterrows():
        a, b = r.pair.split("~")
        print(f"| Item coherence: {ITEML.get(a, a)} ~ {ITEML.get(b, b)} | {LABEL.get(r.model, '–')} | {r.source} | – | {int(r.n)} | {f2(r.spearman)} | {'–' if pd.isna(r.p) else f'{r.p:.3f}'} |")
ICB = _opt("rb_item_coherence_b2")
if ICB is not None:
    for _, r in ICB.iterrows():
        a, b = r.pair.split("~")
        print(f"| Item coherence: {ITEML.get(a, a)} ~ {ITEML.get(b, b)} | {LABEL.get(r.model, '–')} | {r.source} | – | {int(r.n)} | {f2(r.spearman)} | {r.p:.3f} |")
if IM is not None:
    for _, r in IM.iterrows():
        print(f"| Inter-model agreement, 30 countries | {LABEL.get(r.model_a, r.model_a)} ~ {LABEL.get(r.model_b, r.model_b)} | {r.method} | {ITEML[r['var']]} | {int(r.n_countries)} | {f2(r.spearman)} | {r.p:.3f} |")
if ES is not None:
    for _, r in ES.iterrows():
        print(f"| {r.analysis} | {LABEL.get(r.model, r.model)} | {r.method} | {ITEML[r['var']]} | {int(r.n)} | {f2(r.spearman)} | {'–' if pd.isna(r.p) else f'{r.p:.3f}'} |")
if MA is not None:
    for mdl, g in MA.groupby("model"):
        print(f"| Same twin, DLR ~ SSR (median of 15 items) | {LABEL.get(mdl, mdl)} | – | 15 items | {int(g.n_twins.median())} | {g.spearman_dlr_ssr.median():.2f} | – |")
        for v in ("XQ5", "XQ6"):
            r = g[g["var"] == v].iloc[0]
            print(f"| Same twin, DLR ~ SSR | {LABEL.get(mdl, mdl)} | – | {ITEML[v]} | {int(r.n_twins)} | {r.spearman_dlr_ssr:.2f} | {r.p:.3f} |")
CE = _opt("continent_error")
if CE is not None:
    print("\n## Table: mean signed error by continent (pp), listed countries\n")
    conts = sorted(CE.continent.unique())
    print("| Model | Method | Item | " + " | ".join(conts) + " |")
    print("| --- | --- | --- | " + " | ".join("---" for _ in conts) + " |")
    for mdl in MODELS:
        for cond in ["Twins DLR", "Twins SSR"]:
            for v in ["XQ5", "XQ6", "POPMEAN"]:
                g = CE[(CE.model == mdl) & (CE.cond == cond) & (CE["var"] == v)].set_index("continent")
                if g.empty:
                    continue
                cells = [f"{g.at[c, 'mean_error_pp']:+.1f} (n={int(g.at[c, 'n_countries'])})" if c in g.index else "–" for c in conts]
                print(f"| {LABEL[mdl]} | {cond} | {ITEML[v]} | " + " | ".join(cells) + " |")
MC = _opt("monte_carlo_error")
if MC is not None:
    print("\n## Table: Monte Carlo standard error of a country estimate (100 twins per country), pp\n")
    print("| Model | Mode | Item | Median SE | Range over countries |")
    print("| --- | --- | --- | --- | --- |")
    for mdl in MODELS:
        for mode in ["dlr", "ssr"]:
            for v in ["XQ5", "XQ6", "POPMEAN"]:
                r = MC[(MC.model == mdl) & (MC["mode"] == mode) & (MC["var"] == v)]
                if not r.empty:
                    r = r.iloc[0]
                    print(f"| {LABEL[mdl]} | {mode.upper()} | {ITEML[v]} | {r.se_median_pp:.1f} | {r.se_min_pp:.1f}–{r.se_max_pp:.1f} |")
PS = _opt("popmean_sensitivity")
if PS is not None:
    print("\n## Table: popularity average over 13 domains (main) vs 11 domains (sensitivity)\n")
    print("| Model | Method | Definition | n | MAE (pp) | Bias (pp) | ρ |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for mdl in MODELS:
        for meth in ["Twins DLR", "Twins SSR", "B2 persona-free LLM"]:
            for d in ["13 domains", "11 domains"]:
                r = PS[(PS.model == mdl) & (PS.method == meth) & (PS.definition == d)]
                if not r.empty:
                    r = r.iloc[0]
                    print(f"| {LABEL[mdl]} | {meth} | {d} | {int(r.n)} | {r.MAE_pp:.1f} | {r.bias_pp:+.1f} | {f2(r.spearman)} |")

# ---- robustness (written by hallyu_twins.robustness) ------------------------------------------------------
RX = _opt("rb_xq5_all30")
if RX is not None:
    print("\n## Table: favorability on all 30 countries (full ranking printed in the report)\n")
    print("| Model | Method | MAE, 30 countries (95% CI) | Bias | ρ (30) | Spread | Top/bottom-7 recovered (of 14) | MAE, 14 listed | MAE, 16 middle |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    order = ["Twins DLR", "Twins SSR", "Twins SSR + CAL-LOCO (LOO, 30)", "Twins SSR + CAL-LOCO (fit on 14 listed)", "B2 persona-free LLM"]
    base = ["B0 uniform", "B5 30-country total", "B5 leave-one-out total", "LOCO mean", "LOCO continent mean",
            "B-PROFILE knowledge share (LOO)", "B1 carry-forward"]
    for mdl in MODELS + ["none"]:
        for meth in (order if mdl != "none" else base):
            g = RX[(RX.model == mdl) & (RX.method == meth)].set_index("scope")
            if "fit on 14 listed" in meth and "16 middle" in g.index:
                m = g.loc["16 middle"]
                print(f"| {LABEL.get(mdl, '–')} | Twins SSR + CAL-LOCO fitted on the 14 listed | – | – | – | – | – | – | "
                      f"{f1(m.MAE_pp)} (bias {m.bias_pp:+.1f}) |")
                continue
            if "all 30" not in g.index:
                continue
            a = g.loc["all 30"]
            l14 = g.loc["14 listed", "MAE_pp"] if "14 listed" in g.index else np.nan
            m16 = g.loc["16 middle", "MAE_pp"] if "16 middle" in g.index else np.nan
            rec = "–" if pd.isna(a.extreme7_recovery) else f"{a.extreme7_recovery * 14:.0f}"
            nn = "" if int(a.n) == 30 else f" (n = {int(a.n)})"
            print(f"| {LABEL.get(mdl, '–')} | {meth}{nn} | {f1(a.MAE_pp)} ({f1(a.MAE_lo)}–{f1(a.MAE_hi)}) | {a.bias_pp:+.1f} | {f2(a.spearman)} | "
                  f"{f2(a.sd_ratio)} | {rec} | {f1(l14)} | {f1(m16)} |")
    ext = RX[RX.method.str.contains("fit on 14 listed")]
    if not ext.empty:
        print("\nCAL-LOCO fitted on the 14 listed countries and applied to the 16 middle ones: " + "; ".join(
            f"{LABEL[r.model]} {r.method.split(' + ')[0].replace('Twins ', '')} MAE {r.MAE_pp:.1f} (bias {r.bias_pp:+.1f})"
            for _, r in ext.iterrows()))
RP = _opt("rb_xq5_all30_paired")
if RP is not None:
    print("\n## Table: paired contrasts on all 30 countries (favorability; exploratory)\n")
    print("| Model | A | B | MAE(A) | MAE(B) | Difference (pp) | p (sign-flip) | ρ(A) − ρ(B) (95% CI) |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for _, r in RP.iterrows():
        rd = "–" if pd.isna(r.rho_diff) else f"{r.rho_diff:+.2f} ({r.rho_diff_lo:+.2f} to {r.rho_diff_hi:+.2f})"
        print(f"| {LABEL[r.model]} | {r.a} | {r.b} | {r.MAE_a:.1f} | {r.MAE_b:.1f} | {r.MAE_diff_pp:+.1f} | {r.p_signflip:.3f} | {rd} |")
LX = _opt("rb_listed_extra")
if LX is not None:
    print("\n## Table: additional non-LLM comparators on the listed countries\n")
    print("| Method | Item | n | MAE (95% CI) | Bias | ρ | Spread | Top/bottom-7 accuracy |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for _, r in LX.iterrows():
        print(f"| {r.method} | {ITEML[r['var']]} | {int(r.n)} | {f1(r.MAE_pp)} ({f1(r.MAE_lo)}–{f1(r.MAE_hi)}) | {r.bias_pp:+.1f} | "
              f"{f2(r.spearman)} | {f2(r.sd_ratio)} | {f2(r.split_acc)} |")
CN = _opt("rb_censoring")
if CN is not None:
    print("\n## Table: unlisted countries (XQ6: 11, POPMEAN: 16) against the printed band and the backed-out mean\n")
    print("| Item | Model | Method | Outside band | Synthetic mean of unlisted | Implied human mean | Error (pp) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for _, r in CN.iterrows():
        print(f"| {r['var']} [{r.band_lo:.1f}, {r.band_hi:.1f}] | {LABEL[r.model]} | {r.method} | {100 * r.share_outside_band:.0f}% | "
              f"{r.synthetic_unlisted_mean:.1f} | {r.human_unlisted_mean_backout:.1f} | {r.error_unlisted_mean_pp:+.1f} |")
WG = _opt("rb_within_group")
if WG is not None:
    print("\n## Table: rank correlation within the top-7 and within the bottom-7 (Spearman)\n")
    print("| Model | Method | Favorability top | Favorability bottom | Recommendation top | Recommendation bottom | Popularity top | Popularity bottom |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for mdl in MODELS:
        for meth in ["Twins DLR", "Twins SSR", "B2 persona-free LLM"]:
            g = WG[(WG.model == mdl) & (WG.method == meth)].set_index(["var", "group"])["spearman"]
            cells = [f2(g.get((v, grp), np.nan)) for v in ["XQ5", "XQ6", "POPMEAN"] for grp in ["top", "bottom"]]
            print(f"| {LABEL[mdl]} | {meth} | " + " | ".join(cells) + " |")
DR = _opt("rb_dlr_reversal")
if DR is not None:
    print("\n## Table: DLR forward vs reversed option order (30 countries)\n")
    print("| Model | Item | T2B forward | T2B reversed | Mean country difference (pp) | p (sign-flip) |")
    print("| --- | --- | --- | --- | --- | --- |")
    for _, r in DR.iterrows():
        print(f"| {LABEL[r.model]} | {ITEML[r['var']]} | {r.t2b_forward_pct:.1f} | {r.t2b_reversed_pct:.1f} | {r.mean_country_diff_pp:+.1f} | {r.p_signflip:.3f} |")
AS = _opt("rb_anchor_selftest")
if AS is not None:
    AS["grp"] = np.where(AS["var"].str.startswith("XQ1_"), "Popularity (13 domains)", AS["var"].map(ITEML))
    print("\n## Table: SSR anchor self-test (top-2-box share when the answer repeats an anchor; min–max over sets and domains)\n")
    print("| Item | Point 1 | Point 2 | Point 3 | Point 4 | Point 5 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for grp, g in AS.groupby("grp"):
        q = g.groupby("anchor_point")["t2b_if_given_as_answer"].agg(["min", "max"])
        print(f"| {grp} | " + " | ".join(f"{100 * q.at[k, 'min']:.0f}–{100 * q.at[k, 'max']:.0f}%" for k in range(1, 6)) + " |")
VB = _opt("rb_verbatim")
if VB is not None:
    print("\n## Table: round-2 answers identical to the same twin's round-1 answer\n")
    print("| Model | Arm | Popularity items | Own preference items |")
    print("| --- | --- | --- | --- |")
    for mdl in MODELS:
        for cond in ["P3a+N1self", "P3a+N2random", "P3a+N3homophily"]:
            g = VB[(VB.model == mdl) & (VB.cond == cond)].set_index("item_type")["share_verbatim_repeat"]
            print(f"| {LABEL[mdl]} | {cond.replace('P3a+', '')} | {100 * g.get('popularity (XQ1)', np.nan):.1f}% | {100 * g.get('own preference (XQ5, XQ6)', np.nan):.1f}% |")
DU = _opt("rb_duplicates")
if DU is not None:
    print("\n## Table: twins with identical personas and identical responses\n")
    print("| Model | Mode | Duplicate groups | Twins in groups | Same-prompt pairs | Identical responses |")
    print("| --- | --- | --- | --- | --- | --- |")
    for _, r in DU.iterrows():
        print(f"| {LABEL[r.model]} | {r['mode'].upper()} | {int(r.duplicate_groups)} | {int(r.twins_in_groups)} | {int(r.same_prompt_pairs)} | {int(r.identical_response_pairs)} |")
W14 = _opt("rb_wave14")
if W14 is not None:
    print("\n## Table: is the synthetic value closer to the previous wave? (countries with a printed change)\n")
    print("| Model | Method | Item | n | MAE vs 2025 wave | MAE vs 2024 wave | Closer to 2024 |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for _, r in W14.iterrows():
        print(f"| {LABEL[r.model]} | {r.method} | {ITEML[r['var']]} | {int(r.n)} | {r.MAE_vs_wave15:.1f} | {r.MAE_vs_wave14:.1f} | {100 * r.share_closer_to_wave14:.0f}% |")
PR = _opt("rb_probes")
if PR is not None:
    print("\n## Table: contamination probes\n")
    print("| Model | Probe | Item | Target | n | MAE | Bias | ρ | Spread |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for _, r in PR.iterrows():
        print(f"| {LABEL.get(r.model, r.model)} | {r.probe} | {ITEML[r['var']]} | {r.target} | {int(r.n)} | {f1(r.MAE_pp)} | {r.bias_pp:+.1f} | {f2(r.spearman)} | {f2(r.sd_ratio)} |")
    if "share_self_labelled_recall" in PR:
        s = PR.dropna(subset=["share_self_labelled_recall"]).groupby("model")["share_self_labelled_recall"].max()
        print("\nShare of recall-probe answers the model labelled as recalled rather than guessed: " +
              ", ".join(f"{LABEL.get(k, k)} {100 * v:.0f}%" for k, v in s.items()))
TL = _opt("rb_two_level")
if TL is not None:
    print("\n## Table: two-level bootstrap (twins within countries, then countries; 1,000 resamples)\n")
    print("| Model | Item | MAE DLR (95% CI) | MAE SSR (95% CI) | SSR − DLR (95% CI) |")
    print("| --- | --- | --- | --- | --- |")
    for mdl in MODELS:
        for v in ["XQ5", "XQ6", "POPMEAN"]:
            g = TL[(TL.model == mdl) & (TL["var"] == v)].set_index("quantity")
            c = [f"{g.at[q, 'point']:.1f} ({g.at[q, 'lo']:.1f}–{g.at[q, 'hi']:.1f})" for q in ["MAE DLR", "MAE SSR"]]
            d = g.loc["MAE SSR - MAE DLR"]
            print(f"| {LABEL[mdl]} | {ITEML[v]} | {c[0]} | {c[1]} | {d.point:+.1f} ({d.lo:+.1f} to {d.hi:+.1f}) |")
NC = _opt("rb_noise_ceiling")
if NC is not None:
    h = NC[NC.source == "human sampling error only"].set_index("var")["expected_MAE_perfect_pp"]
    allr = NC["expected_MAE_perfect_pp"]
    print("\nNoise ceiling: expected MAE of a perfect predictor from human sampling error alone = " +
          ", ".join(f"{ITEML[k]} {v:.1f} pp" for k, v in h.items()) +
          f"; with twin Monte Carlo error added, {allr.min():.1f}–{allr.max():.1f} pp.")
MG = _opt("rb_margins")
if MG is not None:
    print("\nAchieved vs printed persona margins (largest absolute gap in any category, median / maximum over 30 countries, pp): " +
          "; ".join(f"{r.dimension} {r['median']:.1f} / {r['max']:.1f}" for _, r in MG.iterrows()))

# ---- manuscript main-text tables (compact; every cell read from metrics.csv, rb_listed_extra.csv, paired.csv) ----
LXE = _opt("rb_listed_extra")
PAI = pd.read_csv(D / "paired.csv")


def _cell(r, rho=True, bias=False):
    if r is None:
        return ["–"] * (1 + rho + bias)
    out = [f"{f1(r.MAE_pp)} ({f1(r.MAE_lo)}–{f1(r.MAE_hi)})"]
    if bias:
        out.append(f"{r.bias_pp:+.1f}")
    if rho:
        out.append(f2(r.spearman))
    return out


def _lx(method, var):
    if LXE is None:
        return None
    r = LXE[(LXE.method == method) & (LXE["var"] == var)]
    return None if r.empty else r.iloc[0]


print("\n## Table: MS main comparison, listed countries\n")
print("| Information about the target country | Method | Model | " + " | ".join(f"{v} MAE (95% CI) | bias | ρ" for _, v in VARS) + " |")
print("| --- | --- | --- | " + " | ".join("--- | --- | ---" for _ in VARS) + " |")
for meth, lab, info in [("Twins DLR", "Twins, DLR", "printed profile"), ("Twins SSR", "Twins, SSR", "printed profile"),
                        ("B2 persona-free LLM", "Persona-free LLM (B2)", "country name")]:
    for mdl in MODELS:
        cells = []
        for v, _ in VARS:
            cells += _cell(get(mdl, meth, v), bias=True)
        print(f"| {info} | {lab} | {LABEL[mdl]} | " + " | ".join(cells) + " |")
for meth, lab, info, src in [("B-PROFILE knowledge share (LOO)", "Profile regression (B-PROFILE)", "printed profile (one share)", "lx"),
                             ("B0 uniform", "Uniform 40% (B0)", "none", "m"),
                             ("B5 30-country total", "30-country total (B5)", "pooled total incl. target", "m"),
                             ("B5 leave-one-out total", "Total without target (B5-LOO)", "none", "lx"),
                             ("LOCO mean", "Mean of other countries (LOCO)", "none", "m"),
                             ("LOCO continent mean", "Continent mean (LOCO-continent)", "none", "m")]:
    cells = []
    for v, _ in VARS:
        r = _lx(meth, v) if src == "lx" else get("none", meth, v)
        c = _cell(r, bias=True)
        if meth.startswith(("B0", "B5", "LOCO mean")):
            c[-1] = "–"
        cells += c
    print(f"| {info} | {lab} | – | " + " | ".join(cells) + " |")

print("\n## Table: MS corrections, listed countries\n")
print("| Method | Model | " + " | ".join(f"{v} MAE (n) | Δ vs comparator (95% CI) | p (Holm)" for _, v in VARS) + " |")
print("| --- | --- | " + " | ".join("--- | --- | ---" for _ in VARS) + " |")
for meth, comp in [("Twins SSR + CAL-LOCO", "LOCO continent mean"), ("Twins SSR + CAL-STYLE", "B-XITEM cross-item regression")]:
    for mdl in MODELS:
        cells = []
        for v, _ in VARS:
            r = get(mdl, meth, v)
            p = PAI[(PAI.model == mdl) & (PAI["var"] == v) & (PAI.a == meth) & (PAI.b == comp)]
            cells.append("–" if r is None else f"{f1(r.MAE_pp)} ({int(r.n)})")
            if p.empty:
                cells += ["–", "–"]
            else:
                q = p.iloc[0]
                cells += [f"{q.diff_pp:+.1f} ({q.lo:+.1f} to {q.hi:+.1f})", f"{q.p_holm:.3f}"]
        lab = "SSR + CAL-LOCO (vs continent mean)" if "LOCO" in meth else "SSR + country offset, CAL-STYLE (vs B-XITEM)"
        print(f"| {lab} | {LABEL[mdl]} | " + " | ".join(cells) + " |")
for meth, lab in [("LOCO continent mean", "Continent mean (LOCO-continent)"), ("B-XITEM cross-item regression", "Cross-item regression (B-XITEM)"),
                  ("B1 carry-forward", "Previous wave (B1, change-selected)")]:
    cells = []
    for v, _ in VARS:
        r = get("none", meth, v)
        cells += ["–" if r is None else f"{f1(r.MAE_pp)} ({int(r.n)})", "", ""]
    print(f"| {lab} | – | " + " | ".join(cells) + " |")

# ---- second review round (hallyu_twins.discussion_checks) ---------------------------------------------------
CAL = _opt("rb_calibrated")
RXa = _opt("rb_xq5_all30")
if CAL is not None:
    print("\n## Table: MS calibration of every elicitation, all 30 countries\n")
    print("| Model | SSR, uncalibrated | SSR + CAL-LOCO | DLR + CAL-LOCO | B2 + CAL-LOCO | B-PROFILE (no LLM) | SSR+CAL − DLR+CAL (p) | SSR+CAL − B2+CAL (p) | SSR+CAL − B-PROFILE (p) |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    c30 = CAL[CAL.scope == "XQ5 all 30"]
    for mdl in MODELS:
        g = c30[c30.model == mdl]
        mae = g[g.contrast.isna()].set_index("method")["MAE_pp"]
        d = g[g.contrast.notna()].set_index("contrast")
        raw = RXa[(RXa.model == mdl) & (RXa.method == "Twins SSR") & (RXa.scope == "all 30")]["MAE_pp"].iloc[0]
        cell = lambda k: f"{d.at[k, 'diff_pp']:+.1f} ({d.at[k, 'p_signflip']:.3f})"
        print(f"| {LABEL[mdl]} | {raw:.1f} | {mae['Twins SSR + CAL-LOCO']:.1f} | {mae['Twins DLR + CAL-LOCO']:.1f} | {mae['B2 persona-free LLM + CAL-LOCO']:.1f} | "
              f"{mae['B-PROFILE (no LLM)']:.1f} | {cell('vs Twins DLR + CAL-LOCO')} | {cell('vs B2 persona-free LLM + CAL-LOCO')} | {cell('vs B-PROFILE (no LLM)')} |")
    print("\n## Table: S calibration of every elicitation, listed countries\n")
    print("| Model | Item | n | SSR + CAL-LOCO | DLR + CAL-LOCO | B2 + CAL-LOCO | SSR+CAL − DLR+CAL (p) | SSR+CAL − B2+CAL (p) |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for v, lab in VARS:
        for mdl in MODELS:
            g = CAL[(CAL.scope == f"{v} listed") & (CAL.model == mdl)]
            mae = g[g.contrast.isna()].set_index("method")
            d = g[g.contrast.notna()].set_index("contrast")
            cell = lambda k: f"{d.at[k, 'diff_pp']:+.1f} ({d.at[k, 'p_signflip']:.3f})"
            print(f"| {LABEL[mdl]} | {lab} | {int(mae['n'].iloc[0])} | {mae.at['Twins SSR + CAL-LOCO', 'MAE_pp']:.1f} | {mae.at['Twins DLR + CAL-LOCO', 'MAE_pp']:.1f} | "
                  f"{mae.at['B2 persona-free LLM + CAL-LOCO', 'MAE_pp']:.1f} | {cell('vs Twins DLR + CAL-LOCO')} | {cell('vs B2 persona-free LLM + CAL-LOCO')} |")

SV = _opt("rb_ssr_variants")
JD = _opt("rb_judge")
RG = _opt("rb_ssr_range")
if SV is not None and JD is not None:
    print("\n## Table: MS scoring of the same free-text answers\n")
    print("| Model | Item (countries) | SSR, main: MAE (bias) | SSR, one anchor set: MAE range (bias range) | Nearest anchor: MAE (bias) | LLM judge: MAE (bias) | Answers judged top-2 | ρ with human: SSR | ρ with human: judge top-box share |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    jg = JD[JD.judge == "gpt-5.5"]
    for v, scope, lab in (("XQ5", "all 30", "Favorability (30)"), ("XQ6", "listed", "Recommendation (19)")):
        for mdl in MODELS:
            g = SV[(SV.model == mdl) & (SV["var"] == v) & (SV.scope == scope)].set_index("variant")
            single = g[g.index.str.contains("only")]
            j = jg[(jg.model == mdl) & (jg["var"] == v) & (jg.scope == scope)].iloc[0]
            m, nn = g.loc["all sets (main)"], g.loc["nearest anchor (hard)"]
            print(f"| {LABEL[mdl]} | {lab} | {m.MAE_pp:.1f} ({m.bias_pp:+.1f}) | {single.MAE_pp.min():.1f}–{single.MAE_pp.max():.1f} ({single.bias_pp.min():+.1f} to {single.bias_pp.max():+.1f}) | "
                  f"{nn.MAE_pp:.1f} ({nn.bias_pp:+.1f}) | {j.MAE_pp:.1f} ({j.bias_pp:+.1f}) | {j.t2b_all_answers:.1f}% | {j.rho_ssr_human:.2f} | {j.rho_topbox_human:.2f} |")
    ag = JD[JD.judge.str.startswith("agreement")]
    cj = JD[(JD.judge == "claude-sonnet-5") & JD.scope.eq("listed")]
    if not ag.empty:
        a = ag.iloc[0]
        print(f"\nSecond judge (Claude Sonnet 5, every 10th batch): {int(a.n_parsed)} answers classified by both judges; exact agreement "
              f"{100 * a.exact_agreement:.1f}%, agreement on top-2 vs not {100 * a.t2b_agreement:.1f}%; the second judge put "
              f"{cj.t2b_all_answers.min():.1f}–{cj.t2b_all_answers.max():.1f}% of answers in the top two options (by model and item).")
    print("\n## Table: S SSR anchor-set variants\n")
    print("| Model | Variant | Item | Countries | n | MAE (pp) | Bias (pp) | ρ | Spread |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for _, r in SV.iterrows():
        print(f"| {LABEL[r.model]} | {r.variant} | {ITEML[r['var']]} | {r.scope} | {int(r.n)} | {r.MAE_pp:.1f} | {r.bias_pp:+.1f} | {f2(r.spearman)} | {f2(r.sd_ratio)} |")
if RG is not None:
    print("\n## Table: S range of individual SSR scores\n")
    print("| Model | Item | Answers | Minimum | 1st percentile | 99th percentile | Maximum |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for _, r in RG.iterrows():
        it = {"XQ5": "Favorability", "XQ6": "Recommendation"}.get(r.group, r.group)
        print(f"| {LABEL[r.model]} | {it} | {int(r.n):,} | {100 * r['min']:.1f}% | {100 * r.p01:.1f}% | {100 * r.p99:.1f}% | {100 * r['max']:.1f}% |")

PRI = _opt("rb_prior")
if PRI is not None:
    print("\n## Table: MS what the twins' country estimates track\n")
    print("| Model | ρ(SSR, human) | ρ(SSR, knowledge share) | ρ(SSR, own recall) | ρ(SSR, own B2) | β knowledge | β recall | R² | LOO MAE: knowledge share | LOO MAE: recall | LOO MAE: SSR | LOO MAE: knowledge + recall | LOO MAE: knowledge + recall + SSR |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for mdl in MODELS:
        r = PRI[PRI.model == mdl].iloc[0]
        print(f"| {LABEL[mdl]} | {r.rho_SSR_human:.2f} | {r['rho_SSR_knowledge share']:.2f} | {r.rho_SSR_recall:.2f} | {r.rho_SSR_B2:.2f} | {r.beta_knowledge:.2f} | "
              f"{r.beta_recall:.2f} | {r.R2_knowledge_recall:.2f} | {r.LOO_MAE_knowledge:.1f} | {r.LOO_MAE_recall:.1f} | {r.LOO_MAE_SSR:.1f} | "
              f"{r['LOO_MAE_knowledge+recall']:.1f} | {r['LOO_MAE_knowledge+recall+SSR']:.1f} |")

LG = _opt("rb_language")
if LG is not None:
    print("\n## Table: S favorability error by language group\n")
    print("| Model | Method | Group (n) | Bias, group | Bias, other countries | Raw difference | Difference adjusted for the human level (95% CI) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for _, r in LG.iterrows():
        print(f"| {LABEL[r.model]} | {r.method} | {r.group} ({int(r.n_group)}) | {r.bias_group:+.1f} | {r.bias_other:+.1f} | {r.raw_diff:+.1f} | "
              f"{r.adj_diff:+.1f} ({r.adj_lo:+.1f} to {r.adj_hi:+.1f}) |")

ASIM = _opt("rb_anchor_similarity")
if ASIM is not None:
    ASIM["item"] = np.where(ASIM["var"].str.startswith("XQ1_"), "Popularity (13 domains)", ASIM["var"].map(ITEML))
    print("\n## Table: S anchor similarity\n")
    print("| Item | Anchor sets | Mean pairwise cosine (range over sets) | Lowest pair | Highest pair | Point 1 vs point 5 | Point 4 vs point 5 |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for it, g in ASIM.groupby("item", sort=False):
        print(f"| {it} | {len(g)} | {g.mean_pairwise.mean():.2f} ({g.mean_pairwise.min():.2f}–{g.mean_pairwise.max():.2f}) | {g.min_pairwise.min():.2f} | "
              f"{g.max_pairwise.max():.2f} | {g.sim_1_5.min():.2f}–{g.sim_1_5.max():.2f} | {g.sim_4_5.min():.2f}–{g.sim_4_5.max():.2f} |")

PG = _opt("persona_gradients")
if PG is not None:
    print("\n## Table: S persona gradients\n")
    print("| Model | Mode | Item | Attribute | Top-2-box share by level, % | Largest gap (pp) | Spearman ρ (p) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    ATTR = {"korea_awareness": "Knowledge of Korea (very well / somewhat / little)", "age_band": "Age (15–19 / 20s / 30s / 40s / 50s)",
            "sex": "Sex (male / female)", "nationality": "Nationality (Korean-descended / local / third-country)"}
    for mdl in MODELS:
        for mode in ("dlr", "ssr"):
            for v in ("XQ5", "XQ6"):
                for attr, lab in ATTR.items():
                    g = PG[(PG.model == mdl) & (PG["mode"] == mode) & (PG["var"] == v) & (PG.attribute == attr)]
                    lv = g[~g.level.str.startswith("spearman")]
                    sp = g[g.level.str.startswith("spearman")]
                    rho = f"{sp.mean_score.iloc[0]:+.2f} ({sp.t2b_pct.iloc[0]:.3f})" if len(sp) else "–"
                    print(f"| {LABEL[mdl]} | {mode.upper()} | {ITEML[v]} | {lab} | {' / '.join(f'{x:.1f}' for x in lv.t2b_pct)} | "
                          f"{lv.t2b_pct.max() - lv.t2b_pct.min():.1f} | {rho} |")
