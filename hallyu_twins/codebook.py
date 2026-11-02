"""Variable map for the 2026 Overseas Hallyu Survey (KOFICE, wave 15).

Variable names follow the KOFICE "2026 해외한류실태조사 이용자 가이드북" (data variable guide).
Value codes (e.g. SQ2 1=male) and the exact English item wording are NOT published in the
guide. Every entry marked ``verify=True`` must be checked against the official questionnaire
that is requested together with the raw data. Keep this file as the single source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------------------------
# Content domains (11 domains comparable across waves 13-15). Prefix letters follow the
# questionnaire block letters in the variable guide (AQ = drama ... KQ = food).
# --------------------------------------------------------------------------------------
DOMAINS: dict[str, dict] = {
    "drama":       {"block": "A", "exp": "SQ6_1",  "fav": "AQ4", "rec": "AQ9",  "pop": "XQ1_1",  "label": "Korean TV dramas"},
    "variety":     {"block": "B", "exp": "SQ6_2",  "fav": "BQ4", "rec": "BQ8",  "pop": "XQ1_2",  "label": "Korean variety shows"},
    "movie":       {"block": "C", "exp": "SQ6_3",  "fav": "CQ4", "rec": "CQ9",  "pop": "XQ1_3",  "label": "Korean movies"},
    "music":       {"block": "D", "exp": "SQ6_4",  "fav": "DQ4", "rec": "DQ9",  "pop": "XQ1_4",  "label": "Korean music (K-pop)"},
    "animation":   {"block": "E", "exp": "SQ6_5",  "fav": "EQ4", "rec": "EQ10", "pop": "XQ1_5",  "label": "Korean animation"},
    "publication": {"block": "F", "exp": "SQ6_6",  "fav": "FQ5", "rec": "FQ9",  "pop": "XQ1_6",  "label": "Korean books and e-books"},
    "webtoon":     {"block": "G", "exp": "SQ6_7",  "fav": "GQ4", "rec": "GQ8",  "pop": "XQ1_7",  "label": "Korean webtoons"},
    "game":        {"block": "H", "exp": "SQ6_8",  "fav": "HQ4", "rec": "HQ10", "pop": "XQ1_8",  "label": "Korean games"},
    "fashion":     {"block": "I", "exp": "SQ6_9",  "fav": "IQ6", "rec": "IQ10", "pop": "XQ1_9",  "label": "Korean fashion"},
    "beauty":      {"block": "J", "exp": "SQ6_10", "fav": "JQ6", "rec": "JQ10", "pop": "XQ1_10", "label": "Korean beauty products"},
    "food":        {"block": "K", "exp": "SQ6_11", "fav": "KQ6", "rec": "KQ10", "pop": "XQ1_11", "label": "Korean food"},
}

OVERALL_FAV = "XQ5"   # overall favorability of Korean cultural content (5-point)
OVERALL_REC = "XQ6"   # overall recommendation intention (5-point)
WEIGHT = "WT"
RESP_ID = "IDX"

# Respondent attributes allowed as persona input (never outcomes).
DEMOGRAPHICS = {
    "country": "SQ1AA",     # residence country/region code -> name via config.country_codes
    "region": "SQ1AB",      # sub-region code
    "nationality": "SQ1B",
    "sex": "SQ2",
    "age": "SQ3",
    "age_band": "SQ3A",
    "marital": "DDQ1",
    "occupation": "DDQ2",
    "education": "DDQ3",
    "income": "DDQ4",
    "religion": "DDQ6",
}
KOREA_AWARENESS = "SQ4B"

# "History" items: non-target answers used to ground P4 personas (cross-item transfer,
# cf. Ku et al. 2026; AS benchmark L3 "history" level). Two tiers so the paper can show
# where individual signal comes from.
HISTORY_BEHAVIOR = (
    [d["exp"] for d in DOMAINS.values()]
    + [f"SQ6A_{i}" for i in range(1, 12)]          # used within last year
    + ["SQ6C"]                                       # influence of first content
)
HISTORY_ATTITUDE = [f"Q1_{i}" for i in range(1, 7)] + ["Q2"]  # perceptions of Korea

# Outcomes (targets). Anything here must never appear in a persona.
TARGETS_SCALAR = [OVERALL_FAV, OVERALL_REC]
TARGETS_DOMAIN_FAV = [d["fav"] for d in DOMAINS.values()]
TARGETS_DOMAIN_REC = [d["rec"] for d in DOMAINS.values()]
TARGETS_POP = [d["pop"] for d in DOMAINS.values()]
# Added in wave 15 (2025 fieldwork): popularity-only domains. Variable names VERIFY.
POP_EXTRA = {"character": {"pop": "XQ1_12", "label": "Korean characters (character goods and IP)"},
             "performance": {"pop": "XQ1_13", "label": "Korean performing arts other than K-pop (musicals, theatre, traditional, classical, dance)"}}
TARGETS_POP_15 = TARGETS_POP + [d["pop"] for d in POP_EXTRA.values()]
ALL_TARGETS = TARGETS_SCALAR + TARGETS_DOMAIN_FAV + TARGETS_DOMAIN_REC + TARGETS_POP_15


@dataclass(frozen=True)
class Scale:
    name: str
    labels: tuple[str, ...]           # verbal labels for points 1..5
    favorable: tuple[int, ...] = (4, 5)
    verify: bool = True


LIKING = Scale(
    "liking",
    ("I do not like it at all", "I do not like it", "It is so-so",
     "I like it", "I like it very much"),
)
RECOMMEND = Scale(
    "recommend",
    ("I would never recommend it", "I would not recommend it", "Neutral",
     "I would recommend it", "I would definitely recommend it"),
)
POPULARITY = Scale(
    "popularity",
    ("Almost nobody in my country uses it",
     "It is popular only among some enthusiasts",
     "Besides enthusiasts, quite a few ordinary people know it",
     "It is widely known among ordinary people and related products are sold",
     "It is widely popular among ordinary people and related products sell well"),
)


@dataclass(frozen=True)
class Item:
    var: str
    kind: str                 # overall_fav | overall_rec | domain_fav | domain_rec | popularity
    scale: Scale
    text: str
    domain: str | None = None
    social: bool = False      # item asks about other people (perceived social norm)
    verify: bool = True


def build_items() -> dict[str, Item]:
    """English item wording reconstructed from the published KOFICE report captions.

    VERIFY against the official questionnaire before the confirmatory run.
    """
    items: dict[str, Item] = {}
    for dom, d in DOMAINS.items():
        items[d["fav"]] = Item(d["fav"], "domain_fav", LIKING,
                               f"Overall, how much do you like {d['label']}?", dom)
        items[d["rec"]] = Item(d["rec"], "domain_rec", RECOMMEND,
                               f"Would you recommend {d['label']} to people you know?", dom)
        items[d["pop"]] = Item(d["pop"], "popularity", POPULARITY,
                               f"How popular do you think {d['label']} currently are in your country?",
                               dom, social=True)
    for dom, d in POP_EXTRA.items():
        items[d["pop"]] = Item(d["pop"], "popularity", POPULARITY,
                               f"How popular do you think {d['label']} currently are in your country?",
                               dom, social=True)
    items[OVERALL_FAV] = Item(OVERALL_FAV, "overall_fav", LIKING,
                              "Overall, how much do you like the Korean cultural content you have experienced?")
    # Source of wording: report figure captions 2-1-1 (XQ5), 2-1-10 (XQ6), 2-1-6 (XQ1). Translated; VERIFY.
    items[OVERALL_REC] = Item(OVERALL_REC, "overall_rec", RECOMMEND,
                              "Would you recommend the Korean cultural content you used recently to people you know?")
    return items


ITEMS = build_items()


def questionnaire_order(answered_domains: list[str]) -> list[str]:
    """Order of target items for one respondent, mirroring the survey flow:
    domain blocks (only those the respondent answered, max 6) -> popularity (XQ1) ->
    overall favorability (XQ5) -> overall recommendation (XQ6)."""
    order: list[str] = []
    for dom in DOMAINS:  # canonical A..K order
        if dom in answered_domains:
            order += [DOMAINS[dom]["fav"], DOMAINS[dom]["rec"]]
    order += TARGETS_POP + [OVERALL_FAV, OVERALL_REC]
    return order


# Continents as defined in the KOFICE report (used for B4 neighbor baseline and subgroup
# reporting). Keys are English country names used throughout the package.
CONTINENT: dict[str, str] = {
    **{c: "Asia-Pacific" for c in ["China", "Japan", "Taiwan", "Thailand", "Malaysia", "Indonesia",
                                     "India", "Vietnam", "Kazakhstan", "Australia", "Philippines", "Singapore"]},
    **{c: "Americas" for c in ["United States", "Canada", "Mexico", "Brazil", "Argentina", "Chile"]},
    **{c: "Europe" for c in ["United Kingdom", "France", "Italy", "Spain", "Germany", "Russia", "Turkiye", "Poland"]},
    **{c: "Middle East" for c in ["UAE", "Saudi Arabia"]},
    **{c: "Africa" for c in ["Egypt", "South Africa"]},
    "Hong Kong": "Asia-Pacific",   # wave 14 only
}

# Published wave-15 sample sizes per country (guidebook, 표본 배분).
WAVE15_N: dict[str, int] = {
    "China": 2100, "Japan": 1000, "Taiwan": 750, "Thailand": 850, "Malaysia": 730, "Indonesia": 1200,
    "India": 1850, "Vietnam": 900, "Kazakhstan": 700, "Australia": 710, "Philippines": 700, "Singapore": 700,
    "United States": 1300, "Canada": 800, "Mexico": 960, "Brazil": 1100, "Argentina": 800, "Chile": 500,
    "United Kingdom": 850, "France": 850, "Italy": 840, "Spain": 800, "Germany": 900, "Russia": 1000,
    "Turkiye": 880, "Poland": 500, "UAE": 700, "Saudi Arabia": 730, "Egypt": 900, "South Africa": 800,
}
COUNTRIES = list(WAVE15_N)                       # 30 wave-15 countries
WAVE14_COUNTRIES = [c for c in COUNTRIES if c not in ("Singapore", "Chile", "Poland")] + ["Hong Kong"]
COMMON_14_15 = [c for c in COUNTRIES if c in WAVE14_COUNTRIES]   # 27 countries

# Report publication dates (contamination split). Dates of press releases.
REPORT_RELEASE = {13: "2024-04-02", 14: "2025-04-07", 15: "2026-03-30"}


@dataclass
class ValueCodes:
    """Assumed value codes. VERIFY against the questionnaire; override in config."""
    sex: dict = field(default_factory=lambda: {1: "male", 2: "female"})
    age_band: dict = field(default_factory=lambda: {1: "15-19", 2: "20-29", 3: "30-39", 4: "40-49", 5: "50-59"})
    korea_awareness: dict = field(default_factory=lambda: {1: "know Korea very well", 2: "know Korea somewhat",
                                                           3: "know little about Korea"})
    experience_yes: int = 1   # SQ6_x: 1 = 있음 (has used), 2 = 없음
    missing: tuple = (-1, 97, 98, 99, 999)
    # Category orders below follow the report's respondent-profile tables; VERIFY codes.
    marital: dict = field(default_factory=lambda: {1: "married", 2: "single", 3: "other marital status"})
    education: dict = field(default_factory=lambda: {1: "high school or less", 2: "university degree",
                                                     3: "graduate degree", 4: "other education"})
    occupation: dict = field(default_factory=lambda: {
        1: "middle/high school student", 2: "university or graduate student", 3: "office or technical worker",
        4: "sales or production worker", 5: "professional", 6: "part-time worker", 7: "self-employed",
        8: "full-time homemaker", 9: "unemployed or retired", 10: "other occupation"})
    nationality: dict = field(default_factory=lambda: {1: "korean_descent", 2: "local", 3: "foreign_resident"})
    income_levels: int = 5    # DDQ4 brackets are country-specific; rendered as relative position
    likert5_agree: dict = field(default_factory=lambda: {
        1: "strongly disagree", 2: "disagree", 3: "neither agree nor disagree", 4: "agree", 5: "strongly agree"})
    impression5: dict = field(default_factory=lambda: {
        1: "very negative", 2: "somewhat negative", 3: "neutral", 4: "somewhat positive", 5: "very positive"})
