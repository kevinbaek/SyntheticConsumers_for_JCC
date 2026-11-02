## Table: no human data for the target country

| Model | Method | Favorability MAE (95% CI) | Favorability ρ | Recommendation MAE (95% CI) | Recommendation ρ | Popularity MAE (95% CI) | Popularity ρ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona, DLR | 32.7 (25.5–39.9) | 0.65 | 33.2 (27.3–39.0) | 0.48 | 8.2 (5.7–10.4) | 0.77 |
| GPT-5.5 | Persona, SSR | 13.6 (7.7–20.0) | 0.61 | 10.0 (7.5–12.9) | 0.73 | 10.3 (6.3–14.1) | 0.70 |
| GPT-5.5 | Persona-free estimate (B2) | 15.7 (9.7–21.8) | 0.71 | 10.8 (7.0–15.0) | 0.72 | 11.7 (9.4–14.1) | 0.83 |
| Gemini 3.1 Pro | Persona, DLR | 29.3 (22.6–36.2) | 0.61 | 29.7 (24.7–34.9) | 0.51 | 11.6 (7.9–15.2) | 0.69 |
| Gemini 3.1 Pro | Persona, SSR | 16.7 (10.2–23.3) | 0.73 | 11.1 (7.3–15.0) | 0.53 | 7.9 (5.3–10.8) | 0.74 |
| Gemini 3.1 Pro | Persona-free estimate (B2) | 15.8 (10.5–21.3) | 0.82 | 12.9 (8.8–17.5) | 0.79 | 6.9 (4.6–9.6) | 0.82 |
| Claude Sonnet 5 | Persona, DLR | 32.3 (25.3–39.4) | 0.47 | 32.9 (27.3–38.5) | 0.66 | 11.3 (7.8–15.3) | 0.56 |
| Claude Sonnet 5 | Persona, SSR | 11.1 (6.4–16.2) | 0.82 | 9.8 (6.6–13.4) | 0.74 | 8.3 (5.7–10.9) | 0.67 |
| Claude Sonnet 5 | Persona-free estimate (B2) | 11.6 (7.1–16.2) | 0.78 | 9.3 (6.8–12.3) | 0.80 | 8.9 (6.3–11.5) | 0.84 |
| – | 30-country total (B5) | 14.0 (11.7–16.5) | – | 11.1 (8.3–14.5) | – | 10.9 (9.5–12.5) | – |
| – | Uniform 40% (B0) | 27.0 (20.0–34.4) | – | 26.8 (21.3–32.3) | – | 10.9 (9.0–12.8) | – |

## Table: all metrics, Favorability (XQ5)

| Model | Method | n | MAE (pp) | 1−MAE | JS sim. | Spearman ρ | Bias (pp) | Spread ratio | Top/bottom-7 accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | 14 | 32.7 | 0.67 | 0.812 | 0.65 | 32.7 | 0.03 | 0.43 |
| GPT-5.5 | Persona SSR | 14 | 13.6 | 0.86 | 0.973 | 0.61 | 12.5 | 0.13 | 0.71 |
| GPT-5.5 | Persona SSR + CAL-LOCO | 14 | 9.5 | 0.90 | 0.989 | – | -0.4 | 0.74 | – |
| GPT-5.5 | Persona SSR + CAL-STYLE | 13 | 4.2 | 0.96 | 0.998 | 0.85 | -0.1 | 0.84 | 1.00 |
| GPT-5.5 | B2 persona-free LLM | 14 | 15.7 | 0.84 | 0.968 | 0.71 | 15.3 | 0.31 | 0.86 |
| Gemini 3.1 Pro | Persona DLR | 14 | 29.3 | 0.71 | 0.875 | 0.61 | 29.3 | 0.15 | 0.71 |
| Gemini 3.1 Pro | Persona SSR | 14 | 16.7 | 0.83 | 0.962 | 0.73 | 16.4 | 0.13 | 0.86 |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO | 14 | 8.4 | 0.92 | 0.992 | – | -0.3 | 0.83 | – |
| Gemini 3.1 Pro | Persona SSR + CAL-STYLE | 13 | 4.5 | 0.95 | 0.997 | 0.85 | -0.5 | 0.87 | 1.00 |
| Gemini 3.1 Pro | B2 persona-free LLM | 14 | 15.8 | 0.84 | 0.970 | 0.82 | 15.8 | 0.38 | 1.00 |
| Claude Sonnet 5 | Persona DLR | 14 | 32.3 | 0.68 | 0.822 | 0.47 | 32.3 | 0.08 | 0.71 |
| Claude Sonnet 5 | Persona SSR | 14 | 11.1 | 0.89 | 0.983 | 0.82 | 9.1 | 0.25 | 0.86 |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO | 14 | 6.4 | 0.94 | 0.995 | – | -0.2 | 0.88 | – |
| Claude Sonnet 5 | Persona SSR + CAL-STYLE | 13 | 3.6 | 0.96 | 0.998 | 0.87 | -0.4 | 0.99 | 1.00 |
| Claude Sonnet 5 | B2 persona-free LLM | 14 | 11.6 | 0.88 | 0.983 | 0.78 | 9.1 | 0.31 | 0.86 |
| – | B0 uniform | 14 | 27.0 | 0.73 | 0.926 | – | -27.0 | 0.00 | – |
| – | B5 30-country total | 14 | 14.0 | 0.86 | 0.982 | – | 2.7 | 0.00 | – |
| – | LOCO mean | 14 | 15.1 | 0.85 | 0.979 | – | -0.0 | 0.08 | – |
| – | LOCO continent mean | 14 | 10.6 | 0.89 | 0.985 | 0.11 | -1.8 | 0.64 | 0.71 |
| – | B-XITEM cross-item regression | 13 | 3.6 | 0.96 | 0.998 | 0.83 | -0.1 | 0.96 | 1.00 |
| – | B1 carry-forward | 4 | 3.9 | 0.96 | 0.998 | 1.00 | 0.6 | 1.29 | 1.00 |

## Table: all metrics, Recommendation (XQ6)

| Model | Method | n | MAE (pp) | 1−MAE | JS sim. | Spearman ρ | Bias (pp) | Spread ratio | Top/bottom-7 accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | 19 | 33.2 | 0.67 | 0.812 | 0.48 | 33.2 | 0.04 | 0.57 |
| GPT-5.5 | Persona SSR | 19 | 10.0 | 0.90 | 0.988 | 0.73 | 0.1 | 0.15 | 0.86 |
| GPT-5.5 | Persona SSR + CAL-LOCO | 19 | 8.1 | 0.92 | 0.991 | – | 0.1 | 0.69 | – |
| GPT-5.5 | Persona SSR + CAL-STYLE | 13 | 3.3 | 0.97 | 0.998 | 0.86 | 0.8 | 0.87 | 1.00 |
| GPT-5.5 | B2 persona-free LLM | 19 | 10.8 | 0.89 | 0.985 | 0.72 | 9.9 | 0.40 | 0.71 |
| Gemini 3.1 Pro | Persona DLR | 19 | 29.7 | 0.70 | 0.874 | 0.51 | 29.7 | 0.22 | 0.71 |
| Gemini 3.1 Pro | Persona SSR | 19 | 11.1 | 0.89 | 0.984 | 0.53 | 6.0 | 0.04 | 0.71 |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO | 19 | 10.5 | 0.89 | 0.988 | – | -0.1 | 0.56 | – |
| Gemini 3.1 Pro | Persona SSR + CAL-STYLE | 13 | 5.4 | 0.95 | 0.996 | 0.86 | 0.5 | 0.73 | 1.00 |
| Gemini 3.1 Pro | B2 persona-free LLM | 19 | 12.9 | 0.87 | 0.979 | 0.79 | 12.9 | 0.39 | 0.86 |
| Claude Sonnet 5 | Persona DLR | 19 | 32.9 | 0.67 | 0.820 | 0.66 | 32.9 | 0.09 | 0.71 |
| Claude Sonnet 5 | Persona SSR | 19 | 9.8 | 0.90 | 0.987 | 0.74 | 3.6 | 0.12 | 0.86 |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO | 19 | 7.2 | 0.93 | 0.992 | – | -0.0 | 0.74 | – |
| Claude Sonnet 5 | Persona SSR + CAL-STYLE | 13 | 4.2 | 0.96 | 0.997 | 0.87 | 1.0 | 0.81 | 1.00 |
| Claude Sonnet 5 | B2 persona-free LLM | 19 | 9.3 | 0.91 | 0.990 | 0.80 | 5.8 | 0.39 | 0.86 |
| – | B0 uniform | 19 | 26.8 | 0.73 | 0.933 | – | -26.4 | 0.00 | – |
| – | B5 30-country total | 19 | 11.1 | 0.89 | 0.986 | – | 1.3 | 0.00 | – |
| – | LOCO mean | 19 | 12.0 | 0.88 | 0.984 | – | 0.0 | 0.06 | – |
| – | LOCO continent mean | 19 | 10.3 | 0.90 | 0.986 | 0.20 | -1.3 | 0.49 | 0.71 |
| – | B-XITEM cross-item regression | 13 | 4.3 | 0.96 | 0.997 | 0.83 | -0.1 | 0.93 | 1.00 |
| – | B1 carry-forward | 10 | 5.8 | 0.94 | 0.997 | 0.84 | -1.0 | 1.12 | 1.00 |

## Table: all metrics, Popularity (POPMEAN)

| Model | Method | n | MAE (pp) | 1−MAE | JS sim. | Spearman ρ | Bias (pp) | Spread ratio | Top/bottom-7 accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | 14 | 8.2 | 0.92 | 0.993 | 0.77 | -1.6 | 1.32 | 0.86 |
| GPT-5.5 | Persona SSR | 14 | 10.3 | 0.90 | 0.988 | 0.70 | 9.4 | 0.41 | 0.71 |
| GPT-5.5 | Persona SSR + CAL-LOCO | 14 | 7.1 | 0.93 | 0.995 | – | 0.2 | 0.73 | – |
| GPT-5.5 | Persona SSR + CAL-STYLE | 11 | 4.8 | 0.95 | 0.997 | 0.75 | -0.8 | 1.40 | 1.00 |
| GPT-5.5 | B2 persona-free LLM | 14 | 11.7 | 0.88 | 0.988 | 0.83 | 11.7 | 0.88 | 1.00 |
| Gemini 3.1 Pro | Persona DLR | 14 | 11.6 | 0.88 | 0.985 | 0.69 | 0.8 | 1.72 | 0.86 |
| Gemini 3.1 Pro | Persona SSR | 14 | 7.9 | 0.92 | 0.993 | 0.74 | 6.4 | 0.59 | 0.86 |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO | 14 | 6.3 | 0.94 | 0.996 | – | 0.0 | 0.81 | – |
| Gemini 3.1 Pro | Persona SSR + CAL-STYLE | 11 | 7.4 | 0.93 | 0.995 | 0.89 | -0.1 | 1.62 | 1.00 |
| Gemini 3.1 Pro | B2 persona-free LLM | 14 | 6.9 | 0.93 | 0.995 | 0.82 | 5.5 | 1.37 | 1.00 |
| Claude Sonnet 5 | Persona DLR | 14 | 11.3 | 0.89 | 0.986 | 0.56 | -6.3 | 1.34 | 0.86 |
| Claude Sonnet 5 | Persona SSR | 14 | 8.3 | 0.92 | 0.993 | 0.67 | 4.4 | 0.38 | 0.86 |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO | 14 | 6.9 | 0.93 | 0.994 | – | 0.2 | 0.71 | – |
| Claude Sonnet 5 | Persona SSR + CAL-STYLE | 11 | 3.9 | 0.96 | 0.998 | 0.83 | -0.7 | 1.29 | 1.00 |
| Claude Sonnet 5 | B2 persona-free LLM | 14 | 8.9 | 0.91 | 0.992 | 0.84 | 7.7 | 0.71 | 1.00 |
| – | B0 uniform | 14 | 10.9 | 0.89 | 0.990 | – | -2.4 | 0.00 | – |
| – | B5 30-country total | 14 | 10.9 | 0.89 | 0.990 | – | 0.5 | 0.00 | – |
| – | LOCO mean | 14 | 11.7 | 0.88 | 0.989 | – | -0.0 | 0.08 | – |
| – | LOCO continent mean | 14 | 4.3 | 0.96 | 0.996 | 0.53 | -0.0 | 0.87 | 0.86 |
| – | B-XITEM cross-item regression | 11 | 3.7 | 0.96 | 0.998 | 0.86 | -0.2 | 0.98 | 1.00 |

## Table: paired contrasts

| Model | Item | A | B | n | MAE(A) − MAE(B), pp (95% CI) | p | p (Holm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Favorability | Persona SSR | Persona DLR | 14 | -19.1 (-21.0 to -16.8) | 0.000 | 0.000 |
| GPT-5.5 | Favorability | Persona SSR | B5 30-country total | 14 | -0.4 (-5.3 to +4.3) | 0.892 | 1.000 |
| GPT-5.5 | Favorability | Persona SSR | B2 persona-free LLM | 14 | -2.1 (-4.2 to +0.4) | 0.100 | 1.000 |
| GPT-5.5 | Favorability | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 13 | +0.6 (-0.5 to +1.7) | 0.273 | 1.000 |
| GPT-5.5 | Favorability | Persona SSR + CAL-LOCO | LOCO continent mean | 14 | -1.1 (-4.6 to +2.6) | 0.567 | 1.000 |
| GPT-5.5 | Recommendation | Persona SSR | Persona DLR | 19 | -23.2 (-28.5 to -17.6) | 0.000 | 0.000 |
| GPT-5.5 | Recommendation | Persona SSR | B5 30-country total | 19 | -1.1 (-2.0 to -0.2) | 0.017 | 0.353 |
| GPT-5.5 | Recommendation | Persona SSR | B2 persona-free LLM | 19 | -0.8 (-4.7 to +3.1) | 0.698 | 1.000 |
| GPT-5.5 | Recommendation | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 13 | -1.0 (-2.0 to +0.0) | 0.059 | 1.000 |
| GPT-5.5 | Recommendation | Persona SSR + CAL-LOCO | LOCO continent mean | 19 | -2.2 (-5.2 to +0.9) | 0.162 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR | Persona DLR | 14 | +2.1 (-2.9 to +6.7) | 0.398 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR | B5 30-country total | 14 | -0.6 (-4.7 to +3.2) | 0.758 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR | B2 persona-free LLM | 14 | -1.5 (-4.6 to +1.8) | 0.363 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 11 | +1.2 (-1.5 to +3.5) | 0.362 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR + CAL-LOCO | LOCO continent mean | 14 | +2.8 (+0.6 to +5.2) | 0.014 | 0.317 |
| Gemini 3.1 Pro | Favorability | Persona SSR | Persona DLR | 14 | -12.7 (-13.5 to -11.7) | 0.000 | 0.000 |
| Gemini 3.1 Pro | Favorability | Persona SSR | B5 30-country total | 14 | +2.7 (-3.0 to +7.9) | 0.353 | 1.000 |
| Gemini 3.1 Pro | Favorability | Persona SSR | B2 persona-free LLM | 14 | +0.9 (-1.2 to +3.0) | 0.416 | 1.000 |
| Gemini 3.1 Pro | Favorability | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 13 | +0.9 (-0.3 to +2.1) | 0.154 | 1.000 |
| Gemini 3.1 Pro | Favorability | Persona SSR + CAL-LOCO | LOCO continent mean | 14 | -2.2 (-5.6 to +1.6) | 0.257 | 1.000 |
| Gemini 3.1 Pro | Recommendation | Persona SSR | Persona DLR | 19 | -18.7 (-21.7 to -15.2) | 0.000 | 0.000 |
| Gemini 3.1 Pro | Recommendation | Persona SSR | B5 30-country total | 19 | -0.1 (-2.0 to +1.9) | 0.938 | 1.000 |
| Gemini 3.1 Pro | Recommendation | Persona SSR | B2 persona-free LLM | 19 | -1.9 (-4.2 to +0.7) | 0.141 | 1.000 |
| Gemini 3.1 Pro | Recommendation | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 13 | +1.1 (-0.4 to +2.6) | 0.149 | 1.000 |
| Gemini 3.1 Pro | Recommendation | Persona SSR + CAL-LOCO | LOCO continent mean | 19 | +0.2 (-3.2 to +3.7) | 0.903 | 1.000 |
| Gemini 3.1 Pro | Popularity | Persona SSR | Persona DLR | 14 | -3.7 (-8.2 to +1.2) | 0.151 | 1.000 |
| Gemini 3.1 Pro | Popularity | Persona SSR | B5 30-country total | 14 | -3.0 (-5.9 to +0.1) | 0.058 | 0.922 |
| Gemini 3.1 Pro | Popularity | Persona SSR | B2 persona-free LLM | 14 | +1.0 (-3.0 to +4.9) | 0.628 | 1.000 |
| Gemini 3.1 Pro | Popularity | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 11 | +3.7 (+1.0 to +6.1) | 0.008 | 0.160 |
| Gemini 3.1 Pro | Popularity | Persona SSR + CAL-LOCO | LOCO continent mean | 14 | +2.0 (+0.0 to +3.8) | 0.046 | 0.775 |
| Claude Sonnet 5 | Favorability | Persona SSR | Persona DLR | 14 | -21.2 (-24.1 to -17.7) | 0.000 | 0.000 |
| Claude Sonnet 5 | Favorability | Persona SSR | B5 30-country total | 14 | -2.9 (-6.3 to +0.5) | 0.098 | 1.000 |
| Claude Sonnet 5 | Favorability | Persona SSR | B2 persona-free LLM | 14 | -0.4 (-1.9 to +1.0) | 0.558 | 1.000 |
| Claude Sonnet 5 | Favorability | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 13 | +0.0 (-0.7 to +0.8) | 0.970 | 1.000 |
| Claude Sonnet 5 | Favorability | Persona SSR + CAL-LOCO | LOCO continent mean | 14 | -4.2 (-7.3 to -0.8) | 0.012 | 0.236 |
| Claude Sonnet 5 | Recommendation | Persona SSR | Persona DLR | 19 | -23.0 (-27.1 to -18.8) | 0.000 | 0.000 |
| Claude Sonnet 5 | Recommendation | Persona SSR | B5 30-country total | 19 | -1.3 (-2.4 to -0.3) | 0.017 | 0.310 |
| Claude Sonnet 5 | Recommendation | Persona SSR | B2 persona-free LLM | 19 | +0.5 (-1.3 to +2.4) | 0.605 | 1.000 |
| Claude Sonnet 5 | Recommendation | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 13 | -0.1 (-1.4 to +1.2) | 0.876 | 1.000 |
| Claude Sonnet 5 | Recommendation | Persona SSR + CAL-LOCO | LOCO continent mean | 19 | -3.1 (-6.1 to -0.1) | 0.044 | 0.698 |
| Claude Sonnet 5 | Popularity | Persona SSR | Persona DLR | 14 | -2.9 (-7.7 to +1.4) | 0.212 | 1.000 |
| Claude Sonnet 5 | Popularity | Persona SSR | B5 30-country total | 14 | -2.5 (-4.9 to -0.0) | 0.047 | 0.708 |
| Claude Sonnet 5 | Popularity | Persona SSR | B2 persona-free LLM | 14 | -0.5 (-3.6 to +2.3) | 0.714 | 1.000 |
| Claude Sonnet 5 | Popularity | Persona SSR + CAL-STYLE | B-XITEM cross-item regression | 11 | +0.2 (-1.8 to +2.2) | 0.844 | 1.000 |
| Claude Sonnet 5 | Popularity | Persona SSR + CAL-LOCO | LOCO continent mean | 14 | +2.6 (+0.6 to +4.8) | 0.006 | 0.112 |

## Table: network contrasts

| Model | Item | A | B | n | MAE(A) − MAE(B), pp (95% CI) | p | p (Holm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Favorability | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 14 | -0.2 (-0.5 to +0.1) | 0.128 | 1.000 |
| GPT-5.5 | Favorability | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 14 | -0.1 (-0.4 to +0.1) | 0.300 | 1.000 |
| GPT-5.5 | Favorability | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 14 | +0.0 (-0.3 to +0.3) | 0.854 | 1.000 |
| GPT-5.5 | Recommendation | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 19 | -0.3 (-1.0 to +0.5) | 0.476 | 1.000 |
| GPT-5.5 | Recommendation | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 19 | -0.1 (-0.6 to +0.4) | 0.698 | 1.000 |
| GPT-5.5 | Recommendation | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 19 | -0.3 (-0.8 to +0.1) | 0.113 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 14 | +0.3 (-0.1 to +0.7) | 0.129 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 14 | +0.1 (-0.2 to +0.4) | 0.458 | 1.000 |
| GPT-5.5 | Popularity | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 14 | +0.5 (-0.2 to +1.0) | 0.136 | 1.000 |
| Gemini 3.1 Pro | Favorability | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 14 | +2.0 (+1.4 to +2.5) | 0.000 | 0.000 |
| Gemini 3.1 Pro | Favorability | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 14 | +0.1 (-0.3 to +0.4) | 0.664 | 1.000 |
| Gemini 3.1 Pro | Favorability | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 14 | +0.4 (+0.1 to +0.8) | 0.014 | 0.274 |
| Gemini 3.1 Pro | Recommendation | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 19 | +0.6 (-0.5 to +1.6) | 0.276 | 1.000 |
| Gemini 3.1 Pro | Recommendation | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 19 | +0.1 (-0.3 to +0.5) | 0.545 | 1.000 |
| Gemini 3.1 Pro | Recommendation | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 19 | -0.0 (-0.5 to +0.4) | 0.863 | 1.000 |
| Gemini 3.1 Pro | Popularity | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 14 | +1.4 (+0.3 to +2.5) | 0.013 | 0.256 |
| Gemini 3.1 Pro | Popularity | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 14 | +0.1 (-0.3 to +0.4) | 0.651 | 1.000 |
| Gemini 3.1 Pro | Popularity | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 14 | +0.8 (+0.1 to +1.5) | 0.036 | 0.641 |
| Claude Sonnet 5 | Favorability | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 14 | -0.1 (-0.3 to +0.1) | 0.291 | 1.000 |
| Claude Sonnet 5 | Favorability | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 14 | +0.1 (-0.2 to +0.4) | 0.648 | 1.000 |
| Claude Sonnet 5 | Favorability | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 14 | -0.5 (-1.0 to -0.1) | 0.017 | 0.310 |
| Claude Sonnet 5 | Recommendation | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 19 | +0.2 (+0.1 to +0.4) | 0.000 | 0.009 |
| Claude Sonnet 5 | Recommendation | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 19 | +0.3 (+0.1 to +0.5) | 0.002 | 0.042 |
| Claude Sonnet 5 | Recommendation | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 19 | +0.4 (-0.2 to +0.9) | 0.190 | 1.000 |
| Claude Sonnet 5 | Popularity | Persona SSR + N3 homophily network | Persona SSR (network subsample, round 1) | 14 | -0.1 (-0.2 to +0.1) | 0.489 | 1.000 |
| Claude Sonnet 5 | Popularity | Persona SSR + N3 homophily network | Persona SSR + N2 random network | 14 | -0.1 (-0.3 to +0.1) | 0.373 | 1.000 |
| Claude Sonnet 5 | Popularity | Persona SSR + N3 homophily network | Persona SSR + N1 self-reflection | 14 | -0.0 (-0.3 to +0.2) | 0.686 | 1.000 |

| Model | Arm | Persona–item pairs | Answers moved > 0.25 pt | Mean shift (pt) | Within-country SD, round 1 → 2 |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | N1self | 13500 | 18.9% | -0.019 | 0.227 → 0.235 |
| GPT-5.5 | N2random | 13500 | 20.6% | -0.002 | 0.227 → 0.197 |
| GPT-5.5 | N3homophily | 13500 | 19.3% | +0.002 | 0.227 → 0.211 |
| Gemini 3.1 Pro | N1self | 13500 | 20.6% | +0.022 | 0.314 → 0.325 |
| Gemini 3.1 Pro | N2random | 13500 | 22.7% | +0.057 | 0.314 → 0.279 |
| Gemini 3.1 Pro | N3homophily | 13500 | 22.8% | +0.055 | 0.314 → 0.286 |
| Claude Sonnet 5 | N1self | 13500 | 14.9% | +0.005 | 0.285 → 0.292 |
| Claude Sonnet 5 | N2random | 13499 | 9.4% | +0.002 | 0.285 → 0.272 |
| Claude Sonnet 5 | N3homophily | 13500 | 9.6% | -0.002 | 0.285 → 0.275 |

## Table: structure

| Model | Method | 13-domain MAE (pp) | 13-domain ρ | XQ5 3-band JS sim. | XQ6 3-band JS sim. | XQ5 bands, synthetic (1–2 / 3 / 4–5) |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | 27.2 | 0.91 | 0.839 | 0.827 | 0.0 / 0.3 / 99.7 |
| GPT-5.5 | Persona SSR | 13.6 | 0.68 | 0.970 | 0.988 | 9.9 / 10.9 / 79.2 |
| GPT-5.5 | B2 persona-free LLM | 11.9 | 0.91 | – | – | – |
| Gemini 3.1 Pro | Persona DLR | 22.9 | 0.88 | 0.885 | 0.876 | 0.0 / 2.9 / 97.1 |
| Gemini 3.1 Pro | Persona SSR | 14.0 | 0.76 | 0.951 | 0.941 | 9.4 / 7.1 / 83.5 |
| Gemini 3.1 Pro | B2 persona-free LLM | 8.4 | 0.94 | – | – | – |
| Claude Sonnet 5 | Persona DLR | 27.6 | 0.92 | 0.848 | 0.835 | 0.0 / 0.6 / 99.4 |
| Claude Sonnet 5 | Persona SSR | 13.8 | 0.76 | 0.976 | 0.969 | 11.1 / 13.0 / 75.9 |
| Claude Sonnet 5 | B2 persona-free LLM | 7.7 | 0.92 | – | – | – |
| – | Human (published) | – | – | – | – | 5.0 / 25.3 / 69.7 |

## Table: twin-level variance explained (adjusted R²), country label vs persona attributes

| Model | Mode | Items | Country only | Persona only | Both | Added by persona | Added by country |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | DLR | Favorability | 0.05 | 0.82 | 0.82 | +0.77 | +0.01 |
| GPT-5.5 | DLR | Recommendation | 0.06 | 0.83 | 0.84 | +0.78 | +0.01 |
| GPT-5.5 | DLR | 13 popularity items (mean) | 0.43 | 0.27 | 0.60 | +0.17 | +0.34 |
| GPT-5.5 | SSR | Favorability | 0.05 | 0.65 | 0.66 | +0.61 | +0.01 |
| GPT-5.5 | SSR | Recommendation | 0.05 | 0.21 | 0.25 | +0.20 | +0.03 |
| GPT-5.5 | SSR | 13 popularity items (mean) | 0.25 | 0.25 | 0.43 | +0.18 | +0.19 |
| Gemini 3.1 Pro | DLR | Favorability | 0.05 | 0.73 | 0.74 | +0.69 | +0.01 |
| Gemini 3.1 Pro | DLR | Recommendation | 0.05 | 0.71 | 0.72 | +0.67 | +0.01 |
| Gemini 3.1 Pro | DLR | 13 popularity items (mean) | 0.56 | 0.22 | 0.67 | +0.12 | +0.45 |
| Gemini 3.1 Pro | SSR | Favorability | 0.04 | 0.42 | 0.43 | +0.39 | +0.01 |
| Gemini 3.1 Pro | SSR | Recommendation | 0.01 | 0.06 | 0.08 | +0.06 | +0.02 |
| Gemini 3.1 Pro | SSR | 13 popularity items (mean) | 0.21 | 0.26 | 0.41 | +0.20 | +0.15 |
| Claude Sonnet 5 | DLR | Favorability | 0.07 | 0.63 | 0.65 | +0.58 | +0.02 |
| Claude Sonnet 5 | DLR | Recommendation | 0.07 | 0.63 | 0.65 | +0.58 | +0.02 |
| Claude Sonnet 5 | DLR | 13 popularity items (mean) | 0.48 | 0.26 | 0.64 | +0.16 | +0.37 |
| Claude Sonnet 5 | SSR | Favorability | 0.09 | 0.59 | 0.63 | +0.54 | +0.04 |
| Claude Sonnet 5 | SSR | Recommendation | 0.03 | 0.16 | 0.19 | +0.15 | +0.03 |
| Claude Sonnet 5 | SSR | 13 popularity items (mean) | 0.16 | 0.17 | 0.29 | +0.13 | +0.12 |

## Table: correlation analyses (Spearman ρ)

| Analysis | Model | Method | Items | n | ρ | p |
| --- | --- | --- | --- | --- | --- | --- |
| Item coherence: Favorability ~ Recommendation | – | human (listed countries) | – | 12 | 0.86 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Claude Sonnet 5 | Persona DLR (30 countries) | – | 30 | 1.00 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Claude Sonnet 5 | Persona DLR (same countries as human) | – | 12 | 1.00 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Claude Sonnet 5 | Persona SSR (30 countries) | – | 30 | 0.87 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Claude Sonnet 5 | Persona SSR (same countries as human) | – | 12 | 0.88 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Gemini 3.1 Pro | Persona DLR (30 countries) | – | 30 | 0.99 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Gemini 3.1 Pro | Persona DLR (same countries as human) | – | 12 | 1.00 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Gemini 3.1 Pro | Persona SSR (30 countries) | – | 30 | 0.07 | 0.702 |
| Item coherence: Favorability ~ Recommendation | Gemini 3.1 Pro | Persona SSR (same countries as human) | – | 12 | 0.52 | 0.080 |
| Item coherence: Favorability ~ Recommendation | GPT-5.5 | Persona DLR (30 countries) | – | 30 | 0.90 | 0.000 |
| Item coherence: Favorability ~ Recommendation | GPT-5.5 | Persona DLR (same countries as human) | – | 12 | 0.82 | 0.001 |
| Item coherence: Favorability ~ Recommendation | GPT-5.5 | Persona SSR (30 countries) | – | 30 | 0.83 | 0.000 |
| Item coherence: Favorability ~ Recommendation | GPT-5.5 | Persona SSR (same countries as human) | – | 12 | 0.94 | 0.000 |
| Item coherence: Favorability ~ Popularity | – | human (listed countries) | – | 10 | 0.83 | 0.003 |
| Item coherence: Favorability ~ Popularity | Claude Sonnet 5 | Persona DLR (30 countries) | – | 30 | 0.18 | 0.352 |
| Item coherence: Favorability ~ Popularity | Claude Sonnet 5 | Persona DLR (same countries as human) | – | 10 | 0.46 | 0.182 |
| Item coherence: Favorability ~ Popularity | Claude Sonnet 5 | Persona SSR (30 countries) | – | 30 | 0.60 | 0.001 |
| Item coherence: Favorability ~ Popularity | Claude Sonnet 5 | Persona SSR (same countries as human) | – | 10 | 0.76 | 0.011 |
| Item coherence: Favorability ~ Popularity | Gemini 3.1 Pro | Persona DLR (30 countries) | – | 30 | 0.15 | 0.429 |
| Item coherence: Favorability ~ Popularity | Gemini 3.1 Pro | Persona DLR (same countries as human) | – | 10 | 0.49 | 0.154 |
| Item coherence: Favorability ~ Popularity | Gemini 3.1 Pro | Persona SSR (30 countries) | – | 30 | 0.71 | 0.000 |
| Item coherence: Favorability ~ Popularity | Gemini 3.1 Pro | Persona SSR (same countries as human) | – | 10 | 0.78 | 0.008 |
| Item coherence: Favorability ~ Popularity | GPT-5.5 | Persona DLR (30 countries) | – | 30 | 0.26 | 0.158 |
| Item coherence: Favorability ~ Popularity | GPT-5.5 | Persona DLR (same countries as human) | – | 10 | 0.61 | 0.062 |
| Item coherence: Favorability ~ Popularity | GPT-5.5 | Persona SSR (30 countries) | – | 30 | 0.52 | 0.003 |
| Item coherence: Favorability ~ Popularity | GPT-5.5 | Persona SSR (same countries as human) | – | 10 | 0.79 | 0.006 |
| Item coherence: Recommendation ~ Popularity | – | human (listed countries) | – | 10 | 0.82 | 0.004 |
| Item coherence: Recommendation ~ Popularity | Claude Sonnet 5 | Persona DLR (30 countries) | – | 30 | 0.18 | 0.352 |
| Item coherence: Recommendation ~ Popularity | Claude Sonnet 5 | Persona DLR (same countries as human) | – | 10 | 0.46 | 0.182 |
| Item coherence: Recommendation ~ Popularity | Claude Sonnet 5 | Persona SSR (30 countries) | – | 30 | 0.72 | 0.000 |
| Item coherence: Recommendation ~ Popularity | Claude Sonnet 5 | Persona SSR (same countries as human) | – | 10 | 0.79 | 0.006 |
| Item coherence: Recommendation ~ Popularity | Gemini 3.1 Pro | Persona DLR (30 countries) | – | 30 | 0.16 | 0.410 |
| Item coherence: Recommendation ~ Popularity | Gemini 3.1 Pro | Persona DLR (same countries as human) | – | 10 | 0.53 | 0.112 |
| Item coherence: Recommendation ~ Popularity | Gemini 3.1 Pro | Persona SSR (30 countries) | – | 30 | -0.04 | 0.838 |
| Item coherence: Recommendation ~ Popularity | Gemini 3.1 Pro | Persona SSR (same countries as human) | – | 10 | 0.16 | 0.651 |
| Item coherence: Recommendation ~ Popularity | GPT-5.5 | Persona DLR (30 countries) | – | 30 | 0.36 | 0.050 |
| Item coherence: Recommendation ~ Popularity | GPT-5.5 | Persona DLR (same countries as human) | – | 10 | 0.80 | 0.006 |
| Item coherence: Recommendation ~ Popularity | GPT-5.5 | Persona SSR (30 countries) | – | 30 | 0.69 | 0.000 |
| Item coherence: Recommendation ~ Popularity | GPT-5.5 | Persona SSR (same countries as human) | – | 10 | 0.85 | 0.002 |
| Item coherence: Favorability ~ Recommendation | Claude Sonnet 5 | B2 persona-free LLM (same countries as human) | – | 12 | 0.97 | 0.000 |
| Item coherence: Favorability ~ Popularity | Claude Sonnet 5 | B2 persona-free LLM (same countries as human) | – | 10 | 0.93 | 0.000 |
| Item coherence: Recommendation ~ Popularity | Claude Sonnet 5 | B2 persona-free LLM (same countries as human) | – | 10 | 0.93 | 0.000 |
| Item coherence: Favorability ~ Recommendation | Gemini 3.1 Pro | B2 persona-free LLM (same countries as human) | – | 12 | 0.99 | 0.000 |
| Item coherence: Favorability ~ Popularity | Gemini 3.1 Pro | B2 persona-free LLM (same countries as human) | – | 10 | 0.88 | 0.001 |
| Item coherence: Recommendation ~ Popularity | Gemini 3.1 Pro | B2 persona-free LLM (same countries as human) | – | 10 | 0.83 | 0.003 |
| Item coherence: Favorability ~ Recommendation | GPT-5.5 | B2 persona-free LLM (same countries as human) | – | 12 | 0.99 | 0.000 |
| Item coherence: Favorability ~ Popularity | GPT-5.5 | B2 persona-free LLM (same countries as human) | – | 10 | 0.90 | 0.000 |
| Item coherence: Recommendation ~ Popularity | GPT-5.5 | B2 persona-free LLM (same countries as human) | – | 10 | 0.90 | 0.000 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ Gemini 3.1 Pro | Persona SSR | Favorability | 30 | 0.85 | 0.000 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ GPT-5.5 | Persona SSR | Favorability | 30 | 0.84 | 0.000 |
| Inter-model agreement, 30 countries | Gemini 3.1 Pro ~ GPT-5.5 | Persona SSR | Favorability | 30 | 0.79 | 0.000 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ Gemini 3.1 Pro | Persona DLR | Favorability | 30 | 0.60 | 0.000 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ GPT-5.5 | Persona DLR | Favorability | 30 | 0.26 | 0.164 |
| Inter-model agreement, 30 countries | Gemini 3.1 Pro ~ GPT-5.5 | Persona DLR | Favorability | 30 | 0.40 | 0.028 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ Gemini 3.1 Pro | Persona SSR | Recommendation | 30 | 0.16 | 0.404 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ GPT-5.5 | Persona SSR | Recommendation | 30 | 0.87 | 0.000 |
| Inter-model agreement, 30 countries | Gemini 3.1 Pro ~ GPT-5.5 | Persona SSR | Recommendation | 30 | 0.06 | 0.761 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ Gemini 3.1 Pro | Persona DLR | Recommendation | 30 | 0.59 | 0.001 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ GPT-5.5 | Persona DLR | Recommendation | 30 | 0.38 | 0.038 |
| Inter-model agreement, 30 countries | Gemini 3.1 Pro ~ GPT-5.5 | Persona DLR | Recommendation | 30 | 0.49 | 0.006 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ Gemini 3.1 Pro | Persona SSR | Popularity | 30 | 0.92 | 0.000 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ GPT-5.5 | Persona SSR | Popularity | 30 | 0.96 | 0.000 |
| Inter-model agreement, 30 countries | Gemini 3.1 Pro ~ GPT-5.5 | Persona SSR | Popularity | 30 | 0.95 | 0.000 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ Gemini 3.1 Pro | Persona DLR | Popularity | 30 | 0.92 | 0.000 |
| Inter-model agreement, 30 countries | Claude Sonnet 5 ~ GPT-5.5 | Persona DLR | Popularity | 30 | 0.92 | 0.000 |
| Inter-model agreement, 30 countries | Gemini 3.1 Pro ~ GPT-5.5 | Persona DLR | Popularity | 30 | 0.96 | 0.000 |
| error ~ human level | Claude Sonnet 5 | Persona DLR | Popularity | 14 | -0.19 | 0.513 |
| error ~ human level | Claude Sonnet 5 | Persona DLR | Favorability | 14 | -0.99 | 0.000 |
| error ~ human level | Claude Sonnet 5 | Persona DLR | Recommendation | 19 | -1.00 | 0.000 |
| error ~ human level | Claude Sonnet 5 | Persona SSR | Popularity | 14 | -0.89 | 0.000 |
| error ~ human level | Claude Sonnet 5 | Persona SSR | Favorability | 14 | -0.99 | 0.000 |
| error ~ human level | Claude Sonnet 5 | Persona SSR | Recommendation | 19 | -0.99 | 0.000 |
| error ~ human level | Gemini 3.1 Pro | Persona DLR | Popularity | 14 | 0.15 | 0.605 |
| error ~ human level | Gemini 3.1 Pro | Persona DLR | Favorability | 14 | -0.98 | 0.000 |
| error ~ human level | Gemini 3.1 Pro | Persona DLR | Recommendation | 19 | -0.98 | 0.000 |
| error ~ human level | Gemini 3.1 Pro | Persona SSR | Popularity | 14 | -0.86 | 0.000 |
| error ~ human level | Gemini 3.1 Pro | Persona SSR | Favorability | 14 | -0.99 | 0.000 |
| error ~ human level | Gemini 3.1 Pro | Persona SSR | Recommendation | 19 | -1.00 | 0.000 |
| error ~ human level | GPT-5.5 | Persona DLR | Popularity | 14 | -0.08 | 0.794 |
| error ~ human level | GPT-5.5 | Persona DLR | Favorability | 14 | -1.00 | 0.000 |
| error ~ human level | GPT-5.5 | Persona DLR | Recommendation | 19 | -1.00 | 0.000 |
| error ~ human level | GPT-5.5 | Persona SSR | Popularity | 14 | -0.86 | 0.000 |
| error ~ human level | GPT-5.5 | Persona SSR | Favorability | 14 | -0.98 | 0.000 |
| error ~ human level | GPT-5.5 | Persona SSR | Recommendation | 19 | -0.99 | 0.000 |
| country estimates, 30 countries | Claude Sonnet 5 | SSR vs DLR | Popularity | 30 | 0.92 | 0.000 |
| country estimates, 30 countries | Claude Sonnet 5 | SSR vs DLR | Favorability | 30 | 0.59 | 0.001 |
| country estimates, 30 countries | Claude Sonnet 5 | SSR vs DLR | Recommendation | 30 | 0.65 | 0.000 |
| country estimates, 30 countries | Gemini 3.1 Pro | SSR vs DLR | Popularity | 30 | 0.97 | 0.000 |
| country estimates, 30 countries | Gemini 3.1 Pro | SSR vs DLR | Favorability | 30 | 0.39 | 0.035 |
| country estimates, 30 countries | Gemini 3.1 Pro | SSR vs DLR | Recommendation | 30 | 0.21 | 0.256 |
| country estimates, 30 countries | GPT-5.5 | SSR vs DLR | Popularity | 30 | 0.96 | 0.000 |
| country estimates, 30 countries | GPT-5.5 | SSR vs DLR | Favorability | 30 | 0.30 | 0.113 |
| country estimates, 30 countries | GPT-5.5 | SSR vs DLR | Recommendation | 30 | 0.32 | 0.085 |
| Same persona, DLR ~ SSR (median of 15 items) | Claude Sonnet 5 | – | 15 items | 3000 | 0.30 | – |
| Same persona, DLR ~ SSR | Claude Sonnet 5 | – | Favorability | 3000 | 0.60 | 0.000 |
| Same persona, DLR ~ SSR | Claude Sonnet 5 | – | Recommendation | 3000 | 0.15 | 0.000 |
| Same persona, DLR ~ SSR (median of 15 items) | Gemini 3.1 Pro | – | 15 items | 3000 | 0.44 | – |
| Same persona, DLR ~ SSR | Gemini 3.1 Pro | – | Favorability | 3000 | 0.51 | 0.000 |
| Same persona, DLR ~ SSR | Gemini 3.1 Pro | – | Recommendation | 3000 | 0.03 | 0.056 |
| Same persona, DLR ~ SSR (median of 15 items) | GPT-5.5 | – | 15 items | 3000 | 0.46 | – |
| Same persona, DLR ~ SSR | GPT-5.5 | – | Favorability | 3000 | 0.62 | 0.000 |
| Same persona, DLR ~ SSR | GPT-5.5 | – | Recommendation | 3000 | 0.30 | 0.000 |

## Table: mean signed error by continent (pp), listed countries

| Model | Method | Item | Africa | Americas | Asia-Pacific | Europe | Middle East |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | Favorability | – | +21.1 (n=1) | +26.5 (n=7) | +46.0 (n=5) | +22.0 (n=1) |
| GPT-5.5 | Persona DLR | Recommendation | +21.8 (n=1) | +22.3 (n=2) | +31.7 (n=8) | +41.3 (n=7) | +21.5 (n=1) |
| GPT-5.5 | Persona DLR | Popularity | – | -3.3 (n=2) | +4.8 (n=6) | -5.5 (n=4) | -11.5 (n=2) |
| GPT-5.5 | Persona SSR | Favorability | – | +0.0 (n=1) | +7.4 (n=7) | +23.9 (n=5) | +2.8 (n=1) |
| GPT-5.5 | Persona SSR | Recommendation | -11.9 (n=1) | -11.5 (n=2) | -0.2 (n=8) | +6.7 (n=7) | -9.0 (n=1) |
| GPT-5.5 | Persona SSR | Popularity | – | +15.1 (n=2) | +5.8 (n=6) | +16.8 (n=4) | -0.2 (n=2) |
| Gemini 3.1 Pro | Persona DLR | Favorability | – | +18.1 (n=1) | +23.5 (n=7) | +41.8 (n=5) | +19.0 (n=1) |
| Gemini 3.1 Pro | Persona DLR | Recommendation | +19.8 (n=1) | +20.3 (n=2) | +28.6 (n=8) | +36.7 (n=7) | +18.5 (n=1) |
| Gemini 3.1 Pro | Persona DLR | Popularity | – | -8.0 (n=2) | +12.2 (n=6) | -5.8 (n=4) | -10.9 (n=2) |
| Gemini 3.1 Pro | Persona SSR | Favorability | – | +4.3 (n=1) | +11.4 (n=7) | +27.9 (n=5) | +6.7 (n=1) |
| Gemini 3.1 Pro | Persona SSR | Recommendation | -6.0 (n=1) | -5.1 (n=2) | +4.5 (n=8) | +14.0 (n=7) | -5.1 (n=1) |
| Gemini 3.1 Pro | Persona SSR | Popularity | – | +9.2 (n=2) | +4.8 (n=6) | +11.4 (n=4) | -2.1 (n=2) |
| Claude Sonnet 5 | Persona DLR | Favorability | – | +21.1 (n=1) | +26.0 (n=7) | +45.4 (n=5) | +22.0 (n=1) |
| Claude Sonnet 5 | Persona DLR | Recommendation | +21.8 (n=1) | +22.3 (n=2) | +31.2 (n=8) | +41.0 (n=7) | +21.5 (n=1) |
| Claude Sonnet 5 | Persona DLR | Popularity | – | -8.7 (n=2) | -0.9 (n=6) | -8.0 (n=4) | -16.6 (n=2) |
| Claude Sonnet 5 | Persona SSR | Favorability | – | -2.2 (n=1) | +5.4 (n=7) | +18.4 (n=5) | -0.2 (n=1) |
| Claude Sonnet 5 | Persona SSR | Recommendation | -8.7 (n=1) | -7.3 (n=2) | +3.1 (n=8) | +10.5 (n=7) | -6.5 (n=1) |
| Claude Sonnet 5 | Persona SSR | Popularity | – | +10.1 (n=2) | +0.7 (n=6) | +11.9 (n=4) | -4.9 (n=2) |

## Table: Monte Carlo standard error of a country estimate (100 twins per country), pp

| Model | Mode | Item | Median SE | Range over countries |
| --- | --- | --- | --- | --- |
| GPT-5.5 | DLR | Favorability | 0.0 | 0.0–1.4 |
| GPT-5.5 | DLR | Recommendation | 0.0 | 0.0–1.4 |
| GPT-5.5 | DLR | Popularity | 1.1 | 0.6–1.3 |
| GPT-5.5 | SSR | Favorability | 0.6 | 0.5–0.7 |
| GPT-5.5 | SSR | Recommendation | 0.4 | 0.3–0.6 |
| GPT-5.5 | SSR | Popularity | 0.4 | 0.3–0.5 |
| Gemini 3.1 Pro | DLR | Favorability | 1.4 | 0.0–2.9 |
| Gemini 3.1 Pro | DLR | Recommendation | 1.4 | 0.0–3.4 |
| Gemini 3.1 Pro | DLR | Popularity | 0.9 | 0.5–1.2 |
| Gemini 3.1 Pro | SSR | Favorability | 0.7 | 0.6–1.0 |
| Gemini 3.1 Pro | SSR | Recommendation | 0.4 | 0.3–0.5 |
| Gemini 3.1 Pro | SSR | Popularity | 0.6 | 0.4–0.7 |
| Claude Sonnet 5 | DLR | Favorability | 0.0 | 0.0–2.0 |
| Claude Sonnet 5 | DLR | Recommendation | 0.0 | 0.0–2.0 |
| Claude Sonnet 5 | DLR | Popularity | 0.9 | 0.6–1.4 |
| Claude Sonnet 5 | SSR | Favorability | 0.9 | 0.6–1.2 |
| Claude Sonnet 5 | SSR | Recommendation | 0.5 | 0.3–0.8 |
| Claude Sonnet 5 | SSR | Popularity | 0.4 | 0.3–0.5 |

## Table: popularity average over 13 domains (main) vs 11 domains (sensitivity)

| Model | Method | Definition | n | MAE (pp) | Bias (pp) | ρ |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | 13 domains | 14 | 8.2 | -1.6 | 0.77 |
| GPT-5.5 | Persona DLR | 11 domains | 14 | 8.9 | +4.5 | 0.76 |
| GPT-5.5 | Persona SSR | 13 domains | 14 | 10.3 | +9.4 | 0.70 |
| GPT-5.5 | Persona SSR | 11 domains | 14 | 11.1 | +10.8 | 0.71 |
| Gemini 3.1 Pro | Persona DLR | 13 domains | 14 | 11.6 | +0.8 | 0.69 |
| Gemini 3.1 Pro | Persona DLR | 11 domains | 14 | 12.1 | +6.3 | 0.69 |
| Gemini 3.1 Pro | Persona SSR | 13 domains | 14 | 7.9 | +6.4 | 0.74 |
| Gemini 3.1 Pro | Persona SSR | 11 domains | 14 | 8.8 | +8.3 | 0.73 |
| Claude Sonnet 5 | Persona DLR | 13 domains | 14 | 11.3 | -6.3 | 0.56 |
| Claude Sonnet 5 | Persona DLR | 11 domains | 14 | 10.2 | -1.1 | 0.57 |
| Claude Sonnet 5 | Persona SSR | 13 domains | 14 | 8.3 | +4.4 | 0.67 |
| Claude Sonnet 5 | Persona SSR | 11 domains | 14 | 9.1 | +6.4 | 0.66 |

## Table: favorability on all 30 countries (full ranking printed in the report)

| Model | Method | MAE, 30 countries (95% CI) | Bias | ρ (30) | Spread | Top/bottom-7 recovered (of 14) | MAE, 14 listed | MAE, 16 middle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | 30.8 (27.3–34.7) | +30.8 | 0.47 | 0.05 | 3 | 32.7 | 29.2 |
| GPT-5.5 | Persona SSR | 10.8 (7.7–14.2) | +10.2 | 0.55 | 0.15 | 8 | 13.6 | 8.3 |
| GPT-5.5 | Persona SSR + CAL-LOCO (LOO, 30) | 6.7 (4.6–8.9) | -0.0 | – | 0.57 | 7 | 9.3 | 4.4 |
| GPT-5.5 | Persona SSR + CAL-LOCO fitted on the 14 listed | – | – | – | – | – | – | 7.7 (bias -7.0) |
| GPT-5.5 | B2 persona-free LLM | 13.0 (10.0–16.4) | +12.9 | 0.56 | 0.36 | 8 | 15.7 | 10.7 |
| Gemini 3.1 Pro | Persona DLR | 28.1 (24.8–31.6) | +28.1 | 0.32 | 0.22 | 4 | 29.3 | 27.0 |
| Gemini 3.1 Pro | Persona SSR | 14.7 (11.5–18.2) | +14.6 | 0.64 | 0.16 | 8 | 16.7 | 13.0 |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO (LOO, 30) | 6.6 (4.8–8.6) | -0.1 | – | 0.65 | 8 | 8.1 | 5.4 |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO fitted on the 14 listed | – | – | – | – | – | – | 6.9 (bias -2.8) |
| Gemini 3.1 Pro | B2 persona-free LLM | 13.0 (10.4–16.0) | +13.0 | 0.75 | 0.42 | 10 | 15.8 | 10.5 |
| Claude Sonnet 5 | Persona DLR | 30.5 (27.0–34.3) | +30.5 | 0.55 | 0.09 | 7 | 32.3 | 28.9 |
| Claude Sonnet 5 | Persona SSR | 7.8 (5.4–10.7) | +6.9 | 0.79 | 0.30 | 8 | 11.1 | 5.0 |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO (LOO, 30) | 5.6 (4.0–7.4) | +0.0 | – | 0.75 | 8 | 6.5 | 4.8 |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO fitted on the 14 listed | – | – | – | – | – | – | 7.6 (bias -5.4) |
| Claude Sonnet 5 | B2 persona-free LLM | 9.3 (6.8–11.9) | +8.1 | 0.60 | 0.37 | 8 | 11.6 | 7.4 |
| – | B0 uniform | 29.0 (25.1–32.5) | -29.0 | – | 0.00 | – | 27.0 | 30.6 |
| – | B5 30-country total | 8.6 (6.5–10.9) | +0.7 | – | 0.00 | – | 14.0 | 3.8 |
| – | B5 leave-one-out total | 8.9 (6.8–11.3) | +0.7 | – | 0.04 | – | 14.5 | 4.0 |
| – | LOCO mean | 9.0 (6.9–11.3) | +0.0 | – | 0.03 | – | 14.5 | 4.2 |
| – | LOCO continent mean | 7.4 (5.4–9.8) | +0.0 | 0.13 | 0.60 | 5 | 10.1 | 5.1 |
| – | B-PROFILE knowledge share (LOO) | 6.8 (5.1–8.8) | +0.0 | 0.58 | 0.63 | 7 | 9.0 | 4.9 |
| – | B1 carry-forward (n = 8) | 5.2 (3.9–6.5) | -3.0 | 1.00 | 1.37 | – | 3.9 | 6.6 |

CAL-LOCO fitted on the 14 listed countries and applied to the 16 middle ones: Claude Sonnet 5 DLR MAE 5.0 (bias -2.6); Claude Sonnet 5 SSR MAE 7.6 (bias -5.4); Gemini 3.1 Pro DLR MAE 8.0 (bias +1.2); Gemini 3.1 Pro SSR MAE 6.9 (bias -2.8); GPT-5.5 DLR MAE 6.6 (bias -3.0); GPT-5.5 SSR MAE 7.7 (bias -7.0)

## Table: paired contrasts on all 30 countries (favorability; exploratory)

| Model | A | B | MAE(A) | MAE(B) | Difference (pp) | p (sign-flip) | ρ(A) − ρ(B) (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | Persona SSR | B-PROFILE knowledge share (LOO) | 7.8 | 6.8 | +1.0 | 0.417 | +0.21 (+0.02 to +0.42) |
| Claude Sonnet 5 | Persona SSR | LOCO continent mean | 7.8 | 7.4 | +0.4 | 0.759 | +0.66 (+0.35 to +1.01) |
| Claude Sonnet 5 | Persona SSR | B5 30-country total | 7.8 | 8.6 | -0.7 | 0.472 | – |
| Claude Sonnet 5 | Persona SSR | B2 persona-free LLM | 7.8 | 9.3 | -1.5 | 0.019 | +0.19 (-0.09 to +0.49) |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO (LOO, 30) | B-PROFILE knowledge share (LOO) | 5.6 | 6.8 | -1.2 | 0.134 | – |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO (LOO, 30) | LOCO continent mean | 5.6 | 7.4 | -1.8 | 0.054 | – |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO (LOO, 30) | B5 30-country total | 5.6 | 8.6 | -3.0 | 0.014 | – |
| Claude Sonnet 5 | Persona SSR + CAL-LOCO (LOO, 30) | B2 persona-free LLM | 5.6 | 9.3 | -3.7 | 0.004 | – |
| Gemini 3.1 Pro | Persona SSR | B-PROFILE knowledge share (LOO) | 14.7 | 6.8 | +7.9 | 0.000 | +0.06 (-0.11 to +0.26) |
| Gemini 3.1 Pro | Persona SSR | LOCO continent mean | 14.7 | 7.4 | +7.3 | 0.000 | +0.52 (+0.18 to +0.90) |
| Gemini 3.1 Pro | Persona SSR | B5 30-country total | 14.7 | 8.6 | +6.1 | 0.001 | – |
| Gemini 3.1 Pro | Persona SSR | B2 persona-free LLM | 14.7 | 13.0 | +1.7 | 0.008 | -0.10 (-0.31 to +0.06) |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO (LOO, 30) | B-PROFILE knowledge share (LOO) | 6.6 | 6.8 | -0.2 | 0.834 | – |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO (LOO, 30) | LOCO continent mean | 6.6 | 7.4 | -0.8 | 0.326 | – |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO (LOO, 30) | B5 30-country total | 6.6 | 8.6 | -1.9 | 0.080 | – |
| Gemini 3.1 Pro | Persona SSR + CAL-LOCO (LOO, 30) | B2 persona-free LLM | 6.6 | 13.0 | -6.3 | 0.000 | – |
| GPT-5.5 | Persona SSR | B-PROFILE knowledge share (LOO) | 10.8 | 6.8 | +4.0 | 0.019 | -0.03 (-0.25 to +0.21) |
| GPT-5.5 | Persona SSR | LOCO continent mean | 10.8 | 7.4 | +3.3 | 0.052 | +0.43 (+0.03 to +0.84) |
| GPT-5.5 | Persona SSR | B5 30-country total | 10.8 | 8.6 | +2.2 | 0.117 | – |
| GPT-5.5 | Persona SSR | B2 persona-free LLM | 10.8 | 13.0 | -2.3 | 0.003 | -0.01 (-0.37 to +0.34) |
| GPT-5.5 | Persona SSR + CAL-LOCO (LOO, 30) | B-PROFILE knowledge share (LOO) | 6.7 | 6.8 | -0.1 | 0.835 | – |
| GPT-5.5 | Persona SSR + CAL-LOCO (LOO, 30) | LOCO continent mean | 6.7 | 7.4 | -0.8 | 0.394 | – |
| GPT-5.5 | Persona SSR + CAL-LOCO (LOO, 30) | B5 30-country total | 6.7 | 8.6 | -1.9 | 0.065 | – |
| GPT-5.5 | Persona SSR + CAL-LOCO (LOO, 30) | B2 persona-free LLM | 6.7 | 13.0 | -6.4 | 0.001 | – |

## Table: additional non-LLM comparators on the listed countries

| Method | Item | n | MAE (95% CI) | Bias | ρ | Spread | Top/bottom-7 accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B-PROFILE knowledge share (LOO) | Favorability | 14 | 8.1 (4.9–11.8) | -0.1 | 0.62 | 0.78 | 0.86 |
| B5 leave-one-out total | Favorability | 14 | 14.5 (12.1–17.0) | +2.7 | – | 0.04 | – |
| B-PROFILE knowledge share (LOO) | Recommendation | 19 | 9.9 (6.6–13.7) | -0.0 | 0.35 | 0.44 | 0.57 |
| B5 leave-one-out total | Recommendation | 19 | 11.6 (8.4–15.0) | +1.3 | – | 0.04 | – |
| B-PROFILE knowledge share (LOO) | Popularity | 14 | 4.5 (2.3–6.9) | -0.1 | 0.71 | 0.87 | 0.86 |
| B5 leave-one-out total | Popularity | 14 | 11.2 (9.9–13.0) | +0.5 | – | 0.03 | – |

## Table: unlisted countries (XQ6: 11, POPMEAN: 16) against the printed band and the backed-out mean

| Item | Model | Method | Outside band | Synthetic mean of unlisted | Implied human mean | Error (pp) |
| --- | --- | --- | --- | --- | --- | --- |
| XQ6 [59.5, 75.6] | Claude Sonnet 5 | B2 persona-free LLM | 55% | 75.4 | 69.4 | +6.0 |
| XQ6 [59.5, 75.6] | Claude Sonnet 5 | Persona DLR | 100% | 99.7 | 69.4 | +30.3 |
| XQ6 [59.5, 75.6] | Claude Sonnet 5 | Persona SSR | 0% | 70.5 | 69.4 | +1.1 |
| XQ6 [59.5, 75.6] | Gemini 3.1 Pro | B2 persona-free LLM | 91% | 81.2 | 69.4 | +11.8 |
| XQ6 [59.5, 75.6] | Gemini 3.1 Pro | Persona DLR | 100% | 98.2 | 69.4 | +28.8 |
| XQ6 [59.5, 75.6] | Gemini 3.1 Pro | Persona SSR | 0% | 72.3 | 69.4 | +2.8 |
| XQ6 [59.5, 75.6] | GPT-5.5 | B2 persona-free LLM | 91% | 78.2 | 69.4 | +8.8 |
| XQ6 [59.5, 75.6] | GPT-5.5 | Persona DLR | 100% | 100.0 | 69.4 | +30.6 |
| XQ6 [59.5, 75.6] | GPT-5.5 | Persona SSR | 0% | 66.8 | 69.4 | -2.6 |
| POPMEAN [34.5, 50.2] | Claude Sonnet 5 | B2 persona-free LLM | 50% | 50.5 | 42.8 | +7.8 |
| POPMEAN [34.5, 50.2] | Claude Sonnet 5 | Persona DLR | 88% | 34.0 | 42.8 | -8.8 |
| POPMEAN [34.5, 50.2] | Claude Sonnet 5 | Persona SSR | 19% | 46.0 | 42.8 | +3.2 |
| POPMEAN [34.5, 50.2] | Gemini 3.1 Pro | B2 persona-free LLM | 44% | 47.8 | 42.8 | +5.1 |
| POPMEAN [34.5, 50.2] | Gemini 3.1 Pro | Persona DLR | 81% | 40.9 | 42.8 | -1.9 |
| POPMEAN [34.5, 50.2] | Gemini 3.1 Pro | Persona SSR | 25% | 48.0 | 42.8 | +5.2 |
| POPMEAN [34.5, 50.2] | GPT-5.5 | B2 persona-free LLM | 50% | 52.5 | 42.8 | +9.8 |
| POPMEAN [34.5, 50.2] | GPT-5.5 | Persona DLR | 69% | 39.4 | 42.8 | -3.3 |
| POPMEAN [34.5, 50.2] | GPT-5.5 | Persona SSR | 44% | 51.5 | 42.8 | +8.7 |
| POPMEAN (11 domains) [34.5, 50.2] | Claude Sonnet 5 | B2 persona-free LLM | 69% | 52.7 | 44.8 | +7.9 |
| POPMEAN (11 domains) [34.5, 50.2] | Claude Sonnet 5 | Persona DLR | 81% | 39.0 | 44.8 | -5.8 |
| POPMEAN (11 domains) [34.5, 50.2] | Claude Sonnet 5 | Persona SSR | 25% | 47.9 | 44.8 | +3.1 |
| POPMEAN (11 domains) [34.5, 50.2] | Gemini 3.1 Pro | B2 persona-free LLM | 50% | 50.8 | 44.8 | +6.0 |
| POPMEAN (11 domains) [34.5, 50.2] | Gemini 3.1 Pro | Persona DLR | 62% | 46.1 | 44.8 | +1.2 |
| POPMEAN (11 domains) [34.5, 50.2] | Gemini 3.1 Pro | Persona SSR | 25% | 49.7 | 44.8 | +4.8 |
| POPMEAN (11 domains) [34.5, 50.2] | GPT-5.5 | B2 persona-free LLM | 94% | 56.2 | 44.8 | +11.3 |
| POPMEAN (11 domains) [34.5, 50.2] | GPT-5.5 | Persona DLR | 31% | 45.9 | 44.8 | +1.1 |
| POPMEAN (11 domains) [34.5, 50.2] | GPT-5.5 | Persona SSR | 62% | 52.8 | 44.8 | +8.0 |

## Table: rank correlation within the top-7 and within the bottom-7 (Spearman)

| Model | Method | Favorability top | Favorability bottom | Recommendation top | Recommendation bottom | Popularity top | Popularity bottom |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Persona DLR | – | 0.66 | – | -0.29 | 0.29 | 0.50 |
| GPT-5.5 | Persona SSR | 0.71 | -0.61 | 0.07 | -0.11 | -0.07 | 0.54 |
| GPT-5.5 | B2 persona-free LLM | 0.40 | -0.07 | 0.45 | 0.82 | 0.00 | 0.64 |
| Gemini 3.1 Pro | Persona DLR | 0.47 | -0.27 | -0.57 | 0.20 | -0.07 | 0.18 |
| Gemini 3.1 Pro | Persona SSR | 0.64 | -0.52 | 0.50 | 0.46 | 0.00 | 0.54 |
| Gemini 3.1 Pro | B2 persona-free LLM | 0.72 | -0.16 | 0.61 | 0.75 | 0.29 | 0.21 |
| Claude Sonnet 5 | Persona DLR | – | -0.51 | – | 0.36 | -0.21 | 0.29 |
| Claude Sonnet 5 | Persona SSR | 0.82 | -0.04 | 0.57 | -0.14 | -0.21 | 0.39 |
| Claude Sonnet 5 | B2 persona-free LLM | 0.29 | 0.45 | 0.43 | 0.96 | 0.07 | 0.64 |

## Table: DLR forward vs reversed option order (30 countries)

| Model | Item | T2B forward | T2B reversed | Mean country difference (pp) | p (sign-flip) |
| --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | Popularity | 37.3 | 31.0 | -6.3 | 0.000 |
| Claude Sonnet 5 | Favorability | 99.4 | 99.5 | +0.1 | 1.000 |
| Claude Sonnet 5 | Recommendation | 99.4 | 99.5 | +0.1 | 1.000 |
| GPT-5.5 | Popularity | 44.3 | 35.3 | -9.0 | 0.000 |
| GPT-5.5 | Favorability | 99.8 | 99.8 | +0.0 | 1.000 |
| GPT-5.5 | Recommendation | 99.8 | 99.7 | -0.1 | 1.000 |
| Gemini 3.1 Pro | Popularity | 44.0 | 37.9 | -6.1 | 0.000 |
| Gemini 3.1 Pro | Favorability | 97.5 | 96.5 | -1.0 | 0.024 |
| Gemini 3.1 Pro | Recommendation | 97.6 | 96.1 | -1.5 | 0.014 |

## Table: SSR anchor self-test (top-2-box share when the answer repeats an anchor; min–max over sets and domains)

| Item | Point 1 | Point 2 | Point 3 | Point 4 | Point 5 |
| --- | --- | --- | --- | --- | --- |
| Favorability | 3–5% | 5–9% | 9–18% | 76–83% | 88–90% |
| Popularity (13 domains) | 1–16% | 3–16% | 16–37% | 65–76% | 70–80% |
| Recommendation | 3–8% | 23–30% | 3–44% | 67–69% | 72–79% |

## Table: round-2 answers identical to the same twin's round-1 answer

| Model | Arm | Popularity items | Own preference items |
| --- | --- | --- | --- |
| GPT-5.5 | N1self | 0.0% | 0.1% |
| GPT-5.5 | N2random | 0.1% | 0.5% |
| GPT-5.5 | N3homophily | 0.1% | 0.1% |
| Gemini 3.1 Pro | N1self | 0.0% | 0.0% |
| Gemini 3.1 Pro | N2random | 0.5% | 1.1% |
| Gemini 3.1 Pro | N3homophily | 0.7% | 1.2% |
| Claude Sonnet 5 | N1self | 20.1% | 21.3% |
| Claude Sonnet 5 | N2random | 46.9% | 65.5% |
| Claude Sonnet 5 | N3homophily | 45.1% | 64.4% |

## Table: twins with identical personas and identical responses

| Model | Mode | Duplicate groups | Personas in groups | Same-prompt pairs | Identical responses |
| --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | SSR | 157 | 363 | 277 | 0 |
| Claude Sonnet 5 | DLR | 157 | 363 | 130 | 21 |
| GPT-5.5 | SSR | 157 | 363 | 277 | 0 |
| GPT-5.5 | DLR | 157 | 363 | 130 | 59 |
| Gemini 3.1 Pro | SSR | 157 | 363 | 277 | 15 |
| Gemini 3.1 Pro | DLR | 157 | 363 | 130 | 15 |

## Table: is the synthetic value closer to the previous wave? (countries with a printed change)

| Model | Method | Item | n | MAE vs 2025 wave | MAE vs 2024 wave | Closer to 2024 |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | Persona DLR | Favorability | 8 | 26.8 | 29.7 | 38% |
| Claude Sonnet 5 | Persona SSR | Favorability | 8 | 5.9 | 10.9 | 0% |
| Gemini 3.1 Pro | Persona DLR | Favorability | 8 | 24.6 | 27.6 | 38% |
| Gemini 3.1 Pro | Persona SSR | Favorability | 8 | 11.5 | 15.3 | 25% |
| GPT-5.5 | Persona DLR | Favorability | 8 | 27.4 | 30.4 | 38% |
| GPT-5.5 | Persona SSR | Favorability | 8 | 8.6 | 13.2 | 12% |
| Claude Sonnet 5 | Persona DLR | Recommendation | 10 | 35.0 | 36.0 | 50% |
| Claude Sonnet 5 | Persona SSR | Recommendation | 10 | 8.7 | 11.2 | 30% |
| Gemini 3.1 Pro | Persona DLR | Recommendation | 10 | 31.6 | 32.6 | 50% |
| Gemini 3.1 Pro | Persona SSR | Recommendation | 10 | 10.1 | 12.2 | 40% |
| GPT-5.5 | Persona DLR | Recommendation | 10 | 35.3 | 36.3 | 50% |
| GPT-5.5 | Persona SSR | Recommendation | 10 | 8.9 | 10.0 | 40% |

## Table: contamination probes

| Model | Probe | Item | Target | n | MAE | Bias | ρ | Spread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | recall of previous edition | Favorability | wave 15 (current) | 30 | 6.8 | +2.5 | 0.67 | 0.76 |
| Claude Sonnet 5 | recall of previous edition | Favorability | wave 14 (previous, implied) | 8 | 3.7 | +1.4 | 0.76 | 0.81 |
| Claude Sonnet 5 | recall of previous edition | Recommendation | wave 15 (current) | 19 | 8.4 | +1.0 | 0.69 | 0.71 |
| Claude Sonnet 5 | recall of previous edition | Recommendation | wave 14 (previous, implied) | 10 | 9.0 | +2.5 | 0.55 | 0.78 |
| Claude Sonnet 5 | B2 without survey description | Favorability | wave 15 listed | 14 | 11.4 | +9.7 | 0.71 | 0.31 |
| Claude Sonnet 5 | B2 without survey description | Favorability | wave 15 all 30 | 30 | 8.7 | +7.6 | 0.58 | 0.36 |
| Claude Sonnet 5 | B2 without survey description | Recommendation | wave 15 listed | 19 | 9.7 | +5.9 | 0.68 | 0.36 |
| Claude Sonnet 5 | B2 without survey description | Popularity | wave 15 listed | 14 | 8.4 | +6.3 | 0.71 | 0.63 |
| Gemini 3.1 Pro | recall of previous edition | Favorability | wave 15 (current) | 30 | 6.4 | +2.1 | 0.77 | 1.09 |
| Gemini 3.1 Pro | recall of previous edition | Favorability | wave 14 (previous, implied) | 8 | 3.9 | -2.5 | 0.88 | 1.11 |
| Gemini 3.1 Pro | recall of previous edition | Recommendation | wave 15 (current) | 19 | 6.4 | +0.0 | 0.79 | 1.02 |
| Gemini 3.1 Pro | recall of previous edition | Recommendation | wave 14 (previous, implied) | 10 | 7.7 | +2.2 | 0.70 | 0.96 |
| Gemini 3.1 Pro | B2 without survey description | Favorability | wave 15 listed | 14 | 15.3 | +15.3 | 0.72 | 0.41 |
| Gemini 3.1 Pro | B2 without survey description | Favorability | wave 15 all 30 | 30 | 12.8 | +12.8 | 0.80 | 0.45 |
| Gemini 3.1 Pro | B2 without survey description | Recommendation | wave 15 listed | 19 | 14.2 | +14.2 | 0.84 | 0.37 |
| Gemini 3.1 Pro | B2 without survey description | Popularity | wave 15 listed | 14 | 6.6 | +4.6 | 0.83 | 1.39 |
| GPT-5.5 | recall of previous edition | Favorability | wave 15 (current) | 30 | 11.9 | +11.9 | 0.75 | 0.63 |
| GPT-5.5 | recall of previous edition | Favorability | wave 14 (previous, implied) | 8 | 9.4 | +9.4 | 0.83 | 0.68 |
| GPT-5.5 | recall of previous edition | Recommendation | wave 15 (current) | 19 | 11.2 | +10.9 | 0.78 | 0.64 |
| GPT-5.5 | recall of previous edition | Recommendation | wave 14 (previous, implied) | 10 | 13.2 | +13.2 | 0.70 | 0.59 |
| GPT-5.5 | B2 without survey description | Favorability | wave 15 listed | 14 | 15.5 | +15.3 | 0.79 | 0.26 |
| GPT-5.5 | B2 without survey description | Favorability | wave 15 all 30 | 30 | 12.9 | +12.7 | 0.76 | 0.30 |
| GPT-5.5 | B2 without survey description | Recommendation | wave 15 listed | 19 | 11.0 | +10.0 | 0.83 | 0.34 |
| GPT-5.5 | B2 without survey description | Popularity | wave 15 listed | 14 | 9.8 | +9.4 | 0.85 | 0.83 |

Share of recall-probe answers the model labelled as recalled rather than guessed: Claude Sonnet 5 0%, Gemini 3.1 Pro 0%, GPT-5.5 0%

## Table: two-level bootstrap (twins within countries, then countries; 1,000 resamples)

| Model | Item | MAE DLR (95% CI) | MAE SSR (95% CI) | SSR − DLR (95% CI) |
| --- | --- | --- | --- | --- |
| GPT-5.5 | Favorability | 32.7 (24.9–40.4) | 13.6 (7.3–20.2) | -19.1 (-21.0 to -16.7) |
| GPT-5.5 | Recommendation | 33.2 (27.7–39.0) | 10.0 (7.4–13.2) | -23.2 (-28.4 to -17.6) |
| GPT-5.5 | Popularity | 8.2 (5.7–10.7) | 10.3 (6.3–14.3) | +2.1 (-3.0 to +7.0) |
| Gemini 3.1 Pro | Favorability | 29.3 (22.0–36.7) | 16.7 (9.9–23.6) | -12.7 (-14.2 to -10.7) |
| Gemini 3.1 Pro | Recommendation | 29.7 (24.7–35.2) | 11.1 (7.3–15.3) | -18.7 (-21.9 to -15.1) |
| Gemini 3.1 Pro | Popularity | 11.6 (7.9–15.5) | 7.9 (5.1–11.1) | -3.7 (-8.3 to +1.4) |
| Claude Sonnet 5 | Favorability | 32.3 (24.7–39.7) | 11.1 (6.4–16.4) | -21.2 (-24.3 to -17.6) |
| Claude Sonnet 5 | Recommendation | 32.9 (27.5–38.6) | 9.8 (6.5–13.8) | -23.0 (-27.0 to -18.5) |
| Claude Sonnet 5 | Popularity | 11.3 (8.0–15.4) | 8.3 (5.8–11.3) | -2.9 (-7.8 to +1.4) |

Noise ceiling: expected MAE of a perfect predictor from human sampling error alone = Favorability 1.2 pp, Recommendation 1.2 pp, Popularity 1.3 pp; with persona Monte Carlo error added, 1.2–1.7 pp.

Achieved vs printed persona margins (largest absolute gap in any category, median / maximum over 30 countries, pp): age_band 0.6 / 0.7; education 2.9 / 7.9; korea_awareness 0.5 / 0.9; marital 2.2 / 4.9; nationality 0.4 / 4.5; occupation 3.7 / 7.6; sex 0.0 / 0.0

## Table: MS main comparison, listed countries

| Information about the target country | Method | Model | Favorability MAE (95% CI) | bias | ρ | Recommendation MAE (95% CI) | bias | ρ | Popularity MAE (95% CI) | bias | ρ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| printed profile | Persona, DLR | GPT-5.5 | 32.7 (25.5–39.9) | +32.7 | 0.65 | 33.2 (27.3–39.0) | +33.2 | 0.48 | 8.2 (5.7–10.4) | -1.6 | 0.77 |
| printed profile | Persona, DLR | Gemini 3.1 Pro | 29.3 (22.6–36.2) | +29.3 | 0.61 | 29.7 (24.7–34.9) | +29.7 | 0.51 | 11.6 (7.9–15.2) | +0.8 | 0.69 |
| printed profile | Persona, DLR | Claude Sonnet 5 | 32.3 (25.3–39.4) | +32.3 | 0.47 | 32.9 (27.3–38.5) | +32.9 | 0.66 | 11.3 (7.8–15.3) | -6.3 | 0.56 |
| printed profile | Persona, SSR | GPT-5.5 | 13.6 (7.7–20.0) | +12.5 | 0.61 | 10.0 (7.5–12.9) | +0.1 | 0.73 | 10.3 (6.3–14.1) | +9.4 | 0.70 |
| printed profile | Persona, SSR | Gemini 3.1 Pro | 16.7 (10.2–23.3) | +16.4 | 0.73 | 11.1 (7.3–15.0) | +6.0 | 0.53 | 7.9 (5.3–10.8) | +6.4 | 0.74 |
| printed profile | Persona, SSR | Claude Sonnet 5 | 11.1 (6.4–16.2) | +9.1 | 0.82 | 9.8 (6.6–13.4) | +3.6 | 0.74 | 8.3 (5.7–10.9) | +4.4 | 0.67 |
| country name | Persona-free LLM (B2) | GPT-5.5 | 15.7 (9.7–21.8) | +15.3 | 0.71 | 10.8 (7.0–15.0) | +9.9 | 0.72 | 11.7 (9.4–14.1) | +11.7 | 0.83 |
| country name | Persona-free LLM (B2) | Gemini 3.1 Pro | 15.8 (10.5–21.3) | +15.8 | 0.82 | 12.9 (8.8–17.5) | +12.9 | 0.79 | 6.9 (4.6–9.6) | +5.5 | 0.82 |
| country name | Persona-free LLM (B2) | Claude Sonnet 5 | 11.6 (7.1–16.2) | +9.1 | 0.78 | 9.3 (6.8–12.3) | +5.8 | 0.80 | 8.9 (6.3–11.5) | +7.7 | 0.84 |
| printed profile (one share) | Profile regression (B-PROFILE) | – | 8.1 (4.9–11.8) | -0.1 | 0.62 | 9.9 (6.6–13.7) | -0.0 | 0.35 | 4.5 (2.3–6.9) | -0.1 | 0.71 |
| none | Uniform 40% (B0) | – | 27.0 (20.0–34.4) | -27.0 | – | 26.8 (21.3–32.3) | -26.4 | – | 10.9 (9.0–12.8) | -2.4 | – |
| pooled total incl. target | 30-country total (B5) | – | 14.0 (11.7–16.5) | +2.7 | – | 11.1 (8.3–14.5) | +1.3 | – | 10.9 (9.5–12.5) | +0.5 | – |
| none | Total without target (B5-LOO) | – | 14.5 (12.1–17.0) | +2.7 | – | 11.6 (8.4–15.0) | +1.3 | – | 11.2 (9.9–13.0) | +0.5 | – |
| none | Mean of other countries (LOCO) | – | 15.1 (13.0–17.4) | -0.0 | – | 12.0 (9.2–15.0) | +0.0 | – | 11.7 (10.3–13.4) | -0.0 | – |
| none | Continent mean (LOCO-continent) | – | 10.6 (6.8–14.7) | -1.8 | 0.11 | 10.3 (7.0–14.1) | -1.3 | 0.20 | 4.3 (2.0–7.4) | -0.0 | 0.53 |

## Table: MS corrections, listed countries

| Method | Model | Favorability MAE (n) | Δ vs comparator (95% CI) | p (Holm) | Recommendation MAE (n) | Δ vs comparator (95% CI) | p (Holm) | Popularity MAE (n) | Δ vs comparator (95% CI) | p (Holm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SSR + CAL-LOCO (vs continent mean) | GPT-5.5 | 9.5 (14) | -1.1 (-4.6 to +2.6) | 1.000 | 8.1 (19) | -2.2 (-5.2 to +0.9) | 1.000 | 7.1 (14) | +2.8 (+0.6 to +5.2) | 0.317 |
| SSR + CAL-LOCO (vs continent mean) | Gemini 3.1 Pro | 8.4 (14) | -2.2 (-5.6 to +1.6) | 1.000 | 10.5 (19) | +0.2 (-3.2 to +3.7) | 1.000 | 6.3 (14) | +2.0 (+0.0 to +3.8) | 0.775 |
| SSR + CAL-LOCO (vs continent mean) | Claude Sonnet 5 | 6.4 (14) | -4.2 (-7.3 to -0.8) | 0.236 | 7.2 (19) | -3.1 (-6.1 to -0.1) | 0.698 | 6.9 (14) | +2.6 (+0.6 to +4.8) | 0.112 |
| SSR + country offset, CAL-STYLE (vs B-XITEM) | GPT-5.5 | 4.2 (13) | +0.6 (-0.5 to +1.7) | 1.000 | 3.3 (13) | -1.0 (-2.0 to +0.0) | 1.000 | 4.8 (11) | +1.2 (-1.5 to +3.5) | 1.000 |
| SSR + country offset, CAL-STYLE (vs B-XITEM) | Gemini 3.1 Pro | 4.5 (13) | +0.9 (-0.3 to +2.1) | 1.000 | 5.4 (13) | +1.1 (-0.4 to +2.6) | 1.000 | 7.4 (11) | +3.7 (+1.0 to +6.1) | 0.160 |
| SSR + country offset, CAL-STYLE (vs B-XITEM) | Claude Sonnet 5 | 3.6 (13) | +0.0 (-0.7 to +0.8) | 1.000 | 4.2 (13) | -0.1 (-1.4 to +1.2) | 1.000 | 3.9 (11) | +0.2 (-1.8 to +2.2) | 1.000 |
| Continent mean (LOCO-continent) | – | 10.6 (14) |  |  | 10.3 (19) |  |  | 4.3 (14) |  |  |
| Cross-item regression (B-XITEM) | – | 3.6 (13) |  |  | 4.3 (13) |  |  | 3.7 (11) |  |  |
| Previous wave (B1, change-selected) | – | 3.9 (4) |  |  | 5.8 (10) |  |  | – |  |  |

## Table: MS calibration of every elicitation, all 30 countries

| Model | SSR, uncalibrated | SSR + CAL-LOCO | DLR + CAL-LOCO | B2 + CAL-LOCO | B-PROFILE (no LLM) | SSR+CAL − DLR+CAL (p) | SSR+CAL − B2+CAL (p) | SSR+CAL − B-PROFILE (p) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 10.8 | 6.7 | 9.1 | 7.8 | 6.8 | -2.4 (0.061) | -1.1 (0.328) | -0.1 (0.835) |
| Gemini 3.1 Pro | 14.7 | 6.6 | 8.6 | 5.9 | 6.8 | -1.9 (0.048) | +0.7 (0.392) | -0.2 (0.834) |
| Claude Sonnet 5 | 7.8 | 5.6 | 7.9 | 6.8 | 6.8 | -2.3 (0.044) | -1.2 (0.298) | -1.2 (0.134) |

## Table: S calibration of every elicitation, listed countries

| Model | Item | n | SSR + CAL-LOCO | DLR + CAL-LOCO | B2 + CAL-LOCO | SSR+CAL − DLR+CAL (p) | SSR+CAL − B2+CAL (p) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Favorability | 14 | 9.5 | 11.4 | 11.7 | -1.9 (0.477) | -2.2 (0.290) |
| Gemini 3.1 Pro | Favorability | 14 | 8.4 | 11.5 | 6.1 | -3.1 (0.068) | +2.4 (0.096) |
| Claude Sonnet 5 | Favorability | 14 | 6.4 | 13.4 | 7.4 | -7.0 (0.004) | -1.0 (0.549) |
| GPT-5.5 | Recommendation | 19 | 8.1 | 10.8 | 7.8 | -2.7 (0.136) | +0.3 (0.876) |
| Gemini 3.1 Pro | Recommendation | 19 | 10.5 | 9.2 | 7.0 | +1.3 (0.456) | +3.5 (0.110) |
| Claude Sonnet 5 | Recommendation | 19 | 7.2 | 8.7 | 7.9 | -1.4 (0.491) | -0.7 (0.686) |
| GPT-5.5 | Popularity | 14 | 7.1 | 6.3 | 4.0 | +0.8 (0.046) | +3.2 (0.038) |
| Gemini 3.1 Pro | Popularity | 14 | 6.3 | 7.1 | 4.1 | -0.8 (0.155) | +2.2 (0.095) |
| Claude Sonnet 5 | Popularity | 14 | 6.9 | 7.8 | 6.9 | -0.9 (0.171) | +0.0 (0.990) |

## Table: MS scoring of the same free-text answers

| Model | Item (countries) | SSR, main: MAE (bias) | SSR, one anchor set: MAE range (bias range) | Nearest anchor: MAE (bias) | LLM judge: MAE (bias) | Answers judged top-2 | ρ with human: SSR | ρ with human: judge top-box share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Favorability (30) | 10.8 (+10.2) | 9.2–12.9 (+7.7 to +12.7) | 31.0 (+31.0) | 31.0 (+31.0) | 100.0% | 0.55 | 0.54 |
| Gemini 3.1 Pro | Favorability (30) | 14.7 (+14.6) | 11.6–17.1 (+11.1 to +17.1) | 30.7 (+30.7) | 30.9 (+30.9) | 99.9% | 0.64 | 0.61 |
| Claude Sonnet 5 | Favorability (30) | 7.8 (+6.9) | 7.3–9.4 (+5.2 to +8.8) | 29.5 (+29.5) | 30.9 (+30.9) | 99.9% | 0.79 | 0.79 |
| GPT-5.5 | Recommendation (19) | 10.0 (+0.1) | 12.8–13.5 (-11.5 to +11.6) | 14.9 (+14.2) | 33.6 (+33.6) | 100.0% | 0.73 | 0.54 |
| Gemini 3.1 Pro | Recommendation (19) | 11.1 (+6.0) | 10.7–13.8 (-0.6 to +12.5) | 33.2 (+33.2) | 33.6 (+33.6) | 100.0% | 0.53 | 0.34 |
| Claude Sonnet 5 | Recommendation (19) | 9.8 (+3.6) | 10.8–12.8 (-4.5 to +11.7) | 27.7 (+27.7) | 33.2 (+33.2) | 99.7% | 0.74 | 0.45 |

Second judge (Claude Sonnet 5, every 10th batch): 1650 answers classified by both judges; exact agreement 89.2%, agreement on top-2 vs not 99.6%; the second judge put 97.7–100.0% of answers in the top two options (by model and item).

## Table: S SSR anchor-set variants

| Model | Variant | Item | Countries | n | MAE (pp) | Bias (pp) | ρ | Spread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | all sets (main) | Favorability | listed | 14 | 11.1 | +9.1 | 0.82 | 0.25 |
| Claude Sonnet 5 | all sets (main) | Favorability | all 30 | 30 | 7.8 | +6.9 | 0.79 | 0.30 |
| Claude Sonnet 5 | all sets (main) | Recommendation | listed | 19 | 9.8 | +3.6 | 0.74 | 0.12 |
| Claude Sonnet 5 | all sets (main) | Popularity | listed | 14 | 8.3 | +4.4 | 0.67 | 0.38 |
| Claude Sonnet 5 | anchor set 1 only | Favorability | listed | 14 | 10.4 | +9.0 | 0.84 | 0.33 |
| Claude Sonnet 5 | anchor set 1 only | Favorability | all 30 | 30 | 7.4 | +6.7 | 0.79 | 0.39 |
| Claude Sonnet 5 | anchor set 1 only | Recommendation | listed | 19 | 12.8 | +11.7 | 0.72 | 0.11 |
| Claude Sonnet 5 | anchor set 1 only | Popularity | listed | 14 | 8.0 | +3.2 | 0.67 | 0.42 |
| Claude Sonnet 5 | anchor set 2 only | Favorability | listed | 14 | 11.6 | +7.3 | 0.81 | 0.19 |
| Claude Sonnet 5 | anchor set 2 only | Favorability | all 30 | 30 | 7.3 | +5.2 | 0.81 | 0.21 |
| Claude Sonnet 5 | anchor set 2 only | Recommendation | listed | 19 | 10.8 | -4.5 | 0.71 | 0.14 |
| Claude Sonnet 5 | anchor set 2 only | Popularity | listed | 14 | 8.7 | +5.7 | 0.66 | 0.34 |
| Claude Sonnet 5 | nearest anchor (hard) | Favorability | listed | 14 | 31.5 | +31.5 | 0.70 | 0.08 |
| Claude Sonnet 5 | nearest anchor (hard) | Favorability | all 30 | 30 | 29.5 | +29.5 | 0.66 | 0.13 |
| Claude Sonnet 5 | nearest anchor (hard) | Recommendation | listed | 19 | 27.7 | +27.7 | 0.54 | 0.23 |
| Claude Sonnet 5 | nearest anchor (hard) | Popularity | listed | 14 | 11.6 | +11.6 | 0.69 | 0.81 |
| Claude Sonnet 5 | without anchor set 1 | Favorability | listed | 14 | 11.6 | +9.1 | 0.81 | 0.21 |
| Claude Sonnet 5 | without anchor set 1 | Favorability | all 30 | 30 | 8.1 | +7.0 | 0.79 | 0.25 |
| Claude Sonnet 5 | without anchor set 2 | Favorability | listed | 14 | 11.3 | +10.0 | 0.79 | 0.28 |
| Claude Sonnet 5 | without anchor set 2 | Favorability | all 30 | 30 | 8.4 | +7.7 | 0.77 | 0.34 |
| Claude Sonnet 5 | anchor set 3 only | Favorability | listed | 14 | 12.2 | +11.0 | 0.77 | 0.24 |
| Claude Sonnet 5 | anchor set 3 only | Favorability | all 30 | 30 | 9.4 | +8.8 | 0.75 | 0.29 |
| Claude Sonnet 5 | without anchor set 3 | Favorability | listed | 14 | 10.8 | +8.1 | 0.86 | 0.26 |
| Claude Sonnet 5 | without anchor set 3 | Favorability | all 30 | 30 | 7.2 | +5.9 | 0.81 | 0.30 |
| GPT-5.5 | all sets (main) | Favorability | listed | 14 | 13.6 | +12.5 | 0.61 | 0.13 |
| GPT-5.5 | all sets (main) | Favorability | all 30 | 30 | 10.8 | +10.2 | 0.55 | 0.15 |
| GPT-5.5 | all sets (main) | Recommendation | listed | 19 | 10.0 | +0.1 | 0.73 | 0.15 |
| GPT-5.5 | all sets (main) | Popularity | listed | 14 | 10.3 | +9.4 | 0.70 | 0.41 |
| GPT-5.5 | anchor set 1 only | Favorability | listed | 14 | 15.2 | +14.9 | 0.70 | 0.15 |
| GPT-5.5 | anchor set 1 only | Favorability | all 30 | 30 | 12.9 | +12.7 | 0.60 | 0.16 |
| GPT-5.5 | anchor set 1 only | Recommendation | listed | 19 | 12.8 | +11.6 | 0.52 | 0.12 |
| GPT-5.5 | anchor set 1 only | Popularity | listed | 14 | 9.8 | +8.4 | 0.67 | 0.38 |
| GPT-5.5 | anchor set 2 only | Favorability | listed | 14 | 13.1 | +10.0 | 0.56 | 0.10 |
| GPT-5.5 | anchor set 2 only | Favorability | all 30 | 30 | 9.2 | +7.7 | 0.45 | 0.14 |
| GPT-5.5 | anchor set 2 only | Recommendation | listed | 19 | 13.5 | -11.5 | 0.76 | 0.21 |
| GPT-5.5 | anchor set 2 only | Popularity | listed | 14 | 10.9 | +10.5 | 0.68 | 0.43 |
| GPT-5.5 | nearest anchor (hard) | Favorability | listed | 14 | 33.0 | +33.0 | – | 0.00 |
| GPT-5.5 | nearest anchor (hard) | Favorability | all 30 | 30 | 31.0 | +31.0 | – | 0.00 |
| GPT-5.5 | nearest anchor (hard) | Recommendation | listed | 19 | 14.9 | +14.2 | 0.52 | 0.47 |
| GPT-5.5 | nearest anchor (hard) | Popularity | listed | 14 | 18.8 | +18.8 | 0.71 | 0.91 |
| GPT-5.5 | without anchor set 1 | Favorability | listed | 14 | 13.2 | +11.2 | 0.60 | 0.12 |
| GPT-5.5 | without anchor set 1 | Favorability | all 30 | 30 | 9.9 | +9.0 | 0.54 | 0.14 |
| GPT-5.5 | without anchor set 2 | Favorability | listed | 14 | 14.4 | +13.7 | 0.63 | 0.15 |
| GPT-5.5 | without anchor set 2 | Favorability | all 30 | 30 | 11.8 | +11.5 | 0.63 | 0.16 |
| GPT-5.5 | anchor set 3 only | Favorability | listed | 14 | 13.7 | +12.5 | 0.67 | 0.15 |
| GPT-5.5 | anchor set 3 only | Favorability | all 30 | 30 | 10.8 | +10.3 | 0.60 | 0.16 |
| GPT-5.5 | without anchor set 3 | Favorability | listed | 14 | 13.7 | +12.4 | 0.65 | 0.12 |
| GPT-5.5 | without anchor set 3 | Favorability | all 30 | 30 | 10.8 | +10.2 | 0.56 | 0.15 |
| Gemini 3.1 Pro | all sets (main) | Favorability | listed | 14 | 16.7 | +16.4 | 0.73 | 0.13 |
| Gemini 3.1 Pro | all sets (main) | Favorability | all 30 | 30 | 14.7 | +14.6 | 0.64 | 0.16 |
| Gemini 3.1 Pro | all sets (main) | Recommendation | listed | 19 | 11.1 | +6.0 | 0.53 | 0.04 |
| Gemini 3.1 Pro | all sets (main) | Popularity | listed | 14 | 7.9 | +6.4 | 0.74 | 0.59 |
| Gemini 3.1 Pro | anchor set 1 only | Favorability | listed | 14 | 17.5 | +17.5 | 0.71 | 0.14 |
| Gemini 3.1 Pro | anchor set 1 only | Favorability | all 30 | 30 | 15.6 | +15.6 | 0.58 | 0.17 |
| Gemini 3.1 Pro | anchor set 1 only | Recommendation | listed | 19 | 13.8 | +12.5 | -0.43 | 0.06 |
| Gemini 3.1 Pro | anchor set 1 only | Popularity | listed | 14 | 6.8 | +3.5 | 0.72 | 0.59 |
| Gemini 3.1 Pro | anchor set 2 only | Favorability | listed | 14 | 14.0 | +12.9 | 0.81 | 0.11 |
| Gemini 3.1 Pro | anchor set 2 only | Favorability | all 30 | 30 | 11.6 | +11.1 | 0.65 | 0.14 |
| Gemini 3.1 Pro | anchor set 2 only | Recommendation | listed | 19 | 10.7 | -0.6 | 0.78 | 0.09 |
| Gemini 3.1 Pro | anchor set 2 only | Popularity | listed | 14 | 9.3 | +9.2 | 0.73 | 0.59 |
| Gemini 3.1 Pro | nearest anchor (hard) | Favorability | listed | 14 | 32.6 | +32.6 | 0.39 | 0.02 |
| Gemini 3.1 Pro | nearest anchor (hard) | Favorability | all 30 | 30 | 30.7 | +30.7 | 0.33 | 0.05 |
| Gemini 3.1 Pro | nearest anchor (hard) | Recommendation | listed | 19 | 33.2 | +33.2 | 0.49 | 0.04 |
| Gemini 3.1 Pro | nearest anchor (hard) | Popularity | listed | 14 | 15.9 | +15.9 | 0.75 | 1.13 |
| Gemini 3.1 Pro | without anchor set 1 | Favorability | listed | 14 | 16.2 | +15.9 | 0.74 | 0.13 |
| Gemini 3.1 Pro | without anchor set 1 | Favorability | all 30 | 30 | 14.2 | +14.1 | 0.63 | 0.16 |
| Gemini 3.1 Pro | without anchor set 2 | Favorability | listed | 14 | 18.2 | +18.2 | 0.73 | 0.15 |
| Gemini 3.1 Pro | without anchor set 2 | Favorability | all 30 | 30 | 16.4 | +16.4 | 0.64 | 0.17 |
| Gemini 3.1 Pro | anchor set 3 only | Favorability | listed | 14 | 18.9 | +18.9 | 0.61 | 0.16 |
| Gemini 3.1 Pro | anchor set 3 only | Favorability | all 30 | 30 | 17.1 | +17.1 | 0.60 | 0.19 |
| Gemini 3.1 Pro | without anchor set 3 | Favorability | listed | 14 | 15.6 | +15.2 | 0.76 | 0.12 |
| Gemini 3.1 Pro | without anchor set 3 | Favorability | all 30 | 30 | 13.5 | +13.3 | 0.65 | 0.15 |

## Table: S range of individual SSR scores

| Model | Item | Answers | Minimum | 1st percentile | 99th percentile | Maximum |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | Popularity (13 domains) | 39,000 | 0.0% | 1.7% | 83.1% | 94.9% |
| Claude Sonnet 5 | Favorability | 3,000 | 29.5% | 48.4% | 89.5% | 92.4% |
| Claude Sonnet 5 | Recommendation | 3,000 | 9.1% | 53.0% | 79.1% | 83.0% |
| Gemini 3.1 Pro | Popularity (13 domains) | 39,000 | 0.1% | 1.4% | 84.5% | 88.6% |
| Gemini 3.1 Pro | Favorability | 3,000 | 23.9% | 58.7% | 95.0% | 98.7% |
| Gemini 3.1 Pro | Recommendation | 3,000 | 41.4% | 63.7% | 82.2% | 89.4% |
| GPT-5.5 | Popularity (13 domains) | 39,000 | 0.6% | 3.1% | 83.5% | 87.4% |
| GPT-5.5 | Favorability | 3,000 | 51.5% | 63.1% | 90.4% | 95.0% |
| GPT-5.5 | Recommendation | 3,000 | 41.1% | 50.7% | 75.9% | 79.1% |

## Table: MS what the twins' country estimates track

| Model | ρ(SSR, human) | ρ(SSR, knowledge share) | ρ(SSR, own recall) | ρ(SSR, own B2) | β knowledge | β recall | R² | LOO MAE: knowledge share | LOO MAE: recall | LOO MAE: SSR | LOO MAE: knowledge + recall | LOO MAE: knowledge + recall + SSR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 0.55 | 0.74 | 0.65 | 0.47 | 0.71 | 0.31 | 0.75 | 6.8 | 6.0 | 6.7 | 5.0 | 5.3 |
| Gemini 3.1 Pro | 0.64 | 0.76 | 0.75 | 0.75 | 0.57 | 0.38 | 0.69 | 6.8 | 5.6 | 6.6 | 5.6 | 5.4 |
| Claude Sonnet 5 | 0.79 | 0.82 | 0.70 | 0.56 | 0.67 | 0.42 | 0.83 | 6.8 | 7.0 | 5.6 | 6.2 | 6.0 |

## Table: S favorability error by language group

| Model | Method | Group (n) | Bias, group | Bias, other countries | Raw difference | Difference adjusted for the human level (95% CI) |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5 | Persona SSR | English official language (8) | +2.2 | +8.6 | -6.3 | -0.5 (-2.0 to +1.0) |
| Claude Sonnet 5 | Persona SSR | Continental Europe (7) | +15.5 | +4.3 | +11.2 | -1.5 (-3.4 to +1.7) |
| Claude Sonnet 5 | Persona DLR | English official language (8) | +25.5 | +32.3 | -6.8 | +0.5 (+0.2 to +1.0) |
| Claude Sonnet 5 | Persona DLR | Continental Europe (7) | +42.0 | +27.0 | +15.1 | +0.1 (-1.1 to +1.6) |
| Claude Sonnet 5 | B2 persona-free LLM | English official language (8) | +4.2 | +9.5 | -5.4 | +0.3 (-1.9 to +2.8) |
| Claude Sonnet 5 | B2 persona-free LLM | Continental Europe (7) | +16.5 | +5.6 | +11.0 | -1.3 (-5.6 to +2.9) |
| Gemini 3.1 Pro | Persona SSR | English official language (8) | +9.7 | +16.4 | -6.8 | +0.0 (-1.2 to +1.2) |
| Gemini 3.1 Pro | Persona SSR | Continental Europe (7) | +25.1 | +11.4 | +13.7 | -0.6 (-1.9 to +1.0) |
| Gemini 3.1 Pro | Persona DLR | English official language (8) | +23.9 | +29.6 | -5.7 | +1.3 (-0.4 to +2.7) |
| Gemini 3.1 Pro | Persona DLR | Continental Europe (7) | +38.5 | +24.9 | +13.6 | -1.2 (-4.8 to +2.2) |
| Gemini 3.1 Pro | B2 persona-free LLM | English official language (8) | +7.1 | +15.1 | -8.0 | -3.1 (-5.5 to -0.6) |
| Gemini 3.1 Pro | B2 persona-free LLM | Continental Europe (7) | +22.2 | +10.1 | +12.1 | +1.9 (-1.5 to +6.5) |
| GPT-5.5 | Persona SSR | English official language (8) | +4.6 | +12.3 | -7.7 | -0.8 (-1.7 to +0.1) |
| GPT-5.5 | Persona SSR | Continental Europe (7) | +21.0 | +6.9 | +14.1 | -0.3 (-1.7 to +1.7) |
| GPT-5.5 | Persona DLR | English official language (8) | +25.5 | +32.8 | -7.3 | +0.2 (-0.0 to +0.4) |
| GPT-5.5 | Persona DLR | Continental Europe (7) | +42.6 | +27.3 | +15.3 | -0.0 (-0.6 to +0.6) |
| GPT-5.5 | B2 persona-free LLM | English official language (8) | +7.2 | +14.9 | -7.7 | -1.7 (-3.6 to +0.3) |
| GPT-5.5 | B2 persona-free LLM | Continental Europe (7) | +23.8 | +9.5 | +14.3 | +2.2 (-1.7 to +7.5) |

## Table: S anchor similarity

| Item | Anchor sets | Mean pairwise cosine (range over sets) | Lowest pair | Highest pair | Point 1 vs point 5 | Point 4 vs point 5 |
| --- | --- | --- | --- | --- | --- | --- |
| Favorability | 3 | 0.84 (0.80–0.90) | 0.72 | 0.99 | 0.72–0.87 | 0.87–0.99 |
| Recommendation | 2 | 0.82 (0.80–0.83) | 0.71 | 0.92 | 0.71–0.80 | 0.90–0.91 |
| Popularity (13 domains) | 26 | 0.75 (0.69–0.84) | 0.56 | 0.96 | 0.64–0.78 | 0.82–0.96 |

## Table: S persona gradients

| Model | Mode | Item | Attribute | Top-2-box share by level, % | Largest gap (pp) | Spearman ρ (p) |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | DLR | Favorability | Knowledge of Korea (very well / somewhat / little) | 100.0 / 100.0 / 98.8 | 1.2 | -0.80 (0.000) |
| GPT-5.5 | DLR | Favorability | Age (15–19 / 20s / 30s / 40s / 50s) | 100.0 / 100.0 / 99.9 / 99.5 / 99.2 | 0.8 | -0.15 (0.000) |
| GPT-5.5 | DLR | Favorability | Sex (male / female) | 99.6 / 100.0 | 0.4 | – |
| GPT-5.5 | DLR | Favorability | Nationality (Korean-descended / local / third-country) | 100.0 / 99.8 / 100.0 | 0.2 | – |
| GPT-5.5 | DLR | Recommendation | Knowledge of Korea (very well / somewhat / little) | 100.0 / 100.0 / 98.5 | 1.5 | -0.79 (0.000) |
| GPT-5.5 | DLR | Recommendation | Age (15–19 / 20s / 30s / 40s / 50s) | 100.0 / 100.0 / 99.7 / 99.5 / 99.2 | 0.8 | -0.12 (0.000) |
| GPT-5.5 | DLR | Recommendation | Sex (male / female) | 99.5 / 100.0 | 0.5 | – |
| GPT-5.5 | DLR | Recommendation | Nationality (Korean-descended / local / third-country) | 100.0 / 99.8 / 100.0 | 0.2 | – |
| GPT-5.5 | SSR | Favorability | Knowledge of Korea (very well / somewhat / little) | 85.4 / 78.9 / 69.8 | 15.6 | -0.74 (0.000) |
| GPT-5.5 | SSR | Favorability | Age (15–19 / 20s / 30s / 40s / 50s) | 79.8 / 79.9 / 79.0 / 78.3 / 77.7 | 2.2 | -0.03 (0.097) |
| GPT-5.5 | SSR | Favorability | Sex (male / female) | 77.5 / 80.9 | 3.4 | – |
| GPT-5.5 | SSR | Favorability | Nationality (Korean-descended / local / third-country) | 75.4 / 79.2 / 79.4 | 4.0 | – |
| GPT-5.5 | SSR | Recommendation | Knowledge of Korea (very well / somewhat / little) | 70.0 / 66.2 / 62.7 | 7.3 | -0.35 (0.000) |
| GPT-5.5 | SSR | Recommendation | Age (15–19 / 20s / 30s / 40s / 50s) | 68.7 / 67.5 / 65.9 / 64.8 / 64.1 | 4.5 | -0.18 (0.000) |
| GPT-5.5 | SSR | Recommendation | Sex (male / female) | 65.7 / 67.5 | 1.8 | – |
| GPT-5.5 | SSR | Recommendation | Nationality (Korean-descended / local / third-country) | 64.3 / 66.6 / 69.3 | 5.0 | – |
| Gemini 3.1 Pro | DLR | Favorability | Knowledge of Korea (very well / somewhat / little) | 100.0 / 99.8 / 82.3 | 17.7 | -0.78 (0.000) |
| Gemini 3.1 Pro | DLR | Favorability | Age (15–19 / 20s / 30s / 40s / 50s) | 98.0 / 98.4 / 97.6 / 94.8 / 93.4 | 5.0 | -0.20 (0.000) |
| Gemini 3.1 Pro | DLR | Favorability | Sex (male / female) | 94.4 / 99.7 | 5.3 | – |
| Gemini 3.1 Pro | DLR | Favorability | Nationality (Korean-descended / local / third-country) | 100.0 / 97.0 / 95.9 | 4.1 | – |
| Gemini 3.1 Pro | DLR | Recommendation | Knowledge of Korea (very well / somewhat / little) | 100.0 / 99.5 / 82.1 | 17.9 | -0.77 (0.000) |
| Gemini 3.1 Pro | DLR | Recommendation | Age (15–19 / 20s / 30s / 40s / 50s) | 97.7 / 98.4 / 97.6 / 94.3 / 93.1 | 5.3 | -0.20 (0.000) |
| Gemini 3.1 Pro | DLR | Recommendation | Sex (male / female) | 94.1 / 99.6 | 5.5 | – |
| Gemini 3.1 Pro | DLR | Recommendation | Nationality (Korean-descended / local / third-country) | 100.0 / 96.9 / 95.9 | 4.1 | – |
| Gemini 3.1 Pro | SSR | Favorability | Knowledge of Korea (very well / somewhat / little) | 89.2 / 83.7 / 73.7 | 15.5 | -0.57 (0.000) |
| Gemini 3.1 Pro | SSR | Favorability | Age (15–19 / 20s / 30s / 40s / 50s) | 83.7 / 84.3 / 84.0 / 82.3 / 82.0 | 2.3 | +0.03 (0.083) |
| Gemini 3.1 Pro | SSR | Favorability | Sex (male / female) | 81.1 / 86.0 | 4.9 | – |
| Gemini 3.1 Pro | SSR | Favorability | Nationality (Korean-descended / local / third-country) | 84.7 / 83.6 / 82.8 | 1.9 | – |
| Gemini 3.1 Pro | SSR | Recommendation | Knowledge of Korea (very well / somewhat / little) | 73.4 / 72.4 / 70.7 | 2.7 | -0.03 (0.107) |
| Gemini 3.1 Pro | SSR | Recommendation | Age (15–19 / 20s / 30s / 40s / 50s) | 72.2 / 72.1 / 72.4 / 72.7 / 72.7 | 0.6 | +0.04 (0.014) |
| Gemini 3.1 Pro | SSR | Recommendation | Sex (male / female) | 73.0 / 71.8 | 1.2 | – |
| Gemini 3.1 Pro | SSR | Recommendation | Nationality (Korean-descended / local / third-country) | 73.2 / 72.3 / 74.1 | 1.8 | – |
| Claude Sonnet 5 | DLR | Favorability | Knowledge of Korea (very well / somewhat / little) | 100.0 / 99.8 / 97.1 | 2.9 | -0.67 (0.000) |
| Claude Sonnet 5 | DLR | Favorability | Age (15–19 / 20s / 30s / 40s / 50s) | 100.0 / 99.7 / 99.7 / 98.7 / 97.8 | 2.2 | -0.26 (0.000) |
| Claude Sonnet 5 | DLR | Favorability | Sex (male / female) | 98.9 / 100.0 | 1.1 | – |
| Claude Sonnet 5 | DLR | Favorability | Nationality (Korean-descended / local / third-country) | 100.0 / 99.4 / 100.0 | 0.6 | – |
| Claude Sonnet 5 | DLR | Recommendation | Knowledge of Korea (very well / somewhat / little) | 100.0 / 99.8 / 97.1 | 2.9 | -0.67 (0.000) |
| Claude Sonnet 5 | DLR | Recommendation | Age (15–19 / 20s / 30s / 40s / 50s) | 100.0 / 99.7 / 99.7 / 98.7 / 97.8 | 2.2 | -0.26 (0.000) |
| Claude Sonnet 5 | DLR | Recommendation | Sex (male / female) | 98.9 / 100.0 | 1.1 | – |
| Claude Sonnet 5 | DLR | Recommendation | Nationality (Korean-descended / local / third-country) | 100.0 / 99.4 / 100.0 | 0.6 | – |
| Claude Sonnet 5 | SSR | Favorability | Knowledge of Korea (very well / somewhat / little) | 84.8 / 74.7 / 64.9 | 19.8 | -0.68 (0.000) |
| Claude Sonnet 5 | SSR | Favorability | Age (15–19 / 20s / 30s / 40s / 50s) | 80.3 / 76.1 / 74.6 / 72.9 / 71.8 | 8.6 | -0.30 (0.000) |
| Claude Sonnet 5 | SSR | Favorability | Sex (male / female) | 72.9 / 78.7 | 5.8 | – |
| Claude Sonnet 5 | SSR | Favorability | Nationality (Korean-descended / local / third-country) | 73.4 / 75.9 / 74.1 | 2.5 | – |
| Claude Sonnet 5 | SSR | Recommendation | Knowledge of Korea (very well / somewhat / little) | 73.6 / 70.0 / 65.2 | 8.4 | -0.28 (0.000) |
| Claude Sonnet 5 | SSR | Recommendation | Age (15–19 / 20s / 30s / 40s / 50s) | 71.7 / 70.4 / 70.1 / 69.0 / 68.1 | 3.6 | -0.07 (0.000) |
| Claude Sonnet 5 | SSR | Recommendation | Sex (male / female) | 69.2 / 71.2 | 2.0 | – |
| Claude Sonnet 5 | SSR | Recommendation | Nationality (Korean-descended / local / third-country) | 69.2 / 70.2 / 71.1 | 1.9 | – |
