# axis2/parsing/triggers.py

import re
from axis2.schema import ZoneChangeEvent, DealsDamageEvent

ENTERS_RE = re.compile(
    r"\bwhenever\b.*\benters\b",
    re.IGNORECASE
)

ATTACKS_RE = re.compile(
    r"\bwhenever\b.*\battacks\b",
    re.IGNORECASE
)

ZONE_CHANGE_TRIGGER_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+is\s+put\s+into\s+a?\s*(\w+)\s+from\s+the\s+(\w+)",
    re.IGNORECASE
)

DEALS_DAMAGE_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+deals\s+(combat\s+|noncombat\s+)?damage\s+to\s+(.*)",
    re.IGNORECASE
)

def parse_trigger_event(condition_text: str):
    text = condition_text.lower()

    # 1. Zone-change triggers
    m = ZONE_CHANGE_TRIGGER_RE.search(text)
    if m:
        return ZoneChangeEvent(
            subject=m.group(1).strip(),
            from_zone=m.group(3).strip(),
            to_zone=m.group(2).strip()
        )

    # 2. Deals-damage triggers
    m = DEALS_DAMAGE_RE.search(text)
    if m:
        subject = m.group(1).strip()
        dmg_type = m.group(2).strip() if m.group(2) else "any"
        target = m.group(3).strip()

        return DealsDamageEvent(
            subject=subject,
            target=target,
            damage_type=dmg_type
        )

    # 3. Enters-the-battlefield
    if ENTERS_RE.search(text):
        return "enters"

    # 4. Attacks
    if ATTACKS_RE.search(text):
        return "attacks"

    return None

