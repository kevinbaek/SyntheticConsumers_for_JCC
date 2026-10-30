#!/usr/bin/env bash
# Offline SSR embedder: all-MiniLM-L6-v2 (fp32 ONNX, Xenova export, HF revision 751bff37).
# Primary source: Hugging Face. Fallback (when huggingface.co is blocked): npm mirror package
# @maycombhq/embed-model, whose pins.json records the HF URLs and sha256 values checked below.
set -euo pipefail
DEST="${1:-models/all-MiniLM-L6-v2}"
mkdir -p "$DEST"
REV=751bff37182d3f1213fa05d7196b954e230abad9
if curl -fsSL -o "$DEST/model.onnx" "https://huggingface.co/Xenova/all-MiniLM-L6-v2/resolve/$REV/onnx/model.onnx" \
   && curl -fsSL -o "$DEST/tokenizer.json" "https://huggingface.co/Xenova/all-MiniLM-L6-v2/resolve/$REV/tokenizer.json"; then
  echo "downloaded from Hugging Face"
else
  TMP=$(mktemp -d)
  curl -fsSL -o "$TMP/pkg.tgz" https://registry.npmjs.org/@maycombhq/embed-model/-/embed-model-2.0.0-beta.1.tgz
  tar xzf "$TMP/pkg.tgz" -C "$TMP"
  cp "$TMP/package/model.onnx" "$TMP/package/tokenizer.json" "$TMP/package/pins.json" "$TMP/package/LICENSE" "$DEST/"
  echo "downloaded from npm mirror"
fi
echo "759c3cd2b7fe7e93933ad23c4c9181b7396442a2ed746ec7c1d46192c469c46e  $DEST/model.onnx" | sha256sum -c -
echo "da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0  $DEST/tokenizer.json" | sha256sum -c -
