# Offline embedder (optional)
The main analysis uses OpenAI `text-embedding-3-small` (as in Maier et al., 2025). For an offline
sensitivity check, `bash scripts/fetch_minilm.sh` downloads all-MiniLM-L6-v2 (fp32 ONNX, Xenova export,
Hugging Face revision 751bff37) into `models/all-MiniLM-L6-v2/` and verifies its sha256. Weights are not
committed to this repository.
