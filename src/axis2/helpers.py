import re
from axis1.schema import Axis1Face

def cleaned_oracle_text(face: Axis1Face) -> str:
    """
    Return oracle text with activated and triggered ability text removed.
    Leaves only static/continuous-effect text.
    """
    text = (face.oracle_text or "").lower()

    # ----------------------------------------
    # 1. Remove activated abilities
    # ----------------------------------------
    for a in getattr(face, "activated_abilities", []):
        cost = getattr(a, "cost", "") or getattr(a, "cost_text", "")
        effect = getattr(a, "effect", "") or getattr(a, "effect_text", "")
        combined = f"{cost}: {effect}".strip().lower()

        if combined and combined != ":":
            escaped = re.escape(combined.rstrip("."))
            text = re.sub(escaped + r"\.?\s*", "", text)

    # ----------------------------------------
    # 2. Remove triggered abilities
    # ----------------------------------------
    for t in getattr(face, "triggered_abilities", []):
        cond = (t.condition or "").lower().strip()
        eff = (t.effect or "").lower().strip()
        combined = f"{cond}, {eff}".strip()

        if combined:
            escaped = re.escape(combined.rstrip("."))
            text = re.sub(escaped + r"\.?\s*", "", text)

    return text.strip()
