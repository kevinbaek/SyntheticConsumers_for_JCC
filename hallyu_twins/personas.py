"""Persona construction for one-to-one twins.

Levels (cumulative):
  P0  empty persona (only the survey screening condition)       -- Funhouse Mirrors control
  P1  country only                                                 -- Wang (2026) "country label"
  P2  P1 + demographics                                            -- standard silicon sampling
  P3  P2 + Korea awareness + content-use behaviour (SQ6/SQ6A)       -- behavioural grounding
  P4  P3 + attitudes toward Korea (Q1_1..Q1_6, Q2)                  -- belief-system grounding
                                                                     (AS benchmark "history" level)
  P4D P4 + LLM-distilled profile, audited for target leakage         -- AS benchmark "distilled" level

Country-label modes: "true" | "none" (no geographic cue) | "swap" (another country).
Outcome variables are never rendered; ``assert_no_leakage`` enforces it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .codebook import ALL_TARGETS, COUNTRIES, DOMAINS, HISTORY_ATTITUDE, ValueCodes

LEVELS = ("P0", "P1", "P2", "P3", "P4", "P4D")

_Q1_TEXT = {
    "Q1_1": "Korea is an economically advanced country",
    "Q1_2": "Korea takes part in international social contribution activities",
    "Q1_3": "Korea is friendly toward my country",
    "Q1_4": "Korea is a partner rather than a competitor",
    "Q1_5": "Korea is a likeable country",
    "Q1_6": "Korea is a cultural powerhouse",
}

DISPLAY = {"United States": "the United States", "United Kingdom": "the United Kingdom", "UAE": "the UAE",
           "Philippines": "the Philippines"}

SCREENING = ("You are an adult aged 15 to 59 who has used at least one kind of Korean cultural content "
             "(for example dramas, movies, music, food or beauty products).")


@dataclass
class Persona:
    resp_id: str
    level: str
    label_mode: str
    shown_country: str | None
    text: str
    features: dict


def swap_map(seed: int) -> dict[str, str]:
    """Deterministic derangement: every country is mapped to a different country,
    preferably on another continent (strongest test of stereotype use)."""
    from .codebook import CONTINENT
    rng = np.random.default_rng(seed)
    cs = list(COUNTRIES)
    for _ in range(1000):
        perm = list(rng.permutation(cs))
        if all(a != b and CONTINENT[a] != CONTINENT[b] for a, b in zip(cs, perm)):
            return dict(zip(cs, perm))
    perm = cs[1:] + cs[:1]
    return dict(zip(cs, perm))


def _demographic_sentences(row: pd.Series, codes: ValueCodes) -> list[str]:
    s = []
    sex = codes.sex.get(row.get("sex"))
    if pd.notna(row.get("age")) and sex:
        s.append(f"You are a {int(row['age'])}-year-old {sex}.")
    elif sex:
        s.append(f"You are {sex}.")
    for key, mapping in (("marital", codes.marital), ("education", codes.education),
                         ("occupation", codes.occupation)):
        v = mapping.get(row.get(key))
        if v:
            s.append({"marital": f"Marital status: {v}.", "education": f"Education: {v}.",
                      "occupation": f"Occupation: {v}."}[key])
    nat = codes.nationality.get(row.get("nationality"))
    if nat == "korean_descent":
        s.append("You are of Korean descent.")
    elif nat == "foreign_resident":
        s.append("You are a foreign national living and working in this country, not a citizen.")
    if pd.notna(row.get("income")):
        s.append(f"Household income: bracket {int(row['income'])} of {codes.income_levels} in your country "
                 f"(1 = lowest).")
    return s


def _behaviour_sentences(row: pd.Series, codes: ValueCodes) -> list[str]:
    s = []
    aw = codes.korea_awareness.get(row.get("korea_awareness"))
    if aw:
        s.append(f"How well you know Korea: you {aw}.")  # e.g. "you know Korea somewhat"
    used = [DOMAINS[d]["label"] for d in DOMAINS if row.get(f"exp_{d}") == 1]
    if used:
        s.append("Korean content you have used: " + ", ".join(used) + ".")
    recent = [DOMAINS[d]["label"] for i, d in enumerate(DOMAINS, start=1)
              if row.get(f"SQ6A_{i}") == codes.experience_yes]
    if recent:
        s.append("Used within the last 12 months: " + ", ".join(recent) + ".")
    return s


def _attitude_sentences(row: pd.Series, codes: ValueCodes) -> list[str]:
    s = []
    for var, txt in _Q1_TEXT.items():
        v = codes.likert5_agree.get(row.get(var))
        if v:
            s.append(f'On the statement "{txt}", you {v}.')
    imp = codes.impression5.get(row.get("Q2"))
    if imp:
        s.append(f"Your overall impression of Korea is {imp}.")
    return s


def build_persona(row: pd.Series, level: str, label_mode: str = "true", swap: dict | None = None,
                  codes: ValueCodes | None = None, distilled: str | None = None) -> Persona:
    if level not in LEVELS:
        raise ValueError(level)
    codes = codes or ValueCodes()
    country = row["country"]
    shown = {"true": country, "none": None, "swap": (swap or {}).get(country)}[label_mode]
    if label_mode == "swap" and not shown:
        raise ValueError("swap mode needs a swap map")
    lines = [SCREENING]
    if level != "P0" and shown:
        lines.append(f"You live in {DISPLAY.get(shown, shown)}.")
    if level in ("P2", "P3", "P4", "P4D"):
        lines += _demographic_sentences(row, codes)
    if level in ("P3", "P4", "P4D"):
        lines += _behaviour_sentences(row, codes)
    if level in ("P4", "P4D"):
        lines += _attitude_sentences(row, codes)
    if level == "P4D":
        if not distilled:
            raise ValueError("P4D needs an audited distilled profile")
        lines.append("Summary of who you are: " + distilled)
    text = " ".join(lines)
    if label_mode != "true":
        _assert_no_country_mention(text, allowed=shown)
    feats = {k: row.get(k) for k in row.index if k not in ALL_TARGETS}
    return Persona(str(row["resp_id"]), level, label_mode, shown, text, feats)


def _assert_no_country_mention(text: str, allowed: str | None) -> None:
    for c in COUNTRIES + ["Hong Kong"]:
        if c != allowed and re.search(rf"\b{re.escape(c)}\b", text) and DISPLAY.get(allowed, "") != f"the {c}":
            raise AssertionError(f"Country cue '{c}' leaked into persona under label control")


def assert_no_leakage(persona_text: str, row: pd.Series) -> None:
    """Guard: persona may not contain outcome wording (e.g. 'recommend', 'popular')."""
    banned = [r"\brecommend", r"\bpopular", r"\bfavorab", r"how much (you|do you) like Korean"]
    for pat in banned:
        if re.search(pat, persona_text, flags=re.I):
            raise AssertionError(f"Persona text contains outcome wording /{pat}/ for {row['resp_id']}")


# ---------------------------------------------------------------------------------------
# P4D: distilled profile (AS benchmark style) with a second-model audit
# ---------------------------------------------------------------------------------------
DISTILL_PROMPT = (
    "Below are facts about one survey respondent. Write a short profile (max 90 words) in second person "
    "covering: values, media and content habits, attitude toward Korea, consumer orientation, and how they "
    "typically decide whether they like something. Use only the facts given; do not invent new facts; do not "
    "predict how much they like Korean content or whether they would recommend it.\n\nFacts:\n{facts}"
)
AUDIT_PROMPT = (
    "Facts:\n{facts}\n\nProfile:\n{profile}\n\nIs every statement in the profile supported by the facts, and "
    "does the profile avoid stating how much the person likes Korean content or whether they would recommend "
    "it? Answer PASS or FAIL followed by one short reason."
)


def distill_profile(p4_text: str, writer, auditor) -> tuple[str | None, str]:
    """Return (profile or None if audit failed, audit verdict). writer/auditor are LLM clients."""
    profile = writer.complete([{"role": "user", "content": DISTILL_PROMPT.format(facts=p4_text)}]).text.strip()
    verdict = auditor.complete([{"role": "user", "content": AUDIT_PROMPT.format(facts=p4_text, profile=profile)}]).text
    ok = verdict.strip().upper().startswith("PASS")
    try:
        assert_no_leakage(profile, pd.Series({"resp_id": "distilled"}))
    except AssertionError:
        ok = False
    return (profile if ok else None), verdict.strip()
