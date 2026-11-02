"""Sentence embedders for Semantic Similarity Rating (SSR).

* openai : text-embedding-3-small (the embedder used by Maier et al., 2025) -- main study.
* onnx   : all-MiniLM-L6-v2 run locally with onnxruntime (no network) -- pilot / offline.
* mock   : hashed bag-of-words, for tests only.

Embeddings are cached on disk by (provider, model, text).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np

from .llm import Cache


class Embedder:
    name = "base"

    def __init__(self, cache: Cache | None = None):
        self.cache = cache

    batch = 64

    def embed(self, texts: list[str]) -> np.ndarray:
        keys = [self._k(t) for t in texts]
        hits = self.cache.get_many(list(set(keys))) if self.cache else {}
        out: list[np.ndarray | None] = [None] * len(texts)
        todo: dict[str, list[int]] = {}
        for i, k in enumerate(keys):
            if k in hits:
                out[i] = np.array(json.loads(hits[k]), dtype=np.float32)
            else:
                todo.setdefault(k, []).append(i)
        uniq = list(todo)
        for s in range(0, len(uniq), self.batch):
            ks = uniq[s:s + self.batch]
            vecs = self._embed([texts[todo[k][0]] for k in ks])
            rows = []
            for k, v in zip(ks, vecs):
                v = v / (np.linalg.norm(v) or 1.0)
                stored = [round(float(x), 6) for x in v]            # identical values on first and cached use
                arr = np.array(stored, dtype=np.float32)
                for i in todo[k]:
                    out[i] = arr
                rows.append((k, json.dumps(stored)))
            if self.cache:
                self.cache.put_many(rows)
        return np.vstack(out)

    def _k(self, text: str) -> str:
        return "emb:" + hashlib.sha256(f"{self.name}|{text}".encode()).hexdigest()

    def _embed(self, texts: list[str]) -> np.ndarray:  # pragma: no cover - abstract
        raise NotImplementedError


class OpenAIEmbedder(Embedder):
    batch = 512

    def __init__(self, model_id: str = "text-embedding-3-small", cache=None):
        super().__init__(cache)
        from openai import OpenAI
        self.client, self.model_id, self.name = OpenAI(), model_id, f"openai:{model_id}"

    def _embed(self, texts):
        r = self.client.embeddings.create(model=self.model_id, input=texts)
        return np.array([d.embedding for d in r.data], dtype=np.float32)


class OnnxEmbedder(Embedder):
    """Mean-pooled sentence-transformer exported to ONNX (default: all-MiniLM-L6-v2)."""

    def __init__(self, model_dir: str = "models/all-MiniLM-L6-v2", cache=None, max_len: int = 256):
        super().__init__(cache)
        import onnxruntime as ort
        from tokenizers import Tokenizer
        d = Path(model_dir)
        self._verify(d)
        self.tok = Tokenizer.from_file(str(d / "tokenizer.json"))
        self.tok.enable_padding()
        self.tok.enable_truncation(max_len)
        self.sess = ort.InferenceSession(str(d / "model.onnx"), providers=["CPUExecutionProvider"])
        self.inputs = {i.name for i in self.sess.get_inputs()}
        self.name = f"onnx:{d.name}"

    @staticmethod
    def _verify(d: Path) -> None:
        """Check model.onnx / tokenizer.json against the pinned Hugging Face sha256 values."""
        pins = d / "pins.json"
        if not pins.exists():
            return
        for f in json.loads(pins.read_text()).get("files", []):
            if f["path"] in ("model.onnx", "tokenizer.json"):
                got = hashlib.sha256((d / f["path"]).read_bytes()).hexdigest()
                if got != f["sha256"]:
                    raise RuntimeError(f"{f['path']} sha256 mismatch: {got} != {f['sha256']}")

    def _embed(self, texts):
        enc = self.tok.encode_batch(texts)
        ids = np.array([e.ids for e in enc], dtype=np.int64)
        mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        feeds = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in self.inputs:
            feeds["token_type_ids"] = np.zeros_like(ids)
        h = self.sess.run(None, feeds)[0]
        return (h * mask[..., None]).sum(1) / mask.sum(1, keepdims=True)


class MockEmbedder(Embedder):
    name = "mock:hash-bow"

    def _embed(self, texts):
        dim = 512
        out = np.zeros((len(texts), dim), dtype=np.float32)
        for i, t in enumerate(texts):
            toks = re.findall(r"[a-z']+", t.lower())
            toks += [a + "_" + b for a, b in zip(toks, toks[1:])]          # bigrams catch negation
            for w in toks:
                h = int(hashlib.md5(w.encode()).hexdigest()[:8], 16)
                out[i, h % dim] += 1.0 if (h >> 9) & 1 else -1.0
        return out + 1e-6


def make_embedder(spec: dict, cache: Cache | None) -> Embedder:
    p = spec.get("provider", "mock")
    if p == "openai":
        return OpenAIEmbedder(spec.get("model_id", "text-embedding-3-small"), cache)
    if p == "onnx":
        return OnnxEmbedder(spec.get("model_dir", "models/all-MiniLM-L6-v2"), cache)
    if p == "mock":
        return MockEmbedder(cache)
    raise ValueError(p)


def default_cache(cache_dir: str) -> Cache:
    os.makedirs(cache_dir, exist_ok=True)
    return Cache(os.path.join(cache_dir, "embeddings.sqlite"))
