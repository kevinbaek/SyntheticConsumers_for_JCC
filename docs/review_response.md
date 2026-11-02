# Internal pre-submission review and response

An independent referee report (written by a reviewer agent that had not seen the authors' reasoning, with access to
the manuscript draft, the code, the raw responses and the KOFICE report) and the authors' own review were combined.
No reported number was changed by hand: every change below is either new text, a new analysis of the same
responses, a new transcription double-checked against the PDF, or a small, separately identified probe.

| # | Concern | Response | Where |
|---|---|---|---|
| M1 | Ground truth selected on the outcome (top/bottom 7); the report prints the full 30-country XQ5 ranking on p. 38 | Transcribed the full ranking (`data/pdf_tables/targets_xq5_all30.csv`; names and values matched to the text layer and the page image; listed 14 identical to the main file; n-weighted mean 69.67 vs printed 69.7). XQ5 now evaluated on all 30, the 14 listed and the 16 middle countries. For XQ6 and POPMEAN: band check for unlisted countries and the unlisted-group mean backed out of the 30-country total; within-top-7 and within-bottom-7 rank correlations. The pre-specified 14/19/14-country analysis is unchanged and still reported | `rb_xq5_all30`, `rb_censoring`, `rb_within_group`; §3.1, §3.8, §4 |
| M2 | Comparators not matched on information; B5 includes the target; B1 change-selected; LOCO anti-correlated by construction | Comparator table now states each method's information, including the twins (target country's printed profile). Added B-PROFILE (leave-one-out regression on the printed share who know Korea very well) and a leave-one-out B5. B1 extended to 8 XQ5 countries with the full ranking; its selection on change is stated. Undefined metrics stated | §3.6, `rb_listed_extra`, `rb_xq5_all30` |
| M3 | CAL-STYLE does not identify a response style (XQ5 and XQ6 are near-duplicates) | Renamed in the text as a country-offset correction from the same country's other items; interpreted only against B-XITEM (same information); RQ4 reworded; CAL-LOCO also fitted on the 14 extremes and tested on the 16 middle XQ5 countries | §1, §3.7, `rb_xq5_all30` |
| M4 | Contamination via earlier waves; B2 wording describes the survey | Text corrected (wave-15 values cannot be memorised, earlier waves can). Probes run for all three models: previous-edition recall (all answers self-labelled guesses) and B2 without the survey description. Twins' error against the previous wave vs the current wave reported. Cutoff sources and access dates given; Gemini's cutoff is taken from the Gemini 3 Pro model card because the 3.1 Pro page states none | §3.3, `rb_probes`, `rb_wave14`, `configs/default.yaml` |
| M5 | SSR anchors compress the attainable range; XQ6 low anchors not monotone | Anchor self-test reported (each anchor scored as if it were an answer); SSR level metrics interpreted with that ceiling; rank metrics emphasised; limitation and a negation-robust scorer as future work | `rb_anchor_selftest`; §3.4, §5 |
| M6 | DLR vs SSR confounded with Monte Carlo noise; reversal also renumbers options | Twin-level Monte Carlo SE and a two-level bootstrap (twins within countries, then countries) for MAE and the SSR−DLR difference; forward vs reversed DLR reported separately with a sign-flip test; renumbering stated | `monte_carlo_error`, `rb_two_level`, `rb_dlr_reversal` |
| M7 | Personas from margins; "beyond country labels" not earned without a label ablation | Independence assumptions stated; achieved vs printed margins reported; the persona-free estimate (B2) is the country-label-only comparator at the aggregate level; variance decomposition of twin answers into country and persona parts; title and claims worded to what these support. A label-only twin arm is listed as the next experiment | §3.2, `rb_margins`, `variance_decomposition`; title |
| M8 | Network: one round, k = 3, SSR only; echo risk | Described as one-shot peer exposure; results split by item type (the draft protocol's H3); verbatim-repeat share and neighbour similarity reported; N2 vs N1 added to the sign-flip table | §3.5, `rb_verbatim`, `network.json`, `rb_signflip` |
| M9 | Inference ignores within-country error; small n; seeds | Two-level bootstrap; exact sign-flip tests; noise ceiling from human sampling error; Holm family stated; duplicate personas and identical responses counted and disclosed | `rb_two_level`, `rb_signflip`, `rb_noise_ceiling`, `rb_duplicates` |
| M10 | Code–text disagreements | Each item reconciled in the text (split accuracy, spread on listed countries, undefined metrics, Holm family, renumbered reversal, SSR-only round 2, sampling of sex/nationality/knowledge, homophily features, n per correction). Rendered prompts released and verified against the cache keys (8,790/8,790 per model). README COI fixed | §3, `prompts_*.jsonl.gz`, `prompts_check.json` |
| M11 | Pilot history | Disclosed: a Japan pilot and a 10-per-country test were scored against the targets during development; the changes made afterwards are listed | Appendix C |
| M12 | Prompt details (screening examples, B2 description, knowledge of Korea, item order) | Disclosed as limitations; B2 neutral probe run | §3.4, §5 |
| M13 | COI, AI assistance, vendor neutrality | Declarations expanded: an Anthropic model assisted the writing and one evaluated model is Anthropic's; model comparisons are descriptive | Declarations |
| M14 | Aggregates thin | 3-band and 13-domain comparisons presented as descriptive | §4 |

Not done (stated as limitations or future work): country-label-only and label-swap twin arms, replicate persona
draws (R ≥ 5), negation-robust SSR scorer, round-2 DLR, network dose arms, wave-14 report transcription for a full B1.

## Final revision (manuscript v2, Word file)

| # | Item | Action |
|---|---|---|
| F1 | 11-domain sensitivity of the unlisted-popularity check compared an 11-domain implied human mean with the 13-domain synthetic mean | Code fixed in `hallyu_twins/robustness.py` (`_pop11`): the synthetic side now also averages 11 domains; the 13-domain rebuild is asserted to equal the main estimates. Only the 9 "POPMEAN (11 domains)" rows of `rb_censoring.csv` changed; all other rows are identical (max diff 1e-14). Reported in Appendix Table D9 |
| F2 | GPT-5.5 token counts were offline | Checked on 32 fresh API calls (`outputs/final_gpt-5.5/token_check.json`): input within 0.1% (≤1 token per call), output 0.9% below the API count; stated in Appendix B |
| F3 | Reproducibility | `verify/reproducibility.sh`: two reruns byte-identical and identical to `analysis_final` (metrics, paired, estimates, all30, domains, network) |
| F4 | Number checks | Every results table in the Word file is read verbatim from `paper_tables.md` (generated from the CSVs); prose numbers were checked against the CSVs by the authors and by an independent verifier |
| F5 | Citations | Six citations added and verified (`docs/references_verified.md`); one unverifiable suggestion dropped |
| F6 | Pipeline | `scripts/run_final_analysis.sh` now also runs the robustness module, the cost table and the Graphviz Figure 1 |

## Second review round

| # | Comment | Action | Where |
|---|---|---|---|
| R2-1 | English-only prompts and cultural alignment (Europe +18–28 pp) | Language-group analysis on all 30 countries: raw bias is smaller in English-official countries and larger in continental Europe, but after adjusting for the human level the group differences are −0.8 to +0.0 and −1.5 to −0.3 pp (CIs include 0); discussion of what this can and cannot exclude, a local-language arm as the next test, literature on prompting language | `rb_language.csv`, §4.6, §5.3, Table S18 |
| R2-2 | One-shot network vs interaction as such | Limitations separate what the design shows from what it cannot show (same-country synthetic neighbours, one round, anchoring instruction, Claude's verbatim repetition) | §4.7, §5.6 |
| R2-3 | Parametric knowledge vs persona modelling; title | What the twins' 30-country estimates track: printed knowledge share vs the model's own recall and persona-free estimate, and leave-one-out accuracy of each information source; title changed to a replication question; B2 described as a country-level belief, not a label-only twin | `rb_prior.csv`, §4.6, §5.4, Table 8 |
| R2-4 | Preprints now published | LiA2025 → NeurIPS 2025; Peng2026 Science Advances confirmed; Park2024 later title noted; others remain preprints (checked 2026-10-30) | `paper/refs.json` |
| R2-5 | Distorted back tables | Supplementary tables in landscape; main tables switch to landscape automatically when the minimum word-safe widths do not fit portrait; model names never break | `paper/build_docx.js` |
| R3-1 | Narrow the practice conclusions | Table 9 lists uses as hypotheses with the validation each needs; conclusion limited to a moderate reproduction of the country ordering of favorability; ranking claims qualified by the within-bottom-7 result (n = 7, imprecise) | §5.5, §6 |
| R3-2 | SSR gain vs scoring artifact | Same answers re-scored: single anchor sets / leave-one-out, nearest anchor, LLM judge (GPT-5.5, all 18,000 answers; Claude Sonnet 5 on 10% for agreement); range of real-answer scores; "attainable range"/"cannot reach 100%" wording replaced; non-monotone recommendation anchors treated as a validity problem. Human coding not done (stated) | `rb_ssr_variants.csv`, `rb_ssr_range.csv`, `rb_judge.csv`, §4.5, §5.2, Table 7, Figure 5 |
| R3-3 | Separate country name and persona | Not run (needs new twin arms); title and claims narrowed accordingly; arms listed as next experiments | §5.4, §5.7 |
| R3-4 | Fair calibration | CAL-LOCO applied identically to SSR, DLR and B2 (30 countries and listed countries) with paired sign-flip tests | `rb_calibrated.csv`, §4.2, Table 4, Table S2 |
| R3-5 | Non-significance ≠ equivalence; 30-country first | Results reordered (30 countries first); equivalence wording removed; network conclusion limited to the design | §3.8, §4 |
| R3-6 | Gemini cutoff source | The 3.1 Pro API page (updated 2026-10-09) states no cutoff; its model card refers to the Gemini 3 Pro card (January 2025); both cited | §3.3 |
| R3-7 | Table 3 note on B5-LOO | Rank metrics omitted for constant predictions and for predictions that vary only by leaving out the target country | Tables 3, 5 |
| R3-8 | POPMEAN definition | The report's note under figure 2-1-8 gives no domain count; 13-domain main analysis with 11-domain sensitivity kept | S1 |
| R3-9 | Length | Abstract 199 words; main text about 6,800 words (excluding abstract, tables and references) in 22 A4 pages incl. references; appendices and 29 tables moved to the Supplementary Material | `paper/` |

Cost of the second round: judges USD 6.8 (GPT-5.5) and 0.6 (Claude Sonnet 5); no new twin answers were generated.

## Independent verification of the second-round text

A verifier who had not written the text checked every changed number and claim against the CSVs (`verify_report2`, summarised here). All findings were applied without changing any result:

- Wrong transcriptions fixed: DLR middle band 0.3–2.9%; only the first recommendation anchor set is non-monotone; Claude repeated about half of its answers verbatim (two-thirds of own-preference answers); "11–30 countries"; real SSR scores "rarely" approach the extremes (no round-1 answer above 98.7%).
- Overstatements narrowed: "not significantly more accurate with twins" instead of "with or without twins"; DLR+CAL contrast p = 0.044 / 0.048 (Claude, Gemini) and 0.061 (GPT, not significant); listed-country exceptions reported (GPT popularity DLR+CAL better, p = 0.046; Claude favorability SSR+CAL better, p = 0.004); within-group ρ with n = 7 flagged as imprecise; Gemini's near tie between knowledge share and recall stated, claim rested on regression weights; language result limited to the SSR twins; network section adds Claude recommendation (+0.2 pp, Holm p = 0.009), Gemini recommendation/popularity (+0.6 / +1.4 pp, n.s.), homophily vs random for Claude recommendation (Holm p = 0.042) and homophily vs self-reflection (none significant after Holm); abstract and conclusion say "moderately reproduced the country ordering of favorability".
- Consistency: Table 4 and Table S1 now share one Monte Carlo p per contrast (same country order); table captions and notes aligned (Tables 3, 5, S6, S8, S9); exploratory analyses listed identically in §3.8 and S4; anchor similarity added as Table S29; `docs/preregistration.md` points to Supplementary S4.

## Neutral reframing (authors' revision, after the second round)

No data result changed. The changes are terminology, scope and emphasis:

- **Terminology and scope.** The synthetic respondents are personas drawn from the report's published margins, not digital twins of real people built from their own data. The manuscript now calls them profile-based synthetic consumers (tables: `Persona DLR` / `Persona SSR`; the data files keep the condition label `Twins …`), states the distinction in §1 and §3.2, and limits the conclusions to this lowest-information case (§5.4, §5.6). Title: "What Profile-Based LLM Synthetic Consumers Can and Cannot Replicate: Evidence from a 30-Country Content Survey".
- **Persona-level structure (§4.6, descriptive).** Results already in Tables S17 and S19 are now reported in the main text, with two additions computed from the existing responses: persona gradients by attribute (new Table S30) and the cross-item correlations of the persona-free estimate (added to Table S19). Favorability rises with the persona's knowledge of Korea in every model and mode; age and sex gradients are smaller and differ in direction between models; the same persona's DLR and SSR answers agree only moderately. The cross-item structure is reproduced by SSR for two models but by the persona-free estimate for all three (ρ 0.83–0.99 against human 0.82–0.86), so it is not attributed to the personas. Segment estimates are described as unvalidated.
- **Wording.** Calibrated results stay one-sided ("not significantly more accurate"), with the listed-country result in favour of the persona-free estimate repeated in the summaries; "moderately" and "continuous human benchmarks" kept in the abstract and conclusion; every unfavourable result (scoring artifact, anchor dependence, B-PROFILE and prior-knowledge comparisons, network results) is retained. An independent verifier checked the reframed text twice against the CSVs.
- **Practice table.** Segment-level estimates added to Table 9 as a use that needs validation against respondent-level human data.
- **Conclusion (authors' addition).** A closing paragraph states that the main gap is a country-level offset (compressed between-country differences, overestimation growing as human favorability falls; §4.1, §4.3, §4.7) that cross-validated correction with human values largely removes, and frames post-training on paired human and synthetic data as an untested hypothesis with an explicit test (outperform simple calibration on held-out countries, items and waves without the target country's human values). §5.7 uses the same wording; the conflict of interest remains declared.
