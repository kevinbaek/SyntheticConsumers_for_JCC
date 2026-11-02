"""LLM clients with a shared, persistent response cache.

All clients are called *without* tools, web search or retrieval, so the model can only use
what is in its weights and the prompt (contamination control). Reasoning effort is set to the
lowest available level where the API exposes it (configure via ModelSpec.extra).

MockLLM produces deterministic, persona-sensitive answers so the full pipeline can be
dry-run before any API key or raw data is available. Its numbers mean nothing.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import threading
import time
from dataclasses import dataclass

import numpy as np

from .config import ModelSpec


@dataclass
class Completion:
    text: str
    cached: bool = False


class Cache:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")
        self._db.commit()

    def get(self, key: str) -> str | None:
        with self._lock:
            row = self._db.execute("SELECT v FROM kv WHERE k=?", (key,)).fetchone()
        return row[0] if row else None

    def put(self, key: str, value: str) -> None:
        with self._lock:
            self._db.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (key, value))
            self._db.commit()

    def get_many(self, keys: list[str]) -> dict[str, str]:
        out = {}
        with self._lock:
            for i in range(0, len(keys), 900):
                chunk = keys[i:i + 900]
                q = "SELECT k, v FROM kv WHERE k IN (%s)" % ",".join("?" * len(chunk))
                out.update(dict(self._db.execute(q, chunk).fetchall()))
        return out

    def put_many(self, items: list[tuple[str, str]]) -> None:
        with self._lock:
            self._db.executemany("INSERT OR REPLACE INTO kv VALUES (?, ?)", items)
            self._db.commit()


def _key(*parts) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


_USAGE_LOCK = threading.Lock()


class LLM:
    """Base class: subclasses implement _call(messages, rep)."""

    def __init__(self, spec: ModelSpec, cache: Cache | None = None, retries: int = 5):
        self.spec, self.cache, self.retries = spec, cache, retries
        self.usage: dict[str, int] = {}
        self._tl = threading.local()

    def last_usage(self) -> tuple[int, int, int]:
        """(input, output, thinking) tokens of the last API call made by the calling thread."""
        return getattr(self._tl, "last", (0, 0, 0))

    def complete(self, messages: list[dict], rep: int = 0, call_id: str | None = None) -> Completion:
        """call_id makes the cache entry specific to one twin/condition: two twins whose prompts are
        identical must still get independent samples (and a rerun must return each its own)."""
        key = _key(self.spec.provider, self.spec.model_id, self.spec.temperature, self.spec.max_tokens,
                   self.spec.extra, messages, rep, call_id)
        if self.cache and (hit := self.cache.get(key)) is not None:
            return Completion(hit, cached=True)
        for attempt in range(self.retries):
            try:
                text = self._call(messages, rep)
                break
            except Exception as e:  # noqa: BLE001 - provider SDKs raise many types
                if attempt == self.retries - 1:
                    raise
                time.sleep(min(60, 2 ** attempt + np.random.rand()))
                print(f"[llm] {self.spec.name} retry {attempt + 1}: {type(e).__name__}: {e}")
        if self.cache:
            self.cache.put(key, text)
        return Completion(text)

    def _call(self, messages: list[dict], rep: int) -> str:  # pragma: no cover - abstract
        raise NotImplementedError


class OpenAIChat(LLM):
    def __init__(self, spec, cache=None):
        super().__init__(spec, cache)
        from openai import OpenAI
        kw = {"base_url": spec.base_url} if spec.base_url else {}
        if spec.api_key_env:
            kw["api_key"] = os.environ[spec.api_key_env]
        self.client = OpenAI(timeout=120, max_retries=2, **kw)

    def _call(self, messages, rep):
        kw = dict(model=self.spec.model_id, messages=messages, temperature=self.spec.temperature,
                  max_completion_tokens=self.spec.max_tokens, seed=1000 + rep)
        kw = {k: v for k, v in kw.items() if v is not None}
        kw.update(self.spec.extra)            # e.g. {"reasoning_effort": "minimal"}
        r = self.client.chat.completions.create(**kw)
        if r.usage:
            with _USAGE_LOCK:
                self.usage["input"] = self.usage.get("input", 0) + (r.usage.prompt_tokens or 0)
                self.usage["output"] = self.usage.get("output", 0) + (r.usage.completion_tokens or 0)
                self.usage["calls"] = self.usage.get("calls", 0) + 1
        return r.choices[0].message.content or ""


class AnthropicChat(LLM):
    def __init__(self, spec, cache=None):
        super().__init__(spec, cache)
        import anthropic
        # Always pass base_url explicitly so an ambient ANTHROPIC_BASE_URL can never redirect the key.
        kw = {"base_url": spec.base_url or "https://api.anthropic.com", "timeout": 180, "max_retries": 2}
        if spec.api_key_env:
            kw["api_key"] = os.environ[spec.api_key_env]
        self.client = anthropic.Anthropic(**kw)

    def _call(self, messages, rep):
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        msgs = [m for m in messages if m["role"] != "system"]
        kw = dict(model=self.spec.model_id, system=system or None, messages=msgs,
                  temperature=self.spec.temperature, max_tokens=self.spec.max_tokens)
        kw = {k: v for k, v in kw.items() if v is not None}
        kw.update(self.spec.extra)
        r = self.client.messages.create(**kw)
        with _USAGE_LOCK:
            self.usage["input"] = self.usage.get("input", 0) + r.usage.input_tokens
            self.usage["output"] = self.usage.get("output", 0) + r.usage.output_tokens
            self.usage["calls"] = self.usage.get("calls", 0) + 1
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")


class GeminiChat(LLM):
    def __init__(self, spec, cache=None):
        super().__init__(spec, cache)
        from google import genai
        kw = {"api_key": os.environ[spec.api_key_env]} if spec.api_key_env else {}
        if spec.extra.get("vertexai"):                   # Vertex AI / Agent Platform express-mode key
            kw["vertexai"] = True
        self.client = genai.Client(**kw)

    def _call(self, messages, rep):
        from google.genai import types
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        contents = [types.Content(role="user" if m["role"] == "user" else "model",
                                  parts=[types.Part(text=m["content"])])
                    for m in messages if m["role"] != "system"]
        extra = {k: v for k, v in self.spec.extra.items() if k != "vertexai"}
        if "thinking_level" in extra:
            extra["thinking_config"] = types.ThinkingConfig(thinking_level=extra.pop("thinking_level"))
        cfg = types.GenerateContentConfig(system_instruction=system or None,
                                          temperature=self.spec.temperature,
                                          max_output_tokens=self.spec.max_tokens, seed=1000 + rep,
                                          **extra)
        r = self.client.models.generate_content(model=self.spec.model_id, contents=contents, config=cfg)
        u = r.usage_metadata
        if u:
            with _USAGE_LOCK:
                self.usage["input"] = self.usage.get("input", 0) + (u.prompt_token_count or 0)
                self.usage["output"] = self.usage.get("output", 0) + (u.candidates_token_count or 0)
                self.usage["thinking"] = self.usage.get("thinking", 0) + (u.thoughts_token_count or 0)
                self.usage["calls"] = self.usage.get("calls", 0) + 1
            self._tl.last = (u.prompt_token_count or 0, u.candidates_token_count or 0, u.thoughts_token_count or 0)
        return r.text or ""


# ---------------------------------------------------------------------------------------
# Mock: a crude "LLM" with stereotypes, positivity bias and variance compression
# ---------------------------------------------------------------------------------------
_MOCK_STEREOTYPE = {  # what a model "believes" about countries (invented, partly wrong)
    "Philippines": 1.0, "Indonesia": 1.0, "Thailand": 1.0, "Vietnam": 0.9, "Malaysia": 0.8, "India": 0.4,
    "Mexico": 0.7, "Brazil": 0.7, "Taiwan": 0.8, "China": 0.6, "Japan": 0.6, "Singapore": 0.7,
    "United States": 0.6, "UAE": 0.4, "Saudi Arabia": 0.4, "Egypt": 0.3, "South Africa": 0.2,
    "United Kingdom": 0.4, "Chile": 0.5, "Australia": 0.4, "Turkiye": 0.3, "Argentina": 0.4,
    "Spain": 0.4, "Canada": 0.4, "France": 0.4, "Italy": 0.2, "Poland": 0.1, "Germany": 0.1,
    "Kazakhstan": 0.3, "Russia": 0.2, "Hong Kong": 0.8,
}
_AGREE = {"strongly agree": 1.0, "agree": 0.5, "neither agree nor disagree": 0.0, "disagree": -0.5,
          "strongly disagree": -1.0}


def _mock_latent(prompt: str, rng: np.random.Generator) -> float:
    lat = 0.9                                        # positivity bias
    m = re.search(r"You live in (?:the )?([A-Z][A-Za-z ]+?)\.", prompt)
    if m:
        lat += 0.8 * (_MOCK_STEREOTYPE.get(m.group(1), 0.4) - 0.5)
    ag = [_AGREE[a] for a in re.findall(r"you (strongly agree|agree|neither agree nor disagree|disagree|"
                                        r"strongly disagree)\.", prompt)]
    if ag:
        lat += 0.9 * float(np.mean(ag))
    imp = re.search(r"overall impression of Korea is (very negative|somewhat negative|neutral|"
                    r"somewhat positive|very positive)", prompt)
    if imp:
        lat += {"very negative": -0.8, "somewhat negative": -0.4, "neutral": 0.0,
                "somewhat positive": 0.3, "very positive": 0.6}[imp.group(1)]
    if "know Korea very well" in prompt:
        lat += 0.3
    if "know little about Korea" in prompt:
        lat -= 0.3
    used = re.search(r"Korean content you have used: ([^.]+)\.", prompt)
    if used:
        lat += 0.08 * (used.group(1).count(",") + 1) - 0.3
    m = re.search(r"age(?:d)? ?(\d\d)|(\d\d)-year-old", prompt)
    if m:
        age = int(m.group(1) or m.group(2))
        lat -= 0.01 * (age - 35)
    # social exposure: drift toward what neighbours said
    nb = re.findall(r"Someone you know: \"([^\"]+)\"", prompt)
    if nb:
        lat += 0.25 * (np.mean([_mock_level_of(t) for t in nb]) - 3)
    return lat + rng.normal(0, 0.35)


def _mock_level_of(text: str) -> float:
    t = text.lower()
    for k, pats in ((1, ["not like it at all", "never recommend", "almost nobody"]),
                    (5, ["very much", "definitely", "sell well"]),
                    (2, ["do not like", "would not", "only among"]),
                    (4, ["i like it", "would recommend", "widely known"]),):
        if any(p in t for p in pats):
            return float(k)
    return 3.0


class MockLLM(LLM):
    """Deterministic given (prompt, rep). Understands the prompt formats in elicit.py."""

    def _call(self, messages, rep):
        prompt = "\n".join(m["content"] for m in messages)
        seed = int(hashlib.md5((prompt + str(rep)).encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        if "Write a short profile" in prompt:
            return "You are a practical person who enjoys entertainment from abroad and decides by word of mouth."
        if "Answer PASS or FAIL" in prompt:
            return "PASS - all statements supported."
        if "percentage of adults" in prompt:            # persona-free aggregate estimate (B2)
            base = 25 + 30 * rng.random()
            p = np.array([5, 10, 25, base, 60 - base]) + rng.uniform(0, 5, 5)
            p = np.maximum(p, 1)
            return json.dumps({str(i + 1): round(float(v / p.sum() * 100), 1) for i, v in enumerate(p)})
        if "Recall check" in prompt:
            return json.dumps({"value": round(float(50 + 30 * rng.random()), 1), "confidence": "low"})
        if "Reply with a JSON object only" in prompt:      # questionnaire mode (multicountry.py)
            out = {}
            for q, qtext in re.findall(r"^(Q\d\d)\. (.+)$", prompt, flags=re.M):
                lat = _mock_latent(prompt, rng)
                if "percentage" in prompt:
                    out[q] = round(float(np.clip(50 + 15 * lat + rng.normal(0, 8), 0, 100)), 1)
                    continue
                lvl = int(np.clip(np.round(3 + lat - (0.8 if "popular" in qtext else 0)), 1, 5))
                if "option number" in prompt:
                    blk = prompt.split(f"{q}. ", 1)[1]
                    first = re.search(r"^1\. (.+)$", blk, flags=re.M)
                    reversed_opts = bool(first) and _mock_level_of(first.group(1)) >= 4
                    out[q] = 6 - lvl if reversed_opts else lvl
                else:
                    sc = "recommend" if "recommend" in qtext else "popularity" if "popular" in qtext else "liking"
                    bank = _MOCK_PHRASES[sc][lvl - 1]
                    out[q] = bank[rng.integers(len(bank))]
            return json.dumps(out)
        lat = _mock_latent(prompt, rng)
        level = int(np.clip(np.round(3 + lat), 1, 5))
        labels = re.findall(r"^\s*\d\.\s(.+)$", prompt, flags=re.M)
        if "Reply with the number only" in prompt:      # DLR
            if labels and "1. " + labels[0] in prompt and _mock_level_of(labels[0]) >= 4:  # reversed scale
                return str(6 - level)
            return str(level)
        bank = _MOCK_PHRASES.get(_scale_of(prompt), _MOCK_PHRASES["liking"])
        return bank[level - 1][rng.integers(len(bank[level - 1]))]


def _scale_of(prompt: str) -> str:
    q = prompt.rsplit("Question:", 1)[-1].lower()
    if "recommend" in q:
        return "recommend"
    if "popular" in q:
        return "popularity"
    return "liking"


_MOCK_PHRASES = {
    "liking": [["Honestly I do not like it at all.", "Not for me at all, I really dislike it."],
               ["I do not like it much.", "It is not really my thing, I don't like it."],
               ["It is so-so for me, neither good nor bad.", "It's okay, nothing special."],
               ["I like it, it is enjoyable.", "I quite like it."],
               ["I like it very much, I love it.", "I really love it, it is one of my favourites."]],
    "recommend": [["I would never recommend it to anyone.", "No way I would recommend it."],
                  ["I would not recommend it.", "Probably I would not suggest it to friends."],
                  ["I am neutral about recommending it.", "Maybe, it depends on the person."],
                  ["I would recommend it to friends.", "Yes, I would suggest it."],
                  ["I would definitely recommend it to everyone.", "Absolutely, I would definitely recommend it."]],
    "popularity": [["Almost nobody here uses it.", "Hardly anyone in my country knows it."],
                   ["It is popular only among some enthusiasts.", "Only a small group of fans follow it."],
                   ["Besides fans, quite a few ordinary people know it.", "A fair number of ordinary people know it."],
                   ["It is widely known among ordinary people and products are sold.", "Most people know it and you see related products."],
                   ["It is widely popular and related products sell well.", "It is hugely popular here, products sell very well."]],
}


def make_llm(spec: ModelSpec, cache: Cache | None) -> LLM:
    if spec.provider == "agent":
        raise RuntimeError("provider 'agent' is filled by an external executor: use `hallyu-twins pilot batches` "
                           "and `pilot ingest`, not the API runner")
    return {"openai": OpenAIChat, "openai_compatible": OpenAIChat, "anthropic": AnthropicChat,
            "gemini": GeminiChat, "mock": MockLLM}[spec.provider](spec, cache)
