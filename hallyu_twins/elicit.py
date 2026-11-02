"""Prompts, Direct Likert Rating (DLR) parsing and Semantic Similarity Rating (SSR).

SSR (Maier et al., 2025): the twin answers in free text; the answer is embedded and compared
with five anchor statements per scale point; similarities are turned into a probability mass
over 1..5. We average over several anchor sets so no single wording drives the result.

Two mappings are implemented:
  maier   p_k proportional to (s_k - min_j s_j + eps) ** (1/T)   (paper default, T = 1)
  softmax p_k proportional to exp(s_k / tau)                         (tau calibrated on wave 14)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from .codebook import ITEMS, Item, Scale

SYSTEM = ("{persona}\n\nYou are taking part in an online survey about Korean culture. Answer every "
          "question as this person would, based on who they are and the life they lead. There are no "
          "right or wrong answers. Do not mention that you are an AI, and do not look anything up.")

SSR_USER = ("Question: {question}\nAnswer in one or two sentences in your own words, as this person. "
            "Do not give a number and do not quote answer options.")

DLR_USER = "Question: {question}\nOptions:\n{options}\nReply with the number only."

LOCAL_LANGUAGE_NOTE = " Answer in the main language spoken in your country."


def options_text(scale: Scale, reverse: bool) -> str:
    labels = list(scale.labels)[::-1] if reverse else list(scale.labels)
    return "\n".join(f"{i + 1}. {lab}" for i, lab in enumerate(labels))


def messages(persona_text: str, item: Item, mode: str, reverse: bool = False,
             local_language: bool = False, extra_turns: list[dict] | None = None) -> list[dict]:
    sys = SYSTEM.format(persona=persona_text)
    if mode == "ssr":
        user = SSR_USER.format(question=item.text) + (LOCAL_LANGUAGE_NOTE if local_language else "")
    elif mode == "dlr":
        user = DLR_USER.format(question=item.text, options=options_text(item.scale, reverse))
    else:
        raise ValueError(mode)
    return [{"role": "system", "content": sys}, *(extra_turns or []), {"role": "user", "content": user}]


def parse_dlr(text: str, reverse: bool) -> float:
    m = re.search(r"\b([1-5])\b", text or "")
    if not m:
        return float("nan")
    v = int(m.group(1))
    return float(6 - v if reverse else v)


# ---------------------------------------------------------------------------------------
# Anchor statements. Several sets per scale, written to differ in wording but not in level.
# {topic} is filled per item. Pre-registered; do not tune on wave-15 data.
# ---------------------------------------------------------------------------------------
ANCHORS: dict[str, list[list[str]]] = {
    "liking": [
        ["I really dislike {topic}; it does not appeal to me at all.",
         "I don't like {topic} much; it is mostly not to my taste.",
         "{topic} is okay; I neither like nor dislike it.",
         "I like {topic}; I enjoy it.",
         "I love {topic}; I like it very much."],
        ["{topic} is not for me at all.",
         "{topic} is not really my thing.",
         "{topic} is so-so for me, just average.",
         "{topic} is good, I quite like it.",
         "{topic} is excellent, I am a big fan."],
        ["I have a very negative opinion of {topic}.",
         "I have a somewhat negative opinion of {topic}.",
         "I have a neutral opinion of {topic}.",
         "I have a positive opinion of {topic}.",
         "I have a very positive opinion of {topic}."],
    ],
    "recommend": [
        ["I would never recommend {topic} to anyone.",
         "I would not recommend {topic} to people I know.",
         "I am not sure whether I would recommend {topic}; maybe, maybe not.",
         "I would recommend {topic} to people I know.",
         "I would definitely recommend {topic}; I already tell everyone about it."],
        ["Recommending {topic} is out of the question for me.",
         "I probably wouldn't suggest {topic} to my friends.",
         "It depends on the person whether I'd suggest {topic}.",
         "I'd suggest {topic} to my friends.",
         "I'd strongly urge my friends to try {topic}."],
    ],
    "popularity": [
        ["Almost nobody in my country uses {topic}.",
         "{topic} is popular only among a small group of enthusiasts in my country.",
         "Besides enthusiasts, quite a few ordinary people in my country know {topic}.",
         "{topic} is widely known among ordinary people in my country and related products are sold.",
         "{topic} is hugely popular with ordinary people in my country and related products sell very well."],
        ["Hardly anyone here has heard of {topic}.",
         "Only some fans here follow {topic}.",
         "A fair number of ordinary people here know {topic}, not just fans.",
         "Most people here know {topic}, and you see related products in shops.",
         "{topic} is mainstream here; everyone knows it and related products sell well."],
    ],
}

TOPIC = {
    "overall_fav": "the Korean cultural content I have experienced",
    "overall_rec": "the Korean cultural content I used recently",
}


def topic_of(item: Item) -> str:
    if item.kind in TOPIC:
        return TOPIC[item.kind]
    m = re.search(r"(Korean [^?]+?)(?: currently| to people|\?)", item.text)
    return m.group(1) if m else "it"


def anchor_texts(item: Item) -> list[list[str]]:
    sets = ANCHORS[item.scale.name]
    t = topic_of(item)
    out = []
    for s in sets:
        filled = [a.format(topic=t) for a in s]
        out.append([f[0].upper() + f[1:] for f in filled])
    return out


@dataclass
class SSRScorer:
    embedder: object
    method: str = "maier"
    tau: float = 0.02
    temperature: float = 1.0
    eps: float = 0.0

    def __post_init__(self):
        self._anchor_cache: dict[str, list[np.ndarray]] = {}

    def anchors(self, item: Item) -> list[np.ndarray]:
        if item.var not in self._anchor_cache:
            self._anchor_cache[item.var] = [self.embedder.embed(s) for s in anchor_texts(item)]
        return self._anchor_cache[item.var]

    def probs(self, item: Item, texts: list[str], tau: float | None = None) -> np.ndarray:
        """Return (n, 5) probability mass over scale points 1..5."""
        R = self.embedder.embed([t if t else "(no answer)" for t in texts])
        P = np.zeros((len(texts), 5))
        for A in self.anchors(item):
            S = R @ A.T                                    # cosine (vectors are unit-norm)
            if self.method == "maier":
                W = np.clip(S - S.min(axis=1, keepdims=True) + self.eps, 0, None) ** (1 / self.temperature)
                W = W + 1e-12
            elif self.method == "softmax":
                z = S / (tau or self.tau)
                W = np.exp(z - z.max(axis=1, keepdims=True))
            else:
                raise ValueError(self.method)
            P += W / W.sum(axis=1, keepdims=True)
        return P / len(self.anchors(item))


def expected(P: np.ndarray) -> np.ndarray:
    return P @ np.arange(1, 6)


def t2b(P: np.ndarray) -> np.ndarray:
    return P[:, 3] + P[:, 4]


def item(var: str) -> Item:
    return ITEMS[var]
