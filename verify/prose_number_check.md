# Verification report: numeric and data-tied claims in ms_part1–3.md

Data root: `/home/claude/hallyu-twins/outputs/analysis_final/`. Model order in the brackets is GPT / Gemini / Claude unless stated.

## A. Mismatches (fix these)

1. **ms_part2.md §4.8.** "...changed its favorability MAE by at most 0.6 pp and its other MAEs by at most 1.9 pp."
   - **Data:** GPT-5.5 POPMEAN B2 went from 11.7403 (metrics.csv, B2 persona-free LLM, POPMEAN) to 9.7846 (rb_probes.csv, "B2 without survey description", POPMEAN). The change is −1.9557 pp, which rounds to 2.0.
   - The other changes are within bounds. Gemini XQ6 moved +1.25; the largest favorability change is Claude all-30 at −0.64.
   - **Fix:** "at most 2.0 pp".

2. **Table 6 caption (ms_part2.md §4.3).** "p from exact sign-flip tests over countries".
   - **Data:** every row of rb_xq5_all30_paired.csv has `test = "Monte Carlo (200000)"`. With 30 countries there are 2^30 sign patterns, which were not enumerated.
   - Only the 14–19-country contrasts in rb_signflip.csv are exact.
   - **Fix:** "p from Monte Carlo sign-flip tests over countries (200,000 draws)".

3. **ms_part3.md §5.1.** "SSR twins beat a uniform guess, the mean of the other countries and, by a wide margin, direct ratings."
   - **Data, mean of the other countries:** Gemini SSR favorability MAE is 16.66, against 15.06 for the LOCO mean (metrics.csv, XQ5). Gemini's twins are worse, so they do not beat it.
   - **Data, direct ratings:** on popularity, SSR − DLR is +2.1 / −3.7 / −2.9 pp, all Holm p = 1.0 (paired.csv). GPT's SSR is worse than DLR there, so the "wide margin" holds only for favorability and recommendation.
   - **Fix:** "...beat a uniform guess and, on favorability and recommendation, direct ratings by a wide margin; they beat the mean of the other countries except for Gemini's favorability (16.7 against 15.1 pp)."

4. **ms_part2.md §4.1.** "Under DLR, 99.7% (GPT-5.5), 97.1% (Gemini 3.1 Pro) and 99.4% (Claude Sonnet 5) of all twins chose one of the top two options for favorability".
   - **Data:** these are the sample-size-weighted 30-country totals (all30.csv, syn_t2b; recomputed as 99.73 / 97.07 / 99.36).
   - The unweighted share of all 3,000 twins is 99.80 / 97.03 / 99.43, from the mean of the 30 country estimates in country_estimates_wide.csv.
   - **Fix:** either change "of all twins" to "of twins (30-country total weighted by sample size)", or give 99.8%, 97.0% and 99.4%.

## B. Unsupported or overstated claims

5. **ms_part3.md §5.1.** "...and no difference between the two approached significance (Section 4.2)."
   - **Data (paired.csv, CAL-STYLE vs B-XITEM):**
     - Gemini POPMEAN: diff +3.73, 95% CI +1.04 to +6.14, unadjusted p = 0.0076, Holm p = 0.160. B-XITEM was nominally better, and the CI excludes zero.
     - GPT XQ6: diff −1.02, CI −2.04 to +0.04, unadjusted p = 0.059.
   - §4.2 correctly says "no difference ... was significant (... all adjusted p ≥ 0.160)", which is true after adjustment.
   - **Fix:** "and no difference survived the Holm adjustment (Section 4.2); the one nominal difference favoured the regression without twins (Gemini, popularity)."

6. **"Most of the error" claims for SSR.**
   - **Where:** ms_part2.md §4.1 heading "SSR removes most of the level error"; ms_part1.md §1 "SSR removes most of that error"; ms_part3.md §6 "Semantic similarity rating removed most of that error".
   - **Data:** for Gemini favorability, SSR removed 12.65 of 29.31 pp (43%). The SSR−DLR row is in paired.csv and DLR MAE is in metrics.csv.
   - All other model–item pairs exceed half: GPT XQ5 58%, Claude XQ5 66%, and XQ6 63–70%.
   - **Fix:** "removes most of the level error in five of six model–item pairs (43% for Gemini's favorability)", or "much of".

7. **"Most of the variance" claims for persona attributes.**
   - **Where:** ms_part2.md §4.6 "persona attributes explained most of the variance in favorability: adjusted R² of 0.42–0.65 under SSR"; ms_part3.md §5.1 "...explain most of the variance in their favorability".
   - **Data:** Gemini SSR XQ5 r2_persona = 0.417, and r2_both = 0.432 (variance_decomposition.csv). That is less than half of the variance.
   - **Fix:** "explained much of the variance (adjusted R² 0.42–0.65 under SSR, 0.63–0.82 under DLR)", or state "most" only for DLR and for GPT and Claude under SSR.

8. **ms_part2.md §4.6.** "...and fell slightly with age (Figure 8)."
   - **Data:** persona_gradients.csv, XQ5, SSR, age_band.
     - Claude: 80.3% → 71.8%, ρ(code, score) = −0.30.
     - GPT: 79.8% → 77.7%, ρ = −0.03, p = 0.10.
     - Gemini: 83.7% → 82.0% with a peak at 20–29, and ρ = +0.03 (p = 0.08) on the expected score.
   - Figure 8 shows only knowledge of Korea, not age.
   - **Fix:** "...and fell with age for Claude's twins (80% at 15–19 to 72% at 50–59) but hardly at all for GPT's and Gemini's". Also drop "(Figure 8)" from the age clause, or cite persona_gradients.

9. **ms_part3.md §5.1.** "...because the model's persona-free estimate is as accurate as the twins' average..."
   - True on the listed countries (§4.1).
   - On all 30 countries (rb_xq5_all30_paired.csv, SSR vs B2) it does not hold:
     - Claude SSR was better than B2 by 1.5 pp (p = 0.019).
     - GPT SSR was better by 2.3 pp (p = 0.003).
     - Gemini SSR was worse by 1.7 pp (p = 0.008).
   - **Fix:** "as accurate as the twins' average on the listed countries", or mention the 30-country exception.

10. **ms_part2.md §4.1.** "Figure 3 shows the pattern: DLR places almost every country near 100%, while SSR orders countries but squeezes them into a band at most about 10 points wide."
    - Figure 3 also has two popularity panels.
    - For popularity, listed-country DLR estimates span 15.9–74.0%, and the SSR band is 12.1 / 19.1 / 14.0 pp wide for Claude / Gemini / GPT (Gemini 38.4–57.4; country_estimates_wide.csv).
    - The statement is true for favorability and recommendation: the widest SSR band there is 9.8 pp, Claude XQ5.
    - **Fix:** "Figure 3 shows the pattern for favorability and recommendation: ..."

11. **ms_part2.md §4.1.** "...and B2 ranked countries as well as or better than the twins (ρ 0.71–0.84)."
    - SSR ranked better than B2 in 2 of 9 cases (metrics.csv):
      - Claude XQ5: SSR 0.816 against B2 0.784.
      - GPT XQ6: SSR 0.732 against B2 0.715.
    - **Fix:** "B2 ranked countries about as well as or better than the twins".

12. **ms_part3.md §5.2.** "...its anchors bound the attainable range at about 4–90% T2B (Section 4.7)".
    - This is inconsistent with §4.7 and rb_anchor_selftest.csv:
      - Most-negative anchor: 1–16% (0.6–16.0).
      - Most-positive anchor: 88–90% for favorability, 72–79% for recommendation, 70–80% for popularity.
    - "About 4–90%" fits favorability only (floor 3.1–4.5%, ceiling 88.1–89.6%).
    - **Fix:** "at about 3–90% T2B for favorability, and lower at the top for the other items (Section 4.7)".

13. **Country-count statements.**
    - **Where:** ms_part3.md §5.4 "inference rests on 14 to 30 countries per item"; ms_part1.md §3.8 "Because 14 to 19 countries give the bootstrap little to work with".
    - **Data (metrics.csv, n):**
      - CAL-STYLE and B-XITEM use 13 countries (XQ5, XQ6) and 11 (POPMEAN).
      - B1 uses 4 (XQ5 listed), 8 (XQ5 all 30) and 10 (XQ6) countries.
    - **Fix:** "11 to 30 countries per item (B1: 4–10)", and "11 to 19 countries" in §3.8.

## C. Minor notes (wording or precision; optional)

14. **Resolution of "Holm-adjusted p < 0.001".**
    - **Where:** Abstract; §4.1 "all Holm-adjusted p < 0.001"; §4.5 "Gemini's favorability ... worse by 2.0 pp (Holm-adjusted p < 0.001)".
    - These match paired.csv (p_holm = 0.0), but that value is a bootstrap p of exactly 0.
    - The code (`table_eval.paired_mae_diff`: `2*min(mean(bs<=0), mean(bs>=0))`, B = 5,000) can resolve p only down to 0.0004. After ×24 Holm, the defensible bound is about p < 0.01.
    - The exact sign-flip p for the 14-country favorability contrasts is 0.00012 for SSR vs DLR and 0.0002 for Gemini N3 vs round 1 (rb_signflip.csv). Holm-adjusted, those are about 0.002–0.004, not < 0.001. Recommendation (19 countries, p ≈ 4e-6) does reach < 0.001.
    - **Suggested wording:** "Holm-adjusted p < 0.01" (or < 0.005).

15. **ms_part2.md §4.4.** "The persona-free estimate reproduced the profile best (MAE 7.7–11.9 pp, ρ 0.91–0.94)".
    - Best in MAE, yes.
    - In ρ, Claude's DLR (0.9188) edges Claude's B2 (0.9176) (domains.csv). This is negligible, so it can be left as is or changed to "best in level".

16. **ms_part3.md Appendix A.** "(median deviation 0.49%, ...)"
    - 0.49% is the median including the "total" row (verify/audit/profile_sums.py).
    - Over the seven demographic dimensions the median is 0.47%. The largest value, +2.55% for Chile nationality, is correct.

17. **Table 9a caption "(900 twins × 15 items)" and §4 intro "no unrecovered errors".**
    - For Claude N2 there are 13,499 pairs, not 13,500 (network.csv; parse_stats.json). Twin 23GER-030-016 lacks one round-2 item in final_claude-sonnet-5/scored.csv.
    - All 8,790 calls had errors = 0 (run_meta.json), so the §4 sentence is accurate for calls. The caption could add "(one Claude N2 answer missing)".

18. **ms_part1.md §3.3.** "If that figure applies, Gemini's cutoff also precedes the survey fieldwork."
    - GPT-5.5's cutoff (1 Dec 2025) falls inside the fieldwork window (13 Nov–12 Dec 2025), and Claude's (Jan 2026) is after it.
    - "Also" can be misread as "like the other models". Consider: "...Gemini's cutoff, unlike the other two, also precedes the survey fieldwork."

19. **Two correlations with different methods.** §3.7's "r = 0.93" (Pearson over 19 countries; recomputed 0.925) and §4.6's "0.86" (Spearman over 12 countries; item_coherence.csv) are both correct, but they use different statistics. Pearson over the same 12 countries is 0.926. Consider labelling the statistic in both places to avoid an apparent conflict.

## D. Claims I could not verify from the provided files

- **Report facts not in the transcribed files:**
  - Fieldwork 13 Nov–12 Dec 2025; aged 15–59; two online panels per country; post-stratification by region, sex and age.
  - Sampling errors ±0.59 pp and ±2.14–4.38 pp.
  - PDF of "70 spreads, created 30 March 2026"; profile table on pp. 31–32; "250 dpi" audit images.
  - "earlier waves, which began in 2012".
  - "the Philippines is said to rank first in eight domains".
  - That printed 2024 levels for South Africa, Japan, Vietnam (XQ6) and both totals match wave-15 minus the change. No 2024 country levels are in targets_country.csv.
  - The sample sizes (500–2,100, sum 27,400) and the release dates (30 Mar 2026; 7 Apr 2025) are consistent with `hallyu_twins/codebook.py`, but that is itself a transcription.
- **Vendor documentation:** training cutoffs as stated by OpenAI, Anthropic and Google (run_meta.json agrees with Table 1), and list prices "checked on 30 October 2026". The costs are arithmetically consistent with the stated prices.
- **All literature figures in §2 and §3.4.** Examples: Wang2026 (30 countries, 42 items, 0.44, 0.52, −0.03, ~60%, 41 of 42, 0.03 vs 0.21, 7–8B models); Toubia2025 (500 answers); Peng2026 (five distortions); Lukauskas2026 (37 models); Maier2025 (57 surveys, 9,300 responses, 90% of test–retest reliability, six anchor sets).
- **Content of the figures beyond what the CSVs show:** for example Figure 9's "points: mean; bars: range". Figures 3 and 8 were inspected.
- **"Development pilots used another Anthropic model" / Claude Sonnet 5.5 cutoff "June 2026":** not in the analysis files.

## E. Count

I checked about 500 numeric claims, counting each value in a list and each end of a range separately. That covers the abstract, §1, §3–§6, the figure and table captions and notes, the hand-typed Tables 1, 2 and C1, and Appendices A–C. I recomputed from the CSVs with pandas, the transcribed targets, the code defaults (IPF 200 iterations; B = 2,000 / 5,000 / 1,000; seeds; settings), run_meta, parse_stats, network.json, token files, the probe metadata (93 calls) and the reproducibility folders (repro_a = repro_b = analysis_final). This excludes about 15 literature figures in §2. Apart from items 1–19 above, every checked claim matched the data within normal rounding.
