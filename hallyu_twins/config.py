"""Experiment configuration (YAML -> dataclasses)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .codebook import COUNTRIES


@dataclass
class ModelSpec:
    name: str                 # label used in outputs
    provider: str             # openai | anthropic | gemini | openai_compatible | mock
    model_id: str
    group: str                # G1 | G2 | G3 (training cutoff relative to report releases)
    cutoff: str               # YYYY-MM, from the provider's official model card (record source!)
    cutoff_source: str = ""
    base_url: str | None = None
    api_key_env: str | None = None       # env var holding this model's key (default: SDK default)
    temperature: float | None = 1.0     # None = do not send (some models reject it)
    max_tokens: int = 200
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    out_dir: str = "outputs"
    cache_dir: str = "outputs/cache"
    seed: int = 20261030
    # data
    raw_wave15: str = "data/raw/wave15.sav"
    raw_wave14: str = "data/raw/wave14.sav"
    # VERIFY: real SQ1AA codes come with the KOFICE codebook. Default = mock-data codes.
    country_codes: dict[int, str] = field(
        default_factory=lambda: {**{i + 1: c for i, c in enumerate(COUNTRIES)}, 31: "Hong Kong"})
    country_codes_w14: dict[int, str] | None = None
    # sampling
    n_per_country: int = 100
    n_per_country_ablation: int = 30
    n_repeat_subsample: int = 300
    n_repeats: int = 3
    # design
    main_condition: dict[str, str] = field(default_factory=lambda: {
        "persona": "P4", "label": "true", "elicit": "ssr", "language": "en", "network": "none"})
    ablations: dict[str, list[str]] = field(default_factory=lambda: {
        "persona": ["P0", "P1", "P2", "P3", "P4", "P4D"],
        "label": ["true", "none", "swap"],
        "elicit": ["dlr", "ssr"],
        "language": ["en", "local"],
        "network": ["none", "self", "random", "homophily"],
    })
    reverse_scale_share: float = 0.5
    # network
    network_k: int = 5
    network_items: list[str] = field(default_factory=lambda: ["XQ5", "XQ6"] + [f"XQ1_{i}" for i in range(1, 12)])
    network_features: str = "P4"   # feature set used to define homophily (never outcomes)
    # SSR
    ssr_method: str = "softmax"     # softmax | maier
    ssr_tau_grid: list[float] = field(default_factory=lambda: [0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12])
    n_calibration_twins: int = 600  # wave-14 twins for SSR calibration
    # models
    models: list[ModelSpec] = field(default_factory=list)
    pilot_models: list[ModelSpec] = field(default_factory=list)
    embedding: dict[str, Any] = field(default_factory=lambda: {"provider": "mock", "model_id": "hash-bow"})
    # stats
    bootstrap_reps: int = 1000
    split_half_reps: int = 1000
    tost_margin_pp: float = 5.0
    max_workers: int = 8


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    models = [ModelSpec(**m) for m in raw.pop("models", [])]
    pilot_models = [ModelSpec(**m) for m in raw.pop("pilot_models", [])]
    cc = raw.pop("country_codes", None)
    cfg = Config(**raw)
    if cc:
        cfg.country_codes = {int(k): v for k, v in cc.items()}
    cfg.models = models
    cfg.pilot_models = pilot_models
    return cfg
