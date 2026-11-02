> **Status.** Draft protocol written for the planned microdata study (1:1 twins of real respondents). It was never
> frozen or registered. The table-only study reported in the paper deviates from it: no microdata, so H1 and H4
> (individual accuracy, label swap) were not tested; H2 was tested with country-level T2B metrics rather than KS and
> heterogeneity ratios; H3 used k = 3 neighbours (not 5), a 30-per-country subsample and an SSR-only second round;
> bootstrap resamples were 2,000 (intervals) and 5,000 (paired tests) instead of 1,000; no TOST equivalence test was
> run; anchors were not tagged with a commit hash. Development pilots are disclosed in the paper's Supplementary Material S4.

# Pre-registration (draft for OSF, to be frozen before the confirmatory run)

## Hypotheses
- **H1 (grounding)** P4 > P2 on within-country individual accuracy (Fisher-mean r_wc) for XQ5, XQ6 and domain favorability.
- **H2 (SSR)** SSR > DLR on distributional similarity (KS) and heterogeneity ratio (HR closer to 1), same twins and model.
- **H3 (network)** N-homophily > N-self and N-random on country-level accuracy for social-perception items (XQ1 popularity), with no variance collapse (HR >= 0.8). Not expected for own-preference items (XQ5, XQ6).
- **H4 (stereotype)** Under label swap, synthetic country means follow the *shown* country more than the true one for P1/P2, less for P4.

## Success criteria for "beyond country-level inference" (all four must hold, per model)
1. r_wc(P4, SSR, MAIN) >= r_wc(B3: multinomial logit trained on wave 14 with the same features) **and** > 0.21 (Wang, 2026 demographic benchmark).
2. Country-level CA = r_bc / split-half ceiling >= 0.80.
3. Mean absolute T2B level error <= B4 (same-continent leave-one-out) and reported against B1 and B2.
4. HR_dist within [0.8, 1.2].

## Fixed choices
- SSR mapping: Maier min-subtraction, T = 1 (primary); softmax with tau chosen on wave-14 twins only (secondary). Anchor sets in `elicit.py` frozen at commit hash X.
- Embedder: text-embedding-3-small. Twins: 100 per country (stratified by sex x age band), 30 per country for ablations (nested).
- Network: k = 5 within country, homophily on P4 features (never outcomes), one exposure round.
- Models: listed in `configs/default.yaml`; cutoffs recorded with source and access date. Tools/web/retrieval off.
- Inference: country-cluster bootstrap (1,000), Holm correction across H1-H4, TOST equivalence margin 5 pp for level.
- Reporting: all conditions x models (specification curve), including failures. Subgroup (sex, age band, continent) results.

## Deviations
Any change after freezing is logged here with date and reason.
