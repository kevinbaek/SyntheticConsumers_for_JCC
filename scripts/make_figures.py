"""Publication figures (PNG, 200 dpi) from outputs/analysis_final/*.csv. Every plotted number is read from a CSV.

  python scripts/make_figures.py outputs/analysis_final outputs/analysis_final/figures
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

D = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/analysis_final")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else D / "figures")
OUT.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parents[1]
M = pd.read_csv(D / "metrics.csv")
MODELS = [m for m in ["gpt-5.5", "gemini-3.1-pro", "claude-sonnet-5"] if m in set(M.model)]
LAB = {"gpt-5.5": "GPT-5.5", "gemini-3.1-pro": "Gemini 3.1 Pro", "claude-sonnet-5": "Claude Sonnet 5"}
COL = {"gpt-5.5": "#2a78d6", "gemini-3.1-pro": "#eb6834", "claude-sonnet-5": "#1baf7a"}   # validated categorical palette
MK = {"gpt-5.5": "o", "gemini-3.1-pro": "s", "claude-sonnet-5": "^"}
GREY, INK = "#8a8a8a", "#222222"
VARS = [("XQ5", "Favorability (XQ5)"), ("XQ6", "Recommendation (XQ6)"), ("POPMEAN", "Popularity, 13-domain mean")]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.axisbelow": True})


def _opt(name):
    p = D / f"{name}.csv"
    return pd.read_csv(p) if p.exists() else None


def fig1_design():
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(0, 110); ax.set_ylim(0, 44); ax.axis("off")

    def box(x, y, w, h, title, body, fc="#f3f6fb", ec="#2a78d6"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=1.2))
        ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", fontsize=9.5, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 6.0, body, ha="center", va="top", fontsize=8, color="#333333", linespacing=1.35)

    def arrow(x1, y1, x2, y2, txt=None):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.1))
        if txt:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 1.2, txt, ha="center", fontsize=7.5, color="#555555")
    box(1, 24, 20, 18, "KOFICE report (2026)", "respondent profile\n(30 countries, 31 rows)\n\nprinted outcomes:\nXQ5, XQ6, POPMEAN,\n3-band and 13-domain totals", fc="#fff8ec", ec="#c98a1a")
    box(27, 26, 18, 14, "Personas", "IPF on printed margins\n100 twins per country\n(3,000; 900 for networks)")
    box(51, 31, 22, 11, "Round 1, per model", "DLR (labelled options,\nhalf reversed)  |  SSR (free text)")
    box(51, 17, 22, 11, "Round 2 (900 twins)", "N1 self-reflection\nN2 random  |  N3 homophily, k = 3")
    box(51, 3, 22, 11, "Persona-free estimate (B2)", "same model asked for each\ncountry's share, 3 runs")
    box(79, 24, 15, 18, "SSR scoring", "text-embedding-3-small\nanchor similarity\n-> P(1..5), T2B")
    box(79, 3, 15, 18, "Comparators", "B0, B5, LOCO,\nB-PROFILE, B-XITEM, B1\n(no LLM)", fc="#f4f4f4", ec=GREY)
    box(98, 10, 11, 26, "Evaluation", "MAE, 1-MAE,\nJS sim., Spearman,\nbias, spread,\nsplit accuracy\n\ncross-validated\nCAL-LOCO,\nCAL-STYLE", fc="#eef8f3", ec="#1baf7a")
    arrow(21, 34, 27, 34, "profile only")
    arrow(45, 34, 51, 36)
    arrow(45, 30, 51, 23)
    arrow(73, 36, 79, 34)
    arrow(73, 22, 79, 30)
    arrow(94, 33, 98, 28)
    arrow(73, 8, 98, 16)
    arrow(94, 12, 98, 14)
    ax.annotate("", xy=(103, 36.8), xytext=(11, 42.6), arrowprops=dict(arrowstyle="-|>", color="#c98a1a", lw=1.0,
                connectionstyle="arc3,rad=-0.12", linestyle="--"))
    ax.text(57, 44.5, "printed outcomes enter only at evaluation and in cross-validated corrections", ha="center",
            fontsize=7.8, color="#a06c10")
    ax.text(1, 0.2, "Three models (GPT-5.5, Gemini 3.1 Pro, Claude Sonnet 5), one identical pipeline each; 8,790 calls per model.",
            fontsize=7.8, color="#555555")
    fig.savefig(OUT / "fig1_study_design.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_mae():
    X = _opt("rb_listed_extra")
    methods = [("Twins DLR", "Twins, direct rating (DLR)"), ("Twins SSR", "Twins, SSR"),
               ("B2 persona-free LLM", "Persona-free estimate (B2)"), ("Twins SSR + CAL-LOCO", "SSR + CAL-LOCO"),
               ("Twins SSR + CAL-STYLE", "SSR + country offset (CAL-STYLE)")]
    base = [("B0 uniform", "Uniform 40% (B0)"), ("B5 30-country total", "30-country total (B5)"),
            ("LOCO continent mean", "Continent mean (LOCO)"), ("B-PROFILE knowledge share (LOO)", "Profile regression (B-PROFILE)"),
            ("B-XITEM cross-item regression", "Cross-item regression (B-XITEM)")]
    rows = methods + base
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 5.0), sharey=True)
    for ax, (v, title) in zip(axes, VARS):
        for yi, (meth, _) in enumerate(rows):
            if (meth, _) in base:
                src = X if meth.startswith("B-PROFILE") and X is not None else M
                r = src[(src.model == "none") & (src.method == meth) & (src["var"] == v)]
                if not r.empty:
                    r = r.iloc[0]
                    ax.errorbar(r.MAE_pp, yi, xerr=[[r.MAE_pp - r.MAE_lo], [r.MAE_hi - r.MAE_pp]], fmt="D", color=GREY,
                                mfc="white", ms=6, lw=1)
                continue
            for k, mdl in enumerate(MODELS):
                r = M[(M.model == mdl) & (M.method == meth) & (M["var"] == v)]
                if r.empty:
                    continue
                r = r.iloc[0]
                ax.errorbar(r.MAE_pp, yi + (k - 1) * 0.22, xerr=[[r.MAE_pp - r.MAE_lo], [r.MAE_hi - r.MAE_pp]], fmt=MK[mdl],
                            color=COL[mdl], ms=6, mec="white", mew=0.8, lw=1.2, label=LAB[mdl] if (yi == 0 and v == "XQ5") else None)
        ax.axhline(len(methods) - 0.5, color="#dddddd", lw=0.8)
        ax.set_title(title, fontsize=10); ax.set_xlabel("MAE vs published values, pp (95% CI)")
        ax.grid(axis="x", color="#eeeeee"); ax.set_xlim(0, None)
    axes[0].set_yticks(range(len(rows)), [lab for _, lab in rows]); axes[0].invert_yaxis()
    axes[0].text(-0.02, (len(methods) - 0.5) / len(rows), "", transform=axes[0].transAxes)
    fig.legend(loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("SSR cuts the favorability and recommendation error of direct rating by 13 to 23 points; the country-offset "
                 "correction brings most errors to 3-5 points, about as low as a non-LLM regression on the same data", fontsize=10.5)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97)); fig.savefig(OUT / "fig2_mae_by_method.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_scatter():
    W = pd.read_csv(D / "country_estimates_wide.csv")
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    for col, (v, title) in enumerate(VARS):
        for row, meth in enumerate(["Twins DLR", "Twins SSR"]):
            ax = axes[row, col]
            lo = 0 if v == "POPMEAN" else 20
            ax.plot([lo, 100], [lo, 100], color="#bbbbbb", ls="--", lw=1)
            for mdl in MODELS:
                g = W[(W.model == mdl) & (W.cond == meth) & (W["var"] == v)].dropna(subset=["human"])
                ax.scatter(g.human, g.est, marker=MK[mdl], color=COL[mdl], s=28, edgecolor="white", linewidth=0.6,
                           label=LAB[mdl] if (row == 0 and col == 0) else None)
            ax.set_xlim(lo, 100); ax.set_ylim(lo, 100)
            ax.set_title(f"{title}: {'direct rating' if meth == 'Twins DLR' else 'SSR'}", fontsize=9.5)
            ax.set_xlabel("Published, top-2-box %"); ax.set_ylabel("Synthetic, top-2-box %"); ax.grid(color="#f0f0f0")
    fig.legend(loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Direct ratings put almost every country near 100%; SSR orders countries but compresses them into a narrow band "
                 "(countries listed in the report; dashed line = perfect agreement)", fontsize=10.5)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97)); fig.savefig(OUT / "fig3_scatter.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_xq5_30():
    A = pd.read_csv(ROOT / "data/pdf_tables/targets_xq5_all30.csv").set_index("country")["value"].sort_values()
    E = pd.read_csv(D / "estimates.csv")
    listed = set(pd.read_csv(ROOT / "data/pdf_tables/targets_country.csv").query("wave == 15 and var == 'XQ5' and stat == 't2b' and country != 'ALL30'").country)
    fig, ax = plt.subplots(figsize=(8.5, 8.2))
    y = np.arange(len(A))
    ax.scatter(A.values, y, marker="|", s=260, color=INK, linewidths=2.2, label="Published survey", zorder=3)
    for k, mdl in enumerate(MODELS):
        s = E[(E.model == mdl) & (E.cond == "Twins SSR") & (E["var"] == "XQ5")].set_index("country")["est"].reindex(A.index)
        ax.scatter(s.values, y + (k - 1) * 0.22, marker=MK[mdl], color=COL[mdl], s=26, edgecolor="white", linewidth=0.5,
                   label=f"{LAB[mdl]}, SSR", zorder=4)
    ax.set_yticks(y, [f"{c}{'' if c in listed else '  °'}" for c in A.index])
    ax.set_xlabel("Favorability, top-2-box % (° = middle country, not in the top/bottom-7 lists)")
    ax.grid(axis="x", color="#eeeeee"); ax.set_xlim(40, 95)
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    ax.set_title("All 30 countries: SSR twins place every country between 71% and 87%,\nso the error grows as true favorability falls", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "fig4_xq5_30_countries.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_bands():
    A = pd.read_csv(D / "all30.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), sharey=True)
    for ax, v in zip(axes, ["XQ5", "XQ6"]):
        g = A[A["var"] == v]
        labels, vals = ["Published survey"], [tuple(g.iloc[0][["human_b2b", "human_mid", "human_t2b"]])]
        for mdl in MODELS:
            for meth in ["Twins SSR", "Twins DLR"]:
                r = g[(g.model == mdl) & (g.method == meth)]
                if not r.empty:
                    labels.append(f"{LAB[mdl]}, {'SSR' if meth == 'Twins SSR' else 'DLR'}")
                    vals.append(tuple(r.iloc[0][["syn_b2b", "syn_mid", "syn_t2b"]]))
        yy = np.arange(len(labels))
        V = np.array(vals)
        shades = ["#d6d6d6", "#a8a8a8", "#2a78d6"]
        left = np.zeros(len(labels))
        for j, (name, c) in enumerate(zip(["points 1-2", "point 3", "points 4-5"], shades)):
            ax.barh(yy, V[:, j], left=left, color=c, edgecolor="white", height=0.7, label=name if v == "XQ5" else None)
            for y_, l_, w_ in zip(yy, left, V[:, j]):
                if w_ >= 5:
                    ax.text(l_ + w_ / 2, y_, f"{w_:.0f}", ha="center", va="center", fontsize=7.5, color="white" if j == 2 else "#333333")
            left += V[:, j]
        ax.set_yticks(yy, labels); ax.set_xlim(0, 100)
        ax.set_title({"XQ5": "Favorability, 30 countries", "XQ6": "Recommendation, 30 countries"}[v], fontsize=10)
        ax.set_xlabel("% of respondents (countries weighted by sample size)")
    axes[0].invert_yaxis()
    fig.legend(loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Humans put a quarter of answers in the middle; SSR twins put 7-20% there and direct ratings at most 3%", fontsize=10.5)
    fig.tight_layout(rect=(0, 0.06, 1, 0.95)); fig.savefig(OUT / "fig5_distribution_bands.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_domains():
    P = pd.read_csv(D / "domain_profile.csv")
    names = {"XQ1_1": "Drama", "XQ1_2": "Variety show", "XQ1_3": "Film", "XQ1_4": "Music", "XQ1_5": "Animation",
             "XQ1_6": "Publishing", "XQ1_7": "Webtoon", "XQ1_8": "Game", "XQ1_9": "Fashion", "XQ1_10": "Beauty",
             "XQ1_11": "Food", "XQ1_12": "Character", "XQ1_13": "Performance"}
    h = P.groupby("var")["human"].first().sort_values(ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.0), sharey=True)
    for ax, meth in zip(axes, ["Twins SSR", "Twins DLR"]):
        y = np.arange(len(h))
        ax.scatter(h.values, y, color=INK, marker="|", s=300, linewidths=2.2, label="Published survey", zorder=3)
        for k, mdl in enumerate(MODELS):
            g = P[(P.model == mdl) & (P.method == meth)].set_index("var").reindex(h.index)
            ax.scatter(g.synthetic, y + (k - 1) * 0.2, marker=MK[mdl], color=COL[mdl], s=26, edgecolor="white", linewidth=0.5,
                       label=LAB[mdl])
        ax.set_yticks(y, [names[v] for v in h.index]); ax.invert_yaxis() if meth == "Twins SSR" else None
        ax.set_title("SSR" if meth == "Twins SSR" else "Direct rating (DLR)", fontsize=10)
        ax.set_xlabel("Share saying the domain is popular with the general public (%), 30 countries")
        ax.grid(axis="x", color="#eeeeee"); ax.set_xlim(0, 100)
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("Domain popularity: direct ratings keep the order but not the level; SSR is closer in level but reorders "
                 "character, webtoon and performance", fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(OUT / "fig6_domain_profile.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_network():
    N = pd.read_csv(D / "network_by_item.csv")
    V = _opt("rb_verbatim")
    arms = ["P3a+N1self", "P3a+N2random", "P3a+N3homophily"]
    lab = {"P3a+N1self": "N1 self-reflection", "P3a+N2random": "N2 random", "P3a+N3homophily": "N3 homophily"}
    types = [("social perception (XQ1)", "popularity (XQ1)", "Perceived popularity (13 domains)"),
             ("own preference (XQ5, XQ6)", "own preference (XQ5, XQ6)", "Own favorability and recommendation")]
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.6), sharey="row")
    for c, (it, itv, title) in enumerate(types):
        x = np.arange(len(arms))
        for k, mdl in enumerate(MODELS):
            g = N[(N.model == mdl) & (N.item_type == it)].set_index("cond").reindex(arms)
            axes[0, c].bar(x + (k - 1) * 0.26, 100 * g["share_moved_gt_0.25"], width=0.24, color=COL[mdl],
                           label=LAB[mdl] if c == 0 else None)
            if V is not None:
                gv = V[(V.model == mdl) & (V.item_type == itv)].set_index("cond").reindex(arms)
                axes[1, c].bar(x + (k - 1) * 0.26, 100 * gv["share_verbatim_repeat"], width=0.24, color=COL[mdl])
        axes[0, c].set_title(title, fontsize=10)
        for r in (0, 1):
            axes[r, c].set_xticks(x, [lab[a] for a in arms]); axes[r, c].grid(axis="y", color="#eeeeee")
    axes[0, 0].set_ylabel("Answers moved > 0.25 scale points (%)")
    axes[1, 0].set_ylabel("Round-2 answer identical to round 1 (%)")
    fig.legend(loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("One round of peer exposure moves few answers, mostly on popularity; Claude often repeats its first answer word "
                 "for word", fontsize=10.5)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96)); fig.savefig(OUT / "fig7_network_movement.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_gradients():
    G = pd.read_csv(D / "persona_gradients.csv")
    G = G[(G.attribute == "korea_awareness") & (G.level != "spearman(code, score)")]
    order = ["little", "somewhat", "knows Korea very well"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, mode in zip(axes, ["dlr", "ssr"]):
        for mdl in MODELS:
            g = G[(G.model == mdl) & (G["mode"] == mode) & (G["var"] == "XQ5")].set_index("level").reindex(order)
            ax.plot(range(3), g.t2b_pct, marker=MK[mdl], color=COL[mdl], label=LAB[mdl] if mode == "dlr" else None)
        ax.set_xticks(range(3), ["knows little", "knows somewhat", "knows very well"])
        ax.set_title(f"{'Direct rating' if mode == 'dlr' else 'SSR'}", fontsize=10)
        ax.set_ylabel("Synthetic favorability, top-2-box %"); ax.grid(axis="y", color="#eeeeee")
        ax.tick_params(labelleft=True)
    fig.legend(loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.05))
    fig.suptitle("Persona attributes do move twin answers: favorability rises with the persona's knowledge of Korea (all 3,000 twins)",
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0.06, 1, 0.94)); fig.savefig(OUT / "fig8_persona_gradient.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_anchor():
    A = _opt("rb_anchor_selftest")
    if A is None:
        return
    A = A.copy()
    A["item"] = np.where(A["var"].str.startswith("XQ1_"), "Popularity (13 domains)", A["var"].map({"XQ5": "Favorability", "XQ6": "Recommendation"}))
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    cols = {"Favorability": "#222222", "Recommendation": "#7a7a7a", "Popularity (13 domains)": "#b0b0b0"}   # not the model hues
    mks = {"Favorability": "o", "Recommendation": "D", "Popularity (13 domains)": "v"}
    for k, (item, g) in enumerate(A.groupby("item")):
        q = g.groupby("anchor_point")["t2b_if_given_as_answer"].agg(["min", "max", "mean"])
        xs = q.index.to_numpy() + (k - 1) * 0.12
        ax.vlines(xs, 100 * q["min"], 100 * q["max"], color=cols[item], lw=2.5, alpha=0.6)
        ax.plot(xs, 100 * q["mean"], marker=mks[item], color=cols[item], lw=1.2, label=item)
    ax.axhline(100, color=GREY, ls=":", lw=1); ax.axhline(0, color=GREY, ls=":", lw=1)
    ax.set_xticks(range(1, 6), ["1", "2", "3", "4", "5"]); ax.set_xlabel("Scale point whose anchor statement is given as the answer")
    ax.set_ylabel("SSR top-2-box share (%)"); ax.grid(axis="y", color="#eeeeee"); ax.set_ylim(-3, 103)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title("SSR cannot reach 100%: an answer that repeats the most positive anchor\nscores only 70-90% top-2-box (bars: range over anchor sets)", fontsize=9.5)
    fig.tight_layout(); fig.savefig(OUT / "fig9_anchor_selftest.png", dpi=200, bbox_inches="tight"); plt.close(fig)


for f in (fig1_design, fig_mae, fig_scatter, fig_xq5_30, fig_bands, fig_domains, fig_network, fig_gradients, fig_anchor):
    try:
        f()
        print("ok", f.__name__)
    except Exception as e:  # noqa: BLE001
        print("FAILED", f.__name__, type(e).__name__, e)
