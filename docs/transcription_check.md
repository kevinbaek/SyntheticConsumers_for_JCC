# Transcription check of the report tables

Source: KOFICE, *2026 Overseas Hallyu Survey* summary report (PDF, created 2026-03-30, 70 two-page spreads;
printed page p is PDF page p//2 + 1).

## Pass 1 (first transcription, V3)
Values were transcribed from rendered page images and checked against the PDF text layer and running text.
Five further XQ6 levels were found in the recommendation change box (fig 2-1-11) and added as `list = other`.

## Pass 2 (independent audit, 2026-10-30) — supersedes the counts of pass 1
An auditor who had not done the transcription re-read every value on page images rendered at 250 dpi and
checked the text layer. Evidence per row: `verify/audit/targets_audit.csv`; scripts: `verify/audit/*.py`.

**Targets (`data/pdf_tables/targets_country.csv`): 88 of 88 confirmed, no mismatch.**
- XQ5: p40 fig 2-1-1 (top/bottom 7 and 30-country bar), distribution on the p13 infographic, 2024 value 70.3 (fig 2-1-2, p41).
- XQ6: p62 figs 2-1-10 and 2-1-11, including both change boxes.
- POPMEAN: p58 fig 2-1-8 (printed values, not derived). XQ1 domains: p56 fig 2-1-6 (2025 bars).
- Country-value pairing, item, list label (top/bottom/other), page and the sign of all 18 changes match.
- 83 values also appear in the PDF text layer; 5 are chart-only labels: XQ6 neutral band 26.1 (2025) and 25.1
  (2024), XQ6 low band 6.7 (2024), game 38.3, animation 37.5. The first three are confirmed by arithmetic or text
  (100 − 67.7 − 6.2 = 26.1; 100 − 68.2 − 6.7 = 25.1; "0.5%p 감소" from 6.7 to 6.2).
- Distribution sums: 5.0 + 25.3 + 69.7 = 6.2 + 26.1 + 67.7 = 6.7 + 25.1 + 68.2 = 100.0.
- Implied 2024 values (wave 15 − change): 14 computable, all correct; where the report also prints the 2024 level
  (South Africa XQ6 73.0, Japan XQ6 31.8, Vietnam XQ6 80.8, 30-country XQ5 70.3 and XQ6 68.2) it matches.
  Four XQ5 changes (UK, Spain, US, Australia) have no printed 2025 level and are not used by B1.
- Correction of pass 1: the China XQ6 2024 value 66.6 is implied (61.3 + 5.3); the report prints only 61.3 and the
  5.3 pp fall, so it is not an independent match.

**Respondent profile (`data/pdf_tables/respondent_profile.csv`): 961 of 961 values confirmed** (31 row totals and
930 shares, pp. 31–32; column order checked on the image). Rebuilding each country's n from total × share per
dimension: median deviation 0.49%, largest relative +2.55% (Chile, nationality rows, n = 500), all within the range
allowed by one-decimal rounding. (Pass 1 reported "median about 1.2%"; the audit value is 0.49%.)

## Open definitional point: POPMEAN
Fig 2-1-8's note says the country value is the arithmetic mean of the domains' "대중적 인기(4+5)" shares, without
stating the number of domains. The analysis uses all 13 domains surveyed in 2025 (the report's country discussion
counts character and performance among the domains); `popmean_sensitivity.csv` repeats the evaluation with the 11
domains common to earlier waves. 30-country mean of domain totals: 42.9 (13) vs 44.0 (11).
