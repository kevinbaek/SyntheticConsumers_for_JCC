"""Contamination probes requested in review (small; separate call ids, so the main runs are untouched).

  python scripts/probes.py --model gpt-5.5 --out outputs/probes

1. RECALL: ask the model, from memory, for the previous edition's (published 2025, 14th wave) country values of
   favorability and recommendation for all 30 countries (3 repetitions). If the model can recall published
   rankings, persona answers may echo them.
2. B2-NEUTRAL: the persona-free estimate (B2) without the survey-identifying description ("aged 15-59 ...
   surveyed online in late 2025"), 30 countries x 3 repetitions.
"""
import argparse
import json
import re
from pathlib import Path

import pandas as pd

from hallyu_twins import multicountry as mc
from hallyu_twins.codebook import COUNTRIES, ITEMS
from hallyu_twins.config import load_config
from hallyu_twins.llm import Cache, make_llm
from hallyu_twins.personas import DISPLAY

RECALL = ("The Korea Foundation for International Cultural Exchange (KOFICE) publishes an annual Overseas Hallyu "
          "Survey of people who use Korean cultural content in about 30 countries. From memory only, without looking "
          "anything up: in the edition published in 2025 (the 14th survey, fieldwork in late 2024), what percentage of "
          "respondents in each country below said they liked Korean cultural content overall (top two of five scale "
          "points), and what percentage said they would recommend it (top two)? For each country also say whether "
          "you actually recall the published figure or are guessing.\n\nCountries: {countries}\n\nReply with a JSON "
          "object only: {{\"<country>\": {{\"favorability\": <number>, \"recommendation\": <number>, "
          "\"basis\": \"recall\" or \"guess\"}}, ...}}")
B2N = ("Consider people living in {country} who have used Korean cultural content. Estimate the percentage who would "
       "choose the top two options ('{top}') for each question below.\n\n{questions}\n\nReply with a JSON object only, "
       "mapping each question id (Q01...) to a percentage between 0 and 100. Do not look anything up.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default="outputs/probes")
    ap.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    cfg = load_config("configs/default.yaml")
    spec = next(m for m in cfg.models if m.name == a.model)
    llm = make_llm(spec, Cache(str(Path(cfg.cache_dir) / f"{spec.name}.sqlite")))
    out = Path(a.out) / a.model
    out.mkdir(parents=True, exist_ok=True)
    names = ", ".join(DISPLAY.get(c, c) for c in COUNTRIES)
    calls = [{"call_id": f"PROBE-RECALL|k{r}", "rep": r,
              "messages": [{"role": "user", "content": RECALL.format(countries=names)}]} for r in range(a.reps)]
    qs = "\n".join(f"{mc.QID[v]}. {ITEMS[v].text} (top two options: '{ITEMS[v].scale.labels[3]}' or "
                   f"'{ITEMS[v].scale.labels[4]}')" for v in mc.ITEMS15)
    calls += [{"call_id": f"PROBE-B2N|{c}|k{r}", "rep": r,
               "messages": [{"role": "user", "content": B2N.format(country=DISPLAY.get(c, c), top="4 or 5", questions=qs)}]}
              for c in COUNTRIES for r in range(a.reps)]
    res = mc.execute(calls, llm, out / "raw_probes.jsonl", workers=12)
    with open(out / "prompts_probes.jsonl", "w") as f:
        for c in calls:
            f.write(json.dumps({"call_id": c["call_id"], "messages": c["messages"]}, ensure_ascii=False) + "\n")
    # recall: parse per country
    rows = []
    disp = {DISPLAY.get(c, c).lower(): c for c in COUNTRIES} | {c.lower(): c for c in COUNTRIES}
    for r in res:
        if not r["call_id"].startswith("PROBE-RECALL"):
            continue
        m = re.search(r"\{.*\}", r["text"], flags=re.S)
        try:
            d = json.loads(m.group(0)) if m else {}
        except json.JSONDecodeError:
            d = {}
        for k, v in d.items():
            c = disp.get(k.strip().lower().removeprefix("the "), disp.get(k.strip().lower()))
            if c and isinstance(v, dict):
                rows.append({"rep": r["call_id"], "country": c, "favorability": v.get("favorability"),
                             "recommendation": v.get("recommendation"), "basis": v.get("basis")})
    pd.DataFrame(rows).to_csv(out / "recall.csv", index=False)
    b2n = mc.parse_b2([{"call_id": "B2|" + x["call_id"].split("|")[1], "text": x["text"]}
                       for x in res if x["call_id"].startswith("PROBE-B2N")])
    b2n.to_csv(out / "b2_neutral.csv", index=False)
    json.dump({"model": spec.name, "calls": len(calls), "errors": sum(x["text"].startswith("__ERROR__") for x in res),
               "usage": llm.usage}, open(out / "probe_meta.json", "w"), indent=1)
    print(a.model, "recall rows", len(rows), "b2n rows", len(b2n), "usage", llm.usage)


if __name__ == "__main__":
    main()
