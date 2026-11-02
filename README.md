# SyntheticConsumers_for_JCC

Source code, raw model responses and comparison datasets for

> **What Profile-Based LLM Synthetic Consumers Can and Cannot Replicate: Evidence from a 30-Country Content
> Survey.** Seungkook Baek (Intellicia) and Hyung-jin Kim (Myongji University). Manuscript for
> the *Journal of Contents Computing*.

Profile-based LLM synthetic consumers, personas drawn from the published respondent profile of KOFICE's *2026
Overseas Hallyu Survey* (30 countries, N = 27,400) rather than digital twins of real respondents, answer three survey questions (overall favorability, recommendation
intention, perceived popularity of 13 content domains). Their country-level answers are compared with the
values printed in the survey report, under direct Likert rating (DLR) and semantic similarity rating (SSR),
with and without persona networks and cross-validated country-offset correction, for three models, against
non-LLM comparators that use the same information.

## Repository layout

| Path | Contents |
| --- | --- |
| `paper/` | the manuscript (`Baek_Kim_JCC_manuscript.docx`) and Supplementary Material (`Baek_Kim_JCC_supplementary.docx`), their Markdown sources (`main_part1-3.md`, `supp.md`), references (`refs.json`) and the builder (`build_docx.js`; every results table is read from `results/analysis_final/paper_tables.md`) |
| `hallyu_twins/` | the Python package (persona synthesis, prompts, model clients, SSR, networks, evaluation) |
| `configs/default.yaml` | model identifiers, training cutoffs, settings |
| `data/pdf_tables/` | **comparison datasets**: values transcribed from the report (`targets_country.csv`; the full 30-country favorability ranking in `targets_xq5_all30.csv`) and the respondent-profile table (`respondent_profile.csv`) |
| `results/final_<model>/` | **raw data**: personas, every prompt as sent (`prompts_r1/r2/b2.jsonl.gz`, checked against the response cache in `prompts_check.json`), every raw model response (`raw_r1.jsonl`, `raw_r2.jsonl`, `raw_b2.jsonl`), per-item answers and SSR probabilities (`scored.csv`), token usage (`run_meta.json`) |
| `results/analysis_final/` | metrics, paired tests, structure checks, network diagnostics, robustness analyses (`rb_*.csv`), cost table, figures, and `paper_tables.md` (every table of the paper) |
| `results/probes/` | prior-knowledge probes (recall of the previous edition; persona-free estimate without the survey description) |
| `results/judge/` | LLM-judge classification of the same SSR free-text answers (GPT-5.5 on all favorability and recommendation answers; Claude Sonnet 5 on every 10th batch) |
| `scripts/` | `run_multicountry.py` (one model, full run), `run_final_analysis.sh` (every table and figure), `make_paper_tables.py`, `make_figures.py`, `make_doc_chart_data.py`, `measure_tokens.py` and `cost_table.py` (cost appendix), `check_gpt_tokens.py` (offline vs API token counts), `count_*_tokens.js` (offline tokenizers), `export_prompts.py` (prompts as sent), `probes.py` (prior-knowledge probes), `judge_rescore.py` (LLM-judge re-scoring of SSR answers), `run_progress.py` (cache coverage of a run), `build_repo.sh` |
| `tests/` | unit tests (`pytest -q`) |
| `verify/` | independent re-computation of the headline numbers, reproducibility check, transcription log |
| `docs/` | pre-registration draft, transcription check, verified reference list, review response |

## Main results

Favorability, all 30 countries (MAE in percentage points):

| | GPT-5.5 | Gemini 3.1 Pro | Claude Sonnet 5 |
| --- | --- | --- | --- |
| Personas, direct rating (DLR) | 30.8 | 28.1 | 30.5 |
| Personas, SSR | 10.8 | 14.7 | 7.8 |
| Same SSR answers scored by an LLM judge | 31.0 | 30.9 | 30.9 |
| Persona-free estimate (B2) | 13.0 | 13.0 | 9.3 |
| SSR + leave-one-out calibration | 6.7 | 6.6 | 5.6 |
| B2 + the same calibration | 7.8 | 5.9 | 6.8 |

No-LLM comparators: 30-country total 8.6, continent mean 7.4, regression on the printed share who know Korea very
well 6.8. SSR beats direct rating, but the judge puts 99.7–100% of the same free-text answers in the top two
options: the gain in level comes from the scoring step, and SSR's country ordering (Spearman 0.55–0.79) from the
intensity of uniformly positive answers. Answers follow persona attributes consistently, and two models reproduce
the human relation between favorability and recommendation across countries. After the same calibration, the
synthetic consumers' error does not differ significantly from the calibrated persona-free estimate or the profile
regression; persona networks do not help. Full tables:
`results/analysis_final/paper_tables.md`. Figure files keep their analysis names; in the manuscript, fig4 is
Figure 2, fig2 Figure 3, fig3 Figure 4, fig9 Figure 5, fig8 Figure 6, and fig5–fig7 are Figures S1–S3.

**Labels.** The data files and code call the persona conditions `Twins DLR` / `Twins SSR` (and the package is
`hallyu_twins`); the manuscript and `paper_tables.md` display them as `Persona DLR` / `Persona SSR`. Only the
display label differs; the values are identical.

## Models

| Model | API identifier | Training cutoff | Settings |
| --- | --- | --- | --- |
| GPT-5.5 | `gpt-5.5` | 2025-12-01 | default temperature, `reasoning_effort: none` |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | 2025-01 | temperature 1.0, `thinking_level: low` |
| Claude Sonnet 5 | `claude-sonnet-5` | 2026-01 | default temperature (not settable) |

All cutoffs precede the report's release (2026-03-30). No tools, web search or retrieval are passed.
SSR uses OpenAI `text-embedding-3-small`.

## Reproduce

```bash
pip install -e ".[openai,anthropic,gemini,dev]"
cp .env.example .env            # add your own keys; never commit .env
set -a; source .env; set +a
pytest -q

# one full run per model (3,000 personas x SSR/DLR, 900 personas x 3 network arms, 30 countries x 3 persona-free estimates)
python scripts/run_multicountry.py --model claude-sonnet-5 --n 100 --n-network 30 --k 3 --b2-reps 3 --embedding openai --out outputs/final_claude-sonnet-5
python scripts/run_multicountry.py --model gpt-5.5        --n 100 --n-network 30 --k 3 --b2-reps 3 --embedding openai --out outputs/final_gpt-5.5
python scripts/run_multicountry.py --model gemini-3.1-pro --n 100 --n-network 30 --k 3 --b2-reps 3 --embedding openai --out outputs/final_gemini-3.1-pro

# analysis: every table and figure of the paper (no model calls; SSR answers are embedded once and cached)
bash scripts/run_final_analysis.sh outputs outputs/analysis_final
```

To re-analyse the released responses without any model calls, run `bash scripts/run_final_analysis.sh results
results/analysis_rerun` (an OpenAI key is still needed to embed the free-text answers for SSR).

One full run is about 8,790 calls per model (about 15M input and 4M output tokens); see the paper's
Appendix B for measured token use and cost (USD 168.5 GPT-5.5, 153.8 Gemini 3.1 Pro, 73.0 Claude Sonnet 5 per full run at list prices).

## Notes

- The microdata path (`hallyu_twins/experiment.py`, 1:1 twins of real respondents with P4 grounding) is
  included for the follow-up study; it was dry-run on synthetic microdata only.
- Values in `data/pdf_tables/` are transcribed from the KOFICE report and remain subject to KOFICE's terms.
- Conflict of interest: the first author is employed by Intellicia, which develops synthetic-consumer research
  services; the corresponding author declares no competing interest. Intellicia's own models were not used.
- `docs/preregistration.md` is the never-frozen draft protocol of the planned microdata study; deviations of this
  table-only study are listed at its top. `docs/review_response.md` lists the pre-submission review and the changes.
