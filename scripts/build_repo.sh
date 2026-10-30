#!/usr/bin/env bash
# Assemble the public repository folder (no keys, caches or model weights) and scan it for secrets.
#   bash scripts/build_repo.sh /home/claude/SyntheticConsumers_for_JCC
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="${1:-$SRC/../SyntheticConsumers_for_JCC}"
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$SRC/hallyu_twins" "$SRC/configs" "$SRC/scripts" "$SRC/tests" "$SRC/verify" "$SRC/docs" "$DST/"
mkdir -p "$DST/data" && cp -r "$SRC/data/pdf_tables" "$DST/data/"
mkdir -p "$DST/models" && cp "$SRC/models/README.md" "$DST/models/" 2>/dev/null || true
cp "$SRC/pyproject.toml" "$SRC/README.md" "$DST/"
mkdir -p "$DST/paper" && cp "$SRC"/paper/Baek_Kim_JCC_manuscript.docx "$SRC"/paper/ms_part*.md "$SRC"/paper/refs.json "$SRC"/paper/build_docx.js "$DST/paper/"
[ -f "$SRC/LICENSE" ] && cp "$SRC/LICENSE" "$DST/"
cp "$SRC/.gitignore" "$SRC/.env.example" "$DST/"
# results: final runs (responses, scored items, run metadata) + analysis tables and figures
mkdir -p "$DST/results"
for r in "$SRC"/outputs/final_*; do
  [ -d "$r" ] || continue
  n=$(basename "$r"); mkdir -p "$DST/results/$n"
  for f in twins.csv twins_network.csv network.json raw_r1.jsonl raw_r2.jsonl raw_b2.jsonl jobs_r1.jsonl jobs_r2.jsonl \
           responses_r1.jsonl responses_r2.jsonl scored.csv b2_direct.csv run_meta.json parse_stats.json \
           call_usage.json token_measure.json r1_usage_estimate.json prompts_check.json run_meta_resume1.json \
           call_usage_resume1.json token_check.json; do
    [ -f "$r/$f" ] && cp "$r/$f" "$DST/results/$n/"
  done
  for f in prompts_r1.jsonl prompts_r2.jsonl prompts_b2.jsonl; do      # every prompt as sent (gzip: GitHub file size)
    [ -f "$r/$f" ] && gzip -c "$r/$f" > "$DST/results/$n/$f.gz"
  done
done
[ -d "$SRC/outputs/analysis_final" ] && cp -r "$SRC/outputs/analysis_final" "$DST/results/"
[ -d "$SRC/outputs/probes" ] && cp -r "$SRC/outputs/probes" "$DST/results/"
find "$DST" -name "__pycache__" -prune -exec rm -rf {} + ; find "$DST" -name "*.sqlite" -delete; rm -rf "$DST/.pytest_cache"
# secret scan: provider key shapes, plus the exact values of the keys in use when KEYS_FILE points to the
# (never released) key file; the values are read into a temporary pattern file and never printed
if grep -rIlE "sk-(proj|ant)-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}" "$DST"; then echo "SECRET FOUND - aborting"; exit 1; fi
if [ -n "${KEYS_FILE:-}" ] && [ -f "$KEYS_FILE" ]; then
  PAT=$(mktemp); sed -nE 's/^(export )?[A-Z_]+=["'"'"']?([^"'"'"' ]{12,})["'"'"']?$/\2/p' "$KEYS_FILE" > "$PAT"
  n=$(wc -l < "$PAT"); hit=$(grep -rIlF -f "$PAT" "$DST" || true); rm -f "$PAT"
  if [ -n "$hit" ]; then echo "SECRET VALUE FOUND in: $hit - aborting"; exit 1; fi
  echo "exact-value scan clean ($n key values)"
fi
echo "secret scan clean"; du -sh "$DST"; find "$DST" -type f | wc -l
