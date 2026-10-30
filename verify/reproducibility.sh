#!/usr/bin/env bash
# Verification pass V5a: run the full analysis twice from the saved responses and compare every output byte-for-byte.
set -euo pipefail
cd "$(dirname "$0")/.."
RUNS="$@"
python3 -W ignore -m hallyu_twins.analysis_table --runs $RUNS --embedding openai --dest outputs/repro_a > /dev/null
python3 -W ignore -m hallyu_twins.analysis_table --runs $RUNS --embedding openai --dest outputs/repro_b > /dev/null
for f in outputs/repro_a/*.csv; do
  b=outputs/repro_b/$(basename $f)
  if cmp -s "$f" "$b"; then echo "identical  $(basename $f)"; else echo "DIFFERENT  $(basename $f)"; exit 1; fi
done
