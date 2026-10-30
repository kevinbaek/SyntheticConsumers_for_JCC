import numpy as np
import pandas as pd

from hallyu_twins import table_eval as TE


def test_js_binary_bounds():
    p = np.array([0.0, 0.3, 0.7, 1.0])
    assert np.allclose(TE._js_binary(p, p), 0, atol=1e-9)
    assert abs(TE._js_binary(np.array([0.0]), np.array([1.0]))[0] - 1) < 1e-6   # base-2 JSD max = 1


def test_metrics_perfect_and_known():
    h = pd.Series([50.0, 60.0, 70.0, 80.0], index=list("abcd"))
    m = TE.metrics(h, h)
    assert m["MAE_pp"] == 0 and m["one_minus_MAE"] == 1 and abs(m["JS_sim"] - 1) < 1e-9 and m["spearman"] == 1
    m2 = TE.metrics(h + 10, h)
    assert abs(m2["MAE_pp"] - 10) < 1e-12 and abs(m2["bias_pp"] - 10) < 1e-12 and abs(m2["one_minus_MAE"] - 0.9) < 1e-12


def test_cal_loco_never_uses_heldout_truth():
    rng = np.random.default_rng(0)
    idx = [f"c{i}" for i in range(8)]
    est = pd.Series(rng.uniform(30, 90, 8), index=idx)
    hum = pd.Series(rng.uniform(30, 90, 8), index=idx)
    base = TE.cal_loco(est, hum)
    hum2 = hum.copy(); hum2["c3"] = 0.0           # change only the held-out truth of c3
    assert abs(TE.cal_loco(est, hum2)["c3"] - base["c3"]) < 1e-9


def test_cal_style_uses_only_other_items():
    tr = pd.DataFrame({"country": ["A", "A", "A", "B", "B"], "var": ["XQ5", "XQ6", "POPMEAN", "XQ5", "XQ6"],
                       "human": [50, 40, 30, 70, 60], "list": ["top"] * 5})
    T = pd.DataFrame({"country": ["A", "A", "A", "B", "B"], "cond": ["Twins SSR"] * 5,
                      "var": ["XQ5", "XQ6", "POPMEAN", "XQ5", "XQ6"], "est": [60, 55, 35, 75, 70]})
    s = TE.cal_style(T, tr, "Twins SSR", "XQ5")
    # errors e = human - synthetic: A (-10, -15, -5), B (-5, -10). For A: item bias (B on XQ5) = -5;
    # style from XQ6 = -15 - (-10) = -5 (POPMEAN has no other country) -> 60 - 5 - 5 = 50.
    # For B: item bias (A on XQ5) = -10; style from XQ6 = -10 - (-15) = +5 -> 75 - 10 + 5 = 70.
    assert abs(s["A"] - 50) < 1e-9 and abs(s["B"] - 70) < 1e-9
    tr2 = tr.copy(); tr2.loc[(tr2.country == "A") & (tr2["var"] == "XQ5"), "human"] = 0
    assert abs(TE.cal_style(T, tr2, "Twins SSR", "XQ5")["A"] - 50) < 1e-9    # own truth not used


def test_truth_lists():
    t = TE.truth()
    assert (t[t["var"] == "XQ5"]["list"].value_counts() == 7).all()
    jp = t[(t.country == "Japan")].set_index("var")["human"].to_dict()
    assert jp == {"XQ5": 52.7, "XQ6": 36.4, "POPMEAN": 32.4}


def test_cross_item_baseline_no_leakage():
    tr = TE.truth()
    base = pd.DataFrame(TE._cross_item(tr)).set_index(["country", "var"])["est"]
    tr2 = tr.copy()
    m = (tr2.country == "Japan") & (tr2["var"] == "XQ6")
    tr2.loc[m, "human"] += 17
    new = pd.DataFrame(TE._cross_item(tr2)).set_index(["country", "var"])["est"]
    assert abs(new[("Japan", "XQ6")] - base[("Japan", "XQ6")]) < 1e-9


def test_split_acc_constant_is_nan_and_perfect_is_one():
    h = pd.Series([90.0, 80, 70, 30, 20, 10], index=list("abcdef"))
    lists = pd.Series(["top"] * 3 + ["bottom"] * 3, index=h.index)
    assert "split_acc" not in TE.metrics(pd.Series(40.0, index=h.index), h, lists)
    assert TE.metrics(h, h, lists)["split_acc"] == 1.0


def test_paired_diff_edges():
    h = pd.Series([50.0, 60, 70], index=list("abc"))
    assert TE.paired_mae_diff(h, h, h)["p_two_sided"] == 1.0
    assert np.isnan(TE.paired_mae_diff(pd.Series(dtype=float), h, h)["p_two_sided"])
