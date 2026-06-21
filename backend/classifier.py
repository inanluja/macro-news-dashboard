import re

RULES = [
    {
        "tag": "War / Military",
        "impact": "Critical",
        "keywords": ["war", "military", "airstrike", "missile", "troops", "invasion", "attack", "bomb", "nuclear",
                     "nato", "conflict", "ceasefire", "casualties", "strike"],
    },
    {
        "tag": "Sanctions",
        "impact": "High",
        "keywords": ["sanction", "embargo", "ban", "restriction", "export control", "freeze assets", "blacklist"],
    },
    {
        "tag": "Central Bank / Rate Decision",
        "impact": "High",
        "keywords": ["interest rate", "rate hike", "rate cut", "federal reserve", "fed", "ecb", "boe", "boj",
                     "monetary policy", "quantitative easing", "qe", "qt", "inflation target", "basis points", "bps"],
    },
    {
        "tag": "Inflation / CPI",
        "impact": "High",
        "keywords": ["inflation", "cpi", "consumer price", "pce", "deflation", "stagflation", "price pressure"],
    },
    {
        "tag": "Geopolitical Tension",
        "impact": "High",
        "keywords": ["iran", "russia", "china", "north korea", "taiwan", "ukraine", "middle east", "strait of hormuz",
                     "south china sea", "coup", "regime", "diplomat", "escalation", "provocation"],
    },
    {
        "tag": "Oil & Energy",
        "impact": "Medium",
        "keywords": ["oil", "crude", "brent", "wti", "opec", "natural gas", "lng", "energy", "petroleum",
                     "pipeline", "refinery", "barrel"],
    },
    {
        "tag": "Recession / GDP",
        "impact": "High",
        "keywords": ["recession", "gdp", "contraction", "economic slowdown", "growth", "downturn", "stagflation"],
    },
    {
        "tag": "Banking / Financial Stability",
        "impact": "High",
        "keywords": ["bank failure", "credit crunch", "liquidity", "default", "bankruptcy", "systemic risk",
                     "financial crisis", "bank run", "bailout", "imf loan"],
    },
    {
        "tag": "Markets",
        "impact": "Medium",
        "keywords": ["stock market", "equities", "yield", "spread", "bond market", "vix", "volatility",
                     "sell-off", "rally", "crash", "correction"],
    },
    {
        "tag": "Trade / Tariffs",
        "impact": "Medium",
        "keywords": ["tariff", "trade war", "trade deal", "wto", "import", "export", "supply chain", "protectionism"],
    },
]

IMPACT_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


def classify(title: str, summary: str) -> dict:
    text = (title + " " + summary).lower()
    matched_tags = []
    max_impact = "Low"

    for rule in RULES:
        if any(re.search(r"\b" + re.escape(kw) + r"\b", text) for kw in rule["keywords"]):
            matched_tags.append(rule["tag"])
            if IMPACT_ORDER[rule["impact"]] > IMPACT_ORDER[max_impact]:
                max_impact = rule["impact"]

    return {
        "tags": matched_tags if matched_tags else ["General"],
        "impact": max_impact,
    }
