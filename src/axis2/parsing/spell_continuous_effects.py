import re
from axis2.schema import ContinuousEffect, PTExpression
from axis2.parsing.subject import parse_subject

PT_RE = re.compile(r"get[s]?\s+([+\-]?\d+)\/([+\-]?\d+)", re.I)
DURATION_RE = re.compile(r"until end of turn|this turn|until your next turn", re.I)

def parse_spell_continuous_effect(text: str):
    t = text.lower()
    print(f"Parsing spell continuous effect: {t}")
    # Must contain a P/T modification
    m = PT_RE.search(t)
    if not m:
        return None

    power = m.group(1)
    toughness = m.group(2)

    # Extract subject
    subject = parse_subject(t)
    if not subject:
        return None

    # Extract duration
    d = DURATION_RE.search(t)
    duration = d.group(0).lower() if d else None

    return ContinuousEffect(
        kind="pt_mod",
        applies_to=subject,
        pt_value=PTExpression(power=power, toughness=toughness),
        duration=duration,
        text=text
    )
