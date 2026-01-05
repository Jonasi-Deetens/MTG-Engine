# axis2/parsing/keywords.py

import re
from typing import List, Tuple, Optional

KEYWORD_ALIASES = {
    "totem armor": "umbra armor",
}

KEYWORD_WITH_REMINDER_RE = re.compile(
    r"^([A-Za-z\s]+(?:\{[^}]+\})?)\s*\((.+)\)$",
    re.MULTILINE
)

KEYWORD_WITH_COST_RE = re.compile(
    r"^([A-Za-z\s]+)\s*(?:—|-)?\s*(\{[^}]+\}|pay\s+\d+\s+life|discard\s+(?:a|an|\d+)\s+cards?|sacrifice\s+.*?|collect\s+evidence)",
    re.IGNORECASE | re.MULTILINE
)


def extract_keywords(oracle_text: str) -> List[str]:
    """
    Extracts simple evergreen keywords that appear as standalone lines.
    """
    if not oracle_text:
        return []

    keywords = []
    lines = [l.strip() for l in oracle_text.split("\n")]

    evergreen = {
        "trample",
        "flying",
        "vigilance",
        "haste",
        "deathtouch",
        "lifelink",
        "reach",
        "menace",
        "first strike",
        "double strike",
        "hexproof",
        "ward",
        "indestructible",
        "umbra armor",
        "totem armor",
        "intimidate",
        "shroud",
        "banding",
        "phasing",
        "shadow",
        "horsemanship",
        "fear",
    }

    for line in lines:
        lower = line.lower()
        
        reminder_match = KEYWORD_WITH_REMINDER_RE.match(line)
        if reminder_match:
            keyword_part = reminder_match.group(1).strip().lower()
            cost_match = KEYWORD_WITH_COST_RE.match(keyword_part)
            if cost_match:
                keyword_name = cost_match.group(1).strip().lower()
            else:
                keyword_name = keyword_part
            
            keyword_name = KEYWORD_ALIASES.get(keyword_name, keyword_name)
            if keyword_name in evergreen or keyword_name.startswith("ward") or keyword_name.endswith("walk") or keyword_name.startswith("protection from") or keyword_name.startswith("cycling") or keyword_name.endswith("cycling"):
                keywords.append(keyword_name)
            continue
        
        cost_match = KEYWORD_WITH_COST_RE.match(line)
        if cost_match:
            keyword_name = cost_match.group(1).strip().lower()
            keyword_name = KEYWORD_ALIASES.get(keyword_name, keyword_name)
            if keyword_name in evergreen or keyword_name.startswith("ward") or keyword_name.endswith("walk") or keyword_name.startswith("protection from") or keyword_name.startswith("cycling") or keyword_name.endswith("cycling"):
                keywords.append(keyword_name)
            continue
        
        if lower in evergreen or lower.endswith("walk") or lower.startswith("protection from") or lower.startswith("cycling") or lower.endswith("cycling"):
            keywords.append(line)

    return keywords


def extract_keyword_with_reminder(line: str) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    """
    Extract keyword name, reminder text, and cost from a line.
    
    Returns:
        Tuple of (keyword_name, reminder_text, cost_text) or None
    """
    from axis2.parsing.keyword_abilities import get_registry
    registry = get_registry()
    return registry.detect_keyword(line)

