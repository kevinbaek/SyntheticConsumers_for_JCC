#!/usr/bin/env bash
# Every number and figure of the manuscript, from the three final runs (no model calls; embeddings are cached).
#   bash scripts/run_final_analysis.sh [runs_root=outputs] [dest=outputs/analysis_final]
set -euo pipefail
ROOT=${1:-outputs}
DEST=${2:-outputs/analysis_final}
RUNS="$ROOT/final_claude-sonnet-5 $ROOT/final_gpt-5.5 $ROOT/final_gemini-3.1-pro"
export PYTHONPATH=${PYTHONPATH:-$(pwd)}
mkdir -p "$DEST"
python3 -W ignore -m hallyu_twins.analysis_table --runs $RUNS --embedding openai --dest "$DEST"
python3 -W ignore -m hallyu_twins.extra_analyses --runs $RUNS --est "$DEST/estimates.csv" --dest "$DEST" --embedding openai
python3 -W ignore -m hallyu_twins.robustness --runs $RUNS --est "$DEST/estimates.csv" --dest "$DEST" --embedding openai
python3 -W ignore scripts/cost_table.py "$ROOT" > "$DEST/cost_table.md"
python3 -W ignore scripts/make_paper_tables.py "$DEST" > "$DEST/paper_tables.md"
python3 -W ignore scripts/make_doc_chart_data.py "$DEST"
python3 -W ignore scripts/make_figures.py "$DEST" "$DEST/figures"
# Figure 1 is drawn with Graphviz from its source (replaces the placeholder written by make_figures.py)
if command -v dot >/dev/null; then dot -Tpng -Gdpi=200 docs/figure_sources/fig1_study_design.dot -o "$DEST/figures/fig1_study_design.png"; fi
python3 -W ignore verify/independent_check.py $RUNS "$DEST/estimates.csv"
echo "done: $DEST"
