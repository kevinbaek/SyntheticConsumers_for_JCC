"""Appendix B: tokens and cost of one full run per model (8,790 calls), from the measured token files.

  python scripts/cost_table.py outputs > outputs/analysis_final/cost_table.md

List prices (USD per million tokens, standard tier, prompts <= 200k tokens), checked 2026-10-30:
  Claude Sonnet 5   input 2.00  output 10.00
  GPT-5.5           input 5.00  output 30.00
  Gemini 3.1 Pro    input 2.00  output 12.00 (thinking tokens billed as output)
  text-embedding-3-small 0.02 per million tokens
"""
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs")
PRICE = {"claude-sonnet-5": (2.0, 10.0), "gpt-5.5": (5.0, 30.0), "gemini-3.1-pro": (2.0, 12.0)}
LABEL = {"gpt-5.5": "GPT-5.5", "gemini-3.1-pro": "Gemini 3.1 Pro", "claude-sonnet-5": "Claude Sonnet 5"}
rows = []
for m in ["gpt-5.5", "gemini-3.1-pro", "claude-sonnet-5"]:
    run = ROOT / f"final_{m}"
    if m == "gemini-3.1-pro":
        u = json.load(open(run / "run_meta.json"))["usage"]
        assert u["calls"] == 8790, "Gemini usage must cover every call of the run"
        tin, tout, tth = u["input"], u["output"], u.get("thinking", 0)
        method = "API usage metadata of all 8,790 calls"
    else:
        t = json.load(open(run / "token_measure.json"))
        tin, tout, tth = t["total_input_tokens"], t["total_output_tokens"], t["total_thinking_tokens"]
        method = t["method"]
    pi, po = PRICE[m]
    cost_in, cost_out = tin / 1e6 * pi, (tout + tth) / 1e6 * po
    rows.append((m, tin, tout, tth, cost_in, cost_out, method))
print("| Model | Calls | Input tokens (M) | Output tokens (M) | Thinking tokens (M) | Input cost (USD) | Output cost (USD) | Total (USD) | Token measurement |")
print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
tot = 0.0
for m, tin, tout, tth, ci, co, method in rows:
    tot += ci + co
    print(f"| {LABEL[m]} | 8,790 | {tin / 1e6:.2f} | {tout / 1e6:.2f} | {tth / 1e6:.2f} | {ci:,.1f} | {co:,.1f} | {ci + co:,.1f} | {method} |")
print(f"| All three | 26,370 | – | – | – | – | – | {tot:,.1f} | |")
json.dump([dict(zip(["model", "input", "output", "thinking", "cost_in", "cost_out", "method"], r)) for r in rows],
          open(ROOT / "analysis_final" / "cost_table.json", "w"), indent=1)
