import numpy as np
import pandas as pd
import pytest

from hallyu_twins.codebook import ALL_TARGETS, ITEMS, questionnaire_order
from hallyu_twins.data.loader import tidy
from hallyu_twins.data.mock import make_wave
from hallyu_twins.elicit import SSRScorer, messages, parse_dlr
from hallyu_twins.embed import MockEmbedder
from hallyu_twins.metrics import item_metrics, ks_sim, wdist
from hallyu_twins.network import build_network
from hallyu_twins.personas import assert_no_leakage, build_persona, swap_map
from hallyu_twins.tables import carry_forward, country_targets, marginal_check, synthesize
from hallyu_twins.config import Config


@pytest.fixture(scope="module")
def w15():
    return tidy(make_wave(15, scale=0.03, seed=1), 15, Config().country_codes)


def test_skip_logic_max_six(w15):
    assert w15.answered_domains.map(len).max() <= 6
    order = questionnaire_order(w15.answered_domains.iloc[0])
    assert order[-2:] == ["XQ5", "XQ6"]


def test_persona_never_contains_outcomes(w15):
    row = w15.iloc[0]
    for lvl in ("P0", "P1", "P2", "P3", "P4"):
        p = build_persona(row, lvl)
        assert_no_leakage(p.text, row)
        assert not (set(p.features) & set(ALL_TARGETS))


def test_label_controls(w15):
    row = w15.iloc[0]
    assert row["country"] not in build_persona(row, "P4", "none").text
    sw = swap_map(7)
    assert all(a != b for a, b in sw.items())
    p = build_persona(row, "P4", "swap", sw)
    assert sw[row["country"]] in p.text and row["country"] not in p.text


def test_dlr_reverse_parse():
    assert parse_dlr("2", reverse=False) == 2
    assert parse_dlr("2", reverse=True) == 4
    assert np.isnan(parse_dlr("no idea", reverse=False))
    m = messages("You live in Japan.", ITEMS["XQ5"], "dlr", reverse=True)
    assert "1. I like it very much" in m[-1]["content"]


def test_ssr_probabilities_sum_to_one():
    sc = SSRScorer(MockEmbedder())
    P = sc.probs(ITEMS["XQ5"], ["I love it very much.", "I really dislike it.", ""])
    assert np.allclose(P.sum(1), 1)
    assert P[0, 3:].sum() > P[1, 3:].sum()


def test_network_within_country_and_no_self(w15):
    nb = build_network(w15, "homophily", k=3, seed=0)
    c = w15.set_index("resp_id")["country"]
    for r, ns in nb.items():
        assert r not in ns and all(c[n] == c[r] for n in ns)


def test_metrics_perfect_prediction():
    rng = np.random.default_rng(0)
    h = rng.integers(1, 6, 400).astype(float)
    df = pd.DataFrame({"country": np.repeat(list("ABCD"), 100), "h": h, "w": 1.0})
    P = np.zeros((400, 5)); P[np.arange(400), h.astype(int) - 1] = 1
    df[[f"p{k}" for k in range(1, 6)]] = P
    m, _ = item_metrics(df)
    assert m["acc_indiv"] == 1 and m["level_err_pp"] < 1e-9 and abs(m["r_wc"] - 1) < 1e-2
    assert ks_sim(wdist(h), wdist(h)) == 1


def test_pdf_tables():
    t = country_targets("Japan")
    assert t["XQ5"] == 52.7 and t["XQ6"] == 36.4 and t["POPMEAN"] == 32.4
    assert carry_forward("Japan") == {"XQ5": 46.3, "XQ6": 31.8}
    tw = synthesize("Japan", 40, 3)
    assert (tw.sex.value_counts() == 20).all()
    mc = marginal_check(tw, "Japan")
    assert (mc[mc.dimension == "age_band"].eval("abs(target-achieved)") < 4).all()
    assert not ((tw.occupation == 1) & (tw.age > 18)).any()


def test_cache_key_is_per_call(tmp_path):
    from hallyu_twins.config import ModelSpec
    from hallyu_twins.llm import Cache, MockLLM
    llm = MockLLM(ModelSpec("m", "mock", "m", "-", "-"), Cache(str(tmp_path / "c.sqlite")))
    msgs = [{"role": "user", "content": "same prompt"}]
    llm.complete(msgs, call_id="twin-1")
    assert llm.complete(msgs, call_id="twin-1").cached is True
    assert llm.complete(msgs, call_id="twin-2").cached is False


def test_synthesis_independent_across_countries_and_balanced_reverse():
    a, b = synthesize("Japan", 40, 5), synthesize("Brazil", 40, 5)
    assert list(a.sex) != list(b.sex)
    assert a.reverse.sum() == 20 and b.reverse.sum() == 20
    assert a.resp_id.is_unique and not set(a.resp_id) & set(b.resp_id)


def test_parse_json_normalises_and_recovers():
    from hallyu_twins.multicountry import parse_json
    assert parse_json('```json {"Q01": 4, "q 2": "3", "Q POP03": 5, "Q04": "", "Q05": null} ```') == {
        "Q01": "4", "Q02": "3", "Q03": "5"}
    broken = '{"Q01": "I like it", "Q02": "He said "wow" there", "Q03": 4}'
    out = parse_json(broken)
    assert out.get("Q01") == "I like it" and out.get("Q03") == "4"


def test_parse_json_control_characters():
    from hallyu_twins.multicountry import parse_json
    txt = '{"Q01": "line one\nline two", "Q02": "bad "quote" here\tx", "Q03": 5}'.replace("\\n", "\n")
    out = parse_json(txt)
    assert out["Q03"] == "5" and out["Q01"].startswith("line one")
